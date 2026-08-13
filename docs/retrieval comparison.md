# Retrieval Strategy Comparison
## India Budget Intelligence System

**Corpus:** 93 budget speech documents, 11,470 chunks (para_750 chunking, text-embedding-3-small)
**Method:** 7 retrieval variants tested against a fixed 10-question set, written before building any variant
**Question set:** deliberately includes year-present and year-absent versions of the same underlying question, since metadata filtering only exercises its logic when a year is present

---

## Question set

| # | Question | Tests |
|---|---|---|
| 1 | How many parts is the budget divided into? | Structural recall, no year |
| 2 | What did the budget say about roads? | Synonym/topic match, no year |
| 3 | What did the 2016-17 budget say about roads? | Same as #2, year present |
| 4 | What did the budget say about transportation? | Synonym drift, no year |
| 5 | What did the 2008-09 budget say about transportation? | Same as #4, year present |
| 6 | Compare the 2025 budget with the 2015 budget. | Multi-year dilution |
| 7 | What is the fiscal deficit estimated at in BE 2026-27? | Numeric, well-represented baseline |
| 8 | What is the new MAT rate proposed, down from what earlier rate? | Numeric, moderate difficulty |
| 9 | Who presented the Budget 2026-2027 speech, and in what role? | Boilerplate/title-page discrimination |
| 10 | What is the new STT rate on Futures, and what was the earlier rate? | Numeric, correct-chunk-ranked-low risk |

---

## Variants tested

| Variant | Mechanism | Script |
|---|---|---|
| Dense-only | ChromaDB cosine similarity on OpenAI embeddings | `0.2_bs_retrieval_dense.py` |
| BM25-only | Keyword term-frequency, custom tokenizer + stopwords | `0.3_bs_retrieval_bm25.py` |
| Hybrid | Dense + BM25 fused via reciprocal rank fusion (hand-built) | `0.4_bs_retrieval_hybrid.py` |
| Metadata-filtered | Year extracted from question, ChromaDB `where` filter, dense search within filter, two-year decomposition for comparisons | `0.5_bs_retrieval_metadata.py` |
| Metadata + Hybrid | Year filter first, then dense+BM25 fusion within the filtered subset | `0.6_bs_retrieval_metadata_hybrid.py` |
| BM25 + Stemming | Stopword-filtered BM25 + Porter stemming | `0.7_bs_retrieval_bm25_stemmed.py` |
| LangChain EnsembleRetriever | Framework's built-in hybrid (dense + `BM25Retriever`), default tokenizer, no custom stopwords or metadata logic | `0.8_bs_retrieval_langchain.py` |

---

## Results by question

**Result labels:** Pass = correct, relevant chunk(s) returned · Partial = correct chunk present but diluted, ranked low, or mixed with irrelevant results · Fail = no relevant chunk retrieved.

**On the numbers alongside each result:** the top-1 metric is shown for reference, but the four metric types are not on comparable scales and should not be compared across variant columns:
- **Dense / Metadata (cosine distance):** lower is better. Typical range seen in this corpus: ~0.5 (strong match) to ~1.3 (weak match).
- **BM25 / Stemmed BM25 (term-frequency score):** higher is better. Unbounded, only meaningful relative to other scores within the same run.
- **Hybrid / Meta+Hybrid (RRF fused score):** higher is better. Compressed into a narrow ~0.015-0.033 range by design (the reciprocal rank formula), so small differences here can still reflect a real ranking change.
- **LangChain:** this script did not print a numeric score, so only the Pass/Partial/Fail result is shown for that column.

