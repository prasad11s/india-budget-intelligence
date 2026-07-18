import json
import glob
import os

CHUNK_FOLDERS = [
    "data/chunks/budget_speeches",
    "data/chunks/economic_surveys",
    "data/chunks/budget_documents",
]

grand_total = 0
for folder in CHUNK_FOLDERS:
    folder_total = 0
    for filepath in glob.glob(os.path.join(folder, "*.json")):
        with open(filepath, encoding="utf-8") as f:
            chunks = json.load(f)
        folder_total += len(chunks)
    print(f"{folder}: {folder_total} chunks")
    grand_total += folder_total

print(f"\nTotal chunks across all folders: {grand_total}")
# Rough cost estimate: avg ~1000 chars/chunk =~ 200-250 tokens
est_tokens = grand_total * 225
print(f"Estimated tokens: ~{est_tokens:,}")
print(f"Estimated cost (text-embedding-3-large @ $0.13/1M tokens): ~${est_tokens/1_000_000*0.13:.2f}")