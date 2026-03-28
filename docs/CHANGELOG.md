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
