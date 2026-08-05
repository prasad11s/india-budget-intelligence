import configparser
import chromadb
from openai import OpenAI

config = configparser.ConfigParser()
config.read("docs/config.ini")
openai_client = OpenAI(api_key=config["openai"]["api_key"])

EMBEDDING_MODEL = "text-embedding-3-large"
TOP_K = 5

chroma_client = chromadb.PersistentClient(path="data/chroma_db")
collection = chroma_client.get_collection(name="budget_intelligence")

query = "What was the fiscal deficit target in the 2015 budget?"

response = openai_client.embeddings.create(model=EMBEDDING_MODEL, input=[query])
query_vector = response.data[0].embedding

results = collection.query(query_embeddings=[query_vector], n_results=TOP_K)

for i in range(len(results["documents"][0])):
    print(f"\n--- Result {i+1} ---")
    print(f"Metadata: {results['metadatas'][0][i]}")
    print(f"Text preview: {results['documents'][0][i][:200]}...")