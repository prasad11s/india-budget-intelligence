import fitz
import pytesseract
from PIL import Image
import io

# If Tesseract isn't on your PATH, uncomment and set this to your install path:
pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

PDF_PATH = "data/raw/budget_documents/1969-70/full_budget/BUDGET1969-70.pdf"

doc = fitz.open(PDF_PATH)
page = doc[0]

pix = page.get_pixmap(dpi=300)
img = Image.open(io.BytesIO(pix.tobytes("png")))

text = pytesseract.image_to_string(img)
print("=== OCR result, page 0 ===")
print(text[:500])