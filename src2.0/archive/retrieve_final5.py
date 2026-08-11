import configparser
import chromadb
from openai import OpenAI

config = configparser.ConfigParser()
config.read("../docs/config.ini")
api_key = config["openai"]["api_key"]

client_openai = OpenAI(api_key=api_key)
client_chroma = chromadb.PersistentClient(path="data/chroma_db_test")

COLLECTIONS = [
    {"name": "para_500", "model": "text-embedding-3-small"},
    {"name": "para_1000", "model": "text-embedding-3-small"},
    {"name": "para_500_large", "model": "text-embedding-3-large"},
    {"name": "para_1000_large", "model": "text-embedding-3-large"},
]
TOP_K = 5

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

    for col in COLLECTIONS:
        query_vector = embed_query(question, col["model"])
        collection = client_chroma.get_collection(name=col["name"])
        results = collection.query(query_embeddings=[query_vector], n_results=TOP_K)

        print(f"\n--- {col['name']} ---")
        for i in range(len(results["ids"][0])):
            chunk_id = results["ids"][0][i]
            distance = results["distances"][0][i]
            text = results["documents"][0][i]
            print(f"  rank {i+1} | dist {distance:.4f} | {chunk_id}")
            print(f"  {text[:200]}...")
    print()