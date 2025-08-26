import json
from pathlib import Path
import re
import os
import time
from typing import List, Dict, Optional

import streamlit as st

# Vector DB / embeddings
from langchain_chroma import Chroma
from langchain_huggingface import HuggingFaceEmbeddings
from langchain.schema import Document
from chromadb import PersistentClient

# Ollama chat client (HTTP)
from ollama import chat as ollama_chat

BASE_DIR = Path(__file__).parent.resolve()
GENKI_PATH = BASE_DIR / "Data" / "Genki1.json"    # adjust if needed
CHROMA_DIR = "./chroma_db"                  # db path
COLLECTION_NAME = "genki"                         # explicit collection name
EMBEDDING_MODEL = "intfloat/multilingual-e5-small"  # chose because of English and Japanese capabilities 
OLLAMA_MODEL = "qwen3:1.7b"                       # set to any model you want

# Optional: environment toggle to force a one-off reset without changing code
FORCE_RESET = False

# UI CONFIG
st.set_page_config(page_title="JLPT RAG Tutor (Genki)", page_icon="📘", layout="wide")



# -----------------------
# Helpers: lesson/sublesson extraction & filter 
# -----------------------
def extract_lesson_info(text: str):
    result = {"lesson": None, "sublesson": None}
    lesson_match = re.search(r"\blesson\s+(\d+)\b", text, re.IGNORECASE)
    if lesson_match:
        result["lesson"] = int(lesson_match.group(1))
    sublesson_match = re.search(r"\bsublesson\s+(\d+)\b", text, re.IGNORECASE)
    if sublesson_match:
        result["sublesson"] = int(sublesson_match.group(1))
    return result

def build_effective_filter(user_text: str) -> dict | None:
    # parse text for lesson+sublesson
    parsed = extract_lesson_info(user_text)  # return var in form {'lesson': int|None, 'sublesson': int|None}

    # check if lesson set in sidebar
    sl = st.session_state.get("sidebar_lesson")
    ssl = st.session_state.get("sidebar_sublesson")

    # if lesson in both, sidebar overrides
    eff_lesson = parsed["lesson"]
    eff_sublesson = parsed["sublesson"]

    if isinstance(sl, int):           # sidebar lesson explicitly set
        eff_lesson = sl
    if isinstance(ssl, int):          # sidebar sublesson set
        eff_sublesson = ssl

    # safety: only use sublesson if lesson is set
    if not eff_lesson:
        eff_sublesson = None

    # build filter
    if eff_lesson and eff_sublesson:
        return {"$and": [{"lesson": eff_lesson}, {"sublesson": eff_sublesson}]}
    elif eff_lesson:
        return {"lesson": eff_lesson}
    else:
        return None



# -----------------------
# Cached resources: embeddings, client, and one-time (re)ingest
# -----------------------
@st.cache_resource(show_spinner=False)
def get_embeddings():
    return HuggingFaceEmbeddings(model_name=EMBEDDING_MODEL)

@st.cache_resource(show_spinner=False)
def get_client():
    return PersistentClient(path=CHROMA_DIR)

