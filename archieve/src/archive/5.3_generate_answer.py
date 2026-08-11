import re
import json
import configparser
from collections import defaultdict
from openai import OpenAI

config = configparser.ConfigParser()
config.read("docs/config.ini")
openai_client = OpenAI(api_key=config["openai"]["api_key"])

CHAT_MODEL = "gpt-4o-mini"

DOC_TYPE_LABELS = {
    "budget_speeches": "Budget Speech",
    "economic_surveys": "Economic Survey",
    "budget_documents": "Budget Document",
}

with open("data/cached_retrieval.json", encoding="utf-8") as f:
    cache = json.load(f)

query = cache["query"]
documents = cache["documents"]
metadatas = cache["metadatas"]


def format_year(year_raw):
    if "-" in year_raw:
        return year_raw
    return f"{year_raw[:4]}-{year_raw[4:]}"


def extract_mentioned_years(text):
    matches = re.findall(r"\b(20\d{2})-(\d{2})\b", text)
    years = {f"{start}-{end}" for start, end in matches}
    return sorted(years)


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

context = "\n\n".join(context_blocks)

prompt = f"""You are a fiscal policy research analyst. Answer the user's question using only the context below, in a professional, analytical tone.

Important: Indian government budgets are named by fiscal year (April to March), so "the 2015 budget" could mean the budget presented in February 2015 for fiscal year 2015-16, or could be interpreted as fiscal year 2014-15 depending on convention.

First, build a reconciliation table like a fiscal policy analyst would, listing every fiscal deficit figure found in the context for the fiscal year the question refers to. Format it exactly like this:

| Source | Fiscal Year | Figure | Type (Original Target / Revised Target / Actual) |
|---|---|---|---|

Include every figure you find for that year, even if they conflict, do not skip any. This table is part of your final output, the user should see it.

After the table, write your answer in this structure:

**Answer:** A short, direct answer in 1-2 sentences, referencing the table above. If the table shows more than one figure for the same year, state that clearly here, do not pick only one.

**Details:** Explain the reasoning in more depth, including which fiscal year you interpreted the question as referring to, and any additional useful context from the sources.

**Explore more:** Ask if the user would like to explore this further, or if they meant a different fiscal year.

Accuracy rule: Only attach a figure to a fiscal year if the source text itself explicitly states that figure belongs to that year.

Citation rules:
- Every specific fact or figure must be followed by a citation in this exact format: (Source: [Document Type] [Year])
- Cite every fact individually.

If the context does not contain enough information to answer, say so clearly.

Context:
{context}

Question: {query}

Answer:"""

chat_response = openai_client.chat.completions.create(
    model=CHAT_MODEL,
    messages=[{"role": "user", "content": prompt}],
    temperature=0,
)

answer = chat_response.choices[0].message.content
print(answer)