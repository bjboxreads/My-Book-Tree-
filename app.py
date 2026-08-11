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

    "Enchanted Garden": {
        "page": "#101A15",
        "surface": "#18291F",
        "surface2": "#233B2C",
        "card": "#304D39",
        "text": "#FFF5DF",
        "muted": "#D2C7B2",
        "accent": "#D9B45A",
        "accent2": "#A9B97C",
        "line": "#8E6E36",
        "rose": "#C98A92",
    },

    "Moonlit Manor": {
        "page": "#111526",
        "surface": "#1A2038",
        "surface2": "#252E4C",
        "card": "#354061",
        "text": "#FFF6E7",
        "muted": "#D0CBD6",
        "accent": "#D8B86A",
        "accent2": "#AFA4D0",
        "line": "#776B99",
        "rose": "#C39AAE",
    },

    "Velvet Rose": {
        "page": "#1B0D16",
        "surface": "#2A121F",
        "surface2": "#421A2D",
        "card": "#5A2740",
        "text": "#FFF2E6",
        "muted": "#DEC5CA",
        "accent": "#D9AD62",
        "accent2": "#D28A9B",
        "line": "#9D5069",
        "rose": "#E1A5B1",
    },

    "Autumn Romance": {
        "page": "#21130D",
        "surface": "#332015",
        "surface2": "#4B2D1B",
        "card": "#684127",
        "text": "#FFF0D2",
        "muted": "#D9C3A4",
        "accent": "#D8A34D",
        "accent2": "#C97855",
        "line": "#96542F",
        "rose": "#B97767",
    },

    "Twilight Fairytale": {
        "page": "#160F22",
        "surface": "#211633",
        "surface2": "#30214A",
        "card": "#44305F",
        "text": "#FFF3E5",
        "muted": "#D5C9DC",
        "accent": "#D9B76B",
        "accent2": "#B59ACF",
        "line": "#765C92",
        "rose": "#C895B4",
    },

    "Secret Garden": {
        "page": "#092126",
        "surface": "#10363A",
        "surface2": "#174B4D",
        "card": "#226260",
        "text": "#FFF3DC",
        "muted": "#C9D9D0",
        "accent": "#E0B65B",
        "accent2": "#9AB58A",
        "line": "#5D8C80",
        "rose": "#D28D8D",
    },

    "Old World Library": {
        "page": "#191713",
        "surface": "#28231B",
        "surface2": "#3B3225",
        "card": "#544634",
        "text": "#F8E9C9",
        "muted": "#D2C3A6",
        "accent": "#D3A64F",
        "accent2": "#A79B70",
        "line": "#80633A",
        "rose": "#B67D79",
    },

    "Fairytale Blue": {
        "page": "#0E1725",
        "surface": "#17263A",
        "surface2": "#253A55",
        "card": "#355274",
        "text": "#FFF5E5",
        "muted": "#CBD3DF",
        "accent": "#E0BB68",
        "accent2": "#9DAED0",
        "line": "#667FA4",
        "rose": "#C99AAE",
    },

    "Victorian Romance": {
        "page": "#1D1013",
        "surface": "#32181D",
        "surface2": "#4B2229",
        "card": "#642F38",
        "text": "#FFF0DC",
        "muted": "#DCC5B7",
        "accent": "#D8B064",
        "accent2": "#C28C91",
        "line": "#8E4E57",
        "rose": "#D99BA2",
    },
}

# ============================================================
# SESSION STATE
# ============================================================

if (
    "theme" not in st.session_state
    or st.session_state.theme not in THEMES
):
    st.session_state.theme = "Enchanted Garden"

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

