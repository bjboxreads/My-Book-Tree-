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
    "Rosewood Library": {
        "page": "#160B10",
        "surface": "#251019",
        "surface2": "#351521",
        "card": "#43202C",
        "text": "#F9EBDD",
        "muted": "#D9BFC5",
        "accent": "#D99A9F",
        "accent2": "#B98576",
        "line": "#8E5260",
        "leaf": "#667052",
        "branch": "#4A3028",
    },

    "Burgundy & Blush": {
        "page": "#1B0B12",
        "surface": "#2B101B",
        "surface2": "#421726",
        "card": "#542131",
        "text": "#FFF0E8",
        "muted": "#DDBFC4",
        "accent": "#E5A0A8",
        "accent2": "#C77D88",
        "line": "#965061",
        "leaf": "#687653",
        "branch": "#4B3029",
    },

    "Antique Rose": {
        "page": "#211317",
        "surface": "#342026",
        "surface2": "#493039",
        "card": "#60404A",
        "text": "#FFF4E6",
        "muted": "#DCC8C4",
        "accent": "#D9A6A1",
        "accent2": "#B99386",
        "line": "#9D6968",
        "leaf": "#697454",
        "branch": "#50342C",
    },

    "Plum & Dusty Rose": {
        "page": "#150C18",
        "surface": "#261326",
        "surface2": "#38203A",
        "card": "#4A2A4A",
        "text": "#F9ECF0",
        "muted": "#D5BFD0",
        "accent": "#D5A0B8",
        "accent2": "#B88AA8",
        "line": "#825477",
        "leaf": "#687451",
        "branch": "#49312E",
    },

    "Old Bookshop": {
        "page": "#1B1510",
        "surface": "#2C2118",
        "surface2": "#403025",
        "card": "#584337",
        "text": "#F7E8D0",
        "muted": "#D6C0A5",
        "accent": "#D6A86A",
        "accent2": "#B98772",
        "line": "#8C654D",
        "leaf": "#687153",
        "branch": "#4B352B",
    },

    "Midnight Rose": {
        "page": "#0F0B16",
        "surface": "#1E1425",
        "surface2": "#30203A",
        "card": "#432C4D",
        "text": "#F8EAF0",
        "muted": "#CDBBC8",
        "accent": "#D7A0B5",
        "accent2": "#A989B7",
        "line": "#765278",
        "leaf": "#63704F",
        "branch": "#43302C",
    },
}

# ============================================================
# SESSION STATE
# ============================================================

if (
    "theme" not in st.session_state
    or st.session_state.theme not in THEMES
):
    st.session_state.theme = "Rosewood Library"

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
    'https://fonts.googleapis.com/css2?family=Berkshire+Swash&family=Cormorant+Garamond:wght@400;500;600;700&family=Libre+Baskerville:wght@400;700&display=swap'
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
    --leaf: {theme["leaf"]};
    --branch: {theme["branch"]};
}}

.stApp {{
    background:
        radial-gradient(
            ellipse at 50% -15%,
            var(--surface2) 0%,
            var(--page) 58%
        );
    color: var(--text);
}}

.block-container {{
    max-width: 1450px;
    padding-top: 1.2rem;
    padding-bottom: 4rem;
}}

* {{
    box-sizing: border-box;
}}

/* =========================================================
   GLOBAL TYPE
   ========================================================= */

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

.stMarkdown,
.stText,
.stCaption {{
    font-family:
        "Cormorant Garamond",
        Georgia,
        serif;
}}

/* =========================================================
   HEADER
   ========================================================= */

.book-header {{
    position: relative;
    text-align: center;
    padding: 24px 0 26px;
    margin-bottom: 8px;
}}

.book-header::before,
.book-header::after {{
    content: "❦";
    position: absolute;
    top: 42%;
    transform: translateY(-50%);
    color: var(--accent);
    font-size: 32px;
    opacity: .8;
}}

.book-header::before {{
    left: 25%;
}}

.book-header::after {{
    right: 25%;
    transform: translateY(-50%) scaleX(-1);
}}

.book-header-title {{
    font-family:
        "Berkshire Swash",
        Georgia,
        serif;
    font-size: 70px;
    line-height: 1;
    color: var(--accent);
    text-shadow:
        0 3px 12px rgba(0,0,0,.35);
    letter-spacing: .01em;
}}

