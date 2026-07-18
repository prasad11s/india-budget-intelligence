import json

STOPWORDS = {"the", "and", "of", "in", "to", "for", "is", "budget",
             "government", "year", "crores", "rs", "which", "shall"}


def garbled_score(text):
    words = text.lower().split()
    if not words:
        return 0.0
    hits = sum(1 for w in words if w.strip(".,;:()") in STOPWORDS)
    return hits / len(words)


with open("data/chunks/budget_documents/1969-70_full_budget_BUDGET1969-70.json", encoding="utf-8") as f:
    chunks = json.load(f)

clean = [c for c in chunks if garbled_score(c["text"]) >= 0.05]
garbled = [c for c in chunks if garbled_score(c["text"]) < 0.05]

print(f"Total chunks: {len(chunks)}")
print(f"Clean (keep):   {len(clean)}")
print(f"Garbled (drop): {len(garbled)}")
print(f"\nSample of a CLEAN chunk kept:")
print(clean[len(clean)//2]["text"][:200])