import streamlit as st
import pickle
import numpy as np
import os
from sentence_transformers import SentenceTransformer
import faiss

# ---------------- PAGE CONFIG ----------------
st.set_page_config(
    page_title="Company Internal Chatbot",
    layout="centered"
)

st.title("🔐 Company Internal Chatbot")

# ---------------- PATH CONFIG ----------------
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
INDEX_PATH = os.path.join(BASE_DIR, "data", "vector_db", "index.faiss")
META_PATH = os.path.join(BASE_DIR, "data", "vector_db", "metadata.pkl")

# ---------------- LOAD MODEL ----------------
@st.cache_resource
def load_model():
    return SentenceTransformer("all-MiniLM-L6-v2")

MODEL = load_model()

# ---------------- LOAD VECTOR STORE ----------------
if not os.path.exists(INDEX_PATH) or not os.path.exists(META_PATH):
    st.error("❌ Vector store not found. Build index first.")
    st.stop()

index = faiss.read_index(INDEX_PATH)

with open(META_PATH, "rb") as f:
    metadata = pickle.load(f)

# ---------------- USERS ----------------
USERS = {
    "intern": {"password": "intern123", "role": "employee"},
    "finance": {"password": "finance123", "role": "finance"},
    "hr": {"password": "hr123", "role": "hr"},
    "ceo": {"password": "ceo123", "role": "clevel"},
    "cto": {"password": "cto123", "role": "clevel"},
    "cfo": {"password": "cfo123", "role": "clevel"},
    "admin": {"password": "admin123", "role": "admin"},
}

# ---------------- SESSION ----------------
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

# ---------------- RBAC ----------------
def is_allowed(user_role, doc_role):
    if user_role == "admin":
        return True
    if user_role == "clevel":
        return doc_role in ["general", "finance", "hr"]
    return user_role == doc_role or doc_role == "general"

# ---------------- LOGIN ----------------
if not st.session_state.logged_in:
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")

    if st.button("Login"):
        if username in USERS and USERS[username]["password"] == password:
            st.session_state.logged_in = True
            st.session_state.role = USERS[username]["role"]
            st.success(f"✅ Logged in as {st.session_state.role}")
            st.rerun()
        else:
            st.error("❌ Invalid credentials")

    st.stop()

# ---------------- CHAT ----------------
st.subheader("💬 Ask your question")
query = st.text_input("Enter your question")

if query:
    query_vec = MODEL.encode(query).astype("float32").reshape(1, -1)

    # Retrieve top 5 only
    distances, indices = index.search(query_vec, 5)

    allowed_answers = []

    for idx, dist in zip(indices[0], distances[0]):
        doc = metadata[idx]

        # DEBUG SAFETY
        doc_role = doc.get("role", "general")

        if is_allowed(st.session_state.role, doc_role):
            allowed_answers.append(doc["text"])

    if allowed_answers:
        st.success("Answer:")
        st.write(allowed_answers[0])  # only most relevant
    else:
        st.warning("❌ No relevant information available for your access level.")

# ---------------- LOGOUT ----------------
st.markdown("---")
if st.button("Logout"):
    st.session_state.logged_in = False
    st.rerun()