@st.cache_resource(show_spinner=True)
def init_and_ingest_if_needed(force_reset: bool = False):
    """One-time per server process:
    - Optionally delete the collection (force_reset)
    - Check if collection has vectors; if empty, ingest from GENKI_PATH
    - Return nothing; we re-open vectordb on demand in retrieval
    """
    emb = get_embeddings()
    client = get_client()

    # Optional reset (drop only the collection)
    if force_reset:
        try:
            client.delete_collection(COLLECTION_NAME)
            print(f"🧹 Force reset: cleared collection '{COLLECTION_NAME}'.")
        except Exception as e:
            print(f"🧹 Force reset: collection '{COLLECTION_NAME}' not found (nothing to clear). Details: {e}")

    # Guarded ingest
    try:
        coll = client.get_collection(COLLECTION_NAME)
        existing_count = coll.count()
        print("collection exists")
    except Exception:
        existing_count = 0

    if existing_count == 0:
        with open(GENKI_PATH, "r", encoding="utf-8") as f:
            genki_chunks = json.load(f)

        # Convert JSON to LangChain Documents while preserving metadata (for filtering)
        docs: List[Document] = []
        for chunk in genki_chunks:
            docs.append(Document(
                page_content=chunk["text"],
                metadata={
                    "lesson": chunk["lesson"],
                    "sublesson": chunk["sublesson"],
                    "topic": chunk["topic"],
                    "chunk_id": chunk["chunk_id"],
                },
            ))

        # Store embeddings in ChromaDB
        _vectordb = Chroma.from_documents(
            documents=docs,
            embedding=emb,
            persist_directory=CHROMA_DIR,
            collection_name=COLLECTION_NAME,
        )
        print("✅ ChromaDB populated and saved.")
    else:
        print(f"✅ Found {existing_count} vectors in '{COLLECTION_NAME}'. Skipping ingestion.")



# -----------------------
# Retrieval helper (open an existing collection and search)
# -----------------------
def retrieve_chunks(query: str, k: int = 3):
    emb = get_embeddings()
    vectordb = Chroma(
        persist_directory=CHROMA_DIR,
        collection_name=COLLECTION_NAME,
        embedding_function=emb,
    )
    qfilter = build_effective_filter(query)
    return (vectordb.similarity_search(query, k=k, filter=qfilter)
            if qfilter else
            vectordb.similarity_search(query, k=k))



# -----------------------
# Chat with Ollama (stateful messages + streaming)
# -----------------------
def stream_chat_answer(messages: List[Dict[str, str]], model: str):
    """Yield tokens as they arrive from Ollama's chat stream (for the given model)."""
    stream = ollama_chat(model=model, messages=messages, stream=True)
    for chunk in stream:
        yield chunk["message"]["content"]

def build_sources(results):
    srcs = []
    for r in results:
        meta = r.metadata or {}
        snippet = (r.page_content or "").strip().replace("\n", " ")

        # cap at 500 characters
        if len(snippet) > 750:
            snippet = snippet[:750] + "..."

        srcs.append({
            "lesson": meta.get("lesson"),
            "sublesson": meta.get("sublesson"),
            "topic": meta.get("topic"),
            "snippet": snippet,
        })
    return srcs



# -----------------------
# Sidebar: controls
# -----------------------
with st.sidebar:
    st.subheader("Settings")
    st.caption("Model & DB controls")
    st.text_input("Ollama model", value=OLLAMA_MODEL, key="model_name", disabled=True)
    reset_clicked = st.button("🧹 Wipe & Rebuild Chroma Collection", type="secondary")

    st.markdown("---")
    st.subheader("Filters")
    lesson = st.selectbox("Lesson", ["Auto"] + list(range(1, 13)), index=0, key="sidebar_lesson")
    sublesson = st.selectbox("Sublesson", ["Auto"] + list(range(1, 9)), index=0, key="sidebar_sublesson")
    textbook = st.selectbox("Textbook", ["Genki 1", "Genki 2", "Tobira"], index=0, key="sidebar_textbook")
    st.caption("Textbook filter not implemented yet — UI only for now.")

# Handle FORCE_RESET once at server start
_ = init_and_ingest_if_needed(force_reset=FORCE_RESET)

# Handle manual reset via sidebar
if reset_clicked:
    # Clear caches and re-init
    st.cache_resource.clear()
    st.success("Collection reset requested. Re-initializing…")
    # Recreate and ingest
    _ = init_and_ingest_if_needed(force_reset=True)
    st.rerun()



# -----------------------
# Session state for chat
# -----------------------
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "system", "content": (
            "You are a helpful tutor assisting with Japanese grammar based on Genki textbook material. "
            "Be clear, structured, and educational. Use bullet points and short examples with kana/kanji + romaji."
        )}
    ]



