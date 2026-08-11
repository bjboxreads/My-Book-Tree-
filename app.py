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
    "Grand Library": {
        "page": "#101B26",
        "surface": "#182938",
        "surface2": "#213748",
        "card": "#1C3040",
        "text": "#F8F1DC",
        "muted": "#C8D0C9",
        "accent": "#D5A83B",
        "accent2": "#5D9B83",
        "line": "#D5A83B",
        "button_text": "#101B26",
        "cover_border": "#D5A83B",
    },

    "Dark Academia": {
        "page": "#111923",
        "surface": "#1B2938",
        "surface2": "#293948",
        "card": "#202F3E",
        "text": "#F6EEDC",
        "muted": "#C7CDCE",
        "accent": "#C9A45C",
        "accent2": "#6C98AF",
        "line": "#C9A45C",
        "button_text": "#111923",
        "cover_border": "#C9A45C",
    },

    "Enchanted Garden": {
        "page": "#0E2927",
        "surface": "#153B35",
        "surface2": "#205047",
        "card": "#194239",
        "text": "#FFF7E7",
        "muted": "#C8D9D0",
        "accent": "#E3B747",
        "accent2": "#A85E8B",
        "line": "#72B78F",
        "button_text": "#0E2927",
        "cover_border": "#E3B747",
    },

    "Gothic Romance": {
        "page": "#15121D",
        "surface": "#211A2B",
        "surface2": "#30213B",
        "card": "#271E33",
        "text": "#FFF3F7",
        "muted": "#D5C4CF",
        "accent": "#D04D6C",
        "accent2": "#9670BF",
        "line": "#D04D6C",
        "button_text": "#FFFFFF",
        "cover_border": "#D04D6C",
    },

    "Victorian Parlor": {
        "page": "#102B35",
        "surface": "#173D4A",
        "surface2": "#245666",
        "card": "#1E4856",
        "text": "#FFF5E4",
        "muted": "#CAD9DA",
        "accent": "#D9A33B",
        "accent2": "#D45E79",
        "line": "#D9A33B",
        "button_text": "#102B35",
        "cover_border": "#D9A33B",
    },

    "Midnight Bookshop": {
        "page": "#0D1730",
        "surface": "#152449",
        "surface2": "#20355E",
        "card": "#192D54",
        "text": "#F7F3FF",
        "muted": "#C8CEE3",
        "accent": "#E4BA4D",
        "accent2": "#65BBC7",
        "line": "#65BBC7",
        "button_text": "#0D1730",
        "cover_border": "#E4BA4D",
    },

    "Literary Arts & Crafts": {
        "page": "#173A3B",
        "surface": "#225050",
        "surface2": "#2E6562",
        "card": "#285B59",
        "text": "#FFF8E9",
        "muted": "#D3D9CA",
        "accent": "#E2A832",
        "accent2": "#D85E48",
        "line": "#E2A832",
        "button_text": "#173A3B",
        "cover_border": "#D85E48",
    },

    "Fantasy Bookshelf": {
        "page": "#171532",
        "surface": "#252054",
        "surface2": "#322A6A",
        "card": "#2A245D",
        "text": "#FFF8E9",
        "muted": "#D1CCE8",
        "accent": "#E6B940",
        "accent2": "#6FA9D9",
        "line": "#9C75D6",
        "button_text": "#171532",
        "cover_border": "#E6B940",
    },

    "Modern Book Nook": {
        "page": "#102D36",
        "surface": "#17404B",
        "surface2": "#255A67",
        "card": "#1F4D5A",
        "text": "#FFF8EA",
        "muted": "#CBD9D9",
        "accent": "#F0B643",
        "accent2": "#E66D57",
        "line": "#F0B643",
        "button_text": "#102D36",
        "cover_border": "#F0B643",
    },
}

# ============================================================
# SESSION STATE
# ============================================================

# IMPORTANT:
# This also fixes the old-theme KeyError.
if (
    "theme" not in st.session_state
    or st.session_state.theme not in THEMES
):
    st.session_state.theme = "Grand Library"

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

# ============================================================
# THEME
# ============================================================

theme = THEMES[st.session_state.theme]

# ============================================================
# CSS
# ============================================================

