import requests
import os
import time
import csv
import sys
sys.stdout = open("docs/download_log.txt", "w", buffering=1)

BASE_DIR = "data/raw/budget_documents"
os.makedirs(BASE_DIR, exist_ok=True)

# All three CSVs to download from
CSV_FILES = [
    "docs/budget_doc_links.csv",   # Recent budget docs (1996-2025)
    "docs/dea_budget_links.csv",   # Old full budgets (1947-1995)
]

SKIP_DOC_TYPES = {"other"}  # skip uncategorized docs for now

failed = []

def download(url, filepath):
    """Download a file. Skips if already exists."""
    if os.path.exists(filepath):
        print(f"  EXISTS: {os.path.basename(filepath)}")
        return True
    try:
        response = requests.get(url, timeout=300)
        if response.status_code == 200 and len(response.content) > 1000:
            with open(filepath, "wb") as f:
                f.write(response.content)
            size_kb = len(response.content) // 1024
            print(f"  OK: {os.path.basename(filepath)} ({size_kb} KB)")
            return True
        else:
            print(f"  FAILED: {os.path.basename(filepath)} — status {response.status_code}")
            failed.append(url)
            return False
    except Exception as e:
        print(f"  ERROR: {e}")
        failed.append(url)
        return False
    finally:
        time.sleep(0.5)


def get_subfolder(doc_type):
    """Map doc_type to subfolder name."""
    mapping = {
        "full_budget_document": "full_budget",
        "expenditure_budget": "expenditure_budget",
        "demands_for_grants": "demands_for_grants",
        "annual_financial_statement": "annual_financial_statement",
        "finance_bill": "finance_bill",
        "macro_economic": "macro_economic",
        "output_outcome": "output_outcome",
        "receipt_budget": "receipt_budget",
    }
    return mapping.get(doc_type, "other")


# Read all CSVs and collect rows
all_rows = []
for csv_file in CSV_FILES:
    if not os.path.exists(csv_file):
        print(f"WARNING: {csv_file} not found — skipping")
        continue
    with open(csv_file, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            all_rows.append(row)

print(f"Total links to process: {len(all_rows)}\n")

# Group by year
years = {}
for row in all_rows:
    year = row["year"].strip()
    if year not in years:
        years[year] = []
    years[year].append(row)

# Download
total_downloaded = 0
total_skipped = 0

for year, rows in years.items():
    print(f"\n=== {year} ===")
    for row in rows:
        doc_type = row.get("doc_type", "other").strip()
        url = row.get("doc_url", "").strip()
        filename = row.get("filename", "").strip()

        if not url or not filename:
            continue
        if doc_type in SKIP_DOC_TYPES:
            total_skipped += 1
            continue

        subfolder = get_subfolder(doc_type)
        folder = os.path.join(BASE_DIR, year, subfolder)
        os.makedirs(folder, exist_ok=True)
        filepath = os.path.join(folder, filename)

        success = download(url, filepath)
        if success:
            total_downloaded += 1

print(f"\n=== Download Complete ===")
print(f"Downloaded: {total_downloaded}")
print(f"Skipped:    {total_skipped}")
print(f"Failed:     {len(failed)}")
if failed:
    print("Failed URLs:")
    for url in failed:
        print(f"  {url}")