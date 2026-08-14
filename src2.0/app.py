try:
    __import__("pysqlite3")
    import sys
    sys.modules["sqlite3"] = sys.modules.pop("pysqlite3")
except ImportError:
    pass  # not installed locally, fine, only needed on Streamlit Cloud

import os
import re
import configparser
import streamlit as st
import chromadb
from openai import OpenAI
from rank_bm25 import BM25Okapi

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

COLLECTION_NAME = "budget_speeches_para750"
CHROMA_PATH = os.path.join(BASE_DIR, "data", "chroma_db")
EMBED_MODEL = "text-embedding-3-small"
CHAT_MODEL = "gpt-4o-mini"
TOP_K = 5
CANDIDATE_POOL = 20
RRF_K = 60

STOPWORDS = {
    "a", "an", "the", "is", "are", "was", "were", "be", "been", "being",
    "what", "which", "who", "whom", "how", "why", "when", "where",
    "did", "do", "does", "doing", "and", "or", "but", "if", "in", "on",
    "at", "to", "of", "for", "with", "about", "from", "by", "as", "into",
    "say", "said", "new", "earlier",
}

SMALLTALK = {
    "hi", "hii", "hello", "hey", "yo",
    "good morning", "good afternoon", "good evening",
    "thanks", "thank you", "bye", "goodbye", "ok", "okay"
}


@st.cache_resource
def get_clients():
    try:
        api_key = st.secrets["openai"]["api_key"]
    except (FileNotFoundError, KeyError, st.errors.StreamlitSecretNotFoundError):
        config = configparser.ConfigParser()
        config.read(os.path.join(BASE_DIR, "..", "docs", "config.ini"))
        api_key = config["openai"]["api_key"]
    openai_client = OpenAI(api_key=api_key)
    chroma_client = chromadb.PersistentClient(path=CHROMA_PATH)
    collection = chroma_client.get_collection(name=COLLECTION_NAME)
    return openai_client, collection


openai_client, collection = get_clients()

if "messages" not in st.session_state:
    st.session_state.messages = []
if "answer_cache" not in st.session_state:
    st.session_state.answer_cache = {}


def is_smalltalk(question):
    return question.strip().lower().rstrip("!?.") in SMALLTALK


def tokenize(text):
    tokens = re.findall(r"\b\w+\b", text.lower())
    return [t for t in tokens if t not in STOPWORDS]


def extract_years(question):
    """Find years mentioned in the question, as fiscal-year start years (int)."""
    years = set()
    for match in re.finditer(r"\b(19\d{2}|20\d{2})-(\d{2})\b", question):
        years.add(int(match.group(1)))
    for match in re.finditer(r"\b(19\d{2}|20\d{2})(?:-(\d{4}))?\b", question):
        years.add(int(match.group(1)))
    return sorted(years)


def year_to_metadata_candidates(year):
    """Generate the metadata year strings this fiscal year could be stored as."""
    next_two = str(year + 1)[-2:]
    return [f"{year}{next_two}", f"{year}_{next_two}"]


def dense_query(question, where=None, n_results=TOP_K):
    vector = openai_client.embeddings.create(input=[question], model=EMBED_MODEL).data[0].embedding
    kwargs = {"query_embeddings": [vector], "n_results": n_results}
    if where:
        kwargs["where"] = where
    results = collection.query(**kwargs)
    return results["documents"][0], results["metadatas"][0]


def retrieve_chunks_for_years(question, years):
    """One filtered retrieval per detected year, merged (query decomposition for comparisons)."""
    all_docs, all_metas = [], []
    for year in years:
        candidates = year_to_metadata_candidates(year)
        where = {"year": {"$in": candidates}}
        docs, metas = dense_query(question, where=where)
        all_docs.extend(docs)
        all_metas.extend(metas)
    return all_docs, all_metas


def rewrite_with_history(question, history):
    """Resolve a follow-up question into a standalone one using recent chat history."""
    if not history:
        return question

    recent = history[-6:]  # last few turns, enough context without bloating the prompt
    history_text = "\n".join(f"{m['role']}: {m['content']}" for m in recent)
    prompt = f"""Given this recent conversation and a new question, decide if the new question is a follow-up that depends on the conversation (uses words like "it," "that," "what about," "and," or omits a topic/year mentioned earlier) or if it is a complete, standalone question on its own topic.

If it is a follow-up, rewrite it as a standalone question that includes the necessary context (topic, year, etc.) from the conversation.

If it is already standalone, or introduces a new topic unrelated to the conversation, return it EXACTLY as written, unchanged. Do not add context from the conversation to a question that does not need it.

Output only the resulting question, nothing else.

Conversation:
{history_text}

New question: {question}

Resulting question:"""
    response = openai_client.chat.completions.create(
        model=CHAT_MODEL,
        temperature=0,
        messages=[{"role": "user", "content": prompt}]
    )
    return response.choices[0].message.content.strip()