st.markdown(
    f"""
<style>

@import url(
'https://fonts.googleapis.com/css2?family=Cormorant+Garamond:wght@500;600;700'
'&family=DM+Sans:wght@400;500;600;700'
);

html, body, [class*="css"] {{
    font-family: "DM Sans", sans-serif;
}}

.stApp {{
    background:
        radial-gradient(
            circle at top left,
            {theme["surface2"]} 0%,
            {theme["page"]} 48%
        );
    color: {theme["text"]};
}}

.block-container {{
    max-width: 1450px;
    padding-top: 1.5rem;
    padding-bottom: 4rem;
}}

h1, h2, h3, h4 {{
    font-family:
        "Cormorant Garamond",
        Georgia,
        serif !important;
    color: {theme["text"]} !important;
}}

.hero {{
    text-align: center;
    padding: 15px 0 25px;
}}

.hero-title {{
    font-family:
        "Cormorant Garamond",
        Georgia,
        serif;
    font-size: 64px;
    line-height: 1;
    font-weight: 700;
    color: {theme["text"]};
    letter-spacing: .02em;
}}

.hero-subtitle {{
    margin-top: 10px;
    font-size: 16px;
    color: {theme["muted"]};
}}

/* =========================================================
THEME SELECTOR
========================================================= */

.theme-label {{
    font-family:
        "Cormorant Garamond",
        Georgia,
        serif;
    font-size: 21px;
    font-weight: 700;
    color: {theme["text"]};
    margin-bottom: 5px;
}}

div[data-testid="stSelectbox"] label {{
    color: {theme["text"]} !important;
    font-weight: 600 !important;
}}

div[data-baseweb="select"] > div {{
    background: {theme["surface"]} !important;
    border: 2px solid {theme["accent"]} !important;
    border-radius: 12px !important;
}}

div[data-baseweb="select"] span {{
    color: {theme["text"]} !important;
}}

div[data-baseweb="select"] input {{
    color: {theme["text"]} !important;
}}

/*
THE OPEN DROPDOWN MENU HAS ITS OWN COLORS.
This prevents invisible theme names.
*/

div[role="listbox"] {{
    background: #17202B !important;
    border: 2px solid #D5A83B !important;
    border-radius: 12px !important;
    padding: 6px !important;
    box-shadow:
        0 14px 35px rgba(0,0,0,.5) !important;
}}

div[role="option"] {{
    background: #17202B !important;
    color: #FFFFFF !important;
    border-radius: 8px !important;
    padding: 10px 12px !important;
    font-family:
        "DM Sans",
        sans-serif !important;
    font-size: 15px !important;
    font-weight: 600 !important;
}}

div[role="option"] *,
div[role="option"] span {{
    color: #FFFFFF !important;
}}

div[role="option"]:hover {{
    background: #3A5267 !important;
    color: #FFFFFF !important;
}}

div[role="option"][aria-selected="true"] {{
    background: #A97822 !important;
    color: #FFFFFF !important;
}}

div[role="option"][aria-selected="true"] * {{
    color: #FFFFFF !important;
}}

/* =========================================================
STATS
========================================================= */

.stat {{
    background: {theme["surface"]};
    border: 1px solid {theme["accent"]}66;
    border-radius: 16px;
    padding: 14px;
    text-align: center;
    box-shadow:
        0 8px 25px rgba(0,0,0,.18);
}}

.stat-number {{
    font-family:
        "Cormorant Garamond",
        Georgia,
        serif;
    font-size: 34px;
    font-weight: 700;
    color: {theme["accent"]};
}}

.stat-label {{
    color: {theme["muted"]};
    font-size: 11px;
    text-transform: uppercase;
    letter-spacing: .12em;
}}

/* =========================================================
TREE
========================================================= */

.tree-container {{
    margin-top: 25px;
    padding: 35px;
    background:
        linear-gradient(
            135deg,
            {theme["surface"]},
            {theme["page"]}
        );
    border: 1px solid {theme["accent"]}55;
    border-radius: 24px;
    box-shadow:
        0 15px 45px rgba(0,0,0,.22);
}}

.root-node {{
    width: fit-content;
    min-width: 280px;
    margin: 0 auto 35px;
    padding: 18px 35px;
    text-align: center;
    background: {theme["accent"]};
    color: {theme["button_text"]};
    border-radius: 20px;
    box-shadow:
        0 10px 25px rgba(0,0,0,.25);
}}

.root-title {{
    font-family:
        "Cormorant Garamond",
        Georgia,
        serif;
    font-size: 34px;
    font-weight: 700;
}}

.root-subtitle {{
    font-size: 12px;
    font-weight: 600;
    opacity: .85;
}}

.author-node {{
    background: {theme["card"]};
    border: 2px solid {theme["accent2"]};
    border-radius: 17px;
    padding: 14px 20px;
    margin: 8px 0;
    box-shadow:
        0 8px 20px rgba(0,0,0,.16);
}}

.series-node {{
    background: {theme["surface2"]};
    border: 2px solid {theme["accent"]};
    border-radius: 14px;
    padding: 13px 18px;
    margin: 8px 0 8px 45px;
    box-shadow:
        0 6px 16px rgba(0,0,0,.14);
}}

.book-card {{
    background: {theme["card"]};
    border: 1px solid {theme["accent2"]}99;
    border-radius: 14px;
    padding: 12px;
    margin: 8px 0 8px 90px;
    min-height: 110px;
}}

.branch-label {{
    font-family:
        "Cormorant Garamond",
        Georgia,
        serif;
    font-size: 24px;
    font-weight: 700;
    color: {theme["text"]};
}}

.branch-meta {{
    color: {theme["muted"]};
    font-size: 12px;
    margin-top: 2px;
}}

.book-title {{
    font-family:
        "Cormorant Garamond",
        Georgia,
        serif;
    color: {theme["text"]};
    font-size: 21px;
    font-weight: 700;
}}

.book-meta {{
    color: {theme["muted"]};
    font-size: 12px;
}}

.cover-small {{
    width: 65px;
    height: 92px;
    object-fit: cover;
    border-radius: 5px;
    border: 2px solid {theme["cover_border"]};
}}

/* =========================================================
BUTTONS
========================================================= */

.stButton > button {{
    background: {theme["surface2"]} !important;
    color: {theme["text"]} !important;
    border: 1px solid {theme["accent"]}99 !important;
    border-radius: 10px !important;
    font-weight: 600 !important;
}}

.stButton > button:hover {{
    background: {theme["accent"]} !important;
    color: {theme["button_text"]} !important;
    border-color: {theme["accent"]} !important;
}}

/* =========================================================
INPUTS
========================================================= */

input, textarea {{
    color: {theme["text"]} !important;
}}

div[data-baseweb="input"] > div,
textarea {{
    background: {theme["surface"]} !important;
    color: {theme["text"]} !important;
    border-color: {theme["accent"]}66 !important;
}}

div[data-baseweb="input"] input {{
    color: {theme["text"]} !important;
}}

label {{
    color: {theme["text"]} !important;
}}

/* =========================================================
TABS
========================================================= */

button[data-baseweb="tab"] {{
    color: {theme["muted"]} !important;
    font-weight: 600 !important;
}}

button[data-baseweb="tab"][aria-selected="true"] {{
    color: {theme["accent"]} !important;
}}

</style>
""",
    unsafe_allow_html=True,
)

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

    # --------------------------------
    # ISBN
    # --------------------------------

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

    # --------------------------------
    # OPEN LIBRARY SEARCH
    # --------------------------------

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

    # --------------------------------
    # GOOGLE BOOKS
    # --------------------------------

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
            re.IGNORECASE
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


