import json

input_path = "data/processed/budget_at_a_glance_clean.json"
output_path = "data/processed/budget_at_a_glance_chunks_para750_clean.json"
target_size = 750

with open(input_path, "r", encoding="utf-8") as f:
    doc = json.load(f)

chunks = []
buffer = ""
buffer_pages = set()

for page in doc["pages"]:
    if not page["text"]:
        continue
    paragraphs = page["text"].split("\n\n")
    for para in paragraphs:
        para = para.strip()
        if not para:
            continue
        if len(buffer) + len(para) > target_size and buffer:
            chunks.append({"pages": sorted(buffer_pages), "text": buffer.strip()})
            buffer = ""
            buffer_pages = set()
        buffer += para + "\n\n"
        buffer_pages.add(page["page"])

if buffer.strip():
    chunks.append({"pages": sorted(buffer_pages), "text": buffer.strip()})

with open(output_path, "w", encoding="utf-8") as f:
    json.dump(chunks, f, ensure_ascii=False, indent=2)

print(f"Created {len(chunks)} chunks from {len(doc['pages'])} pages")