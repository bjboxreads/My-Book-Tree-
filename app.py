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
    padding: 35px 40px;
}

/* ==============================
   HEADER
   ============================== */

.book-header {
    position: relative;
    height: 500px;
    display: flex;
    justify-content: center;
    align-items: center;
    overflow: hidden;
}

/* ==============================
   TITLE
   ============================== */

.book-title {
    position: relative;
    z-index: 5;
    text-align: center;
    font-family: "Cormorant Garamond", Georgia, serif;
    font-size: 82px;
    font-weight: 600;
    letter-spacing: 2px;
    color: #F5E8DC;
    text-shadow: 0 4px 18px rgba(0,0,0,.7);
}

/* ==============================
   WILLOW
   ============================== */

.willow-left,
.willow-right {
    position: absolute;
    top: 0;
    width: 43%;
    height: 100%;
    pointer-events: none;
}

.willow-left {
    left: 0;
}

.willow-right {
    right: 0;
    transform: scaleX(-1);
}

/* trunk */

.trunk {
    position: absolute;
    bottom: -40px;
    left: 18%;
    width: 75px;
    height: 420px;
    background: linear-gradient(
        90deg,
        #211519,
        #493039,
        #24171B
    );
    border-radius: 50% 45% 10% 10%;
    transform: rotate(-7deg);
}

/* branches */

.branch {
    position: absolute;
    height: 7px;
    background: #382329;
    border-radius: 100%;
    transform-origin: left center;
}

.branch.one {
    width: 300px;
    left: 19%;
    top: 120px;
    transform: rotate(-28deg);
}

.branch.two {
    width: 270px;
    left: 20%;
    top: 170px;
    transform: rotate(-13deg);
}

.branch.three {
    width: 250px;
    left: 22%;
    top: 220px;
    transform: rotate(8deg);
}

.branch.four {
    width: 220px;
    left: 20%;
    top: 90px;
    transform: rotate(-42deg);
}

/* hanging leaves */

.leaves {
    position: absolute;
    left: 18%;
    top: 30px;
    width: 330px;
    height: 350px;
}

.leaf {
    position: absolute;
    width: 12px;
    height: 52px;
    border-radius: 80% 20% 80% 20%;
    background: #59664A;
    transform-origin: top center;
    opacity: .9;
}

.leaf:nth-child(1)  { left: 35px;  top: 20px;  transform: rotate(-18deg); }
.leaf:nth-child(2)  { left: 65px;  top: 50px;  transform: rotate(14deg); }
.leaf:nth-child(3)  { left: 95px;  top: 80px;  transform: rotate(-12deg); }
.leaf:nth-child(4)  { left: 125px; top: 105px; transform: rotate(16deg); }
.leaf:nth-child(5)  { left: 155px; top: 125px; transform: rotate(-14deg); }
.leaf:nth-child(6)  { left: 190px; top: 85px;  transform: rotate(13deg); }
.leaf:nth-child(7)  { left: 220px; top: 55px;  transform: rotate(-15deg); }
.leaf:nth-child(8)  { left: 250px; top: 30px;  transform: rotate(16deg); }

.leaf:nth-child(9) {
    left: 55px;
    top: 150px;
    transform: rotate(13deg);
}

.leaf:nth-child(10) {
    left: 90px;
    top: 180px;
    transform: rotate(-16deg);
}

.leaf:nth-child(11) {
    left: 130px;
    top: 205px;
    transform: rotate(14deg);
}

.leaf:nth-child(12) {
    left: 170px;
    top: 225px;
    transform: rotate(-13deg);
}

.leaf:nth-child(13) {
    left: 210px;
    top: 190px;
    transform: rotate(16deg);
}

.leaf:nth-child(14) {
    left: 245px;
    top: 160px;
    transform: rotate(-15deg);
}

.leaf:nth-child(15) {
    left: 275px;
    top: 130px;
    transform: rotate(14deg);
}

/* a few lighter leaves */

.leaf:nth-child(3n) {
    background: #74805A;
}

.leaf:nth-child(4n) {
    background: #8A7650;
}

/* small flowers */

.flower {
    position: absolute;
    width: 7px;
    height: 7px;
    background: #B96D84;
    border-radius: 50%;
    box-shadow:
        7px 0 #B96D84,
        3px 6px #B96D84,
        3px -6px #B96D84,
        -4px 0 #B96D84;
}

.flower.one {
    left: 30%;
    top: 90px;
}

.flower.two {
    left: 55%;
    top: 155px;
}

.flower.three {
    left: 43%;
    top: 245px;
}

</style>

<div class="book-header">

    <div class="willow-left">

        <div class="trunk"></div>

        <div class="branch one"></div>
        <div class="branch two"></div>
        <div class="branch three"></div>
        <div class="branch four"></div>

        <div class="leaves">
            <div class="leaf"></div>
            <div class="leaf"></div>
            <div class="leaf"></div>
            <div class="leaf"></div>
            <div class="leaf"></div>
            <div class="leaf"></div>
            <div class="leaf"></div>
            <div class="leaf"></div>
            <div class="leaf"></div>
            <div class="leaf"></div>
            <div class="leaf"></div>
            <div class="leaf"></div>
            <div class="leaf"></div>
            <div class="leaf"></div>
            <div class="leaf"></div>
        </div>

        <div class="flower one"></div>
        <div class="flower two"></div>
        <div class="flower three"></div>

    </div>

    <div class="willow-right">

        <div class="trunk"></div>

        <div class="branch one"></div>
        <div class="branch two"></div>
        <div class="branch three"></div>
        <div class="branch four"></div>

        <div class="leaves">
            <div class="leaf"></div>
            <div class="leaf"></div>
            <div class="leaf"></div>
            <div class="leaf"></div>
            <div class="leaf"></div>
            <div class="leaf"></div>
            <div class="leaf"></div>
            <div class="leaf"></div>
            <div class="leaf"></div>
            <div class="leaf"></div>
            <div class="leaf"></div>
            <div class="leaf"></div>
            <div class="leaf"></div>
            <div class="leaf"></div>
            <div class="leaf"></div>
        </div>

        <div class="flower one"></div>
        <div class="flower two"></div>
        <div class="flower three"></div>

    </div>

    <div class="book-title">
        My Book Tree
    </div>

</div>
""", unsafe_allow_html=True)
