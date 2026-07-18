import json
import os

INPUT_DIR = "data/processed/budget_speeches"

required_keys = {"year", "doc_type", "filename", "pages"}

total = 0
issues = []

for fname in os.listdir(INPUT_DIR):
    if not fname.endswith(".json"):
        continue

    total += 1
    fpath = os.path.join(INPUT_DIR, fname)

    with open(fpath, "r", encoding="utf-8") as f:
        data = json.load(f)

    missing_keys = required_keys - data.keys()
    if missing_keys:
        issues.append(f"{fname}: missing keys {missing_keys}")
        continue

    if not data["pages"]:
        issues.append(f"{fname}: empty pages list")
        continue

    empty_pages = [p["page"] for p in data["pages"] if not p["text"].strip()]
    if empty_pages:
        issues.append(f"{fname}: empty text on pages {empty_pages}")

print(f"Total files checked: {total}")
if issues:
    print(f"\nIssues found ({len(issues)}):")
    for i in issues:
        print(f"  - {i}")
else:
    print("All files passed validation.")