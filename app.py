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
# ============================================================
# WILLOW TREE — DIRECTLY UNDER THE HEADER
# ============================================================

st.markdown("""
<style>
.willow-wrap {
    width: 100%;
    height: 300px;
    margin-top: 10px;
    margin-bottom: 20px;
    display: flex;
    justify-content: center;
    overflow: hidden;
}

.willow-wrap svg {
    width: 100%;
    max-width: 1200px;
    height: 300px;
}
</style>

<div class="willow-wrap">

<svg viewBox="0 0 1200 300"
     xmlns="http://www.w3.org/2000/svg">

    <!-- trunk -->
    <path d="M600 310
             C590 250 585 190 595 135
             C600 105 610 75 625 45"
          fill="none"
          stroke="#4A3028"
          stroke-width="28"
          stroke-linecap="round"/>

    <path d="M604 305
             C598 245 597 190 605 140
             C610 105 620 75 630 48"
          fill="none"
          stroke="#765044"
          stroke-width="7"
          stroke-linecap="round"/>

    <!-- main branches -->
    <g fill="none"
       stroke="#54372E"
       stroke-linecap="round">

        <path d="M605 150 C535 115 470 85 390 70" stroke-width="12"/>
        <path d="M610 140 C675 100 745 72 825 65" stroke-width="12"/>
        <path d="M600 180 C520 155 445 145 350 150" stroke-width="9"/>
        <path d="M615 175 C690 145 770 135 860 145" stroke-width="9"/>
        <path d="M600 115 C550 75 520 45 500 15" stroke-width="8"/>
        <path d="M625 110 C680 70 710 40 730 10" stroke-width="8"/>

    </g>

    <!-- hanging willow branches -->
    <g fill="none"
       stroke="#657452"
       stroke-width="4"
       stroke-linecap="round">

        <path d="M390 70 C380 125 390 175 405 235"/>
        <path d="M430 75 C420 135 430 195 445 250"/>
        <path d="M475 82 C465 145 475 205 490 255"/>
        <path d="M520 90 C510 145 520 205 535 245"/>

        <path d="M680 88 C690 145 680 205 665 250"/>
        <path d="M725 75 C735 135 725 195 710 255"/>
        <path d="M770 70 C780 125 770 185 755 235"/>
        <path d="M815 68 C825 120 815 175 800 225"/>

        <path d="M350 150 C345 190 350 225 360 270"/>
        <path d="M860 145 C865 190 860 225 850 270"/>

    </g>

    <!-- leaves -->
    <g fill="#74835D">

        <ellipse cx="380" cy="115" rx="7" ry="20" transform="rotate(-20 380 115)"/>
        <ellipse cx="398" cy="150" rx="7" ry="21" transform="rotate(18 398 150)"/>
        <ellipse cx="415" cy="190" rx="7" ry="20" transform="rotate(-15 415 190)"/>
        <ellipse cx="435" cy="215" rx="7" ry="22" transform="rotate(17 435 215)"/>
        <ellipse cx="465" cy="130" rx="7" ry="21" transform="rotate(-18 465 130)"/>
        <ellipse cx="485" cy="180" rx="7" ry="22" transform="rotate(16 485 180)"/>
        <ellipse cx="510" cy="215" rx="7" ry="20" transform="rotate(-18 510 215)"/>

        <ellipse cx="820" cy="115" rx="7" ry="20" transform="rotate(20 820 115)"/>
        <ellipse cx="802" cy="150" rx="7" ry="21" transform="rotate(-18 802 150)"/>
        <ellipse cx="785" cy="190" rx="7" ry="20" transform="rotate(15 785 190)"/>
        <ellipse cx="765" cy="215" rx="7" ry="22" transform="rotate(-17 765 215)"/>
        <ellipse cx="735" cy="130" rx="7" ry="21" transform="rotate(18 735 130)"/>
        <ellipse cx="715" cy="180" rx="7" ry="22" transform="rotate(-16 715 180)"/>
        <ellipse cx="690" cy="215" rx="7" ry="20" transform="rotate(18 690 215)"/>

        <ellipse cx="350" cy="205" rx="7" ry="20" transform="rotate(-15 350 205)"/>
        <ellipse cx="360" cy="245" rx="7" ry="21" transform="rotate(15 360 245)"/>
        <ellipse cx="850" cy="205" rx="7" ry="20" transform="rotate(15 850 205)"/>
        <ellipse cx="840" cy="245" rx="7" ry="21" transform="rotate(-15 840 245)"/>

    </g>

    <!-- subtle rose blossoms -->
    <g fill="#B87587">

        <circle cx="430" cy="105" r="4"/>
        <circle cx="475" cy="145" r="4"/>
        <circle cx="520" cy="175" r="4"/>
        <circle cx="770" cy="145" r="4"/>
        <circle cx="725" cy="105" r="4"/>
        <circle cx="680" cy="175" r="4"/>

    </g>

</svg>

</div>
""", unsafe_allow_html=True)
