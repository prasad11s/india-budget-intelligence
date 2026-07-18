# CHANGELOG

## March 14, 2026 - Session 1
- Project concept finalized
- Scope document v1.1 created
- GitHub repository and Project board set up
- Tool stack and timeline defined

## March 28, 2026 - Session 3

### What was done
- Wrote download_budget_speeches.py to download all budget speech PDFs
- Discovered special/interim budget URL patterns through manual investigation
- Discovered recent years (2023 onwards) use new underscore URL pattern
- Successfully downloaded 92 budget speech PDFs to data/raw/budget_speeches/
- Added data/ to .gitignore to exclude raw files from GitHub

### Decisions made
- data/ folder excluded from GitHub — code goes to GitHub, raw data stays local
- Rerunnable script design — skips existing files, safe to run multiple times

### Known gaps
- bs199900 (1999-2000) — missing from government server
- bs201011 (2010-11) — missing from government server  
- 2008-09 and 2009-10 main speeches — HTML format, handled separately later
- 2014-15 (I) interim — served as generic bs.pdf, not year-specific

### Next session plan
- Begin Phase 2: Text extraction from downloaded PDFs using pdfplumber
- Test extraction on a few files across different decades
- Check text quality of older vs newer PDFs

# CHANGELOG
## Indian Budget Intelligence System

---

## March 14, 2026 - Session 1
### What was done
- Project concept finalized
- Scope document v1.1 created
- GitHub repository and Project board set up
- Tool stack and timeline defined

---

## March 28, 2026 - Session 2
### What was done
- Explored indiabudget.gov.in site structure manually
- Confirmed all budget speeches (1947-present) are typed/digitized PDFs — no OCR needed
- Mapped Economic Survey URL patterns across decades
- Created DATA_CATALOG.md with year-wise format notes
- Created WORKLOG.md for session-by-session progress tracking
- Identified 1984-85 speech link as potentially broken (later confirmed working)

### Decisions made
- Phased data collection plan established: 1A (speeches) → 1B (recent surveys) → 1C (older surveys) → 1D (full budget docs)
- Sentiment analysis and topic modeling pulled into MVP scope
- AWS S3 preferred for cloud storage over Google Drive

## March 28-29, 2026 - Session 3
### What was done

#### Phase 1A — Budget Speeches
- Wrote `src/download_budget_speeches.py`
- Discovered special/interim budget URL patterns through manual investigation
- Discovered recent years (2023 onwards) use new underscore URL pattern (`bs2023_24.pdf`)
- Successfully downloaded 92 budget speech PDFs to `data/raw/budget_speeches/`
- Added `data/` to `.gitignore` to exclude raw files from GitHub

#### Phase 1B — Economic Surveys
- Wrote `src/collect_survey_links.py` — scrapes all PDF links from allpes.php
- Saves links to `docs/survey_links.csv` with columns: year, page_url, pdf_url, filename, language
- Collected 1305 links across 70 survey years
- Wrote `src/download_economic_surveys.py` — CSV-based download script
- Downloaded ~546 Economic Survey PDFs organized into:
  - `data/raw/economic_surveys/{year}/chapters/`
  - `data/raw/economic_surveys/{year}/statistical_appendix/`
- Covered survey years: 2018-19 to 2024-25 (clean PDFs) + older archive years where links were available

#### Phase 1C/1D — Budget Documents
- Wrote `src/collect_budget_doc_links.py` — scrapes all budget document links
- Saves to `docs/budget_doc_links.csv` — 3588 links across 42 years
- Wrote `src/collect_dea_budget_links.py` — scrapes older budget PDFs from dea.gov.in
- Saves to `docs/dea_budget_links.csv` — 48 full budget PDFs (1947-1995)
- Wrote `src/download_budget_docs.py` — CSV-based download script
- Downloaded 81 full budget documents (1947-1995) from dea.gov.in
- Downloaded key structured docs for 2021-2025: alldg.pdf, allsbe.xls, allafs.pdf/xlsx

### Decisions made
- Separate scripts for collecting links vs downloading — separation of concerns principle
- CSV as single source of truth for all downloads
- Year-wise folder structure with doc-type subfolders
- `data/` excluded from GitHub — code goes to repo, raw data stays local
- All download scripts are rerunnable — skip existing files automatically
- Moved to Phase 2 (text extraction) without completing 2011-2020 budget docs — can be added later via rerun

### Known gaps
- `bs199900` (1999-2000 speech) — missing from government server
- `bs201011` (2010-11 speech) — missing from government server
- 2008-09 and 2009-10 main speeches — HTML format, not yet handled
- Budget documents 2011-2020 — `allsbe.xls` and `alldg.pdf` not yet downloaded (classifier issue)
- Budget documents 1996-2010 — JavaScript-rendered archive pages, not scraped
- Economic Surveys 2010-2014, 2016-2018 — URL patterns not confirmed
- dea.gov.in files (1947-1995) are large scanned PDFs — OCR will be needed during Phase 2

### Tools/scripts created this session
- `src/download_budget_speeches.py`
- `src/collect_survey_links.py`
- `src/download_economic_surveys.py`
- `src/collect_budget_doc_links.py`
- `src/collect_dea_budget_links.py`
- `src/download_budget_docs.py`
- `src/probe_survey_urls.py` (investigation tool)
- `src/scrape_survey_links.py` (investigation tool)
- `docs/survey_links.csv`
- `docs/budget_doc_links.csv`
- `docs/dea_budget_links.csv`

### Next session plan
- Phase 2: Text extraction pipeline
- Install pdfplumber, test extraction on budget speeches
- Build extraction script that scans folders, processes new files, skips already processed
- Check text quality across different decades (1947 vs 1990 vs 2020)
- Handle Excel files with pandas
- Output: structured JSON per document with metadata (year, doc_type, page, text)

## March 31, 2026 - Session 5

### What was done
- Created data/processed/ folder structure (budget_speeches, economic_surveys, budget_documents)
- Wrote src/extract_text.py — text extraction pipeline using pdfplumber
- Pipeline design:
  - Scans all subfolders under data/raw/ automatically (os.walk)
  - Extracts text page by page with page numbers preserved
  - Saves one JSON per PDF with metadata (year, doc_type, filename, source, pages)
  - Skip logic — safe to rerun, only processes new files
- Debugged and fixed year parsing:
  - Budget speeches: year parsed from filename (bs2023_24.pdf → 2023_24)
  - Budget documents/surveys: year parsed from folder structure
- Extraction results:
  - budget_speeches: 92/92 extracted, 0 failed
  - economic_surveys: 544/546 extracted, 2 unknown (likely scanned)
  - budget_documents: 61/72 extracted, 11 failed (password protected PDFs)

### Known issues
- 11 budget document PDFs (allafs.pdf, alldg.pdf from 2021-2026) are password protected — skipped for now
- Budget speeches year field is filename-based (2023_24 format) not fiscal year format (2023-24) — acceptable for now, can normalize in chunking phase

### Next session plan
- Phase 3: Chunking + metadata
- Split each JSON into ~500 word overlapping chunks
- Each chunk carries year, doc_type, source, page number as metadata