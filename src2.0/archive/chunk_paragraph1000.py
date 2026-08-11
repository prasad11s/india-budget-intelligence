import json
import re

TARGET_SIZE = 1000
OVERLAP_SENTENCES = 1

with open("data/processed/bs2026_27.json", "r", encoding="utf-8") as f:
    doc = json.load(f)

sentences = []
for page in doc["pages"]:
    text = (page["text"] or "").replace("\n", " ")
    for sent in re.split(r"(?<=[.!?])\s+", text):
        sent = sent.strip()
        if sent:
            sentences.append({"text": sent, "page": page["page"]})

def chunk_by_sentences(sentences, target_size, overlap_sentences, doc_type, year, filename, method_name):
    chunks = []
    current = []
    chunk_id = 0

    def flush():
        nonlocal chunk_id, current
        if not current:
            return
        chunk_text = " ".join(s["text"] for s in current)
        chunks.append({
            "chunk_id": f"{year}_{method_name}_{chunk_id:04d}",
            "text": chunk_text,
            "year": year,
            "doc_type": doc_type,
            "filename": filename,
            "page_start": current[0]["page"],
            "page_end": current[-1]["page"],
            "chunk_method": method_name
        })
        chunk_id += 1

    for sent in sentences:
        prospective_len = sum(len(s["text"]) for s in current) + len(sent["text"])
        if current and prospective_len > target_size:
            flush()
            current = current[-overlap_sentences:] if overlap_sentences else []
        current.append(sent)
    flush()
    return chunks

chunks = chunk_by_sentences(
    sentences, TARGET_SIZE, OVERLAP_SENTENCES,
    doc["doc_type"], doc["year"], doc["filename"],
    method_name=f"para_{TARGET_SIZE}"
)

with open(f"data/processed/chunks_para_{TARGET_SIZE}.json", "w", encoding="utf-8") as f:
    json.dump(chunks, f, indent=2, ensure_ascii=False)

print(f"Created {len(chunks)} chunks")