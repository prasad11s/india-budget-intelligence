import json
import glob
import configparser
import chromadb
from collections import defaultdict

config = configparser.ConfigParser()
config.read("docs/config.ini")

chroma_client = chromadb.PersistentClient(path="data/chroma_db")
collection = chroma_client.get_collection(name="budget_intelligence")

BATCH_SIZE = 5000
total = collection.count()

chroma_years = defaultdict(set)
offset = 0
while offset < total:
    batch = collection.get(include=["metadatas"], limit=BATCH_SIZE, offset=offset)
    for meta in batch["metadatas"]:
        chroma_years[meta["doc_type"]].add(meta["year"])
    offset += BATCH_SIZE

DOC_TYPES = ["budget_speeches", "budget_documents", "economic_surveys"]

for doc_type in DOC_TYPES:
    print(f"\n{'='*60}\n{doc_type}\n{'='*60}")
    chunk_files = glob.glob(f"data/chunks/{doc_type}/*.json")

    chunk_years = set()
    for filepath in chunk_files:
        with open(filepath, encoding="utf-8") as f:
            chunks = json.load(f)
        for chunk in chunks:
            meta = chunk.get("metadata", chunk)
            year = meta.get("year")
            if year:
                chunk_years.add(year)

    in_chunks_not_chroma = chunk_years - chroma_years[doc_type]
    print(f"Years in chunk files (from actual JSON metadata): {len(chunk_years)}")
    print(f"Years in ChromaDB: {len(chroma_years[doc_type])}")
    print(f"Chunked but NOT in ChromaDB: {sorted(in_chunks_not_chroma)}")