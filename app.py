import streamlit as st
import pandas as pd
import requests
import re
import html
import time

# ============================================================
# PAGE SETTINGS
# ============================================================

st.set_page_config(
    page_title="My Book Tree",
    page_icon="🌿",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ============================================================
# BOOKISH THEMES
# ============================================================

THEMES = {
    "Emerald Conservatory": {
        "page": "#081A16",
        "surface": "#102A23",
        "surface2": "#183D32",
        "card": "#245447",
        "text": "#FFF7E5",
        "muted": "#D3D6C5",
        "accent": "#D9AD4B",
        "accent2": "#89B99E",
        "line": "#9A7633",
        "rose": "#C9787D",
    },

    "Sapphire Reading Room": {
        "page": "#081326",
        "surface": "#102441",
        "surface2": "#18365A",
        "card": "#244A72",
        "text": "#FFF8E8",
        "muted": "#D0D8E3",
        "accent": "#E5BC58",
        "accent2": "#7EB4D1",
        "line": "#A77A32",
        "rose": "#C77E96",
    },

    "Gothic Garden": {
        "page": "#160A15",
        "surface": "#291126",
        "surface2": "#421735",
        "card": "#592243",
        "text": "#FFF4F2",
        "muted": "#DEC8D2",
        "accent": "#E5A0A8",
        "accent2": "#C69AD8",
        "line": "#A8506B",
        "rose": "#E36D88",
    },

    "Autumn Bookshop": {
        "page": "#211108",
        "surface": "#37200F",
        "surface2": "#563116",
        "card": "#70431F",
        "text": "#FFF2D7",
        "muted": "#DEC6A3",
        "accent": "#E2AE48",
        "accent2": "#D7794E",
        "line": "#A9572F",
        "rose": "#B85D56",
    },

    "Midnight Storybook": {
        "page": "#0C0A20",
        "surface": "#151234",
        "surface2": "#211B50",
        "card": "#30276A",
        "text": "#FFF8E9",
        "muted": "#D2CBE7",
        "accent": "#E7C453",
        "accent2": "#9A7BE0",
        "line": "#6D56AE",
        "rose": "#D77FA3",
    },

    "Teal & Coral Bookshop": {
        "page": "#072329",
        "surface": "#0D3B42",
        "surface2": "#14565C",
        "card": "#1C6D71",
        "text": "#FFF7E5",
        "muted": "#D0D9D2",
        "accent": "#F0C257",
        "accent2": "#F27B65",
        "line": "#D25C4D",
        "rose": "#E28B8D",
    },

    "Vintage Botanical": {
        "page": "#15201D",
        "surface": "#243631",
        "surface2": "#354D45",
        "card": "#48655A",
        "text": "#FFF3D9",
        "muted": "#D5D5C5",
        "accent": "#D9AC4C",
        "accent2": "#A9BA73",
        "line": "#B47C32",
        "rose": "#C9837B",
    },

    "Electric Bookstore": {
        "page": "#101124",
        "surface": "#1B1D3A",
        "surface2": "#292D59",
        "card": "#363C78",
        "text": "#FFFFFF",
        "muted": "#D5D7EA",
        "accent": "#F2C94C",
        "accent2": "#6ED9D0",
        "line": "#A96BDD",
        "rose": "#F083A5",
    },

    "Classic Crimson": {
        "page": "#200B0C",
        "surface": "#351314",
        "surface2": "#531C1D",
        "card": "#6B2928",
        "text": "#FFF4E0",
        "muted": "#DEC9B4",
        "accent": "#E4B74D",
        "accent2": "#D87A5D",
        "line": "#A84337",
        "rose": "#C96870",
    },
}

# ============================================================
# SESSION STATE
# ============================================================

if "theme" not in st.session_state:
    st.session_state.theme = "Emerald Conservatory"

if st.session_state.theme not in THEMES:
    st.session_state.theme = "Emerald Conservatory"

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
            "Genre",
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

if "loading_done" not in st.session_state:
    st.session_state.loading_done = False

theme = THEMES[st.session_state.theme]

# ============================================================
# GLOBAL CSS
# ============================================================

st.html(
    f"""
<style>

@import url(
'https://fonts.googleapis.com/css2?family=Cormorant+Garamond:wght@400;500;600;700'
'&family=Libre+Baskerville:wght@400;700'
'&family=Playfair+Display:ital,wght@0,500;0,600;1,500;1,600'
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
    --rose: {theme["rose"]};
}}

html,
body,
[data-testid="stAppViewContainer"] {{
    background: var(--page) !important;
}}

.stApp {{
    background:
        radial-gradient(
            ellipse at 50% -10%,
            var(--surface2) 0%,
            var(--page) 55%
        ) !important;
    color: var(--text) !important;
}}

.block-container {{
    max-width: 1450px !important;
    padding-top: 1rem !important;
    padding-bottom: 4rem !important;
}}

h1, h2, h3, h4, h5, h6 {{
    font-family:
        "Cormorant Garamond",
        Georgia,
        serif !important;
    color: var(--text) !important;
}}

p, label {{
    color: var(--text) !important;
}}

/* ============================================================
   HEADER
============================================================ */

.hero {{
    text-align: center;
    padding: 22px 0 10px;
}}

.hero-title {{
    font-family:
        "Playfair Display",
        Georgia,
        serif;
    font-size: 68px;
    line-height: 1;
    font-weight: 600;
    font-style: italic;
    color: var(--text);
    text-shadow:
        0 3px 15px rgba(0,0,0,.35);
}}

.hero-subtitle {{
    font-family:
        "Libre Baskerville",
        Georgia,
        serif;
    font-size: 13px;
    letter-spacing: .09em;
    color: var(--muted);
    margin-top: 12px;
}}

/* ============================================================
   DECORATIVE VINE
============================================================ */

.divider-vine {{
    position: relative;
    height: 58px;
    margin: 4px auto 15px;
    max-width: 900px;
    overflow: hidden;
}}

.vine-line {{
    position: absolute;
    left: 4%;
    right: 4%;
    top: 28px;
    height: 3px;
    background: var(--accent2);
    border-radius: 50%;
    transform: rotate(-1deg);
    opacity: .9;
}}

.vine-line::before,
.vine-line::after {{
    content: "";
    position: absolute;
    width: 180px;
    height: 28px;
    border: 3px solid var(--accent2);
    border-color: var(--accent2) transparent transparent transparent;
    border-radius: 50%;
}}

.vine-line::before {{
    left: 8%;
    top: -17px;
    transform: rotate(7deg);
}}

.vine-line::after {{
    right: 8%;
    top: 5px;
    transform: rotate(-8deg);
}}

.leaf {{
    position: absolute;
    width: 13px;
    height: 23px;
    background: var(--accent2);
    border-radius: 100% 0 100% 0;
}}

.leaf.one {{
    left: 20%;
    top: 10px;
    transform: rotate(-35deg);
}}

.leaf.two {{
    left: 35%;
    top: 30px;
    transform: rotate(45deg);
}}

.leaf.three {{
    right: 35%;
    top: 8px;
    transform: rotate(-25deg);
}}

.leaf.four {{
    right: 20%;
    top: 28px;
    transform: rotate(45deg);
}}

.flower {{
    position: absolute;
    left: 50%;
    top: 17px;
    transform: translateX(-50%);
    font-size: 25px;
    color: var(--accent);
}}

/* ============================================================
   LOADING SCREEN
============================================================ */

.loading-screen {{
    text-align: center;
    padding: 35px 20px 60px;
}}

.loading-title {{
    font-family:
        "Playfair Display",
        Georgia,
        serif;
    font-size: 38px;
    font-style: italic;
    color: var(--text);
}}

.loading-vine {{
    height: 100px;
    position: relative;
    max-width: 950px;
    margin: 20px auto;
}}

.loading-stem {{
    position: absolute;
    width: 92%;
    height: 5px;
    background: var(--accent2);
    top: 48px;
    left: 4%;
    border-radius: 50%;
    transform: rotate(-2deg);
    animation: growvine 2.2s ease-out forwards;
    transform-origin: left center;
}}

@keyframes growvine {{
    from {{
        transform: scaleX(0) rotate(-2deg);
    }}
    to {{
        transform: scaleX(1) rotate(-2deg);
    }}
}}

.loading-leaf {{
    position: absolute;
    width: 18px;
    height: 32px;
    background: var(--accent2);
    border-radius: 100% 0 100% 0;
    opacity: 0;
    animation: appearleaf .6s ease forwards;
}}

.loading-leaf:nth-child(2) {{
    left: 15%;
    top: 27px;
    transform: rotate(-35deg);
    animation-delay: .4s;
}}

.loading-leaf:nth-child(3) {{
    left: 30%;
    top: 55px;
    transform: rotate(40deg);
    animation-delay: .8s;
}}

.loading-leaf:nth-child(4) {{
    left: 47%;
    top: 20px;
    transform: rotate(-30deg);
    animation-delay: 1.2s;
}}

.loading-leaf:nth-child(5) {{
    right: 31%;
    top: 57px;
    transform: rotate(42deg);
    animation-delay: 1.5s;
}}

.loading-leaf:nth-child(6) {{
    right: 15%;
    top: 24px;
    transform: rotate(-35deg);
    animation-delay: 1.8s;
}}

@keyframes appearleaf {{
    to {{
        opacity: 1;
    }}
}}

/* ============================================================
   THEME SELECTOR
============================================================ */

.theme-label {{
    font-family:
        "Cormorant Garamond",
        Georgia,
        serif;
    font-size: 23px;
    font-weight: 700;
    margin-bottom: 4px;
    color: var(--text);
}}

div[data-baseweb="select"] > div {{
    background: #171717 !important;
    border: 2px solid var(--accent) !important;
    border-radius: 10px !important;
    min-height: 48px !important;
}}

div[data-baseweb="select"] span {{
    color: #FFFFFF !important;
    font-weight: 700 !important;
}}

div[role="listbox"] {{
    background: #171717 !important;
    border: 2px solid #D9AD4B !important;
    border-radius: 10px !important;
    box-shadow:
        0 15px 45px rgba(0,0,0,.65) !important;
    padding: 5px !important;
}}

div[role="option"] {{
    background: #171717 !important;
    color: #FFFFFF !important;
    border-radius: 7px !important;
    padding: 12px 14px !important;
    font-family:
        "Libre Baskerville",
        Georgia,
        serif !important;
}}

div[role="option"] * {{
    color: #FFFFFF !important;
}}

div[role="option"]:hover {{
    background: #3C3C3C !important;
}}

div[role="option"][aria-selected="true"] {{
    background: #80601D !important;
}}

/* ============================================================
   STATS
============================================================ */

.stat-card {{
    background: var(--surface);
    border: 1px solid var(--line);
    border-radius: 16px;
    padding: 14px 8px;
    text-align: center;
    box-shadow:
        0 8px 22px rgba(0,0,0,.18);
}}

.stat-number {{
    font-family:
        "Playfair Display",
        Georgia,
        serif;
    font-size: 32px;
    color: var(--accent);
    font-weight: 600;
}}

.stat-label {{
    font-family:
        "Libre Baskerville",
        Georgia,
        serif;
    font-size: 9px;
    color: var(--muted);
    letter-spacing: .12em;
    text-transform: uppercase;
}}

/* ============================================================
   FIND / ORGANIZE PANEL
============================================================ */

.organize-panel {{
    margin-top: 25px;
    padding: 20px 22px;
    background: var(--surface);
    border: 1px solid var(--line);
    border-radius: 18px;
    box-shadow:
        0 10px 30px rgba(0,0,0,.16);
}}

.organize-title {{
    font-family:
        "Playfair Display",
        Georgia,
        serif;
    font-size: 25px;
    font-style: italic;
    color: var(--accent);
    margin-bottom: 3px;
}}

.organize-subtitle {{
    color: var(--muted);
    font-size: 11px;
    margin-bottom: 12px;
}}

/* ============================================================
   TREE
============================================================ */

.tree-area {{
    margin-top: 22px;
    padding: 28px 20px 45px;
    background:
        linear-gradient(
            135deg,
            rgba(255,255,255,.025),
            rgba(0,0,0,.08)
        );
    border: 1px solid var(--line);
    border-radius: 22px;
}}

.root-node {{
    width: 330px;
    margin: 0 auto 38px;
    padding: 18px 25px;
    background: var(--accent);
    border-radius: 60px;
    text-align: center;
    box-shadow:
        0 10px 30px rgba(0,0,0,.28);
}}

.root-title {{
    font-family:
        "Playfair Display",
        Georgia,
        serif;
    font-size: 30px;
    font-style: italic;
    font-weight: 600;
    color: var(--page);
}}

.root-small {{
    color: var(--page);
    font-size: 10px;
    font-weight: 700;
    opacity: .8;
}}

/* ============================================================
   TREE NODES
============================================================ */

.author-node {{
    margin: 10px 0 7px;
    padding: 12px 17px;
    background: var(--surface);
    border-left: 5px solid var(--accent);
    border-radius: 0 15px 15px 0;
    box-shadow:
        0 5px 15px rgba(0,0,0,.12);
}}

.author-name {{
    font-family:
        "Playfair Display",
        Georgia,
        serif;
    font-size: 25px;
    font-weight: 600;
}}

.author-count {{
    color: var(--muted);
    font-size: 10px;
    margin-top: 2px;
}}

.series-node {{
    margin: 7px 0 7px 45px;
    padding: 11px 15px;
    background: var(--surface2);
    border-left: 4px solid var(--accent2);
    border-radius: 0 13px 13px 0;
}}

.series-name {{
    font-family:
        "Cormorant Garamond",
        Georgia,
        serif;
    font-size: 23px;
    font-weight: 700;
}}

.series-count {{
    color: var(--muted);
    font-size: 10px;
}}

.book-node {{
    margin: 7px 0 7px 105px;
    padding: 10px 14px;
    background: var(--card);
    border-left: 2px solid var(--rose);
    border-radius: 0 11px 11px 0;
}}

.book-title {{
    font-family:
        "Cormorant Garamond",
        Georgia,
        serif;
    font-size: 21px;
    font-weight: 700;
    line-height: 1.1;
}}

.book-meta {{
    color: var(--muted);
    font-size: 10px;
    margin-top: 4px;
}}

.book-cover {{
    width: 58px;
    height: 82px;
    object-fit: cover;
    border-radius: 4px;
    border: 1px solid var(--accent);
    box-shadow:
        0 5px 12px rgba(0,0,0,.35);
}}

/* ============================================================
   BUTTONS
============================================================ */

.stButton > button {{
    background: var(--surface) !important;
    color: var(--text) !important;
    border: 1px solid var(--line) !important;
    border-radius: 9px !important;
    font-family:
        "Libre Baskerville",
        Georgia,
        serif !important;
    font-size: 12px !important;
}}

.stButton > button:hover {{
    background: var(--surface2) !important;
    border-color: var(--accent) !important;
    color: var(--text) !important;
}}

/* ============================================================
   INPUTS
============================================================ */

div[data-baseweb="input"] > div {{
    background: var(--surface) !important;
    border-color: var(--line) !important;
}}

div[data-baseweb="input"] input {{
    color: var(--text) !important;
}}

div[data-baseweb="input"] input::placeholder {{
    color: var(--muted) !important;
}}

div[data-baseweb="select"] {{
    color: var(--text) !important;
}}

textarea {{
    background: var(--surface) !important;
    color: var(--text) !important;
}}

/* ============================================================
   TABS
============================================================ */

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

/* ============================================================
   EXPANDERS
============================================================ */

[data-testid="stExpander"] {{
    background: var(--surface) !important;
    border: 1px solid var(--line) !important;
    border-radius: 12px !important;
}}

</style>
"""
)

# ============================================================
# LOADING VINE
# ============================================================

if not st.session_state.loading_done:

    st.html(
        """
        <div class="loading-screen">

            <div class="loading-title">
                Growing your book tree...
            </div>

            <div class="loading-vine">

                <div class="loading-stem"></div>

                <div class="loading-leaf"></div>
                <div class="loading-leaf"></div>
                <div class="loading-leaf"></div>
                <div class="loading-leaf"></div>
                <div class="loading-leaf"></div>

            </div>

        </div>
        """
    )

    time.sleep(2)

    st.session_state.loading_done = True
    st.rerun()

# ============================================================
# HEADER
# ============================================================

st.html(
    """
    <div class="hero">

        <div class="hero-title">
            My Book Tree
        </div>

        <div class="hero-subtitle">
            A little place for every story you've collected.
        </div>

        <div class="divider-vine">

            <div class="vine-line"></div>

            <div class="leaf one"></div>
            <div class="leaf two"></div>
            <div class="leaf three"></div>
            <div class="leaf four"></div>

            <div class="flower">✿</div>

        </div>

    </div>
    """
)

# ============================================================
# THEME PICKER
# ============================================================

st.html(
    '<div class="theme-label">Choose your bookish theme</div>'
)

theme_choice = st.selectbox(
    "Theme",
    list(THEMES.keys()),
    index=list(THEMES.keys()).index(
        st.session_state.theme
    ),
    label_visibility="collapsed",
)

if theme_choice != st.session_state.theme:

    st.session_state.theme = theme_choice
    st.rerun()

# ============================================================
# COVER LOOKUP
# ============================================================

@st.cache_data(show_spinner=False)
def get_cover(title, author="", isbn=""):

    isbn_clean = re.sub(
        r"\D",
        "",
        str(isbn)
    )

    if isbn_clean:

        url = (
            "https://covers.openlibrary.org/b/isbn/"
            f"{isbn_clean}-L.jpg"
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

    # Open Library search

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

    # Google Books fallback

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
# GENRE LOOKUP
# ============================================================

@st.cache_data(show_spinner=False)
def get_genre(title, author=""):

    try:

        response = requests.get(
            "https://www.googleapis.com/books/v1/volumes",
            params={
                "q": f'intitle:{title} inauthor:{author}',
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

                categories = (
                    items[0]
                    .get("volumeInfo", {})
                    .get("categories", [])
                )

                if categories:

                    category = categories[0]

                    # Turn things like
                    # "Fiction / Romance / Contemporary"
                    # into "Romance"

                    parts = [
                        x.strip()
                        for x in category.split("/")
                    ]

                    preferred = [
                        "Romance",
                        "Fantasy",
                        "Mystery",
                        "Thriller",
                        "Horror",
                        "Science Fiction",
                        "Historical",
                        "Young Adult",
                        "Biography",
                        "Memoir",
                        "History",
                        "Literary Fiction",
                        "Contemporary",
                        "Paranormal",
                        "Crime",
                    ]

                    for preferred_genre in preferred:

                        if any(
                            preferred_genre.lower()
                            in part.lower()
                            for part in parts
                        ):

                            return preferred_genre

                    if len(parts) > 1:

                        return parts[1]

                    return parts[0]

    except Exception:
        pass

    return "Uncategorized"


# ============================================================
# SERIES DETECTION
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
# IMPORT GOODREADS / CSV
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

                return columns[
                    name.lower()
                ]

        return None

    title_col = find_column(
        ["title", "book title"]
    )

    author_col = find_column(
        ["author", "authors"]
    )

    isbn_col = find_column(
        [
            "isbn13",
            "isbn"
        ]
    )

    rating_col = find_column(
        [
            "my rating",
            "rating"
        ]
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
                    ""
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
                "Genre": "",
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
            "No books were found in the CSV."
        )

        return False

    progress = st.progress(0)

    for i in range(
        len(new_library)
    ):

        title = new_library.loc[
            i,
            "Title"
        ]

        author = new_library.loc[
            i,
            "Author"
        ]

        isbn = new_library.loc[
            i,
            "ISBN"
        ]

        new_library.loc[
            i,
            "Cover"
        ] = get_cover(
            title,
            author,
            isbn
        )

        new_library.loc[
            i,
            "Genre"
        ] = get_genre(
            title,
            author
        )

        progress.progress(
            (i + 1)
            / len(new_library)
        )

    progress.empty()

    st.session_state.library = new_library

    st.session_state.open_authors = set()
    st.session_state.open_series = set()

    return True


# ============================================================
# LIBRARY DATA
# ============================================================

library = st.session_state.library

if not library.empty:

    # Make sure older saved libraries get
    # the new columns.

    for column, default in [
        ("Genre", "Uncategorized"),
        ("Favorite", False),
        ("Cover", ""),
    ]:

        if column not in library.columns:

            library[column] = default

# ============================================================
# STATS
# ============================================================

total = len(library)

author_count = (
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

want_count = (
    len(
        library[
            library["Status"]
            == "Want to Read"
        ]
    )
    if total
    else 0
)

favorite_count = (
    len(
        library[
            library["Favorite"] == True
        ]
    )
    if total
    else 0
)

# ============================================================
# STATS DISPLAY
# ============================================================

stats = [
    (total, "Books"),
    (author_count, "Authors"),
    (series_count, "Series"),
    (read_count, "Read"),
    (want_count, "To Read"),
    (favorite_count, "Favorites"),
]

stat_columns = st.columns(6)

for col, (
    number,
    label
) in zip(
    stat_columns,
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
        "🌿 My Book Tree",
        "📚 All Books",
        "✦ Add a Book",
        "↟ Import Library",
    ]
)

# ============================================================
# TREE TAB
# ============================================================

with tree_tab:

    if library.empty:

        st.html(
            """
            <div class="tree-area"
                 style="text-align:center;">

                <div class="root-title">
                    Your tree is waiting...
                </div>

                <p>
                    Import your Goodreads library
                    or add your first book.
                </p>

            </div>
            """
        )

    else:

        # ----------------------------------------------------
        # ORGANIZE / FIND
        # ----------------------------------------------------

        st.html(
            """
            <div class="organize-panel">

                <div class="organize-title">
                    Find & Organize Your Books
                </div>

                <div class="organize-subtitle">
                    Search, filter, or rearrange your library
                    without changing the tree itself.
                </div>

            </div>
            """
        )

        filter_columns = st.columns(
            [2.2, 1.3, 1.3, 1.5]
        )

        with filter_columns[0]:

            search = st.text_input(
                "Search",
                placeholder=(
                    "Title, author, series..."
                ),
                label_visibility="visible",
            )

        with filter_columns[1]:

            status_filter = st.selectbox(
                "Reading status",
                [
                    "All",
                    "Read",
                    "Currently Reading",
                    "Want to Read",
                ],
            )

        with filter_columns[2]:

            genre_values = sorted(
                [
                    str(x)
                    for x in library[
                        "Genre"
                    ]
                    .fillna("Uncategorized")
                    .unique()
                    if str(x).strip()
                ],
                key=lambda x: x.lower()
            )

            genre_filter = st.selectbox(
                "Genre",
                ["All Genres"] + genre_values,
            )

        with filter_columns[3]:

            favorites_only = st.checkbox(
                "Favorites only"
            )

        sort_columns = st.columns(
            [1.4, 2, 1.3]
        )

        with sort_columns[0]:

            find_by = st.selectbox(
                "Find by",
                [
                    "Everything",
                    "Author",
                    "Title",
                    "Series",
                    "Genre",
                ],
            )

        with sort_columns[1]:

            sort_by = st.selectbox(
                "Sort",
                [
                    "Author A–Z",
                    "Author Z–A",
                    "Title A–Z",
                    "Title Z–A",
                    "Series A–Z",
                    "Highest Rated",
                    "Lowest Rated",
                    "Newest First",
                    "Oldest First",
                ],
            )

        with sort_columns[2]:

            expand_mode = st.selectbox(
                "Tree view",
                [
                    "Collapsed",
                    "Authors Open",
                    "Everything Open",
                ],
            )

        # ----------------------------------------------------
        # FILTER
        # ----------------------------------------------------

        filtered = library.copy()

        if search:

            q = search.lower().strip()

            if find_by == "Author":

                mask = (
                    filtered["Author"]
                    .fillna("")
                    .astype(str)
                    .str.lower()
                    .str.contains(
                        q,
                        na=False
                    )
                )

            elif find_by == "Title":

                mask = (
                    filtered["Title"]
                    .fillna("")
                    .astype(str)
                    .str.lower()
                    .str.contains(
                        q,
                        na=False
                    )
                )

            elif find_by == "Series":

                mask = (
                    filtered["Series"]
                    .fillna("")
                    .astype(str)
                    .str.lower()
                    .str.contains(
                        q,
                        na=False
                    )
                )

            elif find_by == "Genre":

                mask = (
                    filtered["Genre"]
                    .fillna("")
                    .astype(str)
                    .str.lower()
                    .str.contains(
                        q,
                        na=False
                    )
                )

            else:

                mask = (
                    filtered["Title"]
                    .fillna("")
                    .astype(str)
                    .str.lower()
                    .str.contains(
                        q,
                        na=False
                    )
                    |
                    filtered["Author"]
                    .fillna("")
                    .astype(str)
                    .str.lower()
                    .str.contains(
                        q,
                        na=False
                    )
                    |
                    filtered["Series"]
                    .fillna("")
                    .astype(str)
                    .str.lower()
                    .str.contains(
                        q,
                        na=False
                    )
                    |
                    filtered["Genre"]
                    .fillna("")
                    .astype(str)
                    .str.lower()
                    .str.contains(
                        q,
                        na=False
                    )
                )

            filtered = filtered[
                mask
            ]

        if status_filter != "All":

            filtered = filtered[
                filtered["Status"]
                == status_filter
            ]

        if genre_filter != "All Genres":

            filtered = filtered[
                filtered["Genre"]
                == genre_filter
            ]

        if favorites_only:

            filtered = filtered[
                filtered["Favorite"] == True
            ]

        # ----------------------------------------------------
        # SORT
        # ----------------------------------------------------

        if sort_by == "Author A–Z":

            filtered = filtered.sort_values(
                "Author",
                key=lambda s:
                    s.astype(str).str.lower()
            )

        elif sort_by == "Author Z–A":

            filtered = filtered.sort_values(
                "Author",
                ascending=False,
                key=lambda s:
                    s.astype(str).str.lower()
            )

        elif sort_by == "Title A–Z":

            filtered = filtered.sort_values(
                "Title",
                key=lambda s:
                    s.astype(str).str.lower()
            )

        elif sort_by == "Title Z–A":

            filtered = filtered.sort_values(
                "Title",
                ascending=False,
                key=lambda s:
                    s.astype(str).str.lower()
            )

        elif sort_by == "Series A–Z":

            filtered = filtered.sort_values(
                "Series",
                key=lambda s:
                    s.astype(str).str.lower()
            )

        elif sort_by == "Highest Rated":

            filtered = filtered.sort_values(
                "My Rating",
                ascending=False,
                na_position="last"
            )

        elif sort_by == "Lowest Rated":

            filtered = filtered.sort_values(
                "My Rating",
                ascending=True,
                na_position="last"
            )

        elif sort_by == "Newest First":

            if "Date Read" in filtered.columns:

                filtered = filtered.sort_values(
                    "Date Read",
                    ascending=False,
                    na_position="last"
                )

        elif sort_by == "Oldest First":

            if "Date Read" in filtered.columns:

                filtered = filtered.sort_values(
                    "Date Read",
                    ascending=True,
                    na_position="last"
                )

        # ----------------------------------------------------
        # TREE HEADER
        # ----------------------------------------------------

        st.html(
            f"""
            <div class="tree-area">

                <div class="root-node">

                    <div class="root-title">
                        My Library
                    </div>

                    <div class="root-small">
                        {len(filtered)} books ·
                        {filtered["Author"].nunique()}
                        authors
                    </div>

                </div>

            </div>
            """
        )

        # ----------------------------------------------------
        # AUTHORS
        # ----------------------------------------------------

        author_list = sorted(
            filtered["Author"]
            .fillna("Unknown Author")
            .astype(str)
            .unique(),
            key=lambda x:
                x.lower()
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

            if expand_mode == "Authors Open":

                opened = True

            if expand_mode == "Everything Open":

                opened = True

            arrow = (
                "▼"
                if opened
                else "▶"
            )

            if st.button(
                f"{arrow}  {author}",
                key=f"author_{author_id}",
                use_container_width=True,
            ):

                if author_id in (
                    st.session_state
                    .open_authors
                ):

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
                <div class="author-node">

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

            # ------------------------------------------------
            # SERIES
            # ------------------------------------------------

            series_list = sorted(
                author_books[
                    "Series"
                ]
                .fillna("Standalone")
                .astype(str)
                .unique(),
                key=lambda x:
                    x.lower()
            )

            for series in series_list:

                series_books = author_books[
                    author_books["Series"]
                    .fillna("Standalone")
                    .astype(str)
                    == series
                ].copy()

                # --------------------------------------------
                # STANDALONES
                # --------------------------------------------

                if series == "Standalone":

                    st.html(
                        f"""
                        <div class="series-node">

                            <div class="series-name">
                                Standalone Books
                            </div>

                            <div class="series-count">
                                {len(series_books)}
                                {"book" if len(series_books) == 1 else "books"}
                            </div>

                        </div>
                        """
                    )

                    for _, book in (
                        series_books.iterrows()
                    ):

                        cover = str(
                            book.get(
                                "Cover",
                                ""
                            )
                            or ""
                        )

                        title = html.escape(
                            str(
                                book.get(
                                    "Title",
                                    ""
                                )
                            )
                        )

                        rating = book.get(
                            "My Rating"
                        )

                        if pd.notna(rating):

                            try:

                                rating_text = (
                                    "★ "
                                    + str(
                                        float(rating)
                                    ).rstrip("0").rstrip(".")
                                )

                            except Exception:

                                rating_text = ""

                        else:

                            rating_text = ""

                        genre = html.escape(
                            str(
                                book.get(
                                    "Genre",
                                    ""
                                )
                            )
                        )

                        if cover:

                            st.html(
                                f"""
                                <div class="book-node">

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
                                                {genre}
                                                &nbsp; · &nbsp;
                                                {html.escape(
                                                    str(
                                                        book.get(
                                                            "Status",
                                                            ""
                                                        )
                                                    )
                                                )}
                                                &nbsp; · &nbsp;
                                                {rating_text}
                                            </div>

                                        </div>

                                    </div>

                                </div>
                                """
                            )

                        else:

                            st.html(
                                f"""
                                <div class="book-node">

                                    <div class="book-title">
                                        {title}
                                    </div>

                                    <div class="book-meta">
                                        {genre}
                                        &nbsp; · &nbsp;
                                        {html.escape(
                                            str(
                                                book.get(
                                                    "Status",
                                                    ""
                                                )
                                            )
                                        )}
                                        &nbsp; · &nbsp;
                                        {rating_text}
                                    </div>

                                </div>
                                """
                            )

                    continue

                # --------------------------------------------
                # SERIES
                # --------------------------------------------

                series_id = (
                    author_id
                    + "::"
                    + safe_id(series)
                )

                series_open = (
                    series_id
                    in st.session_state.open_series
                )

                if expand_mode == "Everything Open":

                    series_open = True

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

                    if series_id in (
                        st.session_state
                        .open_series
                    ):

                        st.session_state.open_series.discard(
                            series_id
                        )

                    else:

                        st.session_state.open_series.add(
                            series_id
                        )

                    st.rerun()

                st.html(
                    f"""
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

                if not series_open:
                    continue

                # Sort books in a series
                series_books = series_books.sort_values(
                    by=[
                        "Series Number",
                        "Title"
                    ],
                    na_position="last"
                )

                for position, (
                    _,
                    book
                ) in enumerate(
                    series_books.iterrows(),
                    1
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

                    cover = str(
                        book.get(
                            "Cover",
                            ""
                        )
                        or ""
                    )

                    title = html.escape(
                        str(
                            book.get(
                                "Title",
                                ""
                            )
                        )
                    )

                    genre = html.escape(
                        str(
                            book.get(
                                "Genre",
                                ""
                            )
                        )
                    )

                    rating = book.get(
                        "My Rating"
                    )

                    if pd.notna(rating):

                        try:

                            rating_text = (
                                "★ "
                                + str(
                                    float(rating)
                                ).rstrip("0").rstrip(".")
                            )

                        except Exception:

                            rating_text = ""

                    else:

                        rating_text = ""

                    if cover:

                        st.html(
                            f"""
                            <div class="book-node">

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
                                            {genre}
                                            &nbsp; · &nbsp;
                                            {html.escape(
                                                str(
                                                    book.get(
                                                        "Status",
                                                        ""
                                                    )
                                                )
                                            )}
                                            &nbsp; · &nbsp;
                                            {rating_text}
                                        </div>

                                    </div>

                                </div>

                            </div>
                            """
                        )

                    else:

                        st.html(
                            f"""
                            <div class="book-node">

                                <div class="book-title">
                                    {number_text}
                                    ·
                                    {title}
                                </div>

                                <div class="book-meta">
                                    {genre}
                                    &nbsp; · &nbsp;
                                    {html.escape(
                                        str(
                                            book.get(
                                                "Status",
                                                ""
                                            )
                                        )
                                    )}
                                    &nbsp; · &nbsp;
                                    {rating_text}
                                </div>

                            </div>
                            """
                        )

# ============================================================
# ALL BOOKS TAB
# ============================================================

with books_tab:

    if library.empty:

        st.info(
            "No books yet."
        )

    else:

        st.header(
            "Your Books"
        )

        book_filter = st.radio(
            "Show",
            [
                "All",
                "Read",
                "Currently Reading",
                "Want to Read",
                "Favorites",
            ],
            horizontal=True,
        )

        books = library.copy()

        if book_filter == "Favorites":

            books = books[
                books["Favorite"] == True
            ]

        elif book_filter != "All":

            books = books[
                books["Status"]
                == book_filter
            ]

        books = books.sort_values(
            "Title",
            key=lambda s:
                s.astype(str).str.lower()
        )

        for index, book in books.iterrows():

            col1, col2, col3 = st.columns(
                [1, 6, 1]
            )

            with col1:

                if book.get(
                    "Cover"
                ):

                    st.image(
                        book["Cover"],
                        width=75
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
                        <br>
                        {html.escape(
                            str(
                                book["Genre"]
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
                    label_visibility="visible",
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
            placeholder=(
                "Leave blank if this is a standalone"
            )
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

        genre = st.text_input(
            "Genre",
            placeholder=(
                "Romance, Fantasy, Mystery..."
            )
        )

        status = st.selectbox(
            "Reading status",
            [
                "Want to Read",
                "Currently Reading",
                "Read",
            ]
        )

        rating = st.slider(
            "My Rating",
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

                if not genre.strip():

                    actual_genre = get_genre(
                        title,
                        author
                    )

                else:

                    actual_genre = (
                        genre.strip()
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
                    "Genre": actual_genre,
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
                    f'"{title}" has been added to your tree.'
                )

                st.rerun()

# ============================================================
# IMPORT TAB
# ============================================================

with import_tab:

    st.header(
        "Import Your Library"
    )

    st.write(
        "Upload a Goodreads CSV or another book-list CSV."
    )

    st.caption(
        "The app will import your reading status, "
        "find covers, and attempt to find genres."
    )

    uploaded = st.file_uploader(
        "Choose your CSV",
        type=["csv"]
    )

    if uploaded:

        st.success(
            f"Ready to import: {uploaded.name}"
        )

        if st.button(
            "🌿 Build My Book Tree"
        ):

            with st.spinner(
                "Growing your library... finding covers and genres..."
            ):

                success = import_books(
                    uploaded
                )

            if success:

                st.success(
                    "Your book tree has been grown!"
                )

                st.session_state.loading_done = True

                st.rerun()
