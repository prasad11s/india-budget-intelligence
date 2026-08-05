import pdfplumber
import fitz
import pytesseract
from PIL import Image
import io
import json
import os

pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

RAW_DIR = "data/raw"
PROCESSED_DIR = "data/processed"

FOLDERS = {
    "budget_speeches": "budget_speeches",
    "economic_surveys": "economic_surveys",
    "budget_documents": "budget_documents"
}

MIN_CHARS_BEFORE_OCR = 30


def ocr_page(fitz_doc, page_number):
    page = fitz_doc[page_number]
    pix = page.get_pixmap(dpi=300)
    img = Image.open(io.BytesIO(pix.tobytes("png")))
    return pytesseract.image_to_string(img, lang="eng")


def extract_pdf(pdf_path):
    pages = []
    fitz_doc = None
    try:
        with pdfplumber.open(pdf_path) as pdf:
            for i, page in enumerate(pdf.pages, start=1):
                text = page.extract_text() or ""
                if len(text.strip()) < MIN_CHARS_BEFORE_OCR:
                    if fitz_doc is None:
                        fitz_doc = fitz.open(pdf_path)
                    text = ocr_page(fitz_doc, i - 1)
                pages.append({"page": i, "text": text})
    finally:
        if fitz_doc is not None:
            fitz_doc.close()
    return pages


def get_metadata(pdf_path, doc_type):
    parts = pdf_path.replace("\\", "/").split("/")
    filename = parts[-1]
    raw_idx = parts.index("raw")
    after_type = parts[raw_idx + 2:]

    if doc_type == "budget_speeches":
        year = filename.replace("bs", "").replace(".pdf", "")
    elif len(after_type) > 1:
        year = parts[raw_idx + 2]
    else:
        year = "unknown"

    return {
        "year": year,
        "doc_type": doc_type,
        "filename": filename,
        "source": pdf_path
    }


def already_processed(out_path):
    return os.path.exists(out_path)


def process_folder(doc_type):
    raw_folder = os.path.join(RAW_DIR, FOLDERS[doc_type])
    processed_folder = os.path.join(PROCESSED_DIR, FOLDERS[doc_type])

    pdf_files = []
    for root, dirs, files in os.walk(raw_folder):
        for f in files:
            if f.lower().endswith(".pdf"):
                pdf_files.append(os.path.join(root, f))

    print(f"\n{doc_type}: {len(pdf_files)} PDFs found")

    skipped, success, failed = 0, 0, 0

    for pdf_path in pdf_files:
        rel_path = os.path.relpath(pdf_path, raw_folder)
        out_name = rel_path.replace("\\", "_").replace("/", "_").replace(".pdf", ".json")
        out_path = os.path.join(processed_folder, out_name)

        if already_processed(out_path):
            skipped += 1
            continue

        try:
            pages = extract_pdf(pdf_path)
            metadata = get_metadata(pdf_path, doc_type)
            output = {**metadata, "pages": pages}

            with open(out_path, "w", encoding="utf-8") as f:
                json.dump(output, f, ensure_ascii=False, indent=2)
            success += 1
            print(f"  OK: {out_name}")
        except Exception as e:
            failed += 1
            print(f"  FAIL: {pdf_path} - {e}")

    print(f"  Done - {success} extracted, {skipped} skipped, {failed} failed")


for doc_type in FOLDERS:
    process_folder(doc_type)

print("\nExtraction complete.")