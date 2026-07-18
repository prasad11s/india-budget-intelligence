import os
import json
import glob
import chromadb
from openai import OpenAI

EMBEDDING_MODEL = "text-embedding-3-large"
BATCH_SIZE = 100
CHUNK_FOLDERS = [
    "data/chunks/budget_speeches",
    "data/chunks/economic_surveys",
    "data/chunks/budget_documents",
]

openai_client = OpenAI()
chroma_client = chromadb.PersistentClient(path="data/chroma_db")
collection = chroma_client.get_or_create_collection("budget_intelligence")

existing_ids = set()
offset = 0
page_size = 1000
while True:
    page = collection.get(limit=page_size, offset=offset, include=[])
    if not page["ids"]:
        break
    existing_ids.update(page["ids"])
    offset += page_size
print(f"Already in ChromaDB: {len(existing_ids)} chunks")


def normalize_chunk(chunk):
    """budget_speeches chunks nest fields under 'metadata'; the other two
    doc types keep everything flat. This makes both shapes look the same."""
    if "metadata" in chunk:
        return chunk["text"], chunk["metadata"]
    meta = {k: v for k, v in chunk.items() if k != "text"}
    return chunk["text"], meta


STOPWORDS = {"the", "and", "of", "in", "to", "for", "is", "budget",
             "government", "year", "crores", "rs", "which", "shall"}


def is_garbled(text):
    """Some budget_documents PDFs interleave Hindi-script sections whose
    font encoding decodes to gibberish. A chunk with almost no common
    English words is very likely one of those — skip it rather than
    embed nonsense."""
    words = text.lower().split()
    if not words:
        return True
    hits = sum(1 for w in words if w.strip(".,;:()") in STOPWORDS)
    return (hits / len(words)) < 0.05


# Gather every chunk not already embedded
texts, metadatas, ids = [], [], []
for folder in CHUNK_FOLDERS:
    for filepath in glob.glob(os.path.join(folder, "*.json")):
        with open(filepath, encoding="utf-8") as f:
            chunks = json.load(f)
        for chunk in chunks:
            text, meta = normalize_chunk(chunk)
            chunk_id = meta["chunk_id"]
            if chunk_id in existing_ids:
                continue
            if is_garbled(text):
                continue
            texts.append(text)
            metadatas.append(meta)
            ids.append(chunk_id)

print(f"New chunks to embed: {len(texts)}")

# Embed and store in batches
for i in range(0, len(texts), BATCH_SIZE):
    batch_texts = texts[i:i + BATCH_SIZE]
    batch_meta = metadatas[i:i + BATCH_SIZE]
    batch_ids = ids[i:i + BATCH_SIZE]

    response = openai_client.embeddings.create(model=EMBEDDING_MODEL, input=batch_texts)
    embeddings = [d.embedding for d in response.data]

    collection.add(
        ids=batch_ids,
        embeddings=embeddings,
        documents=batch_texts,
        metadatas=batch_meta,
    )
    print(f"Added batch {i // BATCH_SIZE + 1} ({len(batch_texts)} chunks)")

print(f"\nDone. Total chunks in collection: {collection.count()}")