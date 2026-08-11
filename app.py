# ============================================================
# MY BOOK TREE
# A visual book library
# ============================================================

import streamlit as st
import pandas as pd
import re
import html
import requests
import json
import os
from pathlib import Path

# ============================================================
# PAGE SETUP
# ============================================================

st.set_page_config(
    page_title="My Book Tree",
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ============================================================
# THEMES
# ============================================================

THEMES = {
    "Classic": {
        "bg": "#F7F3EA",
        "surface": "#FFFFFF",
        "surface2": "#EEE8DC",
        "text": "#292622",
        "muted": "#716B62",
        "accent": "#315C52",
        "accent2": "#B4863D",
        "line": "#8E9D92",
        "book": "#E5D6B8",
        "button_text": "#FFFFFF",
    },

    "Botanical": {
        "bg": "#EEF3E9",
        "surface": "#FAFCF7",
        "surface2": "#DCE7D5",
        "text": "#203326",
        "muted": "#617063",
        "accent": "#356B4A",
        "accent2": "#B07A32",
        "line": "#71927A",
        "book": "#C9DDBF",
        "button_text": "#FFFFFF",
    },

    "Blue & Gold": {
        "bg": "#EAF0F6",
        "surface": "#FFFFFF",
        "surface2": "#D5E0ED",
        "text": "#182B42",
        "muted": "#617086",
        "accent": "#234D73",
        "accent2": "#C49742",
        "line": "#6889A8",
        "book": "#C9D8E8",
        "button_text": "#FFFFFF",
    },

    "Berry": {
        "bg": "#F8EDF2",
        "surface": "#FFF9FB",
        "surface2": "#EED4DF",
        "text": "#351D29",
        "muted": "#755965",
        "accent": "#9C3F62",
        "accent2": "#D18B42",
        "line": "#B56A87",
        "book": "#E4B9C9",
        "button_text": "#FFFFFF",
    },

    "Jewel": {
        "bg": "#E9F2F1",
        "surface": "#FCFFFF",
        "surface2": "#CDE3DF",
        "text": "#173735",
        "muted": "#55716E",
        "accent": "#176B68",
        "accent2": "#9B6A25",
        "line": "#55928D",
        "book": "#BBD8D2",
        "button_text": "#FFFFFF",
    },

    "Night Garden": {
        "bg": "#171E2B",
        "surface": "#222B3B",
        "surface2": "#2D394C",
        "text": "#F3F0E8",
        "muted": "#B7BECA",
        "accent": "#79A78B",
        "accent2": "#D2A65A",
        "line": "#668C7A",
        "book": "#344B46",
        "button_text": "#17201E",
    },

    "Warm Library": {
        "bg": "#F4EBDD",
        "surface": "#FFF9EF",
        "surface2": "#E8D6BB",
        "text": "#38271E",
        "muted": "#786354",
        "accent": "#A64B35",
        "accent2": "#C18A35",
        "line": "#A47A5E",
        "book": "#E4C9A6",
        "button_text": "#FFFFFF",
    },
}

# ============================================================
# SESSION STATE
# ============================================================

if "theme" not in st.session_state:
    st.session_state.theme = "Classic"

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
            "Date Read",
            "Publisher",
            "Pages",
            "Description",
            "Cover"
        ]
    )

theme = THEMES[st.session_state.theme]

# ============================================================
# CSS
# ============================================================

