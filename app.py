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
# DISTINCT BOOKISH THEMES
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
    'https://fonts.googleapis.com/css2?family=Cormorant+Garamond:wght@500;600;700&family=Libre+Baskerville:wght@400;700'
);

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
    --button: {theme["button"]};
}}

.stApp {{
    background:
        radial-gradient(
            circle at 15% 0%,
            var(--surface2) 0%,
            var(--page) 55%
        );
    color: var(--text);
}}

.block-container {{
    max-width: 1400px;
    padding-top: 1rem;
    padding-bottom: 4rem;
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

/* ==========================================================
   HEADER
   ========================================================== */

.book-header {{
    text-align: center;
    padding: 25px 0 30px;
}}

.book-header-title {{
    font-family:
        "Cormorant Garamond",
        Georgia,
        serif;
    font-size: 68px;
    line-height: .95;
    font-weight: 700;
    color: var(--text);
    text-shadow:
        0 3px 20px rgba(0, 0, 0, .35);
}}

.book-header-subtitle {{
    font-family:
        "Libre Baskerville",
        Georgia,
        serif;
    color: var(--muted);
    margin-top: 14px;
    font-size: 14px;
    letter-spacing: .04em;
}}

/* ==========================================================
   THEME SELECTOR
   ========================================================== */

.theme-heading {{
    font-family:
        "Cormorant Garamond",
        Georgia,
        serif;
    font-size: 23px;
    font-weight: 700;
    color: var(--text);
    margin-bottom: 6px;
}}

div[data-baseweb="select"] > div {{
    background: var(--surface) !important;
    border: 2px solid var(--accent) !important;
    border-radius: 10px !important;
    min-height: 48px !important;
    box-shadow:
        0 5px 20px rgba(0,0,0,.18) !important;
}}

div[data-baseweb="select"] span {{
    color: var(--text) !important;
    font-weight: 600 !important;
}}

div[data-baseweb="select"] input {{
    color: var(--text) !important;
}}

div[role="listbox"] {{
    background: #171717 !important;
    border: 2px solid var(--accent) !important;
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

/* ==========================================================
   STATS
   ========================================================== */

.stat-card {{
    background:
        linear-gradient(
            145deg,
            var(--surface),
            var(--button)
        );
    border: 1px solid var(--accent);
    border-radius: 12px;
    padding: 14px 8px;
    text-align: center;
    box-shadow:
        0 5px 18px rgba(0,0,0,.15);
}}

.stat-number {{
    font-family:
        "Cormorant Garamond",
        Georgia,
        serif;
    font-size: 34px;
    font-weight: 700;
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

/* ==========================================================
   TREE AREA
   ========================================================== */

.tree-area {{
    margin-top: 25px;
    margin-bottom: 22px;
    padding: 30px;
    background:
        linear-gradient(
            145deg,
            rgba(0,0,0,.18),
            rgba(0,0,0,.08)
        );
    border: 1px solid var(--line);
    border-radius: 18px;
}}

/* ==========================================================
   ROOT
   ========================================================== */

.root-node {{
    width: 300px;
    margin: 0 auto 30px;
    padding: 18px 25px;
    background:
        linear-gradient(
            135deg,
            var(--accent),
            var(--line)
        );
    color: {theme["page"]};
    border-radius: 50px;
    text-align: center;
    box-shadow:
        0 8px 25px rgba(0,0,0,.3);
}}

.root-node-title {{
    color: {theme["page"]};
    font-family:
        "Cormorant Garamond",
        Georgia,
        serif;
    font-size: 32px;
    font-weight: 700;
}}

.root-node-small {{
    color: {theme["page"]};
    font-size: 11px;
    font-weight: 700;
    opacity: .8;
}}

/* ==========================================================
   TREE BUTTONS
   ========================================================== */

.tree-button {{
    position: relative;
}}

.stButton > button {{
    background:
        linear-gradient(
            90deg,
            var(--surface),
            var(--button)
        ) !important;
    color: var(--text) !important;
    border: 1px solid var(--line) !important;
    border-radius: 9px !important;
    font-family:
        "Libre Baskerville",
        Georgia,
        serif !important;
    font-weight: 600 !important;
    text-align: left !important;
    transition:
        all .15s ease !important;
}}

.stButton > button:hover {{
    background: var(--surface2) !important;
    border-color: var(--accent) !important;
    color: var(--text) !important;
    transform: translateX(2px);
}}

/* ==========================================================
   AUTHOR
   ========================================================== */

.author-info {{
    padding: 10px 15px;
    margin: 8px 0;
    border-left: 4px solid var(--accent);
    background:
        linear-gradient(
            90deg,
            var(--surface),
            rgba(0,0,0,.08)
        );
    border-radius: 0 12px 12px 0;
}}

.author-name {{
    font-family:
        "Cormorant Garamond",
        Georgia,
        serif;
    font-size: 27px;
    font-weight: 700;
    color: var(--text);
}}

.author-count {{
    color: var(--muted);
    font-size: 11px;
}}

/* ==========================================================
   SERIES
   ========================================================== */

.series-info {{
    margin-left: 48px;
    padding: 10px 15px;
    border-left: 3px solid var(--accent2);
    background:
        linear-gradient(
            90deg,
            var(--surface2),
            rgba(0,0,0,.08)
        );
    border-radius: 0 10px 10px 0;
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
    color: var(--muted);
    font-size: 11px;
}}

/* ==========================================================
   BOOK
   ========================================================== */

.book-info {{
    margin-left: 100px;
    margin-top: 8px;
    padding: 10px 14px;
    background: var(--card);
    border-left: 2px solid var(--line);
    border-radius: 0 10px 10px 0;
    box-shadow:
        0 3px 10px rgba(0,0,0,.12);
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
    font-size: 11px;
    margin-top: 3px;
}}

.book-cover {{
    width: 55px;
    height: 80px;
    object-fit: cover;
    border-radius: 4px;
    border: 1px solid var(--accent);
    box-shadow:
        0 4px 10px rgba(0,0,0,.3);
}}

/* ==========================================================
   INPUTS
   ========================================================== */

div[data-baseweb="input"] > div {{
    background: var(--surface) !important;
    border-color: var(--line) !important;
}}

div[data-baseweb="input"] input {{
    color: var(--text) !important;
}}

textarea {{
    background: var(--surface) !important;
    color: var(--text) !important;
}}

input {{
    color: var(--text) !important;
}}

div[data-baseweb="textarea"] > div {{
    background: var(--surface) !important;
    border-color: var(--line) !important;
}}

/* ==========================================================
   TABS
   ========================================================== */

button[data-baseweb="tab"] {{
    color: var(--muted) !important;
    font-family:
        "Libre Baskerville",
        Georgia,
        serif !important;
}}

button[data-baseweb="tab"][aria-selected="true"] {{
    color: var(--accent) !important;
}}

div[data-baseweb="tab-highlight"] {{
    background: var(--accent) !important;
}}

/* ==========================================================
   RADIO / CHECKBOX
   ========================================================== */

div[data-testid="stRadio"] label p,
div[data-testid="stCheckbox"] label p {{
    color: var(--text) !important;
}}

/* ==========================================================
   FILE UPLOADER
   ========================================================== */

section[data-testid="stFileUploaderDropzone"] {{
    background: var(--surface) !important;
    border: 1px dashed var(--line) !important;
}}

section[data-testid="stFileUploaderDropzone"] * {{
    color: var(--text) !important;
}}

/* ==========================================================
   FORM BUTTON
   ========================================================== */

button[kind="formSubmit"] {{
    background:
        linear-gradient(
            135deg,
            var(--accent),
            var(--line)
        ) !important;
    color: var(--page) !important;
    border: none !important;
    font-weight: 700 !important;
}}

/* ==========================================================
   MOBILE
   ========================================================== */

@media (max-width: 700px) {{

    .book-header-title {{
        font-size: 48px;
    }}

    .book-header-subtitle {{
        font-size: 12px;
    }}

    .root-node {{
        width: 240px;
    }}

    .tree-area {{
        padding: 15px;
    }}

    .series-info {{
        margin-left: 25px;
    }}

    .book-info {{
        margin-left: 45px;
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

        <div class="book-header-subtitle">
            Your books, connected from author to series to story.
        </div>

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

    # ---------- ISBN ----------
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

    # ---------- Open Library ----------
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

    # ---------- Google Books ----------
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

        # ---------- ROOT ----------

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

        # ---------- AUTHORS ----------

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

            # ---------- SERIES ----------

            series_list = sorted(
                author_books["Series"]
                .fillna("Standalone")
                .astype(str)
                .unique(),
                key=lambda x: x.lower()
            )

            for series in series_list:

                # ---------- STANDALONES ----------

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

                # ---------- SERIES ----------

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

                # ---------- SORT BOOKS ----------

                series_books = series_books.sort_values(
                    by=[
                        "Series Number",
                        "Title"
                    ],
                    na_position="last"
                )

                # ---------- BOOKS ----------

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
