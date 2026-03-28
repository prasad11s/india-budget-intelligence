# Data Catalog
## Indian Budget Intelligence System

**Last Updated:** March 15, 2026
**Status:** Phase 1 - Exploration In Progress

---

## Data Sources Overview

| Source | URL | Years Available | Format |
|---|---|---|---|
| Budget Speeches | indiabudget.gov.in/bspeech.php | 1947-48 to 2025-26 | PDF (typed/digitized) |
| Full Budget Documents | indiabudget.gov.in/previous_union_budget.php + dea.gov.in/budget-division/469 | 1947-48 to 2025-26 | Mixed (PDF, HTML, Excel) |
| Economic Surveys | indiabudget.gov.in/economicsurvey/allpes.php | 1957-58 to 2024-25 | Mixed (scanned PDF, chapter-wise PDF, HTML) |

---

## 1. Budget Speeches

**Source URL:** https://www.indiabudget.gov.in/bspeech.php

**URL Pattern:** `https://www.indiabudget.gov.in/doc/bspeech/bs{year}.pdf`

**Key Observations:**
- ALL budget speeches from 1947-48 onward are typed/digitized PDFs
- Text is selectable/copyable even in oldest documents (1947-48 confirmed)
- OCR likely NOT needed for budget speeches — direct text extraction should work
- Some years have interim budgets marked with `(I)` — these are separate documents
- Some years have special budgets (e.g., 1965-66 August, 1974-75 July)
- 2008-09 and 2009-10 link to `.htm` pages instead of direct PDFs
- 1984-85 link may be broken (to be verified — possibly the emergency period budget)

**Document Count:** ~85-90 files (including interim and special budgets)

### Year-wise Format Notes

| Period | Format | Text Extractable? | OCR Needed? | Notes |
|---|---|---|---|---|
| 1947-48 to ~1970s | Typed/digitized PDF | Yes (copy-paste works) | No | Old typewriter font but selectable text |
| ~1970s to ~1990s | Typed/digitized PDF | Yes | No | Quality improves over time |
| ~1990s to 2007 | Clean PDF | Yes | No | Modern formatting |
| 2008-09 to 2010-11 | HTML pages (.htm) | Yes (scrape HTML) | No | Different format — need HTML scraping |
| 2011-12 to present | Clean PDF | Yes | No | Modern clean PDFs |

### Special Cases
- Years with interim budgets `(I)`: 1952-53, 1957-58, 1962-63, 1967-68, 1971-72, 1977-78, 1980-81, 1991-92, 1996-97, 1998-99, 2004-05, 2009-10, 2014-15, 2019-20, 2024-25
- Special budgets: 1956-57 (November), 1965-66 (August), 1971-72 (December), 1974-75 (July)
- Broken/missing: 1984-85 (to be investigated)

---

## 2. Full Budget Documents

**Source URLs:**
- https://www.indiabudget.gov.in/previous_union_budget.php
- https://dea.gov.in/budget-division/469

**Key Observations:**
- These contain MUCH more than just the speech — financial statements, expenditure budgets, demands for grants, receipt budgets, etc.
- Structure varies significantly across decades
- Pre-2000: Scattered archive pages with inconsistent HTML structures
- Post-2000: More organized but still chapter/section-wise
- Some years include "Budget at a Glance" summaries
- Some years include Excel data alongside PDFs (e.g., 2011-12 Expenditure Budget Volume II in Excel)

### Sub-documents within Full Budget (example from 2011-12)
- Key to Budget Documents
- Budget Highlights (Key Features)
- Budget Speech
- Budget at a Glance
- Annual Financial Statement
- Finance Bill
- Memorandum
- Receipt Budget
- Expenditure Budget (Volume I, Volume II in PDF, Volume II in Excel)
- Customs & Central Excise
- Macro Economic Framework Statement
- Medium Term Fiscal Policy Statement
- Fiscal Policy Strategy Statement
- Statement of Revenue Foregone
- Implementation of Budget Announcements

### Decision for MVP
**For MVP, we will focus on Budget Speeches only from this source.** Full budget documents with financial data can be added in Phase 2. The Expenditure Budget Excel files are high-value targets for future numerical analysis.

---

## 3. Economic Surveys

**Source URL:** https://www.indiabudget.gov.in/economicsurvey/allpes.php