.header-ornament {{
    margin: 14px auto 0;
    width: 280px;
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
    position: relative;
}}

.header-ornament::after {{
    content: "✦";
    position: absolute;
    left: 50%;
    top: 50%;
    transform: translate(-50%, -50%);
    background: var(--page);
    padding: 0 12px;
    color: var(--accent);
    font-size: 14px;
}}

/* =========================================================
   THEME AREA
   ========================================================= */

.theme-wrap {{
    max-width: 650px;
    margin: 0 auto 28px;
    text-align: center;
}}

.theme-heading {{
    font-family:
        "Berkshire Swash",
        Georgia,
        serif;
    font-size: 22px;
    color: var(--accent);
    margin-bottom: 6px;
}}

.theme-note {{
    font-family:
        "Cormorant Garamond",
        Georgia,
        serif;
    font-size: 15px;
    color: var(--muted);
    margin-bottom: 8px;
}}

/* Selectbox */

div[data-baseweb="select"] > div {{
    background:
        linear-gradient(
            135deg,
            var(--surface),
            var(--surface2)
        ) !important;
    border: 1px solid var(--line) !important;
    border-radius: 5px !important;
    min-height: 46px !important;
    box-shadow:
        0 4px 18px rgba(0,0,0,.18) !important;
}}

div[data-baseweb="select"] span {{
    color: var(--text) !important;
    font-family:
        "Cormorant Garamond",
        Georgia,
        serif !important;
    font-size: 16px !important;
}}

div[data-baseweb="select"] input {{
    color: var(--text) !important;
}}

div[role="listbox"] {{
    background: var(--surface) !important;
    border: 1px solid var(--line) !important;
    border-radius: 5px !important;
}}

div[role="option"] {{
    background: var(--surface) !important;
    color: var(--text) !important;
    font-family:
        "Cormorant Garamond",
        Georgia,
        serif !important;
    font-size: 16px !important;
    padding: 11px 14px !important;
}}

div[role="option"]:hover {{
    background: var(--surface2) !important;
}}

div[role="option"][aria-selected="true"] {{
    background: var(--card) !important;
    color: var(--accent) !important;
}}

/* =========================================================
   STATS — ORNAMENTAL, NOT BOXES
   ========================================================= */

.stats-row {{
    display: flex;
    justify-content: center;
    align-items: stretch;
    gap: 0;
    margin: 22px auto 34px;
    max-width: 900px;
}}

.stat-card {{
    flex: 1;
    text-align: center;
    padding: 4px 22px 8px;
    position: relative;
    background: transparent;
}}

.stat-card:not(:last-child)::after {{
    content: "❦";
    position: absolute;
    right: -7px;
    top: 50%;
    transform: translateY(-50%);
    color: var(--line);
    font-size: 17px;
}}

.stat-number {{
    font-family:
        "Berkshire Swash",
        Georgia,
        serif;
    font-size: 34px;
    color: var(--accent);
    line-height: 1;
}}

.stat-label {{
    margin-top: 5px;
    font-family:
        "Cormorant Garamond",
        Georgia,
        serif;
    font-size: 14px;
    letter-spacing: .12em;
    text-transform: uppercase;
    color: var(--muted);
}}

/* =========================================================
   TABS
   ========================================================= */

.stTabs [data-baseweb="tab-list"] {{
    gap: 28px;
    justify-content: center;
    border-bottom: 1px solid var(--line);
}}

.stTabs [data-baseweb="tab"] {{
    font-family:
        "Cormorant Garamond",
        Georgia,
        serif !important;
    font-size: 18px !important;
    color: var(--muted) !important;
    padding: 10px 8px !important;
}}

.stTabs [aria-selected="true"] {{
    color: var(--accent) !important;
}}

.stTabs [data-baseweb="tab-highlight"] {{
    background: var(--accent) !important;
    height: 2px !important;
}}

/* =========================================================
   TREE SEARCH
   ========================================================= */

.tree-search-label {{
    font-family:
        "Berkshire Swash",
        Georgia,
        serif;
    color: var(--accent);
    font-size: 22px;
    margin-bottom: 5px;
}}

div[data-baseweb="input"] > div {{
    background: rgba(0,0,0,.13) !important;
    border: none !important;
    border-bottom: 1px solid var(--line) !important;
    border-radius: 0 !important;
}}