st.markdown(
    f"""
<style>

@import url(
'https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700'
'&family=Playfair+Display:wght@500;600;700&display=swap'
);

html, body, [class*="css"] {{
    font-family: 'DM Sans', sans-serif;
}}

.stApp {{
    background:
        radial-gradient(
            circle at 15% 0%,
            {theme["surface2"]} 0%,
            transparent 28%
        ),
        {theme["bg"]};
    color: {theme["text"]};
}}

.block-container {{
    max-width: 1450px;
    padding-top: 2.5rem;
    padding-bottom: 4rem;
}}

h1, h2, h3 {{
    font-family: 'Playfair Display', Georgia, serif !important;
    color: {theme["text"]} !important;
    letter-spacing: -0.02em;
}}

p, label, span, div {{
    color: {theme["text"]};
}}

.hero {{
    padding: 35px 10px 25px 10px;
}}

.hero-title {{
    font-family: 'Playfair Display', Georgia, serif;
    font-size: 54px;
    font-weight: 600;
    line-height: 1;
    color: {theme["text"]};
    margin-bottom: 12px;
}}

.hero-subtitle {{
    font-size: 18px;
    color: {theme["muted"]};
    letter-spacing: .02em;
}}

.stat {{
    background: {theme["surface"]};
    border-bottom: 3px solid {theme["accent"]};
    padding: 18px 22px;
    border-radius: 14px;
    min-height: 100px;
}}

.stat-number {{
    font-family: 'Playfair Display', Georgia, serif;
    font-size: 30px;
    font-weight: 600;
}}

.stat-label {{
    color: {theme["muted"]};
    font-size: 13px;
    text-transform: uppercase;
    letter-spacing: .08em;
}}

.section-title {{
    font-family: 'Playfair Display', Georgia, serif;
    font-size: 30px;
    margin: 30px 0 12px 0;
}}

.tree-area {{
    margin-top: 25px;
    padding: 25px 5px;
}}

.author-title {{
    font-family: 'Playfair Display', Georgia, serif;
    font-size: 31px;
    font-weight: 600;
    color: {theme["text"]};
    margin: 30px 0 15px 0;
}}

.author-branch {{
    border-left: 4px solid {theme["line"]};
    margin-left: 20px;
    padding-left: 30px;
}}

.series-row {{
    display: flex;
    align-items: center;
    margin: 18px 0;
}}

.series-branch {{
    width: 45px;
    height: 2px;
    background: {theme["line"]};
    margin-right: 15px;
}}

.series-name {{
    font-family: 'Playfair Display', Georgia, serif;
    font-size: 21px;
    font-weight: 600;
}}

.series-count {{
    color: {theme["muted"]};
    font-size: 13px;
    margin-left: 10px;
}}

.book-row {{
    display: flex;
    align-items: center;
    margin: 8px 0 8px 58px;
    position: relative;
}}

.book-row::before {{
    content: "";
    position: absolute;
    left: -35px;
    top: 0;
    bottom: 0;
    width: 2px;
    background: {theme["line"]};
}}

.book-dot {{
    width: 10px;
    height: 10px;
    border-radius: 50%;
    background: {theme["accent2"]};
    margin-right: 14px;
    flex-shrink: 0;
}}

.book-title {{
    font-family: 'Playfair Display', Georgia, serif;
    font-size: 17px;
    font-weight: 600;
}}

.book-author {{
    color: {theme["muted"]};
    font-size: 13px;
}}

.book-read {{
    color: {theme["accent"]};
    font-size: 12px;
    margin-left: 8px;
}}

.cover-card {{
    text-align: center;
    padding: 10px;
}}

.cover-card img {{
    width: 145px;
    height: 215px;
    object-fit: cover;
    border-radius: 5px;
    box-shadow: 0 8px 20px rgba(0,0,0,.18);
}}

.cover-placeholder {{
    width: 145px;
    height: 215px;
    border-radius: 5px;
    background: {theme["book"]};
    display: flex;
    align-items: center;
    justify-content: center;
    padding: 15px;
    text-align: center;
    font-family: 'Playfair Display', Georgia, serif;
    font-size: 15px;
    box-shadow: 0 8px 20px rgba(0,0,0,.12);
}}

.book-name {{
    font-family: 'Playfair Display', Georgia, serif;
    font-weight: 600;
    margin-top: 9px;
}}

.book-meta {{
    color: {theme["muted"]};
    font-size: 13px;
}}

div[data-testid="stTabs"] button {{
    font-family: 'DM Sans', sans-serif;
    font-weight: 600;
}}

button {{
    border-radius: 9px !important;
}}

div[data-baseweb="input"],
div[data-baseweb="select"] {{
    border-radius: 9px;
}}

</style>
""",
    unsafe_allow_html=True
)

