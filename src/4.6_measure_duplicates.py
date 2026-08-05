import configparser
import chromadb
from collections import Counter

config = configparser.ConfigParser()
config.read("docs/config.ini")

chroma_client = chromadb.PersistentClient(path="data/chroma_db")
collection = chroma_client.get_collection(name="budget_intelligence")

BATCH_SIZE = 5000
total = collection.count()
print(f"Total entries in collection: {total}")

chunk_ids = []
offset = 0
while offset < total:
    batch = collection.get(include=["metadatas"], limit=BATCH_SIZE, offset=offset)
    chunk_ids.extend(m["chunk_id"] for m in batch["metadatas"])
    offset += BATCH_SIZE
    print(f"Fetched {len(chunk_ids)} / {total}")

print(f"\nUnique chunk_ids: {len(set(chunk_ids))}")

id_counts = Counter(chunk_ids)
duplicates = {cid: count for cid, count in id_counts.items() if count > 1}

print(f"Number of chunk_ids that are duplicated: {len(duplicates)}")

sample = list(duplicates.items())[:5]
print("\nSample duplicated chunk_ids:")
for cid, count in sample:
    print(f"  {cid} appears {count} times")