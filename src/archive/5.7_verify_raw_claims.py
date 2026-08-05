import configparser
import chromadb
from openai import OpenAI

config = configparser.ConfigParser()
config.read("docs/config.ini")
openai_client = OpenAI(api_key=config["openai"]["api_key"])

EMBEDDING_MODEL = "text-embedding-3-large"
TOP_K = 8

chroma_client = chromadb.PersistentClient(path="data/chroma_db")
collection = chroma_client.get_collection(name="budget_intelligence")

CHECK_QUERIES = [
    "fiscal deficit revised target 2018-19 3 percent Economic Survey",
    "education budget trend India last 10 years",
]

for query in CHECK_QUERIES:
    print(f"\n{'='*80}\nQUERY: {query}\n{'='*80}")
    response = openai_client.embeddings.create(model=EMBEDDING_MODEL, input=[query])
    query_vector = response.data[0].embedding
    results = collection.query(query_embeddings=[query_vector], n_results=TOP_K)

    for i, (text, meta) in enumerate(zip(results["documents"][0], results["metadatas"][0])):
        print(f"\n--- Result {i+1} ({meta['doc_type']}, {meta['year']}) ---")
        print(text[:400])