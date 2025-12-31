import streamlit as st
import os

# -----------------------------
# USERS (RBAC)
# -----------------------------
USERS = {
    "intern": {
        "password": "intern123",
        "role": "employee"
    },
    "finance_user": {
        "password": "finance123",
        "role": "finance"
    },
    "hr_user": {
        "password": "hr123",
        "role": "hr"
    },
    "admin": {
        "password": "admin123",
        "role": "admin"
    }
}

# -----------------------------
# ROLE → DOCUMENT ACCESS
# -----------------------------
ROLE_DOCS = {
    "employee": ["general.txt"],
    "finance": ["finance.txt", "general.txt"],
    "hr": ["hr.txt", "general.txt"],
    "admin": ["general.txt", "finance.txt", "hr.txt", "engineering.txt", "employeedata.txt"]
}

DATA_DIR = "data/documents"

# -----------------------------
# AUTH FUNCTION
# -----------------------------
def authenticate(username, password):
    user = USERS.get(username)
    if user and user["password"] == password:
        return user["role"]
    return None

# -----------------------------
# LOAD DOCUMENTS BY ROLE
# -----------------------------
def load_documents(role):
    docs = []
    allowed_files = ROLE_DOCS.get(role, [])

    for file in allowed_files:
        path = os.path.join(DATA_DIR, file)
        if os.path.exists(path):
            with open(path, "r", encoding="utf-8") as f:
                docs.append(f.read())

    return "\n".join(docs)

# -----------------------------
# SIMPLE CHAT RESPONSE (RAG-like)
# -----------------------------
def chatbot_response(query, role):
    knowledge = load_documents(role)
    if query.lower() in knowledge.lower():
        return "✅ Based on company documents:\n\n" + knowledge[:500]
    else:
        return "❌ Sorry, I could not find this information in your permitted documents."

# -----------------------------
# STREAMLIT UI
# -----------------------------
st.set_page_config(page_title="Internal RBAC Chatbot", page_icon="🤖")

st.title("🤖 Company Internal Chatbot")
st.write("Secure Role-Based Access Chatbot (Infosys Springboard 6.0)")

# Session state
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "role" not in st.session_state:
    st.session_state.role = None

# -----------------------------
# LOGIN PAGE
# -----------------------------
if not st.session_state.logged_in:
    st.subheader("🔐 Login")

    username = st.text_input("Username")
    password = st.text_input("Password", type="password")

    if st.button("Login"):
        role = authenticate(username, password)
        if role:
            st.session_state.logged_in = True
            st.session_state.role = role
            st.success(f"Logged in as **{role.upper()}**")
            st.rerun()
        else:
            st.error("Invalid username or password")

# -----------------------------
# CHAT PAGE
# -----------------------------
else:
    st.success(f"Role: {st.session_state.role.upper()}")

    query = st.text_input("Ask a question")

    if st.button("Ask"):
        if query.strip() == "":
            st.warning("Please enter a question")
        else:
            answer = chatbot_response(query, st.session_state.role)
            st.write(answer)

    if st.button("Logout"):
        st.session_state.logged_in = False
        st.session_state.role = None
        st.rerun()
