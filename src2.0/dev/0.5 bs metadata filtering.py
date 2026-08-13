import configparser
import json
import re
import chromadb
from openai import OpenAI

CHROMA_PATH = "../data/chroma_db"
COLLECTION_NAME = "budget_speeches_para750"
EMBED_MODEL = "text-embedding-3-small"
TOP_K = 5
OUTPUT_PATH = "results_metadata.json"

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


def extract_years(question):
    """Find years mentioned in the question, as fiscal-year start years (int)."""
    years = set()

    # pattern like "2016-17" or "BE 2026-27"
    for match in re.finditer(r"\b(20\d{2})-(\d{2})\b", question):
        years.add(int(match.group(1)))

    # standalone 4-digit years like "2025" or "2026-2027" (calendar-year form)
    for match in re.finditer(r"\b(20\d{2})(?:-(\d{4}))?\b", question):
        years.add(int(match.group(1)))

    return sorted(years)


def year_to_metadata_candidates(year):
    """Generate the metadata year strings this fiscal year could be stored as."""
    next_two = str(year + 1)[-2:]
    return [f"{year}{next_two}", f"{year}_{next_two}"]


def dense_query(client, collection, question, where=None, n_results=TOP_K):
    vector = client.embeddings.create(input=[question], model=EMBED_MODEL).data[0].embedding
    kwargs = {"query_embeddings": [vector], "n_results": n_results}
    if where:
        kwargs["where"] = where
    results = collection.query(**kwargs)
    return results["ids"][0], results["documents"][0], results["metadatas"][0], results["distances"][0]


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

        combined = []

        if not years:
            # no year found, fall back to unfiltered dense search
            ids, docs, metas, distances = dense_query(client, collection, question)
            combined = list(zip(ids, docs, metas, distances))
        else:
            # one filtered retrieval per detected year, merged
            for year in years:
                candidates = year_to_metadata_candidates(year)
                where = {"year": {"$in": candidates}}
                ids, docs, metas, distances = dense_query(client, collection, question, where=where)
                combined.extend(zip(ids, docs, metas, distances))

        for cid, doc, meta, dist in combined:
            year_val = meta.get("year", "unknown")
            print(f"\n  id={cid}  year={year_val}  distance={dist:.4f}")
            print(f"  {doc[:200]}...")
        print()

        all_results.append({
            "question": question,
            "years_detected": years,
            "retrieved": [
                {"id": cid, "year": meta.get("year", "unknown"), "distance": dist}
                for cid, doc, meta, dist in combined
            ]
        })

    with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
        json.dump(all_results, f, indent=2)
    print(f"Saved results to {OUTPUT_PATH}")


if __name__ == "__main__":
    main()