import os
import json

folder = "data/processed/economic_surveys"
target = "5%20Fiscal%20Policy%20and%20Government%20Budgets"

for filename in os.listdir(folder):
    if not filename.endswith(".json"):
        continue
    with open(os.path.join(folder, filename), "r", encoding="utf-8") as f:
        data = json.load(f)
    if target in data.get("source", ""):
        print(f"FOUND: {filename}")
        print(f"  pages: {len(data.get('pages', []))}")
        first_page_text = data["pages"][0].get("text", "")
        print(f"  page 1 text length: {len(first_page_text)}")
        break
else:
    print("No processed file references this raw source.")