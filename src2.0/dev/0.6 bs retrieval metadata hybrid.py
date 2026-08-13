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
CANDIDATE_POOL = 20
RRF_K = 60
OUTPUT_PATH = "results_metadata_hybrid.json"

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


def extract_years(question):
    years = set()
    for match in re.finditer(r"\b(20\d{2})-(\d{2})\b", question):
        years.add(int(match.group(1)))
    for match in re.finditer(r"\b(20\d{2})(?:-(\d{4}))?\b", question):
        years.add(int(match.group(1)))
    return sorted(years)


def year_to_metadata_candidates(year):
    next_two = str(year + 1)[-2:]
    return [f"{year}{next_two}", f"{year}_{next_two}"]


def get_subset(collection, year_candidates=None):
    """Return ids/docs/metas for either the full corpus or a year-filtered subset."""
    kwargs = {"include": ["documents", "metadatas"]}
    if year_candidates:
        kwargs["where"] = {"year": {"$in": year_candidates}}
    data = collection.get(**kwargs)
    return data["ids"], data["documents"], data["metadatas"]


def dense_ranking(client, ids, docs, metas, question, chroma_client, where=None):
    vector = client.embeddings.create(input=[question], model=EMBED_MODEL).data[0].embedding
    kwargs = {"query_embeddings": [vector], "n_results": min(CANDIDATE_POOL, len(ids))}
    if where:
        kwargs["where"] = where
    results = chroma_client.query(**kwargs)
    return results["ids"][0]


def bm25_ranking(ids, docs, question):
    tokenized_corpus = [tokenize(doc) for doc in docs]
    bm25 = BM25Okapi(tokenized_corpus)
    scores = bm25.get_scores(tokenize(question))
    top_indices = sorted(range(len(scores)), key=lambda i: scores[i], reverse=True)[:min(CANDIDATE_POOL, len(ids))]
    return [ids[i] for i in top_indices]


def reciprocal_rank_fusion(dense_ids, bm25_ids):
    scores = {}
    for rank, cid in enumerate(dense_ids):
        scores[cid] = scores.get(cid, 0) + 1 / (RRF_K + rank + 1)
    for rank, cid in enumerate(bm25_ids):
        scores[cid] = scores.get(cid, 0) + 1 / (RRF_K + rank + 1)
    return sorted(scores.items(), key=lambda x: x[1], reverse=True)


def main():
    client = OpenAI(api_key=load_api_key())
    chroma = chromadb.PersistentClient(path=CHROMA_PATH)
    collection = chroma.get_collection(COLLECTION_NAME)

    all_results = []

    for question in QUESTIONS:
        years = extract_years(question)
        print("=" * 80)
        print(f"QUESTION: {question}")
        print(f"  years detected: {years}")

        fused_all = []

        if not years:
            ids, docs, metas = get_subset(collection)
            id_to_meta = dict(zip(ids, metas))
            id_to_doc = dict(zip(ids, docs))
            dense_ids = dense_ranking(client, ids, docs, metas, question, collection)
            bm25_ids = bm25_ranking(ids, docs, question)
            fused = reciprocal_rank_fusion(dense_ids, bm25_ids)[:TOP_K]
            fused_all.extend((cid, score, id_to_meta[cid], id_to_doc[cid]) for cid, score in fused)
        else:
            for year in years:
                candidates = year_to_metadata_candidates(year)
                where = {"year": {"$in": candidates}}
                ids, docs, metas = get_subset(collection, candidates)
                if not ids:
                    continue
                id_to_meta = dict(zip(ids, metas))
                id_to_doc = dict(zip(ids, docs))
                dense_ids = dense_ranking(client, ids, docs, metas, question, collection, where=where)
                bm25_ids = bm25_ranking(ids, docs, question)
                fused = reciprocal_rank_fusion(dense_ids, bm25_ids)[:TOP_K]
                fused_all.extend((cid, score, id_to_meta[cid], id_to_doc[cid]) for cid, score in fused)

        for cid, score, meta, doc in fused_all:
            year_val = meta.get("year", "unknown")
            print(f"\n  id={cid}  year={year_val}  fused_score={score:.4f}")
            print(f"  {doc[:200]}...")
        print()

        all_results.append({
            "question": question,
            "years_detected": years,
            "retrieved": [
                {"id": cid, "year": meta.get("year", "unknown"), "fused_score": score}
                for cid, score, meta, doc in fused_all
            ]
        })

    with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
        json.dump(all_results, f, indent=2)
    print(f"Saved results to {OUTPUT_PATH}")


if __name__ == "__main__":
    main()