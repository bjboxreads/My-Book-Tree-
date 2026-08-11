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
    padding: 50px 40px;
}

.book-title {
    text-align: center;
    font-family: "Cormorant Garamond", Georgia, serif;
    font-size: 82px;
    font-weight: 600;
    letter-spacing: 2px;
    color: #F5E8DC;
    margin-top: 40px;
}

</style>

<div class="book-title">
    My Book Tree
</div>
""", unsafe_allow_html=True)
