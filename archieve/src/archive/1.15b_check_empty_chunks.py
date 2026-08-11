import os
import json

BASE = "data/chunks"  # ADJUST if your chunk output folder is named differently
DOC_TYPES = ["budget_speeches", "budget_documents", "economic_surveys"]

empty_files = []

for doc_type in DOC_TYPES:
    folder = os.path.join(BASE, doc_type)
    for filename in os.listdir(folder):
        if not filename.endswith(".json"):
            continue
        filepath = os.path.join(folder, filename)
        with open(filepath, "r", encoding="utf-8") as f:
            chunks = json.load(f)
        if len(chunks) == 0:
            empty_files.append((doc_type, filename))

print(f"Found {len(empty_files)} empty chunk files")
for doc_type, filename in empty_files:
    print(f"{doc_type}: {filename}")