# Indian Budget Intelligence System
## Project Scope Document

**Author:** Prasad
**AI Development Advisor:** Claude (Anthropic) — Architecture guidance, code review, research, and technical consultation. All decisions and implementation by the author.
**Date Created:** March 14, 2026
**Last Updated:** March 14, 2026
**Version:** 1.1
**Status:** Planning Phase

---

## 1. Problem Statement

India has published Union Budget speeches since 1947 and Economic Survey documents since 1957–58 (the first Economic Survey). Together, these represent over seven decades of fiscal policy data — covering government priorities, spending allocations, scheme launches, and economic assessments.

Despite being publicly available on government websites (primarily indiabudget.gov.in and the Ministry of Finance archives), this data is largely inaccessible in a queryable format. Documents are scattered across multiple sections, formats vary widely — early decades exist only as scanned image PDFs, later years are available as clean text PDFs, and some Economic Surveys are split across multiple chapter-wise files. Some Economic Survey sections also include numerical data in Excel format alongside PDF versions.

There is currently no unified system that allows a user to query, compare, or analyze this data across years using natural language.

---

## 2. Project Objective

Build an AI-powered natural language query system that enables users to ask questions about Indian fiscal policy (1947–present) and receive structured, cited answers drawn from Union Budget speeches and Economic Survey documents.

---

## 3. Target Users

- Citizens seeking to understand government fiscal decisions
- Students studying public policy, economics, or political science
- Academic researchers analyzing fiscal trends
- Stock market investors and financial analysts tracking policy impact
- Journalists covering economic policy
- Government employees and policy professionals

---

## 4. Scope — What's IN (MVP)

### Data Sources
- Union Budget speeches (1947–2026), sourced from indiabudget.gov.in
- Economic Survey documents (1957–58 onward), sourced from indiabudget.gov.in and Ministry of Finance archives
- Numerical/statistical data available in Excel format for select Economic Surveys

### Document Formats to Handle
- Scanned image PDFs (primarily pre-2000 documents)
- Clean text PDFs (primarily post-2000 documents)
- Chapter-wise split PDFs (some Economic Surveys)
- Excel files (numerical data from select Economic Surveys)

### Query Types Supported
- Factual queries (e.g., "Who presented the budget in 1991?")
- Analytical queries (e.g., "What has the government done for education in the last 10 years?")
- Comparative queries (e.g., "Compare defense spending 2014 vs 2024")
- Scheme lifecycle queries (e.g., "When was MGNREGA launched and how has its allocation changed?")

### Core Features
- Natural language question-answering with source citations
- Every answer linked to specific document, year, and page/section
- Trend charts and visualizations for spending/allocation comparisons
- Confidence scoring and "insufficient data" fallback when relevant information is not found
- Streamlit-based web interface
- English language support

### Analytics & NLP Layer
- Sentiment analysis of budget speeches across decades
- Topic modeling to identify dominant themes per era
- Sector-wise spending trend analysis
- Budget allocation vs actual expenditure comparison (Budget speech vs Economic Survey)

---

## 5. Scope — What's OUT (Future Phases)

