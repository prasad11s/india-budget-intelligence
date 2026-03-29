# Project Knowledge Document
## Indian Budget Intelligence System
**Author:** Prasad | **Purpose:** Interview prep + personal learning reference

---

## Phase 1 — Data Collection

### What I did
- Downloaded 92 budget speech PDFs (1947-2025)
- Downloaded ~546 Economic Survey PDFs (1957-2025)
- Downloaded 81 full budget documents (1947-1995) from dea.gov.in
- Downloaded key budget documents for 2021-2025
- Built reusable, CSV-driven download pipeline

---

## Tools & Concepts Used

### 1. `requests` library
**What it is:** Python library for making HTTP requests — same as what your browser does when it opens a URL, but in code.

**How I used it:** `requests.get(url)` to download PDF files from government websites.

**Key concept:** HTTP status codes
- `200` = success
- `404` = file not found
- `503` = server temporarily unavailable

**Interview question:** *"How did you handle failed downloads?"*
> Answer: Used try/except to catch errors, checked status codes, maintained a `failed` list, and built skip logic so the script could be safely rerun.

---

### 2. `BeautifulSoup` (bs4)
**What it is:** Python library for parsing HTML — it reads the raw HTML of a webpage and lets you find specific elements like links, headings, and buttons.

**How I used it:** Scraped PDF links from government archive pages like `indiabudget.gov.in/economicsurvey/allpes.php` and `dea.gov.in/budget-division/469`.

**Key concept:** HTML parsing
- Every webpage is HTML text
- BeautifulSoup converts that text into a searchable structure
- `soup.find_all("a", href=True)` finds all link elements

