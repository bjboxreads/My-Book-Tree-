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

    "Enchanted Garden": {
        "page": "#101A16",
        "surface": "#182720",
        "surface2": "#23382E",
        "card": "#304A3D",
        "text": "#FFF7E6",
        "muted": "#D1D8CC",
        "accent": "#D9B45B",
        "accent2": "#8FA77A",
        "line": "#A98A4C",
        "button": "#20352C",
        "button_text": "#FFF7E6",
    },

    "Midnight & Moonlight": {
        "page": "#111222",
        "surface": "#191A30",
        "surface2": "#292A4A",
        "card": "#393A62",
        "text": "#FFF8E9",
        "muted": "#D2D0DF",
        "accent": "#E4C66B",
        "accent2": "#9B91C9",
        "line": "#8075A7",
        "button": "#22243F",
        "button_text": "#FFF8E9",
    },

    "Velvet Rose": {
        "page": "#1B1018",
        "surface": "#291520",
        "surface2": "#3B1D2D",
        "card": "#51283D",
        "text": "#FFF5F1",
        "muted": "#DECBD1",
        "accent": "#D8A05F",
        "accent2": "#C98DA5",
        "line": "#9D536F",
        "button": "#321A29",
        "button_text": "#FFF5F1",
    },

    "Autumn Storybook": {
        "page": "#21150E",
        "surface": "#302016",
        "surface2": "#4A3020",
        "card": "#604027",
        "text": "#FFF3DA",
        "muted": "#DCC8A8",
        "accent": "#D9A14D",
        "accent2": "#B87852",
        "line": "#A56B39",
        "button": "#3C281B",
        "button_text": "#FFF3DA",
    },

    "Rosewood Library": {
        "page": "#1D1010",
        "surface": "#2C1616",
        "surface2": "#421F20",
        "card": "#5A2A2A",
        "text": "#FFF4E2",
        "muted": "#DDC9B9",
        "accent": "#D8AD61",
        "accent2": "#B87578",
        "line": "#9E5B52",
        "button": "#351B1B",
        "button_text": "#FFF4E2",
    },

    "Moonlit Lavender": {
        "page": "#151124",
        "surface": "#211A35",
        "surface2": "#30254A",
        "card": "#42345E",
        "text": "#FFF8EF",
        "muted": "#D8D0DF",
        "accent": "#E0C16B",
        "accent2": "#A894C7",
        "line": "#78649A",
        "button": "#29213E",
        "button_text": "#FFF8EF",
    },

    "Vintage Conservatory": {
        "page": "#17201D",
        "surface": "#24302B",
        "surface2": "#35443C",
        "card": "#4A5B4F",
        "text": "#FFF4DD",
        "muted": "#D4D5C8",
        "accent": "#D5AE61",
        "accent2": "#9CAA78",
        "line": "#8C7547",
        "button": "#2B3A33",
        "button_text": "#FFF4DD",
    },

    "Fairytale Crimson": {
        "page": "#210E13",
        "surface": "#32151C",
        "surface2": "#4B202B",
        "card": "#642C38",
        "text": "#FFF5E8",
        "muted": "#DEC9C4",
        "accent": "#E1B65D",
        "accent2": "#C9828F",
        "line": "#A75C6A",
        "button": "#3B1A22",
        "button_text": "#FFF5E8",
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

st.html(
    f"""
    <style>

    @import url('https://fonts.googleapis.com/css2?family=Berkshire+Swash&family=Cormorant+Garamond:wght@500;600;700&family=Libre+Baskerville:wght@400;700&display=swap');

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
                circle at 50% 0%,
                var(--surface2) 0%,
                var(--page) 58%
            );
        color: var(--text);
    }}

    .block-container {{
        max-width: 1400px;
        padding-top: 1rem;
        padding-bottom: 3rem;
    }}

    h1, h2, h3, h4 {{
        font-family:
            "Cormorant Garamond",
            Georgia,
            serif !important;
        color: var(--text) !important;
    }}

    p, label {{
        color: var(--text);
    }}

    /* ========================================================
       HEADER
       ======================================================== */

    .book-header {{
        text-align: center;
        padding: 18px 0 0;
        position: relative;
    }}

    .book-header-title {{
        font-family:
            "Berkshire Swash",
            cursive !important;
        font-size: 72px;
        line-height: 1;
        font-weight: 400;
        color: var(--text);
        text-shadow:
            0 2px 4px rgba(0,0,0,.45);
        letter-spacing: .01em;
    }}

    /* ========================================================
       WILLOW TREE
       ======================================================== */

    .willow-wrapper {{
        width: 100%;
        height: 285px;
        margin: -5px auto 5px;
        overflow: hidden;
        position: relative;
    }}

    .willow-wrapper svg {{
        width: 100%;
        height: 100%;
        display: block;
    }}

    .willow-trunk {{
        stroke: #4A3028;
    }}

    .willow-highlight {{
        stroke: #765044;
    }}

    .willow-branch {{
        stroke: #54372E;
    }}

    .willow-branch-light {{
        stroke: #765044;
    }}

    .willow-leaf {{
        fill: var(--accent2);
    }}

    .willow-leaf-light {{
        fill: #A8B78B;
    }}

    .willow-leaf-deep {{
        fill: #627651;
    }}

    .willow-flower {{
        fill: #B87587;
    }}

    /* ========================================================
       THEME SELECTOR
       ======================================================== */

    .theme-heading {{
        font-family:
            "Berkshire Swash",
            cursive;
        font-size: 25px;
        color: var(--text);
        text-align: center;
        margin: 0 0 7px;
    }}

    div[data-baseweb="select"] > div {{
        background: var(--surface) !important;
        border: 1px solid var(--accent) !important;
        border-radius: 6px !important;
        min-height: 45px !important;
        box-shadow: 0 4px 15px rgba(0,0,0,.18) !important;
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
        border-radius: 6px !important;
        box-shadow: 0 15px 40px rgba(0,0,0,.55) !important;
    }}

    div[role="option"] {{
        background: var(--surface) !important;
        color: var(--text) !important;
        padding: 12px 14px !important;
        font-family:
            "Libre Baskerville",
            Georgia,
            serif !important;
    }}

    div[role="option"] span {{
        color: var(--text) !important;
    }}

    div[role="option"]:hover {{
        background: var(--surface2) !important;
    }}

    div[role="option"][aria-selected="true"] {{
        background: var(--card) !important;
    }}

    /* ========================================================
       STATS
       ======================================================== */

    .stat-card {{
        background:
            linear-gradient(
                145deg,
                var(--surface),
                var(--surface2)
            );
        border-top: 1px solid var(--line);
        border-bottom: 1px solid var(--line);
        padding: 14px 8px;
        text-align: center;
        box-shadow:
            0 5px 20px rgba(0,0,0,.14);
    }}

    .stat-number {{
        font-family:
            "Berkshire Swash",
            cursive;
        font-size: 36px;
        color: var(--accent);
        line-height: 1;
    }}

    .stat-label {{
        color: var(--muted);
        font-family:
            "Libre Baskerville",
            Georgia,
            serif;
        font-size: 10px;
        text-transform: uppercase;
        letter-spacing: .13em;
        margin-top: 5px;
    }}

    /* ========================================================
       TREE AREA
       ======================================================== */

    .tree-area {{
        margin-top: 28px;
        padding: 30px 20px;
        background:
            radial-gradient(
                circle at 50% 0%,
                rgba(255,255,255,.035),
                transparent 65%
            );
        border-top: 1px solid var(--line);
        border-bottom: 1px solid var(--line);
    }}

    .root-node {{
        width: 300px;
        margin: 0 auto 35px;
        padding: 18px 25px;
        background:
            linear-gradient(
                135deg,
                var(--accent),
                #B8873B
            );
        color: var(--page);
        text-align: center;
        box-shadow:
            0 8px 25px rgba(0,0,0,.25);
    }}

    .root-node-title {{
        color: var(--page);
        font-family:
            "Berkshire Swash",
            cursive;
        font-size: 32px;
    }}

    .root-node-small {{
        color: var(--page);
        font-family:
            "Libre Baskerville",
            Georgia,
            serif;
        font-size: 10px;
        opacity: .85;
    }}

    /* ========================================================
       AUTHOR
       ======================================================== */

    .author-info {{
        padding: 8px 15px;
        margin: 8px 0;
        border-left: 3px solid var(--accent);
        background:
            linear-gradient(
                90deg,
                var(--surface),
                transparent
            );
    }}

    .author-name {{
        font-family:
            "Berkshire Swash",
            cursive;
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
    }}

    /* ========================================================
       SERIES
       ======================================================== */

    .series-info {{
        margin-left: 48px;
        padding: 8px 15px;
        border-left: 2px solid var(--accent2);
        background:
            linear-gradient(
                90deg,
                var(--surface2),
                transparent
            );
    }}

    .series-name {{
        font-family:
            "Cormorant Garamond",
            Georgia,
            serif;
        font-size: 24px;
        font-weight: 700;
        color: var(--text);
    }}

    .series-count {{
        color: var(--muted);
        font-size: 10px;
    }}

    /* ========================================================
       BOOK
       ======================================================== */

    .book-info {{
        margin-left: 100px;
        margin-top: 7px;
        padding: 9px 14px;
        background:
            linear-gradient(
                90deg,
                var(--card),
                transparent
            );
        border-left: 1px solid var(--line);
    }}

    .book-title {{
        font-family:
            "Cormorant Garamond",
            Georgia,
            serif;
        font-size: 22px;
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
        border-radius: 2px;
        border: 1px solid var(--accent);
        box-shadow:
            2px 4px 10px rgba(0,0,0,.35);
    }}

    /* ========================================================
       BUTTONS
       ======================================================== */

    .stButton > button {{
        background: transparent !important;
        color: var(--text) !important;
        border: none !important;
        border-bottom: 1px solid transparent !important;
        border-radius: 0 !important;
        font-family:
            "Cormorant Garamond",
            Georgia,
            serif !important;
        font-size: 17px !important;
        font-weight: 600 !important;
        transition: all .2s ease !important;
    }}

    .stButton > button:hover {{
        background: transparent !important;
        color: var(--accent) !important;
        border-bottom-color: var(--accent) !important;
    }}

    /* ========================================================
       INPUTS
       ======================================================== */

    div[data-baseweb="input"] > div {{
        background: var(--surface) !important;
        border-color: var(--line) !important;
        border-radius: 3px !important;
    }}

    div[data-baseweb="input"] input {{
        color: var(--text) !important;
    }}

    textarea {{
        background: var(--surface) !important;
        color: var(--text) !important;
    }}

    /* ========================================================
       TABS
       ======================================================== */

    button[data-baseweb="tab"] {{
        font-family:
            "Cormorant Garamond",
            Georgia,
            serif !important;
        font-size: 17px !important;
        color: var(--muted) !important;
    }}

    button[data-baseweb="tab"][aria-selected="true"] {{
        color: var(--accent) !important;
    }}

    /* ========================================================
       GENERAL STREAMLIT CLEANUP
       ======================================================== */

    [data-testid="stMetric"] {{
        background: transparent !important;
    }}

    [data-testid="stFileUploader"] {{
        background: var(--surface) !important;
        border: 1px solid var(--line);
    }}

    </style>
    """
)

# ============================================================
# HEADER
# ============================================================

st.html(
    """
    <div class="book-header">

        <div class="book-header-title">
            My Book Tree
        </div>

        <div class="willow-wrapper">

            <svg
                viewBox="0 0 1000 285"
                preserveAspectRatio="xMidYMid meet"
                xmlns="http://www.w3.org/2000/svg"
            >

                <!-- CENTRAL TRUNK -->

                <path
                    d="
                    M500 285
                    C490 235 488 185 495 140
                    C500 105 510 70 525 38
                    "
                    fill="none"
                    class="willow-trunk"
                    stroke-width="24"
                    stroke-linecap="round"
                />

                <path
                    d="
                    M503 280
                    C498 230 498 185 503 142
                    C508 105 518 70 530 42
                    "
                    fill="none"
                    class="willow-highlight"
                    stroke-width="6"
                    stroke-linecap="round"
                />

                <!-- MAIN LEFT BRANCHES -->

                <g
                    fill="none"
                    class="willow-branch"
                    stroke-linecap="round"
                >

                    <path
                        d="M500 150 C435 118 370 92 285 75"
                        stroke-width="12"
                    />

                    <path
                        d="M495 175 C420 150 345 140 250 148"
                        stroke-width="9"
                    />

                    <path
                        d="M505 120 C455 82 420 48 395 15"
                        stroke-width="8"
                    />

                    <path
                        d="M500 138 C450 110 405 75 350 48"
                        stroke-width="8"
                    />

                </g>

                <!-- MAIN RIGHT BRANCHES -->

                <g
                    fill="none"
                    class="willow-branch"
                    stroke-linecap="round"
                >

                    <path
                        d="M515 145 C580 112 650 85 730 70"
                        stroke-width="12"
                    />

                    <path
                        d="M510 175 C585 145 665 135 755 145"
                        stroke-width="9"
                    />

                    <path
                        d="M515 115 C565 78 600 45 625 12"
                        stroke-width="8"
                    />

                    <path
                        d="M515 138 C570 105 620 72 675 45"
                        stroke-width="8"
                    />

                </g>

                <!-- LEFT CASCADING BRANCHES -->

                <g
                    fill="none"
                    class="willow-branch-light"
                    stroke-width="3"
                    stroke-linecap="round"
                >

                    <path d="M285 75 C275 125 285 175 300 235"/>
                    <path d="M330 78 C320 135 330 195 345 250"/>
                    <path d="M375 88 C365 145 375 205 390 260"/>
                    <path d="M420 100 C410 155 420 210 435 250"/>

                    <path d="M250 148 C245 190 250 225 260 265"/>

                </g>

                <!-- RIGHT CASCADING BRANCHES -->

                <g
                    fill="none"
                    class="willow-branch-light"
                    stroke-width="3"
                    stroke-linecap="round"
                >

                    <path d="M730 70 C740 125 730 175 715 235"/>
                    <path d="M685 78 C695 135 685 195 670 250"/>
                    <path d="M640 88 C650 145 640 205 625 260"/>
                    <path d="M595 100 C605 155 595 210 580 250"/>

                    <path d="M755 145 C760 190 755 225 745 265"/>

                </g>

                <!-- LEFT LEAVES -->

                <g>

                    <ellipse
                        class="willow-leaf"
                        cx="280"
                        cy="115"
                        rx="7"
                        ry="19"
                        transform="rotate(-20 280 115)"
                    />

                    <ellipse
                        class="willow-leaf-light"
                        cx="300"
                        cy="155"
                        rx="7"
                        ry="21"
                        transform="rotate(18 300 155)"
                    />

                    <ellipse
                        class="willow-leaf-deep"
                        cx="320"
                        cy="195"
                        rx="7"
                        ry="20"
                        transform="rotate(-15 320 195)"
                    />

                    <ellipse
                        class="willow-leaf"
                        cx="345"
                        cy="220"
                        rx="7"
                        ry="22"
                        transform="rotate(17 345 220)"
                    />

                    <ellipse
                        class="willow-leaf-light"
                        cx="375"
                        cy="130"
                        rx="7"
                        ry="21"
                        transform="rotate(-18 375 130)"
                    />

                    <ellipse
                        class="willow-leaf-deep"
                        cx="400"
                        cy="180"
                        rx="7"
                        ry="22"
                        transform="rotate(16 400 180)"
                    />

                    <ellipse
                        class="willow-leaf"
                        cx="425"
                        cy="220"
                        rx="7"
                        ry="20"
                        transform="rotate(-18 425 220)"
                    />

                    <ellipse
                        class="willow-leaf-light"
                        cx="250"
                        cy="205"
                        rx="7"
                        ry="20"
                        transform="rotate(-15 250 205)"
                    />

                    <ellipse
                        class="willow-leaf"
                        cx="260"
                        cy="245"
                        rx="7"
                        ry="21"
                        transform="rotate(15 260 245)"
                    />

                </g>

                <!-- RIGHT LEAVES -->

                <g>

                    <ellipse
                        class="willow-leaf"
                        cx="720"
                        cy="115"
                        rx="7"
                        ry="19"
                        transform="rotate(20 720 115)"
                    />

                    <ellipse
                        class="willow-leaf-light"
                        cx="700"
                        cy="155"
                        rx="7"
                        ry="21"
                        transform="rotate(-18 700 155)"
                    />

                    <ellipse
                        class="willow-leaf-deep"
                        cx="680"
                        cy="195"
                        rx="7"
                        ry="20"
                        transform="rotate(15 680 195)"
                    />

                    <ellipse
                        class="willow-leaf"
                        cx="655"
                        cy="220"
                        rx="7"
                        ry="22"
                        transform="rotate(-17 655 220)"
                    />

                    <ellipse
                        class="willow-leaf-light"
                        cx="625"
                        cy="130"
                        rx="7"
                        ry="21"
                        transform="rotate(18 625 130)"
                    />

                    <ellipse
                        class="willow-leaf-deep"
                        cx="600"
                        cy="180"
                        rx="7"
                        ry="22"
                        transform="rotate(-16 600 180)"
                    />

                    <ellipse
                        class="willow-leaf"
                        cx="575"
                        cy="220"
                        rx="7"
                        ry="20"
                        transform="rotate(18 575 220)"
                    />

                    <ellipse
                        class="willow-leaf-light"
                        cx="750"
                        cy="205"
                        rx="7"
                        ry="20"
                        transform="rotate(15 750 205)"
                    />

                    <ellipse
                        class="willow-leaf"
                        cx="740"
                        cy="245"
                        rx="7"
                        ry="21"
                        transform="rotate(-15 740 245)"
                    />

                </g>

                <!-- SMALL ROSE BLOSSOMS -->

                <g class="willow-flower">

                    <circle cx="330" cy="105" r="4"/>
                    <circle cx="380" cy="145" r="4"/>
                    <circle cx="425" cy="175" r="4"/>

                    <circle cx="670" cy="145" r="4"/>
                    <circle cx="620" cy="105" r="4"/>
                    <circle cx="575" cy="175" r="4"/>

                </g>

            </svg>

        </div>

    </div>
    """
)

# ============================================================
# THEME PICKER
# ============================================================

st.html(
    '<div class="theme-heading">Choose your storybook</div>'
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
        r"\(([^()]+?)\s*#\s*(\d+(?:\.\d+)?)\)",
        r"\[([^\[\]]+?)\s*#\s*(\d+(?:\.\d+)?)\]",
        r"\(([^()]+?)\s*\bBook\s+(\d+(?:\.\d+)?)\)",
        r"\[([^\[\]]+?)\s*\bBook\s+(\d+(?:\.\d+)?)\]",
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
            placeholder=(
                "Search author, series, or book..."
            )
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

            author_id = safe_id(
                author
            )

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
                                                {html.escape(
                                                    str(
                                                        book.get(
                                                            "Status",
                                                            ""
                                                        )
                                                    )
                                                )}
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
                                        {html.escape(
                                            str(
                                                book.get(
                                                    "Status",
                                                    ""
                                                )
                                            )
                                        )}
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
                                            {html.escape(
                                                str(
                                                    book.get(
                                                        "Status",
                                                        ""
                                                    )
                                                )
                                            )}
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
                                    {html.escape(
                                        str(
                                            book.get(
                                                "Status",
                                                ""
                                            )
                                        )
                                    )}
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
