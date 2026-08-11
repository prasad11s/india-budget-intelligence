import configparser
import chromadb
from openai import OpenAI

config = configparser.ConfigParser()
config.read("../docs/config.ini")
api_key = config["openai"]["api_key"]

client_openai = OpenAI(api_key=api_key)
client_chroma = chromadb.PersistentClient(path="data/chroma_db_test")

EMBED_MODEL = "text-embedding-3-small"
COLLECTIONS = ["fixed_500", "fixed_1000", "para_500", "para_1000"]
TOP_K = 3

QUESTIONS = [
    "What is the fiscal deficit estimated at in BE 2026-27?",
    "What is the debt to GDP ratio estimated at in BE 2026-27?",
    "What is the new MAT rate proposed, down from what earlier rate?",
    "What is the new STT rate on Futures, and what was the earlier rate?",
]

def embed_query(text):
    response = client_openai.embeddings.create(input=[text], model=EMBED_MODEL)
    return response.data[0].embedding

for question in QUESTIONS:
    print("=" * 80)
    print(f"QUESTION: {question}")
    query_vector = embed_query(question)

    for name in COLLECTIONS:
        collection = client_chroma.get_collection(name=name)
        results = collection.query(query_embeddings=[query_vector], n_results=TOP_K)

        print(f"\n--- {name} ---")
        for i in range(len(results["ids"][0])):
            chunk_id = results["ids"][0][i]
            distance = results["distances"][0][i]
            text = results["documents"][0][i]
            print(f"  rank {i+1} | dist {distance:.4f} | {chunk_id}")
            print(f"  {text[:200]}...")
    print()