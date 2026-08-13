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

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

COLLECTION_NAME = "budget_speeches_para750"
CHROMA_PATH = os.path.join(BASE_DIR, "data", "chroma_db")
EMBED_MODEL = "text-embedding-3-small"
CHAT_MODEL = "gpt-4o-mini"
TOP_K = 5

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
if "pending_question" not in st.session_state:
    st.session_state.pending_question = None


def is_smalltalk(question):
    return question.strip().lower().rstrip("!?.") in SMALLTALK


def extract_years(question):
    """Find years mentioned in the question, as fiscal-year start years (int)."""
    years = set()
    for match in re.finditer(r"\b(20\d{2})-(\d{2})\b", question):
        years.add(int(match.group(1)))
    for match in re.finditer(r"\b(20\d{2})(?:-(\d{4}))?\b", question):
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
    prompt = f"""Answer the question using ONLY the context below. If the answer is not in the context, say "insufficient data."

Context:
{context}

Question: {question}"""
    response = openai_client.chat.completions.create(
        model=CHAT_MODEL,
        temperature=0,
        messages=[{"role": "user", "content": prompt}]
    )
    return response.choices[0].message.content


CLARIFY_MESSAGE = "Which year or budget are you asking about? For example: '2016-17'."
CLARIFY_RETRY_MESSAGE = "I didn't catch a year there. Could you give one, e.g. '2016-17'?"

st.title("India Budget Intelligence: Union Budget Speeches, 1947-2025")
st.caption("Covers Union Budget speeches from 1947-48 to 2025-26.")

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

    if st.session_state.pending_question:
        original_question = st.session_state.pending_question
        years = extract_years(question)
        if years:
            docs, metas = retrieve_chunks_for_years(original_question, years)
            answer = generate_answer(original_question, docs)
            sources = format_sources(metas)
            st.session_state.pending_question = None
        else:
            answer = CLARIFY_RETRY_MESSAGE
            sources = ""

    elif is_smalltalk(question):
        answer = (
            "Hi! I can answer questions about Union Budget speeches from "
            "1947-48 to 2025-26. Ask about a specific year, finance minister, "
            "tax proposal, or fiscal figure."
        )
        sources = ""

    elif question in st.session_state.answer_cache:
        answer, sources = st.session_state.answer_cache[question]

    else:
        years = extract_years(question)
        if years:
            docs, metas = retrieve_chunks_for_years(question, years)
            answer = generate_answer(question, docs)
            sources = format_sources(metas)
            st.session_state.answer_cache[question] = (answer, sources)
        else:
            answer = CLARIFY_MESSAGE
            sources = ""
            st.session_state.pending_question = question

    st.session_state.messages.append({"role": "assistant", "content": answer, "sources": sources})
    with st.chat_message("assistant"):
        st.write(answer)
        if sources:
            with st.expander("Sources"):
                st.markdown(sources)