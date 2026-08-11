import streamlit as st

st.set_page_config(
    page_title="My Book Tree",
    page_icon="🌿",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ============================================================
# MY BOOK TREE — FOUNDATION
# ============================================================

st.markdown("""
<style>

@import url('https://fonts.googleapis.com/css2?family=Libre+Baskerville:wght@400;700&display=swap');

:root {
    --background: #4A0000;
    --text: #FFD700;
    --accent: #FFA6C9;
    --gold: #C8A46A;
}

/* Main application */

.stApp {
    background: var(--background);
    color: var(--text);
}

/* Remove Streamlit's default top spacing */

.block-container {
    max-width: 1500px;
    padding-top: 35px;
    padding-left: 50px;
    padding-right: 50px;
}

/* Main typography */

html,
body,
.stApp,
.stApp * {
    font-family: "Libre Baskerville", Georgia, serif;
}

/* Hide Streamlit branding */

#MainMenu {
    visibility: hidden;
}

footer {
    visibility: hidden;
}

header {
    visibility: hidden;
}

/* Title */

.book-tree-title {
    text-align: center;
    margin-top: 20px;
}

.book-tree-title h1 {
    margin: 0;
    padding: 0;
    color: var(--text);
    font-size: 76px;
    font-weight: 400;
    letter-spacing: 1px;
    line-height: 1.05;
}

.book-tree-title p {
    margin-top: 14px;
    color: var(--accent);
    font-size: 18px;
    font-style: italic;
    letter-spacing: 3px;
}

</style>
""", unsafe_allow_html=True)


st.markdown("""
<div class="book-tree-title">
    <h1>My Book Tree</h1>
</div>
""", unsafe_allow_html=True)
