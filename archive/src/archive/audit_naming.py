import os
import json

PROCESSED_BASE = "data/processed"
DOC_TYPES = ["budget_speeches", "budget_documents", "economic_surveys"]

print("=== YEAR FORMAT AUDIT ===")
for doc_type in DOC_TYPES:
    folder = os.path.join(PROCESSED_BASE, doc_type)
    year_values = {}
    for filename in os.listdir(folder):
        if not filename.endswith(".json"):
            continue
        with open(os.path.join(folder, filename), "r", encoding="utf-8") as f:
            data = json.load(f)
        year = data.get("year", "MISSING")
        year_values[year] = year_values.get(year, 0) + 1

    print(f"\n{doc_type}: {len(year_values)} distinct year formats")
    for year, count in sorted(year_values.items(), key=lambda x: str(x[0])):
        print(f"  {year!r}: {count} file(s)")

print("\n=== LOCATING %20 FILE ===")
raw_surveys = "data/raw/economic_surveys"
for root, dirs, files in os.walk(raw_surveys):
    for f in files:
        if "%20" in f:
            print(f"  {os.path.join(root, f)}")