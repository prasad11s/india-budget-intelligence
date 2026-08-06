import os
import json
import pdfplumber

PROCESSED_DIR = "data/processed/budget_documents"

def find_by_year(target_year):
    for filename in os.listdir(PROCESSED_DIR):
        if not filename.endswith(".json"):
            continue
        with open(os.path.join(PROCESSED_DIR, filename), "r", encoding="utf-8") as f:
            data = json.load(f)
        if data.get("year") == target_year:
            print(f"  {filename}")
            print(f"    source: {data.get('source')}")

print("=== CENTRAL-BIDGET-91-92.pdf entry ===")
find_by_year("CENTRAL-BIDGET-91-92.pdf")

print("\n=== 1992-92 entry ===")
find_by_year("1992-92")

print("\n=== testing the one failed economic survey file ===")
test_path = "data/raw/economic_surveys/1978-1979/chapters/5%20Fiscal%20Policy%20and%20Government%20Budgets.PDF"
try:
    with pdfplumber.open(test_path) as pdf:
        print(f"  Opened fine. {len(pdf.pages)} pages.")
        text = pdf.pages[0].extract_text()
        print(f"  Page 1 text length: {len(text) if text else 0}")
except Exception as e:
    print(f"  FAILED TO OPEN: {e}")