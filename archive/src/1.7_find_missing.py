import os
import csv

# ---------- 1. Budget Speeches (no CSV — filenames generated from a rule) ----------
HTML_YEARS = {"200809", "200910"}
speeches_expected = set()
for y in range(1947, 2023):
    ystr = f"bs{y}{str(y+1)[-2:]}"
    if ystr[2:] not in HTML_YEARS:
        speeches_expected.add(ystr + ".pdf")
for name in ["bs2023_24", "bs2024_25", "bs2025_26"]:
    speeches_expected.add(name + ".pdf")
special = ["bs195253(I)", "bs195657(november)", "bs195758(I)", "bs196263(I)",
           "bs196566(august)", "bs196768(I)", "bs197172december", "bs197172(I)",
           "bs197475(july)", "bs197778(I)", "bs198081(I)", "bs199192(I)",
           "bs199697(I)", "bs199899(I)", "bs200405(I)", "bs201920(I)", "bs2024_25(I)"]
for name in special:
    speeches_expected.add(name + ".pdf")

speeches_actual = set(os.listdir("data/raw/budget_speeches")) if os.path.exists("data/raw/budget_speeches") else set()
speeches_missing = speeches_expected - speeches_actual

# ---------- 2. Budget Documents (from two CSVs) ----------
docs_expected = set()
for csv_file in ["docs/budget_doc_links.csv", "docs/dea_budget_links.csv"]:
    if os.path.exists(csv_file):
        with open(csv_file, encoding="utf-8") as f:
            for row in csv.DictReader(f):
                docs_expected.add(row["filename"])

docs_actual = set()
if os.path.exists("data/raw/budget_documents"):
    for root, dirs, files in os.walk("data/raw/budget_documents"):
        docs_actual.update(files)
docs_missing = docs_expected - docs_actual

# ---------- 3. Economic Surveys (from CSV, English + downloadable categories only) ----------
def classify(name):
    n = name.lower()
    if n.startswith("tab") and n.endswith(".pdf"):
        return "skip"
    if any(k in n for k in ["infographic", "highlight", "preface", "epreface",
                             "acknowledgement", "corrigenda", "index"]):
        return "skip"
    if "statistical-appendix-in-english" in n or "estat" in n:
        return "keep"
    if any(k in n for k in ["echap", "chapter", "chap", "echapter", "vol1", "vol2",
                             "part_i", "part_ii", "part_iii", "ch_", "ch1", "ch2", "ch3"]):
        return "keep"
    if "%20" in name:
        return "keep"
    return "skip"

surveys_expected = set()
if os.path.exists("docs/survey_links.csv"):
    with open("docs/survey_links.csv", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            if row["language"] == "english" and row["filename"] and classify(row["filename"]) == "keep":
                surveys_expected.add(row["filename"])

surveys_actual = set()
if os.path.exists("data/raw/economic_surveys"):
    for root, dirs, files in os.walk("data/raw/economic_surveys"):
        surveys_actual.update(files)
surveys_missing = surveys_expected - surveys_actual

# ---------- Report ----------
for label, expected, missing in [
    ("Budget Speeches", speeches_expected, speeches_missing),
    ("Budget Documents", docs_expected, docs_missing),
    ("Economic Surveys", surveys_expected, surveys_missing),
]:
    print(f"\n=== {label} ===")
    print(f"Expected: {len(expected)} | On disk (matched): {len(expected) - len(missing)} | Missing: {len(missing)}")
    for m in sorted(missing):
        print(f"  MISSING: {m}")