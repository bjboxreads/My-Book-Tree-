```python
import streamlit as st

st.set_page_config(
    page_title="My Book Tree",
    page_icon="🌿",
    layout="wide"
)

st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Cormorant+Garamond:wght@500;600;700&display=swap');

    .stApp {
        background: #171019;
    }

    .title {
        text-align: center;
        font-family: 'Cormorant Garamond', Georgia, serif;
        font-size: 64px;
        color: #f5dfc0;
        margin-top: 80px;
    }

    .subtitle {
        text-align: center;
        font-family: Georgia, serif;
        font-size: 17px;
        color: #d4b9b0;
        margin-top: 10px;
    }
    </style>
    """,
    unsafe_allow_html=True
)

st.markdown(
    '<div class="title">My Book Tree</div>',
    unsafe_allow_html=True
)

st.markdown(
    '<div class="subtitle">Where every story has a branch</div>',
    unsafe_allow_html=True
)

st.write("")

st.success("The new app is working.")
```
