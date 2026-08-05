import json, os

FILES = {
    "bs202223.json": [2, 4, 37],
    "bs2023_24.json": [2, 4],
    "bs2024_25(I).json": [2, 4],
    "bs2024_25.json": [2, 4],
    "bs2025_26.json": [2, 4],
}

INPUT_DIR = "data/processed/budget_speeches"

for fname, empty_pages in FILES.items():
    fpath = os.path.join(INPUT_DIR, fname)
    with open(fpath, "r", encoding="utf-8") as f:
        data = json.load(f)

    print(f"\n=== {fname} — {len(data['pages'])} total pages ===")
    for p in data["pages"]:
        if p["page"] in empty_pages:
            print(f"  Page {p['page']}: [EMPTY]")
        elif p["page"] in [ep - 1 for ep in empty_pages] + [ep + 1 for ep in empty_pages]:
            preview = p["text"].strip()[:80].replace("\n", " ")
            print(f"  Page {p['page']}: {preview}")