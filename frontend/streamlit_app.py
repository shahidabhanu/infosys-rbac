import streamlit as st
import os
import warnings
warnings.filterwarnings("ignore")

from sentence_transformers import SentenceTransformer
import chromadb
from chromadb.utils import embedding_functions

# ---------------- PAGE CONFIG ----------------
st.set_page_config(
    page_title="Company Internal Chatbot",
    layout="centered"
)

st.title("🔐 Company Internal Chatbot")

# ---------------- PATH CONFIG ----------------
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CHROMA_DIR = os.path.join(BASE_DIR, "data", "chroma_db")
os.makedirs(CHROMA_DIR, exist_ok=True)

# ---------------- EMBEDDING MODEL ----------------
@st.cache_resource
def load_embedding():
    return embedding_functions.SentenceTransformerEmbeddingFunction(
        model_name="all-MiniLM-L6-v2"
    )

embedding_fn = load_embedding()

# ---------------- CREATE CHROMA CLIENT ----------------
client = chromadb.Client(
    settings=chromadb.Settings(
        persist_directory=CHROMA_DIR,
        anonymized_telemetry=False
    )
)

# ---------------- BUILD VECTOR STORE ----------------
def build_vector_store():
    documents = [
        {"text": "Interns receive mentorship and training programs.", "role": "general"},
        {"text": "Employee salaries are confidential.", "role": "hr"},
        {"text": "Company profit grew by 18% this year.", "role": "finance"},
        {"text": "HR policies are available to HR staff only.", "role": "hr"},
        {"text": "Company culture promotes innovation and teamwork.", "role": "general"},
    ]

    collection = client.get_or_create_collection(
        name="company_docs",
        embedding_function=embedding_fn
    )

    if collection.count() == 0:
        for i, doc in enumerate(documents):
            collection.add(
                documents=[doc["text"]],
                metadatas=[{"role": doc["role"]}],
                ids=[f"doc_{i}"]
            )

# 🔥 BUILD ONLY ONCE
build_vector_store()

# ---------------- USERS (RBAC) ----------------
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

# ---------------- RBAC CHECK ----------------
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
    collection = client.get_collection(
        name="company_docs",
        embedding_function=embedding_fn
    )

    results = collection.query(
        query_texts=[query],
        n_results=3
    )

    answers = []
    for doc, meta in zip(results["documents"][0], results["metadatas"][0]):
        if is_allowed(st.session_state.role, meta["role"]):
            answers.append(doc)

    if answers:
        st.success("Answer:")
        st.write(answers[0])  # only best answer
    else:
        st.warning("❌ No relevant information available for your access level.")

# ---------------- LOGOUT ----------------
st.markdown("---")
if st.button("Logout"):
    st.session_state.logged_in = False
    st.rerun()
