import streamlit as st
import warnings
warnings.filterwarnings("ignore", category=FutureWarning)

import os
import pickle
import faiss
import numpy as np
from sentence_transformers import SentenceTransformer

# --------------------------------------------------
# PAGE CONFIG
# --------------------------------------------------
st.set_page_config(
    page_title="Company Internal Chatbot",
    layout="centered"
)

st.title("🔐 Company Internal Chatbot")

# --------------------------------------------------
# PATH CONFIG
# --------------------------------------------------
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

INDEX_PATH = os.path.join(BASE_DIR, "data", "vector_db", "index.faiss")
META_PATH  = os.path.join(BASE_DIR, "data", "vector_db", "metadata.pkl")

# --------------------------------------------------
# SAFETY CHECK
# --------------------------------------------------
if not os.path.exists(INDEX_PATH) or not os.path.exists(META_PATH):
    st.error("❌ Vector store not found. Please create FAISS index first.")
    st.stop()

# --------------------------------------------------
# LOAD MODEL (CPU SAFE)
# --------------------------------------------------
@st.cache_resource
def load_model():
    return SentenceTransformer("all-MiniLM-L6-v2", device="cpu")

MODEL = load_model()

# --------------------------------------------------
# LOAD VECTOR STORE
# --------------------------------------------------
index = faiss.read_index(INDEX_PATH)

with open(META_PATH, "rb") as f:
    metadata = pickle.load(f)

# --------------------------------------------------
# USERS (RBAC)
# --------------------------------------------------
USERS = {
    "intern": {"password": "intern123", "role": "employee"},
    "hr": {"password": "hr123", "role": "hr"},
    "finance": {"password": "finance123", "role": "finance"},

    "ceo": {"password": "ceo123", "role": "clevel"},
    "cto": {"password": "cto123", "role": "clevel"},
    "cfo": {"password": "cfo123", "role": "clevel"},

    "admin": {"password": "admin123", "role": "admin"},
}

# --------------------------------------------------
# SESSION STATE
# --------------------------------------------------
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.role = None
    st.session_state.username = None

# --------------------------------------------------
# RBAC FILTER (VERY IMPORTANT)
# --------------------------------------------------
def allowed_docs(user_role, docs):
    if user_role == "admin":
        return docs

    if user_role == "clevel":
        return [d for d in docs if d["role"] in ["general", "hr", "finance"]]

    if user_role == "employee":
        return [d for d in docs if d["role"] in ["general", "employee"]]

    return [d for d in docs if d["role"] in ["general", user_role]]

# --------------------------------------------------
# LOGIN UI
# --------------------------------------------------
if not st.session_state.logged_in:
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")

    if st.button("Login"):
        if username in USERS and USERS[username]["password"] == password:
            st.session_state.logged_in = True
            st.session_state.role = USERS[username]["role"]
            st.session_state.username = username
            st.success(f"✅ Logged in as {st.session_state.role}")
            st.rerun()   # 🔥 THIS FIXES YOUR ISSUE
        else:
            st.error("❌ Invalid credentials")

    st.stop()

# --------------------------------------------------
# CHAT UI
# --------------------------------------------------
st.subheader(f"💬 Welcome {st.session_state.username}")
query = st.text_input("Ask your question")

if query:
    query_vec = MODEL.encode([query]).astype("float32")
    D, I = index.search(query_vec, 5)

    retrieved_docs = [metadata[i] for i in I[0]]
    permitted_docs = allowed_docs(st.session_state.role, retrieved_docs)

    if not permitted_docs:
        st.error("❌ Access denied for your role.")
    else:
        st.success("Answer:")
        for doc in permitted_docs[:2]:   # 🔥 LIMIT ANSWERS
            st.write("•", doc["text"])

# --------------------------------------------------
# LOGOUT
# --------------------------------------------------
st.markdown("---")
if st.button("Logout"):
    st.session_state.clear()
    st.rerun()
