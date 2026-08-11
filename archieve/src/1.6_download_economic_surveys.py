import requests
import os
import time
import csv

BASE_DIR = "data/raw/economic_surveys"
CSV_FILE = "docs/survey_links.csv"

failed = []

def download(url, filepath):
    """Download a single PDF. Returns True if successful."""
    if os.path.exists(filepath):
        print(f"  EXISTS: {os.path.basename(filepath)}")
        return True
    try:
        response = requests.get(url, timeout=30)
        if response.status_code == 200 and b"%PDF" in response.content[:10]:
            with open(filepath, "wb") as f:
                f.write(response.content)
            print(f"  OK: {os.path.basename(filepath)} ({len(response.content)//1024} KB)")
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


def classify(filename):
    """Classify a PDF into chapters, statistical_appendix, or skip."""
    name = filename.lower()

    # Skip individual stat tables
    if name.startswith("tab") and name.endswith(".pdf"):
        return "skip"

    # Skip corrigenda, index, infographics, highlights, preface
    skip_keywords = ["infographic", "highlight", "preface", "epreface",
                     "acknowledgement", "corrigenda", "index"]
    if any(kw in name for kw in skip_keywords):
        return "skip"

    # Statistical appendix
    if "statistical-appendix-in-english" in name or "estat" in name:
        return "statistical_appendix"

    # Chapters — all known patterns
    chapter_keywords = ["echap", "chapter", "chap", "echapter",
                        "vol1", "vol2", "part_i", "part_ii", "part_iii",
                        "ch_", "ch1", "ch2", "ch3"]
    if any(kw in name for kw in chapter_keywords):
        return "chapters"

    # Archive chapters with URL-encoded names (contain %20)
    if "%20" in filename:
        return "chapters"

    return "skip"


# Read CSV and download
print(f"Reading links from {CSV_FILE}...\n")

with open(CSV_FILE, "r", encoding="utf-8") as f:
    reader = csv.DictReader(f)
    rows = list(reader)

# Filter English only and non-empty URLs
english_rows = [r for r in rows if r["language"] == "english" and r["pdf_url"].strip()]

# Group by year
years = {}
for row in english_rows:
    year = row["year"]
    if year not in years:
        years[year] = []
    years[year].append(row)

print(f"Found {len(english_rows)} English PDF links across {len(years)} years\n")

# Download
total_downloaded = 0
total_skipped = 0

for year, year_rows in years.items():
    print(f"\n=== {year} ===")

    for row in year_rows:
        filename = row["filename"]
        pdf_url = row["pdf_url"]
        category = classify(filename)

        if category == "skip":
            total_skipped += 1
            continue

        # Create folder
        folder = os.path.join(BASE_DIR, year, category)
        os.makedirs(folder, exist_ok=True)
        filepath = os.path.join(folder, filename)

        success = download(pdf_url, filepath)
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