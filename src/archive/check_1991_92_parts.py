import json

files = {
    "CENTRAL-BIDGET-91-92": "data/processed/budget_documents/CENTRAL-BIDGET-91-92.json_full_budget_CENTRAL-BIDGET-91-92.json",
    "1992-92-part2": "data/processed/budget_documents/1992-92_full_budget_CENTRAL-BUDGET-1992-92-part2.json",
}

for label, path in files.items():
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
    print(f"=== {label} ===")
    print(data["pages"][0]["text"][:300])
    print()