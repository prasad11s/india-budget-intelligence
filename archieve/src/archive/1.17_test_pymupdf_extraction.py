import fitz

pdf_path = "data/raw/economic_surveys/1957-1958/chapters/6%20Conclusion.pdf"

doc = fitz.open(pdf_path)
print(f"Total pages: {len(doc)}")

for i, page in enumerate(doc[:3]):
    text = page.get_text()
    char_count = len(text)
    print(f"\nPage {i+1}: {char_count} characters extracted")
    if text:
        print(f"Preview: {text[:200]}")
    else:
        print("Preview: (still nothing extracted)")