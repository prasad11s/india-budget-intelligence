import csv
import os

BASE_DIR = "data/raw/budget_documents"
CSV_FILES = ["docs/budget_doc_links.csv", "docs/dea_budget_links.csv"]
SKIP_DOC_TYPES = {"other"}

SUBFOLDER_MAP = {
    "full_budget_document": "full_budget",
    "expenditure_budget": "expenditure_budget",
    "demands_for_grants": "demands_for_grants",
    "annual_financial_statement": "annual_financial_statement",
    "finance_bill": "finance_bill",
    "macro_economic": "macro_economic",
    "output_outcome": "output_outcome",
    "receipt_budget": "receipt_budget",
}

missing = []
attempted = 0
found = 0

for csv_file in CSV_FILES:
    with open(csv_file, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            doc_type = row.get("doc_type", "other").strip()
            url = row.get("doc_url", "").strip()
            filename = row.get("filename", "").strip()
            year = row.get("year", "").strip()

            if not url or not filename or doc_type in SKIP_DOC_TYPES:
                continue

            attempted += 1
            subfolder = SUBFOLDER_MAP.get(doc_type, "other")
            filepath = os.path.join(BASE_DIR, year, subfolder, filename)

            if os.path.exists(filepath):
                found += 1
            else:
                missing.append({"year": year, "doc_type": doc_type, "filename": filename, "url": url})

print(f"Attempted (doc_type not 'other'): {attempted}")
print(f"Found on disk: {found}")
print(f"Missing: {len(missing)}")
print()
for m in missing[:20]:
    print(m)
if len(missing) > 20:
    print(f"... and {len(missing) - 20} more")