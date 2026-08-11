import os
import glob

def list_years(base_path):
    if not os.path.isdir(base_path):
        return set()
    return set(e for e in os.listdir(base_path) if os.path.isdir(os.path.join(base_path, e)))

DOC_TYPES = ["budget_speeches", "budget_documents", "economic_surveys"]

for doc_type in DOC_TYPES:
    print(f"\n{'='*60}\n{doc_type}\n{'='*60}")

    raw_years = list_years(f"data/raw/{doc_type}")
    print(f"RAW folders found: {len(raw_years)}")

    chunks_path = f"data/chunks/{doc_type}"
    chunk_files = glob.glob(os.path.join(chunks_path, "*.json")) if os.path.isdir(chunks_path) else []
    print(f"CHUNK files found: {len(chunk_files)}")

    chunk_years_seen = set()
    for f in chunk_files:
        name = os.path.basename(f)
        chunk_years_seen.add(name.split("_")[0])
    print(f"Distinct years represented in chunk files: {len(chunk_years_seen)}")
    print(f"Sample: {sorted(chunk_years_seen)[:10]}")