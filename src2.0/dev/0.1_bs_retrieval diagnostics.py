import configparser
import chromadb
from openai import OpenAI

CHROMA_PATH = "../data/chroma_db"
COLLECTION_NAME = "budget_speeches_para750"
EMBED_MODEL = "text-embedding-3-small"
TOP_K = 5

QUESTIONS = [
    "How many parts is the budget divided into?",
    "What did the budget say about roads?",
    "What did the budget say about transportation?",
    "Compare the 2025 budget with the 2015 budget.",
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
    return results["documents"][0], results["metadatas"][0], results["distances"][0]


def main():
    client = OpenAI(api_key=load_api_key())
    chroma = chromadb.PersistentClient(path=CHROMA_PATH)
    collection = chroma.get_collection(COLLECTION_NAME)

    for question in QUESTIONS:
        docs, metas, distances = retrieve(collection, client, question)
        print("=" * 80)
        print(f"QUESTION: {question}")
        for doc, meta, dist in zip(docs, metas, distances):
            year = meta.get("year", "unknown")
            print(f"\n  year={year}  distance={dist:.4f}")
            print(f"  {doc[:200]}...")
        print()


if __name__ == "__main__":
    main()