# -----------------------
# Header
# -----------------------
st.markdown(
    """
    <style>
    /* rounder chat bubbles */
    .stChatMessage { border-radius: 12px; padding: 0.6em; }
    /* smaller sidebar text */
    section[data-testid="stSidebar"] { font-size: 0.9em; }
    </style>
    """,
    unsafe_allow_html=True,
)
st.title("📘 JLPT RAG Tutor (Genki)")
st.caption("RAG: Chroma (multilingual-e5) + Ollama (Qwen) | Multi-turn with streaming")

with st.expander("ℹ️ About this app"):
        st.markdown(
            """
            **RAG loop**: user question → Chroma (multilingual-e5) similarity search (k=3) → retrieved chunks →
            Ollama chat with **Qwen** → streamed response.

            **Notes**
            - If the Chroma collection is empty, the app ingests from your `Genki1.json` once.
            - Use the sidebar button to wipe & rebuild the collection.
            - To force a reset at startup: `FORCE_RESET=1 streamlit run streamlit_app.py`.
            - Ensure the **Ollama daemon** is running (`ollama serve`) and the model is available (`ollama pull qwen3:1.7b`).
            - **Textbook** selector in sidebar is UI‑only for now; we will wire it into metadata later.
            """
        )



# -----------------------
# Display conversation
# -----------------------
for msg in st.session_state.messages:
    if msg["role"] == "system":
        continue
    with st.chat_message("user" if msg["role"] == "user" else "assistant"):
        st.markdown(msg["content"]) 

         # 📚 Persistent Sources
        if "sources" in msg and msg["sources"]:
            with st.expander(f"📚 Sources ({len(msg['sources'])})", expanded=False):
                for i, s in enumerate(msg["sources"], 1):
                    # Nested expander for the full snippet (optional)
                    with st.expander(f"Source {i}: Lesson {s['lesson']} Sub {s['sublesson']} — {s['topic']}", expanded=False):
                        st.markdown(s["snippet"])



# -----------------------
# Chat input + retrieval + streaming
# -----------------------
user_input = st.chat_input("Ask a question about grammar, vocab, or a specific lesson… (e.g., 'lesson 3 sublesson 2 te-form')")

if user_input:
    # Retrieve context from vector DB
    with st.spinner("Searching Genki notes…"):
        results = retrieve_chunks(user_input, k=3)
        context = "\n\n".join([r.page_content for r in results])

    # Filter from sidebar if not defaults
    hint_parts = []
    sl = st.session_state.get("sidebar_lesson")
    ssl = st.session_state.get("sidebar_sublesson")
    if isinstance(sl, int):
        hint_parts.append(f"lesson {sl}")
    if isinstance(ssl, int):
        hint_parts.append(f"sublesson {ssl}")
    hint_txt = f" ({', '.join(hint_parts)})" if hint_parts else ""

    # Visible transcript: show user's message first
    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.markdown(user_input)

    # Working prompt for the model (include retrieved context)
    user_msg = f"Context:\n{context}\n\nQuestion{hint_txt}: {user_input}"
    working_msgs = list(st.session_state.messages)
    working_msgs.append({"role": "user", "content": user_msg})

    # Stream assistant answer
    with st.chat_message("assistant"):
        placeholder = st.empty()
        accum = ""
        try:
            for token in stream_chat_answer(working_msgs, OLLAMA_MODEL):
                accum += token
                placeholder.markdown(accum)
        except Exception as e:
            st.error(f"Ollama streaming error: {e}")

    # Commit assistant message to history
    if accum:
        st.session_state.messages.append({
            "role": "assistant",
            "content": accum,
            "sources": build_sources(results),  # attach sources here
        })

        with st.expander("📚 Sources"):
            for r in results:
                st.markdown(
                    f"- **Lesson {r.metadata['lesson']} Sub {r.metadata['sublesson']}** — {r.metadata['topic']}\n\n"
                    f"    {r.page_content[:750]}..."
                )

