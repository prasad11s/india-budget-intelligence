import csv
import os
import urllib.parse

def survey_missing():
    RAW_DIR = "data/raw/economic_surveys"
    missing = []
    with open("docs/survey_links.csv", "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            if row.get("language", "").strip().lower() != "english":
                continue
            year = row["year"].strip()
            filename = row["filename"].strip()
            url = row["pdf_url"].strip()
            found = False
            for folder_name in os.listdir(RAW_DIR):
                if not folder_name.startswith(year):
                    continue
                for root, dirs, files in os.walk(os.path.join(RAW_DIR, folder_name)):
                    if any(urllib.parse.unquote(f).lower() == filename.lower() for f in files):
                        found = True
                        break
                if found:
                    break
            if not found:
                missing.append({"doc_type": "economic_survey", "year": year, "filename": filename, "url": url})
    return missing


def budget_doc_missing():
    BASE_DIR = "data/raw/budget_documents"
    missing = []
    for csv_file in ["docs/budget_doc_links.csv", "docs/dea_budget_links.csv"]:
        with open(csv_file, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                if row.get("doc_type", "").strip() != "full_budget_document":
                    continue
                year = row["year"].strip()
                filename = row["filename"].strip()
                url = row["doc_url"].strip()
                found = any(filename in files for _, _, files in os.walk(BASE_DIR))
                if not found:
                    missing.append({"doc_type": "budget_document", "year": year, "filename": filename, "url": url})
    return missing


def speech_known_gaps():
    return [
        {"doc_type": "budget_speech", "year": "1999-2000", "filename": "bs199900.pdf", "url": "missing from government server"},
        {"doc_type": "budget_speech", "year": "2010-11", "filename": "bs201011.pdf", "url": "missing from government server"},
        {"doc_type": "budget_speech", "year": "2008-09", "filename": "N/A", "url": "served as HTML page, not PDF, needs separate handling"},
        {"doc_type": "budget_speech", "year": "2009-10", "filename": "N/A", "url": "served as HTML page, not PDF, needs separate handling"},
    ]


all_missing = survey_missing() + budget_doc_missing() + speech_known_gaps()

with open("docs/missing_documents.csv", "w", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(f, fieldnames=["doc_type", "year", "filename", "url"])
    writer.writeheader()
    writer.writerows(all_missing)

print(f"Total real gaps: {len(all_missing)}")
print("Saved to docs/missing_documents.csv")