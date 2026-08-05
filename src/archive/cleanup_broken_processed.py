import json
import glob
import os

FOLDERS_TO_CHECK = ["data/processed/economic_surveys", "data/processed/budget_documents"]

removed = 0
for folder in FOLDERS_TO_CHECK:
    for filepath in glob.glob(f"{folder}/*.json"):
        try:
            with open(filepath, encoding="utf-8") as f:
                data = json.load(f)
            total_chars = sum(len(p.get("text", "")) for p in data.get("pages", []))
            if total_chars < 30:
                os.remove(filepath)
                removed += 1
                print(f"Removed broken/empty: {filepath}")
        except (json.JSONDecodeError, UnicodeDecodeError):
            os.remove(filepath)
            removed += 1
            print(f"Removed corrupted (unreadable): {filepath}")

print(f"\nTotal removed: {removed}")