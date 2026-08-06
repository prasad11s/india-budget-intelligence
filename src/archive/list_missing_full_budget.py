import csv
import os

BASE_DIR = "data/raw/budget_documents"
CSV_FILES = ["docs/budget_doc_links.csv", "docs/dea_budget_links.csv"]
SUBFOLDER_MAP = {"full_budget_document": "full_budget"}

for csv_file in CSV_FILES:
    with open(csv_file, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            if row.get("doc_type", "").strip() != "full_budget_document":
                continue
            year = row.get("year", "").strip()
            filename = row.get("filename", "").strip()
            url = row.get("doc_url", "").strip()
            filepath = os.path.join(BASE_DIR, year, "full_budget", filename)
            if not os.path.exists(filepath):
                print(f"{year} | {filename} | {url}")