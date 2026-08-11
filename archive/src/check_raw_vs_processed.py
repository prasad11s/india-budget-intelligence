import os

RAW_BASE = "data/raw"
PROCESSED_BASE = "data/processed"
DOC_TYPES = ["budget_speeches", "budget_documents", "economic_surveys"]

for doc_type in DOC_TYPES:
    raw_folder = os.path.join(RAW_BASE, doc_type)
    processed_folder = os.path.join(PROCESSED_BASE, doc_type)

    raw_stems = []
    for root, dirs, files in os.walk(raw_folder):
        for f in files:
            if f.lower().endswith(".pdf"):
                raw_stems.append(os.path.splitext(f)[0])

    processed_names = [os.path.splitext(f)[0] for f in os.listdir(processed_folder) if f.endswith(".json")]

    missing = [stem for stem in raw_stems if not any(name.endswith(stem) for name in processed_names)]

    print(f"\n{doc_type}: {len(raw_stems)} raw PDFs, {len(processed_names)} processed JSONs, {len(missing)} unmatched")
    for m in missing:
        print(f"  MISSING: {m}")