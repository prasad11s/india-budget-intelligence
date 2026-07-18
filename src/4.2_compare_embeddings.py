import json
import glob
import math
from openai import OpenAI

client = OpenAI()

# Each test case: (query, keyword that marks a relevant chunk, keyword that marks an irrelevant one)
TEST_CASES = [
    ("What did the budget say about income tax?", "income tax", "defence"),
    ("What did the budget say about agriculture?", "agriculture", "customs"),
    ("What did the budget say about education?", "education", "railway"),
]

# Load every budget speech chunk once, so we only scan the corpus a single time
all_chunks = []
for f in glob.glob("data/chunks/budget_speeches/*.json"):
    with open(f, encoding="utf-8") as file:
        all_chunks.extend(json.load(file))


def find_chunk(keyword, exclude):
    for c in all_chunks:
        text = c["text"].lower()
        if keyword in text and exclude not in text:
            return c["text"]
    return None


def cosine_similarity(a, b):
    dot = sum(x * y for x, y in zip(a, b))
    norm_a = math.sqrt(sum(x * x for x in a))
    norm_b = math.sqrt(sum(x * x for x in b))
    return dot / (norm_a * norm_b)


models = ["text-embedding-3-small", "text-embedding-3-large"]
gaps = {m: [] for m in models}

for query, rel_kw, irr_kw in TEST_CASES:
    rel_chunk = find_chunk(rel_kw, exclude=irr_kw)
    irr_chunk = find_chunk(irr_kw, exclude=rel_kw)

    if not rel_chunk or not irr_chunk:
        print(f"Skipping '{query}' — couldn't find both sample chunks")
        continue

    print(f"\nQuery: {query}")
    for model in models:
        response = client.embeddings.create(model=model, input=[query, rel_chunk, irr_chunk])
        q_vec, rel_vec, irr_vec = [d.embedding for d in response.data]
        rel_sim = cosine_similarity(q_vec, rel_vec)
        irr_sim = cosine_similarity(q_vec, irr_vec)
        gap = rel_sim - irr_sim
        gaps[model].append(gap)
        print(f"  [{model}] relevant: {rel_sim:.4f} | irrelevant: {irr_sim:.4f} | gap: {gap:.4f}")

print("\n=== Average gap across all test queries ===")
for model, g in gaps.items():
    if g:
        print(f"{model}: {sum(g)/len(g):.4f}  (from {len(g)} queries)")