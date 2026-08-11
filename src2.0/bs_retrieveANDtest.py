import configparser
import chromadb
from openai import OpenAI

CHROMA_PATH = "data/chroma_db"
COLLECTION_NAME = "budget_speeches_para750"
EMBED_MODEL = "text-embedding-3-small"
CHAT_MODEL = "gpt-4o-mini"
TOP_K = 5

QUESTIONS = [
    "Who presented the Budget 2026-2027 speech, and in what role?",
    "What is the fiscal deficit estimated at in BE 2026-27?",
    "What is the debt to GDP ratio estimated at in BE 2026-27?",
    "What is the new MAT rate proposed, down from what earlier rate?",
    "What is the new STT rate on Futures, and what was the earlier rate?",
]


def load_api_key():
    config = configparser.ConfigParser()
    config.read("../docs/config.ini")
    return config["openai"]["api_key"]


def embed_query(client, text):
    response = client.embeddings.create(input=[text], model=EMBED_MODEL)
    return response.data[0].embedding


def retrieve(collection, client, question):
    vector = embed_query(client, question)
    results = collection.query(query_embeddings=[vector], n_results=TOP_K)
    return results["documents"][0], results["ids"][0]


def generate_answer(client, question, chunks):
    context = "\n\n---\n\n".join(chunks)
    prompt = f"""Answer the question using ONLY the context below. If the answer is not in the context, say "insufficient data."

Context:
{context}

Question: {question}"""
    response = client.chat.completions.create(
        model=CHAT_MODEL, temperature=0, messages=[{"role": "user", "content": prompt}]
    )
    return response.choices[0].message.content


def main():
    client = OpenAI(api_key=load_api_key())
    chroma = chromadb.PersistentClient(path=CHROMA_PATH)
    collection = chroma.get_collection(COLLECTION_NAME)

    for question in QUESTIONS:
        chunks, ids = retrieve(collection, client, question)
        answer = generate_answer(client, question, chunks)
        print("=" * 80)
        print(f"QUESTION: {question}")
        print(f"RETRIEVED: {ids}")
        print(f"ANSWER: {answer}")
        print()


if __name__ == "__main__":
    main()