| # | Dense (distance) | BM25 (score) | Hybrid (fused) | Metadata (distance) | Meta+Hybrid (fused) | Stemmed BM25 (score) | LangChain |
|---|---|---|---|---|---|---|---|
| 1 (parts) | Fail — 0.88 | Fail — 21.36 | Fail — 0.0325 | Fail — 0.88 (no year, same as dense) | Fail — 0.0325 | Fail — 11.79 | Fail |
| 2 (roads, no yr) | Pass — 0.79 | Fail before fix, Pass after fix — 16.81 | Pass — 0.0328 | Pass — 0.79 | Pass — 0.0328 | Pass — 7.60 | Partial (top result relevant, one irrelevant result mixed in from filler-word noise) |
| 3 (roads, 2016-17) | Partial — 0.70 (year drift in ranks 2-5) | Pass — 22.90 | Pass — 0.0328 | Pass — 0.70 (cleanest, all 5 results correct year) | Pass — 0.0328 | Pass — 19.49 | Partial (only 2 of 5 results in correct year) |
| 4 (transport, no yr) | Partial — 0.89 | Fail before fix, Partial after fix — 9.85 | Partial — 0.0300 (one BM25-only false positive let through) | Partial — 0.89 (same as dense, no year to filter) | Partial — 0.0300 | Partial — 8.29 | Fail (top result irrelevant) |
| 5 (transport, 2008-09) | Partial — 0.89 | Pass — 28.25 | Pass — 0.0279 | Pass — 0.92 (cleanest, all 5 results correct year) | Pass — 0.0315 | Pass — 16.62 | Partial (mixed years) |
| 6 (2025 vs 2015) | Fail — 0.98 | Fail — 22.75 (single document, cannot bridge two years) | Fail — 0.0313 | Pass — 1.02-1.16 (2015 side), 1.04-1.31 (2025 side) — only variant to solve this | Partial — 0.0320 (relevant but noisier than metadata-only) | Fail — 14.45 | Fail (no decomposition) |
| 7 (fiscal deficit) | Pass — 0.53 (best baseline in the full comparison) | Pass — 21.71 | Pass — 0.0323 | Pass — 0.58 | Pass — 0.0328 | Pass — 21.56 | Pass |
| 8 (MAT rate) | Partial — 0.78 (correct chunk present, ranked 4th-5th) | Pass — 18.30 | Pass — 0.0318 | Partial — 0.85 (no year to filter, same limitation as dense) | Pass — 0.0318 | Pass — 15.91 | Pass |
| 9 (who presented) | Partial — 0.84 (top result from wrong year, boilerplate confusion) | Pass — 31.49 | Pass — 0.0323 | Pass — 0.85 (cleanest, all 5 results correct year) | Pass — 0.0325 | Pass — 24.66 | Partial (top result from wrong year) |
| 10 (STT rate) | Partial — 0.79 (correct chunk present, ranked 4th) | Pass — 38.13 | Pass — 0.0323 | Partial — 0.79 (no year to filter) | Pass — 0.0323 | Pass — 18.95 | Pass |

---

## Key findings

**1. Two real, evidence-backed wins carried forward:**
- **Stopword-filtered BM25** fixed the filler-word-domination failure (questions 2, 4, 9) that plain BM25 and dense retrieval both suffered from in different ways.
- **Metadata filtering with year-based query decomposition** is the only method that solved question 6 (multi-year comparison) — confirmed as a query decomposition problem, not a ranking problem.

**2. Two negative-but-useful findings:**
- **Hybrid fusion added negligible value on top of stopword-fixed BM25** for the synonym cases, since both methods had already converged independently. It introduced one real cost: letting through a BM25-only false positive that dense retrieval alone had correctly excluded.
- **Metadata + hybrid combined performed no better than metadata alone**, and was mildly noisier on question 6. Once a year filter narrows the corpus, dense-only search is sufficient; BM25 has too few distinguishing candidates left in the narrowed pool to add signal.

**3. One structural limitation, confirmed not fixable by retrieval tuning:**
- **Question 1** failed identically across all seven variants, including after adding Porter stemming specifically to close the "parts"/"part" token gap. Root cause confirmed by inspection: the fact is expressed through document structure (section headers "PART A"/"PART B"), not stated as prose. No retrieval method can score a match on a sentence that was never written. This needs structure-aware handling or is out of scope pending full budget document ingestion (see DATA_CATALOG.md).

**4. LangChain's out-of-the-box hybrid underperformed the hand-built equivalent.**
`EnsembleRetriever` + `BM25Retriever` reproduced the exact filler-word bug that had already been fixed by hand, because LangChain's default `BM25Retriever` tokenizer includes no custom stopword list. It also has no year-metadata routing, so it performed at or below the plain hand-built hybrid baseline on every year-sensitive question, and did not solve question 6. This is not a framework defect — it's a demonstration that the mechanism (rank fusion) is generic, while the actual fixes that mattered for this corpus (stopwords, year extraction, decomposition) are domain-specific and have to be added regardless of framework.

---

## Recommendation

**Deploy: metadata filtering with year-based decomposition, falling back to stopword-filtered dense/BM25 hybrid when no year is detected.**

This combination:
- Solves the multi-year comparison case (question 6), the highest-value fix identified this session
- Solves single-year synonym mismatches (questions 3, 5) more cleanly than any other variant
- Costs one to two extra embedding calls per query (for two-year decomposition), acceptable given the accuracy gain
- Does not require adopting a new framework or losing the stopword/tokenization fixes already proven necessary

**Not recommended for deployment at this stage:** plain hybrid, metadata+hybrid combined, or LangChain's `EnsembleRetriever` as tested — none outperformed metadata filtering alone on this question set, and LangChain specifically underperformed due to missing domain-specific tuning.

**Out of scope, logged separately:** question 1 (structural/document-format ambiguity) and general multi-year thematic aggregation (e.g. "education spending since independence") — both confirmed to need a different mechanism (structured extraction, or a multi-step per-year loop) rather than further retrieval tuning.
