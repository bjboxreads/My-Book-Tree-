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

    "Enchanted Emerald": {
        "page": "#10231D",
        "surface": "#17352C",
        "surface2": "#21483A",
        "card": "#2C5A49",
        "text": "#FFF5D9",
        "muted": "#D8CCB1",
        "accent": "#D9AD52",
        "accent2": "#91B68C",
        "line": "#B98A3C",
    },

    "Midnight Sapphire": {
        "page": "#101A2C",
        "surface": "#17263E",
        "surface2": "#213757",
        "card": "#2E496D",
        "text": "#FFF5DC",
        "muted": "#D0D3D5",
        "accent": "#DDB45B",
        "accent2": "#9AB9C9",
        "line": "#B68A3D",
    },

    "Velvet Rose": {
        "page": "#24121D",
        "surface": "#351A2A",
        "surface2": "#4A2439",
        "card": "#63314B",
        "text": "#FFF1E9",
        "muted": "#DEC5CB",
        "accent": "#D99A9F",
        "accent2": "#BCA1C8",
        "line": "#A96578",
    },

    "Old Rose Library": {
        "page": "#28191A",
        "surface": "#3B2525",
        "surface2": "#513333",
        "card": "#684343",
        "text": "#FFF1D8",
        "muted": "#DAC7B1",
        "accent": "#D8A45D",
        "accent2": "#B88B88",
        "line": "#A66C51",
    },

    "Moonlit Garden": {
        "page": "#16152A",
        "surface": "#211F3C",
        "surface2": "#302C50",
        "card": "#433D68",
        "text": "#FFF5DF",
        "muted": "#D4CDE0",
        "accent": "#DCC16A",
        "accent2": "#A99CCB",
        "line": "#8370A9",
    },

    "Antique Bookshop": {
        "page": "#292116",
        "surface": "#3C3021",
        "surface2": "#51412C",
        "card": "#695338",
        "text": "#FFF0D0",
        "muted": "#D8C6A8",
        "accent": "#D6A64F",
        "accent2": "#9EAA72",
        "line": "#A87835",
    },

    "Poison Garden": {
        "page": "#171D18",
        "surface": "#243126",
        "surface2": "#334535",
        "card": "#465C43",
        "text": "#FFF2D9",
        "muted": "#D1CDB8",
        "accent": "#D6A653",
        "accent2": "#A9B98A",
        "line": "#9C7737",
    },

    "Crimson Romance": {
        "page": "#241012",
        "surface": "#38181C",
        "surface2": "#512229",
        "card": "#69313A",
        "text": "#FFF0DE",
        "muted": "#DBC4B5",
        "accent": "#D7A455",
        "accent2": "#C68A91",
        "line": "#A65360",
    },
}

# ============================================================
# SESSION STATE
# ============================================================

if (
    "theme" not in st.session_state
    or st.session_state.theme not in THEMES
):
    st.session_state.theme = "Enchanted Emerald"

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

@import url('https://fonts.googleapis.com/css2?family=Berkshire+Swash&family=Cormorant+Garamond:wght@400;500;600;700&family=Libre+Baskerville:wght@400;700&display=swap');

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

.stApp {{
    background:
        radial-gradient(
            ellipse at 50% -15%,
            var(--surface2) 0%,
            var(--page) 65%
        );
    color: var(--text);
}}

.block-container {{
    max-width: 1450px;
    padding-top: 1rem;
    padding-bottom: 4rem;
}}

/* ============================================================
   TYPOGRAPHY
   ============================================================ */

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

/* ============================================================
   HEADER
   ============================================================ */

.book-header {{
    position: relative;
    text-align: center;
    padding: 22px 0 18px;
}}

.book-header::before,
.book-header::after {{
    content: "❦";
    position: absolute;
    top: 42px;
    color: var(--accent);
    font-family: Georgia, serif;
    font-size: 28px;
    opacity: .8;
}}

.book-header::before {{
    left: 30%;
}}

.book-header::after {{
    right: 30%;
    transform: scaleX(-1);
}}

.book-header-title {{
    font-family:
        "Berkshire Swash",
        Georgia,
        serif !important;

    font-size: 72px;
    line-height: 1;
    font-weight: 400;
    letter-spacing: .01em;
    color: var(--text) !important;

    text-shadow:
        0 3px 12px rgba(0,0,0,.35);
}}

/* ============================================================
   THEME SELECTOR
   ============================================================ */

.theme-heading {{
    font-family:
        "Berkshire Swash",
        Georgia,
        serif;

    color: var(--accent);
    font-size: 25px;
    margin: 12px 0 7px;
}}

/* Closed selector */

