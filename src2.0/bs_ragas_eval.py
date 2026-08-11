import os
import configparser
import chromadb
from openai import OpenAI
from datasets import Dataset
from ragas import evaluate
from ragas.metrics import faithfulness, answer_relevancy, context_precision, context_recall

CHROMA_PATH = "data/chroma_db"
COLLECTION_NAME = "budget_speeches_para750"
EMBED_MODEL = "text-embedding-3-small"
CHAT_MODEL = "gpt-4o-mini"
TOP_K = 5

# Add more questions as the corpus scales. ground_truth left blank still
# works for faithfulness and answer_relevancy, just not for the other two.
GOLDEN_SET = [
    {
        "question": "What is the fiscal deficit estimated at in BE 2026-27?",
        "ground_truth": "4.3 percent of GDP",
    },
    {
        "question": "What is the debt to GDP ratio estimated at in BE 2026-27?",
        "ground_truth": "55.6 percent of GDP",
    },
    {
        "question": "What is the new MAT rate proposed, down from what earlier rate?",
        "ground_truth": "14 percent, down from 15 percent",
    },
    {
        "question": "What is the new STT rate on Futures, and what was the earlier rate?",
        "ground_truth": "0.05 percent, up from 0.02 percent",
    },
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
    return results["documents"][0]


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
    api_key = load_api_key()
    os.environ["OPENAI_API_KEY"] = api_key  # ragas' own judge model reads this env var
    client = OpenAI(api_key=api_key)
    chroma = chromadb.PersistentClient(path=CHROMA_PATH)
    collection = chroma.get_collection(COLLECTION_NAME)

    rows = []
    for item in GOLDEN_SET:
        contexts = retrieve(collection, client, item["question"])
        answer = generate_answer(client, item["question"], contexts)
        rows.append({
            "question": item["question"],
            "contexts": contexts,
            "answer": answer,
            "ground_truth": item["ground_truth"],
        })

    dataset = Dataset.from_list(rows)
    result = evaluate(dataset, metrics=[faithfulness, answer_relevancy, context_precision, context_recall])
    print(result)
    result.to_pandas().to_csv("ragas_results.csv", index=False)
    print("Saved to ragas_results.csv")


if __name__ == "__main__":
    main()