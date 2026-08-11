import json
import re
import configparser
import chromadb
from openai import OpenAI

TARGET_SIZE = 750
OVERLAP_SENTENCES = 1

config = configparser.ConfigParser()
config.read("../docs/config.ini")
api_key = config["openai"]["api_key"]

client_openai = OpenAI(api_key=api_key)
client_chroma = chromadb.PersistentClient(path="data/chroma_db_test")

QUESTIONS = [
    "Who presented the Budget 2026-2027 speech, and in what role?",
    "What is the fiscal deficit estimated at in BE 2026-27?",
    "What is the fiscal deficit estimated at in RE 2025-26?",
    "What is the debt to GDP ratio estimated at in BE 2026-27?",
    "What is the total expenditure estimated for 2026-27?",
    "What is the outlay proposed for Biopharma SHAKTI, and over how many years?",
    "By how much is the outlay for the Electronics Components Manufacturing Scheme proposed to increase, and to what amount?",
    "What is the new MAT rate proposed, down from what earlier rate?",
    "What is the proposed public capex figure for FY2026-27, and what was it in BE 2025-26?",
    "What is the new STT rate on Futures, and what was the earlier rate?",
]

# ---- Step 1: chunk ----
with open("data/processed/bs2026_27.json", "r", encoding="utf-8") as f:
    doc = json.load(f)

sentences = []
for page in doc["pages"]:
    text = (page["text"] or "").replace("\n", " ")
    for sent in re.split(r"(?<=[.!?])\s+", text):
        sent = sent.strip()
        if sent:
            sentences.append({"text": sent, "page": page["page"]})

def chunk_by_sentences(sentences, target_size, overlap_sentences, doc_type, year, filename, method_name):
    chunks = []
    current = []
    chunk_id = 0

    def flush():
        nonlocal chunk_id, current
        if not current:
            return
        chunk_text = " ".join(s["text"] for s in current)
        chunks.append({
            "chunk_id": f"{year}_{method_name}_{chunk_id:04d}",
            "text": chunk_text,
            "page_start": current[0]["page"],
            "page_end": current[-1]["page"],
        })
        chunk_id += 1

    for sent in sentences:
        prospective_len = sum(len(s["text"]) for s in current) + len(sent["text"])
        if current and prospective_len > target_size:
            flush()
            current = current[-overlap_sentences:] if overlap_sentences else []
        current.append(sent)
    flush()
    return chunks

chunks = chunk_by_sentences(
    sentences, TARGET_SIZE, OVERLAP_SENTENCES,
    doc["doc_type"], doc["year"], doc["filename"],
    method_name=f"para_{TARGET_SIZE}"
)
print(f"Chunking done: {len(chunks)} chunks created")

with open(f"data/processed/chunks_para_{TARGET_SIZE}.json", "w", encoding="utf-8") as f:
    json.dump(chunks, f, indent=2, ensure_ascii=False)
print(f"Saved chunks to data/processed/chunks_para_{TARGET_SIZE}.json")

# ---- Step 2: embed with both models ----
EMBED_CONFIGS = [
    {"model": "text-embedding-3-small", "collection": f"para_{TARGET_SIZE}"},
    {"model": "text-embedding-3-large", "collection": f"para_{TARGET_SIZE}_large"},
]

texts = [c["text"] for c in chunks]
ids = [c["chunk_id"] for c in chunks]
metadatas = [{"page_start": c["page_start"], "page_end": c["page_end"]} for c in chunks]

for cfg in EMBED_CONFIGS:
    collection = client_chroma.get_or_create_collection(name=cfg["collection"])
    response = client_openai.embeddings.create(input=texts, model=cfg["model"])
    embeddings = [item.embedding for item in response.data]
    collection.add(ids=ids, embeddings=embeddings, documents=texts, metadatas=metadatas)
    print(f"Embedded into '{cfg['collection']}' using {cfg['model']}")

# ---- Step 3: retrieve, 10 questions, both collections ----
TOP_K = 5
query_cache = {}

def embed_query(text, model):
    key = (text, model)
    if key not in query_cache:
        response = client_openai.embeddings.create(input=[text], model=model)
        query_cache[key] = response.data[0].embedding
    return query_cache[key]

for question in QUESTIONS:
    print("=" * 80)
    print(f"QUESTION: {question}")
    for cfg in EMBED_CONFIGS:
        query_vector = embed_query(question, cfg["model"])
        collection = client_chroma.get_collection(name=cfg["collection"])
        results = collection.query(query_embeddings=[query_vector], n_results=TOP_K)

        print(f"\n--- {cfg['collection']} ---")
        for i in range(len(results["ids"][0])):
            chunk_id = results["ids"][0][i]
            distance = results["distances"][0][i]
            text = results["documents"][0][i]
            print(f"  rank {i+1} | dist {distance:.4f} | {chunk_id}")
            print(f"  {text[:200]}...")
    print()