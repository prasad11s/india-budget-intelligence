import os
import json

INPUT_DIR = "data/processed/economic_surveys"
OUTPUT_DIR = "data/chunks/economic_surveys"
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

for filename in os.listdir(INPUT_DIR):
    if not filename.endswith(".json"):
        continue

    output_path = os.path.join(OUTPUT_DIR, filename)
    if os.path.exists(output_path):
        continue

    with open(os.path.join(INPUT_DIR, filename), encoding="utf-8") as f:
        doc = json.load(f)

    full_text = " ".join(p["text"] for p in doc["pages"] if p["text"].strip())

    chunks = chunk_text(full_text, CHUNK_SIZE, OVERLAP)

    output = []
    for i, chunk in enumerate(chunks):
        output.append({
            "year": doc["year"],
            "doc_type": doc["doc_type"],
            "filename": doc["filename"],
            "chunk_id": f"{doc['filename']}_{i}",
            "chunk_index": i,
            "total_chunks": len(chunks),
            "text": chunk
        })

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(output, f, ensure_ascii=False, indent=2)

print("Done.")