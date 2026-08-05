import chromadb

chroma_client = chromadb.PersistentClient(path="data/chroma_db")
collection = chroma_client.get_or_create_collection("budget_intelligence")

print(f"Total chunks in collection: {collection.count()}")

sample = collection.get(limit=3, include=["documents", "metadatas"])

for i in range(len(sample["ids"])):
    print(f"\n--- Record {i+1} ---")
    print(f"ID: {sample['ids'][i]}")
    print(f"Metadata: {sample['metadatas'][i]}")
    print(f"Text preview: {sample['documents'][i][:200]}")