div[data-baseweb="input"] input {{
    color: var(--text) !important;
    font-family:
        "Cormorant Garamond",
        Georgia,
        serif !important;
    font-size: 17px !important;
}}

/* =========================================================
   TREE STAGE
   ========================================================= */

.tree-area {{
    position: relative;
    min-height: 230px;
    margin: 20px 0 24px;
    padding: 30px 20px 25px;
    overflow: hidden;

    background:
        radial-gradient(
            ellipse at center,
            rgba(255,255,255,.025),
            transparent 70%
        );

    border-top: 1px solid var(--line);
    border-bottom: 1px solid var(--line);
}}

.tree-area::before {{
    content: "✦   ❦   ✦";
    display: block;
    text-align: center;
    color: var(--line);
    font-size: 17px;
    letter-spacing: 12px;
    margin-bottom: 18px;
}}

/* =========================================================
   ROOT
   ========================================================= */

.root-node {{
    width: min(430px, 90%);
    margin: 0 auto;
    padding: 14px 24px 17px;
    text-align: center;
    position: relative;
    background:
        linear-gradient(
            135deg,
            var(--surface2),
            var(--card)
        );
    border: 1px solid var(--accent2);
    border-radius: 3px;
    box-shadow:
        0 10px 25px rgba(0,0,0,.22);
}}

.root-node::before,
.root-node::after {{
    content: "❦";
    position: absolute;
    top: 50%;
    transform: translateY(-50%);
    color: var(--accent);
    font-size: 20px;
}}

.root-node::before {{
    left: 16px;
}}

.root-node::after {{
    right: 16px;
    transform: translateY(-50%) scaleX(-1);
}}

.root-node-title {{
    font-family:
        "Berkshire Swash",
        Georgia,
        serif;
    color: var(--accent) !important;
    font-size: 31px;
}}

.root-node-small {{
    margin-top: 2px;
    color: var(--muted) !important;
    font-family:
        "Cormorant Garamond",
        Georgia,
        serif;
    font-size: 14px;
}}

/* =========================================================
   AUTHOR BRANCH
   ========================================================= */

.author-info {{
    position: relative;
    margin: 14px 0 5px;
    padding: 7px 18px 8px 34px;

    background: transparent;

    border-left: 1px solid var(--line);
}}

.author-info::before {{
    content: "";
    position: absolute;
    left: 0;
    top: 0;
    width: 26px;
    height: 1px;
    background: var(--line);
}}

.author-name {{
    font-family:
        "Berkshire Swash",
        Georgia,
        serif;
    font-size: 27px;
    color: var(--accent);
}}

.author-count {{
    font-family:
        "Cormorant Garamond",
        Georgia,
        serif;
    font-size: 13px;
    color: var(--muted);
}}

/* =========================================================
   SERIES
   ========================================================= */

.series-info {{
    position: relative;
    margin: 8px 0 5px 55px;
    padding: 7px 16px 7px 25px;
    background: transparent;
    border-left: 1px solid var(--accent2);
}}

.series-info::before {{
    content: "";
    position: absolute;
    left: 0;
    top: 0;
    width: 18px;
    height: 1px;
    background: var(--accent2);
}}

.series-name {{
    font-family:
        "Cormorant Garamond",
        Georgia,
        serif;
    font-size: 23px;
    font-weight: 700;
    color: var(--text);
}}

.series-count {{
    font-family:
        "Cormorant Garamond",
        Georgia,
        serif;
    color: var(--muted);
    font-size: 13px;
}}

/* =========================================================
   BOOKS
   ========================================================= */

.book-info {{
    position: relative;
    margin: 7px 0 7px 112px;
    padding: 7px 14px 7px 22px;
    background: rgba(255,255,255,.025);
    border-left: 1px solid var(--line);
    transition: background .2s ease;
}}

.book-info:hover {{
    background: rgba(255,255,255,.055);
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
        "Cormorant Garamond",
        Georgia,
        serif;
    font-size: 14px;
    margin-top: 2px;
}}

.book-cover {{
    width: 58px;
    height: 84px;
    object-fit: cover;
    border: 1px solid var(--accent2);
    border-radius: 2px;
    box-shadow:
        3px 4px 10px rgba(0,0,0,.35);
}}

/* =========================================================
   TREE BUTTONS
   ========================================================= */

.stButton {{
    margin-bottom: -7px !important;
}}

