import configparser
import json
import chromadb
from openai import OpenAI

CHROMA_PATH = "../data/chroma_db"
COLLECTION_NAME = "budget_speeches_para750"
EMBED_MODEL = "text-embedding-3-small"
TOP_K = 5
OUTPUT_PATH = "results_dense.json"

QUESTIONS = [
    "How many parts is the budget divided into?",
    "What did the budget say about roads?",
    "What did the 2016-17 budget say about roads?",
    "What did the budget say about transportation?",
    "What did the 2008-09 budget say about transportation?",
    "Compare the 2025 budget with the 2015 budget.",
    "What is the fiscal deficit estimated at in BE 2026-27?",
    "What is the new MAT rate proposed, down from what earlier rate?",
    "Who presented the Budget 2026-2027 speech, and in what role?",
    "What is the new STT rate on Futures, and what was the earlier rate?",
]


def load_api_key():
    config = configparser.ConfigParser()
    config.read("../../docs/config.ini")
    return config["openai"]["api_key"]


def embed_query(client, text):
    response = client.embeddings.create(input=[text], model=EMBED_MODEL)
    return response.data[0].embedding


def retrieve(collection, client, question):
    vector = embed_query(client, question)
    results = collection.query(query_embeddings=[vector], n_results=TOP_K)
    return results["ids"][0], results["documents"][0], results["metadatas"][0], results["distances"][0]


def main():
    client = OpenAI(api_key=load_api_key())
    chroma = chromadb.PersistentClient(path=CHROMA_PATH)
    collection = chroma.get_collection(COLLECTION_NAME)

    all_results = []

    for question in QUESTIONS:
        ids, docs, metas, distances = retrieve(collection, client, question)
        print("=" * 80)
        print(f"QUESTION: {question}")
        for chunk_id, doc, meta, dist in zip(ids, docs, metas, distances):
            year = meta.get("year", "unknown")
            print(f"\n  id={chunk_id}  year={year}  distance={dist:.4f}")
            print(f"  {doc[:200]}...")
        print()

        all_results.append({
            "question": question,
            "retrieved": [
                {"id": cid, "year": meta.get("year", "unknown"), "distance": dist}
                for cid, meta, dist in zip(ids, metas, distances)
            ]
        })

    with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
        json.dump(all_results, f, indent=2)
    print(f"Saved results to {OUTPUT_PATH}")


if __name__ == "__main__":
    main()