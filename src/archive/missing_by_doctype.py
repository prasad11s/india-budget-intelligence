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

stats = {}

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

            subfolder = SUBFOLDER_MAP.get(doc_type, "other")
            filepath = os.path.join(BASE_DIR, year, subfolder, filename)

            if doc_type not in stats:
                stats[doc_type] = {"total": 0, "missing": 0}
            stats[doc_type]["total"] += 1
            if not os.path.exists(filepath):
                stats[doc_type]["missing"] += 1

print(f"{'doc_type':<30} {'total':>8} {'missing':>8}")
for doc_type, counts in sorted(stats.items(), key=lambda x: -x[1]["missing"]):
    print(f"{doc_type:<30} {counts['total']:>8} {counts['missing']:>8}")