st.markdown(
    f"""
<style>

@import url('https://fonts.googleapis.com/css2?family=Berkshire+Swash&family=Cormorant+Garamond:ital,wght@0,400;0,500;0,600;0,700;1,400;1,500;1,600&family=Libre+Baskerville:wght@400;700&display=swap');

/* ==========================================================
   ROOT
========================================================== */

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
    --rose: {theme["rose"]};
}}

.stApp {{
    background:
        radial-gradient(
            ellipse at 50% -10%,
            var(--surface2) 0%,
            var(--page) 58%
        );
    color: var(--text);
}}

.block-container {{
    max-width: 1450px;
    padding-top: 1rem;
    padding-bottom: 4rem;
}}

#MainMenu {{
    visibility: hidden;
}}

footer {{
    visibility: hidden;
}}

/* ==========================================================
   GENERAL TYPOGRAPHY
========================================================== */

h1, h2, h3, h4 {{
    font-family:
        "Cormorant Garamond",
        Georgia,
        serif !important;
    color: var(--text) !important;
}}

p, label {{
    color: var(--text) !important;
}}

.stMarkdown,
.stTextInput,
.stSelectbox,
.stRadio,
.stFileUploader {{
    color: var(--text);
}}

/* ==========================================================
   HEADER
========================================================== */

.book-header {{
    text-align: center;
    padding: 25px 0 5px;
    position: relative;
}}

.book-header-title {{
    font-family:
        "Berkshire Swash",
        cursive !important;
    font-size: 76px;
    line-height: 1;
    font-weight: 400;
    color: #E7C979 !important;
    text-shadow:
        0 3px 12px rgba(0,0,0,.65),
        0 0 25px rgba(231,201,121,.12);
}}

.book-header-subtitle {{
    font-family:
        "Cormorant Garamond",
        Georgia,
        serif;
    color: var(--muted);
    margin-top: 12px;
    font-size: 18px;
    font-style: italic;
    letter-spacing: .08em;
}}

/* ==========================================================
   WILLOW TREE
========================================================== */

.willow-container {{
    width: 100%;
    height: 360px;
    margin: 0 auto 8px;
    display: flex;
    justify-content: center;
    align-items: center;
    overflow: hidden;
}}

.willow-tree {{
    width: 100%;
    max-width: 1200px;
    height: 360px;
    display: block;
}}

/* ==========================================================
   ORNAMENTAL DIVIDER
========================================================== */

.ornament {{
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 13px;
    margin: 4px auto 25px;
    color: var(--accent);
}}

.ornament-line {{
    height: 1px;
    width: 110px;
    background: linear-gradient(
        to right,
        transparent,
        var(--line)
    );
}}

.ornament-line.right {{
    background: linear-gradient(
        to left,
        transparent,
        var(--line)
    );
}}

.ornament-symbol {{
    font-size: 18px;
    color: var(--accent);
}}

/* ==========================================================
   THEME AREA
========================================================== */

.theme-panel {{
    max-width: 700px;
    margin: 0 auto 28px;
    text-align: center;
}}

.theme-heading {{
    font-family:
        "Cormorant Garamond",
        Georgia,
        serif;
    font-size: 25px;
    font-weight: 600;
    font-style: italic;
    color: var(--text);
    margin-bottom: 7px;
}}

.theme-caption {{
    color: var(--muted);
    font-family:
        "Libre Baskerville",
        Georgia,
        serif;
    font-size: 11px;
    letter-spacing: .05em;
    margin-bottom: 8px;
}}

/* ==========================================================
   SELECTOR
========================================================== */

div[data-baseweb="select"] > div {{
    background: var(--surface) !important;
    border: 1px solid var(--accent) !important;
    border-radius: 18px !important;
    min-height: 48px !important;
    box-shadow:
        0 5px 18px rgba(0,0,0,.2);
}}

div[data-baseweb="select"] span {{
    color: var(--text) !important;
}}

div[data-baseweb="select"] input {{
    color: var(--text) !important;
}}

div[role="listbox"] {{
    background: #171717 !important;
    border: 1px solid var(--accent) !important;
    border-radius: 14px !important;
    box-shadow:
        0 18px 45px rgba(0,0,0,.65) !important;
}}

div[role="option"] {{
    background: #171717 !important;
    color: #FFFFFF !important;
    padding: 12px 16px !important;
    border-radius: 8px !important;
    font-family:
        "Cormorant Garamond",
        Georgia,
        serif !important;
    font-size: 17px !important;
}}

div[role="option"] span {{
    color: #FFFFFF !important;
}}

div[role="option"]:hover {{
    background: #3A3A3A !important;
}}

div[role="option"][aria-selected="true"] {{
    background: #705323 !important;
}}

/* ==========================================================
   STAT BOOKPLATES
========================================================== */

.stats-wrap {{
    display: flex;
    justify-content: center;
    gap: 15px;
    margin: 10px auto 32px;
    flex-wrap: wrap;
}}

.stat-card {{
    min-width: 145px;
    background:
        linear-gradient(
            145deg,
            var(--surface2),
            var(--surface)
        );
    border: 1px solid var(--line);
    border-radius: 15px;
    padding: 15px 20px;
    text-align: center;
    box-shadow:
        0 7px 20px rgba(0,0,0,.16);
    position: relative;
}}

.stat-card::before,
.stat-card::after {{
    content: "✦";
    color: var(--accent);
    position: absolute;
    font-size: 9px;
    top: 8px;
}}

.stat-card::before {{
    left: 10px;
}}

.stat-card::after {{
    right: 10px;
}}

.stat-number {{
    font-family:
        "Cormorant Garamond",
        Georgia,
        serif;
    font-size: 35px;
    font-weight: 700;
    color: var(--accent);
    line-height: 1;
}}

.stat-label {{
    color: var(--muted);
    font-family:
        "Libre Baskerville",
        Georgia,
        serif;
    font-size: 9px;
    text-transform: uppercase;
    letter-spacing: .13em;
    margin-top: 5px;
}}

/* ==========================================================
   TABS
========================================================== */

button[data-baseweb="tab"] {{
    font-family:
        "Cormorant Garamond",
        Georgia,
        serif !important;
    font-size: 18px !important;
    color: var(--muted) !important;
}}

button[data-baseweb="tab"][aria-selected="true"] {{
    color: var(--accent) !important;
}}

div[data-baseweb="tab-highlight"] {{
    background: var(--accent) !important;
}}

/* ==========================================================
   TREE
========================================================== */

.tree-area {{
    margin-top: 10px;
    padding: 32px 30px 40px;
    background:
        linear-gradient(
            145deg,
            rgba(255,255,255,.025),
            rgba(0,0,0,.13)
        );
    border: 1px solid var(--line);
    border-radius: 22px;
    box-shadow:
        inset 0 0 35px rgba(0,0,0,.12);
}}

.root-node {{
    width: 330px;
    margin: 0 auto 40px;
    padding: 18px 25px;
    background:
        linear-gradient(
            135deg,
            var(--accent),
            #B88D42
        );
    color: {theme["page"]};
    border-radius: 60px;
    text-align: center;
    box-shadow:
        0 10px 30px rgba(0,0,0,.3);
}}

.root-node-title {{
    color: {theme["page"]};
    font-family:
        "Berkshire Swash",
        cursive;
    font-size: 30px;
}}

.root-node-small {{
    color: {theme["page"]};
    font-family:
        "Libre Baskerville",
        Georgia,
        serif;
    font-size: 10px;
    margin-top: 3px;
}}

/* ==========================================================
   TREE BUTTONS
========================================================== */

.stButton > button {{
    background: transparent !important;
    color: var(--text) !important;
    border: 0 !important;
    text-align: left !important;
    font-family:
        "Cormorant Garamond",
        Georgia,
        serif !important;
    font-size: 19px !important;
    font-weight: 600 !important;
    padding: 7px 12px !important;
}}

.stButton > button:hover {{
    background: rgba(255,255,255,.035) !important;
    color: var(--accent) !important;
    border: 0 !important;
}}

/* ==========================================================
   AUTHOR
========================================================== */

.author-info {{
    padding: 8px 18px 8px 20px;
    margin: -3px 0 3px 5px;
    border-left: 4px solid var(--accent);
    background:
        linear-gradient(
            to right,
            var(--surface),
            transparent
        );
    border-radius: 0 14px 14px 0;
}}

.author-name {{
    font-family:
        "Cormorant Garamond",
        Georgia,
        serif;
    font-size: 29px;
    font-weight: 700;
    color: var(--text);
}}

.author-count {{
    color: var(--muted);
    font-family:
        "Libre Baskerville",
        Georgia,
        serif;
    font-size: 10px;
    letter-spacing: .03em;
}}

/* ==========================================================
   SERIES
========================================================== */

.series-info {{
    margin-left: 58px;
    padding: 9px 16px;
    border-left: 3px solid var(--accent2);
    background:
        linear-gradient(
            to right,
            var(--surface2),
            transparent
        );
    border-radius: 0 12px 12px 0;
}}

.series-name {{
    font-family:
        "Cormorant Garamond",
        Georgia,
        serif;
    font-size: 24px;
    font-weight: 700;
}}

.series-count {{
    color: var(--muted);
    font-family:
        "Libre Baskerville",
        Georgia,
        serif;
    font-size: 10px;
}}

/* ==========================================================
   BOOKS
========================================================== */

.book-info {{
    margin-left: 110px;
    margin-top: 7px;
    padding: 10px 15px;
    background:
        linear-gradient(
            to right,
            var(--card),
            rgba(0,0,0,.05)
        );
    border-left: 2px solid var(--line);
    border-radius: 0 12px 12px 0;
}}

.book-title {{
    font-family:
        "Cormorant Garamond",
        Georgia,
        serif;
    font-size: 21px;
    font-weight: 700;
    color: var(--text);
}}

.book-meta {{
    color: var(--muted);
    font-family:
        "Libre Baskerville",
        Georgia,
        serif;
    font-size: 10px;
    margin-top: 3px;
}}

.book-cover {{
    width: 55px;
    height: 80px;
    object-fit: cover;
    border-radius: 5px;
    border: 1px solid var(--accent);
    box-shadow:
        0 4px 12px rgba(0,0,0,.3);
}}

/* ==========================================================
   INPUTS
========================================================== */

div[data-baseweb="input"] > div {{
    background: var(--surface) !important;
    border: 1px solid var(--line) !important;
    border-radius: 12px !important;
}}

div[data-baseweb="input"] input {{
    color: var(--text) !important;
}}

textarea {{
    background: var(--surface) !important;
    color: var(--text) !important;
    border-color: var(--line) !important;
}}

/* ==========================================================
   SEARCH
========================================================== */

.search-title {{
    font-family:
        "Cormorant Garamond",
        Georgia,
        serif;
    font-size: 25px;
    font-style: italic;
    color: var(--accent);
    margin-bottom: 5px;
}}

/* ==========================================================
   HEADERS
========================================================== */

.stSubheader,
.stHeader {{
    font-family:
        "Cormorant Garamond",
        Georgia,
        serif !important;
    color: var(--text) !important;
}}

/* ==========================================================
   FILE UPLOADER
========================================================== */

section[data-testid="stFileUploader"] {{
    background: var(--surface) !important;
    border: 1px dashed var(--line) !important;
    border-radius: 15px !important;
    padding: 10px !important;
}}

/* ==========================================================
   CHECKBOX / RADIO
========================================================== */

.stCheckbox label,
.stRadio label {{
    color: var(--text) !important;
    font-family:
        "Cormorant Garamond",
        Georgia,
        serif !important;
    font-size: 17px !important;
}}

</style>
""",
    unsafe_allow_html=True,
)

