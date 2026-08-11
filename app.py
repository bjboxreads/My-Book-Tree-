import streamlit as st
import pandas as pd
import requests
import re
import html

# ============================================================
# PAGE CONFIG
# ============================================================

st.set_page_config(
    page_title="My Book Tree",
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="collapsed"
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
        "page": "#121923",
        "surface": "#1C2735",
        "surface2": "#293746",
        "card": "#202E3D",
        "text": "#F4EBD8",
        "muted": "#C3C8C7",
        "accent": "#C6A15B",
        "accent2": "#6B91A8",
        "line": "#C6A15B",
        "button_text": "#101923",
        "cover_border": "#C6A15B",
    },

    "Enchanted Garden": {
        "page": "#102A28",
        "surface": "#163A35",
        "surface2": "#214B42",
        "card": "#194239",
        "text": "#FFF5E5",
        "muted": "#C8D8CF",
        "accent": "#E1B34B",
        "accent2": "#A95D86",
        "line": "#73B58D",
        "button_text": "#102A28",
        "cover_border": "#E1B34B",
    },

    "Gothic Romance": {
        "page": "#15121D",
        "surface": "#211A2A",
        "surface2": "#302039",
        "card": "#261D31",
        "text": "#FAF1F5",
        "muted": "#D0C2CC",
        "accent": "#C94B69",
        "accent2": "#8D6BB3",
        "line": "#C94B69",
        "button_text": "#FFFFFF",
        "cover_border": "#C94B69",
    },

    "Victorian Parlor": {
        "page": "#102A35",
        "surface": "#173C49",
        "surface2": "#235362",
        "card": "#1D4655",
        "text": "#FFF4E1",
        "muted": "#C9D7D7",
        "accent": "#D7A23A",
        "accent2": "#D35C76",
        "line": "#D7A23A",
        "button_text": "#102A35",
        "cover_border": "#D7A23A",
    },

    "Midnight Bookshop": {
        "page": "#0D1730",
        "surface": "#152448",
        "surface2": "#20335B",
        "card": "#192C52",
        "text": "#F6F3FF",
        "muted": "#C7CBE0",
        "accent": "#E2B84B",
        "accent2": "#64B8C4",
        "line": "#64B8C4",
        "button_text": "#0D1730",
        "cover_border": "#E2B84B",
    },

    "Literary Arts & Crafts": {
        "page": "#173A3B",
        "surface": "#225050",
        "surface2": "#2D6260",
        "card": "#285958",
        "text": "#FFF7E8",
        "muted": "#D2D7C7",
        "accent": "#E0A52F",
        "accent2": "#D75B46",
        "line": "#E0A52F",
        "button_text": "#173A3B",
        "cover_border": "#D75B46",
    },

    "Fantasy Bookshelf": {
        "page": "#171531",
        "surface": "#242052",
        "surface2": "#302A68",
        "card": "#29235A",
        "text": "#FFF8E8",
        "muted": "#D0CCE6",
        "accent": "#E5B63E",
        "accent2": "#6BA5D5",
        "line": "#9D75D4",
        "button_text": "#171531",
        "cover_border": "#E5B63E",
    },

    "Modern Book Nook": {
        "page": "#102C35",
        "surface": "#173F4A",
        "surface2": "#245866",
        "card": "#1E4B58",
        "text": "#FFF8EA",
        "muted": "#CBD8D8",
        "accent": "#F0B544",
        "accent2": "#E56B55",
        "line": "#F0B544",
        "button_text": "#102C35",
        "cover_border": "#F0B544",
    },
}

# ============================================================
# SESSION STATE
# ============================================================

if "theme" not in st.session_state:
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
            {theme["page"]} 42%
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
    padding: 10px 0 25px;
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

.theme-label {{
    font-family:
        "Cormorant Garamond",
        Georgia,
        serif;
    font-size: 20px;
    font-weight: 700;
    color: {theme["text"]};
    margin-bottom: 4px;
}}

/* =========================================================
   THE IMPORTANT PART:
   FORCE THE THEME DROPDOWN AND ITS OPEN MENU TO BE READABLE
   ========================================================= */

div[data-testid="stSelectbox"] label {{
    color: {theme["text"]} !important;
    font-weight: 600 !important;
}}

div[data-baseweb="select"] > div {{
    background: {theme["surface"]} !important;
    border: 2px solid {theme["accent"]} !important;
    border-radius: 12px !important;
    color: {theme["text"]} !important;
}}

div[data-baseweb="select"] span {{
    color: {theme["text"]} !important;
}}

div[data-baseweb="select"] input {{
    color: {theme["text"]} !important;
}}

div[role="listbox"] {{
    background: #17202B !important;
    border: 2px solid #D5A83B !important;
    border-radius: 12px !important;
    padding: 6px !important;
    box-shadow:
        0 14px 35px rgba(0,0,0,.45) !important;
}}

div[role="option"] {{
    background: #17202B !important;
    color: #FFFFFF !important;
    border-radius: 8px !important;
    font-family:
        "DM Sans",
        sans-serif !important;
    font-size: 15px !important;
    font-weight: 600 !important;
    padding: 10px 12px !important;
}}

div[role="option"] * {{
    color: #FFFFFF !important;
}}

div[role="option"]:hover {{
    background: #33485A !important;
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
        0 8px 25px rgba(0,0,0,.15);
}}

.stat-number {{
    font-family:
        "Cormorant Garamond",
        Georgia,
        serif;
    font-size: 32px;
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
   TREE AREA
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
        0 15px 45px rgba(0,0,0,.20);
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
        0 10px 25px rgba(0,0,0,.22);
}}

