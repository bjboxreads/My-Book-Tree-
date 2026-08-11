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
    'https://fonts.googleapis.com/css2?family=Cormorant+Garamond:wght@400;500;600;700&family=Libre+Baskerville:wght@400;700&display=swap'
);

/* =========================================================
   ROOT
========================================================= */

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
            ellipse at 50% -10%,
            var(--surface2) 0%,
            var(--page) 52%
        ) !important;
}}

.block-container {{
    max-width: 1450px;
    padding-top: 1rem !important;
    padding-bottom: 4rem !important;
}}

h1, h2, h3, h4, h5 {{
    font-family:
        "Cormorant Garamond",
        Georgia,
        serif !important;
    color: var(--text) !important;
}}

p,
label,
span {{
    color: var(--text);
}}

/* =========================================================
   HEADER
========================================================= */

.willow-header {{
    position: relative;
    text-align: center;
    padding: 35px 0 20px;
    min-height: 180px;
    overflow: hidden;
}}

.willow-header::before {{
    content: "";
    position: absolute;
    left: 50%;
    top: 0;
    width: 4px;
    height: 170px;
    transform: translateX(-50%);
    background:
        linear-gradient(
            to bottom,
            transparent,
            var(--line) 15%,
            var(--line) 100%
        );
    opacity: .65;
}}

.willow-header::after {{
    content: "";
    position: absolute;
    left: 50%;
    top: 0;
    width: 650px;
    height: 145px;
    transform: translateX(-50%);
    border-radius: 50%;
    border-top: 2px solid var(--accent2);
    opacity: .28;
    box-shadow:
        -210px 20px 0 -48px var(--accent2),
        210px 20px 0 -48px var(--accent2),
        -280px 55px 0 -55px var(--accent2),
        280px 55px 0 -55px var(--accent2);
}}

.header-leaves {{
    position: absolute;
    width: 100%;
    height: 100%;
    left: 0;
    top: 0;
    pointer-events: none;
}}

.header-leaves::before,
.header-leaves::after {{
    content: "❧";
    position: absolute;
    color: var(--accent2);
    font-size: 38px;
    opacity: .45;
}}

.header-leaves::before {{
    left: 16%;
    top: 42px;
    transform: rotate(-25deg);
}}

.header-leaves::after {{
    right: 16%;
    top: 42px;
    transform: scaleX(-1) rotate(-25deg);
}}

.book-title {{
    position: relative;
    z-index: 5;
    font-family:
        "Cormorant Garamond",
        Georgia,
        serif;
    font-size: clamp(58px, 7vw, 88px);
    line-height: .85;
    font-weight: 600;
    letter-spacing: .01em;
    color: var(--text);
    text-shadow:
        0 3px 20px rgba(0,0,0,.35);
}}

.book-title::before {{
    content: "❦";
    display: block;
    font-size: 28px;
    line-height: 1;
    color: var(--accent);
    margin-bottom: 10px;
}}

.book-title::after {{
    content: "❦";
    display: block;
    font-size: 24px;
    line-height: 1;
    color: var(--accent);
    margin-top: 14px;
    transform: rotate(180deg);
}}

/* =========================================================
   THEME PICKER
========================================================= */

.theme-wrap {{
    max-width: 430px;
    margin: 8px auto 26px;
    text-align: center;
}}

.theme-heading {{
    font-family:
        "Cormorant Garamond",
        Georgia,
        serif;
    font-size: 22px;
    font-weight: 600;
    color: var(--text);
    margin-bottom: 8px;
}}

