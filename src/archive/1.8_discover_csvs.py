import csv
import glob

CSV_CANDIDATES = glob.glob("docs/*.csv")

for path in CSV_CANDIDATES:
    print(f"\n{'='*60}\n{path}\n{'='*60}")
    with open(path, encoding="utf-8", errors="ignore") as f:
        reader = csv.reader(f)
        header = next(reader, None)
        print(f"Columns: {header}")
        first_row = next(reader, None)
        print(f"First data row: {first_row}")
        row_count = 1 + sum(1 for _ in reader) if first_row else 0
        print(f"Total data rows: {row_count}")


        