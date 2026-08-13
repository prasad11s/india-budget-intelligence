import json
import re
import chromadb
from rank_bm25 import BM25Okapi
from nltk.stem import PorterStemmer

CHROMA_PATH = "../data/chroma_db"
COLLECTION_NAME = "budget_speeches_para750"
TOP_K = 5
OUTPUT_PATH = "results_bm25_stemmed.json"

STOPWORDS = {
    "a", "an", "the", "is", "are", "was", "were", "be", "been", "being",
    "what", "which", "who", "whom", "how", "why", "when", "where",
    "did", "do", "does", "doing", "and", "or", "but", "if", "in", "on",
    "at", "to", "of", "for", "with", "about", "from", "by", "as", "into",
    "say", "said", "new", "earlier",
}

stemmer = PorterStemmer()

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


def tokenize(text):
    tokens = re.findall(r"\b\w+\b", text.lower())
    tokens = [t for t in tokens if t not in STOPWORDS]
    return [stemmer.stem(t) for t in tokens]


def matched_terms(query_tokens, doc_text):
    doc_tokens = set(tokenize(doc_text))
    return [t for t in dict.fromkeys(query_tokens) if t in doc_tokens]


def main():
    chroma = chromadb.PersistentClient(path=CHROMA_PATH)
    collection = chroma.get_collection(COLLECTION_NAME)

    data = collection.get(include=["documents", "metadatas"])
    ids, docs, metas = data["ids"], data["documents"], data["metadatas"]

    tokenized_corpus = [tokenize(doc) for doc in docs]
    bm25 = BM25Okapi(tokenized_corpus)

    all_results = []

    for question in QUESTIONS:
        q_tokens = tokenize(question)
        scores = bm25.get_scores(q_tokens)
        top_indices = sorted(range(len(scores)), key=lambda i: scores[i], reverse=True)[:TOP_K]

        print("=" * 80)
        print(f"QUESTION: {question}")
        print(f"  stemmed query tokens: {q_tokens}")
        for i in top_indices:
            year = metas[i].get("year", "unknown")
            matches = matched_terms(q_tokens, docs[i])
            print(f"\n  id={ids[i]}  year={year}  score={scores[i]:.4f}")
            print(f"  matched terms: {matches}")
            print(f"  {docs[i][:200]}...")
        print()

        all_results.append({
            "question": question,
            "retrieved": [
                {
                    "id": ids[i],
                    "year": metas[i].get("year", "unknown"),
                    "score": float(scores[i]),
                    "matched_terms": matched_terms(q_tokens, docs[i]),
                }
                for i in top_indices
            ]
        })

    with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
        json.dump(all_results, f, indent=2)
    print(f"Saved results to {OUTPUT_PATH}")


if __name__ == "__main__":
    main()  