div[data-baseweb="select"] > div {{
    background: var(--surface) !important;
    border: 1px solid var(--accent) !important;
    border-radius: 30px !important;
    min-height: 46px !important;
    box-shadow:
        0 4px 20px rgba(0,0,0,.18);
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
    overflow: hidden;
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

/* =========================================================
   ORNAMENTAL STAT AREA
========================================================= */

.stats-garden {{
    position: relative;
    margin: 15px auto 34px;
    padding: 15px 10px 28px;
    max-width: 1100px;
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
            var(--line),
            var(--accent),
            var(--line),
            transparent
        );
}}

.stats-garden::after {{
    content: "❦";
    position: absolute;
    bottom: -15px;
    left: 50%;
    transform: translateX(-50%);
    padding: 0 12px;
    background: var(--page);
    color: var(--accent);
    font-size: 23px;
}}

.stat-card {{
    position: relative;
    text-align: center;
    padding: 13px 10px 8px;
    min-height: 100px;
    background:
        linear-gradient(
            145deg,
            rgba(255,255,255,.035),
            rgba(0,0,0,.10)
        );
    border: none;
    border-radius: 50% 50% 44% 44%;
}}

.stat-card::before {{
    content: "";
    position: absolute;
    left: 50%;
    top: -7px;
    width: 50px;
    height: 1px;
    transform: translateX(-50%);
    background: var(--accent2);
}}

.stat-card::after {{
    content: "✦";
    position: absolute;
    top: -18px;
    left: 50%;
    transform: translateX(-50%);
    color: var(--accent);
    font-size: 14px;
}}

.stat-number {{
    font-family:
        "Cormorant Garamond",
        Georgia,
        serif;
    font-size: 45px;
    line-height: 1;
    font-weight: 600;
    color: var(--accent);
    text-shadow:
        0 2px 12px rgba(0,0,0,.25);
}}

.stat-label {{
    margin-top: 8px;
    color: var(--muted);
    font-family:
        "Libre Baskerville",
        Georgia,
        serif;
    font-size: 9px;
    text-transform: uppercase;
    letter-spacing: .18em;
}}

/* =========================================================
   TABS
========================================================= */

.stTabs {{
    margin-top: 8px;
}}

.stTabs [data-baseweb="tab-list"] {{
    justify-content: center;
    gap: 8px;
    background: transparent !important;
    border-bottom: 1px solid var(--line) !important;
}}

.stTabs [data-baseweb="tab"] {{
    background: transparent !important;
    color: var(--muted) !important;
    border-radius: 25px 25px 0 0 !important;
    padding: 10px 22px !important;
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

/* =========================================================
   SEARCH
========================================================= */

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

/* =========================================================
   WILLOW TREE
========================================================= */

.tree-area {{
    position: relative;
    margin: 28px auto 20px;
    padding: 45px 28px 55px;
    min-height: 250px;
    overflow: hidden;
    background:
        radial-gradient(
            ellipse at 50% 0%,
            var(--surface2),
            var(--surface) 65%
        );
    border: 1px solid rgba(255,255,255,.05);
    border-radius: 45% 45% 20px 20px / 30px 30px 20px 20px;
    box-shadow:
        inset 0 20px 60px rgba(0,0,0,.12),
        0 18px 45px rgba(0,0,0,.16);
}}

.tree-area::before {{
    content: "";
    position: absolute;
    left: 50%;
    top: 0;
    width: 14px;
    height: 100%;
    transform: translateX(-50%);
    background:
        linear-gradient(
            90deg,
            transparent,
            var(--line),
            var(--accent2),
            var(--line),
            transparent
        );
    opacity: .16;
    border-radius: 50%;
}}

.tree-area::after {{
    content: "";
    position: absolute;
    left: 50%;
    top: 15px;
    width: 80%;
    height: 100px;
    transform: translateX(-50%);
    border-top: 1px solid var(--accent2);
    border-radius: 50%;
    opacity: .22;
}}

/* =========================================================
   ROOT
========================================================= */

.root-node {{
    position: relative;
    z-index: 2;
    width: min(350px, 85%);
    margin: 0 auto 50px;
    padding: 22px 28px 19px;
    text-align: center;
    background:
        linear-gradient(
            135deg,
            var(--accent),
            var(--line)
        );
    color: var(--page);
    border-radius: 60% 40% 55% 45% / 55% 45% 55% 45%;
    box-shadow:
        0 10px 35px rgba(0,0,0,.28);
    transform: rotate(-1deg);
}}

.root-node::before {{
    content: "❦";
    position: absolute;
    left: -28px;
    top: 20px;
    color: var(--accent2);
    font-size: 30px;
    transform: rotate(-25deg);
}}

.root-node::after {{
    content: "❦";
    position: absolute;
    right: -28px;
    bottom: 18px;
    color: var(--accent2);
    font-size: 30px;
    transform: scaleX(-1) rotate(-25deg);
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

/* =========================================================
   AUTHOR BRANCHES
========================================================= */

.author-info {{
    position: relative;
    margin: 18px 2% 8px;
    padding: 13px 22px;
    background:
        linear-gradient(
            90deg,
            var(--surface2),
            rgba(0,0,0,0)
        );
    border: none;
    border-left: 2px solid var(--accent2);
    border-radius: 0 35px 35px 0;
}}

.author-info::before {{
    content: "";
    position: absolute;
    left: -2px;
    top: -13px;
    width: 55px;
    height: 25px;
    border-left: 2px solid var(--accent2);
    border-top: 1px solid var(--accent2);
    border-radius: 50%;
    opacity: .55;
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

/* =========================================================
   SERIES
========================================================= */

.series-info {{
    position: relative;
    margin: 10px 6% 8px;
    padding: 10px 17px;
    background: rgba(0,0,0,.09);
    border-left: 1px solid var(--accent2);
    border-radius: 0 22px 22px 0;
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

/* =========================================================
   BOOKS
========================================================= */

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
    border-left: 1px solid var(--line);
    border-radius: 0 16px 16px 0;
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
    border: 1px solid var(--accent);
    box-shadow:
        0 5px 12px rgba(0,0,0,.3);
}}

/* =========================================================
   BUTTONS
========================================================= */

.stButton > button {{
    background: transparent !important;
    color: var(--text) !important;
    border: 1px solid transparent !important;
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
    background: var(--surface2) !important;
    border-color: var(--line) !important;
    color: var(--text) !important;
    transform: translateX(3px);
}}

.stButton > button:focus {{
    box-shadow:
        0 0 0 1px var(--accent) !important;
}}

/* =========================================================
   FORM ELEMENTS
========================================================= */

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

.stSlider [data-baseweb="slider"] {{
    color: var(--accent) !important;
}}

.stCheckbox label span {{
    color: var(--text) !important;
}}

.stRadio label span {{
    color: var(--text) !important;
}}

/* =========================================================
   HEADINGS INSIDE TABS
========================================================= */

.tab-heading {{
    font-family:
        "Cormorant Garamond",
        Georgia,
        serif;
    color: var(--text);
    font-size: 34px;
    font-weight: 600;
    text-align: center;
    margin: 15px 0 20px;
}}

.tab-heading::after {{
    content: "  ❦  ";
    display: block;
    color: var(--accent);
    font-size: 19px;
    margin-top: 3px;
}}

/* =========================================================
   INFO / SUCCESS
========================================================= */

div[data-testid="stAlert"] {{
    background: var(--surface) !important;
    border: 1px solid var(--line) !important;
    border-radius: 15px !important;
}}

div[data-testid="stAlert"] * {{
    color: var(--text) !important;
}}

/* =========================================================
   FILE UPLOADER
========================================================= */

section[data-testid="stFileUploaderDropzone"] {{
    background: var(--surface) !important;
    border: 1px dashed var(--line) !important;
    border-radius: 18px !important;
}}

section[data-testid="stFileUploaderDropzone"] * {{
    color: var(--text) !important;
}}

/* =========================================================
   PROGRESS
========================================================= */

div[data-testid="stProgressBar"] > div > div {{
    background: var(--accent) !important;
}}

/* =========================================================
   MOBILE
========================================================= */

@media (max-width: 700px) {{

    .book-title {{
        font-size: 55px;
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
# HEADER
# ============================================================

st.html(
    """
    <div class="willow-header">

        <div class="header-leaves"></div>

        <div class="book-title">
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

    isbn = re.sub(
        r"\D",
        "",
        str(isbn)
    )

    # --------------------------------------------------------
    # ISBN
    # --------------------------------------------------------

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

    # --------------------------------------------------------
    # OPEN LIBRARY
    # --------------------------------------------------------

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

                cover_id = docs[0].get(
                    "cover_i"
                )

                if cover_id:

                    return (
                        "https://covers.openlibrary.org/"
                        f"b/id/{cover_id}-L.jpg"
                    )

    except Exception:
        pass

    # --------------------------------------------------------
    # GOOGLE BOOKS
    # --------------------------------------------------------

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

        r"\(([^()]*?)#\s*\d+(?:\.\d+)?[^()]*\)",
        r"\[([^\[\]]*?)#\s*\d+(?:\.\d+)?[^\[\]]*\]",

        r"\(([^()]*?)\bBook\s+\d+(?:\.\d+)?[^()]*\)",
        r"\[([^\[\]]*?)\bBook\s+\d+(?:\.\d+)?[^\[\]]*\]",
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
                return float(
                    match.group(1)
                )

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

    new_library = pd.DataFrame(
        books
    )

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
    <div class="stats-garden">
    </div>
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

for col, (number, label) in zip(
    columns,
    stats
):

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
            placeholder=(
                "Search author, series, or book..."
            ),
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

                # ------------------------------------------------
                # STANDALONE
                # ------------------------------------------------

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
                            book.get(
                                "Cover",
                                ""
                            ) or ""
                        )

                        title = html.escape(
                            str(
                                book.get(
                                    "Title",
                                    ""
                                )
                            )
                        )

                        status = html.escape(
                            str(
                                book.get(
                                    "Status",
                                    ""
                                )
                            )
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

                # ------------------------------------------------
                # SERIES
                # ------------------------------------------------

                series_id = (
                    author_id
                    + "::"
                    + safe_id(series)
                )

                series_open = (
                    series_id
                    in st.session_state.open_series
                )

                arrow = (
                    "⌄"
                    if series_open
                    else "›"
                )

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
                    by=[
                        "Series Number",
                        "Title"
                    ],
                    na_position="last"
                )

                for position, (_, book) in enumerate(
                    series_books.iterrows(),
                    1
                ):

                    number = book.get(
                        "Series Number"
                    )

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

                            number_text = (
                                f"Book {position}"
                            )

                    else:

                        number_text = (
                            f"Book {position}"
                        )

                    cover = str(
                        book.get(
                            "Cover",
                            ""
                        ) or ""
                    )

                    title = html.escape(
                        str(
                            book.get(
                                "Title",
                                ""
                            )
                        )
                    )

                    status = html.escape(
                        str(
                            book.get(
                                "Status",
                                ""
                            )
                        )
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

            col1, col2, col3 = st.columns(
                [1, 6, 1]
            )

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
                            str(
                                book["Title"]
                            )
                        )}
                    </div>

                    <div class="book-meta">
                        {html.escape(
                            str(
                                book["Author"]
                            )
                        )}
                        <br>
                        {html.escape(
                            str(
                                book["Series"]
                            )
                        )}
                    </div>
                    """
                )

            with col3:

                favorite = st.checkbox(
                    "♥",
                    value=bool(
                        book.get(
                            "Favorite",
                            False
                        )
                    ),
                    key=f"fav_{index}",
                    label_visibility="collapsed",
                )

                if favorite != bool(
                    book.get(
                        "Favorite",
                        False
                    )
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

        title = st.text_input(
            "Title"
        )

        author = st.text_input(
            "Author"
        )

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

        isbn = st.text_input(
            "ISBN"
        )

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

        favorite = st.checkbox(
            "Favorite"
        )

        submit = st.form_submit_button(
            "Add to My Tree"
        )

        if submit:

            if not title.strip():

                st.error(
                    "Please enter a title."
                )

            elif not author.strip():

                st.error(
                    "Please enter an author."
                )

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
                        number
                        if number
                        else None,
                    "ISBN": re.sub(
                        r"\D",
                        "",
                        isbn
                    ),
                    "My Rating":
                        rating
                        if rating
                        else None,
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
                        pd.DataFrame(
                            [new_book]
                        ),
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

        if st.button(
            "Build My Book Tree"
        ):

            with st.spinner(
                "Finding your books and covers..."
            ):

                success = import_books(
                    uploaded
                )

            if success:

                st.success(
                    "Your book tree is ready!"
                )

                st.rerun()
