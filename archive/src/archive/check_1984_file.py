import fitz
import pytesseract
from PIL import Image
import io
import time

pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

pdf_path = "data/raw/budget_documents/1984-85/full_budget/BUDGETVOLUMEFOR1984-85.pdf"

doc = fitz.open(pdf_path)
print(f"Total pages: {len(doc)}")

start = time.time()
for i in range(min(3, len(doc))):
    page_start = time.time()
    page = doc[i]
    pix = page.get_pixmap(dpi=300)
    img = Image.open(io.BytesIO(pix.tobytes("png")))
    text = pytesseract.image_to_string(img, lang="eng")
    print(f"Page {i+1}: {len(text)} chars, took {time.time() - page_start:.1f} seconds")

print(f"\nTotal time for {min(3, len(doc))} pages: {time.time() - start:.1f} seconds")