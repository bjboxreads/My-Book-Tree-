import streamlit as st
import pandas as pd
import requests
import re
import html

# ============================================================
# PAGE
# ============================================================

st.set_page_config(
    page_title="My Book Tree",
    page_icon="🌿",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ============================================================
# THEMES
# ============================================================

THEMES = {
    "Emerald Library": {
        "page": "#071B18",
        "surface": "#0E2924",
        "surface2": "#164239",
        "card": "#1C5146",
        "text": "#FFF7DE",
        "muted": "#C7D8CF",
        "accent": "#D8A93A",
        "accent2": "#6FB39A",
        "line": "#B9822C",
        "button": "#163D35",
        "button_text": "#FFF7DE",
    },

    "Sapphire & Gold": {
        "page": "#071426",
        "surface": "#0D2340",
        "surface2": "#15365D",
        "card": "#1C4774",
        "text": "#FFF7E1",
        "muted": "#C7D5E5",
        "accent": "#E5B94D",
        "accent2": "#75B5D4",
        "line": "#B8862F",
        "button": "#16365A",
        "button_text": "#FFF7E1",
    },

    "Gothic Rose": {
        "page": "#180B16",
        "surface": "#2A1024",
        "surface2": "#421735",
        "card": "#592044",
        "text": "#FFF4F5",
        "muted": "#DEC8D0",
        "accent": "#E36A83",
        "accent2": "#C79AD7",
        "line": "#A83F5C",
        "button": "#3A1730",
        "button_text": "#FFF4F5",
    },

    "Autumn Library": {
        "page": "#24130A",
        "surface": "#38200F",
        "surface2": "#5A3015",
        "card": "#70401D",
        "text": "#FFF1D5",
        "muted": "#DCC4A1",
        "accent": "#E2A33D",
        "accent2": "#C9663C",
        "line": "#A84F2B",
        "button": "#4B2914",
        "button_text": "#FFF1D5",
    },

    "Midnight Fantasy": {
        "page": "#0C0A20",
        "surface": "#151235",
        "surface2": "#211C51",
        "card": "#30276A",
        "text": "#FFF8E7",
        "muted": "#D1CAE7",
        "accent": "#E8C34D",
        "accent2": "#8B73D1",
        "line": "#6851A8",
        "button": "#211C4C",
        "button_text": "#FFF8E7",
    },

    "Teal & Coral Bookshop": {
        "page": "#08252A",
        "surface": "#0E3B42",
        "surface2": "#14565D",
        "card": "#1C6B70",
        "text": "#FFF6DF",
        "muted": "#C9D9D4",
        "accent": "#F0BD4D",
        "accent2": "#F27A63",
        "line": "#D65D4B",
        "button": "#14515A",
        "button_text": "#FFF6DF",
    },

    "Vintage Reader": {
        "page": "#172322",
        "surface": "#243633",
        "surface2": "#36504A",
        "card": "#49665D",
        "text": "#FFF3D8",
        "muted": "#D2D5C6",
        "accent": "#D8A84A",
        "accent2": "#A9B86B",
        "line": "#B47B31",
        "button": "#304943",
        "button_text": "#FFF3D8",
    },

    "Electric Bookstore": {
        "page": "#111225",
        "surface": "#1B1E3A",
        "surface2": "#292E59",
        "card": "#353B76",
        "text": "#FFFFFF",
        "muted": "#D0D3E9",
        "accent": "#F4C84D",
        "accent2": "#6AD6D0",
        "line": "#A66CDB",
        "button": "#24284D",
        "button_text": "#FFFFFF",
    },

    "Classic Crimson": {
        "page": "#210D0D",
        "surface": "#351313",
        "surface2": "#531B1B",
        "card": "#6A2524",
        "text": "#FFF4DF",
        "muted": "#DCC8B4",
        "accent": "#E3B34B",
        "accent2": "#D57958",
        "line": "#A83E32",
        "button": "#461717",
        "button_text": "#FFF4DF",
    },
}

# ============================================================
# SESSION STATE
# ============================================================

if (
    "theme" not in st.session_state
    or st.session_state.theme not in THEMES
):
    st.session_state.theme = "Emerald Library"

if "library" not in st.session_state:
    st.session_state.library = pd.DataFrame(
        columns=[
            "Title",
            "Author",
            "Series",
            "Series Number",
            "ISBN",
            "My Rating",
            "Status",
            "Favorite",
            "Cover",
            "Description",
            "Publisher",
            "Pages",
            "Date Read",
        ]
    )

if "open_authors" not in st.session_state:
    st.session_state.open_authors = set()

if "open_series" not in st.session_state:
    st.session_state.open_series = set()

theme = THEMES[st.session_state.theme]

# ============================================================
# CSS
# ============================================================

st.html(
    f"""
<style>

@import url(
'https://fonts.googleapis.com/css2?family=Cormorant+Garamond:wght@400;500;600;700&family=Libre+Baskerville:wght@400;700&family=Parisienne&display=swap'
);

/* ============================================================
   ROOT
============================================================ */

:root {{
    --page: {theme["page"]};
    --surface: {theme["surface"]};
    --surface2: {theme["surface2"]};
    --card: {theme["card"]};
    --text: {theme["text"]};
    --muted: {theme["muted"]};
    --accent: {theme["accent"]};
    --accent2: {theme["accent2"]};
    --line: {theme["line"]};
}}

html,
body,
.stApp {{
    background: var(--page) !important;
}}

.stApp {{
    color: var(--text) !important;

    background:
        radial-gradient(
            ellipse at 50% -8%,
            var(--surface2) 0%,
            var(--page) 55%
        ) !important;
}}

.block-container {{
    max-width: 1450px;
    padding-top: 0 !important;
    padding-bottom: 4rem !important;
}}

h1, h2, h3, h4, h5 {{
    font-family: "Cormorant Garamond", Georgia, serif !important;
    color: var(--text) !important;
}}

p,
label,
span {{
    color: var(--text);
}}

/* ============================================================
   WEEPING WILLOW HEADER
============================================================ */

.willow-header {{
    position: relative;
    width: 100%;
    height: 430px;
    overflow: hidden;
    margin: 0 auto 8px;
}}

.willow-art {{
    position: absolute;
    inset: 0;
    width: 100%;
    height: 100%;
    pointer-events: none;
}}

.willow-title {{
    position: absolute;
    z-index: 20;
    left: 50%;
    top: 175px;
    transform: translateX(-50%);
    width: 100%;
    text-align: center;

    font-family:
        "Cormorant Garamond",
        Georgia,
        serif;

    font-size: clamp(62px, 7.5vw, 96px);
    line-height: .82;
    font-weight: 600;
    letter-spacing: .01em;

    color: var(--text);

    text-shadow:
        0 3px 18px rgba(0,0,0,.45);
}}

.willow-title::before {{
    content: "❦";
    display: block;

    color: var(--accent);
    font-size: 28px;

    margin-bottom: 13px;
}}

.willow-title::after {{
    content: "❦";
    display: block;

    color: var(--accent);
    font-size: 23px;

    margin-top: 17px;
}}

/* ============================================================
   THEME SELECTOR
============================================================ */

.theme-wrap {{
    max-width: 430px;
    margin: 0 auto 30px;
    text-align: center;
}}

.theme-heading {{
    font-family:
        "Cormorant Garamond",
        Georgia,
        serif;

    font-size: 21px;
    font-weight: 600;

    margin-bottom: 8px;
    color: var(--text);
}}

div[data-baseweb="select"] > div {{
    background: var(--surface) !important;
    border: 1px solid var(--accent) !important;
    border-radius: 30px !important;
    min-height: 46px !important;

    box-shadow:
        0 6px 25px rgba(0,0,0,.22);
}}

div[data-baseweb="select"] span {{
    color: var(--text) !important;

    font-family:
        "Libre Baskerville",
        Georgia,
        serif !important;
}}

div[data-baseweb="select"] input {{
    color: var(--text) !important;
}}

div[role="listbox"] {{
    background: var(--surface) !important;
    border: 1px solid var(--accent) !important;
    border-radius: 14px !important;

    box-shadow:
        0 20px 50px rgba(0,0,0,.55) !important;
}}

div[role="option"] {{
    background: var(--surface) !important;
    color: var(--text) !important;
    padding: 12px 15px !important;
    border-radius: 8px !important;

    font-family:
        "Libre Baskerville",
        Georgia,
        serif !important;
}}

div[role="option"] * {{
    color: var(--text) !important;
}}

div[role="option"]:hover {{
    background: var(--surface2) !important;
}}

div[role="option"][aria-selected="true"] {{
    background: var(--card) !important;
}}

/* ============================================================
   STAT GARDEN
============================================================ */

.stats-garden {{
    position: relative;
    max-width: 1120px;

    margin: 0 auto 42px;
    padding: 15px 20px 30px;
}}

.stats-garden::before {{
    content: "";

    position: absolute;
    left: 5%;
    right: 5%;
    bottom: 0;

    height: 1px;

    background:
        linear-gradient(
            90deg,
            transparent,
            var(--accent2),
            var(--accent),
            var(--accent2),
            transparent
        );

    opacity: .7;
}}

.stats-garden::after {{
    content: "❦";

    position: absolute;
    left: 50%;
    bottom: -15px;

    transform: translateX(-50%);

    background: var(--page);
    padding: 0 14px;

    color: var(--accent);
    font-size: 22px;
}}

.stat-card {{
    position: relative;

    min-height: 115px;

    padding: 18px 10px 16px;

    text-align: center;

    background:
        linear-gradient(
            145deg,
            rgba(255,255,255,.06),
            rgba(0,0,0,.13)
        );

    border: 1px solid rgba(255,255,255,.12);

    border-radius:
        58% 42% 53% 47%
        /
        48% 54% 46% 52%;

    box-shadow:
        0 8px 24px rgba(0,0,0,.18);
}}

.stat-card::before {{
    content: "❧";

    position: absolute;
    left: 50%;
    top: -13px;

    transform:
        translateX(-50%)
        rotate(90deg);

    color: var(--accent2);
    font-size: 20px;
}}

.stat-card::after {{
    content: "";

    position: absolute;
    left: 23%;
    right: 23%;
    bottom: 9px;

    height: 1px;

    background:
        linear-gradient(
            90deg,
            transparent,
            var(--accent2),
            transparent
        );
}}

.stat-number {{
    font-family:
        "Cormorant Garamond",
        Georgia,
        serif;

    font-size: 46px;
    line-height: 1;
    font-weight: 600;

    color: var(--accent);
}}

.stat-label {{
    margin-top: 9px;

    color: var(--muted);

    font-family:
        "Libre Baskerville",
        Georgia,
        serif;

    font-size: 9px;
    text-transform: uppercase;
    letter-spacing: .18em;
}}

/* ============================================================
   TABS
============================================================ */

.stTabs {{
    margin-top: 8px;
}}

.stTabs [data-baseweb="tab-list"] {{
    justify-content: center;
    gap: 8px;

    background: transparent !important;

    border-bottom:
        1px solid var(--line) !important;
}}

.stTabs [data-baseweb="tab"] {{
    background: transparent !important;

    color: var(--muted) !important;

    border-radius:
        25px 25px 0 0 !important;

    padding:
        10px 22px !important;

    font-family:
        "Cormorant Garamond",
        Georgia,
        serif !important;

    font-size: 19px !important;
    font-weight: 600 !important;
}}

.stTabs [data-baseweb="tab"] p,
.stTabs [data-baseweb="tab"] span {{
    color: inherit !important;
}}

.stTabs [aria-selected="true"] {{
    color: var(--text) !important;
    background: var(--surface) !important;

    box-shadow:
        inset 0 -3px 0 var(--accent);
}}

/* ============================================================
   SEARCH
============================================================ */

div[data-baseweb="input"] > div {{
    background: var(--surface) !important;
    border: 1px solid var(--line) !important;
    border-radius: 25px !important;
}}

div[data-baseweb="input"] input {{
    color: var(--text) !important;
}}

div[data-baseweb="input"] input::placeholder {{
    color: var(--muted) !important;
    opacity: .75;
}}

/* ============================================================
   TREE AREA
============================================================ */

.tree-area {{
    position: relative;

    margin: 28px auto 22px;

    padding: 45px 28px 55px;

    min-height: 250px;

    overflow: hidden;

    background:
        radial-gradient(
            ellipse at 50% 0%,
            var(--surface2),
            var(--surface) 68%
        );

    border:
        1px solid rgba(255,255,255,.07);

    border-radius:
        45% 45% 22px 22px
        /
        35px 35px 22px 22px;

    box-shadow:
        inset 0 20px 60px rgba(0,0,0,.13),
        0 18px 45px rgba(0,0,0,.16);
}}

.tree-area::before {{
    content: "❧";

    position: absolute;
    left: 7%;
    top: 30px;

    color: var(--accent2);
    font-size: 48px;
    opacity: .18;

    transform: rotate(-25deg);
}}

.tree-area::after {{
    content: "❧";

    position: absolute;
    right: 7%;
    top: 30px;

    color: var(--accent2);
    font-size: 48px;
    opacity: .18;

    transform:
        scaleX(-1)
        rotate(-25deg);
}}

/* ============================================================
   ROOT
============================================================ */

.root-node {{
    position: relative;
    z-index: 5;

    width: min(360px, 85%);

    margin: 0 auto 48px;

    padding: 22px 28px 19px;

    text-align: center;

    background:
        linear-gradient(
            135deg,
            var(--accent),
            var(--line)
        );

    color: var(--page);

    border-radius:
        56% 44% 52% 48%
        /
        50% 45% 55% 50%;

    box-shadow:
        0 10px 35px rgba(0,0,0,.30);

    transform: rotate(-1deg);
}}

.root-node::before {{
    content: "❦";

    position: absolute;
    left: -31px;
    top: 18px;

    color: var(--accent2);
    font-size: 29px;

    transform: rotate(-25deg);
}}

.root-node::after {{
    content: "❦";

    position: absolute;
    right: -31px;
    bottom: 18px;

    color: var(--accent2);
    font-size: 29px;

    transform:
        scaleX(-1)
        rotate(-25deg);
}}

.root-node-title {{
    color: var(--page) !important;

    font-family:
        "Cormorant Garamond",
        Georgia,
        serif;

    font-size: 36px;
    font-weight: 700;
}}

.root-node-small {{
    color: var(--page) !important;

    font-family:
        "Libre Baskerville",
        Georgia,
        serif;

    font-size: 10px;
    letter-spacing: .06em;
    opacity: .82;
}}

/* ============================================================
   AUTHOR
============================================================ */

.author-info {{
    position: relative;

    margin: 18px 2% 8px;
    padding: 13px 22px;

    background:
        linear-gradient(
            90deg,
            var(--surface2),
            transparent
        );

    border-left:
        2px solid var(--accent2);

    border-radius:
        0 35px 35px 0;
}}

.author-info::before {{
    content: "❦";

    position: absolute;
    left: -28px;
    top: 4px;

    color: var(--accent2);
    font-size: 21px;
}}

.author-name {{
    font-family:
        "Cormorant Garamond",
        Georgia,
        serif;

    font-size: 29px;
    font-weight: 600;
    color: var(--text);
}}

.author-count {{
    color: var(--muted);

    font-family:
        "Libre Baskerville",
        Georgia,
        serif;

    font-size: 10px;
    margin-top: 1px;
}}

/* ============================================================
   SERIES
============================================================ */

.series-info {{
    position: relative;

    margin: 10px 6% 8px;
    padding: 10px 17px;

    background:
        rgba(0,0,0,.09);

    border-left:
        1px solid var(--accent2);

    border-radius:
        0 22px 22px 0;
}}

.series-info::before {{
    content: "❧";

    position: absolute;
    left: -28px;
    top: 2px;

    color: var(--accent2);
    font-size: 20px;
}}

.series-name {{
    font-family:
        "Cormorant Garamond",
        Georgia,
        serif;

    font-size: 24px;
    font-weight: 600;
    color: var(--text);
}}

.series-count {{
    color: var(--muted);
    font-size: 10px;
}}

/* ============================================================
   BOOKS
============================================================ */

.book-info {{
    position: relative;

    margin: 8px 11% 10px;
    padding: 11px 15px;

    background:
        linear-gradient(
            90deg,
            var(--card),
            rgba(0,0,0,.08)
        );

    border-left:
        1px solid var(--line);

    border-radius:
        0 16px 16px 0;

    box-shadow:
        0 4px 15px rgba(0,0,0,.10);
}}

.book-info::before {{
    content: "";

    position: absolute;
    left: -1px;
    top: 50%;

    width: 28px;
    height: 1px;

    background: var(--line);

    transform: translateX(-100%);
}}

.book-title {{
    font-family:
        "Cormorant Garamond",
        Georgia,
        serif;

    font-size: 22px;
    line-height: 1.05;
    font-weight: 600;
    color: var(--text);
}}

.book-meta {{
    color: var(--muted);

    font-family:
        "Libre Baskerville",
        Georgia,
        serif;

    font-size: 10px;
    margin-top: 5px;
}}

.book-cover {{
    width: 55px;
    height: 80px;

    object-fit: cover;

    border-radius: 5px;

    border:
        1px solid var(--accent);

    box-shadow:
        0 5px 12px rgba(0,0,0,.3);
}}

/* ============================================================
   BUTTONS
============================================================ */

.stButton > button {{
    background: transparent !important;
    color: var(--text) !important;

    border:
        1px solid transparent !important;

    border-radius: 30px !important;

    font-family:
        "Cormorant Garamond",
        Georgia,
        serif !important;

    font-size: 18px !important;
    font-weight: 600 !important;

    text-align: left !important;

    transition: all .2s ease;
}}

.stButton > button:hover {{
    background:
        var(--surface2) !important;

    border-color:
        var(--line) !important;

    color: var(--text) !important;

    transform:
        translateX(3px);
}}

.stButton > button:focus {{
    box-shadow:
        0 0 0 1px var(--accent) !important;
}}

/* ============================================================
   FORMS
============================================================ */

textarea {{
    background: var(--surface) !important;
    color: var(--text) !important;
    border-color: var(--line) !important;
}}

div[data-baseweb="textarea"] > div {{
    background: var(--surface) !important;
    border-color: var(--line) !important;
    border-radius: 14px !important;
}}

.stSelectbox > div > div {{
    background: var(--surface) !important;
}}

.stNumberInput > div > div {{
    background: var(--surface) !important;
}}

.stCheckbox label span,
.stRadio label span {{
    color: var(--text) !important;
}}

.stSlider [data-baseweb="slider"] {{
    color: var(--accent) !important;
}}

/* ============================================================
   TAB HEADINGS
============================================================ */

.tab-heading {{
    font-family:
        "Cormorant Garamond",
        Georgia,
        serif;

    color: var(--text);

    font-size: 35px;
    font-weight: 600;

    text-align: center;

    margin: 15px 0 20px;
}}

.tab-heading::after {{
    content: "❦";

    display: block;

    color: var(--accent);
    font-size: 19px;

    margin-top: 3px;
}}

/* ============================================================
   ALERTS
============================================================ */

div[data-testid="stAlert"] {{
    background: var(--surface) !important;
    border: 1px solid var(--line) !important;
    border-radius: 15px !important;
}}

div[data-testid="stAlert"] * {{
    color: var(--text) !important;
}}

/* ============================================================
   UPLOADER
============================================================ */

section[data-testid="stFileUploaderDropzone"] {{
    background: var(--surface) !important;
    border: 1px dashed var(--line) !important;
    border-radius: 18px !important;
}}

section[data-testid="stFileUploaderDropzone"] * {{
    color: var(--text) !important;
}}

/* ============================================================
   MOBILE
============================================================ */

@media (max-width: 700px) {{

    .willow-header {{
        height: 330px;
    }}

    .willow-title {{
        top: 140px;
        font-size: 58px;
    }}

    .stat-number {{
        font-size: 38px;
    }}

    .tree-area {{
        padding-left: 12px;
        padding-right: 12px;
    }}

    .author-info {{
        margin-left: 1%;
    }}

    .series-info {{
        margin-left: 5%;
    }}

    .book-info {{
        margin-left: 9%;
        margin-right: 3%;
    }}

    .stTabs [data-baseweb="tab"] {{
        padding: 8px 10px !important;
        font-size: 16px !important;
    }}
}}

</style>
"""
)

# ============================================================
# HEADER — ACTUAL WEEPING WILLOW SVG
# ============================================================

st.html(
    f"""
<div class="willow-header">

<svg
    class="willow-art"
    viewBox="0 0 1400 430"
    preserveAspectRatio="xMidYMid meet"
    xmlns="http://www.w3.org/2000/svg"
>

    <!-- SOFT CANOPY GLOW -->
    <defs>

        <radialGradient id="canopyGlow">
            <stop
                offset="0%"
                stop-color="{theme["accent2"]}"
                stop-opacity=".18"
            />
            <stop
                offset="100%"
                stop-color="{theme["accent2"]}"
                stop-opacity="0"
            />
        </radialGradient>

        <linearGradient
            id="trunkGradient"
            x1="0%"
            x2="100%"
        >
            <stop
                offset="0%"
                stop-color="{theme["line"]}"
                stop-opacity=".35"
            />
            <stop
                offset="45%"
                stop-color="{theme["accent2"]}"
                stop-opacity=".78"
            />
            <stop
                offset="100%"
                stop-color="{theme["line"]}"
                stop-opacity=".3"
            />
        </linearGradient>

        <linearGradient
            id="branchGradient"
            x1="0%"
            x2="100%"
        >
            <stop
                offset="0%"
                stop-color="{theme["accent2"]}"
                stop-opacity=".15"
            />
            <stop
                offset="50%"
                stop-color="{theme["accent2"]}"
                stop-opacity=".75"
            />
            <stop
                offset="100%"
                stop-color="{theme["accent2"]}"
                stop-opacity=".12"
            />
        </linearGradient>

    </defs>

    <!-- LARGE SOFT TREE CANOPY -->

    <ellipse
        cx="700"
        cy="85"
        rx="610"
        ry="175"
        fill="url(#canopyGlow)"
    />

    <!-- TRUNK -->

    <path
        d="
        M670 430
        C675 365 680 295 690 220
        C695 175 700 135 700 95
        C700 135 705 175 712 220
        C720 295 725 365 730 430
        Z
        "
        fill="url(#trunkGradient)"
    />

    <!-- CENTRAL TRUNK HIGHLIGHT -->

    <path
        d="
        M700 430
        C698 350 700 270 700 205
        C700 150 700 120 700 95
        "
        fill="none"
        stroke="{theme["accent2"]}"
        stroke-opacity=".45"
        stroke-width="3"
    />

    <!-- MAIN LEFT BRANCHES -->

    <path
        d="
        M700 145
        C625 115 535 92 430 78
        C330 65 245 72 135 105
        "
        fill="none"
        stroke="url(#branchGradient)"
        stroke-width="8"
        stroke-linecap="round"
    />

    <path
        d="
        M700 165
        C605 145 505 137 405 135
        C300 133 220 150 120 185
        "
        fill="none"
        stroke="url(#branchGradient)"
        stroke-width="5"
        stroke-linecap="round"
    />

    <path
        d="
        M700 190
        C600 180 515 188 420 215
        C315 245 230 260 125 250
        "
        fill="none"
        stroke="url(#branchGradient)"
        stroke-width="4"
        stroke-linecap="round"
    />

    <!-- MAIN RIGHT BRANCHES -->

    <path
        d="
        M700 145
        C775 115 865 92 970 78
        C1070 65 1155 72 1265 105
        "
        fill="none"
        stroke="url(#branchGradient)"
        stroke-width="8"
        stroke-linecap="round"
    />

    <path
        d="
        M700 165
        C795 145 895 137 995 135
        C1100 133 1180 150 1280 185
        "
        fill="none"
        stroke="url(#branchGradient)"
        stroke-width="5"
        stroke-linecap="round"
    />

    <path
        d="
        M700 190
        C800 180 885 188 980 215
        C1085 245 1170 260 1275 250
        "
        fill="none"
        stroke="url(#branchGradient)"
        stroke-width="4"
        stroke-linecap="round"
    />

    <!-- LEFT WEEPING BRANCHES -->

    <g
        fill="none"
        stroke="{theme["accent2"]}"
        stroke-opacity=".48"
        stroke-linecap="round"
    >

        <path
            d="M440 80 C370 125 355 190 365 285"
            stroke-width="3"
        />

        <path
            d="M365 90 C300 145 285 220 295 335"
            stroke-width="2"
        />

        <path
            d="M290 105 C235 170 225 245 235 310"
            stroke-width="3"
        />

        <path
            d="M220 120 C170 180 160 235 170 285"
            stroke-width="2"
        />

        <path
            d="M490 140 C445 190 435 255 445 330"
            stroke-width="2"
        />

        <path
            d="M545 150 C510 210 505 270 515 350"
            stroke-width="3"
        />

    </g>

    <!-- RIGHT WEEPING BRANCHES -->

    <g
        fill="none"
        stroke="{theme["accent2"]}"
        stroke-opacity=".48"
        stroke-linecap="round"
    >

        <path
            d="M960 80 C1030 125 1045 190 1035 285"
            stroke-width="3"
        />

        <path
            d="M1035 90 C1100 145 1115 220 1105 335"
            stroke-width="2"
        />

        <path
            d="M1110 105 C1165 170 1175 245 1165 310"
            stroke-width="3"
        />

        <path
            d="M1180 120 C1230 180 1240 235 1230 285"
            stroke-width="2"
        />

        <path
            d="M910 140 C955 190 965 255 955 330"
            stroke-width="2"
        />

        <path
            d="M855 150 C890 210 895 270 885 350"
            stroke-width="3"
        />

    </g>

    <!-- DELICATE LEAF CLUSTERS -->

    <g
        fill="{theme["accent2"]}"
        fill-opacity=".45"
    >

        <ellipse cx="150" cy="105" rx="10" ry="4" transform="rotate(-25 150 105)" />
        <ellipse cx="195" cy="145" rx="9" ry="4" transform="rotate(25 195 145)" />
        <ellipse cx="250" cy="105" rx="11" ry="4" transform="rotate(-30 250 105)" />
        <ellipse cx="315" cy="125" rx="10" ry="4" transform="rotate(20 315 125)" />
        <ellipse cx="380" cy="92" rx="12" ry="4" transform="rotate(-20 380 92)" />

        <ellipse cx="1250" cy="105" rx="10" ry="4" transform="rotate(25 1250 105)" />
        <ellipse cx="1205" cy="145" rx="9" ry="4" transform="rotate(-25 1205 145)" />
        <ellipse cx="1150" cy="105" rx="11" ry="4" transform="rotate(30 1150 105)" />
        <ellipse cx="1085" cy="125" rx="10" ry="4" transform="rotate(-20 1085 125)" />
        <ellipse cx="1020" cy="92" rx="12" ry="4" transform="rotate(20 1020 92)" />

        <ellipse cx="270" cy="205" rx="8" ry="3" transform="rotate(-25 270 205)" />
        <ellipse cx="1120" cy="205" rx="8" ry="3" transform="rotate(25 1120 205)" />

    </g>

    <!-- LITTLE GOLDEN BOOKISH STARS -->

    <g
        fill="{theme["accent"]}"
        opacity=".72"
    >

        <text x="185" y="82" font-size="16">✦</text>
        <text x="335" y="66" font-size="12">✧</text>
        <text x="1080" y="66" font-size="12">✧</text>
        <text x="1215" y="82" font-size="16">✦</text>

        <text x="255" y="285" font-size="13">✧</text>
        <text x="1145" y="285" font-size="13">✧</text>

    </g>

</svg>

<div class="willow-title">
    My Book Tree
</div>

</div>
"""
)

# ============================================================
# THEME PICKER
# ============================================================

st.html(
    """
    <div class="theme-wrap">
        <div class="theme-heading">
            Choose your bookish world
        </div>
    </div>
    """
)

theme_choice = st.selectbox(
    "Bookish theme",
    list(THEMES.keys()),
    index=list(THEMES.keys()).index(
        st.session_state.theme
    ),
    key="theme_selector",
    label_visibility="collapsed",
)

if theme_choice != st.session_state.theme:
    st.session_state.theme = theme_choice
    st.rerun()

# ============================================================
# COVER SEARCH
# ============================================================

@st.cache_data(show_spinner=False)
def get_cover(title, author="", isbn=""):

    isbn = re.sub(r"\D", "", str(isbn))

    if isbn:

        url = (
            "https://covers.openlibrary.org/b/isbn/"
            f"{isbn}-L.jpg"
        )

        try:

            response = requests.get(
                url,
                timeout=8
            )

            if (
                response.status_code == 200
                and len(response.content) > 1000
            ):
                return url

        except Exception:
            pass

    try:

        response = requests.get(
            "https://openlibrary.org/search.json",
            params={
                "title": title,
                "author": author,
                "limit": 1,
            },
            timeout=10,
        )

        if response.status_code == 200:

            docs = response.json().get(
                "docs",
                []
            )

            if docs:

                cover_id = docs[0].get("cover_i")

                if cover_id:

                    return (
                        "https://covers.openlibrary.org/"
                        f"b/id/{cover_id}-L.jpg"
                    )

    except Exception:
        pass

    try:

        response = requests.get(
            "https://www.googleapis.com/books/v1/volumes",
            params={
                "q": f"{title} {author}",
                "maxResults": 1,
            },
            timeout=10,
        )

        if response.status_code == 200:

            items = response.json().get(
                "items",
                []
            )

            if items:

                image = (
                    items[0]
                    .get("volumeInfo", {})
                    .get("imageLinks", {})
                    .get("thumbnail")
                )

                if image:

                    return image.replace(
                        "http://",
                        "https://"
                    )

    except Exception:
        pass

    return ""


# ============================================================
# SERIES HELPERS
# ============================================================

def detect_series(title):

    patterns = [
        r"\(([^()]*)#\s*\d+(?:\.\d+)?[^()]*\)",
        r"\[([^\[\]]*)#\s*\d+(?:\.\d+)?[^\[\]]*\]",
        r"\(([^()]*)\bBook\s+\d+(?:\.\d+)?[^()]*\)",
        r"\[([^\[\]]*)\bBook\s+\d+(?:\.\d+)?[^\[\]]*\]",
    ]

    for pattern in patterns:

        match = re.search(
            pattern,
            str(title),
            re.I
        )

        if match:

            series = match.group(1)

            series = re.sub(
                r",?\s*#\s*\d+(?:\.\d+)?",
                "",
                series,
                flags=re.I
            )

            series = re.sub(
                r"\bBook\s+\d+(?:\.\d+)?",
                "",
                series,
                flags=re.I
            )

            series = re.sub(
                r"\s+",
                " ",
                series
            ).strip(" ,-:")

            if series:
                return series

    return "Standalone"


def detect_series_number(title):

    patterns = [
        r"#\s*(\d+(?:\.\d+)?)",
        r"\bBook\s+(\d+(?:\.\d+)?)",
        r"\bVol(?:ume)?\.?\s+(\d+(?:\.\d+)?)",
    ]

    for pattern in patterns:

        match = re.search(
            pattern,
            str(title),
            re.I
        )

        if match:

            try:
                return float(match.group(1))
            except Exception:
                pass

    return None


def safe_id(text):

    return re.sub(
        r"[^a-zA-Z0-9_-]",
        "_",
        str(text)
    )


# ============================================================
# IMPORT
# ============================================================

def import_books(uploaded):

    try:

        df = pd.read_csv(
            uploaded,
            low_memory=False
        )

    except Exception:

        df = pd.read_csv(
            uploaded,
            encoding="latin-1",
            low_memory=False
        )

    columns = {
        str(c).strip().lower(): c
        for c in df.columns
    }

    def find_column(names):

        for name in names:

            if name.lower() in columns:
                return columns[name.lower()]

        return None

    title_col = find_column(
        ["title", "book title"]
    )

    author_col = find_column(
        ["author", "authors"]
    )

    isbn_col = find_column(
        ["isbn13", "isbn"]
    )

    rating_col = find_column(
        ["my rating", "rating"]
    )

    shelf_col = find_column(
        [
            "exclusive shelf",
            "shelf",
            "status"
        ]
    )

    if not title_col:

        st.error(
            "I couldn't find a Title column in this CSV."
        )

        return False

    books = []

    for _, row in df.iterrows():

        title = str(
            row.get(
                title_col,
                ""
            )
        ).strip()

        if not title or title.lower() == "nan":
            continue

        author = "Unknown Author"

        if author_col:

            author = str(
                row.get(
                    author_col,
                    ""
                )
            ).strip()

        if not author or author.lower() == "nan":
            author = "Unknown Author"

        isbn = ""

        if isbn_col:

            isbn = re.sub(
                r"\D",
                "",
                str(
                    row.get(
                        isbn_col,
                        ""
                    )
                )
            )

        rating = None

        if rating_col:

            try:
                rating = float(
                    row.get(
                        rating_col
                    )
                )
            except Exception:
                pass

        status = "Want to Read"

        if shelf_col:

            shelf = str(
                row.get(
                    shelf_col,
                    ""
                )
            ).lower()

            if "currently" in shelf:

                status = "Currently Reading"

            elif (
                "read" in shelf
                and "to-read" not in shelf
            ):

                status = "Read"

        books.append(
            {
                "Title": title,
                "Author": author,
                "Series": detect_series(title),
                "Series Number":
                    detect_series_number(title),
                "ISBN": isbn,
                "My Rating": rating,
                "Status": status,
                "Favorite": False,
                "Cover": "",
                "Description": "",
                "Publisher": "",
                "Pages": "",
                "Date Read": "",
            }
        )

    new_library = pd.DataFrame(books)

    if new_library.empty:

        st.error(
            "No books were found in the file."
        )

        return False

    progress = st.progress(0)

    for i in range(len(new_library)):

        new_library.loc[
            i,
            "Cover"
        ] = get_cover(
            new_library.loc[i, "Title"],
            new_library.loc[i, "Author"],
            new_library.loc[i, "ISBN"]
        )

        progress.progress(
            (i + 1) / len(new_library)
        )

    progress.empty()

    st.session_state.library = new_library
    st.session_state.open_authors = set()
    st.session_state.open_series = set()

    return True


# ============================================================
# DATA
# ============================================================

library = st.session_state.library

total = len(library)

authors = (
    library["Author"].nunique()
    if total
    else 0
)

series_count = (
    library[
        library["Series"] != "Standalone"
    ]["Series"].nunique()
    if total
    else 0
)

read_count = (
    len(
        library[
            library["Status"] == "Read"
        ]
    )
    if total
    else 0
)

favorites = (
    len(
        library[
            library["Favorite"] == True
        ]
    )
    if total
    else 0
)

# ============================================================
# STATS
# ============================================================

st.html(
    """
    <div class="stats-garden"></div>
    """
)

columns = st.columns(5)

stats = [
    (total, "Books"),
    (authors, "Authors"),
    (series_count, "Series"),
    (read_count, "Read"),
    (favorites, "Favorites"),
]

for col, (number, label) in zip(columns, stats):

    with col:

        st.html(
            f"""
            <div class="stat-card">

                <div class="stat-number">
                    {number}
                </div>

                <div class="stat-label">
                    {label}
                </div>

            </div>
            """
        )

# ============================================================
# TABS
# ============================================================

tree_tab, books_tab, add_tab, import_tab = st.tabs(
    [
        "🌿 Book Tree",
        "📚 Books",
        "✦ Add Book",
        "❧ Import",
    ]
)

# ============================================================
# TREE
# ============================================================

with tree_tab:

    if library.empty:

        st.info(
            "Your tree is empty. "
            "Import your library or add your first book."
        )

    else:

        search = st.text_input(
            "Search your tree",
            placeholder="Search author, series, or book...",
            label_visibility="collapsed",
        )

        filtered = library.copy()

        if search:

            q = search.lower()

            filtered = filtered[
                filtered["Title"]
                .fillna("")
                .astype(str)
                .str.lower()
                .str.contains(q, na=False)
                |
                filtered["Author"]
                .fillna("")
                .astype(str)
                .str.lower()
                .str.contains(q, na=False)
                |
                filtered["Series"]
                .fillna("")
                .astype(str)
                .str.lower()
                .str.contains(q, na=False)
            ]

        st.html(
            f"""
            <div class="tree-area">

                <div class="root-node">

                    <div class="root-node-title">
                        My Library
                    </div>

                    <div class="root-node-small">
                        {len(filtered)} books
                        ·
                        {filtered["Author"].nunique()} authors
                    </div>

                </div>

            </div>
            """
        )

        author_list = sorted(
            filtered["Author"]
            .fillna("Unknown Author")
            .astype(str)
            .unique(),
            key=lambda x: x.lower()
        )

        for author in author_list:

            author_id = safe_id(author)

            author_books = filtered[
                filtered["Author"]
                .fillna("Unknown Author")
                .astype(str)
                == author
            ]

            opened = (
                author_id
                in st.session_state.open_authors
            )

            arrow = "⌄" if opened else "›"

            if st.button(
                f"{arrow}  {author}",
                key=f"author_{author_id}",
                use_container_width=True,
            ):

                if opened:
                    st.session_state.open_authors.discard(
                        author_id
                    )
                else:
                    st.session_state.open_authors.add(
                        author_id
                    )

                st.rerun()

            st.html(
                f"""
                <div class="author-info">

                    <div class="author-name">
                        {html.escape(author)}
                    </div>

                    <div class="author-count">
                        {len(author_books)}
                        {"book" if len(author_books) == 1 else "books"}
                    </div>

                </div>
                """
            )

            if not opened:
                continue

            series_list = sorted(
                author_books["Series"]
                .fillna("Standalone")
                .astype(str)
                .unique(),
                key=lambda x: x.lower()
            )

            for series in series_list:

                if series == "Standalone":

                    standalone_books = author_books[
                        author_books["Series"]
                        .fillna("Standalone")
                        .astype(str)
                        == "Standalone"
                    ]

                    st.html(
                        f"""
                        <div class="series-info">

                            <div class="series-name">
                                Standalone Books
                            </div>

                            <div class="series-count">
                                {len(standalone_books)}
                                {"book" if len(standalone_books) == 1 else "books"}
                            </div>

                        </div>
                        """
                    )

                    for _, book in standalone_books.iterrows():

                        cover = str(
                            book.get("Cover", "") or ""
                        )

                        title = html.escape(
                            str(book.get("Title", ""))
                        )

                        status = html.escape(
                            str(book.get("Status", ""))
                        )

                        if cover:

                            st.html(
                                f"""
                                <div class="book-info">

                                    <div style="
                                        display:flex;
                                        gap:14px;
                                        align-items:center;
                                    ">

                                        <img
                                            class="book-cover"
                                            src="{html.escape(cover)}"
                                        >

                                        <div>

                                            <div class="book-title">
                                                {title}
                                            </div>

                                            <div class="book-meta">
                                                {status}
                                            </div>

                                        </div>

                                    </div>

                                </div>
                                """
                            )

                        else:

                            st.html(
                                f"""
                                <div class="book-info">

                                    <div class="book-title">
                                        {title}
                                    </div>

                                    <div class="book-meta">
                                        {status}
                                    </div>

                                </div>
                                """
                            )

                    continue

                series_id = (
                    author_id
                    + "::"
                    + safe_id(series)
                )

                series_open = (
                    series_id
                    in st.session_state.open_series
                )

                arrow = "⌄" if series_open else "›"

                if st.button(
                    f"{arrow}  {series}",
                    key=f"series_{series_id}",
                    use_container_width=True,
                ):

                    if series_open:
                        st.session_state.open_series.discard(
                            series_id
                        )
                    else:
                        st.session_state.open_series.add(
                            series_id
                        )

                    st.rerun()

                series_books = author_books[
                    author_books["Series"]
                    .fillna("Standalone")
                    .astype(str)
                    == series
                ].copy()

                st.html(
                    f"""
                    <div class="series-info">

                        <div class="series-name">
                            {html.escape(series)}
                        </div>

                        <div class="series-count">
                            {len(series_books)}
                            {"book" if len(series_books) == 1 else "books"}
                        </div>

                    </div>
                    """
                )

                if not series_open:
                    continue

                series_books = series_books.sort_values(
                    by=["Series Number", "Title"],
                    na_position="last"
                )

                for position, (_, book) in enumerate(
                    series_books.iterrows(),
                    1
                ):

                    number = book.get("Series Number")

                    if pd.notna(number):

                        try:

                            if float(number).is_integer():

                                number_text = (
                                    f"Book {int(number)}"
                                )

                            else:

                                number_text = (
                                    f"Book {number}"
                                )

                        except Exception:

                            number_text = f"Book {position}"

                    else:

                        number_text = f"Book {position}"

                    cover = str(
                        book.get("Cover", "") or ""
                    )

                    title = html.escape(
                        str(book.get("Title", ""))
                    )

                    status = html.escape(
                        str(book.get("Status", ""))
                    )

                    if cover:

                        st.html(
                            f"""
                            <div class="book-info">

                                <div style="
                                    display:flex;
                                    gap:14px;
                                    align-items:center;
                                ">

                                    <img
                                        class="book-cover"
                                        src="{html.escape(cover)}"
                                    >

                                    <div>

                                        <div class="book-title">
                                            {number_text}
                                            ·
                                            {title}
                                        </div>

                                        <div class="book-meta">
                                            {status}
                                        </div>

                                    </div>

                                </div>

                            </div>
                            """
                        )

                    else:

                        st.html(
                            f"""
                            <div class="book-info">

                                <div class="book-title">
                                    {number_text}
                                    ·
                                    {title}
                                </div>

                                <div class="book-meta">
                                    {status}
                                </div>

                            </div>
                            """
                        )

# ============================================================
# BOOKS
# ============================================================

with books_tab:

    st.html(
        """
        <div class="tab-heading">
            My Books
        </div>
        """
    )

    if library.empty:

        st.info("No books yet.")

    else:

        choice = st.radio(
            "Show",
            [
                "All",
                "Favorites",
                "Read",
                "Currently Reading",
                "Want to Read",
            ],
            horizontal=True,
            label_visibility="collapsed",
        )

        books = library.copy()

        if choice == "Favorites":

            books = books[
                books["Favorite"] == True
            ]

        elif choice != "All":

            books = books[
                books["Status"] == choice
            ]

        for index, book in books.iterrows():

            col1, col2, col3 = st.columns([1, 6, 1])

            with col1:

                if book.get("Cover"):

                    st.image(
                        book["Cover"],
                        width=70
                    )

            with col2:

                st.html(
                    f"""
                    <div class="book-title">
                        {html.escape(
                            str(book["Title"])
                        )}
                    </div>

                    <div class="book-meta">
                        {html.escape(
                            str(book["Author"])
                        )}
                        <br>
                        {html.escape(
                            str(book["Series"])
                        )}
                    </div>
                    """
                )

            with col3:

                favorite = st.checkbox(
                    "♥",
                    value=bool(
                        book.get("Favorite", False)
                    ),
                    key=f"fav_{index}",
                    label_visibility="collapsed",
                )

                if favorite != bool(
                    book.get("Favorite", False)
                ):

                    st.session_state.library.loc[
                        index,
                        "Favorite"
                    ] = favorite

                    st.rerun()

# ============================================================
# ADD BOOK
# ============================================================

with add_tab:

    st.html(
        """
        <div class="tab-heading">
            Add a Book
        </div>
        """
    )

    with st.form("add_book"):

        title = st.text_input("Title")

        author = st.text_input("Author")

        series = st.text_input(
            "Series",
            placeholder="Leave blank for standalone"
        )

        number = st.number_input(
            "Series number",
            min_value=0.0,
            value=0.0,
            step=0.5
        )

        isbn = st.text_input("ISBN")

        status = st.selectbox(
            "Status",
            [
                "Want to Read",
                "Currently Reading",
                "Read",
            ]
        )

        rating = st.slider(
            "Rating",
            0,
            5,
            0
        )

        favorite = st.checkbox("Favorite")

        submit = st.form_submit_button(
            "Add to My Tree"
        )

        if submit:

            if not title.strip():

                st.error("Please enter a title.")

            elif not author.strip():

                st.error("Please enter an author.")

            else:

                actual_series = (
                    series.strip()
                    if series.strip()
                    else "Standalone"
                )

                cover = get_cover(
                    title,
                    author,
                    isbn
                )

                new_book = {
                    "Title": title.strip(),
                    "Author": author.strip(),
                    "Series": actual_series,
                    "Series Number":
                        number if number else None,
                    "ISBN": re.sub(
                        r"\D",
                        "",
                        isbn
                    ),
                    "My Rating":
                        rating if rating else None,
                    "Status": status,
                    "Favorite": favorite,
                    "Cover": cover,
                    "Description": "",
                    "Publisher": "",
                    "Pages": "",
                    "Date Read": "",
                }

                st.session_state.library = pd.concat(
                    [
                        st.session_state.library,
                        pd.DataFrame([new_book]),
                    ],
                    ignore_index=True
                )

                st.success(
                    f'"{title}" was added to your tree!'
                )

                st.rerun()

# ============================================================
# IMPORT
# ============================================================

with import_tab:

    st.html(
        """
        <div class="tab-heading">
            Import Your Library
        </div>
        """
    )

    st.write(
        "Upload a Goodreads CSV, StoryGraph export, "
        "or another compatible book-list CSV."
    )

    uploaded = st.file_uploader(
        "Choose your CSV",
        type=["csv"]
    )

    if uploaded:

        if st.button("Build My Book Tree"):

            with st.spinner(
                "Finding your books and covers..."
            ):

                success = import_books(uploaded)

            if success:

                st.success(
                    "Your book tree is ready!"
                )

                st.rerun()
