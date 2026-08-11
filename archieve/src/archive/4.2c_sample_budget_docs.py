import json
import glob
import random

files = glob.glob("data/chunks/budget_documents/*.json")
sample_files = random.sample(files, min(3, len(files)))

for filepath in sample_files:
    with open(filepath, encoding="utf-8") as f:
        chunks = json.load(f)
    print(f"\n=== {filepath} — {len(chunks)} chunks ===")
    # Print first, middle, and last chunk as a spread check
    for idx in [0, len(chunks) // 2, len(chunks) - 1]:
        text = chunks[idx]["text"]
        print(f"  [chunk {idx}] {text[:150]!r}")