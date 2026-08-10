import streamlit as st
import pandas as pd
import requests
import re
import json
from pathlib import Path
from urllib.parse import quote

# ============================================================
# MY BOOK TREE
# ============================================================

st.set_page_config(
    page_title="My Book Tree",
    page_icon="🌳",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ============================================================
# COLORS / THEMES
# ============================================================

THEMES = {
    "Midnight Garden": {
        "bg": "#101820",
        "panel": "#17252F",
        "panel2": "#203541",
        "accent": "#7FB8A4",
        "accent2": "#B8D8C8",
        "text": "#E8F1EC",
        "muted": "#9DB3AA",
        "line": "#38535B",
        "branch": "#6E9F8D"
    },

    "Emerald & Gold": {
        "bg": "#101B16",
        "panel": "#17271F",
        "panel2": "#21382C",
        "accent": "#76B98B",
        "accent2": "#D7B76A",
        "text": "#F0EEE3",
        "muted": "#A7B6AA",
        "line": "#3D5A49",
        "branch": "#83A96F"
    },

    "Blueberry Night": {
        "bg": "#101827",
        "panel": "#182338",
        "panel2": "#22304A",
        "accent": "#789BCB",
        "accent2": "#B8C8E8",
        "text": "#EEF3FA",
        "muted": "#9DAEC7",
        "line": "#3B4F70",
        "branch": "#718DB8"
    },

    "Forest": {
        "bg": "#101A14",
        "panel": "#18271D",
        "panel2": "#233A29",
        "accent": "#79A96B",
        "accent2": "#B8C98C",
        "text": "#EEF4E9",
        "muted": "#A5B39D",
        "line": "#405A43",
        "branch": "#719663"
    },

    "Black & Teal": {
        "bg": "#0D1517",
        "panel": "#132326",
        "panel2": "#1B3235",
        "accent": "#56B8B1",
        "accent2": "#9DDED9",
        "text": "#EAF5F4",
        "muted": "#98B4B3",
        "line": "#34565A",
        "branch": "#4F9693"
    }
}

# ============================================================
# SESSION STATE
# ============================================================

if "books" not in st.session_state:
    st.session_state.books = pd.DataFrame(columns=[
        "Title",
        "Author",
        "Series",
        "Series Number",
        "Status",
        "Favorite",
        "ISBN",
        "Rating",
        "Description",
        "Cover"
    ])

if "theme" not in st.session_state:
    st.session_state.theme = "Midnight Garden"

if "loaded" not in st.session_state:
    st.session_state.loaded = False

theme = THEMES[st.session_state.theme]

# ============================================================
# CSS
# ============================================================

st.markdown(
    f"""
<style>

.stApp {{
    background:
        radial-gradient(
            circle at 15% 0%,
            {theme["panel2"]} 0%,
            {theme["bg"]} 45%
        );
    color: {theme["text"]};
}}

.main {{
    background: transparent;
}}

h1, h2, h3 {{
    color: {theme["text"]} !important;
}}

p, label, span {{
    color: {theme["text"]};
}}

.book-title {{
    font-size: 18px;
    font-weight: 700;
    color: {theme["text"]};
}}

.author-name {{
    font-size: 14px;
    color: {theme["accent2"]};
}}

.series-name {{
    font-size: 13px;
    color: {theme["muted"]};
}}

.tree-root {{
    margin: 15px 0;
    padding: 18px;
    border: 1px solid {theme["line"]};
    border-radius: 18px;
    background: {theme["panel"]};
}}

.author-node {{
    font-size: 24px;
    font-weight: 700;
    color: {theme["accent2"]};
    margin-bottom: 10px;
}}

.series-node {{
    margin-left: 25px;
    padding: 12px 18px;
    border-left: 3px solid {theme["branch"]};
    margin-top: 8px;
    background: {theme["panel2"]};
    border-radius: 0 12px 12px 0;
}}

.book-node {{
    margin-left: 48px;
    padding: 8px 14px;
    border-left: 2px solid {theme["line"]};
    color: {theme["text"]};
}}

.book-node:hover {{
    background: {theme["panel2"]};
}}

.stat {{
    background: {theme["panel"]};
    border: 1px solid {theme["line"]};
    border-radius: 14px;
    padding: 15px;
    text-align: center;
}}

.stat-number {{
    font-size: 28px;
    font-weight: bold;
    color: {theme["accent"]};
}}

.stat-label {{
    font-size: 13px;
    color: {theme["muted"]};
}}

div[data-testid="stSidebar"] {{
    background: {theme["panel"]};
}}

.stButton > button {{
    border-radius: 10px;
    border: 1px solid {theme["line"]};
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
    for wanted in names:
        for col in df.columns:
            if str(col).strip().lower() == wanted.lower():
                return col

    for wanted in names:
        for col in df.columns:
            if wanted.lower() in str(col).lower():
                return col

    return None


def detect_series(title):
    title = clean_text(title)

    patterns = [
        r"\(([^()]*)#\s*\d+(?:\.\d+)?[^()]*\)",
        r"\[([^\[\]]*)#\s*\d+(?:\.\d+)?[^\[\]]*\]",
        r"\(([^()]*)\bBook\s+\d+(?:\.\d+)?[^()]*\)",
        r"\[([^\[\]]*)\bBook\s+\d+(?:\.\d+)?[^\[\]]*\]"
    ]

    for pattern in patterns:
        match = re.search(
            pattern,
            title,
            flags=re.IGNORECASE
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
            except:
                pass

    return None


def normalize_book_dataframe(df):
    title_col = find_column(df, ["Title"])
    author_col = find_column(df, ["Author"])

    if title_col is None or author_col is None:
        raise ValueError(
            "The file needs columns named Title and Author."
        )

    isbn_col = find_column(df, ["ISBN13", "ISBN"])
    rating_col = find_column(df, ["My Rating", "Rating"])
    shelf_col = find_column(df, ["Exclusive Shelf", "Shelf"])
    series_col = find_column(df, ["Series"])

    result = pd.DataFrame()

    result["Title"] = df[title_col].apply(clean_text)
    result["Author"] = df[author_col].apply(clean_text)

    if series_col:
        result["Series"] = df[series_col].apply(clean_text)
        result["Series"] = result["Series"].replace(
            "",
            pd.NA
        )
        result["Series"] = result["Series"].fillna(
            result["Title"].apply(detect_series)
        )
    else:
        result["Series"] = result["Title"].apply(
            detect_series
        )

    result["Series Number"] = result["Title"].apply(
        detect_series_number
    )

    if isbn_col:
        result["ISBN"] = (
            df[isbn_col]
            .fillna("")
            .astype(str)
            .str.replace(r"\D", "", regex=True)
        )
    else:
        result["ISBN"] = ""

    if rating_col:
        result["Rating"] = pd.to_numeric(
            df[rating_col],
            errors="coerce"
        )
    else:
        result["Rating"] = None

    if shelf_col:
        shelves = (
            df[shelf_col]
            .fillna("")
            .astype(str)
            .str.lower()
        )

        def status_from_shelf(value):
            if "currently-reading" in value:
                return "Currently Reading"

            if "read" in value and "to-read" not in value:
                return "Read"

            return "Want to Read"

        result["Status"] = shelves.apply(
            status_from_shelf
        )

    else:
        result["Status"] = "Want to Read"

    result["Favorite"] = False
    result["Description"] = ""
    result["Cover"] = ""

    result = result[
        result["Title"].str.strip() != ""
    ].copy()

    return result


# ============================================================
# COVER SEARCH
# ============================================================

@st.cache_data(show_spinner=False)
def find_cover(title, author, isbn):
    isbn = clean_text(isbn)

    # Open Library ISBN lookup
    if isbn:
        url = (
            "https://covers.openlibrary.org/b/isbn/"
            + isbn
            + "-L.jpg"
        )

        try:
            response = requests.get(
                url,
                timeout=5
            )

            if response.status_code == 200:
                if len(response.content) > 1000:
                    return url
        except:
            pass

    # Open Library search
    query = quote(
        f"{title} {author}"
    )

    try:
        response = requests.get(
            f"https://openlibrary.org/search.json?q={query}&limit=1",
            timeout=8
        )

        if response.status_code == 200:
            data = response.json()

            docs = data.get("docs", [])

            if docs:
                cover_id = docs[0].get(
                    "cover_i"
                )

                if cover_id:
                    return (
                        "https://covers.openlibrary.org/b/id/"
                        + str(cover_id)
                        + "-L.jpg"
                    )

    except:
        pass

    return ""


def fill_missing_covers(df):
    df = df.copy()

    for index, row in df.iterrows():

        if not clean_text(row.get("Cover", "")):

            cover = find_cover(
                row["Title"],
                row["Author"],
                row["ISBN"]
            )

            df.at[index, "Cover"] = cover

    return df


# ============================================================
# IMPORT CSV
# ============================================================

def import_csv(uploaded_file):

    df = pd.read_csv(
        uploaded_file,
        encoding="utf-8",
        low_memory=False
    )

    books = normalize_book_dataframe(df)

    books = fill_missing_covers(books)

    st.session_state.books = books
    st.session_state.loaded = True


# ============================================================
# SIDEBAR
# ============================================================

with st.sidebar:

    st.markdown(
        "## 🌳 My Book Tree"
    )

    st.markdown(
        "Your personal visual book library."
    )

    st.divider()

    st.markdown("### 🎨 Choose Your Colors")

    selected_theme = st.selectbox(
        "Color scheme",
        list(THEMES.keys()),
        index=list(THEMES.keys()).index(
            st.session_state.theme
        )
    )

    if selected_theme != st.session_state.theme:
        st.session_state.theme = selected_theme
        st.rerun()

    st.divider()

    st.markdown("### 📥 Import Books")

    uploaded_file = st.file_uploader(
        "Upload a CSV book list",
        type=["csv"]
    )

    if uploaded_file is not None:

        if st.button(
            "Import This List",
            use_container_width=True
        ):

            try:
                import_csv(uploaded_file)

                st.success(
                    "Books imported!"
                )

                st.rerun()

            except Exception as e:

                st.error(
                    f"Could not import file: {e}"
                )

    st.divider()

    st.markdown("### 📊 Library")

    total = len(
        st.session_state.books
    )

    read = len(
        st.session_state.books[
            st.session_state.books["Status"]
            == "Read"
        ]
    )

    reading = len(
        st.session_state.books[
            st.session_state.books["Status"]
            == "Currently Reading"
        ]
    )

    want = len(
        st.session_state.books[
            st.session_state.books["Status"]
            == "Want to Read"
        ]
    )

    favorites = len(
        st.session_state.books[
            st.session_state.books["Favorite"]
            == True
        ]
    )

    st.write(f"📚 {total} books")
    st.write(f"✓ {read} read")
    st.write(f"📖 {reading} reading")
    st.write(f"○ {want} want to read")
    st.write(f"❤️ {favorites} favorites")


# ============================================================
# HEADER
# ============================================================

st.markdown(
    """
# 🌳 MY BOOK TREE

### Your books. Your branches. Your library.

Organize your books by **author → series → book**.
"""
)

# ============================================================
# STATS
# ============================================================

books = st.session_state.books

if len(books) > 0:

    cols = st.columns(5)

    stats = [
        ("📚", len(books), "Books"),
        ("✦", books["Author"].nunique(), "Authors"),
        ("📖", len(
            books[
                books["Status"]
                == "Read"
            ]
        ), "Read"),
        ("○", len(
            books[
                books["Status"]
                == "Want to Read"
            ]
        ), "Want to Read"),
        ("❤️", len(
            books[
                books["Favorite"]
                == True
            ]
        ), "Favorites")
    ]

    for col, stat in zip(
        cols,
        stats
    ):

        with col:

            st.markdown(
                f"""
                <div class="stat">
                    <div class="stat-number">
                        {stat[0]} {stat[1]}
                    </div>
                    <div class="stat-label">
                        {stat[2]}
                    </div>
                </div>
                """,
                unsafe_allow_html=True
            )

else:

    st.info(
        "Upload a Goodreads CSV from the sidebar "
        "to build your library."
    )

# ============================================================
# TABS
# ============================================================

tab_tree, tab_books, tab_add, tab_favorites, tab_reading = st.tabs(
    [
        "🌳 Book Tree",
        "📚 All Books",
        "➕ Add Book",
        "❤️ Favorites",
        "📖 Reading"
    ]
)

# ============================================================
# TREE
# ============================================================

with tab_tree:

    st.markdown(
        "## 🌳 Your Book Tree"
    )

    if books.empty:

        st.info(
            "Upload your book list to grow your tree."
        )

    else:

        search = st.text_input(
            "🔎 Search your tree",
            placeholder="Book, author, or series..."
        )

        filtered = books.copy()

        if search:

            search_lower = search.lower()

            filtered = filtered[
                filtered["Title"]
                .str.lower()
                .str.contains(
                    search_lower,
                    na=False
                )
                |
                filtered["Author"]
                .str.lower()
                .str.contains(
                    search_lower,
                    na=False
                )
                |
                filtered["Series"]
                .str.lower()
                .str.contains(
                    search_lower,
                    na=False
                )
            ]

        authors = sorted(
            filtered["Author"]
            .dropna()
            .unique(),
            key=lambda x: x.lower()
        )

        for author in authors:

            author_books = filtered[
                filtered["Author"]
                == author
            ]

            st.markdown(
                f"""
                <div class="tree-root">
                    <div class="author-node">
                        🌿 {author}
                    </div>
                """,
                unsafe_allow_html=True
            )

            series_names = sorted(
                author_books["Series"]
                .fillna("Standalone")
                .unique(),
                key=lambda x: x.lower()
            )

            for series in series_names:

                series_books = author_books[
                    author_books["Series"]
                    == series
                ].copy()

                if series == "Standalone":

                    label = "📕 Standalone Books"

                else:

                    read_count = len(
                        series_books[
                            series_books["Status"]
                            == "Read"
                        ]
                    )

                    label = (
                        f"📚 {series} "
                        f"({read_count}/{len(series_books)} read)"
                    )

                with st.expander(
                    label,
                    expanded=False
                ):

                    series_books = series_books.sort_values(
                        by=[
                            "Series Number",
                            "Title"
                        ],
                        na_position="last"
                    )

                    for _, book in series_books.iterrows():

                        favorite = (
                            " ❤️"
                            if book["Favorite"]
                            else ""
                        )

                        status_icon = {
                            "Read": "✓",
                            "Currently Reading": "📖",
                            "Want to Read": "○"
                        }.get(
                            book["Status"],
                            "○"
                        )

                        number = ""

                        if pd.notna(
                            book["Series Number"]
                        ):
                            number = (
                                f"{book['Series Number']:g}. "
                            )

                        st.markdown(
                            f"""
                            <div class="book-node">
                                {status_icon}
                                <strong>
                                    {number}{book['Title']}
                                </strong>
                                {favorite}
                            </div>
                            """,
                            unsafe_allow_html=True
                        )

            st.markdown(
                "</div>",
                unsafe_allow_html=True
            )

# ============================================================
# ALL BOOKS
# ============================================================

with tab_books:

    st.markdown(
        "## 📚 All Books"
    )

    if books.empty:

        st.info(
            "Your library is empty."
        )

    else:

        search = st.text_input(
            "Search books",
            key="all_books_search"
        )

        status_filter = st.selectbox(
            "Reading status",
            [
                "All",
                "Read",
                "Currently Reading",
                "Want to Read"
            ]
        )

        data = books.copy()

        if search:

            search_lower = search.lower()

            data = data[
                data["Title"]
                .str.lower()
                .str.contains(
                    search_lower,
                    na=False
                )
                |
                data["Author"]
                .str.lower()
                .str.contains(
                    search_lower,
                    na=False
                )
            ]

        if status_filter != "All":

            data = data[
                data["Status"]
                == status_filter
            ]

        data = data.sort_values(
            by=[
                "Author",
                "Series",
                "Series Number",
                "Title"
            ],
            na_position="last"
        )

        st.write(
            f"Showing **{len(data)} books**"
        )

        st.dataframe(
            data[
                [
                    "Title",
                    "Author",
                    "Series",
                    "Status",
                    "Favorite",
                    "Rating"
                ]
            ],
            use_container_width=True,
            hide_index=True
        )

# ============================================================
# ADD BOOK
# ============================================================

with tab_add:

    st.markdown(
        "## ➕ Add a Book"
    )

    st.write(
        "Add a book manually without importing another list."
    )

    with st.form("add_book_form"):

        title = st.text_input(
            "Book title *"
        )

        author = st.text_input(
            "Author *"
        )

        series = st.text_input(
            "Series",
            placeholder="Leave blank for standalone"
        )

        series_number = st.text_input(
            "Series number",
            placeholder="Example: 1 or 2.5"
        )

        status_value = st.selectbox(
            "Reading status",
            [
                "Want to Read",
                "Currently Reading",
                "Read"
            ]
        )

        favorite_value = st.checkbox(
            "❤️ Add to Favorites"
        )

        isbn = st.text_input(
            "ISBN",
            placeholder="Optional"
        )

        rating = st.number_input(
            "Your rating",
            min_value=0,
            max_value=5,
            value=0
        )

        submitted = st.form_submit_button(
            "🌱 Add Book",
            use_container_width=True
        )

        if submitted:

            if not title or not author:

                st.error(
                    "Please enter a title and author."
                )

            else:

                if not series:
                    series = "Standalone"

                try:
                    number = (
                        float(series_number)
                        if series_number
                        else None
                    )
                except:
                    number = None

                cover = find_cover(
                    title,
                    author,
                    isbn
                )

                new_book = pd.DataFrame(
                    [{
                        "Title": title,
                        "Author": author,
                        "Series": series,
                        "Series Number": number,
                        "Status": status_value,
                        "Favorite": favorite_value,
                        "ISBN": isbn,
                        "Rating": rating
                        if rating > 0
                        else None,
                        "Description": "",
                        "Cover": cover
                    }]
                )

                st.session_state.books = pd.concat(
                    [
                        st.session_state.books,
                        new_book
                    ],
                    ignore_index=True
                )

                st.success(
                    f"Added {title}!"
                )

                st.rerun()

# ============================================================
# FAVORITES
# ============================================================

with tab_favorites:

    st.markdown(
        "## ❤️ Favorites"
    )

    favorites = books[
        books["Favorite"] == True
    ]

    if favorites.empty:

        st.info(
            "You haven't added any favorites yet."
        )

    else:

        cols = st.columns(5)

        for index, (_, book) in enumerate(
            favorites.iterrows()
        ):

            with cols[index % 5]:

                cover = book["Cover"]

                if cover:

                    st.image(
                        cover,
                        use_container_width=True
                    )

                st.markdown(
                    f"**{book['Title']}**"
                )

                st.caption(
                    book["Author"]
                )

# ============================================================
# READING
# ============================================================

with tab_reading:

    st.markdown(
        "## 📖 Reading"
    )

    currently = books[
        books["Status"]
        == "Currently Reading"
    ]

    if currently.empty:

        st.info(
            "Nothing is currently marked as reading."
        )

    else:

        for _, book in currently.iterrows():

            col1, col2 = st.columns(
                [1, 4]
            )

            with col1:

                if book["Cover"]:

                    st.image(
                        book["Cover"],
                        width=120
                    )

            with col2:

                st.markdown(
                    f"### {book['Title']}"
                )

                st.write(
                    book["Author"]
                )

                if book["Series"] != "Standalone":

                    st.caption(
                        book["Series"]
                    )

                st.success(
                    "Currently Reading"
                )

# ============================================================
# FOOTER
# ============================================================

st.divider()

st.markdown(
    """
    <div style="
        text-align:center;
        padding:20px;
        color:#888;
    ">
        🌿 My Book Tree
        <br>
        <small>
        Your library, growing one book at a time.
        </small>
    </div>
    """,
    unsafe_allow_html=True
)
