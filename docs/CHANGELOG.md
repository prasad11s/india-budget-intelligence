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



## August 5, 2026 - Session 6

### What was done
- Fixed .gitignore: removed corrupted NUL byte lines left over from a UTF-16
  save in the config.ini exclusion block
- Added *_log.txt and structure.txt to .gitignore, since both are
  regenerated output rather than authored source
- Confirmed docs/config.ini (holding the OpenAI API key) was never
  committed to git history, using git log --all --full-history, so no key
  rotation was needed
- Reorganized src/ ahead of making the repository public, separating the
  live rerunnable pipeline from one time diagnostic and prototype scripts
  - Kept in src/ root: 1.1 through 1.7 (data collection), 2.1
    (extraction), 3.1 through 3.3 (chunking), 4.3 (embedding), 4.4 and 4.5
    (ChromaDB inspection, kept since both run fast and add value), 4.6
    through 4.8 (duplicate cleanup, documented one time fix), 5.6 (the
    real RAG query pipeline, matching the Phase 5 description in this
    changelog), 5.8 (coverage check)
  - Moved to src/archive/: superseded or single use diagnostic scripts
    from Phases 1, 2, 4, and 5, along with two scripts that had been
    created outside src/ by mistake (check_1984_file.py,
    cleanup_broken_processed.py)
  - Deleted outright, not archived: 1.10_check_pipeline_stages.py and
    1.12_find_unembedded_years.py, since both were superseded by corrected
    versions (1.11, 1.13) that fixed real bugs rather than simply being
    older iterations
- While reviewing src/2.1_extract_text.py and src/4.3_load_chromadb.py for
  the reorganization, found that both already contained real, working
  changes that had never been committed
  - 2.1_extract_text.py: added the OCR fallback path (fitz plus
    pytesseract plus PIL), with a MIN_CHARS_BEFORE_OCR threshold of 30
    characters, triggering OCR only on pages where direct extraction
    returns too little text
  - 4.3_load_chromadb.py: fixed a chunk ID collision bug. Chunk IDs were
    previously taken directly from each chunk's filename based chunk_id,
    which is not unique, since generic filenames such as echap-01.pdf
    repeat across many different survey years. IDs are now prefixed with
    the year before being written to ChromaDB, preventing one year's
    chunk from silently overwriting another year's chunk with the same
    filename. Also moved OpenAI client setup to read the API key from
    docs/config.ini through configparser, matching the pattern used
    elsewhere in the pipeline

### Decisions made
- Committed the folder reorganization and the two real pipeline fixes as
  two separate commits, rather than one combined commit, so that git
  history accurately distinguishes organizational changes from functional
  changes
- src/dev/ created but left empty for now, since nothing is currently in
  active development as distinct from finished pipeline code or archived
  history
- Archived scripts are committed to GitHub rather than gitignored, since
  they document real debugging work, such as the OCR and font encoding
  investigation and the embedding model comparison, consistent with the
  earlier decision to keep 4.6 through 4.8 as a documented fix rather than
  deleting them

### Known gaps and notes for later
- 5.6_run_golden_set.py currently loops over a fixed set of ten questions.
  Before it can serve a live interface, the retrieval, prompt building,
  and generation logic need to be pulled out into a callable function
- 3.1_chunk_budget_documents.py and 3.2_chunk_economic_surveys.py are
  currently identical except for their input and output paths, a
  candidate for merging later, not done in this session

### Next session plan
- Resume Phase 6 planning, the structured extraction fix for the numeric
  year misattribution issue identified during Phase 5 evaluation


## August 6, 2026 - Session 7

### What was done
- Ran empty-chunk check across all 3 doc types. Only real gap: the
  already-known 1984-85 corrupted PDF
- Found and fixed 2 bugs in 2.1_extract_text.py: case-sensitive .pdf
  replace (hid 2 survey files under wrong extension), underscore not
  stripped from newest budget speech years. Re-extracted + re-chunked
  the 6 affected files
- Found 1991-92 budget doc split across two badly-named folders
  (CENTRAL-BIDGET-91-92.pdf, 1992-92), confirmed via content, merged and
  fixed
- Checked download CSVs vs raw folder. demands_for_grants and
  expenditure_budget are mostly never-downloaded (2333/1237 missing) —
  deferring these, not core to RAG scope
- Built year_checklist.csv, one row per fiscal year, yes/no + real link
  for speech/budget doc/survey
- Found new gap: economic surveys 1997-98 to 2008-09 have no processed
  files at all, not previously documented
- 03_rerun_pipeline_verify.md is stale (written for an old, already-
  resolved coverage problem), ignored it

### Decisions made
- demands_for_grants / expenditure_budget: deliberate deferral, not a gap
- Trusting code + actual files over old changelog/task doc claims from
  now on, found stale info twice this session

### Known gaps / next session
- ChromaDB still has stale entries for the 6 fixed files + 2 budget docs
- 1997-2008 survey gap not fixed yet, needs scraper-level look
- known_data_gaps.md still not written to disk
- year_checklist.csv has a minor blank-cell display bug
- Resume Phase 6 structured extraction after this