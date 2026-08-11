import configparser
import chromadb
from openai import OpenAI

config = configparser.ConfigParser()
config.read("../docs/config.ini")
api_key = config["openai"]["api_key"]

client_openai = OpenAI(api_key=api_key)
client_chroma = chromadb.PersistentClient(path="data/chroma_db_test")

COLLECTION_NAME = "para_750"
EMBED_MODEL = "text-embedding-3-small"
CHAT_MODEL = "gpt-4o-mini"
TOP_K = 5

QUESTIONS = [
    "Who presented the Budget 2026-2027 speech, and in what role?",
    "What is the fiscal deficit estimated at in BE 2026-27?",
    "What is the fiscal deficit estimated at in RE 2025-26?",
    "What is the debt to GDP ratio estimated at in BE 2026-27?",
    "What is the total expenditure estimated for 2026-27?",
    "What is the outlay proposed for Biopharma SHAKTI, and over how many years?",
    "By how much is the outlay for the Electronics Components Manufacturing Scheme proposed to increase, and to what amount?",
    "What is the new MAT rate proposed, down from what earlier rate?",
    "What is the proposed public capex figure for FY2026-27, and what was it in BE 2025-26?",
    "What is the new STT rate on Futures, and what was the earlier rate?",
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