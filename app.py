import streamlit as st

st.set_page_config(
    page_title="My Book Tree",
    page_icon="🌿",
    layout="wide"
)

st.markdown("""
<style>

@import url('https://fonts.googleapis.com/css2?family=Berkshire+Swash&family=Cormorant+Garamond:ital,wght@0,400;0,500;0,600;1,400;1,500&display=swap');

.stApp {
    background: #160D13;
}

.block-container {
    max-width: 1500px;
    padding: 50px;
}

/* ==============================
   MY BOOK TREE TITLE
   ============================== */

.book-tree-title {
    text-align: center;
    margin-top: 55px;
}

.book-tree-title h1 {
    margin: 0 !important;
    padding: 0 !important;

    font-family: "Berkshire Swash", cursive !important;
    font-size: 88px !important;
    font-weight: 400 !important;
    letter-spacing: 1px;
    line-height: 1.1;

    color: #E8C77B !important;

    text-shadow:
        0 3px 8px rgba(0, 0, 0, 0.8),
        0 0 18px rgba(232, 199, 123, 0.15);
}

.book-tree-title p {
    margin: 15px 0 0 !important;
    padding: 0 !important;

    font-family: "Cormorant Garamond", serif !important;
    font-size: 22px !important;
    font-style: italic;
    font-weight: 500;

    letter-spacing: 4px;

    color: #C98A9D !important;
}

</style>
""", unsafe_allow_html=True)

st.markdown("""
<div class="book-tree-title">
    <h1>My Book Tree</h1>
</div>
""", unsafe_allow_html=True)
