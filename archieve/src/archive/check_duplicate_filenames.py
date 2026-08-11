import os

RAW_DIR = "data/raw/budget_documents"
filenames_to_check = [
    "BUDGET-1947-48.pdf",
    "BUDGET-1948-49.pdf",
    "BUDGET-1949-50.pdf",
    "BUDGET_1950-51.pdf",
    "BUDGETPAPERS-1952-53.pdf",
    "BUDGET-195354.pdf",
]

for target in filenames_to_check:
    found_at = []
    for root, dirs, files in os.walk(RAW_DIR):
        if target in files:
            found_at.append(root)
    if found_at:
        print(f"FOUND: {target} -> {found_at}")
    else:
        print(f"REALLY MISSING: {target}")