div[data-baseweb="select"] > div {{
    background:
        rgba(255,255,255,.035) !important;

    border: 1px solid var(--line) !important;

    border-radius: 8px !important;

    min-height: 46px !important;

    box-shadow:
        inset 0 0 0 1px rgba(255,255,255,.025),
        0 5px 18px rgba(0,0,0,.18) !important;
}}

div[data-baseweb="select"] span {{
    color: var(--text) !important;
    font-family:
        "Cormorant Garamond",
        Georgia,
        serif !important;

    font-size: 16px !important;
    font-weight: 600 !important;
}}

div[data-baseweb="select"] input {{
    color: var(--text) !important;
}}

/* Open selector */

div[role="listbox"] {{
    background: var(--surface) !important;
    border: 1px solid var(--accent) !important;
    border-radius: 8px !important;

    box-shadow:
        0 18px 45px rgba(0,0,0,.55) !important;
}}

div[role="option"] {{
    background: var(--surface) !important;
    color: var(--text) !important;

    padding: 11px 14px !important;

    font-family:
        "Cormorant Garamond",
        Georgia,
        serif !important;

    font-size: 16px !important;
}}

div[role="option"] span {{
    color: var(--text) !important;
}}

div[role="option"]:hover {{
    background: var(--surface2) !important;
}}

div[role="option"][aria-selected="true"] {{
    background: var(--card) !important;
    color: var(--accent) !important;
}}

/* ============================================================
   STATS
   ============================================================ */

.stat-card {{
    position: relative;

    background:
        linear-gradient(
            145deg,
            rgba(255,255,255,.035),
            rgba(0,0,0,.10)
        );

    border-top: 1px solid var(--line);
    border-bottom: 1px solid rgba(255,255,255,.08);

    padding: 15px 8px 13px;

    text-align: center;

    box-shadow:
        0 8px 22px rgba(0,0,0,.12);
}}

.stat-card::after {{
    content: "✦";
    display: block;

    color: var(--accent);
    font-size: 9px;

    margin-top: 5px;
    opacity: .75;
}}

.stat-number {{
    font-family:
        "Berkshire Swash",
        Georgia,
        serif;

    font-size: 38px;
    line-height: 1;

    color: var(--accent);
}}

.stat-label {{
    color: var(--muted);

    font-family:
        "Cormorant Garamond",
        Georgia,
        serif;

    font-size: 13px;
    font-weight: 700;

    text-transform: uppercase;
    letter-spacing: .16em;
}}

/* ============================================================
   TREE AREA
   ============================================================ */

.tree-area {{
    position: relative;

    margin-top: 28px;
    padding: 36px 25px 30px;

    background:
        radial-gradient(
            ellipse at center top,
            rgba(255,255,255,.035),
            transparent 65%
        );

    border-top: 1px solid var(--line);
    border-bottom: 1px solid var(--line);

    min-height: 120px;
}}

.tree-area::before {{
    content: "❧";
    position: absolute;

    top: 7px;
    left: 50%;

    transform: translateX(-50%);

    color: var(--accent);
    font-size: 22px;
}}

/* ============================================================
   ROOT
   ============================================================ */