def hybrid_fallback(question):
    """Full-corpus hybrid (dense + BM25 fused) search, used when no year could be determined."""
    corpus = collection.get(include=["documents", "metadatas"])
    ids, docs, metas = corpus["ids"], corpus["documents"], corpus["metadatas"]

    vector = openai_client.embeddings.create(input=[question], model=EMBED_MODEL).data[0].embedding
    dense_results = collection.query(query_embeddings=[vector], n_results=min(CANDIDATE_POOL, len(ids)))
    dense_ids = dense_results["ids"][0]
    best_distance = dense_results["distances"][0][0] if dense_results["distances"][0] else 1.0

    tokenized_corpus = [tokenize(doc) for doc in docs]
    bm25 = BM25Okapi(tokenized_corpus)
    scores = bm25.get_scores(tokenize(question))
    top_indices = sorted(range(len(scores)), key=lambda i: scores[i], reverse=True)[:min(CANDIDATE_POOL, len(ids))]
    bm25_ids = [ids[i] for i in top_indices]

    fused = {}
    for rank, cid in enumerate(dense_ids):
        fused[cid] = fused.get(cid, 0) + 1 / (RRF_K + rank + 1)
    for rank, cid in enumerate(bm25_ids):
        fused[cid] = fused.get(cid, 0) + 1 / (RRF_K + rank + 1)
    top_ids = [cid for cid, _ in sorted(fused.items(), key=lambda x: x[1], reverse=True)[:TOP_K]]

    id_to_doc = dict(zip(ids, docs))
    id_to_meta = dict(zip(ids, metas))
    return [id_to_doc[i] for i in top_ids], [id_to_meta[i] for i in top_ids], best_distance


def format_sources(metadatas):
    lines = []
    for m in metadatas:
        year = m.get("year", "unknown").replace("_", "-")
        pages = f"p.{m.get('page_start', '?')}"
        if m.get("page_end") != m.get("page_start"):
            pages += f"-{m.get('page_end', '?')}"
        lines.append(f"- Budget Speech {year}, {pages}")
    return "\n".join(dict.fromkeys(lines))  # de-duplicate, keep order


def generate_answer(question, chunks):
    context = "\n\n---\n\n".join(chunks)
    prompt = f"""Answer the question using ONLY the context below. You may combine and summarize information across multiple pieces of context to answer general or descriptive questions. When multiple relevant facts are present in the context, include all of them, not just the most prominent one. Only say "insufficient data" if none of the context is relevant to the question, not if the context only partially covers it.

Do not describe something as a "trend," "steady increase," or similar unless the context contains figures from at least three different years supporting that claim. If the context only has data for one or two years, state the specific figures for those years only and say the available data does not cover a full trend.

Context:
{context}

Question: {question}"""
    response = openai_client.chat.completions.create(
        model=CHAT_MODEL,
        temperature=0,
        messages=[{"role": "user", "content": prompt}]
    )
    return response.choices[0].message.content


st.title("India Budget Intelligence: Union Budget Speeches, 1947-2025")
st.caption("Covers Union Budget speeches from 1947-48 to 2025-26.")
st.caption(
    "Try: \"What did the 2016-17 budget say about roads?\" · "
    "\"Compare education spending in 2013 and 2014\" · "
    "\"What is the fiscal deficit in BE 2026-27?\""
)

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.write(msg["content"])
        if msg.get("sources"):
            with st.expander("Sources"):
                st.markdown(msg["sources"])

question = st.chat_input("Ask about any Union Budget speech, 1947-2025")

if question:
    st.session_state.messages.append({"role": "user", "content": question})
    with st.chat_message("user"):
        st.write(question)

    if is_smalltalk(question):
        answer = (
            "Hi! I can answer questions about Union Budget speeches from "
            "1947-48 to 2025-26. Ask about a specific year, finance minister, "
            "tax proposal, or fiscal figure."
        )
        sources = ""

    elif question in st.session_state.answer_cache:
        answer, sources = st.session_state.answer_cache[question]

    else:
        history = st.session_state.messages[:-1]  # everything before this new user turn
        resolved_question = rewrite_with_history(question, history)
        years = extract_years(resolved_question)
        if years:
            docs, metas = retrieve_chunks_for_years(resolved_question, years)
            answer = generate_answer(resolved_question, docs)
        else:
            docs, metas, best_distance = hybrid_fallback(resolved_question)
            answer = generate_answer(resolved_question, docs)
            if best_distance > 0.9:
                answer += ("\n\n*This looks like a broad question and I only found loosely "
                           "related content. Try asking about a specific topic (e.g. roads, "
                           "education, tax) or year for a more reliable answer.*")
            else:
                answer += ("\n\n*I didn't find a specific year in your question, so I searched "
                           "broadly across all budgets. For a more precise answer, try naming "
                           "a year, e.g. '2016-17'.*")
        if resolved_question != question:
            answer += f"\n\n*(interpreted as: \"{resolved_question}\")*"
        sources = format_sources(metas)
        st.session_state.answer_cache[question] = (answer, sources)

    st.session_state.messages.append({"role": "assistant", "content": answer, "sources": sources})
    with st.chat_message("assistant"):
        st.write(answer)
        if sources:
            with st.expander("Sources"):
                st.markdown(sources)