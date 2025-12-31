import streamlit as st
import requests

st.title("Company Internal Chatbot")

username = st.text_input("Username")
password = st.text_input("Password", type="password")

if st.button("Login"):
    res = requests.post(
        "http://127.0.0.1:8000/login",
        params={"username": username, "password": password}
    )
    st.write(res.json())
