import json
import configparser
import chromadb
from openai import OpenAI

INPUT_FILE = "data/processed/budget_speeches_chunks_para750.jsonl"
CHROMA_PATH = "data/chroma_db"
COLLECTION_NAME = "budget_speeches_para750"
EMBED_MODEL = "text-embedding-3-small"
BATCH_SIZE = 100


def load_api_key():
    config = configparser.ConfigParser()
    config.read("../docs/config.ini")  # config.ini lives at project root, one level above src2.0
    return config["openai"]["api_key"]


def load_chunks():
    chunks = []
    with open(INPUT_FILE, "r", encoding="utf-8") as f:
        for line in f:
            chunks.append(json.loads(line))
    return chunks


def main():
    client = OpenAI(api_key=load_api_key())
    chroma = chromadb.PersistentClient(path=CHROMA_PATH)
    collection = chroma.get_or_create_collection(COLLECTION_NAME)

    chunks = load_chunks()
    print(f"Loaded {len(chunks)} chunks to embed")

    for start in range(0, len(chunks), BATCH_SIZE):
        batch = chunks[start:start + BATCH_SIZE]
        texts = [c["text"] for c in batch]

        response = client.embeddings.create(model=EMBED_MODEL, input=texts)
        vectors = [item.embedding for item in response.data]

        collection.upsert(
            ids=[c["chunk_id"] for c in batch],
            embeddings=vectors,
            documents=texts,
            metadatas=[
                {
                    "year": str(c["year"]),
                    "doc_type": c["doc_type"],
                    "filename": c["filename"],
                    "page_start": c["page_start"] or 0,
                    "page_end": c["page_end"] or 0,
                    "chunk_method": c["chunk_method"],
                }
                for c in batch
            ],
        )
        print(f"Embedded {start + len(batch)}/{len(chunks)}")

    print(f"\nDone. Collection '{COLLECTION_NAME}' now has {collection.count()} chunks")


if __name__ == "__main__":
    main()