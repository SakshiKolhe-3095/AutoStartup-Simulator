"""
Frontend scaffold — Streamlit basic input form.
Owner: Sakshi
"""

import streamlit as st

st.set_page_config(page_title="AutoStartup Simulator", layout="centered")

st.title("AutoStartup Simulator")
st.write("Enter a one-line startup idea to generate a full startup package.")

idea = st.text_input("Startup idea", placeholder="e.g. AI-powered plant care app")

if st.button("Generate"):
    if idea.strip():
        st.info(f"Received idea: {idea}")
        # TODO: wire to backend /generate endpoint (Wk2 Day2)
    else:
        st.warning("Please enter an idea first.")