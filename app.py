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

    "Old Bookshop": {
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

css = f"""
<style>

@import url('https://fonts.googleapis.com/css2?family=Berkshire+Swash&family=Libre+Baskerville:wght@400;700&display=swap');

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
    padding-top: 1rem;
    padding-bottom: 4rem;
}}

/* GENERAL TYPOGRAPHY */

h1, h2, h3, h4 {{
    font-family:
        "Berkshire Swash",
        Georgia,
        serif !important;
    color: var(--text) !important;
}}

p, label {{
    color: var(--text) !important;
}}

.stMarkdown {{
    color: var(--text) !important;
}}

/* HEADER */

.book-header {{
    text-align: center;
    padding: 18px 0 0;
}}

.book-header-title {{
    font-family:
        "Berkshire Swash",
        Georgia,
        serif !important;
    font-size: 70px;
    line-height: 1;
    font-weight: 400;
    color: var(--text) !important;
    text-shadow:
        0 3px 12px rgba(0,0,0,.35);
}}

/* WILLOW */

.willow-logo {{
    width: 100%;
    max-width: 980px;
    height: 250px;
    margin: 0 auto 8px;
    display: block;
}}

.willow-logo svg {{
    width: 100%;
    height: 100%;
    overflow: visible;
}}

.willow-trunk {{
    fill: none;
    stroke: #4A3028;
    stroke-width: 27;
    stroke-linecap: round;
}}

.willow-trunk-highlight {{
    fill: none;
    stroke: #765044;
    stroke-width: 7;
    stroke-linecap: round;
}}

.willow-main-branch {{
    fill: none;
    stroke: #54372E;
    stroke-linecap: round;
}}

.willow-hanging {{
    fill: none;
    stroke: #657452;
    stroke-width: 4;
    stroke-linecap: round;
}}

.willow-leaf {{
    fill: #74835D;
}}

.willow-leaf-light {{
    fill: #89966B;
}}

.willow-leaf-deep {{
    fill: #536346;
}}

.willow-flower {{
    fill: #B87587;
}}

.willow-flower-center {{
    fill: #E2B35E;
}}

/* THEME SELECTOR */

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
    box-shadow:
        0 15px 40px rgba(0,0,0,.6) !important;
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

div[role="option"] *,
div[role="option"] span {{
    color: #FFFFFF !important;
}}

div[role="option"]:hover {{
    background: #3C3C3C !important;
}}

div[role="option"][aria-selected="true"] {{
    background: #8A641E !important;
}}

div[role="option"][aria-selected="true"] * {{
    color: #FFFFFF !important;
}}

/* STATS */

.stat-card {{
    position: relative;
    background:
        linear-gradient(
            145deg,
            rgba(255,255,255,.045),
            rgba(0,0,0,.12)
        );
    border: none;
    border-bottom: 2px solid var(--line);
    border-radius: 4px 18px 4px 18px;
    padding: 16px 8px 13px;
    text-align: center;
    box-shadow:
        0 8px 25px rgba(0,0,0,.14);
}}

.stat-number {{
    font-family:
        "Berkshire Swash",
        Georgia,
        serif;
    font-size: 36px;
    font-weight: 400;
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

/* TREE */

.tree-area {{
    margin-top: 25px;
    padding: 35px 25px;
    background:
        radial-gradient(
            ellipse at top,
            rgba(255,255,255,.035),
            transparent 65%
        );
    border: none;
    border-top: 1px solid rgba(255,255,255,.10);
    border-bottom: 1px solid rgba(255,255,255,.08);
}}

.root-node {{
    width: 300px;
    margin: 0 auto 38px;
    padding: 17px 25px;
    background: var(--accent);
    color: {theme["page"]};
    border-radius: 4px 28px 4px 28px;
    text-align: center;
    box-shadow:
        0 10px 28px rgba(0,0,0,.25);
}}

.root-node-title {{
    color: {theme["page"]};
    font-family:
        "Berkshire Swash",
        Georgia,
        serif;
    font-size: 34px;
    font-weight: 400;
}}

.root-node-small {{
    color: {theme["page"]};
    font-family:
        "Libre Baskerville",
        Georgia,
        serif;
    font-size: 10px;
    font-weight: 700;
    opacity: .78;
}}

/* AUTHOR */

.author-info {{
    padding: 11px 17px;
    margin: 9px 0;
    border-left: 3px solid var(--accent);
    background:
        linear-gradient(
            90deg,
            var(--surface),
            transparent
        );
    border-radius: 0 18px 0 0;
}}

.author-name {{
    font-family:
        "Berkshire Swash",
        Georgia,
        serif;
    font-size: 28px;
    font-weight: 400;
}}

.author-count {{
    color: var(--muted);
    font-family:
        "Libre Baskerville",
        Georgia,
        serif;
    font-size: 10px;
}}

/* SERIES */

.series-info {{
    margin-left: 48px;
    padding: 10px 15px;
    border-left: 2px solid var(--accent2);
    background:
        linear-gradient(
            90deg,
            var(--surface2),
            transparent
        );
    border-radius: 0 15px 0 0;
}}

.series-name {{
    font-family:
        "Berkshire Swash",
        Georgia,
        serif;
    font-size: 24px;
    font-weight: 400;
}}

.series-count {{
    color: var(--muted);
    font-family:
        "Libre Baskerville",
        Georgia,
        serif;
    font-size: 10px;
}}

/* BOOK */

.book-info {{
    margin-left: 100px;
    margin-top: 8px;
    padding: 11px 14px;
    background:
        linear-gradient(
            90deg,
            var(--card),
            transparent
        );
    border-left: 2px solid var(--line);
    border-radius: 0 14px 0 0;
}}

.book-title {{
    font-family:
        "Berkshire Swash",
        Georgia,
        serif;
    font-size: 22px;
    font-weight: 400;
    color: var(--text);
}}

.book-meta {{
    color: var(--muted);
    font-family:
        "Libre Baskerville",
        Georgia,
        serif;
    font-size: 10px;
    margin-top: 4px;
}}

.book-cover {{
    width: 55px;
    height: 80px;
    object-fit: cover;
    border-radius: 3px 10px 3px 10px;
    border: 1px solid var(--accent);
    box-shadow:
        3px 5px 12px rgba(0,0,0,.3);
}}

/* BUTTONS */

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
    transition: all .2s ease !important;
}}

.stButton > button:hover {{
    background: var(--surface2) !important;
    border-left-color: var(--accent) !important;
    color: var(--text) !important;
    transform: translateX(3px);
}}

/* INPUTS */

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

/* TABS */

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

/* FILE UPLOADER */

section[data-testid="stFileUploaderDropzone"] {{
    background: var(--surface) !important;
    border: 1px dashed var(--line) !important;
    border-radius: 4px 18px 4px 18px !important;
}}

</style>
"""

st.html(css)


# ============================================================
# HEADER + WILLOW
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
            viewBox="0 0 1000 330"
            xmlns="http://www.w3.org/2000/svg"
        >

            <!-- TRUNK -->
            <path
                d="M500 325
                   C490 275 492 225 500 180
                   C508 135 520 95 535 55"
                fill="none"
                stroke="#51352C"
                stroke-width="30"
                stroke-linecap="round"
            />

            <path
                d="M505 320
                   C498 270 500 225 508 180
                   C515 135 527 95 540 58"
                fill="none"
                stroke="#795449"
                stroke-width="7"
                stroke-linecap="round"
            />

            <!-- LEFT BRANCHES -->
            <g
                fill="none"
                stroke="#51352C"
                stroke-linecap="round"
            >
                <path
                    d="M505 180
                       C445 145 370 115 285 105"
                    stroke-width="14"
                />

                <path
                    d="M500 205
                       C425 180 340 175 245 190"
                    stroke-width="11"
                />

                <path
                    d="M510 145
                       C465 105 425 70 395 30"
                    stroke-width="10"
                />
            </g>

            <!-- RIGHT BRANCHES -->
            <g
                fill="none"
                stroke="#51352C"
                stroke-linecap="round"
            >
                <path
                    d="M515 175
                       C575 140 650 110 735 105"
                    stroke-width="14"
                />

                <path
                    d="M515 205
                       C590 180 675 175 760 190"
                    stroke-width="11"
                />

                <path
                    d="M520 140
                       C565 100 605 65 635 25"
                    stroke-width="10"
                />
            </g>

            <!-- WILLOW HANGING BRANCHES -->
            <g
                fill="none"
                stroke="#687653"
                stroke-width="4"
                stroke-linecap="round"
            >
                <path d="M285 105 C275 160 282 225 300 300"/>
                <path d="M330 115 C320 175 330 245 345 315"/>
                <path d="M375 125 C365 185 375 250 390 305"/>
                <path d="M420 140 C410 195 420 250 435 290"/>
                <path d="M460 155 C450 205 458 250 470 280"/>
                <path d="M245 190 C238 235 245 270 260 310"/>

                <path d="M735 105 C745 160 738 225 720 300"/>
                <path d="M690 115 C700 175 690 245 675 315"/>
                <path d="M645 125 C655 185 645 250 630 305"/>
                <path d="M600 140 C610 195 600 250 585 290"/>
                <path d="M560 155 C570 205 562 250 550 280"/>
                <path d="M760 190 C767 235 760 270 745 310"/>
            </g>

            <!-- LEAVES -->
            <g fill="#7D8C65">

                <ellipse cx="285" cy="145" rx="7" ry="24"
                    transform="rotate(-18 285 145)"/>
                <ellipse cx="300" cy="205" rx="7" ry="25"
                    transform="rotate(16 300 205)"/>
                <ellipse cx="305" cy="260" rx="7" ry="24"
                    transform="rotate(-14 305 260)"/>

                <ellipse cx="330" cy="155" rx="7" ry="24"
                    transform="rotate(18 330 155)"/>
                <ellipse cx="345" cy="220" rx="7" ry="25"
                    transform="rotate(-15 345 220)"/>
                <ellipse cx="350" cy="275" rx="7" ry="23"
                    transform="rotate(15 350 275)"/>

                <ellipse cx="375" cy="165" rx="7" ry="24"
                    transform="rotate(-18 375 165)"/>
                <ellipse cx="390" cy="225" rx="7" ry="25"
                    transform="rotate(15 390 225)"/>

                <ellipse cx="420" cy="175" rx="7" ry="24"
                    transform="rotate(16 420 175)"/>
                <ellipse cx="435" cy="230" rx="7" ry="24"
                    transform="rotate(-16 435 230)"/>

                <ellipse cx="720" cy="145" rx="7" ry="24"
                    transform="rotate(18 720 145)"/>
                <ellipse cx="705" cy="205" rx="7" ry="25"
                    transform="rotate(-16 705 205)"/>
                <ellipse cx="700" cy="260" rx="7" ry="24"
                    transform="rotate(14 700 260)"/>

                <ellipse cx="675" cy="155" rx="7" ry="24"
                    transform="rotate(-18 675 155)"/>
                <ellipse cx="660" cy="220" rx="7" ry="25"
                    transform="rotate(15 660 220)"/>
                <ellipse cx="655" cy="275" rx="7" ry="23"
                    transform="rotate(-15 655 275)"/>

                <ellipse cx="630" cy="165" rx="7" ry="24"
                    transform="rotate(18 630 165)"/>
                <ellipse cx="615" cy="225" rx="7" ry="25"
                    transform="rotate(-15 615 225)"/>

                <ellipse cx="585" cy="175" rx="7" ry="24"
                    transform="rotate(-16 585 175)"/>
                <ellipse cx="570" cy="230" rx="7" ry="24"
                    transform="rotate(16 570 230)"/>

            </g>

            <!-- LIGHTER LEAVES -->
            <g fill="#92A06F">

                <ellipse cx="320" cy="130" rx="6" ry="21"
                    transform="rotate(-20 320 130)"/>
                <ellipse cx="360" cy="195" rx="6" ry="22"
                    transform="rotate(18 360 195)"/>
                <ellipse cx="410" cy="145" rx="6" ry="21"
                    transform="rotate(-17 410 145)"/>

                <ellipse cx="680" cy="130" rx="6" ry="21"
                    transform="rotate(20 680 130)"/>
                <ellipse cx="640" cy="195" rx="6" ry="22"
                    transform="rotate(-18 640 195)"/>
                <ellipse cx="590" cy="145" rx="6" ry="21"
                    transform="rotate(17 590 145)"/>

            </g>

            <!-- SMALL FLOWERS -->
            <g fill="#B97888">

                <circle cx="320" cy="120" r="5"/>
                <circle cx="327" cy="124" r="5"/>
                <circle cx="324" cy="116" r="5"/>
                <circle cx="316" cy="117" r="5"/>

                <circle cx="410" cy="150" r="5"/>
                <circle cx="417" cy="154" r="5"/>
                <circle cx="414" cy="146" r="5"/>
                <circle cx="406" cy="147" r="5"/>

                <circle cx="680" cy="120" r="5"/>
                <circle cx="687" cy="124" r="5"/>
                <circle cx="684" cy="116" r="5"/>
                <circle cx="676" cy="117" r="5"/>

                <circle cx="590" cy="150" r="5"/>
                <circle cx="597" cy="154" r="5"/>
                <circle cx="594" cy="146" r="5"/>
                <circle cx="586" cy="147" r="5"/>

            </g>

            <!-- GOLD CENTERS -->
            <g fill="#E2B35E">

                <circle cx="321" cy="120" r="2"/>
                <circle cx="411" cy="150" r="2"/>
                <circle cx="681" cy="120" r="2"/>
                <circle cx="591" cy="150" r="2"/>

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

    isbn = re.sub(
        r"\D",
        "",
        str(isbn)
    )

    # First try ISBN
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

    # Then Open Library search
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

    # Finally Google Books
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

    text = str(title)

    patterns = [
        r"\(([^()]*)\s*#\s*\d+(?:\.\d+)?[^()]*\)",
        r"\[([^\[\]]*)\s*#\s*\d+(?:\.\d+)?[^\[\]]*\]",
        r"\(([^()]*)\bBook\s+\d+(?:\.\d+)?[^()]*\)",
        r"\[([^\[\]]*)\bBook\s+\d+(?:\.\d+)?[^\[\]]*\]",
    ]

    for pattern in patterns:

        match = re.search(
            pattern,
            text,
            re.IGNORECASE
        )

        if match:

            series = match.group(1)

            series = re.sub(
                r",?\s*#\s*\d+(?:\.\d+)?",
                "",
                series,
                flags=re.IGNORECASE
            )

            series = re.sub(
                r"\bBook\s+\d+(?:\.\d+)?",
                "",
                series,
                flags=re.IGNORECASE
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

    text = str(title)

    patterns = [
        r"#\s*(\d+(?:\.\d+)?)",
        r"\bBook\s+(\d+(?:\.\d+)?)",
        r"\bVol(?:ume)?\.?\s+(\d+(?:\.\d+)?)",
    ]

    for pattern in patterns:

        match = re.search(
            pattern,
            text,
            re.IGNORECASE
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

                value = row.get(
                    rating_col
                )

                if pd.notna(value):
                    rating = float(value)

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
                "Series Number": detect_series_number(title),
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

        new_library.loc[i, "Cover"] = get_cover(
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

        search = st.text_input(
            "Search your tree",
            placeholder="Search author, series, or book..."
        )

        filtered = library.copy()

        if search:

            q = search.lower()

            filtered = filtered[
                (
                    filtered["Title"]
                    .fillna("")
                    .astype(str)
                    .str.lower()
                    .str.contains(q, na=False)
                )
                |
                (
                    filtered["Author"]
                    .fillna("")
                    .astype(str)
                    .str.lower()
                    .str.contains(q, na=False)
                )
                |
                (
                    filtered["Series"]
                    .fillna("")
                    .astype(str)
                    .str.lower()
                    .str.contains(q, na=False)
                )
            ]

        st.html(
            f"""
            <div class="tree-area">

                <div class="root-node">

                    <div class="root-node-title">
                        My Library
                    </div>

                    <div class="root-node-small">
                        {len(filtered)} books ·
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

                series_id = (
                    author_id
                    + "::"
                    + safe_id(series)
                )

                series_open = (
                    series_id
                    in st.session_state.open_series
                )

                arrow = "▼" if series_open else "▶"

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

    st.header(
        "Import Your Library"
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
