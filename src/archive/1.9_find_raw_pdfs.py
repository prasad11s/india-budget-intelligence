import glob

for pattern in ["data/raw/**/*.pdf", "data/**/*.pdf"]:
    files = glob.glob(pattern, recursive=True)
    print(f"\nPattern: {pattern}")
    print(f"Total PDFs found: {len(files)}")
    if files:
        print("Sample paths:")
        for f in files[:5]:
            print(f"  {f}")