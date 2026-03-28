import requests
import os
import time

BASE_URL = "https://www.indiabudget.gov.in/doc/bspeech/{filename}.pdf"
SAVE_DIR = "data/raw/budget_speeches"
os.makedirs(SAVE_DIR, exist_ok=True)

HTML_YEARS = {"200809", "200910"}

failed = []

def download(filename):
    """Download a single budget speech PDF. Skips if already exists."""
    filepath = os.path.join(SAVE_DIR, f"{filename}.pdf")

    if os.path.exists(filepath):
        print(f"EXISTS: {filename}.pdf")
        return

    url = BASE_URL.format(filename=filename)
    try:
        response = requests.get(url, timeout=30)
        if response.status_code == 200 and b"%PDF" in response.content[:10]:
            with open(filepath, "wb") as f:
                f.write(response.content)
            print(f"OK: {filename}.pdf ({len(response.content)//1024} KB)")
        else:
            print(f"FAILED: {filename}.pdf — status {response.status_code}")
            failed.append(filename)
    except Exception as e:
        print(f"ERROR: {filename}.pdf — {e}")
        failed.append(filename)
    time.sleep(1)


def make_year_string(start):
    """Convert start year like 1947 → 'bs194748'"""
    return f"bs{start}{str(start + 1)[-2:]}"


# --- Part 1: Main budget speeches (1947 to 2022) ---
print("=== Part 1: Main Budget Speeches ===")
for start_year in range(1947, 2023):
    year_str = make_year_string(start_year)

    if year_str[2:] in HTML_YEARS:
        print(f"SKIP (HTML): {year_str}")
        continue

    download(year_str)

# --- Part 2: Recent years (new URL pattern with underscore) ---
print("\n=== Part 2: Recent Budget Speeches (2023 onwards) ===")
recent = ["bs2023_24", "bs2024_25", "bs2025_26"]
for name in recent:
    download(name)

# --- Part 3: Special and interim budgets ---
print("\n=== Part 3: Special and Interim Budgets ===")
special = [
    "bs195253(I)", "bs195657(november)", "bs195758(I)",
    "bs196263(I)", "bs196566(august)", "bs196768(I)",
    "bs197172december", "bs197172(I)", "bs197475(july)",
    "bs197778(I)", "bs198081(I)", "bs199192(I)",
    "bs199697(I)", "bs199899(I)", "bs200405(I)",
    "bs201920(I)", "bs2024_25(I)"
]
for name in special:
    download(name)

# --- Summary ---
print("\n=== Download Complete ===")
print(f"Failed: {failed if failed else 'None'}")