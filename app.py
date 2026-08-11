```python
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
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="collapsed",
)


# ============================================================
# BOOKISH THEMES
# ============================================================

THEMES = {
    "Enchanted Library": {
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
    "Midnight & Gold": {
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
    "Victorian Rose": {
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
    "Autumn Manor": {
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
    "Moonlit Library": {
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
    "Secret Garden": {
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
    "Old World Library": {
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
    "Spellbound": {
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
    "Velvet & Crimson": {
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
    st.session_state.theme = "Enchanted Library"

if "library" not in st.session_state:
    st.session_state.library = pd.DataFrame(
        columns=[
            "Title",
            "Author",
            "Series",
            "Series Number",
            "ISBN",
            "Genre",
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

theme = THEMES[st.session_state.theme]


# ============================================================
# CSS
# ============================================================

st.html(
    f"""
    <style>

    @import url(
        'https://fonts.googleapis.com/css2?family=Berkshire+Swash&family=Libre+Baskerville:wght@400;700&display=swap'
    );

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

    .stApp {{
        background:
            radial-gradient(
                ellipse at 50% -10%,
                var(--surface2) 0%,
                var(--page) 62%
            ) !important;
        color: var(--text) !important;
    }}

    .block-container {{
        max-width: 1400px;
        padding-top: 3rem;
        padding-bottom: 4rem;
    }}

    h1, h2, h3, h4 {{
        font-family:
            "Berkshire Swash",
            Georgia,
            serif !important;
        color: var(--text) !important;
    }}

    p, label {{
        color: var(--text);
    }}

    .stMarkdown {{
        color: var(--text);
    }}


    /* ========================================================
       HEADER
       ======================================================== */

    .book-header {{
        text-align: center;
        padding-top: 15px;
        margin-bottom: 0;
    }}

    .book-header-title {{
        font-family:
            "Berkshire Swash",
            Georgia,
            serif !important;
        font-size: clamp(48px, 6vw, 76px);
        line-height: 1.15;
        font-weight: 400;
        color: var(--text) !important;
        text-shadow: 0 3px 12px rgba(0,0,0,.35);
        margin: 0;
        padding: 0;
    }}


    /* ========================================================
       WILLOW TREE
       ======================================================== */

    .willow-logo {{
        width: 100%;
        max-width: 1000px;
        height: 300px;
        margin: 0 auto 5px;
        display: block;
    }}

    .willow-logo svg {{
        width: 100%;
        height: 100%;
        display: block;
        overflow: visible;
    }}


    /* ========================================================
       THEME SELECTOR
       ======================================================== */

    .theme-heading {{
        font-family:
            "Berkshire Swash",
            Georgia,
            serif;
        font-size: 25px;
        color: var(--text);
        margin: 4px 0 7px;
    }}

    div[data-baseweb="select"] > div {{
        background: #171717 !important;
        border: 2px solid var(--accent) !important;
        border-radius: 10px !important;
        min-height: 48px !important;
    }}

    div[data-baseweb="select"] span {{
        color: #FFFFFF !important;
        font-weight: 600 !important;
    }}

    div[data-baseweb="select"] input {{
        color: #FFFFFF !important;
    }}

    div[role="listbox"] {{
        background: #171717 !important;
        border: 2px solid #D7A83A !important;
        border-radius: 10px !important;
        padding: 5px !important;
        box-shadow: 0 15px 40px rgba(0,0,0,.6) !important;
    }}

    div[role="option"] {{
        background: #171717 !important;
        color: #FFFFFF !important;
        padding: 12px 14px !important;
        border-radius: 7px !important;
        font-family:
            "Libre Baskerville",
            Georgia,
            serif !important;
        font-size: 14px !important;
    }}

    div[role="option"] span {{
        color: #FFFFFF !important;
    }}

    div[role="option"]:hover {{
        background: #3C3C3C !important;
    }}

    div[role="option"][aria-selected="true"] {{
        background: #8A641E !important;
    }}


    /* ========================================================
       STATS
       ======================================================== */

    .stat-card {{
        background:
            linear-gradient(
                145deg,
                rgba(255,255,255,.045),
                rgba(0,0,0,.12)
            );
        border-bottom: 2px solid var(--line);
        border-radius: 4px 18px 4px 18px;
        padding: 16px 8px 13px;
        text-align: center;
        box-shadow: 0 8px 25px rgba(0,0,0,.14);
    }}

    .stat-number {{
        font-family:
            "Berkshire Swash",
            Georgia,
            serif;
        font-size: 36px;
        color: var(--accent);
    }}

    .stat-label {{
        color: var(--muted);
        font-family:
            "Libre Baskerville",
            Georgia,
            serif;
        font-size: 10px;
        text-transform: uppercase;
        letter-spacing: .12em;
    }}


    /* ========================================================
       BUTTONS
       ======================================================== */

    .stButton > button {{
        background:
            linear-gradient(
                90deg,
                var(--surface),
                rgba(255,255,255,.025)
            ) !important;
        color: var(--text) !important;
        border: none !important;
        border-left: 2px solid var(--line) !important;
        border-radius: 0 14px 0 14px !important;
        font-family:
            "Libre Baskerville",
            Georgia,
            serif !important;
        font-weight: 600 !important;
    }}

    .stButton > button:hover {{
        background: var(--surface2) !important;
        border-left-color: var(--accent) !important;
        color: var(--text) !important;
        transform: translateX(3px);
    }}


    /* ========================================================
       INPUTS
       ======================================================== */

    div[data-baseweb="input"] > div {{
        background: var(--surface) !important;
        border-color: var(--line) !important;
        border-radius: 4px 12px 4px 12px !important;
    }}

    div[data-baseweb="input"] input {{
        color: var(--text) !important;
    }}

    textarea {{
        background: var(--surface) !important;
        color: var(--text) !important;
        border-radius: 4px 12px 4px 12px !important;
    }}


    /* ========================================================
       TABS
       ======================================================== */

    button[data-baseweb="tab"] {{
        font-family:
            "Berkshire Swash",
            Georgia,
            serif !important;
        font-size: 17px !important;
        color: var(--muted) !important;
    }}

    button[data-baseweb="tab"][aria-selected="true"] {{
        color: var(--accent) !important;
    }}

    div[data-baseweb="tab-highlight"] {{
        background-color: var(--accent) !important;
    }}


    /* ========================================================
       FILE UPLOADER
       ======================================================== */

    section[data-testid="stFileUploaderDropzone"] {{
        background: var(--surface) !important;
        border: 1px dashed var(--line) !important;
        border-radius: 4px 18px 4px 18px !important;
    }}


    /* ========================================================
       ANCESTRY-STYLE BOOK TREE
       ======================================================== */

    .ancestry-tree {{
        margin-top: 35px;
        padding: 35px 15px 50px;
        overflow-x: auto;
    }}

    .library-root {{
        width: 280px;
        margin: 0 auto 55px;
        padding: 18px 25px;
        background: var(--accent);
        color: var(--page);
        text-align: center;
        border-radius: 6px 28px 6px 28px;
        box-shadow: 0 8px 25px rgba(0,0,0,.25);
        position: relative;
    }}

    .library-root::after {{
        content: "";
        position: absolute;
        width: 2px;
        height: 55px;
        background: var(--line);
        left: 50%;
        top: 100%;
    }}

    .library-root-title {{
        font-family:
            "Berkshire Swash",
            Georgia,
            serif;
        font-size: 34px;
    }}

    .library-root-count {{
        font-family:
            "Libre Baskerville",
            Georgia,
            serif;
        font-size: 10px;
        margin-top: 5px;
        opacity: .8;
    }}

    .author-tree {{
        display: flex;
        gap: 35px;
        justify-content: center;
        align-items: flex-start;
        min-width: max-content;
        padding: 0 30px;
    }}

    .author-branch {{
        width: 300px;
        position: relative;
        padding-top: 28px;
    }}

    .author-branch::before {{
        content: "";
        position: absolute;
        width: 2px;
        height: 28px;
        background: var(--line);
        top: 0;
        left: 50%;
    }}

    .author-node {{
        position: relative;
        background: var(--surface);
        border: 2px solid var(--accent);
        border-radius: 5px 22px 5px 22px;
        padding: 15px 18px;
        text-align: center;
        box-shadow: 0 7px 20px rgba(0,0,0,.2);
        margin-bottom: 32px;
    }}

    .author-node::after {{
        content: "";
        position: absolute;
        width: 2px;
        height: 32px;
        background: var(--line);
        left: 50%;
        top: 100%;
    }}

    .author-name {{
        font-family:
            "Berkshire Swash",
            Georgia,
            serif;
        font-size: 27px;
        color: var(--text);
    }}

    .author-count {{
        color: var(--muted);
        font-family:
            "Libre Baskerville",
            Georgia,
            serif;
        font-size: 10px;
        margin-top: 5px;
    }}

    .author-children {{
        position: relative;
        padding-top: 5px;
    }}

    .author-children::before {{
        content: "";
        position: absolute;
        top: 0;
        left: 12%;
        right: 12%;
        height: 2px;
        background: var(--line);
    }}

    .series-branch {{
        position: relative;
        padding-top: 25px;
        margin-bottom: 25px;
    }}

    .series-branch::before {{
        content: "";
        position: absolute;
        width: 2px;
        height: 25px;
        background: var(--line);
        left: 50%;
        top: 0;
    }}

    .series-node {{
        background: var(--surface2);
        border: 1px solid var(--accent2);
        border-radius: 4px 18px 4px 18px;
        padding: 12px 15px;
        text-align: center;
        margin-bottom: 18px;
    }}

    .series-name {{
        font-family:
            "Berkshire Swash",
            Georgia,
            serif;
        font-size: 22px;
        color: var(--text);
    }}

    .series-count {{
        color: var(--muted);
        font-family:
            "Libre Baskerville",
            Georgia,
            serif;
        font-size: 9px;
        margin-top: 4px;
    }}

    .book-branch {{
        position: relative;
        margin-left: 25px;
        padding-left: 25px;
        margin-bottom: 10px;
        border-left: 2px solid var(--line);
    }}

    .book-branch::before {{
        content: "";
        position: absolute;
        width: 25px;
        height: 2px;
        background: var(--line);
        left: -2px;
        top: 50%;
    }}

    .tree-book {{
        background: var(--card);
        border-radius: 4px 14px 4px 14px;
        padding: 9px 11px;
        display: flex;
        gap: 10px;
        align-items: center;
        min-height: 62px;
    }}

    .tree-book-cover {{
        width: 42px;
        height: 62px;
        object-fit: cover;
        border-radius: 3px 8px 3px 8px;
        border: 1px solid var(--accent);
        flex-shrink: 0;
    }}

    .tree-book-title {{
        font-family:
            "Berkshire Swash",
            Georgia,
            serif;
        font-size: 17px;
        color: var(--text);
        line-height: 1.2;
    }}

    .tree-book-meta {{
        color: var(--muted);
        font-family:
            "Libre Baskerville",
            Georgia,
            serif;
        font-size: 8px;
        margin-top: 4px;
    }}

    .standalone-node {{
        background: var(--surface2);
        border: 1px solid var(--accent2);
        border-radius: 4px 18px 4px 18px;
        padding: 12px 15px;
        text-align: center;
        margin-bottom: 18px;
        position: relative;
    }}

    .standalone-node::before {{
        content: "";
        position: absolute;
        width: 2px;
        height: 25px;
        background: var(--line);
        left: 50%;
        bottom: 100%;
    }}

    .standalone-title {{
        font-family:
            "Berkshire Swash",
            Georgia,
            serif;
        font-size: 21px;
        color: var(--text);
    }}

    </style>
    """
)


# ============================================================
# HEADER + WILLOW TREE
# ============================================================

st.html(
    """
    <div class="book-header">
        <div class="book-header-title">
            My Book Tree
        </div>
    </div>

    <div class="willow-logo">

        <svg
            viewBox="0 0 1000 300"
            xmlns="http://www.w3.org/2000/svg"
            aria-label="Decorative willow tree"
        >

            <!-- TRUNK -->

            <path
                d="M500 300
                   C490 245 490 200 500 155
                   C510 110 525 70 540 35"
                fill="none"
                stroke="#54382E"
                stroke-width="30"
                stroke-linecap="round"
            />

            <path
                d="M505 295
                   C497 240 498 195 508 150
                   C518 105 530 70 542 38"
                fill="none"
                stroke="#765044"
                stroke-width="7"
                stroke-linecap="round"
            />

            <!-- MAIN BRANCHES -->

            <g
                fill="none"
                stroke="#54382E"
                stroke-linecap="round"
            >

                <path
                    d="M505 175
                       C440 135 365 105 275 95"
                    stroke-width="14"
                />

                <path
                    d="M500 195
                       C420 165 330 165 235 180"
                    stroke-width="11"
                />

                <path
                    d="M510 140
                       C465 95 430 60 400 20"
                    stroke-width="10"
                />

                <path
                    d="M515 170
                       C580 130 655 100 745 95"
                    stroke-width="14"
                />

                <path
                    d="M515 195
                       C595 165 680 165 765 180"
                    stroke-width="11"
                />

                <path
                    d="M520 135
                       C565 90 600 55 635 15"
                    stroke-width="10"
                />

            </g>

            <!-- HANGING WILLOW BRANCHES -->

            <g
                fill="none"
                stroke="#72805C"
                stroke-width="4"
                stroke-linecap="round"
            >

                <path d="M275 95 C260 155 270 225 290 295"/>
                <path d="M320 105 C305 170 315 240 335 300"/>
                <path d="M365 115 C350 180 360 245 380 290"/>
                <path d="M410 130 C395 185 405 240 425 280"/>
                <path d="M455 145 C445 195 455 240 470 270"/>
                <path d="M235 180 C225 225 235 265 250 295"/>

                <path d="M745 95 C760 155 750 225 730 295"/>
                <path d="M700 105 C715 170 705 240 685 300"/>
                <path d="M655 115 C670 180 660 245 640 290"/>
                <path d="M610 130 C625 185 615 240 595 280"/>
                <path d="M565 145 C575 195 565 240 550 270"/>
                <path d="M765 180 C775 225 765 265 750 295"/>

            </g>

            <!-- LEAVES -->

            <g fill="#7D8C65">

                <ellipse cx="275" cy="135" rx="7" ry="23"
                    transform="rotate(-20 275 135)"/>
                <ellipse cx="290" cy="195" rx="7" ry="24"
                    transform="rotate(18 290 195)"/>
                <ellipse cx="295" cy="250" rx="7" ry="23"
                    transform="rotate(-15 295 250)"/>

                <ellipse cx="320" cy="145" rx="7" ry="23"
                    transform="rotate(18 320 145)"/>
                <ellipse cx="335" cy="210" rx="7" ry="24"
                    transform="rotate(-15 335 210)"/>
                <ellipse cx="340" cy="265" rx="7" ry="22"
                    transform="rotate(15 340 265)"/>

                <ellipse cx="365" cy="155" rx="7" ry="23"
                    transform="rotate(-18 365 155)"/>
                <ellipse cx="380" cy="215" rx="7" ry="24"
                    transform="rotate(15 380 215)"/>

                <ellipse cx="410" cy="165" rx="7" ry="23"
                    transform="rotate(16 410 165)"/>
                <ellipse cx="425" cy="220" rx="7" ry="23"
                    transform="rotate(-16 425 220)"/>

                <ellipse cx="745" cy="135" rx="7" ry="23"
                    transform="rotate(20 745 135)"/>
                <ellipse cx="730" cy="195" rx="7" ry="24"
                    transform="rotate(-18 730 195)"/>
                <ellipse cx="725" cy="250" rx="7" ry="23"
                    transform="rotate(15 725 250)"/>

                <ellipse cx="700" cy="145" rx="7" ry="23"
                    transform="rotate(-18 700 145)"/>
                <ellipse cx="685" cy="210" rx="7" ry="24"
                    transform="rotate(15 685 210)"/>
                <ellipse cx="680" cy="265" rx="7" ry="22"
                    transform="rotate(-15 680 265)"/>

                <ellipse cx="655" cy="155" rx="7" ry="23"
                    transform="rotate(18 655 155)"/>
                <ellipse cx="640" cy="215" rx="7" ry="24"
                    transform="rotate(-15 640 215)"/>

                <ellipse cx="610" cy="165" rx="7" ry="23"
                    transform="rotate(-16 610 165)"/>
                <ellipse cx="595" cy="220" rx="7" ry="23"
                    transform="rotate(16 595 220)"/>

            </g>

            <!-- LIGHTER LEAVES -->

            <g fill="#95A574">

                <ellipse cx="310" cy="125" rx="6" ry="21"
                    transform="rotate(-20 310 125)"/>
                <ellipse cx="355" cy="190" rx="6" ry="22"
                    transform="rotate(18 355 190)"/>
                <ellipse cx="400" cy="140" rx="6" ry="21"
                    transform="rotate(-17 400 140)"/>

                <ellipse cx="690" cy="125" rx="6" ry="21"
                    transform="rotate(20 690 125)"/>
                <ellipse cx="645" cy="190" rx="6" ry="22"
                    transform="rotate(-18 645 190)"/>
                <ellipse cx="600" cy="140" rx="6" ry="21"
                    transform="rotate(17 600 140)"/>

            </g>

            <!-- FLOWERS -->

            <g fill="#B87587">

                <circle cx="310" cy="115" r="6"/>
                <circle cx="320" cy="120" r="6"/>
                <circle cx="315" cy="108" r="6"/>
                <circle cx="305" cy="110" r="6"/>

                <circle cx="400" cy="145" r="6"/>
                <circle cx="410" cy="150" r="6"/>
                <circle cx="405" cy="138" r="6"/>
                <circle cx="395" cy="140" r="6"/>

                <circle cx="690" cy="115" r="6"/>
                <circle cx="700" cy="120" r="6"/>
                <circle cx="695" cy="108" r="6"/>
                <circle cx="685" cy="110" r="6"/>

                <circle cx="600" cy="145" r="6"/>
                <circle cx="610" cy="150" r="6"/>
                <circle cx="605" cy="138" r="6"/>
                <circle cx="595" cy="140" r="6"/>

            </g>

            <!-- FLOWER CENTERS -->

            <g fill="#E2B35E">
                <circle cx="312" cy="115" r="3"/>
                <circle cx="402" cy="145" r="3"/>
                <circle cx="692" cy="115" r="3"/>
                <circle cx="602" cy="145" r="3"/>
            </g>

        </svg>
    </div>
    """
)


# ============================================================
# THEME PICKER
# ============================================================

st.html(
    '<div class="theme-heading">Choose your bookish theme</div>'
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
            f"https://covers.openlibrary.org/"
            f"b/isbn/{isbn}-L.jpg"
        )

        try:

            r = requests.get(
                url,
                timeout=8,
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
                [],
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
                [],
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
                        "https://",
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
            re.I,
        )

        if match:

            series = match.group(1)

            series = re.sub(
                r",?\s*#\s*\d+(?:\.\d+)?",
                "",
                series,
                flags=re.I,
            )

            series = re.sub(
                r"\bBook\s+\d+(?:\.\d+)?",
                "",
                series,
                flags=re.I,
            )

            series = re.sub(
                r"\s+",
                " ",
                series,
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
            re.I,
        )

        if match:

            try:
                return float(
                    match.group(1)
                )

            except Exception:
                pass

    return None


# ============================================================
# IMPORT
# ============================================================

def import_books(uploaded):

    try:

        df = pd.read_csv(
            uploaded,
            low_memory=False,
        )

    except Exception:

        uploaded.seek(0)

        df = pd.read_csv(
            uploaded,
            encoding="latin-1",
            low_memory=False,
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
        [
            "title",
            "book title",
        ]
    )

    author_col = find_column(
        [
            "author",
            "authors",
        ]
    )

    isbn_col = find_column(
        [
            "isbn13",
            "isbn",
            "isbn13 number",
        ]
    )

    rating_col = find_column(
        [
            "my rating",
            "rating",
        ]
    )

    shelf_col = find_column(
        [
            "exclusive shelf",
            "shelf",
            "status",
        ]
    )

    genre_col = find_column(
        [
            "genre",
            "genres",
            "category",
            "categories",
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
                "",
            )
        ).strip()

        if (
            not title
            or title.lower() == "nan"
        ):
            continue

        author = "Unknown Author"

        if author_col:

            author = str(
                row.get(
                    author_col,
                    "",
                )
            ).strip()

        if (
            not author
            or author.lower() == "nan"
        ):
            author = "Unknown Author"

        isbn = ""

        if isbn_col:

            isbn = re.sub(
                r"\D",
                "",
                str(
                    row.get(
                        isbn_col,
                        "",
                    )
                ),
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

        genre = ""

        if genre_col:

            genre = str(
                row.get(
                    genre_col,
                    "",
                )
            ).strip()

            if genre.lower() == "nan":
                genre = ""

        status = "Want to Read"

        if shelf_col:

            shelf = str(
                row.get(
                    shelf_col,
                    "",
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
                "Series Number": detect_series_number(title),
                "ISBN": isbn,
                "Genre": genre,
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

    for i in range(
        len(new_library)
    ):

        new_library.loc[
            i,
            "Cover",
        ] = get_cover(
            new_library.loc[
                i,
                "Title",
            ],
            new_library.loc[
                i,
                "Author",
            ],
            new_library.loc[
                i,
                "ISBN",
            ],
        )

        progress.progress(
            (i + 1)
            / len(new_library)
        )

    progress.empty()

    st.session_state.library = (
        new_library
    )

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
    stats,
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
        "🌳 Book Tree",
        "📚 Books",
        "➕ Add Book",
        "📥 Import",
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

        # ----------------------------------------------------
        # SEARCH
        # ----------------------------------------------------

        search = st.text_input(
            "Search your tree",
            placeholder=(
                "Search by author, title, genre, or ISBN..."
            ),
            key="tree_search",
        )

        filtered = library.copy()

        if search.strip():

            q = search.strip().lower()

            searchable = (
                filtered["Author"]
                .fillna("")
                .astype(str)
                .str.lower()
                .str.contains(
                    q,
                    na=False,
                )
                |
                filtered["Title"]
                .fillna("")
                .astype(str)
                .str.lower()
                .str.contains(
                    q,
                    na=False,
                )
                |
                filtered["ISBN"]
                .fillna("")
                .astype(str)
                .str.lower()
                .str.contains(
                    q,
                    na=False,
                )
            )

            if "Genre" in filtered.columns:

                searchable = (
                    searchable
                    |
                    filtered["Genre"]
                    .fillna("")
                    .astype(str)
                    .str.lower()
                    .str.contains(
                        q,
                        na=False,
                    )
                )

            filtered = filtered[
                searchable
            ]

        if filtered.empty:

            st.warning(
                "No books matched your search."
            )

        else:

            # ------------------------------------------------
            # ROOT
            # ------------------------------------------------

            st.html(
                f"""
                <div class="ancestry-tree">

                    <div class="library-root">

                        <div class="library-root-title">
                            My Library
                        </div>

                        <div class="library-root-count">
                            {len(filtered)} books ·
                            {filtered["Author"].nunique()} authors
                        </div>

                    </div>

                    <div class="author-tree">
                """
            )

            # ------------------------------------------------
            # AUTHORS
            # ------------------------------------------------

            author_list = sorted(
                filtered["Author"]
                .fillna("Unknown Author")
                .astype(str)
                .unique(),
                key=lambda x: x.lower(),
            )

            for author in author_list:

                author_books = filtered[
                    filtered["Author"]
                    .fillna("Unknown Author")
                    .astype(str)
                    == author
                ].copy()

                st.html(
                    f"""
                    <div class="author-branch">

                        <div class="author-node">

                            <div class="author-name">
                                {html.escape(author)}
                            </div>

                            <div class="author-count">
                                {len(author_books)}
                                {"book" if len(author_books) == 1 else "books"}
                            </div>

                        </div>

                        <div class="author-children">
                    """
                )

                # --------------------------------------------
                # SERIES + STANDALONES
                # --------------------------------------------

                series_list = sorted(
                    author_books["Series"]
                    .fillna("Standalone")
                    .astype(str)
                    .unique(),
                    key=lambda x: x.lower(),
                )

                for series in series_list:

                    series_books = author_books[
                        author_books["Series"]
                        .fillna("Standalone")
                        .astype(str)
                        == series
                    ].copy()

                    # ----------------------------------------
                    # STANDALONE BOOKS
                    # ----------------------------------------

                    if series == "Standalone":

                        st.html(
                            """
                            <div class="standalone-node">
                                <div class="standalone-title">
                                    Standalone Books
                                </div>
                            </div>
                            """
                        )

                        for _, book in (
                            series_books.iterrows()
                        ):

                            title = html.escape(
                                str(
                                    book.get(
                                        "Title",
                                        "",
                                    )
                                )
                            )

                            status = html.escape(
                                str(
                                    book.get(
                                        "Status",
                                        "",
                                    )
                                )
                            )

                            cover = str(
                                book.get(
                                    "Cover",
                                    "",
                                )
                                or ""
                            )

                            if cover:

                                st.html(
                                    f"""
                                    <div class="book-branch">

                                        <div class="tree-book">

                                            <img
                                                class="tree-book-cover"
                                                src="{html.escape(cover)}"
                                            >

                                            <div>

                                                <div class="tree-book-title">
                                                    {title}
                                                </div>

                                                <div class="tree-book-meta">
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
                                    <div class="book-branch">

                                        <div class="tree-book">

                                            <div>

                                                <div class="tree-book-title">
                                                    {title}
                                                </div>

                                                <div class="tree-book-meta">
                                                    {status}
                                                </div>

                                            </div>

                                        </div>

                                    </div>
                                    """
                                )

                        continue

                    # ----------------------------------------
                    # SERIES NODE
                    # ----------------------------------------

                    st.html(
                        f"""
                        <div class="series-branch">

                            <div class="series-node">

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

                    # ----------------------------------------
                    # BOOKS IN SERIES
                    # ----------------------------------------

                    series_books = (
                        series_books.sort_values(
                            by=[
                                "Series Number",
                                "Title",
                            ],
                            na_position="last",
                        )
                    )

                    for position, (
                        _,
                        book,
                    ) in enumerate(
                        series_books.iterrows(),
                        1,
                    ):

                        number = book.get(
                            "Series Number"
                        )

                        if pd.notna(number):

                            try:

                                if float(
                                    number
                                ).is_integer():

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

                        title = html.escape(
                            str(
                                book.get(
                                    "Title",
                                    "",
                                )
                            )
                        )

                        status = html.escape(
                            str(
                                book.get(
                                    "Status",
                                    "",
                                )
                            )
                        )

                        cover = str(
                            book.get(
                                "Cover",
                                "",
                            )
                            or ""
                        )

                        if cover:

                            st.html(
                                f"""
                                <div class="book-branch">

                                    <div class="tree-book">

                                        <img
                                            class="tree-book-cover"
                                            src="{html.escape(cover)}"
                                        >

                                        <div>

                                            <div class="tree-book-title">
                                                {number_text} · {title}
                                            </div>

                                            <div class="tree-book-meta">
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
                                <div class="book-branch">

                                    <div class="tree-book">

                                        <div>

                                            <div class="tree-book-title">
                                                {number_text} · {title}
                                            </div>

                                            <div class="tree-book-meta">
                                                {status}
                                            </div>

                                        </div>

                                    </div>

                                </div>
                                """
                            )

                    st.html(
                        "</div>"
                    )

                st.html(
                    """
                        </div>
                    </div>
                    """
                )

            st.html(
                """
                    </div>
                </div>
                """
            )


# ============================================================
# BOOKS
# ============================================================

with books_tab:

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
                        width=70,
                    )

            with col2:

                genre = str(
                    book.get(
                        "Genre",
                        "",
                    )
                    or ""
                )

                genre_text = (
                    f"<br>{html.escape(genre)}"
                    if genre
                    else ""
                )

                st.html(
                    f"""
                    <div class="tree-book-title">
                        {html.escape(str(book["Title"]))}
                    </div>

                    <div class="tree-book-meta">
                        {html.escape(str(book["Author"]))}
                        <br>
                        {html.escape(str(book["Series"]))}
                        {genre_text}
                    </div>
                    """
                )

            with col3:

                favorite = st.checkbox(
                    "♥",
                    value=bool(
                        book.get(
                            "Favorite",
                            False,
                        )
                    ),
                    key=f"fav_{index}",
                )

                if favorite != bool(
                    book.get(
                        "Favorite",
                        False,
                    )
                ):

                    st.session_state.library.loc[
                        index,
                        "Favorite",
                    ] = favorite

                    st.rerun()


# ============================================================
# ADD BOOK
# ============================================================

with add_tab:

    st.header("Add a Book")

    with st.form("add_book"):

        title = st.text_input(
            "Title"
        )

        author = st.text_input(
            "Author"
        )

        genre = st.text_input(
            "Genre"
        )

        series = st.text_input(
            "Series",
            placeholder=(
                "Leave blank for standalone"
            ),
        )

        number = st.number_input(
            "Series number",
            min_value=0.0,
            value=0.0,
            step=0.5,
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
            ],
        )

        rating = st.slider(
            "Rating",
            0,
            5,
            0,
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
                    isbn,
                )

                new_book = {
                    "Title": title.strip(),
                    "Author": author.strip(),
                    "Series": actual_series,
                    "Series Number": (
                        number
                        if number
                        else None
                    ),
                    "ISBN": re.sub(
                        r"\D",
                        "",
                        isbn,
                    ),
                    "Genre": genre.strip(),
                    "My Rating": (
                        rating
                        if rating
                        else None
                    ),
                    "Status": status,
                    "Favorite": favorite,
                    "Cover": cover,
                    "Description": "",
                    "Publisher": "",
                    "Pages": "",
                    "Date Read": "",
                }

                st.session_state.library = (
                    pd.concat(
                        [
                            st.session_state.library,
                            pd.DataFrame(
                                [new_book]
                            ),
                        ],
                        ignore_index=True,
                    )
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
        "Import Your Library"
    )

    st.write(
        "Upload a Goodreads CSV, StoryGraph export, "
        "or another compatible book-list CSV."
    )

    uploaded = st.file_uploader(
        "Choose your CSV",
        type=["csv"],
    )

    if uploaded:

        st.success(
            f"File loaded: {uploaded.name}"
        )

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
```