# ============================================================
# COVER LOOKUP
# ============================================================

@st.cache_data(show_spinner=False)
def find_cover(title, author="", isbn=""):

    title = str(title).strip()
    author = str(author).strip()
    isbn = re.sub(r"\D", "", str(isbn))

    # Open Library ISBN
    if isbn:
        url = f"https://covers.openlibrary.org/b/isbn/{isbn}-L.jpg"

        try:
            r = requests.get(
                url,
                timeout=8,
                allow_redirects=True
            )

            if r.status_code == 200 and len(r.content) > 1000:
                return url

        except:
            pass

    # Open Library search
    try:

        params = {
            "title": title,
            "author": author,
            "limit": 1
        }

        r = requests.get(
            "https://openlibrary.org/search.json",
            params=params,
            timeout=10
        )

        if r.status_code == 200:

            docs = r.json().get("docs", [])

            if docs:

                covers = docs[0].get("cover_i")

                if covers:
                    return (
                        f"https://covers.openlibrary.org/"
                        f"b/id/{covers}-L.jpg"
                    )

    except:
        pass

    # Google Books
    try:

        query = f"{title} {author}"

        r = requests.get(
            "https://www.googleapis.com/books/v1/volumes",
            params={
                "q": query,
                "maxResults": 1
            },
            timeout=10
        )

        if r.status_code == 200:

            items = r.json().get("items", [])

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

    except:
        pass

    return ""

# ============================================================
# SERIES DETECTION
# ============================================================