# ============================================================
# SAFE ID
# ============================================================

def make_id(text):

    return re.sub(
        r"[^a-zA-Z0-9_-]",
        "_",
        str(text)
    )


# ============================================================
# IMPORT CSV
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

        for name in names:

            for key, original in columns.items():

                if name.lower() in key:

                    return original

        return None

    title_col = find_column(
        ["Title", "Book Title"]
    )

    author_col = find_column(
        ["Author", "Authors"]
    )

    if not title_col:

        st.error(
            "I couldn't find a Title column in this CSV."
        )

        return False

    isbn_col = find_column(
        ["ISBN13", "ISBN"]
    )

    rating_col = find_column(
        ["My Rating", "Rating"]
    )

    shelf_col = find_column(
        [
            "Exclusive Shelf",
            "Shelf",
            "Status"
        ]
    )

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
            "No books were found in the CSV."
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
            new_library.loc[
                i,
                "Title"
            ],
            new_library.loc[
                i,
                "Author"
            ],
            new_library.loc[
                i,
                "ISBN"
            ]
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
# HEADER
# ============================================================

st.markdown(
    """
<div class="hero">

    <div class="hero-title">
        My Book Tree
    </div>

    <div class="hero-subtitle">
        Follow your library from author to series to book.
    </div>

</div>
""",
    unsafe_allow_html=True
)

