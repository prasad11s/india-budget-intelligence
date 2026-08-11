import pdfplumber
import json

pdf_path = "data/raw/bs2026_27.pdf"
output_path = "data/processed/bs2026_27.json"

pages = []
with pdfplumber.open(pdf_path) as pdf:
    for i, page in enumerate(pdf.pages, start=1):
        text = page.extract_text()
        pages.append({"page": i, "text": text})

output = {
    "filename": "bs2026_27.pdf",
    "year": "2026_27",
    "doc_type": "budget_speech",
    "pages": pages
}

with open(output_path, "w", encoding="utf-8") as f:
    json.dump(output, f, indent=2, ensure_ascii=False)

print(f"Extracted {len(pages)} pages")