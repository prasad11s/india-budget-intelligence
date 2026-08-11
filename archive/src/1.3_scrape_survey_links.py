import requests
from bs4 import BeautifulSoup
import time
import sys
import os
import csv

sys.stdout.reconfigure(encoding="utf-8")

BASE = "https://www.indiabudget.gov.in"
os.makedirs("docs", exist_ok=True)
OUTPUT_CSV = "docs/survey_links.csv"

HINDI_KEYWORDS = ["hindi", "Hindi", "hechap", "Statistical-Appendix-in-Hindi"]

def is_hindi(url):
    return any(kw in url for kw in HINDI_KEYWORDS)

def get_all_links(url):
    """Fetch a page and return all href links, resolving relative URLs."""
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
        print(f"  ERROR fetching {url}: {e}")
        return []
    finally:
        time.sleep(0.5)


# Step 1 — Get all year links from allpes.php
print("Fetching year links from allpes.php...")
allpes_url = f"{BASE}/economicsurvey/allpes.php"
year_links = get_all_links(allpes_url)

survey_years = []
for text, href in year_links:
    if text and any(c.isdigit() for c in text) and "-" in text:
        survey_years.append((text.strip(), href))

print(f"Found {len(survey_years)} survey year links\n")

# Step 2 — Visit each year page and collect all PDF links
rows = []
total_english = 0
total_hindi = 0

for year_text, year_url in survey_years:
    print(f"[{year_text}] {year_url}")
    page_links = get_all_links(year_url)
    pdf_links = [(t, h) for t, h in page_links if ".pdf" in h.lower()]

    if not pdf_links:
        print("  No PDF links found")
        rows.append({
            "year": year_text,
            "page_url": year_url,
            "pdf_url": "",
            "filename": "",
            "language": "none"
        })

    for text, href in pdf_links:
        language = "hindi" if is_hindi(href) else "english"
        filename = href.split("/")[-1]
        rows.append({
            "year": year_text,
            "page_url": year_url,
            "pdf_url": href,
            "filename": filename,
            "language": language
        })
        print(f"  [{language}] {href}")
        if language == "english":
            total_english += 1
        else:
            total_hindi += 1
    print()

# Step 3 — Save to CSV (overwrite each run)
with open(OUTPUT_CSV, "w", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(f, fieldnames=["year", "page_url", "pdf_url", "filename", "language"])
    writer.writeheader()
    writer.writerows(rows)

print("=== Done ===")
print(f"English links: {total_english}")
print(f"Hindi links:   {total_hindi}")
print(f"Years processed: {len(survey_years)}")
print(f"Saved to: {OUTPUT_CSV}")