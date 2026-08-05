import fitz
import pytesseract
from PIL import Image
import io

pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

pdf_path = "data/raw/economic_surveys/1957-1958/chapters/6%20Conclusion.pdf"

doc = fitz.open(pdf_path)
page = doc[0]

pix = page.get_pixmap(dpi=300)
img_bytes = pix.tobytes("png")
img = Image.open(io.BytesIO(img_bytes))

text = pytesseract.image_to_string(img)

print(f"Characters extracted via OCR: {len(text)}")
print(f"\nPreview:\n{text[:500]}")