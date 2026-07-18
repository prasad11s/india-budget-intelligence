import json
import glob

# Common English words that should appear frequently in real budget text.
# Garbled/corrupted extraction won't contain these at any meaningful rate.
STOPWORDS = {"the", "and", "of", "in", "to", "for", "is", "budget",
             "government", "year", "crores", "rs", "which", "shall"}


def garbled_score(text):
    words = text.lower().split()
    if not words:
        return 0.0
    hits = sum(1 for w in words if w.strip(".,;:()") in STOPWORDS)
    return hits / len(words)


results = []
for filepath in glob.glob("data/processed/budget_documents/*.json"):
    with open(filepath, encoding="utf-8") as f:
        doc = json.load(f)
    full_text = " ".join(p["text"] for p in doc["pages"] if p["text"].strip())
    score = garbled_score(full_text)
    results.append((filepath, doc.get("year", "?"), len(full_text), score))

results.sort(key=lambda r: r[3])  # worst first

print(f"{'Year':<12} {'Score':<8} {'Chars':<10} File")
for filepath, year, chars, score in results:
    flag = "  <-- LIKELY GARBLED/EMPTY" if score < 0.05 else ""
    print(f"{str(year):<12} {score:<8.3f} {chars:<10} {filepath}{flag}")

garbled_count = sum(1 for r in results if r[3] < 0.05)
print(f"\n{garbled_count} / {len(results)} documents likely garbled or empty (score < 0.05)")