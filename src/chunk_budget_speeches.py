import json
import os

INPUT_DIR = "data/processed/budget_speeches"
OUTPUT_DIR = "data/chunks/budget_speeches"
CHUNK_SIZE = 1000
OVERLAP = 200

os.makedirs(OUTPUT_DIR, exist_ok=True)


def chunk_text(text, chunk_size, overlap):
    chunks = []
    start = 0
    while start < len(text):
        end = start + chunk_size
        chunks.append(text[start:end])
        start += chunk_size - overlap
    return chunks


for fname in os.listdir(INPUT_DIR):
    if not fname.endswith(".json"):
        continue

    output_path = os.path.join(OUTPUT_DIR, fname)
    if os.path.exists(output_path):
        print(f"Skipping {fname} (already chunked)")
        continue

    with open(os.path.join(INPUT_DIR, fname), "r", encoding="utf-8") as f:
        doc = json.load(f)

    full_text = " ".join(
        page["text"].strip()
        for page in doc["pages"]
        if page["text"].strip()
    )

    raw_chunks = chunk_text(full_text, CHUNK_SIZE, OVERLAP)

    chunks = []
    for i, text in enumerate(raw_chunks):
        chunks.append({
            "text": text,
            "metadata": {
                "year": doc["year"],
                "doc_type": doc["doc_type"],
                "filename": doc["filename"],
                "chunk_id": f"{doc['filename'].replace('.pdf', '')}_chunk_{i:03d}",
                "chunk_index": i,
                "total_chunks": len(raw_chunks)
            }
        })

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(chunks, f, ensure_ascii=False, indent=2)

    print(f"OK: {fname} — {len(chunks)} chunks")

print("\nChunking complete.")   