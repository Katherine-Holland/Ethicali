# frontend/app.py

import streamlit as st

st.set_page_config(
    page_title="Ethicali AI Validator",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.title("🛡️ Ethicali AI Validator")
st.write("Welcome! Use the sidebar to select a validation framework, view compliance results, or upload your data.")
