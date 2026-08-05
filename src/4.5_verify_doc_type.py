import chromadb
 
chroma_client = chromadb.PersistentClient(path="data/chroma_db")
collection = chroma_client.get_or_create_collection("budget_intelligence")
 
for doc_type in ["budget_speeches", "economic_surveys", "budget_documents"]:
    result = collection.get(where={"doc_type": doc_type}, limit=1, include=["documents", "metadatas"])
    if result["ids"]:
        print(f"\n=== {doc_type}: FOUND ===")
        print(f"Sample ID: {result['ids'][0]}")
        print(f"Metadata: {result['metadatas'][0]}")
        print(f"Text preview: {result['documents'][0][:120]}")
    else:
        print(f"\n=== {doc_type}: NOT FOUND ===")
 