# ============================================================
# THEME SELECTOR
# ============================================================

st.markdown(
    '<div class="theme-label">Choose your bookish theme</div>',
    unsafe_allow_html=True
)

theme_choice = st.selectbox(
    "Theme",
    list(THEMES.keys()),
    index=list(THEMES.keys()).index(
        st.session_state.theme
    ),
    label_visibility="collapsed",
    key="theme_selector",
)

if theme_choice != st.session_state.theme:

    st.session_state.theme = theme_choice

    st.rerun()

# ============================================================
# DATA
# ============================================================

library = st.session_state.library

total = len(library)

author_count = (
    library["Author"].nunique()
    if total
    else 0
)

series_count = (
    library[
        library["Series"]
        != "Standalone"
    ]["Series"].nunique()
    if total
    else 0
)

read_count = (
    len(
        library[
            library["Status"]
            == "Read"
        ]
    )
    if total
    else 0
)

favorite_count = (
    len(
        library[
            library["Favorite"]
            == True
        ]
    )
    if total
    else 0
)

# ============================================================
# STATS
# ============================================================

c1, c2, c3, c4, c5 = st.columns(5)

stats = [
    (total, "Books"),
    (author_count, "Authors"),
    (series_count, "Series"),
    (read_count, "Read"),
    (favorite_count, "Favorites"),
]

for column, (number, label) in zip(
    [c1, c2, c3, c4, c5],
    stats
):

    with column:

        st.markdown(
            f"""
            <div class="stat">

                <div class="stat-number">
                    {number}
                </div>

                <div class="stat-label">
                    {label}
                </div>

            </div>
            """,
            unsafe_allow_html=True
        )

# ============================================================
# TABS
# ============================================================

tree_tab, books_tab, add_tab, import_tab = st.tabs(
    [
        "🌳 Book Tree",
        "📚 Books",
        "➕ Add Book",
        "📥 Import Library",
    ]
)

# ============================================================
# TREE TAB
# ============================================================

