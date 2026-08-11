import csv
import os

RAW = "data/raw"

def year_forms(start_year):
    end_year = start_year + 1
    yy_end = end_year % 100
    six_digit = f"{start_year}{yy_end:02d}"          # 194748
    underscore = f"{start_year}_{yy_end:02d}"        # 2023_24
    two_dash = f"{start_year}-{yy_end:02d}"          # 1947-48
    four_dash = f"{start_year}-{end_year}"           # 1947-1948
    return six_digit, underscore, two_dash, four_dash


def check_speech(six_digit, underscore):
    folder = os.path.join(RAW, "budget_speeches")
    for fname in os.listdir(folder):
        if six_digit in fname or underscore in fname:
            return True, None
    url_year = underscore if int(six_digit[:4]) >= 2023 else six_digit
    return False, f"https://www.indiabudget.gov.in/doc/bspeech/bs{url_year}.pdf"


def check_folder_type(doc_type, two_dash, four_dash, link_csvs, url_col):
    folder = os.path.join(RAW, doc_type)
    for name in os.listdir(folder):
        if name.startswith(two_dash) or name.startswith(four_dash):
            path = os.path.join(folder, name)
            if any(files for _, _, files in os.walk(path)):
                return True, None

    for csv_file in link_csvs:
        with open(csv_file, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                if row.get("year", "").strip() in (two_dash, four_dash):
                    return False, row.get(url_col, "").strip()
    return False, "No link found in CSVs"


rows = []
for start_year in range(1947, 2026):
    six_digit, underscore, two_dash, four_dash = year_forms(start_year)
    label = f"{start_year}-{(start_year+1) % 100:02d}"

    speech_ok, speech_link = check_speech(six_digit, underscore)
    doc_ok, doc_link = check_folder_type("budget_documents", two_dash, four_dash,
                                          ["docs/budget_doc_links.csv", "docs/dea_budget_links.csv"], "doc_url")
    survey_ok, survey_link = check_folder_type("economic_surveys", two_dash, four_dash,
                                                 ["docs/survey_links.csv"], "pdf_url")

    rows.append({
        "year": label,
        "budget_speech": "Yes" if speech_ok else speech_link,
        "budget_document": "Yes" if doc_ok else doc_link,
        "economic_survey": "Yes" if survey_ok else survey_link,
    })

with open("docs/year_checklist.csv", "w", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(f, fieldnames=["year", "budget_speech", "budget_document", "economic_survey"])
    writer.writeheader()
    writer.writerows(rows)

print("Saved to docs/year_checklist.csv")