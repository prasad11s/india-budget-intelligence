import csv
import os
import urllib.parse

RAW_DIR = "data/raw/economic_surveys"
missing = []
checked = 0

with open("docs/survey_links.csv", "r", encoding="utf-8") as f:
    reader = csv.DictReader(f)
    for row in reader:
        if row.get("language", "").strip().lower() != "english":
            continue

        year = row["year"].strip()
        filename = row["filename"].strip()
        url = row["pdf_url"].strip()
        checked += 1

        found = False
        for folder_name in os.listdir(RAW_DIR):
            if not folder_name.startswith(year):
                continue
            for root, dirs, files in os.walk(os.path.join(RAW_DIR, folder_name)):
                for f_on_disk in files:
                    if urllib.parse.unquote(f_on_disk).lower() == filename.lower():
                        found = True
                        break
                if found:
                    break
            if found:
                break

        if not found:
            missing.append({"year": year, "filename": filename, "url": url})

print(f"Checked (English only): {checked}")
print(f"Missing: {len(missing)}")
for m in missing[:20]:
    print(m)
if len(missing) > 20:
    print(f"... and {len(missing) - 20} more")