**Limitation I discovered:** BeautifulSoup can only read static HTML. If a page loads content via JavaScript (like dea.gov.in's VIEW buttons), BeautifulSoup sees an empty page. This is why some pages showed "No document links found."

**Interview question:** *"What's the difference between static and dynamic web scraping?"*
> Answer: Static scraping (BeautifulSoup) reads the raw HTML. Dynamic scraping (Selenium, Playwright) actually runs the JavaScript in a browser. dea.gov.in required dynamic scraping for full pagination — we worked around it by directly probing known URL patterns.

---

### 3. CSV files with `csv` module
**What it is:** Comma-Separated Values — a simple tabular data format. Python's built-in `csv` module reads and writes these files.

**How I used it:** Saved all scraped links to CSV files (`survey_links.csv`, `budget_doc_links.csv`) as the single source of truth for downloads.

**Key concept:** Separation of concerns
- Script 1 collects links → saves to CSV
- Script 2 reads CSV → downloads files
- If download fails, just rerun Script 2 — no need to re-scrape

**Interview question:** *"Why did you use CSV instead of just downloading directly in the scraper?"*
> Answer: Separating collection from downloading makes the pipeline more robust. If a download fails midway, I don't need to re-scrape 70 pages — I just rerun the downloader. It also gives me a record of what's available before I commit to downloading.

---

### 4. `os` module
**What it is:** Python's built-in module for interacting with the operating system — creating folders, checking if files exist, building file paths.

**How I used it:**
- `os.makedirs(path, exist_ok=True)` — creates nested folders without crashing if they already exist
- `os.path.exists(filepath)` — checks if a file is already downloaded before re-downloading
- `os.path.join()` — builds file paths correctly on any OS (Windows uses `\`, Mac/Linux use `/`)

**Interview question:** *"How did you make your download scripts rerunnable?"*
> Answer: Before every download, I check `os.path.exists(filepath)`. If the file already exists, skip it. This means the script can run 100 times safely — it only downloads what's missing.

---

### 5. `time.sleep()`
**What it is:** Pauses the script for a specified number of seconds.

**How I used it:** Added `time.sleep(0.5)` or `time.sleep(1)` between every HTTP request.

**Why it matters:** Sending hundreds of requests per second to a government server is called a "denial of service" — it can crash their server and get your IP blocked. Being polite with delays is both ethical and practical.

**Interview question:** *"How did you avoid getting blocked while scraping?"*
> Answer: Added sleep delays between requests, used HEAD requests (lighter than GET) for URL checking, and spread downloads over time rather than hitting the server all at once.

---

### 6. `requests.head()` vs `requests.get()`
**What it is:** Two types of HTTP requests.
- `GET` — downloads the full file content
- `HEAD` — only checks if the file exists, without downloading it

**How I used it:** Used `HEAD` requests in the probe script to check which URL patterns existed without downloading 100MB files unnecessarily.

**Interview question:** *"How did you efficiently check hundreds of URLs without downloading everything?"*
> Answer: Used HEAD requests — they return just the HTTP status code (200/404) without downloading the file body. Much faster and lighter than GET requests for existence checks.

---

### 7. URL patterns and string formatting
**What it is:** Constructing URLs programmatically using Python f-strings.

**How I used it:**
```python
url = f"https://www.indiabudget.gov.in/doc/bspeech/bs{year}.pdf"
```

**Key concept:** Government websites follow predictable URL patterns. Once you identify the pattern, you can generate hundreds of URLs with a loop instead of manually copying each one.

**What I discovered:** URL patterns changed across decades — required investigation and multiple pattern variants.

---

### 8. Error handling with `try/except`
**What it is:** Python's mechanism for gracefully handling errors without crashing the program.

**How I used it:**
```python
try:
    response = requests.get(url, timeout=30)
except Exception as e:
    print(f"ERROR: {e}")
    failed.append(url)
```

**Why it matters:** Network requests can fail for many reasons — timeout, server down, connection reset. Without try/except, one failed request would crash the entire script after hours of downloading.

---

### 9. File classification with `classify()` function
**What it is:** A function that looks at a filename and categorizes it into a document type.

**How I used it:** Created a `classify()` function that maps filenames like `alldg.pdf` → `demands_for_grants`, `echap01.pdf` → `chapters`, `Statistical-Appendix-in-English.pdf` → `statistical_appendix`.

**Key concept:** Rule-based classification — using keyword matching to categorize data. Simple but effective when the naming patterns are known.

---

### 10. Data pipeline design
**What it is:** A sequence of steps that transforms raw data from source to destination.

**My pipeline:**
```
Website → Scraper → CSV → Downloader → Organized folders
```

**Key engineering principles applied:**
- **Idempotency** — running the script multiple times gives the same result (no duplicates, no crashes)
- **Separation of concerns** — each script does one job
- **Fail gracefully** — errors are logged, not fatal
- **Reusability** — any new data source can be added by updating the CSV

---

## Possible Interview Questions — Phase 1

| Question | Key Points in Answer |
|---|---|
| Walk me through your data collection pipeline | Scraper → CSV → Downloader, separation of concerns, rerunnable |
| How did you handle inconsistent URL patterns? | Manual investigation first, then automated probing, then scripted download |
| What's BeautifulSoup and when does it fail? | Parses static HTML, fails on JavaScript-rendered content |
| How did you make scripts production-ready? | Exists check, error handling, logging, sleep delays |
| What's the difference between GET and HEAD requests? | GET downloads content, HEAD only checks existence |
| Why CSV as intermediate storage? | Decouples scraping from downloading, enables reruns |
| How did you organize downloaded files? | Year-wise folders, doc-type subfolders, consistent naming |
| What would you do differently? | Use Selenium for JS pages, add retry logic with exponential backoff |

---

## What's Next — Phase 2 (Text Extraction)

### Tools I will use
- `pdfplumber` — extract text from clean PDFs
- `pytesseract` — OCR for scanned PDFs
- `pandas` / `openpyxl` — process Excel files
- `json` — store extracted text with metadata

### Key concept I will learn
**Chunking** — splitting long documents into smaller pieces for embedding. A 500-page PDF needs to be split into ~300 word chunks so the RAG system can retrieve specific sections rather than entire documents.
