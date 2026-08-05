import re
import json
import configparser
import chromadb
from collections import defaultdict
from openai import OpenAI

config = configparser.ConfigParser()
config.read("docs/config.ini")
openai_client = OpenAI(api_key=config["openai"]["api_key"])

EMBEDDING_MODEL = "text-embedding-3-large"
CHAT_MODEL = "gpt-4o-mini"
TOP_K = 5

DOC_TYPE_LABELS = {
    "budget_speeches": "Budget Speech",
    "economic_surveys": "Economic Survey",
    "budget_documents": "Budget Document",
}

chroma_client = chromadb.PersistentClient(path="data/chroma_db")
collection = chroma_client.get_collection(name="budget_intelligence")

GOLDEN_QUESTIONS = [
    "What was the fiscal deficit target for 2018-19?",
    "What was the fiscal deficit for 2013-14?",
    "What was the fiscal deficit target in the 2015 budget?",
    "What did the 1947-48 budget say about the country's financial situation?",
    "What was India's fiscal deficit target for 2025-26?",
    "What was the revenue deficit for 2014-15?",
    "What was the trend in India's education budget over the last 10 years?",
    "Tell me about the budget in 1993.",
    "Which years have had two budgets, and why?",
    "Why did 2024 have two budgets, and which one should be followed?",
]


def format_year(year_raw):
    if "-" in year_raw:
        return year_raw
    return f"{year_raw[:4]}-{year_raw[4:]}"


def extract_mentioned_years(text):
    matches = re.findall(r"\b(20\d{2})-(\d{2})\b", text)
    years = {f"{start}-{end}" for start, end in matches}
    return sorted(years)


def build_context(documents, metadatas):
    grouped = defaultdict(list)
    for text, meta in zip(documents, metadatas):
        pub_year = format_year(meta["year"])
        label = DOC_TYPE_LABELS[meta["doc_type"]]
        mentioned_years = extract_mentioned_years(text)
        relevant_years = set(mentioned_years) | {pub_year}
        for year in relevant_years:
            grouped[year].append(f"({label}, published {pub_year})\n{text}")

    context_blocks = []
    for year in sorted(grouped.keys()):
        year_content = "\n\n".join(grouped[year])
        context_blocks.append(f"=== Year: {year} ===\n{year_content}")
    return "\n\n".join(context_blocks)


def build_prompt(context, query):
    return f"""You are a fiscal policy research analyst. Answer the user's question using only the context below, in a professional, analytical tone.

Important: Indian government budgets are named by fiscal year (April to March), so a year reference could mean more than one fiscal year depending on convention.

First, build a reconciliation table listing every relevant figure found in the context for the fiscal year(s) the question refers to. Format it exactly like this:

| Source | Fiscal Year | Figure | Type (Original Target / Revised Target / Actual) |
|---|---|---|---|

Include every figure you find, even if they conflict, do not skip any. This table is part of your final output.

After the table, write your answer in this structure:

**Answer:** A short, direct answer in 1-2 sentences, referencing the table above. If the table shows more than one figure for the same year, state that clearly here.

**Details:** Explain the reasoning in more depth, including any year interpretation, and additional useful context from the sources.

**Explore more:** Ask if the user would like to explore this further.

Accuracy rule: Only attach a figure to a fiscal year if the source text itself explicitly states that figure belongs to that year.

Citation rules:
- Every specific fact or figure must be followed by a citation in this exact format: (Source: [Document Type] [Year])
- Cite every fact individually.

If the context does not contain enough information to answer, say so clearly, do not invent a figure.

Context:
{context}

Question: {query}

Answer:"""


results_log = []

for query in GOLDEN_QUESTIONS:
    print(f"Running: {query}")

    response = openai_client.embeddings.create(model=EMBEDDING_MODEL, input=[query])
    query_vector = response.data[0].embedding

    search_results = collection.query(query_embeddings=[query_vector], n_results=TOP_K)
    context = build_context(search_results["documents"][0], search_results["metadatas"][0])
    prompt = build_prompt(context, query)

    chat_response = openai_client.chat.completions.create(
        model=CHAT_MODEL,
        messages=[{"role": "user", "content": prompt}],
        temperature=0,
    )

    answer = chat_response.choices[0].message.content
    results_log.append({"question": query, "answer": answer})

with open("data/golden_set_results.json", "w", encoding="utf-8") as f:
    json.dump(results_log, f, indent=2)

print("\nAll done. Results saved to data/golden_set_results.json")