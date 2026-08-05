import json
import glob

DOC_TYPES = ["budget_speeches", "budget_documents", "economic_surveys"]

for doc_type in DOC_TYPES:
    chunk_files = glob.glob(f"data/chunks/{doc_type}/*.json")
    empty_files = []
    non_empty_files = []

    for path in chunk_files:
        with open(path, encoding="utf-8") as f:
            chunks = json.load(f)
        if len(chunks) == 0:
            empty_files.append(path)
        else:
            non_empty_files.append(path)

    print(f"\n{doc_type}: {len(chunk_files)} total chunk files")
    print(f"  Empty: {len(empty_files)}")
    print(f"  Non-empty: {len(non_empty_files)}"1.)
    if empty_files:
        print("  Sample empty files:")
        for f in empty_files[:5]:
            print(f"    {f}")