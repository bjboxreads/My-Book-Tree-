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
    font-family: "Cormorant Garamond", Georgia, serif;
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
# ============================================================
# SECTION 3 — WILLOW TREE HEADER DECORATION
# ============================================================

st.markdown("""
<style>

.willow-header {
    position: relative;
    height: 360px;
    width: 100%;
    margin-top: -40px;
    overflow: hidden;
    pointer-events: none;
}

/* Tree trunks */

.willow-trunk {
    position: absolute;
    bottom: -35px;
    width: 48px;
    height: 310px;
    background: linear-gradient(
        90deg,
        #24161b 0%,
        #51343a 45%,
        #2a191e 100%
    );
    border-radius: 48% 52% 8% 8%;
}

.willow-trunk.left {
    left: 7%;
    transform: rotate(-7deg);
}

.willow-trunk.right {
    right: 7%;
    transform: rotate(7deg);
}

/* Main branches */

.willow-branch {
    position: absolute;
    height: 8px;
    background: #3d272e;
    border-radius: 100%;
    transform-origin: left center;
}

.willow-branch.left-a {
    width: 360px;
    left: 8%;
    top: 75px;
    transform: rotate(-25deg);
}

.willow-branch.left-b {
    width: 320px;
    left: 9%;
    top: 125px;
    transform: rotate(-12deg);
}

.willow-branch.left-c {
    width: 285px;
    left: 10%;
    top: 175px;
    transform: rotate(5deg);
}

.willow-branch.right-a {
    width: 360px;
    right: 8%;
    top: 75px;
    transform: rotate(205deg);
}

.willow-branch.right-b {
    width: 320px;
    right: 9%;
    top: 125px;
    transform: rotate(192deg);
}

.willow-branch.right-c {
    width: 285px;
    right: 10%;
    top: 175px;
    transform: rotate(185deg);
}

/* Hanging willow strands */

.willow-strand {
    position: absolute;
    width: 5px;
    background: linear-gradient(
        180deg,
        #526048,
        #7b875c,
        transparent
    );
    border-radius: 50%;
}

.willow-strand.left {
    transform-origin: top center;
}

.willow-strand.right {
    transform-origin: top center;
}

/* Left hanging strands */

.ws-l1 { left: 10%; top: 55px; height: 210px; transform: rotate(-7deg); }
.ws-l2 { left: 13%; top: 78px; height: 245px; transform: rotate(5deg); }
.ws-l3 { left: 16%; top: 60px; height: 220px; transform: rotate(-4deg); }
.ws-l4 { left: 19%; top: 90px; height: 205px; transform: rotate(6deg); }
.ws-l5 { left: 22%; top: 65px; height: 190px; transform: rotate(-5deg); }
.ws-l6 { left: 25%; top: 95px; height: 180px; transform: rotate(7deg); }

/* Right hanging strands */

.ws-r1 { right: 10%; top: 55px; height: 210px; transform: rotate(7deg); }
.ws-r2 { right: 13%; top: 78px; height: 245px; transform: rotate(-5deg); }
.ws-r3 { right: 16%; top: 60px; height: 220px; transform: rotate(4deg); }
.ws-r4 { right: 19%; top: 90px; height: 205px; transform: rotate(-6deg); }
.ws-r5 { right: 22%; top: 65px; height: 190px; transform: rotate(5deg); }
.ws-r6 { right: 25%; top: 95px; height: 180px; transform: rotate(-7deg); }

/* Willow leaves */

.willow-leaf {
    position: absolute;
    width: 11px;
    height: 32px;
    background: #657452;
    border-radius: 90% 15% 90% 15%;
    transform-origin: bottom center;
}

.willow-leaf.light {
    background: #879568;
}

.willow-leaf.deep {
    background: #48563f;
}

/* Left leaves */

.wl1  { left: 9%;  top: 105px; transform: rotate(-30deg); }
.wl2  { left: 12%; top: 150px; transform: rotate(25deg); }
.wl3  { left: 15%; top: 120px; transform: rotate(-20deg); }
.wl4  { left: 18%; top: 175px; transform: rotate(28deg); }
.wl5  { left: 21%; top: 135px; transform: rotate(-25deg); }
.wl6  { left: 24%; top: 185px; transform: rotate(25deg); }

.wl7  { left: 11%; top: 220px; transform: rotate(30deg); }
.wl8  { left: 14%; top: 250px; transform: rotate(-25deg); }
.wl9  { left: 18%; top: 230px; transform: rotate(28deg); }
.wl10 { left: 22%; top: 260px; transform: rotate(-25deg); }

/* Right leaves */

.wr1  { right: 9%;  top: 105px; transform: rotate(30deg); }
.wr2  { right: 12%; top: 150px; transform: rotate(-25deg); }
.wr3  { right: 15%; top: 120px; transform: rotate(20deg); }
.wr4  { right: 18%; top: 175px; transform: rotate(-28deg); }
.wr5  { right: 21%; top: 135px; transform: rotate(25deg); }
.wr6  { right: 24%; top: 185px; transform: rotate(-25deg); }

.wr7  { right: 11%; top: 220px; transform: rotate(-30deg); }
.wr8  { right: 14%; top: 250px; transform: rotate(25deg); }
.wr9  { right: 18%; top: 230px; transform: rotate(-28deg); }
.wr10 { right: 22%; top: 260px; transform: rotate(25deg); }

</style>

<div class="willow-header">

    <!-- LEFT TREE -->

    <div class="willow-trunk left"></div>

    <div class="willow-branch left-a"></div>
    <div class="willow-branch left-b"></div>
    <div class="willow-branch left-c"></div>

    <div class="willow-strand left ws-l1"></div>
    <div class="willow-strand left ws-l2"></div>
    <div class="willow-strand left ws-l3"></div>
    <div class="willow-strand left ws-l4"></div>
    <div class="willow-strand left ws-l5"></div>
    <div class="willow-strand left ws-l6"></div>

    <div class="willow-leaf light wl1"></div>
    <div class="willow-leaf wl2"></div>
    <div class="willow-leaf deep wl3"></div>
    <div class="willow-leaf wl4"></div>
    <div class="willow-leaf light wl5"></div>
    <div class="willow-leaf deep wl6"></div>
    <div class="willow-leaf wl7"></div>
    <div class="willow-leaf light wl8"></div>
    <div class="willow-leaf deep wl9"></div>
    <div class="willow-leaf wl10"></div>


    <!-- RIGHT TREE -->

    <div class="willow-trunk right"></div>

    <div class="willow-branch right-a"></div>
    <div class="willow-branch right-b"></div>
    <div class="willow-branch right-c"></div>

    <div class="willow-strand right ws-r1"></div>
    <div class="willow-strand right ws-r2"></div>
    <div class="willow-strand right ws-r3"></div>
    <div class="willow-strand right ws-r4"></div>
    <div class="willow-strand right ws-r5"></div>
    <div class="willow-strand right ws-r6"></div>

    <div class="willow-leaf light wr1"></div>
    <div class="willow-leaf wr2"></div>
    <div class="willow-leaf deep wr3"></div>
    <div class="willow-leaf wr4"></div>
    <div class="willow-leaf light wr5"></div>
    <div class="willow-leaf deep wr6"></div>
    <div class="willow-leaf wr7"></div>
    <div class="willow-leaf light wr8"></div>
    <div class="willow-leaf deep wr9"></div>
    <div class="willow-leaf wr10"></div>

</div>
""", unsafe_allow_html=True)
