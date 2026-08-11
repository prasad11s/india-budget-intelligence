import pdfplumber
import json

pdf_path = "data/raw/budget_at_a_glance.pdf"
output_path = "data/processed/budget_at_a_glance.json"

pages = []
with pdfplumber.open(pdf_path) as pdf:
    for i, page in enumerate(pdf.pages, start=1):
        text = page.extract_text()
        pages.append({"page": i, "text": text})

doc = {
    "filename": "budget_at_a_glance.pdf",
    "year": "2026_27",
    "doc_type": "budget_at_a_glance",
    "pages": pages
}

with open(output_path, "w", encoding="utf-8") as f:
    json.dump(doc, f, ensure_ascii=False, indent=2)

print(f"Extracted {len(pages)} pages to {output_path}")