.root-title {{
    font-family:
        "Cormorant Garamond",
        Georgia,
        serif;
    font-size: 32px;
    font-weight: 700;
}}

.root-subtitle {{
    font-size: 12px;
    font-weight: 600;
    opacity: .85;
}}

.branch-line {{
    width: 3px;
    height: 30px;
    background: {theme["line"]};
    margin: -35px auto 0;
}}

.author-node {{
    background: {theme["card"]};
    border: 2px solid {theme["accent2"]};
    border-radius: 17px;
    padding: 15px 20px;
    margin: 10px 0;
    box-shadow:
        0 8px 20px rgba(0,0,0,.15);
}}

.series-node {{
    background: {theme["surface2"]};
    border: 2px solid {theme["accent"]};
    border-radius: 14px;
    padding: 13px 18px;
    margin: 9px 0 9px 45px;
    box-shadow:
        0 6px 16px rgba(0,0,0,.13);
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
    font-size: 23px;
    font-weight: 700;
    color: {theme["text"]};
}}

.branch-meta {{
    color: {theme["muted"]};
    font-size: 12px;
    margin-top: 2px;
}}

.expand-arrow {{
    color: {theme["accent"]};
    font-size: 20px;
    font-weight: 700;
}}

.book-title {{
    font-family:
        "Cormorant Garamond",
        Georgia,
        serif;
    color: {theme["text"]};
    font-size: 20px;
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
    unsafe_allow_html=True
)

# ============================================================
# COVER LOOKUP
# ============================================================

@st.cache_data(show_spinner=False)
def get_cover(title, author="", isbn=""):

    isbn = re.sub(
        r"\D",
        "",
        str(isbn)
    )

    # Open Library ISBN
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

    # Google Books
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
            "I couldn't find a Title column."
        )

        return

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
            "No books were found."
        )

        return

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
            (i + 1)
            /
            len(new_library)
        )

    progress.empty()

    st.session_state.library = (
        new_library
    )

    st.session_state.open_authors = set()
    st.session_state.open_series = set()


# ============================================================
# HELPER: SAFE ID
# ============================================================

def make_id(text):
    return re.sub(
        r"[^a-zA-Z0-9_-]",
        "_",
        str(text)
    )


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
    key="theme_selector"
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
# TREE
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
                .str.lower()
                .str.contains(
                    query,
                    na=False
                )
                |
                filtered["Author"]
                .fillna("")
                .str.lower()
                .str.contains(
                    query,
                    na=False
                )
                |
                filtered["Series"]
                .fillna("")
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
            .unique(),
            key=lambda x: str(x).lower()
        )

        for author in authors:

            author_id = make_id(author)

            author_books = filtered[
                filtered["Author"]
                .fillna("Unknown Author")
                == author
            ]

            is_open = (
                author_id
                in st.session_state.open_authors
            )

            arrow = "▼" if is_open else "▶"

            # AUTHOR BUTTON

            if st.button(
                f"{arrow}   {author}",
                key=f"author_{author_id}",
                use_container_width=True
            ):

                if is_open:

                    st.session_state.open_authors.remove(
                        author_id
                    )

                    # Close series under it too

                    for series in (
                        author_books["Series"]
                        .fillna("Standalone")
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
                        {html.escape(str(author))}
                    </div>
                    <div class="branch-meta">
                        {len(author_books)} book
                        {"s" if len(author_books) != 1 else ""}
                    </div>
                </div>
                """,
                unsafe_allow_html=True
            )

            # ------------------------------------------------
            # AUTHOR OPEN
            # ------------------------------------------------

            if is_open:

                series_list = sorted(
                    author_books[
                        "Series"
                    ]
                    .fillna("Standalone")
                    .unique(),
                    key=lambda x:
                    str(x).lower()
                )

                for series in series_list:

                    series_id = (
                        f"{author_id}::"
                        f"{make_id(series)}"
                    )

                    series_books = author_books[
                        author_books["Series"]
                        .fillna("Standalone")
                        == series
                    ].copy()

                    is_series_open = (
                        series_id
                        in st.session_state.open_series
                    )

                    # Standalone books do not need
                    # another expandable level.

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

                    else:

                        # SERIES BUTTON

                        if st.button(
                            (
                                f"{'▼' if is_series_open else '▶'}   "
                                f"{series}"
                            ),
                            key=f"series_{series_id}",
                            use_container_width=True
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
                                    📚 {html.escape(str(series))}
                                </div>

                                <div class="branch-meta">
                                    {len(series_books)} book
                                    {"s" if len(series_books) != 1 else ""}
                                </div>

                            </div>
                            """,
                            unsafe_allow_html=True
                        )

                        # ------------------------------------
                        # SERIES OPEN
                        # ------------------------------------

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
                                    "Series Number",
                                    None
                                )

                                if pd.notna(number):

                                    try:

                                        number_text = (
                                            f"Book {int(number)}"
                                            if float(number).is_integer()
                                            else f"Book {number}"
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
                                                        {number_text} ·
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
                                                {number_text} ·
                                                {title}{favorite}
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
            horizontal=True
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

        for _, book in books.iterrows():

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

# ============================================================
# ADD BOOK
# ============================================================

with add_tab:

    st.markdown(
        "## Add a Book"
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
                "Leave blank if it is standalone"
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
                "Read"
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
# IMPORT TAB
# ============================================================

with import_tab:

    st.markdown(
        "## Import Your Library"
    )

    st.write(
        "You can import a Goodreads CSV, "
        "StoryGraph export, or another CSV "
        "containing your books."
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

                import_books(
                    uploaded
                )

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