**Historical Note:** The Economic Survey was first published in 1950-51 as part of the Union Budget documents. It was separated from the budget in 1964 and has since been presented in Parliament a day before the Union Budget. The earliest survey available on the website is 1957-58.

### URL Patterns (inconsistent across decades)

| Period | URL Pattern | Format |
|---|---|---|
| 1957-58 to ~1996 | `/budget_archive/es{year}/esmain.htm` | HTML index → chapter-wise PDFs (likely scanned) |
| 1997-98 to 2000-01 | `/budget_archive/es{year}/welcome.html` | HTML pages |
| 2001-02 to 2003-04 | `/budget_archive/es{year}/esmain.htm` or `/welcome.html` | HTML pages |
| 2004-05 to 2008-09 | `/budget_archive/es{year}/esmain.htm` | HTML index → chapter PDFs |
| 2009-10 to 2017-18 | `/budget{year}/economicsurvey/index.php` or `.html` or `survey.asp` | Chapter-wise PDFs |
| 2018-19 to present | `/budget{year}/economicsurvey/index.php` | Chapter-wise PDFs (clean) |

**Key Observations:**
- Each survey is split into multiple chapters (typically 10-13 chapters)
- Older surveys (1957-58 through ~1980s) are scanned image PDFs — OCR WILL be needed
- The 1958-59 survey confirmed as scanned but readable quality
- 1974-75 has THREE separate parts
- 1991-92 has TWO parts (A and B) — liberalization year
- No 1959-60 survey listed (gap — may not exist or not digitized)
- Recent surveys also include: Highlights, Infographics, Statistical Appendix (with tables)
- Statistical Appendix tables available as PDF — potentially parseable for numerical data

### Estimated Document Count
- ~65 survey years × average ~10 chapters = ~650+ individual PDF files
- Plus statistical appendices, highlights, and infographics

---

## 4. Phased Data Collection Plan

### Phase 1A (MVP Priority — Start Here)
**Budget Speeches only** — ~85-90 PDF files from bspeech.php
- All typed/digitized — direct text extraction
- Single URL pattern — easy to script
- Fastest path to a working demo

### Phase 1B (Next)
**Economic Surveys (recent first)** — 2004-05 to 2024-25
- Clean PDFs, chapter-wise
- ~20 years × ~10 chapters = ~200 files
- May need to navigate different page structures per year

### Phase 1C (Later)
**Economic Surveys (older)** — 1957-58 to 2003-04
- Scanned PDFs — OCR required
- HTML archive pages with inconsistent structures
- Higher effort, lower priority for MVP

### Phase 1D (Future)
**Full Budget Documents + Excel Data**
- Expenditure budgets, financial statements, demands for grants
- Excel files for numerical analysis
- Budget at a Glance summaries

---

## 5. Known Issues & Gaps

| Issue | Details | Impact | Action |
|---|---|---|---|
| 1984-85 budget speech not opening | Link may be broken or file missing | One year gap | Investigate alternative sources |
| 2008-10 speeches are HTML not PDF | Different extraction method needed | Minor — 3 files | Write separate HTML scraper |
| No Economic Survey for 1959-60 | Not listed on the site | One year gap | Verify if it was published that year |
| Economic Survey started in 1950-51 | But earliest on website is 1957-58 | Missing 7 early years | Check National Archives or other sources |
| Older Economic Surveys are scanned | 1957-58 through ~1980s | OCR needed | Defer to Phase 1C |
| URL patterns inconsistent | Different structures across decades for Economic Surveys | Scraping complexity | Build separate scrapers per era |

---

## 6. Data Quality Checklist (To Fill During Extraction)

*Template for each document — to be filled as we process files*

| Year | Document Type | Pages | Format | Text Extractable? | Language | Quality Score (1-5) | Notes |
|---|---|---|---|---|---|---|---|
| 1947-48 | Budget Speech | 146 | Typed PDF | Yes | English | TBD | First budget, old typewriter font |
| 1959-60 | Budget Speech | 582 | Typed PDF | Yes | English | TBD | Very long document |
| 1958-59 | Economic Survey Ch.1 | 2 | Scanned PDF | Needs OCR | English | TBD | Readable scan quality |
| ... | ... | ... | ... | ... | ... | ... | ... |

*This table will be populated during Phase 2 (Text Extraction)*