# ============================================================
# HEADER + WILLOW
# ============================================================

st.html(
    f"""
<div class="book-header">

    <div class="book-header-title">
        My Book Tree
    </div>

    <div class="book-header-subtitle">
        where every story has a branch
    </div>

</div>

<div class="willow-container">

<svg class="willow-tree"
     viewBox="0 0 1200 360"
     xmlns="http://www.w3.org/2000/svg">

    <!-- TRUNK -->

    <path
        d="M600 360
           C580 300 580 235 590 175
           C595 135 605 95 620 55"
        fill="none"
        stroke="#493128"
        stroke-width="30"
        stroke-linecap="round"
    />

    <path
        d="M607 350
           C595 290 595 235 603 180
           C608 135 617 95 625 58"
        fill="none"
        stroke="#775447"
        stroke-width="7"
        stroke-linecap="round"
    />

    <!-- LEFT MAIN BRANCHES -->

    <g fill="none"
       stroke="#493128"
       stroke-linecap="round">

        <path
            d="M598 185
               C530 145 460 105 365 85"
            stroke-width="13"
        />

        <path
            d="M590 215
               C510 185 430 175 330 180"
            stroke-width="10"
        />

        <path
            d="M600 150
               C550 110 510 65 485 20"
            stroke-width="9"
        />

        <path
            d="M575 175
               C515 130 475 110 420 100"
            stroke-width="7"
        />

    </g>

    <!-- RIGHT MAIN BRANCHES -->

    <g fill="none"
       stroke="#493128"
       stroke-linecap="round">

        <path
            d="M615 180
               C685 140 755 105 845 85"
            stroke-width="13"
        />

        <path
            d="M620 210
               C700 180 780 175 870 180"
            stroke-width="10"
        />

        <path
            d="M625 145
               C680 105 715 60 740 18"
            stroke-width="9"
        />

        <path
            d="M645 175
               C705 130 750 105 800 98"
            stroke-width="7"
        />

    </g>

    <!-- LEFT WEEPING BRANCHES -->

    <g fill="none"
       stroke="#71805D"
       stroke-width="4"
       stroke-linecap="round">

        <path d="M365 85 C350 140 355 205 375 275"/>
        <path d="M400 92 C385 155 390 225 410 305"/>
        <path d="M440 105 C425 165 430 235 450 320"/>
        <path d="M480 115 C465 175 470 235 490 300"/>
        <path d="M520 135 C505 190 510 245 525 285"/>
        <path d="M330 180 C315 225 320 270 335 315"/>

    </g>

    <!-- RIGHT WEEPING BRANCHES -->

    <g fill="none"
       stroke="#71805D"
       stroke-width="4"
       stroke-linecap="round">

        <path d="M845 85 C860 140 855 205 835 275"/>
        <path d="M810 92 C825 155 820 225 800 305"/>
        <path d="M770 105 C785 165 780 235 760 320"/>
        <path d="M730 115 C745 175 740 235 720 300"/>
        <path d="M690 135 C705 190 700 245 685 285"/>
        <path d="M870 180 C885 225 880 270 865 315"/>

    </g>

    <!-- LEAVES -->

    <g fill="#7E9167">

        <ellipse cx="350" cy="140" rx="7" ry="20"
                 transform="rotate(-18 350 140)"/>

        <ellipse cx="375" cy="185" rx="7" ry="21"
                 transform="rotate(15 375 185)"/>

        <ellipse cx="390" cy="235" rx="7" ry="22"
                 transform="rotate(-15 390 235)"/>

        <ellipse cx="410" cy="270" rx="7" ry="21"
                 transform="rotate(15 410 270)"/>

        <ellipse cx="430" cy="150" rx="7" ry="20"
                 transform="rotate(-18 430 150)"/>

        <ellipse cx="450" cy="210" rx="7" ry="22"
                 transform="rotate(15 450 210)"/>

        <ellipse cx="475" cy="265" rx="7" ry="21"
                 transform="rotate(-15 475 265)"/>

        <ellipse cx="510" cy="190" rx="7" ry="21"
                 transform="rotate(15 510 190)"/>

        <ellipse cx="530" cy="245" rx="7" ry="20"
                 transform="rotate(-15 530 245)"/>

        <ellipse cx="330" cy="235" rx="7" ry="20"
                 transform="rotate(-15 330 235)"/>

        <ellipse cx="335" cy="285" rx="7" ry="21"
                 transform="rotate(15 335 285)"/>

        <ellipse cx="850" cy="140" rx="7" ry="20"
                 transform="rotate(18 850 140)"/>

        <ellipse cx="825" cy="185" rx="7" ry="21"
                 transform="rotate(-15 825 185)"/>

        <ellipse cx="810" cy="235" rx="7" ry="22"
                 transform="rotate(15 810 235)"/>

        <ellipse cx="790" cy="270" rx="7" ry="21"
                 transform="rotate(-15 790 270)"/>

        <ellipse cx="770" cy="150" rx="7" ry="20"
                 transform="rotate(18 770 150)"/>

        <ellipse cx="750" cy="210" rx="7" ry="22"
                 transform="rotate(-15 750 210)"/>

        <ellipse cx="725" cy="265" rx="7" ry="21"
                 transform="rotate(15 725 265)"/>

        <ellipse cx="690" cy="190" rx="7" ry="21"
                 transform="rotate(-15 690 190)"/>

        <ellipse cx="670" cy="245" rx="7" ry="20"
                 transform="rotate(15 670 245)"/>

        <ellipse cx="870" cy="235" rx="7" ry="20"
                 transform="rotate(15 870 235)"/>

        <ellipse cx="865" cy="285" rx="7" ry="21"
                 transform="rotate(-15 865 285)"/>

    </g>

    <!-- SMALL ROSE BLOSSOMS -->

    <g fill="#C98A92">

        <circle cx="405" cy="120" r="4"/>
        <circle cx="455" cy="165" r="4"/>
        <circle cx="500" cy="205" r="4"/>

        <circle cx="795" cy="120" r="4"/>
        <circle cx="745" cy="165" r="4"/>
        <circle cx="700" cy="205" r="4"/>

    </g>

</svg>

</div>

<div class="ornament">
    <div class="ornament-line"></div>
    <div class="ornament-symbol">❦</div>
    <div class="ornament-line right"></div>
</div>
"""
)

