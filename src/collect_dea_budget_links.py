import requests
from bs4 import BeautifulSoup
import csv
import os
import time
import re

DEA_BASE = "https://dea.gov.in"
os.makedirs("docs", exist_ok=True)
OUTPUT_CSV = "docs/dea_budget_links.csv"

PAGES = [
    "https://dea.gov.in/budget-division/469",
    "https://dea.gov.in/budget-division/469?page=1",
    "https://dea.gov.in/budget-division/469?page=2",
    "https://dea.gov.in/budget-division/469?page=3",
    "https://dea.gov.in/budget-division/469?page=4",
]

def get_pdf_links(page_url):
    """Scrape all PDF links from a dea.gov.in page."""
    try:
        r = requests.get(page_url, timeout=15)
        soup = BeautifulSoup(r.content, "html.parser")
        links = []
        for a in soup.find_all("a", href=True):
            href = a["href"].strip()
            if ".pdf" in href.lower():
                full_url = DEA_BASE + href if href.startswith("/") else href
                links.append(full_url)
        return links
    except Exception as e:
        print(f"  ERROR: {e}")
        return []
    finally:
        time.sleep(0.5)


def extract_year(filename):
    """Extract year string from filename."""
    m = re.search(r"(\d{4}-\d{2})", filename)
    if m:
        return m.group(1)
    m2 = re.search(r"(\d{4})(\d{2})", filename)
    if m2:
        return f"{m2.group(1)}-{m2.group(2)}"
    return filename


rows = []
total = 0

print("Scraping PDF links from dea.gov.in...\n")

for page_url in PAGES:
    print(f"Page: {page_url}")
    pdf_urls = get_pdf_links(page_url)

    for url in pdf_urls:
        filename = url.split("/")[-1]
        year = extract_year(filename)
        rows.append({
            "year": year,
            "doc_url": url,
            "filename": filename,
            "doc_type": "full_budget_document",
            "source": "dea.gov.in"
        })
        print(f"  {year} — {filename}")
        total += 1
    print()

# Save to CSV
with open(OUTPUT_CSV, "w", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(f,
        fieldnames=["year", "doc_url", "filename", "doc_type", "source"])
    writer.writeheader()
    writer.writerows(rows)

print(f"=== Done ===")
print(f"Total links: {total}")
print(f"Saved to: {OUTPUT_CSV}")