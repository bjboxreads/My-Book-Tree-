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
    color: #F5E8D8;
}

.block-container {
    max-width: 1500px;
    padding: 50px;
}

.book-tree-title {
    text-align: center;
    margin-top: 55px;
}

.book-tree-title h1 {
    margin: 0;
    font-family: "Berkshire Swash", cursive;
    font-size: 88px;
    font-weight: 400;
    letter-spacing: 1px;
    line-height: 1.1;
    color: #F5E8D8;
    text-shadow:
        0 3px 10px rgba(0, 0, 0, 0.7),
        0 0 28px rgba(201, 138, 157, 0.18);
}

.book-tree-title p {
    margin: 15px 0 0;
    font-family: "Cormorant Garamond", serif;
    font-size: 22px;
    font-style: italic;
    letter-spacing: 4px;
    color: #C98A9D;
}

</style>
""", unsafe_allow_html=True)


st.markdown("""
<div class="book-tree-title">
    <h1>My Book Tree</h1>
    <p>where every story has a branch</p>
</div>
""", unsafe_allow_html=True)
