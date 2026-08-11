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
        groups[meta["chunk_id"]].append(entry_id)
    offset += BATCH_SIZE

ids_to_delete = []
for chunk_id, entry_ids in groups.items():
    if len(entry_ids) > 1:
        old_style = [eid for eid in entry_ids if eid == chunk_id]
        ids_to_delete.extend(old_style)

print(f"Old-style duplicate ids to delete: {len(ids_to_delete)}")

DELETE_BATCH = 1000
for i in range(0, len(ids_to_delete), DELETE_BATCH):
    batch = ids_to_delete[i:i + DELETE_BATCH]
    collection.delete(ids=batch)
    print(f"Deleted {i + len(batch)} / {len(ids_to_delete)}")

print(f"\nDone. Total chunks remaining: {collection.count()}")