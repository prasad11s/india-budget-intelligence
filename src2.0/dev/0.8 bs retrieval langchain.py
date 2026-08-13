import configparser
import json
import chromadb
from langchain_openai import OpenAIEmbeddings
from langchain_chroma import Chroma
from langchain_community.retrievers import BM25Retriever
from langchain_classic.retrievers import EnsembleRetriever

CHROMA_PATH = "../data/chroma_db"
COLLECTION_NAME = "budget_speeches_para750"
EMBED_MODEL = "text-embedding-3-small"
TOP_K = 5
OUTPUT_PATH = "results_langchain.json"

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


def main():
    api_key = load_api_key()
    embeddings = OpenAIEmbeddings(model=EMBED_MODEL, api_key=api_key)

    # wrap the EXISTING chroma_db, do not rebuild or re-embed anything
    chroma_client = chromadb.PersistentClient(path=CHROMA_PATH)
    vectorstore = Chroma(
        client=chroma_client,
        collection_name=COLLECTION_NAME,
        embedding_function=embeddings,
    )
    dense_retriever = vectorstore.as_retriever(search_kwargs={"k": TOP_K})

    collection = chroma_client.get_collection(COLLECTION_NAME)
    corpus = collection.get(include=["documents", "metadatas"])
    bm25_retriever = BM25Retriever.from_texts(corpus["documents"], metadatas=corpus["metadatas"])
    bm25_retriever.k = TOP_K

    ensemble = EnsembleRetriever(retrievers=[dense_retriever, bm25_retriever], weights=[0.5, 0.5])

    all_results = []

    for question in QUESTIONS:
        docs = ensemble.invoke(question)[:TOP_K]

        print("=" * 80)
        print(f"QUESTION: {question}")
        for doc in docs:
            year = doc.metadata.get("year", "unknown")
            print(f"\n  year={year}")
            print(f"  {doc.page_content[:200]}...")
        print()

        all_results.append({
            "question": question,
            "retrieved": [
                {"year": doc.metadata.get("year", "unknown"), "text_preview": doc.page_content[:200]}
                for doc in docs
            ]
        })

    with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
        json.dump(all_results, f, indent=2)
    print(f"Saved results to {OUTPUT_PATH}")


if __name__ == "__main__":
    main()