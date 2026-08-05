import configparser
import chromadb
from openai import OpenAI

config = configparser.ConfigParser()
config.read("docs/config.ini")
openai_client = OpenAI(api_key=config["openai"]["api_key"])

EMBEDDING_MODEL = "text-embedding-3-large"
TOP_K = 5

DOC_TYPE_LABELS = {
    "budget_speeches": "Budget Speech",
    "economic_surveys": "Economic Survey",
    "budget_documents": "Budget Document",
}

chroma_client = chromadb.PersistentClient(path="data/chroma_db")
collection = chroma_client.get_collection(name="budget_intelligence")

query = "What was the fiscal deficit target in the 2015 budget?"

response = openai_client.embeddings.create(model=EMBEDDING_MODEL, input=[query])
query_vector = response.data[0].embedding

results = collection.query(query_embeddings=[query_vector], n_results=TOP_K)


def format_year(year_raw):
    if "-" in year_raw:
        return year_raw
    return f"{year_raw[:4]}-{year_raw[4:]}"


context_blocks = []
for text, meta in zip(results["documents"][0], results["metadatas"][0]):
    label = f"{format_year(meta['year'])} {DOC_TYPE_LABELS[meta['doc_type']]}"
    context_blocks.append(f"[Source: {label}]\n{text}")

context = "\n\n".join(context_blocks)

prompt = f"""Answer the question using only the context below. Write in complete, natural sentences. When you use information from a source, mention it naturally, for example "According to the 2014-15 Budget Speech...". If the context does not contain enough information to answer, say so clearly.

Context:
{context}

Question: {query}

Answer:"""

print(prompt)