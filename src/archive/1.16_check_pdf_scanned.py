import glob
import pdfplumber

pdf_files = glob.glob("data/raw/economic_surveys/1957-1958/**/*.pdf", recursive=True)
print(f"PDFs found for 1957-1958: {pdf_files}")

for pdf_path in pdf_files:
    print(f"\n{'='*60}\n{pdf_path}\n{'='*60}")
    with pdfplumber.open(pdf_path) as pdf:
        print(f"Total pages: {len(pdf.pages)}")
        for i, page in enumerate(pdf.pages[:3]):
            text = page.extract_text()
            char_count = len(text) if text else 0
            print(f"\nPage {i+1}: {char_count} characters extracted")
            if text:
                print(f"Preview: {text[:200]}")
            else:
                print("Preview: (nothing extracted, likely a scanned image)")