def detect_series(title):

    title = str(title)

    patterns = [
        r"\(([^()]*)#\s*(\d+(?:\.\d+)?)",
        r"\[([^\[\]]*)#\s*(\d+(?:\.\d+)?)",
        r"\(([^()]*)\bBook\s+(\d+(?:\.\d+)?)",
        r"\[([^\[\]]*)\bBook\s+(\d+(?:\.\d+)?)"
    ]

    for pattern in patterns:

        match = re.search(
            pattern,
            title,
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

            series = series.strip(" ,-:")

            if series:
                return series

    return "Standalone"


def detect_number(title):

    patterns = [
        r"#\s*(\d+(?:\.\d+)?)",
        r"\bBook\s+(\d+(?:\.\d+)?)",
        r"\bVol(?:ume)?\.?\s+(\d+(?:\.\d+)?)"
    ]

    for pattern in patterns:

        match = re.search(
            pattern,
            str(title),
            re.IGNORECASE
        )

        if match:

            try:
                return float(match.group(1))
            except:
                pass

    return None

# ============================================================
# IMPORT CSV
# ============================================================

def import_csv(uploaded_file):

    try:

        data = pd.read_csv(
            uploaded_file,
            encoding="utf-8",
            low_memory=False
        )

    except:

        data = pd.read_csv(
            uploaded_file,
            encoding="latin-1",
            low_memory=False
        )

    columns = {
        str(c).strip().lower(): c
        for c in data.columns
    }

    def col(*names):

        for name in names:

            key = name.lower()

            if key in columns:
                return columns[key]

        for name in names:

            for key, original in columns.items():

                if name.lower() in key:
                    return original

        return None

    title_col = col(
        "Title",
        "Book Title"
    )

    author_col = col(
        "Author",
        "Authors"
    )

    if not title_col:
        st.error("I couldn't find a book title column.")
        return

    if not author_col:
        data["Author"] = "Unknown Author"
        author_col = "Author"

    books = []

    for _, row in data.iterrows():

        title = str(
            row.get(title_col, "")
        ).strip()

        if not title or title == "nan":
            continue

        author = str(
            row.get(author_col, "")
        ).strip()

        isbn_col = col(
            "ISBN13",
            "ISBN"
        )

        isbn = ""

        if isbn_col:
            isbn = re.sub(
                r"\D",
                "",
                str(row.get(isbn_col, ""))
            )

        rating_col = col(
            "My Rating",
            "Rating"
        )

        rating = None

        if rating_col:

            try:
                rating = float(
                    row.get(
                        rating_col,
                        0
                    )
                )

            except:
                rating = None

        status = "Want to Read"

        shelf_col = col(
            "Exclusive Shelf",
            "Shelf",
            "Status"
        )

        if shelf_col:

            shelf = str(
                row.get(
                    shelf_col,
                    ""
                )
            ).lower()

            if "currently" in shelf:
                status = "Currently Reading"

            elif "read" in shelf and "to-read" not in shelf:
                status = "Read"

        books.append({
            "Title": title,
            "Author": author,
            "Series": detect_series(title),
            "Series Number": detect_number(title),
            "ISBN": isbn,
            "My Rating": rating,
            "Status": status,
            "Favorite": False,
            "Date Read": "",
            "Publisher": "",
            "Pages": "",
            "Description": "",
            "Cover": ""
        })

    if not books:
        st.error("No books were found in that file.")
        return

    new_df = pd.DataFrame(books)

    # Fill covers
    progress = st.progress(0)

    for i in range(len(new_df)):

        new_df.loc[i, "Cover"] = find_cover(
            new_df.loc[i, "Title"],
            new_df.loc[i, "Author"],
            new_df.loc[i, "ISBN"]
        )

        progress.progress(
            int(
                ((i + 1) / len(new_df)) * 100
            )
        )

    progress.empty()

    st.session_state.library = new_df

    st.success(
        f"Imported {len(new_df):,} books."
    )

# ============================================================
# HEADER
# ============================================================

st.markdown(
    """
    <div class="hero">
        <div class="hero-title">My Book Tree</div>
        <div class="hero-subtitle">
            Your books, connected.
        </div>
    </div>
    """,
    unsafe_allow_html=True
)

# ============================================================
# THEME PICKER
# ============================================================

theme_choice = st.selectbox(
    "Color scheme",
    list(THEMES.keys()),
    index=list(THEMES.keys()).index(
        st.session_state.theme
    )
)

if theme_choice != st.session_state.theme:

    st.session_state.theme = theme_choice

    st.rerun()

# ============================================================
# STATS
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

favorite_count = (
    len(
        library[
            library["Favorite"] == True
        ]
    )
    if total
    else 0
)

c1, c2, c3, c4, c5 = st.columns(5)

with c1:
    st.markdown(
        f"""
        <div class="stat">
            <div class="stat-number">{total:,}</div>
            <div class="stat-label">Books</div>
        </div>
        """,
        unsafe_allow_html=True
    )

with c2:
    st.markdown(
        f"""
        <div class="stat">
            <div class="stat-number">{authors:,}</div>
            <div class="stat-label">Authors</div>
        </div>
        """,
        unsafe_allow_html=True
    )

with c3:
    st.markdown(
        f"""
        <div class="stat">
            <div class="stat-number">{series_count:,}</div>
            <div class="stat-label">Series</div>
        </div>
        """,
        unsafe_allow_html=True
    )

with c4:
    st.markdown(
        f"""
        <div class="stat">
            <div class="stat-number">{read_count:,}</div>
            <div class="stat-label">Read</div>
        </div>
        """,
        unsafe_allow_html=True
    )

with c5:
    st.markdown(
        f"""
        <div class="stat">
            <div class="stat-number">{favorite_count:,}</div>
            <div class="stat-label">Favorites</div>
        </div>
        """,
        unsafe_allow_html=True
    )

# ============================================================
# TABS
# ============================================================

tab_tree, tab_books, tab_add, tab_import = st.tabs(
    [
        "🌿 My Tree",
        "📚 Books",
        "➕ Add a Book",
        "📥 Import"
    ]
)

# ============================================================
# TREE
# ============================================================

with tab_tree:

    st.markdown(
        '<div class="section-title">Your Book Tree</div>',
        unsafe_allow_html=True
    )

    if library.empty:

        st.info(
            "Import a book list or add your first book "
            "to grow your tree."
        )

    else:

        col1, col2, col3 = st.columns(3)

        with col1:

            search = st.text_input(
                "Search",
                placeholder="Book, author, or series..."
            )

        with col2:

            statuses = [
                "All",
                "Read",
                "Currently Reading",
                "Want to Read"
            ]

            selected_status = st.selectbox(
                "Reading status",
                statuses
            )

        with col3:

            selected_author = st.selectbox(
                "Author",
                ["All"] +
                sorted(
                    library["Author"]
                    .dropna()
                    .unique()
                    .tolist()
                )
            )

        data = library.copy()

        if search:

            q = search.lower()

            data = data[
                data["Title"]
                .fillna("")
                .str.lower()
                .str.contains(q)
                |
                data["Author"]
                .fillna("")
                .str.lower()
                .str.contains(q)
                |
                data["Series"]
                .fillna("")
                .str.lower()
                .str.contains(q)
            ]

        if selected_status != "All":

            data = data[
                data["Status"]
                == selected_status
            ]

        if selected_author != "All":

            data = data[
                data["Author"]
                == selected_author
            ]

        st.markdown(
            '<div class="tree-area">',
            unsafe_allow_html=True
        )

        for author_name in sorted(
            data["Author"].dropna().unique(),
            key=lambda x: x.lower()
        ):

            author_books = data[
                data["Author"]
                == author_name
            ]

            st.markdown(
                f"""
                <div class="author-title">
                    {html.escape(author_name)}
                </div>
                <div class="author-branch">
                """,
                unsafe_allow_html=True
            )

            series_names = sorted(
                author_books["Series"]
                .dropna()
                .unique(),
                key=lambda x: x.lower()
            )

            for series_name in series_names:

                series_books = author_books[
                    author_books["Series"]
                    == series_name
                ].copy()

                read = len(
                    series_books[
                        series_books["Status"]
                        == "Read"
                    ]
                )

                total_series = len(series_books)

                st.markdown(
                    f"""
                    <div class="series-row">
                        <div class="series-branch"></div>
                        <div class="series-name">
                            {html.escape(series_name)}
                        </div>
                        <div class="series-count">
                            {read}/{total_series} read
                        </div>
                    </div>
                    """,
                    unsafe_allow_html=True
                )

                series_books = series_books.sort_values(
                    by=[
                        "Series Number",
                        "Title"
                    ],
                    na_position="last"
                )

                for _, book in series_books.iterrows():

                    title = html.escape(
                        str(book["Title"])
                    )

                    status = str(
                        book["Status"]
                    )

                    if status == "Read":
                        icon = "✓"
                    elif status == "Currently Reading":
                        icon = "📖"
                    else:
                        icon = "○"

                    favorite = ""

                    if bool(
                        book.get(
                            "Favorite",
                            False
                        )
                    ):
                        favorite = " ♥"

                    st.markdown(
                        f"""
                        <div class="book-row">
                            <div class="book-dot"></div>
                            <div>
                                <span class="book-title">
                                    {title}
                                </span>
                                <span class="book-read">
                                    {icon}{favorite}
                                </span>
                            </div>
                        </div>
                        """,
                        unsafe_allow_html=True
                    )

            st.markdown(
                "</div>",
                unsafe_allow_html=True
            )

        st.markdown(
            "</div>",
            unsafe_allow_html=True
        )

# ============================================================
# BOOKS / COVERS
# ============================================================

with tab_books:

    st.markdown(
        '<div class="section-title">Your Books</div>',
        unsafe_allow_html=True
    )

    if library.empty:

        st.info(
            "Your books will appear here."
        )

    else:

        filter_choice = st.radio(
            "Show",
            [
                "All Books",
                "Favorites",
                "Read",
                "Currently Reading",
                "Want to Read"
            ],
            horizontal=True
        )

        books = library.copy()

        if filter_choice == "Favorites":

            books = books[
                books["Favorite"] == True
            ]

        elif filter_choice != "All Books":

            books = books[
                books["Status"]
                == filter_choice
            ]

        if books.empty:

            st.info(
                "Nothing here yet."
            )

        else:

            cols = st.columns(6)

            for i, (_, book) in enumerate(
                books.iterrows()
            ):

                with cols[i % 6]:

                    cover = book.get(
                        "Cover",
                        ""
                    )

                    if cover:

                        st.markdown(
                            f"""
                            <div class="cover-card">
                                <img src="{html.escape(cover)}">
                                <div class="book-name">
                                    {html.escape(str(book["Title"]))}
                                </div>
                                <div class="book-meta">
                                    {html.escape(str(book["Author"]))}
                                </div>
                            </div>
                            """,
                            unsafe_allow_html=True
                        )

                    else:

                        st.markdown(
                            f"""
                            <div class="cover-card">
                                <div class="cover-placeholder">
                                    {html.escape(str(book["Title"]))}
                                </div>
                                <div class="book-name">
                                    {html.escape(str(book["Title"]))}
                                </div>
                                <div class="book-meta">
                                    {html.escape(str(book["Author"]))}
                                </div>
                            </div>
                            """,
                            unsafe_allow_html=True
                        )

# ============================================================
# ADD BOOK
# ============================================================

with tab_add:

    st.markdown(
        '<div class="section-title">Add a Book</div>',
        unsafe_allow_html=True
    )

    st.write(
        "Add books individually without importing a file."
    )

    with st.form("add_book_form"):

        title = st.text_input(
            "Book title"
        )

        author = st.text_input(
            "Author"
        )

        series = st.text_input(
            "Series",
            placeholder="Leave blank if standalone"
        )

        series_number = st.text_input(
            "Series number"
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

        rating = st.select_slider(
            "Your rating",
            options=[
                0,
                1,
                2,
                3,
                4,
                5
            ],
            value=0
        )

        favorite = st.checkbox(
            "❤️ Favorite"
        )

        submitted = st.form_submit_button(
            "Add Book"
        )

        if submitted:

            if not title or not author:

                st.error(
                    "Please enter both a title and author."
                )

            else:

                if not series:
                    series = "Standalone"

                cover = find_cover(
                    title,
                    author,
                    isbn
                )

                new_book = {
                    "Title": title,
                    "Author": author,
                    "Series": series,
                    "Series Number": (
                        float(series_number)
                        if series_number
                        else None
                    ),
                    "ISBN": re.sub(
                        r"\D",
                        "",
                        isbn
                    ),
                    "My Rating": (
                        rating
                        if rating > 0
                        else None
                    ),
                    "Status": status,
                    "Favorite": favorite,
                    "Date Read": "",
                    "Publisher": "",
                    "Pages": "",
                    "Description": "",
                    "Cover": cover
                }

                st.session_state.library = pd.concat(
                    [
                        st.session_state.library,
                        pd.DataFrame([new_book])
                    ],
                    ignore_index=True
                )

                st.success(
                    f'"{title}" was added to your library.'
                )

                st.rerun()

# ============================================================
# IMPORT
# ============================================================

with tab_import:

    st.markdown(
        '<div class="section-title">Import Your Library</div>',
        unsafe_allow_html=True
    )

    st.write(
        "Upload a CSV from Goodreads, StoryGraph, "
        "LibraryThing, or another book service."
    )

    uploaded = st.file_uploader(
        "Choose a CSV file",
        type=["csv"]
    )

    if uploaded:

        if st.button(
            "Import Books"
        ):

            import_csv(uploaded)

            st.rerun()

# ============================================================
# FOOTER
# ============================================================

st.markdown(
    f"""
    <div style="
        margin-top:60px;
        padding-top:25px;
        border-top:1px solid {theme["line"]};
        color:{theme["muted"]};
        text-align:center;
        font-size:13px;
    ">
        My Book Tree · Your books, connected.
    </div>
    """,
    unsafe_allow_html=True
)