.stButton > button {{
    background: transparent !important;
    color: var(--text) !important;
    border: none !important;
    box-shadow: none !important;

    font-family:
        "Cormorant Garamond",
        Georgia,
        serif !important;

    font-size: 17px !important;
    text-align: left !important;

    padding: 4px 10px !important;
}}

.stButton > button:hover {{
    background: transparent !important;
    color: var(--accent) !important;
    border: none !important;
}}

/* =========================================================
   BOOKS TAB
   ========================================================= */

.book-list-row {{
    border-bottom: 1px solid rgba(255,255,255,.08);
    padding: 10px 0;
}}

/* =========================================================
   FORM ELEMENTS
   ========================================================= */

.stTextInput label,
.stNumberInput label,
.stSelectbox label,
.stSlider label,
.stCheckbox label,
.stFileUploader label,
.stRadio label {{
    font-family:
        "Cormorant Garamond",
        Georgia,
        serif !important;
    color: var(--text) !important;
    font-size: 16px !important;
}}

textarea {{
    background: var(--surface) !important;
    color: var(--text) !important;
}}

.stTextInput input,
.stNumberInput input {{
    font-family:
        "Cormorant Garamond",
        Georgia,
        serif !important;
}}

/* =========================================================
   GENERAL BUTTONS
   ========================================================= */

button[kind="primary"] {{
    background:
        linear-gradient(
            135deg,
            var(--accent2),
            var(--accent)
        ) !important;

    color: var(--page) !important;

    border: none !important;
    border-radius: 3px !important;

    font-family:
        "Cormorant Garamond",
        Georgia,
        serif !important;

    font-size: 17px !important;
    font-weight: 700 !important;
}}

button[kind="primary"]:hover {{
    filter: brightness(1.08);
}}

/* =========================================================
   INFO / SUCCESS / ERROR
   ========================================================= */

div[data-testid="stAlert"] {{
    background: rgba(255,255,255,.035) !important;
    border-left: 2px solid var(--accent) !important;
    border-radius: 0 !important;
}}

div[data-testid="stAlert"] p {{
    font-family:
        "Cormorant Garamond",
        Georgia,
        serif !important;
    font-size: 16px !important;
}}

/* =========================================================
   RADIO
   ========================================================= */

div[role="radiogroup"] label {{
    color: var(--muted) !important;
    font-family:
        "Cormorant Garamond",
        Georgia,
        serif !important;
}}

/* =========================================================
   FILE UPLOADER
   ========================================================= */

[data-testid="stFileUploaderDropzone"] {{
    background: rgba(255,255,255,.025) !important;
    border: 1px dashed var(--line) !important;
    border-radius: 3px !important;
}}

/* =========================================================
   MOBILE
   ========================================================= */

@media (max-width: 800px) {{

    .book-header-title {{
        font-size: 48px;
    }}

    .book-header::before {{
        left: 8%;
    }}

    .book-header::after {{
        right: 8%;
    }}

    .stats-row {{
        flex-wrap: wrap;
    }}

    .stat-card {{
        min-width: 30%;
    }}

    .book-info {{
        margin-left: 55px;
    }}

    .series-info {{
        margin-left: 28px;
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
    <div class="book-header">

        <div class="book-header-title">
            My Book Tree
        </div>

        <div class="header-ornament"></div>

    </div>
    """
)

# ============================================================
# THEME SELECTOR
# ============================================================

st.html(
    """
    <div class="theme-wrap">
        <div class="theme-heading">
            Choose Your Bookish World
        </div>
        <div class="theme-note">
            A little atmosphere for your library
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

stats = [
    (total, "Books"),
    (authors, "Authors"),
    (series_count, "Series"),
    (read_count, "Read"),
    (favorites, "Favorites"),
]

st.html(
    '<div class="stats-row">'
    + "".join(
        f"""
        <div class="stat-card">
            <div class="stat-number">{number}</div>
            <div class="stat-label">{label}</div>
        </div>
        """
        for number, label in stats
    )
    + "</div>"
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

    st.html(
        """
        <div class="tree-search-label">
            Search the library
        </div>
        """
    )

    search = st.text_input(
        "Search your tree",
        placeholder="Author, series, or book...",
        label_visibility="collapsed"
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

    if filtered.empty:

        st.info(
            "No books match your search."
        )

    else:

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

    st.markdown(
        "## Add a Book"
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

    st.markdown(
        "## Import Your Library"
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
