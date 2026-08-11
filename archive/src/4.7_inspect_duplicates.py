import configparser
import chromadb
from collections import defaultdict

config = configparser.ConfigParser()
config.read("docs/config.ini")

chroma_client = chromadb.PersistentClient(path="data/chroma_db")
collection = chroma_client.get_collection(name="budget_intelligence")

BATCH_SIZE = 5000
total = collection.count()

groups = defaultdict(list)
offset = 0
while offset < total:
    batch = collection.get(include=["metadatas"], limit=BATCH_SIZE, offset=offset)
    for entry_id, meta in zip(batch["ids"], batch["metadatas"]):
        groups[meta["chunk_id"]].append((entry_id, meta.get("year")))
    offset += BATCH_SIZE

duplicated = {cid: entries for cid, entries in groups.items() if len(entries) > 1}
print(f"Duplicated chunk_ids: {len(duplicated)}")

sample = list(duplicated.items())[:5]
for cid, entries in sample:
    print(f"\nchunk_id: {cid}")
    for entry_id, year in entries:
        print(f"  actual id: {entry_id}, year field: {year}")