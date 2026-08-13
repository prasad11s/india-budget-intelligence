import configparser
import json
import re
import chromadb
from openai import OpenAI
from rank_bm25 import BM25Okapi

CHROMA_PATH = "../data/chroma_db"
COLLECTION_NAME = "budget_speeches_para750"
EMBED_MODEL = "text-embedding-3-small"
TOP_K = 5
CANDIDATE_POOL = 20  # each method contributes this many candidates before fusion
RRF_K = 60  # standard RRF constant, dampens the effect of rank 1 vs rank 2 etc
OUTPUT_PATH = "results_hybrid.json"

STOPWORDS = {
    "a", "an", "the", "is", "are", "was", "were", "be", "been", "being",
    "what", "which", "who", "whom", "how", "why", "when", "where",
    "did", "do", "does", "doing", "and", "or", "but", "if", "in", "on",
    "at", "to", "of", "for", "with", "about", "from", "by", "as", "into",
    "say", "said", "new", "earlier",
}

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


def tokenize(text):
    tokens = re.findall(r"\b\w+\b", text.lower())
    return [t for t in tokens if t not in STOPWORDS]


def matched_terms(query_tokens, doc_text):
    doc_tokens = set(tokenize(doc_text))
    return [t for t in dict.fromkeys(query_tokens) if t in doc_tokens]


def dense_ranking(client, collection, question):
    vector = client.embeddings.create(input=[question], model=EMBED_MODEL).data[0].embedding
    results = collection.query(query_embeddings=[vector], n_results=CANDIDATE_POOL)
    return results["ids"][0]  # already ordered best to worst


def bm25_ranking(bm25, all_ids, question):
    scores = bm25.get_scores(tokenize(question))
    ranked_indices = sorted(range(len(scores)), key=lambda i: scores[i], reverse=True)[:CANDIDATE_POOL]
    return [all_ids[i] for i in ranked_indices]


def reciprocal_rank_fusion(dense_ids, bm25_ids):
    scores = {}
    for rank, cid in enumerate(dense_ids):
        scores[cid] = scores.get(cid, 0) + 1 / (RRF_K + rank + 1)
    for rank, cid in enumerate(bm25_ids):
        scores[cid] = scores.get(cid, 0) + 1 / (RRF_K + rank + 1)
    return sorted(scores.items(), key=lambda x: x[1], reverse=True)[:TOP_K]


def main():
    client = OpenAI(api_key=load_api_key())
    chroma = chromadb.PersistentClient(path=CHROMA_PATH)
    collection = chroma.get_collection(COLLECTION_NAME)

    corpus = collection.get(include=["documents", "metadatas"])
    all_ids, all_docs, all_metas = corpus["ids"], corpus["documents"], corpus["metadatas"]
    id_to_doc = dict(zip(all_ids, all_docs))
    id_to_meta = dict(zip(all_ids, all_metas))

    tokenized_corpus = [tokenize(doc) for doc in all_docs]
    bm25 = BM25Okapi(tokenized_corpus)

    all_results = []

    for question in QUESTIONS:
        dense_ids = dense_ranking(client, collection, question)
        bm25_ids = bm25_ranking(bm25, all_ids, question)
        fused = reciprocal_rank_fusion(dense_ids, bm25_ids)

        q_tokens = tokenize(question)
        print("=" * 80)
        print(f"QUESTION: {question}")
        for cid, fused_score in fused:
            year = id_to_meta[cid].get("year", "unknown")
            matches = matched_terms(q_tokens, id_to_doc[cid])
            in_dense = cid in dense_ids
            in_bm25 = cid in bm25_ids
            print(f"\n  id={cid}  year={year}  fused_score={fused_score:.4f}  "
                  f"(dense={in_dense}, bm25={in_bm25})")
            print(f"  matched terms: {matches}")
            print(f"  {id_to_doc[cid][:200]}...")
        print()

        all_results.append({
            "question": question,
            "retrieved": [
                {
                    "id": cid,
                    "year": id_to_meta[cid].get("year", "unknown"),
                    "fused_score": fused_score,
                    "in_dense": cid in dense_ids,
                    "in_bm25": cid in bm25_ids,
                    "matched_terms": matched_terms(q_tokens, id_to_doc[cid]),
                }
                for cid, fused_score in fused
            ]
        })

    with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
        json.dump(all_results, f, indent=2)
    print(f"Saved results to {OUTPUT_PATH}")


if __name__ == "__main__":
    main()