# ============================================================
# 📚 MY BOOK TREE
# A visual book library
# ============================================================

import streamlit as st
import pandas as pd
import requests
import re
import html
import json
from pathlib import Path

# ============================================================
# PAGE CONFIG
# ============================================================

st.set_page_config(
    page_title="My Book Tree",
    page_icon="🌳",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ============================================================
# SESSION STATE
# ============================================================

if "library" not in st.session_state:
    st.session_state.library = pd.DataFrame(
        columns=[
            "Title",
            "Author",
            "Series",
            "Series Number",
            "ISBN",
            "Cover",
            "Status",
            "Favorite",
            "Rating",
            "Notes"
        ]
    )

if "uploaded" not in st.session_state:
    st.session_state.uploaded = False

if "cover_cache" not in st.session_state:
    st.session_state.cover_cache = {}

# ============================================================
# COLOR THEMES
# ============================================================

THEMES = {
    "Forest": {
        "background": "#10231c",
        "background2": "#18352a",
        "card": "#214538",
        "card2": "#2d5948",
        "accent": "#8fbf9f",
        "accent2": "#c5d9b7",
        "text": "#f1ead7",
        "muted": "#b8c8b4",
        "line": "#668d73",
        "gold": "#d6bd72"
    },

    "Emerald": {
        "background": "#071f1a",
        "background2": "#0e342b",
        "card": "#15483b",
        "card2": "#1d604e",
        "accent": "#72c7a5",
        "accent2": "#b9e2cf",
        "text": "#f1f5e9",
        "muted": "#a9c8ba",
        "line": "#4f9279",
        "gold": "#d7c47a"
    },

    "Midnight Blue": {
        "background": "#0b1424",
        "background2": "#13223b",
        "card": "#1a3150",
        "card2": "#234366",
        "accent": "#8db7d9",
        "accent2": "#c5d8e8",
        "text": "#edf3f7",
        "muted": "#aebdcb",
        "line": "#527ca3",
        "gold": "#d9c47b"
    },

    "Sapphire": {
        "background": "#08182b",
        "background2": "#102b49",
        "card": "#163e66",
        "card2": "#205685",
        "accent": "#75a9d4",
        "accent2": "#bfd5e8",
        "text": "#f3f7fb",
        "muted": "#abbfd3",
        "line": "#507da6",
        "gold": "#d8c47a"
    },

    "Teal": {
        "background": "#08201f",
        "background2": "#103a38",
        "card": "#16504d",
        "card2": "#216966",
        "accent": "#71c3bc",
        "accent2": "#b9ded9",
        "text": "#eff7f4",
        "muted": "#a9c9c5",
        "line": "#4c918c",
        "gold": "#d9c37a"
    },

    "Lavender": {
        "background": "#17152b",
        "background2": "#242044",
        "card": "#332e59",
        "card2": "#443d72",
        "accent": "#aaa1d4",
        "accent2": "#d2cdec",
        "text": "#f5f3fb",
        "muted": "#bdb8d0",
        "line": "#756da5",
        "gold": "#d8c47b"
    },

    "Rose": {
        "background": "#28151e",
        "background2": "#42202e",
        "card": "#5a2b3e",
        "card2": "#71364d",
        "accent": "#d59aaf",
        "accent2": "#ebc4d0",
        "text": "#fff3f5",
        "muted": "#d1b1bb",
        "line": "#a35e78",
        "gold": "#d9c27a"
    },

    "Autumn": {
        "background": "#20180f",
        "background2": "#352414",
        "card": "#4b321c",
        "card2": "#634321",
        "accent": "#c69a61",
        "accent2": "#e0c59a",
        "text": "#f8f0df",
        "muted": "#c8b99f",
        "line": "#936b3e",
        "gold": "#dfc475"
    }
}

# ============================================================
# GLOBAL CSS
# ============================================================

def apply_theme(theme_name):

    t = THEMES[theme_name]

    st.markdown(
        f"""
        <style>

        .stApp {{
            background:
                radial-gradient(
                    circle at 15% 0%,
                    {t["background2"]} 0%,
                    {t["background"]} 48%,
                    {t["background"]} 100%
                );
            color: {t["text"]};
        }}

        .block-container {{
            max-width: 1500px;
            padding-top: 2rem;
            padding-bottom: 4rem;
        }}

        h1, h2, h3 {{
            color: {t["text"]} !important;
            font-family: Georgia, serif !important;
        }}

        p, label, span, div {{
            font-family: Georgia, serif;
        }}

        [data-testid="stSidebar"] {{
            background: {t["background2"]};
            border-right: 1px solid {t["line"]};
        }}

        [data-testid="stSidebar"] * {{
            color: {t["text"]} !important;
        }}

        .hero {{
            padding: 42px 35px;
            border-radius: 28px;
            background:
                linear-gradient(
                    135deg,
                    {t["card2"]},
                    {t["background2"]}
                );
            border: 1px solid {t["line"]};
            margin-bottom: 25px;
            box-shadow: 0 18px 45px rgba(0,0,0,.22);
        }}

        .hero-title {{
            font-size: 52px;
            font-weight: 700;
            letter-spacing: 2px;
            color: {t["text"]};
        }}

        .hero-sub {{
            font-size: 19px;
            color: {t["muted"]};
            margin-top: 8px;
        }}

        .stat {{
            background: {t["card"]};
            border: 1px solid {t["line"]};
            border-radius: 18px;
            padding: 18px;
            text-align: center;
            box-shadow: 0 8px 20px rgba(0,0,0,.18);
        }}

        .stat-number {{
            font-size: 30px;
            font-weight: bold;
            color: {t["accent2"]};
        }}

        .stat-label {{
            color: {t["muted"]};
            font-size: 13px;
            margin-top: 3px;
        }}

        .tree-wrapper {{
            overflow-x: auto;
            padding: 40px 20px 70px;
        }}

        .tree-root {{
            text-align: center;
            margin-bottom: 45px;
        }}

        .root-node {{
            display: inline-block;
            padding: 18px 35px;
            border-radius: 50px;
            background:
                linear-gradient(
                    135deg,
                    {t["card2"]},
                    {t["card"]}
                );
            border: 2px solid {t["accent"]};
            color: {t["text"]};
            font-size: 25px;
            font-weight: bold;
            box-shadow: 0 10px 30px rgba(0,0,0,.25);
        }}

        .author-tree {{
            display: flex;
            flex-wrap: wrap;
            justify-content: center;
            gap: 35px;
            align-items: flex-start;
        }}

        .author-branch {{
            position: relative;
            width: 330px;
            padding-top: 28px;
        }}

        .author-branch::before {{
            content: "";
            position: absolute;
            width: 2px;
            height: 28px;
            background: {t["line"]};
            top: 0;
            left: 50%;
        }}

        .author-node {{
            padding: 15px 20px;
            border-radius: 17px;
            background: {t["card2"]};
            border: 1px solid {t["accent"]};
            text-align: center;
            color: {t["text"]};
            font-size: 20px;
            font-weight: bold;
            box-shadow: 0 8px 20px rgba(0,0,0,.2);
            margin-bottom: 20px;
        }}

        .author-count {{
            display: block;
            font-size: 12px;
            color: {t["muted"]};
            margin-top: 5px;
            font-weight: normal;
        }}

        .series-branch {{
            position: relative;
            margin: 14px 0 14px 22px;
            padding-left: 22px;
            border-left: 2px solid {t["line"]};
        }}

        .series-node {{
            padding: 11px 14px;
            border-radius: 12px;
            background: {t["card"]};
            border: 1px solid {t["line"]};
            color: {t["accent2"]};
            font-size: 16px;
            font-weight: bold;
            margin-bottom: 9px;
        }}

        .series-progress {{
            color: {t["muted"]};
            font-size: 11px;
            font-weight: normal;
        }}

        .book-node {{
            position: relative;
            display: flex;
            gap: 11px;
            align-items: center;
            padding: 9px;
            margin: 7px 0 7px 15px;
            background: {t["background2"]};
            border: 1px solid {t["line"]};
            border-radius: 11px;
            min-height: 65px;
        }}

        .book-node::before {{
            content: "";
            position: absolute;
            left: -17px;
            top: 50%;
            width: 15px;
            height: 2px;
            background: {t["line"]};
        }}

        .book-cover {{
            width: 40px;
            height: 59px;
            object-fit: cover;
            border-radius: 4px;
            flex-shrink: 0;
            box-shadow: 0 4px 10px rgba(0,0,0,.35);
        }}

        .cover-placeholder {{
            width: 40px;
            height: 59px;
            border-radius: 4px;
            background: {t["card2"]};
            display: flex;
            align-items: center;
            justify-content: center;
            text-align: center;
            font-size: 8px;
            color: {t["muted"]};
            flex-shrink: 0;
        }}

        .book-title {{
            color: {t["text"]};
            font-size: 13px;
            line-height: 1.25;
        }}

        .book-meta {{
            color: {t["muted"]};
            font-size: 10px;
            margin-top: 4px;
        }}

        .favorite {{
            color: {t["gold"]};
            font-size: 14px;
        }}

        .section-card {{
            background: {t["card"]};
            border: 1px solid {t["line"]};
            border-radius: 20px;
            padding: 25px;
            margin-bottom: 20px;
        }}

        .empty {{
            text-align: center;
            padding: 80px 20px;
            color: {t["muted"]};
            font-size: 20px;
        }}

        </style>
        """,
        unsafe_allow_html=True
    )

# ============================================================
# HELPERS
# ============================================================

def clean_text(value):
    if pd.isna(value):
        return ""
    return re.sub(r"\s+", " ", str(value)).strip()


def find_column(df, names):
    normalized = {
        str(c).strip().lower(): c
        for c in df.columns
    }

    for name in names:
        if name.lower() in normalized:
            return normalized[name.lower()]

    for name in names:
        for col in df.columns:
            if name.lower() in str(col).lower():
                return col

    return None


def detect_series(title):
    title = clean_text(title)

    patterns = [
        r"\(([^()]*)#\s*(\d+(?:\.\d+)?)\)",
        r"\[([^\[\]]*)#\s*(\d+(?:\.\d+)?)\]",
        r"\(([^()]*)\bBook\s+(\d+(?:\.\d+)?)",
        r"\[([^\[\]]*)\bBook\s+(\d+(?:\.\d+)?)"
    ]

    for pattern in patterns:
        match = re.search(
            pattern,
            title,
            flags=re.IGNORECASE
        )

        if match:
            name = clean_text(match.group(1))

            name = re.sub(
                r",?\s*#\s*\d+(?:\.\d+)?",
                "",
                name,
                flags=re.IGNORECASE
            )

            name = re.sub(
                r"\bBook\s+\d+(?:\.\d+)?",
                "",
                name,
                flags=re.IGNORECASE
            )

            name = name.strip(" ,-:")

            if name:
                return name

    return "Standalone"


def detect_number(title):
    title = clean_text(title)

    patterns = [
        r"#\s*(\d+(?:\.\d+)?)",
        r"\bBook\s+(\d+(?:\.\d+)?)",
        r"\bVol(?:ume)?\.?\s+(\d+(?:\.\d+)?)"
    ]

    for pattern in patterns:
        match = re.search(
            pattern,
            title,
            flags=re.IGNORECASE
        )

        if match:
            try:
                return float(match.group(1))
            except Exception:
                pass

    return None


def normalize_status(value):
    value = clean_text(value).lower()

    if "currently" in value or "reading" in value:
        return "Currently Reading"

    if "read" in value and "want" not in value:
        return "Read"

    if "favorite" in value:
        return "Want to Read"

    return "Want to Read"


def cover_from_isbn(isbn):
    isbn = re.sub(r"\D", "", clean_text(isbn))

    if not isbn:
        return ""

    return (
        "https://covers.openlibrary.org/b/isbn/"
        + isbn
        + "-M.jpg"
    )


def make_cover_from_row(row):
    cover = clean_text(row.get("Cover", ""))

    if cover.startswith("http"):
        return cover

    isbn = clean_text(row.get("ISBN", ""))

    return cover_from_isbn(isbn)


# ============================================================
# IMPORT LIBRARY
# ============================================================

def import_file(uploaded_file):

    if uploaded_file is None:
        return

    try:
        if uploaded_file.name.lower().endswith(".csv"):
            raw = pd.read_csv(
                uploaded_file,
                encoding="utf-8",
                low_memory=False
            )
        else:
            raw = pd.read_excel(uploaded_file)

    except Exception as e:
        st.error(f"Could not read this file: {e}")
        return

    title_col = find_column(
        raw,
        [
            "Title",
            "Book Title",
            "Name"
        ]
    )

    author_col = find_column(
        raw,
        [
            "Author",
            "Author Name",
            "Authors"
        ]
    )

    if title_col is None:
        st.error(
            "I couldn't find a Title column in this file."
        )
        return

    if author_col is None:
        st.error(
            "I couldn't find an Author column in this file."
        )
        return

    series_col = find_column(
        raw,
        [
            "Series",
            "Series Name"
        ]
    )

    number_col = find_column(
        raw,
        [
            "Series Number",
            "Series #",
            "Number"
        ]
    )

    isbn_col = find_column(
        raw,
        [
            "ISBN13",
            "ISBN",
            "ISBN-13"
        ]
    )

    cover_col = find_column(
        raw,
        [
            "Cover",
            "Cover URL",
            "Cover Image",
            "Image",
            "Image URL",
            "Book Cover"
        ]
    )

    status_col = find_column(
        raw,
        [
            "Status",
            "Exclusive Shelf",
            "Shelf",
            "Reading Status"
        ]
    )

    rating_col = find_column(
        raw,
        [
            "My Rating",
            "Rating"
        ]
    )

    favorite_col = find_column(
        raw,
        [
            "Favorite",
            "Favorites",
            "Favourite"
        ]
    )

    records = []

    for _, row in raw.iterrows():

        title = clean_text(row[title_col])

        if not title:
            continue

        author = clean_text(row[author_col])

        if series_col:
            series = clean_text(row[series_col])
        else:
            series = detect_series(title)

        if not series:
            series = "Standalone"

        if number_col:
            try:
                number = float(row[number_col])
            except Exception:
                number = detect_number(title)
        else:
            number = detect_number(title)

        isbn = ""
        if isbn_col:
            isbn = re.sub(
                r"\D",
                "",
                clean_text(row[isbn_col])
            )

        cover = ""
        if cover_col:
            cover = clean_text(row[cover_col])

        status = "Want to Read"
        if status_col:
            status = normalize_status(row[status_col])

        rating = ""
        if rating_col:
            rating = clean_text(row[rating_col])

        favorite = False
        if favorite_col:
            fav = clean_text(row[favorite_col]).lower()
            favorite = fav in [
                "true",
                "yes",
                "1",
                "favorite",
                "favourite"
            ]

        records.append(
            {
                "Title": title,
                "Author": author,
                "Series": series,
                "Series Number": number,
                "ISBN": isbn,
                "Cover": cover,
                "Status": status,
                "Favorite": favorite,
                "Rating": rating,
                "Notes": ""
            }
        )

    new_library = pd.DataFrame(records)

    st.session_state.library = new_library
    st.session_state.uploaded = True

    st.success(
        f"Imported {len(new_library):,} books."
    )


# ============================================================
# TITLE / HERO
# ============================================================

st.sidebar.markdown("## 🌳 My Book Tree")

theme = st.sidebar.selectbox(
    "Choose your color scheme",
    list(THEMES.keys())
)

apply_theme(theme)

st.markdown(
    """
    <div class="hero">
        <div class="hero-title">🌳 MY BOOK TREE</div>
        <div class="hero-sub">
            Your books, connected.
            Build a visual library from your reading life.
        </div>
    </div>
    """,
    unsafe_allow_html=True
)

# ============================================================
# SIDEBAR IMPORT
# ============================================================

st.sidebar.markdown("---")
st.sidebar.markdown("### 📥 Import Books")

uploaded_file = st.sidebar.file_uploader(
    "Upload your book list",
    type=["csv", "xlsx"],
    help=(
        "Goodreads, StoryGraph, or another spreadsheet "
        "with Title and Author columns."
    )
)

if uploaded_file is not None:

    file_key = (
        uploaded_file.name
        + str(uploaded_file.size)
    )

    if st.session_state.get(
        "last_uploaded_file"
    ) != file_key:

        import_file(uploaded_file)

        st.session_state.last_uploaded_file = file_key

# ============================================================
# SIDEBAR ADD BOOK
# ============================================================

st.sidebar.markdown("---")
st.sidebar.markdown("### ➕ Add a Book")

with st.sidebar.form("add_book_form"):

    new_title = st.text_input("Title")

    new_author = st.text_input("Author")

    new_series = st.text_input(
        "Series",
        placeholder="Leave blank for standalone"
    )

    new_number = st.text_input(
        "Series number",
        placeholder="Example: 1"
    )

    new_isbn = st.text_input(
        "ISBN",
        placeholder="Optional"
    )

    new_cover = st.text_input(
        "Cover URL",
        placeholder="Optional"
    )

    new_status = st.selectbox(
        "Reading status",
        [
            "Want to Read",
            "Currently Reading",
            "Read"
        ]
    )

    new_favorite = st.checkbox(
        "❤️ Favorite"
    )

    add_book = st.form_submit_button(
        "Add Book"
    )

    if add_book:

        if not new_title.strip():
            st.error("Please enter a book title.")

        elif not new_author.strip():
            st.error("Please enter an author.")

        else:

            try:
                number = float(new_number)
            except Exception:
                number = None

            new_row = pd.DataFrame(
                [
                    {
                        "Title": new_title.strip(),
                        "Author": new_author.strip(),
                        "Series": (
                            new_series.strip()
                            if new_series.strip()
                            else "Standalone"
                        ),
                        "Series Number": number,
                        "ISBN": re.sub(
                            r"\D",
                            "",
                            new_isbn
                        ),
                        "Cover": new_cover.strip(),
                        "Status": new_status,
                        "Favorite": new_favorite,
                        "Rating": "",
                        "Notes": ""
                    }
                ]
            )

            st.session_state.library = pd.concat(
                [
                    st.session_state.library,
                    new_row
                ],
                ignore_index=True
            )

            st.success("Book added!")

# ============================================================
# LIBRARY
# ============================================================

library = st.session_state.library.copy()

# ============================================================
# STATS
# ============================================================

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

favorite_count = (
    int(library["Favorite"].sum())
    if total
    else 0
)

cols = st.columns(5)

stats = [
    (total, "BOOKS"),
    (authors, "AUTHORS"),
    (series_count, "SERIES"),
    (read_count, "READ"),
    (favorite_count, "FAVORITES")
]

for col, (number, label) in zip(
    cols,
    stats
):

    with col:

        st.markdown(
            f"""
            <div class="stat">
                <div class="stat-number">
                    {number:,}
                </div>
                <div class="stat-label">
                    {label}
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )

st.write("")

# ============================================================
# EMPTY LIBRARY
# ============================================================

if total == 0:

    st.markdown(
        """
        <div class="empty">
            <div style="font-size:60px;">🌱</div>
            <h2>Your book tree is waiting to grow.</h2>
            <p>
                Upload a CSV or spreadsheet from the sidebar,
                or add your first book manually.
            </p>
        </div>
        """,
        unsafe_allow_html=True
    )

    st.stop()

# ============================================================
# SEARCH / FILTERS
# ============================================================

st.markdown("### 🔎 Explore Your Library")

filter_cols = st.columns(
    [2, 1, 1, 1]
)

with filter_cols[0]:

    search = st.text_input(
        "Search",
        placeholder=(
            "Search books, authors, or series..."
        ),
        label_visibility="collapsed"
    )

with filter_cols[1]:

    status_filter = st.selectbox(
        "Status",
        [
            "All",
            "Read",
            "Currently Reading",
            "Want to Read"
        ],
        label_visibility="collapsed"
    )

with filter_cols[2]:

    author_options = [
        "All"
    ] + sorted(
        library["Author"]
        .dropna()
        .unique()
        .tolist(),
        key=lambda x: str(x).lower()
    )

    author_filter = st.selectbox(
        "Author",
        author_options,
        label_visibility="collapsed"
    )

with filter_cols[3]:

    view = st.selectbox(
        "View",
        [
            "🌳 Tree",
            "📚 Bookshelf",
            "❤️ Favorites",
            "📖 Reading"
        ],
        label_visibility="collapsed"
    )

# ============================================================
# FILTER DATA
# ============================================================

filtered = library.copy()

if search:

    term = search.lower()

    filtered = filtered[
        filtered["Title"]
        .fillna("")
        .str.lower()
        .str.contains(term, na=False)
        |
        filtered["Author"]
        .fillna("")
        .str.lower()
        .str.contains(term, na=False)
        |
        filtered["Series"]
        .fillna("")
        .str.lower()
        .str.contains(term, na=False)
    ]

if status_filter != "All":

    filtered = filtered[
        filtered["Status"] == status_filter
    ]

if author_filter != "All":

    filtered = filtered[
        filtered["Author"] == author_filter
    ]

if view == "❤️ Favorites":

    filtered = filtered[
        filtered["Favorite"] == True
    ]

elif view == "📖 Reading":

    filtered = filtered[
        filtered["Status"] == "Currently Reading"
    ]

# ============================================================
# TREE VIEW
# ============================================================

def build_tree(data):

    if data.empty:

        return """
        <div class="empty">
            No books match your search.
        </div>
        """

    output = """
    <div class="tree-wrapper">

        <div class="tree-root">
            <div class="root-node">
                🌳 MY LIBRARY
            </div>
        </div>

        <div class="author-tree">
    """

    authors_list = sorted(
        data["Author"]
        .fillna("Unknown Author")
        .unique(),
        key=lambda x: str(x).lower()
    )

    for author_name in authors_list:

        author_data = data[
            data["Author"].fillna(
                "Unknown Author"
            ) == author_name
        ].copy()

        output += f"""
        <div class="author-branch">

            <div class="author-node">
                ✦ {html.escape(str(author_name))}
                <span class="author-count">
                    {len(author_data)} book
                    {"s" if len(author_data) != 1 else ""}
                </span>
            </div>
        """

        series_list = sorted(
            author_data["Series"]
            .fillna("Standalone")
            .unique(),
            key=lambda x: str(x).lower()
        )

        for series_name in series_list:

            series_data = author_data[
                author_data["Series"].fillna(
                    "Standalone"
                ) == series_name
            ].copy()

            read = len(
                series_data[
                    series_data["Status"] == "Read"
                ]
            )

            total_series = len(series_data)

            if series_name == "Standalone":

                series_title = "📖 Standalone"

            else:

                series_title = (
                    "📚 "
                    + html.escape(str(series_name))
                    + f"""
                    <span class="series-progress">
                        · {read}/{total_series} read
                    </span>
                    """
                )

            output += f"""
            <div class="series-branch">

                <div class="series-node">
                    {series_title}
                </div>
            """

            series_data["sort_number"] = pd.to_numeric(
                series_data["Series Number"],
                errors="coerce"
            )

            series_data = series_data.sort_values(
                by=[
                    "sort_number",
                    "Title"
                ],
                na_position="last"
            )

            for _, book in series_data.iterrows():

                title = html.escape(
                    clean_text(book["Title"])
                )

                status = clean_text(
                    book["Status"]
                )

                favorite = (
                    " <span class='favorite'>♥</span>"
                    if bool(book["Favorite"])
                    else ""
                )

                if status == "Read":
                    icon = "✓"
                elif status == "Currently Reading":
                    icon = "📖"
                else:
                    icon = "○"

                cover = make_cover_from_row(book)

                if cover:

                    cover_html = f"""
                    <img
                        class="book-cover"
                        src="{html.escape(cover)}"
                        loading="lazy"
                    >
                    """

                else:

                    cover_html = f"""
                    <div class="cover-placeholder">
                        {html.escape(
                            clean_text(book["Title"])[:20]
                        )}
                    </div>
                    """

                rating = ""

                if clean_text(book["Rating"]):
                    rating = (
                        " · ★ "
                        + html.escape(
                            clean_text(book["Rating"])
                        )
                    )

                output += f"""
                <div class="book-node">

                    {cover_html}

                    <div>

                        <div class="book-title">
                            {icon}
                            {title}
                            {favorite}
                        </div>

                        <div class="book-meta">
                            {status}{rating}
                        </div>

                    </div>

                </div>
                """

            output += """
            </div>
            """

        output += """
        </div>
        """

    output += """
        </div>
    </div>
    """

    return output


# ============================================================
# BOOKSHELF VIEW
# ============================================================

def build_shelf(data):

    if data.empty:

        return """
        <div class="empty">
            No books match your search.
        </div>
        """

    output = """
    <div style="
        display:grid;
        grid-template-columns:
            repeat(auto-fill,minmax(180px,1fr));
        gap:24px;
        padding:25px 5px;
    ">
    """

    for _, book in data.iterrows():

        title = html.escape(
            clean_text(book["Title"])
        )

        author = html.escape(
            clean_text(book["Author"])
        )

        cover = make_cover_from_row(book)

        favorite = (
            "♥"
            if bool(book["Favorite"])
            else ""
        )

        if cover:

            image = f"""
            <img
                src="{html.escape(cover)}"
                loading="lazy"
                style="
                    width:150px;
                    height:225px;
                    object-fit:cover;
                    border-radius:8px;
                    box-shadow:
                        0 10px 25px rgba(0,0,0,.35);
                "
            >
            """

        else:

            image = f"""
            <div style="
                width:150px;
                height:225px;
                border-radius:8px;
                background:#2a3f36;
                display:flex;
                align-items:center;
                justify-content:center;
                text-align:center;
                padding:15px;
                color:#dce7d9;
            ">
                {title}
            </div>
            """

        output += f"""
        <div style="
            text-align:center;
            padding:12px;
        ">

            {image}

            <div style="
                margin-top:12px;
                font-weight:bold;
                font-size:15px;
            ">
                {title} {favorite}
            </div>

            <div style="
                margin-top:5px;
                opacity:.7;
                font-size:13px;
            ">
                {author}
            </div>

        </div>
        """

    output += "</div>"

    return output


# ============================================================
# DISPLAY
# ============================================================

if view == "🌳 Tree":

    st.markdown(
        f"""
        **Showing {len(filtered):,} of {len(library):,} books**
        """,
    )

    st.components.v1.html(
        build_tree(filtered),
        height=850,
        scrolling=True
    )

elif view == "📚 Bookshelf":

    st.markdown(
        f"**Showing {len(filtered):,} books**"
    )

    st.components.v1.html(
        build_shelf(filtered),
        height=900,
        scrolling=True
    )

elif view == "❤️ Favorites":

    st.markdown(
        f"**{len(filtered):,} favorite books**"
    )

    if filtered.empty:

        st.info(
            "You haven't marked any books as favorites yet."
        )

    else:

        st.components.v1.html(
            build_shelf(filtered),
            height=900,
            scrolling=True
        )

elif view == "📖 Reading":

    st.markdown(
        f"**{len(filtered):,} currently-reading books**"
    )

    if filtered.empty:

        st.info(
            "You don't have any books marked "
            "Currently Reading."
        )

    else:

        st.components.v1.html(
            build_shelf(filtered),
            height=900,
            scrolling=True
        )

# ============================================================
# EDIT BOOKS
# ============================================================

st.markdown("---")

with st.expander("✏️ Edit your library"):

    st.caption(
        "You can change status, favorites, series, "
        "ratings, and other information here."
    )

    edited = st.data_editor(
        st.session_state.library,
        use_container_width=True,
        num_rows="dynamic",
        column_config={
            "Favorite": st.column_config.CheckboxColumn(
                "❤️ Favorite"
            ),
            "Status": st.column_config.SelectboxColumn(
                "Reading Status",
                options=[
                    "Want to Read",
                    "Currently Reading",
                    "Read"
                ]
            ),
            "Cover": st.column_config.TextColumn(
                "Cover URL"
            )
        },
        hide_index=True
    )

    if st.button(
        "💾 Save Library Changes",
        type="primary"
    ):

        st.session_state.library = edited.copy()

        st.success(
            "Your library changes were saved."
        )

        st.rerun()

# ============================================================
# EXPORT
# ============================================================

st.sidebar.markdown("---")
st.sidebar.markdown("### 💾 Save Your Library")

if not st.session_state.library.empty:

    csv_data = st.session_state.library.to_csv(
        index=False
    )

    st.sidebar.download_button(
        "Download Library CSV",
        data=csv_data,
        file_name="my_book_tree_library.csv",
        mime="text/csv"
    )

# ============================================================
# FOOTER
# ============================================================

st.markdown(
    """
    <div style="
        text-align:center;
        margin-top:60px;
        opacity:.55;
        font-size:13px;
    ">
        ✦ My Book Tree ✦
    </div>
    """,
    unsafe_allow_html=True
)
