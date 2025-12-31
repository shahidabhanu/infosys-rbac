# main.py
import streamlit as st
from rag import query_rag
from users import USERS

# ----------------------
# SESSION STATE FOR LOGIN
# ----------------------
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "username" not in st.session_state:
    st.session_state.username = ""
if "role" not in st.session_state:
    st.session_state.role = ""

# ----------------------
# LOGIN FUNCTION
# ----------------------
def login():
    username = st.session_state["username_input"]
    password = st.session_state["password_input"]

    if username in USERS and USERS[username]["password"] == password:
        st.session_state.logged_in = True
        st.session_state.username = username
        st.session_state.role = USERS[username]["role"]
        st.success(f"Logged in as {username} ({st.session_state.role})")
    else:
        st.error("Invalid username or password")

# ----------------------
# LOGOUT FUNCTION
# ----------------------
def logout():
    st.session_state.logged_in = False
    st.session_state.username = ""
    st.session_state.role = ""
    st.experimental_rerun()

# ----------------------
# LOGIN PAGE
# ----------------------
if not st.session_state.logged_in:
    st.title("Company Internal Chatbot (RBAC)")
    st.text_input("Username", key="username_input")
    st.text_input("Password", key="password_input", type="password")
    st.button("Login", on_click=login)
else:
    st.title(f"Welcome, {st.session_state.username} ({st.session_state.role})")
    st.button("Logout", on_click=logout)

    # ----------------------
    # CHAT INPUT
    # ----------------------
    user_query = st.text_input("Ask a question or query the system:")

    if user_query:
        role = st.session_state.role
        results = query_rag(role, user_query, top_k=5)

        st.subheader("Answer:")
        for res in results:
            st.write(res)