- State-level budgets
- Multi-country expansion (US, UK budgets)
- Hindi / multilingual Q&A
- Real-time parliament session tracking
- Mobile application
- User authentication / accounts
- Fine-tuning or training a custom LLM (to be revisited post-MVP based on performance evaluation)
- Predictive modeling (forecasting next year's sector allocations)
- NER-based auto-extraction of scheme names and amounts

---

## 6. Research & Prior Work

Before beginning development, existing work in this space was reviewed to identify gaps and ensure this project adds distinct value.

| Existing Work | What They Did | Limitations | How This Project Differs |
|---|---|---|---|
| Aniket Kalushe (LinkedIn, 2025) | RAG chatbot on Indian budget speeches | Appears to be a basic RAG implementation on limited documents; equivalent to uploading a PDF to an LLM with prompts | Comprehensive 75+ year coverage; dual-source cross-referencing (Budget + Economic Survey); citation system; analytics layer |
| Makwana K. (2024) - Research Paper, Indian Journal of Science & Technology | Textual analysis using NLP, TF-IDF, topic modeling on Union Budget | Analyzed only two budget speeches; limited scope produces biased/incomplete findings | Full historical coverage; interactive query system, not a static paper |
| Open Budgets India (cbgaindia, GitHub) | Scripts to parse budget documents into machine-readable formats | Data parsing and visualization only; no AI query layer; no natural language interface | AI-powered natural language interface; semantic search; cited answers |
| Aryan Shenoy (GitHub) | Fund allocation visualization 2022–2025 using Tkinter/Matplotlib | Only 3 years of data; basic bar charts; no AI component; no search capability | 75+ years; AI-powered Q&A; auto-generated comparative visualizations |

### What Makes This Project Distinct
1. **Comprehensive historical coverage** — 1947 to present, not limited to recent years
2. **Dual-source cross-referencing** — Budget speeches paired with Economic Surveys to verify what was promised vs what was delivered
3. **Scheme lifecycle tracking** — Tracks when schemes were launched, modified, expanded, or discontinued, with citations
4. **Citation-first design** — Every answer links to exact source document, year, and page
5. **Analytics layer** — Sentiment analysis, topic modeling, and trend visualization built on top of the query system
6. **Built for diverse users** — Designed for citizens, students, researchers, investors, and policy professionals

---

## 7. Technical Architecture

### 7.1 Data Sources

| Source | URL | Content |
|---|---|---|
| Union Budget - Budget Speeches | indiabudget.gov.in | Budget speeches 1947–2026 |
| Ministry of Finance / Economic Survey | indiabudget.gov.in + MoF archives | Economic Surveys 1957–58 onward |

*Note: Exact year-wise breakdown of document formats (scanned vs clean PDF vs Excel) to be documented during Phase 1 data collection.*

### 7.2 Data Pipeline (One-time processing)

```
Data Sources (indiabudget.gov.in + MoF archives)
        │
        ▼
    Download All Documents ──→ Store Raw Files in AWS S3
        │
        ├── Clean PDFs ──→ PyPDF2 / pdfplumber ──→ Raw Text
        │
        ├── Scanned PDFs ──→ Image Preprocessing (Pillow/OpenCV)
        │                         ──→ Tesseract OCR ──→ Raw Text
        │
        └── Excel Files ──→ pandas / openpyxl ──→ Structured Data
                                │
                                ▼
                Text Cleaning, Chunking & Metadata Tagging
                    (year, document type, section, page)
                                │
                        ┌───────┴───────┐
                        ▼               ▼
                   ChromaDB        SQLite / PostgreSQL
              (Vector Embeddings    (Structured Data:
              for Semantic Search)   FM names, amounts,
                                     scheme metadata,
                                     Excel numerical data)
```

### 7.3 Query Pipeline (Per user query)

```
User Question (Streamlit UI)
        │
        ▼
  Query Classification (factual vs analytical vs comparative)
        │
        ▼
  Metadata Filtering (extract year range, sector, document type)
        │
        ▼
  ┌─────┴─────┐
  ▼           ▼
ChromaDB    SQLite/PostgreSQL
(Semantic    (Exact Lookups)
 Search)          │
  │               │
  ▼               ▼
  Merge Retrieved Context
        │
        ▼
  LLM (Claude API / GPT API) with System Prompt
  "Answer ONLY from provided context. Cite sources."
        │
        ▼
  Generate Response + Citations + Charts (if applicable)
        │
        ▼
  Streamlit UI (Answer + Sources + Visualizations)
```

### 7.4 Tool Stack

| Component | Tool | Rationale |
|---|---|---|
| Cloud Storage | AWS S3 (Free Tier - 5GB/12 months) | Industry standard; demonstrates cloud infrastructure skills |
| Development Environment | Local machine (i9 processor) → Google Colab / AWS EC2 if needed | Start local; scale compute as required |
| OCR (scanned PDFs) | Tesseract (pytesseract) with OpenCV preprocessing | Free, open-source, supports Hindi script |
| Text Extraction (clean PDFs) | PyPDF2 / pdfplumber | Lightweight, reliable for text PDFs |
| Excel Processing | pandas / openpyxl | Standard tools for structured data |
| Text Preprocessing | Python (regex, NLTK) | Standard NLP preprocessing |
| Embeddings | sentence-transformers (all-MiniLM-L6-v2) | Free, runs on CPU, strong performance for retrieval |
| Vector Database | ChromaDB | Free, lightweight, easy integration |
| Structured Database | SQLite (development) → PostgreSQL / Supabase (production) | Factual lookups, metadata queries, numerical data |
| LLM - Development | Ollama + Llama 3 (8B) | Free, local, no API costs during development |
| LLM - Production | Claude Sonnet API + GPT-4o-mini API | High quality; existing subscriptions available |
| NLP / Analytics | scikit-learn, NLTK, Gensim | Topic modeling (LDA), sentiment analysis |
| Visualization | Plotly, Matplotlib | Interactive charts for Streamlit |
| Frontend | Streamlit | Rapid development, free hosting |
| Hosting | Streamlit Community Cloud | Free public URL for demonstration |
| Version Control | GitHub (private repository during development) | Commit history documents development timeline |
| Project Management | GitHub Projects (Kanban board) | Task tracking; demonstrates project management discipline |

*Note: Tool selections may evolve during development based on performance evaluation and project needs. Changes will be documented in the CHANGELOG.*

---

## 8. Budget Estimate

| Item | Estimated Cost |
|---|---|
| AWS S3 (Free Tier) | $0 |
| Google Colab (Free Tier) | $0 |
| Tesseract OCR | $0 |
| ChromaDB | $0 |
| Sentence-transformers | $0 |
| Ollama + Llama 3 | $0 |
| Claude API (production testing) | $5–10 |
| GPT API (production testing) | $5–10 |
| Streamlit Community Cloud | $0 |
| **Total Estimated Cost** | **$10–20** |

---

## 9. Timeline

| Phase | Duration | Estimated Hours | Deliverable |
|---|---|---|---|
| Phase 1: Data Collection & Cataloging | Week 1–2 | ~20 hrs | All documents downloaded; format catalog (scanned/clean/Excel per year); metadata spreadsheet; raw files in S3 |
| Phase 2: Text Extraction & Cleaning | Week 3–4 | ~25 hrs | All text extracted (OCR + PDF + Excel); cleaned and stored as structured JSON with metadata |
| Phase 3: Database Setup & Indexing | Week 5 | ~15 hrs | ChromaDB loaded with embeddings; SQLite populated with structured data; basic search verified |
| Phase 4: RAG Pipeline & LLM Integration | Week 6–7 | ~20 hrs | Working query pipeline; citation system; hallucination safeguards; tested across query types |
| Phase 5: Analytics Layer | Week 8 | ~10 hrs | Sentiment analysis; topic modeling; trend visualizations |
| Phase 6: Frontend Development | Week 9 | ~10 hrs | Streamlit app with chat interface, charts, citations, example queries |
| Phase 7: Testing, Deployment & Documentation | Week 10 | ~5 hrs | Live on Streamlit Cloud; README complete; demo recording |
| **Total** | **10 weeks** | **~105 hrs** | **Working MVP** |

---

## 10. Risks & Mitigation

| Risk | Probability | Impact | Mitigation Strategy |
|---|---|---|---|
| Poor OCR quality on pre-1980 scanned documents | High | Medium | Implement image preprocessing (contrast, deskew) before OCR; prioritize post-2000 documents for initial MVP; document quality scores per year |
| LLM generates unsupported claims (hallucination) | Medium | High | RAG architecture restricts answers to retrieved context; system prompt enforces citation requirement; "insufficient data" fallback when retrieval confidence is low |
| Scope creep delays MVP delivery | Medium | High | Strict adherence to scope document; features outside Section 4 are deferred to future phases; weekly progress review |
| API costs exceed budget | Low | Low | Use Ollama locally for development; API calls reserved for production testing only |
| Missing documents (some years unavailable online) | Medium | Low | Document gaps transparently; check National Archives and alternative sources; acknowledge coverage limitations in documentation |
| Tool/library compatibility issues | Medium | Medium | Maintain flexible tool stack; evaluate alternatives during each phase; document changes in CHANGELOG |

---

## 11. Skills Demonstrated

| Skill Area | How This Project Demonstrates It |
|---|---|
| Data Engineering | Web scraping, OCR pipeline, ETL processing, cloud storage (AWS S3), data cleaning and structuring |
| Data Analysis | Sector-wise spending trend analysis, budget vs actual expenditure comparison, interactive dashboards |
| Data Science / NLP | Text embeddings, semantic search, topic modeling (LDA), sentiment analysis, entity extraction |
| AI Engineering | RAG architecture design, multi-LLM API integration (Claude + GPT), prompt engineering, hallucination mitigation |
| Cloud & Infrastructure | AWS S3, deployment pipeline, Streamlit hosting |
| Software Engineering | End-to-end system design, modular architecture, version control, documentation |
| Project Management | Scope document, GitHub Projects kanban, CHANGELOG, structured timeline |

---

## 12. Success Criteria

- [ ] User can submit a natural language question and receive a sourced answer within 15 seconds
- [ ] Every answer includes citations with document name, year, and page/section reference
- [ ] System returns "insufficient data" response when no relevant information is found in the corpus
- [ ] Minimum 50 years of budget data queryable
- [ ] Comparison charts auto-generate for spending/trend queries
- [ ] Sentiment analysis and topic modeling results available for budget speeches
- [ ] Application deployed with a public URL
- [ ] Complete documentation: README, architecture diagram, CHANGELOG, and setup instructions

---

## 13. Intellectual Property & Attribution

- **Original work by:** Prasad — MS Applied Data Science, Syracuse University (iSchool)
- **All source data:** Publicly available government documents from indiabudget.gov.in and Ministry of Finance archives
- **Development timeline:** Documented via GitHub commit history (repository created March 2026)
- **Concept origin:** Initially explored as a deep learning project in Fall 2025; pivoted to RAG-based architecture in Spring 2026 after evaluating feasibility, cost, and effectiveness
- **AI Development Advisor:** Claude (Anthropic) — used for architecture consultation, code review, and research assistance. All implementation decisions and code authored by Prasad.
- **License:** To be determined at public release (MIT / Apache 2.0 recommended for portfolio projects)

**Declaration:** This project is original work. The concept, architecture, implementation, and all code are authored by the project owner. Prior work in this space was reviewed (see Section 6) and this project is differentiated by scope, methodology, and features as documented.

---

## 14. Future Expansion (Post-MVP)

*To be discussed and prioritized after MVP completion.*

- Hindi / multilingual language support for queries and answers
- Multi-country expansion (US Congressional Budget, UK Budget)
- Fine-tuning a domain-specific model on the budget corpus
- Scheme lifecycle auto-tracker (detect launch, modification, discontinuation)
- Predictive analysis (forecast likely focus areas for next budget)
- NER-based auto-extraction of scheme names, monetary amounts, and sectors
- Mobile-responsive interface
- State-level budget integration

---

## 15. Project Documentation Standards

The following documents will be maintained throughout the project:

| Document | Location | Purpose |
|---|---|---|
| Project Scope (this document) | `/docs/PROJECT_SCOPE.md` | Defines boundaries, objectives, and architecture |
| CHANGELOG | `/CHANGELOG.md` | Records all decisions, changes, and session notes after every working session |
| README | `/README.md` | Project overview, setup instructions, usage guide |
| Data Catalog | `/docs/DATA_CATALOG.md` | Year-wise breakdown of available documents, formats, and quality notes |
| Architecture Diagram | `/docs/ARCHITECTURE.md` | Visual and written system architecture |

All documentation maintained in the GitHub repository with version history.

---

*This is a living document. Updates will be tracked in the CHANGELOG with version increments.*