.root-node {{
    position: relative;

    width: 310px;
    margin: 0 auto 42px;

    padding: 17px 25px 14px;

    background:
        linear-gradient(
            145deg,
            var(--accent),
            color-mix(in srgb, var(--accent), #000 15%)
        );

    color: var(--page);

    text-align: center;

    border-top: 2px solid rgba(255,255,255,.35);
    border-bottom: 2px solid rgba(0,0,0,.15);

    box-shadow:
        0 10px 30px rgba(0,0,0,.28);
}}

.root-node::before,
.root-node::after {{
    content: "❦";

    position: absolute;
    top: 50%;

    transform: translateY(-50%);

    color: var(--page);
    opacity: .7;
    font-size: 18px;
}}

.root-node::before {{
    left: 13px;
}}

.root-node::after {{
    right: 13px;
    transform:
        translateY(-50%)
        scaleX(-1);
}}

.root-node-title {{
    color: var(--page);

    font-family:
        "Berkshire Swash",
        Georgia,
        serif;

    font-size: 32px;
    font-weight: 400;
}}

.root-node-small {{
    color: var(--page);
    font-family:
        "Cormorant Garamond",
        Georgia,
        serif;

    font-size: 13px;
    font-weight: 700;
    opacity: .82;
}}

/* ============================================================
   AUTHOR
   ============================================================ */

.author-info {{
    position: relative;

    margin: 13px 0 7px;
    padding: 10px 18px 9px 23px;

    background:
        linear-gradient(
            90deg,
            rgba(255,255,255,.035),
            transparent
        );

    border-left: 2px solid var(--accent);

    box-shadow:
        0 5px 18px rgba(0,0,0,.08);
}}

.author-info::before {{
    content: "❧";

    position: absolute;
    left: -10px;
    top: 50%;

    transform: translateY(-50%);

    color: var(--accent);
    background: var(--page);

    padding: 0 2px;

    font-size: 17px;
}}

.author-name {{
    font-family:
        "Berkshire Swash",
        Georgia,
        serif;

    font-size: 28px;
    font-weight: 400;

    color: var(--text);
}}

.author-count {{
    color: var(--muted);

    font-family:
        "Cormorant Garamond",
        Georgia,
        serif;

    font-size: 14px;
}}

/* ============================================================
   SERIES
   ============================================================ */

.series-info {{
    position: relative;

    margin: 7px 0 5px 42px;
    padding: 8px 15px;

    background:
        rgba(255,255,255,.025);

    border-left: 1px solid var(--accent2);

    box-shadow:
        0 3px 12px rgba(0,0,0,.06);
}}

.series-info::before {{
    content: "✦";

    position: absolute;
    left: -7px;
    top: 50%;

    transform: translateY(-50%);

    color: var(--accent2);
    background: var(--page);

    padding: 0 2px;
    font-size: 11px;
}}

.series-name {{
    font-family:
        "Berkshire Swash",
        Georgia,
        serif;

    font-size: 23px;
    font-weight: 400;
}}

.series-count {{
    color: var(--muted);

    font-family:
        "Cormorant Garamond",
        Georgia,
        serif;

    font-size: 13px;
}}

/* ============================================================
   BOOKS
   ============================================================ */

.book-info {{
    position: relative;

    margin-left: 88px;
    margin-top: 7px;

    padding: 9px 13px;

    background:
        linear-gradient(
            90deg,
            rgba(255,255,255,.035),
            transparent
        );

    border-left: 1px solid var(--line);

    box-shadow:
        0 3px 12px rgba(0,0,0,.06);
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

    font-size: 13px;
    margin-top: 2px;
}}

.book-cover {{
    width: 55px;
    height: 80px;

    object-fit: cover;

    border-radius: 2px;

    border: 1px solid var(--accent);

    box-shadow:
        3px 5px 10px rgba(0,0,0,.28);
}}

/* ============================================================
   BUTTONS
   ============================================================ */

.stButton > button {{
    background: transparent !important;

    color: var(--text) !important;

    border: none !important;
    border-bottom: 1px solid rgba(255,255,255,.07) !important;

    border-radius: 0 !important;

    font-family:
        "Cormorant Garamond",
        Georgia,
        serif !important;

    font-size: 17px !important;
    font-weight: 600 !important;

    text-align: left !important;

    padding: 7px 10px !important;

    box-shadow: none !important;
}}

.stButton > button:hover {{
    background:
        rgba(255,255,255,.035) !important;

    color: var(--accent) !important;

    border-bottom-color: var(--accent) !important;
}}

/* ============================================================
   TABS
   ============================================================ */

button[data-baseweb="tab"] {{
    font-family:
        "Berkshire Swash",
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

/* ============================================================
   INPUTS
   ============================================================ */

div[data-baseweb="input"] > div,
div[data-baseweb="textarea"] > div {{
    background:
        rgba(255,255,255,.035) !important;

    border: 1px solid var(--line) !important;
    border-radius: 5px !important;
}}

div[data-baseweb="input"] input,
textarea {{
    color: var(--text) !important;

    font-family:
        "Cormorant Garamond",
        Georgia,
        serif !important;

    font-size: 16px !important;
}}

textarea {{
    background: var(--surface) !important;
}}

/* ============================================================
   RADIO / CHECKBOX
   ============================================================ */

.stRadio label,
.stCheckbox label {{
    font-family:
        "Cormorant Garamond",
        Georgia,
        serif !important;

    color: var(--text) !important;
    font-size: 16px !important;
}}

/* ============================================================
   FILE UPLOADER
   ============================================================ */

section[data-testid="stFileUploaderDropzone"] {{
    background:
        rgba(255,255,255,.025) !important;

    border: 1px dashed var(--line) !important;
    border-radius: 5px !important;
}}

/* ============================================================
   GENERAL HEADERS
   ============================================================ */

.stMarkdown h1,
.stMarkdown h2,
.stMarkdown h3,
.stMarkdown h4 {{
    font-family:
        "Berkshire Swash",
        Georgia,
        serif !important;
}}

/* ============================================================
   SUCCESS / INFO
   ============================================================ */

div[data-testid="stAlert"] {{
    border-radius: 5px !important;

    border-left: 2px solid var(--accent) !important;

    background:
        rgba(255,255,255,.035) !important;
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
