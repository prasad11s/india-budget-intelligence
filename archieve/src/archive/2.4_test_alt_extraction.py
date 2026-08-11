import fitz  # PyMuPDF

PDF_PATH = "data/raw/budget_documents/1969-70/full_budget/BUDGET1969-70.pdf"

doc = fitz.open(PDF_PATH)
print(f"Total pages: {len(doc)}")

# Print the same early page range that looked garbled via pdfplumber
for page_num in [0, 1, 2]:
    text = doc[page_num].get_text()
    print(f"\n=== Page {page_num} (PyMuPDF) ===")
    print(text[:300])