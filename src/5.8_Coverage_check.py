import configparser
import chromadb
from collections import defaultdict

config = configparser.ConfigParser()
config.read("docs/config.ini")

chroma_client = chromadb.PersistentClient(path="data/chroma_db")
collection = chroma_client.get_collection(name="budget_intelligence")

BATCH_SIZE = 5000
total = collection.count()

doc_type_years = defaultdict(set)
doc_type_counts = defaultdict(int)

offset = 0
while offset < total:
    batch = collection.get(include=["metadatas"], limit=BATCH_SIZE, offset=offset)
    for meta in batch["metadatas"]:
        doc_type_years[meta["doc_type"]].add(meta["year"])
        doc_type_counts[meta["doc_type"]] += 1
    offset += BATCH_SIZE

for doc_type in sorted(doc_type_counts.keys()):
    years = sorted(doc_type_years[doc_type])
    print(f"\n{doc_type}: {doc_type_counts[doc_type]} chunks, {len(years)} distinct years")
    print(f"Years present: {years}")