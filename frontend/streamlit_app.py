import streamlit as st

st.title("GuardSQL Enterprise")
lang = st.selectbox("Language", ["TR", "EN"])
if lang == "TR":
    st.write("Hoş geldiniz.")
else:
    st.write("Welcome.")
