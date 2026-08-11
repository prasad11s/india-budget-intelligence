import os
import glob
import json
import pdfplumber

INPUT_DIR = "data/raw/budget_speeches"
OUTPUT_DIR = "data/processed/budget_speeches"


def year_from_filename(filename):
    # bs2023_24.pdf -> 2023_24, bs199798.pdf -> 199798
    name = os.path.splitext(filename)[0]
    return name.replace("bs", "")


def extract_pdf(path):
    pages = []
    with pdfplumber.open(path) as pdf:
        for i, page in enumerate(pdf.pages, start=1):
            text = page.extract_text() or ""
            pages.append({"page_number": i, "text": text})
    return pages


def main():
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    pdf_files = sorted(glob.glob(os.path.join(INPUT_DIR, "*.pdf")))
    print(f"Found {len(pdf_files)} PDF files")

    extracted = 0
    skipped = 0
    failed = []

    for pdf_path in pdf_files:
        filename = os.path.basename(pdf_path)
        output_path = os.path.join(OUTPUT_DIR, filename.replace(".pdf", ".json"))

        if os.path.exists(output_path):
            skipped += 1
            continue

        try:
            pages = extract_pdf(pdf_path)
            doc = {
                "year": year_from_filename(filename),
                "doc_type": "budget_speech",
                "filename": filename,
                "source": pdf_path,
                "pages": pages,
            }
            with open(output_path, "w", encoding="utf-8") as f:
                json.dump(doc, f, ensure_ascii=False, indent=2)
            extracted += 1
            print(f"Extracted: {filename}, {len(pages)} pages")
        except Exception as e:
            failed.append(filename)
            print(f"FAILED: {filename}, {e}")

    print(f"\nExtracted: {extracted}, Skipped (already done): {skipped}, Failed: {len(failed)}")
    if failed:
        print("Failed files:", failed)


if __name__ == "__main__":
    main()