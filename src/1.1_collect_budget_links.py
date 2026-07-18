import requests
from bs4 import BeautifulSoup
import csv
import os
import time
import sys

sys.stdout.reconfigure(encoding="utf-8")

BASE = "https://www.indiabudget.gov.in"
os.makedirs("docs", exist_ok=True)
OUTPUT_CSV = "docs/budget_doc_links.csv"

# Keywords to identify document types
DOC_TYPES = {
    "expenditure_budget": ["allsbe.xls", "allsbe.xlsx", "sbe", "expend"],
    "demands_for_grants": ["alldg.pdf", "alldg.xlsx", "dg", "demand"],
    "annual_financial_statement": ["allafs", "afs", "annualfinancial"],
    "finance_bill": ["fb.pdf", "financebill", "finance_bill", "Finance_Bill"],
    "macro_economic": ["mefs", "macro", "frbm", "medterm"],
    "output_outcome": ["oof", "output", "OutcomeBudget"],
    "receipt_budget": ["rb.pdf", "allrb", "receipt"],
    "budget_highlights": ["bh1", "bh2", "highlight", "budget_at_a_glance"],
    "full_budget_document": ["impbud", "ub20"],
}

SKIP_KEYWORDS = ["speech", "highlight", "mobile", "webcast", "hindi",
                 "notification", "customs", "corrigenda", "key-to"]

def get_links(url):
    """Fetch page and return all href links with resolved URLs."""
    try:
        r = requests.get(url, timeout=15)
        soup = BeautifulSoup(r.content, "html.parser")
        links = []
        for a in soup.find_all("a", href=True):
            href = a["href"].strip()
            text = a.get_text(strip=True)
            if href.startswith("http"):
                full_url = href
            elif href.startswith("/"):
                full_url = BASE + href
            else:
                full_url = url.rsplit("/", 1)[0] + "/" + href
            links.append((text, full_url))
        return links
    except Exception as e:
        print(f"  ERROR: {e}")
        return []
    finally:
        time.sleep(0.5)


def classify_doc(url):
    """Classify a URL into a document type."""
    url_lower = url.lower()
    filename = url.split("/")[-1].lower()
    # Full budget documents from dea.gov.in
    if "budget-" in filename or "budget_" in filename or "budgetpapers" in filename:
        return "full_budget_document"
    for doc_type, keywords in DOC_TYPES.items():
        if any(kw in url_lower for kw in keywords):
            return doc_type
    return "other"


def should_skip(url):
    """Return True if URL should be skipped."""
    url_lower = url.lower()
    return any(kw in url_lower for kw in SKIP_KEYWORDS)


# Step 1 — Get all year links from previous_union_budget.php
print("Fetching year links from previous_union_budget.php...")
index_url = f"{BASE}/previous_union_budget.php"
year_links = get_links(index_url)

budget_years = []  # (year_text, year_url, is_direct_pdf)
for text, href in year_links:
    if text and any(c.isdigit() for c in text) and (
        "-" in text or "(" in text
    ) and "budget" in href.lower():
        budget_years.append((text.strip(), href, False))

# Also scrape all 5 pages of dea.gov.in for older budgets (direct PDFs)
print("Fetching dea.gov.in pages 1-5...")
DEA_BASE = "https://dea.gov.in"
for page in range(0, 5):
    dea_url = f"{DEA_BASE}/budget-division/469?page={page}"
    print(f"  Page {page}: {dea_url}")
    dea_links = get_links(dea_url)
    for text, href in dea_links:
        if text and "Union Budget" in text and href.endswith(".pdf"):
            budget_years.append((text.strip(), href, True))

print(f"Found {len(budget_years)} budget entries\n")

print(f"Found {len(budget_years)} budget year links\n")

# Step 2 — Visit each year page and collect document links
rows = []
total = 0

for year_text, year_url, is_direct_pdf in budget_years:
    print(f"[{year_text}] {year_url}")

    # dea.gov.in entries are direct PDF links
    if is_direct_pdf:
        filename = year_url.split("/")[-1]
        rows.append({
            "year": year_text,
            "page_url": year_url,
            "doc_url": year_url,
            "filename": filename,
            "doc_type": "full_budget_document",
        })
        print(f"  [full_budget_document] {filename}")
        total += 1
        print()
        continue
    page_links = get_links(year_url)

    year_rows = []
    seen_urls = set()

    for text, href in page_links:
        # Skip duplicates
        if href in seen_urls:
            continue
        seen_urls.add(href)

        # Skip non-PDF/Excel files and unwanted content
        ext = href.lower().split("?")[0].split("#")[0]
        if not any(ext.endswith(e) for e in [".pdf", ".xls", ".xlsx"]):
            continue
        if should_skip(href):
            continue

        doc_type = classify_doc(href)
        filename = href.split("/")[-1]

        year_rows.append({
            "year": year_text,
            "page_url": year_url,
            "doc_url": href,
            "filename": filename,
            "doc_type": doc_type,
        })
        print(f"  [{doc_type}] {filename}")
        total += 1

    rows.extend(year_rows)
    if not year_rows:
        print("  No document links found")
    print()

# Step 3 — Save to CSV
with open(OUTPUT_CSV, "w", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(f, fieldnames=["year", "page_url", "doc_url", "filename", "doc_type"])
    writer.writeheader()
    writer.writerows(rows)

print("=== Done ===")
print(f"Total links collected: {total}")
print(f"Budget years processed: {len(budget_years)}")
print(f"Saved to: {OUTPUT_CSV}")