import re
import json
import glob
import os

INPUT_DIR = "data/processed/budget_speeches"
OUTPUT_FILE = "data/processed/budget_speeches_chunks_para750.jsonl"
TARGET_SIZE = 750
OVERLAP_SENTENCES = 1

SENTENCE_SPLIT = re.compile(r"(?<=[.])\s+")


def split_sentences(text):
    return [s.strip() for s in SENTENCE_SPLIT.split(text) if s.strip()]


def chunk_document(pages, year, filename, doc_type="budget_speech"):
    sentences = []
    for page in pages:
        page_num = page.get("page_number") or page.get("page")
        text = page.get("text", "")
        if not text.strip():
            continue
        for sent in split_sentences(text):
            sentences.append((sent, page_num))

    chunks = []
    current = []
    current_len = 0
    idx = 0

    for sent, page in sentences:
        if current and current_len + len(sent) > TARGET_SIZE:
            chunks.append(build_chunk(current, year, filename, doc_type, idx))
            idx += 1
            current = current[-OVERLAP_SENTENCES:] if OVERLAP_SENTENCES else []
            current_len = sum(len(s) for s, _ in current)
        current.append((sent, page))
        current_len += len(sent)

    if current:
        chunks.append(build_chunk(current, year, filename, doc_type, idx))

    return chunks


def build_chunk(sentence_list, year, filename, doc_type, idx):
    text = " ".join(s for s, _ in sentence_list)
    return {
        "chunk_id": f"{year}_{filename}_{idx:04d}",
        "text": text,
        "year": year,
        "doc_type": doc_type,
        "filename": filename,
        "page_start": sentence_list[0][1],
        "page_end": sentence_list[-1][1],
        "chunk_method": "para_750",
    }


def main():
    files = sorted(glob.glob(os.path.join(INPUT_DIR, "*.json")))
    print(f"Found {len(files)} extracted speech files")

    total_chunks = 0
    with open(OUTPUT_FILE, "w", encoding="utf-8") as out:
        for path in files:
            with open(path, "r", encoding="utf-8") as f:
                doc = json.load(f)

            year = doc.get("year", "unknown")
            filename = doc.get("filename", os.path.basename(path))
            doc_type = doc.get("doc_type", "budget_speech")
            pages = doc.get("pages", [])

            chunks = chunk_document(pages, year, filename, doc_type)
            for c in chunks:
                out.write(json.dumps(c, ensure_ascii=False) + "\n")

            total_chunks += len(chunks)
            print(f"{filename}: {len(chunks)} chunks")

    print(f"\nTotal: {total_chunks} chunks across {len(files)} speeches")
    print(f"Written to {OUTPUT_FILE}")


if __name__ == "__main__":
    main()