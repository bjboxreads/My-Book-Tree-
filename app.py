st.markdown("""
<style>

@import url('https://fonts.googleapis.com/css2?family=Berkshire+Swash&family=Cormorant+Garamond:ital,wght@0,400;0,500;0,600;1,400;1,500&display=swap');

:root {
    --background: #160D13;
    --cream: #F5E8D8;
    --rose: #C98A9D;
    --gold: #C9A66B;
}

/* PAGE */

.stApp {
    background: var(--background);
    color: var(--cream);
}

.block-container {
    max-width: 1500px;
    padding: 40px 50px 80px;
}

/* MAIN TITLE */

.book-tree-title {
    text-align: center;
    margin-top: 45px;
    position: relative;
    z-index: 10;
}

.book-tree-title h1 {
    margin: 0;
    padding: 0;

    font-family: "Berkshire Swash", cursive;

    font-size: 86px;
    font-weight: 400;
    letter-spacing: 1px;
    line-height: 1.1;

    color: var(--cream);

    text-shadow:
        0 3px 10px rgba(0,0,0,.7),
        0 0 28px rgba(201,138,157,.18);
}

.book-tree-title p {
    margin: 15px 0 0;

    font-family: "Cormorant Garamond", serif;

    font-size: 22px;
    font-style: italic;
    font-weight: 500;
    letter-spacing: 4px;

    color: var(--rose);
}

</style>
""", unsafe_allow_html=True)


st.markdown("""
<div class="book-tree-title">
    <h1>My Book Tree</h1>
    <p>where every story has a branch</p>
</div>
""", unsafe_allow_html=True)