# ============================================================
# THEME PICKER
# ============================================================

st.html(
    """
    <div class="theme-panel">
        <div class="theme-heading">
            Choose the mood of your library
        </div>
        <div class="theme-caption">
            Change the colors and atmosphere of your book tree
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

    if isbn:

        url = (
            "https://covers.openlibrary.org/b/isbn/"
            f"{isbn}-L.jpg"
        )

        try:

            r = requests.get(
                url,
                timeout=8
            )

            if (
                r.status_code == 200
                and len(r.content) > 1000
            ):
                return url

        except Exception:
            pass

    try:

        r = requests.get(
            "https://openlibrary.org/search.json",
            params={
                "title": title,
                "author": author,
                "limit": 1,
            },
            timeout=10,
        )

        if r.status_code == 200:

            docs = r.json().get(
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

    try:

        r = requests.get(
            "https://www.googleapis.com/books/v1/volumes",
            params={
                "q": f"{title} {author}",
                "maxResults": 1,
            },
            timeout=10,
        )

        if r.status_code == 200:

            items = r.json().get(
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

        if not title or title == "nan":
            continue

        author = "Unknown Author"

        if author_col:

            author = str(
                row.get(
                    author_col,
                    ""
                )
            ).strip()

        if not author or author == "nan":
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

    for i in range(
        len(new_library)
    ):

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
    '<div class="stats-wrap">'
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

st.html(
    "</div>"
)

# ============================================================
# TABS
# ============================================================

tree_tab, books_tab, add_tab, import_tab = st.tabs(
    [
        "🌿 My Book Tree",
        "📖 My Books",
        "✦ Add a Book",
        "❧ Import Library",
    ]
)

# ============================================================
# TREE
# ============================================================

with tree_tab:

    if library.empty:

        st.info(
            "Your tree is waiting for its first story. "
            "Import your library or add your first book."
        )

    else:

        st.html(
            """
            <div class="search-title">
                Find a story in your tree
            </div>
            """
        )

        search = st.text_input(
            "Search your tree",
            placeholder="Search by author, series, or book title...",
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

            arrow = "▼" if opened else "▶"

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
                                Standalone Stories
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
                    "▼"
                    if series_open
                    else "▶"
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

    if library.empty:

        st.info(
            "No books yet."
        )

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

        if books.empty:

            st.info(
                "Nothing here yet."
            )

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

    st.header(
        "Add a Book"
    )

    with st.form(
        "add_book"
    ):

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
            step=.5
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

    st.header(
        "Bring Your Books Into the Tree"
    )

    st.write(
        "Upload your Goodreads CSV, StoryGraph export, "
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
