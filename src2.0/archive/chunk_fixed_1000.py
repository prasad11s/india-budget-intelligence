import json

CHUNK_SIZE = 1000
OVERLAP = 200

with open("data/processed/bs2026_27.json", "r", encoding="utf-8") as f:
    doc = json.load(f)

full_text = ""
page_offsets = []

for page in doc["pages"]:
    text = page["text"] or ""
    page_offsets.append((len(full_text), page["page"]))
    full_text += text + "\n"

def get_page(offset):
    page_num = page_offsets[0][1]
    for start, num in page_offsets:
        if start <= offset:
            page_num = num
        else:
            break
    return page_num

chunks = []
start = 0
chunk_id = 0
step = CHUNK_SIZE - OVERLAP

while start < len(full_text):
    end = start + CHUNK_SIZE
    chunk_text = full_text[start:end]
    chunks.append({
        "chunk_id": f"2026_27_fixed1000_{chunk_id:04d}",
        "text": chunk_text,
        "year": doc["year"],
        "doc_type": doc["doc_type"],
        "filename": doc["filename"],
        "page_start": get_page(start),
        "page_end": get_page(end - 1),
        "chunk_method": "fixed_1000"
    })
    chunk_id += 1
    start += step

with open("data/processed/chunks_fixed_1000.json", "w", encoding="utf-8") as f:
    json.dump(chunks, f, indent=2, ensure_ascii=False)

print(f"Created {len(chunks)} chunks")