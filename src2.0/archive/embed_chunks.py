import json
import configparser
import chromadb
from openai import OpenAI

config = configparser.ConfigParser()
config.read("../docs/config.ini")
api_key = config["openai"]["api_key"]

client_openai = OpenAI(api_key=api_key)
client_chroma = chromadb.PersistentClient(path="data/chroma_db_test")

CHUNK_FILE = "data/processed/chunks_para_1000.json"
COLLECTION_NAME = "para_1000"
EMBED_MODEL = "text-embedding-3-small"

with open(CHUNK_FILE, "r", encoding="utf-8") as f:
    chunks = json.load(f)

collection = client_chroma.get_or_create_collection(name=COLLECTION_NAME)

texts = [c["text"] for c in chunks]
ids = [c["chunk_id"] for c in chunks]
metadatas = [{
    "year": c["year"],
    "doc_type": c["doc_type"],
    "filename": c["filename"],
    "page_start": c["page_start"],
    "page_end": c["page_end"],
    "chunk_method": c["chunk_method"]
} for c in chunks]

response = client_openai.embeddings.create(input=texts, model=EMBED_MODEL)
embeddings = [item.embedding for item in response.data]

collection.add(ids=ids, embeddings=embeddings, documents=texts, metadatas=metadatas)

print(f"Added {len(ids)} chunks to collection '{COLLECTION_NAME}'")