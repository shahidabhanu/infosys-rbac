import streamlit as st
import os
from sentence_transformers import SentenceTransformer
import chromadb
from chromadb.config import Settings

# ---------------- PAGE CONFIG ----------------
st.set_page_config(
    page_title="Company Internal Chatbot",
    layout="centered"
)

st.title("🔐 Company Internal Chatbot")

# ---------------- PATH CONFIG ----------------
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
VECTOR_DB_PATH = os.path.join(BASE_DIR, "data", "vectorstore")

# ---------------- LOAD MODEL ----------------
@st.cache_resource
def load_model():
    return SentenceTransformer("all-MiniLM-L6-v2")

MODEL = load_model()

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

# ---------------- BUILD VECTOR STORE ----------------
def build_vector_store():
    client = chromadb.Client(
        Settings(persist_directory=VECTOR_DB_PATH)
    )

    collection = client.get_or_create_collection("company_docs")

    documents = [
        {"text": "Employee salaries are confidential.", "role": "hr"},
        {"text": "Interns receive mentorship and training programs.", "role": "employee"},
        {"text": "Company profit grew by 18% this year.", "role": "finance"},
        {"text": "HR policies apply to all full-time employees.", "role": "hr"},
        {"text": "Company vision focuses on long-term innovation.", "role": "general"},
    ]

    texts = [d["text"] for d in documents]
    roles = [d["role"] for d in documents]

    embeddings = MODEL.encode(texts).tolist()

    collection.add(
        documents=texts,
        embeddings=embeddings,
        metadatas=[{"role": r} for r in roles],
        ids=[str(i) for i in range(len(texts))]
    )

    client.persist()

# ---------------- LOAD / CREATE VECTOR STORE ----------------
if not os.path.exists(VECTOR_DB_PATH):
    st.warning("📦 Vector store not found. Building index...")
    os.makedirs(VECTOR_DB_PATH, exist_ok=True)
    build_vector_store()
    st.success("✅ Vector store created")

client = chromadb.Client(
    Settings(persist_directory=VECTOR_DB_PATH)
)
collection = client.get_collection("company_docs")

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
    query_embedding = MODEL.encode(query).tolist()

    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=5
    )

    allowed_answers = []

    for doc, meta in zip(results["documents"][0], results["metadatas"][0]):
        doc_role = meta.get("role", "general")

        if is_allowed(st.session_state.role, doc_role):
            allowed_answers.append(doc)

    if allowed_answers:
        st.success("Answer:")
        st.write(allowed_answers[0])  # most relevant only
    else:
        st.warning("❌ No relevant information available for your access level.")

# ---------------- LOGOUT ----------------
st.markdown("---")
if st.button("Logout"):
    st.session_state.logged_in = False
    st.rerun()
