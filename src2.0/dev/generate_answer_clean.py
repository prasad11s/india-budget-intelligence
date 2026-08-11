
import configparser
import chromadb
from openai import OpenAI

config = configparser.ConfigParser()
config.read("../docs/config.ini")
api_key = config["openai"]["api_key"]

client_openai = OpenAI(api_key=api_key)
client_chroma = chromadb.PersistentClient(path="data/chroma_db_test")

COLLECTION_NAME = "budget_at_a_glance_para_750_clean"
EMBED_MODEL = "text-embedding-3-small"
CHAT_MODEL = "gpt-4o-mini"
TOP_K = 5

QUESTIONS = [
    "What is the Budget Estimate for Defence for 2026-27?",
    "What is the Budget Estimate for Education for 2026-27?",
    "What is the Revised Estimate for Defence for 2025-26, compared to the Budget Estimate for 2026-27?",
    "What is the fiscal deficit estimated at in BE 2026-27, in rupees crore and as a percentage of GDP?",
    "What is the allocation for the Samagra Shiksha scheme in BE 2026-27?",
]

def embed_query(text):
    response = client_openai.embeddings.create(input=[text], model=EMBED_MODEL)
    return response.data[0].embedding

def retrieve_chunks(question):
    query_vector = embed_query(question)
    collection = client_chroma.get_collection(name=COLLECTION_NAME)
    results = collection.query(query_embeddings=[query_vector], n_results=TOP_K)
    return results["documents"][0], results["ids"][0]

def generate_answer(question, chunks):
    context = "\n\n---\n\n".join(chunks)
    prompt = f"""Answer the question using ONLY the context below. If the answer is not in the context, say "insufficient data."

Context:
{context}

Question: {question}"""

    response = client_openai.chat.completions.create(
        model=CHAT_MODEL,
        temperature=0,
        messages=[{"role": "user", "content": prompt}]
    )
    return response.choices[0].message.content

for question in QUESTIONS:
    chunks, chunk_ids = retrieve_chunks(question)
    answer = generate_answer(question, chunks)
    print("=" * 80)
    print(f"QUESTION: {question}")
    print(f"RETRIEVED: {chunk_ids}")
    print(f"ANSWER: {answer}")
    print()