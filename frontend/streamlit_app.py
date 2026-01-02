import streamlit as st
from sentence_transformers import SentenceTransformer
import chromadb
from chromadb.config import Settings

# ----------------------------
# BASIC CONFIG
# ----------------------------
st.set_page_config(page_title="🔐 Company Internal Chatbot", layout="centered")

# ----------------------------
# USERS & ROLES
# ----------------------------
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
    "admin": ["general", "hr", "finance", "c_level"],
    "c_level": ["general", "finance", "c_level"],
}

# ----------------------------
# LOGIN
# ----------------------------
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

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

# ----------------------------
# AFTER LOGIN
# ----------------------------
st.success(f"✅ Logged in as **{st.session_state.user}** ({st.session_state.role})")

# ----------------------------
# LOAD MODEL
# ----------------------------
@st.cache_resource
def load_model():
    return SentenceTransformer("all-MiniLM-L6-v2")

model = load_model()

# ----------------------------
# CHROMADB SETUP
# ----------------------------
@st.cache_resource
def load_chroma():
    client = chromadb.Client(Settings(anonymized_telemetry=False))
    return client.get_or_create_collection(name="company_docs")

collection = load_chroma()

# ----------------------------
# SAMPLE DATA (YOU CAN REPLACE WITH FILE INGESTION)
# ----------------------------
if collection.count() == 0:
    docs = [
        ("Company working hours are 9AM to 6PM.", "general"),
        ("Interns receive mentorship and training programs.", "general"),
        ("HR policy includes leave, attendance, and conduct rules.", "hr"),
        ("Employee salaries are confidential.", "finance"),
        ("Company profit grew by 18% this year.", "finance"),
        ("CEO strategy focuses on global expansion.", "c_level"),
    ]

    collection.add(
        documents=[d[0] for d in docs],
        metadatas=[{"category": d[1]} for d in docs],
        ids=[str(i) for i in range(len(docs))]
    )

# ----------------------------
# CHAT INTERFACE
# ----------------------------
st.subheader("💬 Ask a Question")

query = st.text_input("Your question")

if st.button("Ask") and query:
    query_embedding = model.encode(query).tolist()

    allowed_categories = ROLE_ACCESS[st.session_state.role]

    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=3,
        where={"category": {"$in": allowed_categories}}
    )

    docs = results.get("documents", [[]])[0]

    if not docs:
        st.warning("🚫 Access denied or no relevant data found.")
    else:
        st.markdown("### ✅ Answer")
        for d in docs:
            st.write("•", d)
