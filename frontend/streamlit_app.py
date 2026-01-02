import streamlit as st
from sentence_transformers import Sentence_Transformers
import chromadb
from chromadb.config import Settings
import numpy as np

# ---------------- PAGE CONFIG ----------------
st.set_page_config(page_title="🔐 Company Internal Chatbot", layout="centered")

# ---------------- USERS & ROLES ----------------
USERS = {
    "intern": {"password": "intern123", "role": "intern"},
    "hr": {"password": "hr123", "role": "hr"},
    "finance": {"password": "finance123", "role": "finance"},
    "admin": {"password": "admin123", "role": "admin"},
    "ceo": {"password": "ceo123", "role": "c_level"},
}

ROLE_ACCESS = {
    "intern": ["general"],
    "hr": ["general", "hr"],
    "finance": ["general", "finance"],
    "c_level": ["general", "finance", "c_level"],
    "admin": ["general", "hr", "finance", "c_level"],
}

SIMILARITY_THRESHOLD = 0.35   # 🔥 KEY FIX

# ---------------- SESSION STATE ----------------
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

# ---------------- LOGIN ----------------
if not st.session_state.logged_in:
    st.title("🔐 Company Internal Chatbot")

    username = st.text_input("Username")
    password = st.text_input("Password", type="password")

    if st.button("Login"):
        if username in USERS and USERS[username]["password"] == password:
            st.session_state.logged_in = True
            st.session_state.user = username
            st.session_state.role = USERS[username]["role"]
            st.rerun()
        else:
            st.error("❌ Invalid credentials")

    st.stop()

# ---------------- AFTER LOGIN ----------------
st.success(f"✅ Logged in as **{st.session_state.user}** ({st.session_state.role})")

# ---------------- LOAD MODEL ----------------
@st.cache_resource
def load_model():
    return SentenceTransformer("all-MiniLM-L6-v2")

model = load_model()

# ---------------- CHROMADB ----------------
@st.cache_resource
def load_chroma():
    client = chromadb.Client(Settings(anonymized_telemetry=False))
    return client.get_or_create_collection(name="company_docs")

collection = load_chroma()

# ---------------- SEED DATA ----------------
if collection.count() == 0:
    docs = [
        ("Company working hours are 9 AM to 6 PM.", "general"),
        ("Interns receive mentorship and training programs.", "general"),
        ("HR policies include leave, attendance, and conduct rules.", "hr"),
        ("Employee salaries are confidential.", "finance"),
        ("Company profit grew by 18% this year.", "finance"),
        ("CEO strategy focuses on global expansion.", "c_level"),
    ]

    collection.add(
        documents=[d[0] for d in docs],
        metadatas=[{"category": d[1]} for d in docs],
        ids=[str(i) for i in range(len(docs))]
    )

# ---------------- CHAT ----------------
st.subheader("💬 Ask your question")
query = st.text_input("Enter your question")

if query:
    query_embedding = model.encode(query).tolist()
    allowed_categories = ROLE_ACCESS[st.session_state.role]

    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=5,
        where={"category": {"$in": allowed_categories}}
    )

    documents = results.get("documents", [[]])[0]
    distances = results.get("distances", [[]])[0]

    if not documents:
        st.error("❌ No authorized data available.")
        st.stop()

    # 🔥 PICK BEST MATCH WITH THRESHOLD
    best_idx = np.argmin(distances)
    best_distance = distances[best_idx]
    best_answer = documents[best_idx]

    if best_distance > SIMILARITY_THRESHOLD:
        st.warning("⚠️ No relevant information found for your question.")
    else:
        st.success("Answer:")
        st.write(best_answer)

# ---------------- LOGOUT ----------------
st.markdown("---")
if st.button("Logout"):
    st.session_state.logged_in = False
    st.rerun()
