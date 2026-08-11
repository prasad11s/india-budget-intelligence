import json
import configparser
import chromadb
from openai import OpenAI

config = configparser.ConfigParser()
config.read("../docs/config.ini")
api_key = config["openai"]["api_key"]

client_openai = OpenAI(api_key=api_key)
client_chroma = chromadb.PersistentClient(path="data/chroma_db_test")

CHUNK_FILE = "data/processed/budget_at_a_glance_chunks_para750_clean.json"
COLLECTION_NAME = "budget_at_a_glance_para_750_clean"
EMBED_MODEL = "text-embedding-3-small"

with open(CHUNK_FILE, "r", encoding="utf-8") as f:
    chunks = json.load(f)

collection = client_chroma.get_or_create_collection(name=COLLECTION_NAME)

texts = [c["text"] for c in chunks]
ids = [f"baag_clean_para750_{i:04d}" for i in range(len(chunks))]
metadatas = [{
    "source": "budget_at_a_glance_clean",
    "pages": ",".join(str(p) for p in c["pages"])
} for c in chunks]

response = client_openai.embeddings.create(input=texts, model=EMBED_MODEL)
embeddings = [item.embedding for item in response.data]

collection.add(ids=ids, embeddings=embeddings, documents=texts, metadatas=metadatas)

print(f"Added {len(ids)} chunks to collection '{COLLECTION_NAME}'")