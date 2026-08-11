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
st.markdown("""
<style>

.book-title {
    text-align: center;
    margin-top: 55px;
    position: relative;
    z-index: 10;
}

.book-title-main {
    font-family: "Caslon 540 Roman,", Georgia, serif;
    font-size: 88px;
    font-weight: 600;
    letter-spacing: 2px;
    line-height: 1;
    color: #F4E6D7;
    text-shadow:
        0 3px 8px rgba(0, 0, 0, 0.65),
        0 0 25px rgba(201, 138, 157, 0.15);
}

.book-title-subtitle {
    font-family: "Cormorant Garamond", Georgia, serif;
    font-size: 20px;
    font-style: italic;
    letter-spacing: 5px;
    color: #C98A9D;
    margin-top: 14px;
}

</style>

<div class="book-title">
    <div class="book-title-main">My Book Tree</div>
    <div class="book-title-subtitle"></div>
</div>
""", unsafe_allow_html=True)
