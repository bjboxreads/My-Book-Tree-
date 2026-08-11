import streamlit as st

st.set_page_config(
    page_title="My Book Tree",
    page_icon="🌿",
    layout="wide"
)

st.markdown("""
<style>

@import url('https://fonts.googleapis.com/css2?family=Cormorant+Garamond:wght@400;500;600;700&display=swap');

.stApp {
    background: #120B10;
    color: #F5E8DC;
}

.block-container {
    max-width: 1500px;
    padding: 40px;
}

</style>
""", unsafe_allow_html=True)
