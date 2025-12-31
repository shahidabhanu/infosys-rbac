import streamlit as st
import os

# ---------------------------------
# USERS (RBAC)
# ---------------------------------
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

# ---------------------------------
# ROLE → DOCUMENT ACCESS
# ---------------------------------
ROLE_DOCS = {
    "employee": ["general.txt"],
    "finance": ["finance.txt", "general.txt"],
    "hr": ["hr.txt", "general.txt"],
    "admin": [
        "general.txt",
        "finance.txt",
        "hr.txt",
        "engineering.txt",
        "employeedata.txt"
    ]
}

DATA_DIR = "data/documents"

# ---------------------------------
# AUTHENTICATION
# ---------------------------------
def authenticate(username, password):
    user = USERS.get(username)
    if user and user["password"] == password:
        return user["role"]
    return None

# ---------------------------------
# LOAD DOCUMENTS BY ROLE
# ---------------------------------
def load_documents(role):
    docs = []
    for file in ROLE_DOCS.get(role, []):
        path = os.path.join(DATA_DIR, file)
        if os.path.exists(path):
            with open(path, "r", encoding="utf-8") as f:
                docs.append(f.read())
    return "\n".join(docs)

# ---------------------------------
# CHATBOT RESPONSE (FIXED LOGIC)
# ---------------------------------
def chatbot_response(query, role):
    knowledge = load_documents(role)

    if not knowledge.strip():
        return "❌ No documents available for your role."

    # Keyword-based relevance check
    keywords = query.lower().split()
    match_found = any(word in knowledge.lower() for word in keywords)

    if match_found:
        return (
            "✅ Based on documents permitted for your role:\n\n"
            + knowledge[:800]
        )
    else:
        return (
            "❌ The information you requested is not available "
            "for your role based on access permissions."
        )

# ---------------------------------
# STREAMLIT UI
# ---------------------------------
st.set_page_config(
    page_title="Internal RBAC Chatbot",
    page_icon="🤖",
    layout="centered"
)

st.title("🤖 Company Internal Chatbot")
st.write("Role-Based Access Control + Document-Aware Chatbot")

# Session state
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "role" not in st.session_state:
    st.session_state.role = None

# ---------------------------------
# LOGIN PAGE
# ---------------------------------
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

# ---------------------------------
# CHAT PAGE
# ---------------------------------
else:
    st.success(f"Logged in role: **{st.session_state.role.upper()}**")

    query = st.text_input("Ask a question related to your department")

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