with tree_tab:

    st.markdown(
        "## Your Library"
    )

    if library.empty:

        st.info(
            "Your tree is empty. "
            "Add a book or import your library to begin."
        )

    else:

        search = st.text_input(
            "Search",
            placeholder=(
                "Search by author, series, or book..."
            )
        )

        filtered = library.copy()

        if search:

            query = search.lower()

            filtered = filtered[
                filtered["Title"]
                .fillna("")
                .astype(str)
                .str.lower()
                .str.contains(
                    query,
                    na=False
                )
                |
                filtered["Author"]
                .fillna("")
                .astype(str)
                .str.lower()
                .str.contains(
                    query,
                    na=False
                )
                |
                filtered["Series"]
                .fillna("")
                .astype(str)
                .str.lower()
                .str.contains(
                    query,
                    na=False
                )
            ]

        st.markdown(
            '<div class="tree-container">',
            unsafe_allow_html=True
        )

        # ROOT

        st.markdown(
            f"""
            <div class="root-node">

                <div class="root-title">
                    My Book Tree
                </div>

                <div class="root-subtitle">
                    {len(filtered)} books
                </div>

            </div>
            """,
            unsafe_allow_html=True
        )

        # AUTHORS

        authors = sorted(
            filtered["Author"]
            .fillna("Unknown Author")
            .astype(str)
            .unique(),
            key=lambda x: x.lower()
        )

        for author in authors:

            author_id = make_id(
                author
            )

            author_books = filtered[
                filtered["Author"]
                .fillna("Unknown Author")
                .astype(str)
                == author
            ]

            is_open = (
                author_id
                in st.session_state.open_authors
            )

            arrow = (
                "▼"
                if is_open
                else "▶"
            )

            if st.button(
                f"{arrow}   {author}",
                key=f"author_{author_id}",
                use_container_width=True,
            ):

                if is_open:

                    st.session_state.open_authors.remove(
                        author_id
                    )

                    for series in (
                        author_books["Series"]
                        .fillna("Standalone")
                        .astype(str)
                        .unique()
                    ):

                        st.session_state.open_series.discard(
                            f"{author_id}::{make_id(series)}"
                        )

                else:

                    st.session_state.open_authors.add(
                        author_id
                    )

                st.rerun()

            st.markdown(
                f"""
                <div class="author-node">

                    <div class="branch-label">
                        {html.escape(author)}
                    </div>

                    <div class="branch-meta">
                        {len(author_books)} book
                        {"s" if len(author_books) != 1 else ""}
                    </div>

                </div>
                """,
                unsafe_allow_html=True
            )

            # -----------------------------------------------
            # AUTHOR EXPANDED
            # -----------------------------------------------

            if is_open:

                series_list = sorted(
                    author_books["Series"]
                    .fillna("Standalone")
                    .astype(str)
                    .unique(),
                    key=lambda x: x.lower()
                )

                for series in series_list:

                    series_id = (
                        f"{author_id}::"
                        f"{make_id(series)}"
                    )

                    series_books = author_books[
                        author_books["Series"]
                        .fillna("Standalone")
                        .astype(str)
                        == series
                    ].copy()

                    # ---------------------------------------
                    # STANDALONES
                    # ---------------------------------------

                    if series == "Standalone":

                        st.markdown(
                            f"""
                            <div class="series-node">

                                <div class="branch-label">
                                    📖 Standalone Books
                                </div>

                                <div class="branch-meta">
                                    {len(series_books)} book
                                    {"s" if len(series_books) != 1 else ""}
                                </div>

                            </div>
                            """,
                            unsafe_allow_html=True
                        )

                        for _, book in series_books.iterrows():

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

                            favorite = (
                                " ♥"
                                if book.get(
                                    "Favorite",
                                    False
                                )
                                else ""
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

                                st.markdown(
                                    f"""
                                    <div class="book-card">

                                        <div style="
                                            display:flex;
                                            gap:15px;
                                            align-items:center;
                                        ">

                                            <img
                                                class="cover-small"
                                                src="{html.escape(cover)}"
                                            >

                                            <div>

                                                <div class="book-title">
                                                    {title}{favorite}
                                                </div>

                                                <div class="book-meta">
                                                    {status}
                                                </div>

                                            </div>

                                        </div>

                                    </div>
                                    """,
                                    unsafe_allow_html=True
                                )

                            else:

                                st.markdown(
                                    f"""
                                    <div class="book-card">

                                        <div class="book-title">
                                            📖 {title}{favorite}
                                        </div>

                                        <div class="book-meta">
                                            {status}
                                        </div>

                                    </div>
                                    """,
                                    unsafe_allow_html=True
                                )

                    # ---------------------------------------
                    # SERIES
                    # ---------------------------------------

                    else:

                        is_series_open = (
                            series_id
                            in st.session_state.open_series
                        )

                        arrow = (
                            "▼"
                            if is_series_open
                            else "▶"
                        )

                        if st.button(
                            f"{arrow}   📚 {series}",
                            key=f"series_{series_id}",
                            use_container_width=True,
                        ):

                            if is_series_open:

                                st.session_state.open_series.remove(
                                    series_id
                                )

                            else:

                                st.session_state.open_series.add(
                                    series_id
                                )

                            st.rerun()

                        st.markdown(
                            f"""
                            <div class="series-node">

                                <div class="branch-label">
                                    📚 {html.escape(series)}
                                </div>

                                <div class="branch-meta">
                                    {len(series_books)} book
                                    {"s" if len(series_books) != 1 else ""}
                                </div>

                            </div>
                            """,
                            unsafe_allow_html=True
                        )

                        # -----------------------------------
                        # SERIES EXPANDED
                        # -----------------------------------

                        if is_series_open:

                            series_books = series_books.sort_values(
                                by=[
                                    "Series Number",
                                    "Title"
                                ],
                                na_position="last"
                            )

                            for book_number, (
                                _,
                                book
                            ) in enumerate(
                                series_books.iterrows(),
                                start=1
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

                                favorite = (
                                    " ♥"
                                    if book.get(
                                        "Favorite",
                                        False
                                    )
                                    else ""
                                )

                                status = html.escape(
                                    str(
                                        book.get(
                                            "Status",
                                            ""
                                        )
                                    )
                                )

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
                                            f"Book {book_number}"
                                        )

                                else:

                                    number_text = (
                                        f"Book {book_number}"
                                    )

                                if cover:

                                    st.markdown(
                                        f"""
                                        <div class="book-card">

                                            <div style="
                                                display:flex;
                                                gap:15px;
                                                align-items:center;
                                            ">

                                                <img
                                                    class="cover-small"
                                                    src="{html.escape(cover)}"
                                                >

                                                <div>

                                                    <div class="book-title">
                                                        {number_text}
                                                        ·
                                                        {title}
                                                        {favorite}
                                                    </div>

                                                    <div class="book-meta">
                                                        {status}
                                                    </div>

                                                </div>

                                            </div>

                                        </div>
                                        """,
                                        unsafe_allow_html=True
                                    )

                                else:

                                    st.markdown(
                                        f"""
                                        <div class="book-card">

                                            <div class="book-title">
                                                {number_text}
                                                ·
                                                {title}
                                                {favorite}
                                            </div>

                                            <div class="book-meta">
                                                {status}
                                            </div>

                                        </div>
                                        """,
                                        unsafe_allow_html=True
                                    )

        st.markdown(
            "</div>",
            unsafe_allow_html=True
        )

# ============================================================
# BOOKS TAB
# ============================================================

with books_tab:

    st.markdown(
        "## Books"
    )

    if library.empty:

        st.info(
            "No books yet."
        )

    else:

        filter_choice = st.radio(
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

        if filter_choice == "Favorites":

            books = books[
                books["Favorite"] == True
            ]

        elif filter_choice != "All":

            books = books[
                books["Status"]
                == filter_choice
            ]

        for index, book in books.iterrows():

            cover = str(
                book.get(
                    "Cover",
                    ""
                )
                or ""
            )

            col1, col2, col3 = st.columns(
                [1, 5, 1]
            )

            with col1:

                if cover:

                    st.image(
                        cover,
                        width=85
                    )

            with col2:

                st.markdown(
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
                                book["Status"]
                            )
                        )}
                    </div>
                    """,
                    unsafe_allow_html=True
                )

            with col3:

                new_favorite = st.checkbox(
                    "♥",
                    value=bool(
                        book.get(
                            "Favorite",
                            False
                        )
                    ),
                    key=f"favorite_{index}",
                )

                if new_favorite != bool(
                    book.get(
                        "Favorite",
                        False
                    )
                ):

                    st.session_state.library.loc[
                        index,
                        "Favorite"
                    ] = new_favorite

                    st.rerun()

# ============================================================
# ADD BOOK
# ============================================================

with add_tab:

    st.markdown(
        "## Add a Book"
    )

    st.write(
        "Add a book individually when you don't "
        "want to import an entire list."
    )

    with st.form(
        "add_book_form"
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
                "Leave blank if standalone"
            )
        )

        series_number = st.number_input(
            "Series number",
            min_value=0.0,
            value=0.0,
            step=0.5
        )

        isbn = st.text_input(
            "ISBN"
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
            "Your rating",
            0,
            5,
            0
        )

        favorite = st.checkbox(
            "♥ Favorite"
        )

        submit = st.form_submit_button(
            "Add Book"
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

                if not series.strip():

                    series = "Standalone"

                cover = get_cover(
                    title,
                    author,
                    isbn
                )

                new_book = pd.DataFrame(
                    [{
                        "Title": title.strip(),
                        "Author": author.strip(),
                        "Series": series.strip(),
                        "Series Number":
                            series_number
                            if series_number
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
                    }]
                )

                st.session_state.library = pd.concat(
                    [
                        st.session_state.library,
                        new_book
                    ],
                    ignore_index=True
                )

                st.success(
                    f"{title} was added to your tree."
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
        "Import a Goodreads CSV, StoryGraph export, "
        "or another compatible book-list CSV."
    )

    uploaded = st.file_uploader(
        "Choose your CSV file",
        type=["csv"]
    )

    if uploaded:

        if st.button(
            "Import Books"
        ):

            with st.spinner(
                "Building your book tree..."
            ):

                success = import_books(
                    uploaded
                )

            if success:

                st.success(
                    "Your books have been imported."
                )

                st.rerun()

# ============================================================
# FOOTER
# ============================================================

st.markdown(
    f"""
    <div style="
        text-align:center;
        margin-top:55px;
        padding:20px;
        color:{theme["muted"]};
        font-size:13px;
    ">
        My Book Tree · Your reading life, beautifully connected.
    </div>
    """,
    unsafe_allow_html=True
)
