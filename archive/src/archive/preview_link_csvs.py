import csv
import os

CSV_FILES = ["docs/budget_doc_links.csv", "docs/survey_links.csv", "docs/dea_budget_links.csv"]

for path in CSV_FILES:
    print(f"=== {path} ===")
    with open(path, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        rows = list(reader)
        print(f"columns: {reader.fieldnames}")
        print(f"total rows: {len(rows)}")
        for row in rows[:2]:
            print(row)
    print()