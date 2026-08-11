import configparser
import streamlit as st
import chromadb
from openai import OpenAI

COLLECTION_NAME = "budget_speeches_para750"
CHROMA_PATH = "data/chroma_db"
EMBED_MODEL = "text-embedding-3-small"
CHAT_MODEL = "gpt-4o-mini"
TOP_K = 5

@st.cache_resource
def get_clients():
    if "openai" in st.secrets:
        api_key = st.secrets["openai"]["api_key"]
    else:
        config = configparser.ConfigParser()
        config.read("../docs/config.ini")
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

def retrieve_chunks(question):
    response = openai_client.embeddings.create(input=[question], model=EMBED_MODEL)
    query_vector = response.data[0].embedding
    results = collection.query(query_embeddings=[query_vector], n_results=TOP_K)
    return results["documents"][0], results["metadatas"][0]

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

st.title("India Budget Intelligence")
st.caption("Covers Union Budget speeches from 1947-48 to 2025-26.")

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.write(msg["content"])
        if msg.get("sources"):
            with st.expander("Sources"):
                st.markdown(msg["sources"])

question = st.chat_input("Ask about any Union Budget speech, 1947–2025")

if question:
    st.session_state.messages.append({"role": "user", "content": question})
    with st.chat_message("user"):
        st.write(question)

    if question in st.session_state.answer_cache:
        answer, sources = st.session_state.answer_cache[question]
    else:
        chunks, metadatas = retrieve_chunks(question)
        answer = generate_answer(question, chunks)
        sources = format_sources(metadatas)
        st.session_state.answer_cache[question] = (answer, sources)

    st.session_state.messages.append({"role": "assistant", "content": answer, "sources": sources})
    with st.chat_message("assistant"):
        st.write(answer)
        with st.expander("Sources"):
            st.markdown(sources)