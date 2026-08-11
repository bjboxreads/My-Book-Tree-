import streamlit as st

st.set_page_config(
    page_title="My Book Tree",
    page_icon="🌿",
    layout="wide"
)

st.markdown("""
<style>

@import url('https://fonts.googleapis.com/css2?family=Cormorant+Garamond:wght@400;500;600;700&family=Italianno&display=swap');

.stApp {
    background:
        radial-gradient(circle at 50% 35%,
            #382231 0%,
            #1d111b 45%,
            #0d080d 100%);
    color: #f5e9dc;
}

.block-container {
    max-width: 1500px;
    padding: 20px 25px 80px;
}

/* =========================================================
   HEADER
   ========================================================= */

.book-header {
    position: relative;
    height: 430px;
    width: 100%;
    display: flex;
    align-items: center;
    justify-content: center;
    overflow: hidden;
}

/* ---------------------------------------------------------
   TITLE
   --------------------------------------------------------- */

.title-wrapper {
    position: relative;
    z-index: 10;
    text-align: center;
    margin-top: -10px;
}

.title-small {
    font-family: "Cormorant Garamond", serif;
    color: #d6ad69;
    font-size: 16px;
    letter-spacing: 7px;
    text-transform: uppercase;
    margin-bottom: 8px;
}

.main-title {
    font-family: "Cormorant Garamond", serif;
    font-size: 92px;
    line-height: .82;
    font-weight: 500;
    letter-spacing: 2px;
    color: #f6e8d8;
    text-shadow:
        0 2px 4px rgba(0,0,0,.8),
        0 8px 30px rgba(0,0,0,.65);
    margin: 0;
}

.subtitle {
    font-family: "Italianno", cursive;
    font-size: 32px;
    color: #c98a9d;
    margin-top: 18px;
}

/* =========================================================
   WILLOW TREE
   ========================================================= */

.willow {
    position: absolute;
    inset: 0;
    width: 100%;
    height: 100%;
    pointer-events: none;
}

/* Trunks */

.trunk {
    fill: none;
    stroke: #24171b;
    stroke-linecap: round;
    stroke-linejoin: round;
}

.trunk-highlight {
    fill: none;
    stroke: #4b3030;
    stroke-linecap: round;
    stroke-linejoin: round;
}

/* Branches */

.branch {
    fill: none;
    stroke: #332024;
    stroke-linecap: round;
}

.branch-light {
    fill: none;
    stroke: #5c3b43;
    stroke-linecap: round;
}

/* Hanging willow leaves */

.leaf {
    fill: #617052;
}

.leaf-light {
    fill: #7f8b62;
}

.leaf-dark {
    fill: #394936;
}

/* Decorative tiny flowers */

.flower {
    fill: #b86c83;
}

.flower-gold {
    fill: #d6ad69;
}

/* =========================================================
   LITTLE BOOKISH ORNAMENT
   ========================================================= */

.ornament {
    position: absolute;
    bottom: 22px;
    left: 50%;
    transform: translateX(-50%);
    color: #d6ad69;
    font-family: "Cormorant Garamond", serif;
    font-size: 22px;
    letter-spacing: 10px;
    z-index: 12;
}

.ornament-line {
    display: inline-block;
    width: 160px;
    border-top: 1px solid #6f4c58;
    vertical-align: middle;
    margin: 0 15px;
}

</style>

<div class="book-header">

    <!-- =====================================================
         WILLOW TREE SVG
         ===================================================== -->

    <svg class="willow"
         viewBox="0 0 1500 430"
         preserveAspectRatio="xMidYMid meet"
         xmlns="http://www.w3.org/2000/svg">

        <!-- LEFT TRUNK -->

        <path class="trunk"
              stroke-width="30"
              d="
              M 90 430
              C 115 350, 125 275, 150 210
              C 170 155, 205 105, 235 55
              " />

        <path class="trunk-highlight"
              stroke-width="7"
              d="
              M 100 430
              C 130 345, 135 275, 160 215
              C 182 155, 210 110, 238 60
              " />

        <!-- LEFT MAIN BRANCHES -->

        <path class="branch" stroke-width="14"
              d="M 145 225 C 90 170, 55 115, 35 45" />

        <path class="branch-light" stroke-width="4"
              d="M 145 225 C 90 170, 55 115, 35 45" />

        <path class="branch" stroke-width="11"
              d="M 155 205 C 90 145, 70 85, 65 20" />

        <path class="branch" stroke-width="10"
              d="M 165 185 C 120 120, 115 70, 125 12" />

        <path class="branch" stroke-width="9"
              d="M 185 145 C 160 85, 170 40, 195 8" />

        <path class="branch-light" stroke-width="4"
              d="M 185 145 C 160 85, 170 40, 195 8" />

        <path class="branch" stroke-width="8"
              d="M 210 105 C 215 60, 245 30, 280 10" />

        <!-- LEFT CASCADING BRANCHES -->

        <path class="branch-light" stroke-width="4"
              d="M 65 40 C 55 100, 70 145, 82 190" />

        <path class="branch-light" stroke-width="3"
              d="M 100 30 C 95 95, 105 150, 125 205" />

        <path class="branch-light" stroke-width="3"
              d="M 145 20 C 140 80, 150 130, 170 175" />

        <path class="branch-light" stroke-width="3"
              d="M 200 18 C 185 70, 195 105, 210 145" />

        <!-- RIGHT TRUNK -->

        <path class="trunk"
              stroke-width="31"
              d="
              M 1410 430
              C 1380 350, 1370 275, 1345 210
              C 1325 155, 1295 105, 1265 55
              " />

        <path class="trunk-highlight"
              stroke-width="7"
              d="
              M 1400 430
              C 1370 345, 1365 275, 1340 215
              C 1318 155, 1290 110, 1262 60
              " />

        <!-- RIGHT MAIN BRANCHES -->

        <path class="branch" stroke-width="14"
              d="M 1355 225 C 1410 170, 1445 115, 1465 45" />

        <path class="branch-light" stroke-width="4"
              d="M 1355 225 C 1410 170, 1445 115, 1465 45" />

        <path class="branch" stroke-width="11"
              d="M 1345 205 C 1410 145, 1430 85, 1435 20" />

        <path class="branch" stroke-width="10"
              d="M 1335 185 C 1380 120, 1385 70, 1375 12" />

        <path class="branch" stroke-width="9"
              d="M 1315 145 C 1340 85, 1330 40, 1305 8" />

        <path class="branch-light" stroke-width="4"
              d="M 1315 145 C 1340 85, 1330 40, 1305 8" />

        <path class="branch" stroke-width="8"
              d="M 1290 105 C 1285 60, 1255 30, 1220 10" />

        <!-- RIGHT CASCADING BRANCHES -->

        <path class="branch-light" stroke-width="4"
              d="M 1435 40 C 1445 100, 1430 145, 1418 190" />

        <path class="branch-light" stroke-width="3"
              d="M 1400 30 C 1405 95, 1395 150, 1375 205" />

        <path class="branch-light" stroke-width="3"
              d="M 1355 20 C 1360 80, 1350 130, 1330 175" />

        <path class="branch-light" stroke-width="3"
              d="M 1300 18 C 1315 70, 1305 105, 1290 145" />

        <!-- =================================================
             LEFT LEAVES
             ================================================= -->

        <g>
            <ellipse class="leaf" cx="35" cy="48" rx="9" ry="25" transform="rotate(-15 35 48)"/>
            <ellipse class="leaf-light" cx="48" cy="72" rx="8" ry="24" transform="rotate(18 48 72)"/>
            <ellipse class="leaf-dark" cx="61" cy="105" rx="8" ry="25" transform="rotate(-12 61 105)"/>
            <ellipse class="leaf" cx="75" cy="138" rx="8" ry="25" transform="rotate(15 75 138)"/>
            <ellipse class="leaf-light" cx="82" cy="172" rx="8" ry="25" transform="rotate(-10 82 172)"/>

            <ellipse class="leaf-dark" cx="65" cy="20" rx="8" ry="25"/>
            <ellipse class="leaf" cx="75" cy="55" rx="8" ry="26"/>
            <ellipse class="leaf-light" cx="91" cy="91" rx="8" ry="25"/>
            <ellipse class="leaf-dark" cx="105" cy="130" rx="8" ry="27"/>
            <ellipse class="leaf" cx="120" cy="168" rx="8" ry="25"/>

            <ellipse class="leaf" cx="125" cy="20" rx="8" ry="25"/>
            <ellipse class="leaf-light" cx="135" cy="52" rx="8" ry="25"/>
            <ellipse class="leaf-dark" cx="145" cy="88" rx="8" ry="26"/>
            <ellipse class="leaf" cx="158" cy="125" rx="8" ry="27"/>
            <ellipse class="leaf-light" cx="170" cy="160" rx="8" ry="25"/>

            <ellipse class="leaf-light" cx="195" cy="15" rx="8" ry="24"/>
            <ellipse class="leaf" cx="202" cy="47" rx="8" ry="25"/>
            <ellipse class="leaf-dark" cx="210" cy="78" rx="8" ry="25"/>
            <ellipse class="leaf-light" cx="220" cy="110" rx="8" ry="24"/>
        </g>

        <!-- =================================================
             RIGHT LEAVES
             ================================================= -->

        <g>
            <ellipse class="leaf" cx="1465" cy="48" rx="9" ry="25" transform="rotate(15 1465 48)"/>
            <ellipse class="leaf-light" cx="1452" cy="72" rx="8" ry="24" transform="rotate(-18 1452 72)"/>
            <ellipse class="leaf-dark" cx="1439" cy="105" rx="8" ry="25" transform="rotate(12 1439 105)"/>
            <ellipse class="leaf" cx="1425" cy="138" rx="8" ry="25" transform="rotate(-15 1425 138)"/>
            <ellipse class="leaf-light" cx="1418" cy="172" rx="8" ry="25" transform="rotate(10 1418 172)"/>

            <ellipse class="leaf-dark" cx="1435" cy="20" rx="8" ry="25"/>
            <ellipse class="leaf" cx="1425" cy="55" rx="8" ry="26"/>
            <ellipse class="leaf-light" cx="1409" cy="91" rx="8" ry="25"/>
            <ellipse class="leaf-dark" cx="1395" cy="130" rx="8" ry="27"/>
            <ellipse class="leaf" cx="1380" cy="168" rx="8" ry="25"/>

            <ellipse class="leaf" cx="1375" cy="20" rx="8" ry="25"/>
            <ellipse class="leaf-light" cx="1365" cy="52" rx="8" ry="25"/>
            <ellipse class="leaf-dark" cx="1355" cy="88" rx="8" ry="26"/>
            <ellipse class="leaf" cx="1342" cy="125" rx="8" ry="27"/>
            <ellipse class="leaf-light" cx="1330" cy="160" rx="8" ry="25"/>

            <ellipse class="leaf-light" cx="1305" cy="15" rx="8" ry="24"/>
            <ellipse class="leaf" cx="1298" cy="47" rx="8" ry="25"/>
            <ellipse class="leaf-dark" cx="1290" cy="78" rx="8" ry="25"/>
            <ellipse class="leaf-light" cx="1280" cy="110" rx="8" ry="24"/>
        </g>

        <!-- =================================================
             SMALL FLOWERS
             ================================================= -->

        <g class="flower">
            <circle cx="245" cy="65" r="3"/>
            <circle cx="250" cy="60" r="3"/>
            <circle cx="255" cy="65" r="3"/>
            <circle cx="250" cy="70" r="3"/>
        </g>

        <g class="flower">
            <circle cx="1255" cy="65" r="3"/>
            <circle cx="1250" cy="60" r="3"/>
            <circle cx="1245" cy="65" r="3"/>
            <circle cx="1250" cy="70" r="3"/>
        </g>

        <circle class="flower-gold" cx="280" cy="95" r="3"/>
        <circle class="flower-gold" cx="1220" cy="95" r="3"/>

    </svg>

    <!-- =====================================================
         TITLE
         ===================================================== -->

    <div class="title-wrapper">

        <div class="title-small">
            A Library of Stories
        </div>

        <div class="main-title">
            My Book Tree
        </div>

        <div class="subtitle">
            where every story has a branch
        </div>

    </div>

    <div class="ornament">
        <span class="ornament-line"></span>
        ❦
        <span class="ornament-line"></span>
    </div>

</div>
""", unsafe_allow_html=True)
