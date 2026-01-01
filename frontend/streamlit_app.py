import streamlit as st
import warnings
warnings.filterwarnings("ignore", category=FutureWarning)

import pickle
import faiss
from sentence_transformers import SentenceTransformer
import numpy as np
import os

# ---------------- PAGE CONFIG ----------------
st.set_page_config(
    page_title="Company Internal Chatbot",
    layout="centered"
)

# ---------------- PATH CONFIG ----------------
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
INDEX_PATH = os.path.join(BASE_DIR, "data", "vector_db", "index.faiss")
META_PATH = os.path.join(BASE_DIR, "data", "vector_db", "metadata.pkl")

# ---------------- LOAD MODEL ----------------
MODEL = SentenceTransformer("all-MiniLM-L6-v2")

# ---------------- LOAD VECTOR STORE ----------------
if not os.path.exists(INDEX_PATH) or not os.path.exists(META_PATH):
    st.error("❌ Vector store not found. Please create FAISS index first.")
    st.stop()

index = faiss.read_index(INDEX_PATH)

with open(META_PATH, "rb") as f:
    metadata = pickle.load(f)

# ---------------- USERS (RBAC) ----------------
USERS = {
    "intern": {"password": "intern123", "role": "employee"},
    "finance": {"password": "finance123", "role": "finance"},
    "hr": {"password": "hr123", "role": "hr"},
    "ceo": {"password": "ceo123", "role": "clevel"},
    "cto": {"password": "cto123", "role": "clevel"},
    "cfo": {"password": "cfo123", "role": "clevel"},
    "admin": {"password": "admin123", "role": "admin"}
}

# ---------------- SESSION STATE ----------------
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

# ---------------- ACCESS CONTROL ----------------
def is_allowed(user_role, doc_role):
    if user_role == "admin":
        return True
    if user_role == "clevel":
        return doc_role in ["general", "finance", "hr"]
    return user_role == doc_role or doc_role == "general"

# ---------------- UI ----------------
st.title("🔐 Company Internal Chatbot")

# ---------------- LOGIN ----------------
if not st.session_state.logged_in:
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")

    if st.button("Login"):
        if username in USERS and USERS[username]["password"] == password:
            st.session_state.logged_in = True
            st.session_state.role = USERS[username]["role"]
            st.session_state.username = username
            st.success(f"✅ Logged in as {st.session_state.role}")
            st.rerun()  # ✅ FIX: forces page refresh
        else:
            st.error("❌ Invalid credentials")

    st.stop()

# ---------------- CHAT ----------------
st.subheader("💬 Ask your question")
query = st.text_input("Enter your question")

if query:
    query_vec = MODEL.encode([query])
    D, I = index.search(np.array(query_vec), 10)

    answers = []
    for idx in I[0]:
        doc = metadata[idx]
        if is_allowed(st.session_state.role, doc["role"]):
            answers.append(doc["text"])

    if answers:
        st.success("Answer:")
        st.write(" ".join(answers[:3]))
    else:
        st.error("❌ Sorry, this information is not permitted for your role.")

# ---------------- LOGOUT ----------------
st.markdown("---")
if st.button("Logout"):
    st.session_state.logged_in = False
    st.rerun()
