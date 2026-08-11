import streamlit as st
import pandas as pd
import re
import html
import requests
from datetime import datetime

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
# SESSION STATE
# ============================================================

if "theme" not in st.session_state:
    st.session_state.theme = "Gothic Library"

if "books" not in st.session_state:
    st.session_state.books = pd.DataFrame()

if "open_authors" not in st.session_state:
    st.session_state.open_authors = set()

if "open_series" not in st.session_state:
    st.session_state.open_series = set()

if "favorites" not in st.session_state:
    st.session_state.favorites = set()

# ============================================================
# THEMES
# ============================================================

THEMES = {
    "Gothic Library": {
        "bg": "#120D12",
        "panel": "#211720",
        "panel2": "#30202B",
        "text": "#F7EBDD",
        "muted": "#D2BFC6",
        "gold": "#D5AE63",
        "rose": "#B96A86",
        "green": "#6F876C",
        "vine": "#65745B",
        "border": "#735263",
    },

    "Victorian Rose": {
        "bg": "#1A1014",
        "panel": "#2A171F",
        "panel2": "#3A202A",
        "text": "#F8E8E5",
        "muted": "#D8BFC0",
        "gold": "#D8B26A",
        "rose": "#C76F86",
        "green": "#71846A",
        "vine": "#68745E",
        "border": "#865061",
    },

    "Emerald Reading Room": {
        "bg": "#0C1511",
        "panel": "#15251C",
        "panel2": "#203528",
        "text": "#F4E9D4",
        "muted": "#C6C9B5",
        "gold": "#D4AF62",
        "rose": "#A87882",
        "green": "#799B70",
        "vine": "#66815D",
        "border": "#526D58",
    },

    "Midnight Bookshelf": {
        "bg": "#0B101A",
        "panel": "#151E2C",
        "panel2": "#202D40",
        "text": "#F3E9D5",
        "muted": "#BEC9D3",
        "gold": "#D6B56A",
        "rose": "#9F7187",
        "green": "#6F8C7C",
        "vine": "#5F786A",
        "border": "#53677F",
    },

    "Dark Academia": {
        "bg": "#17130E",
        "panel": "#272016",
        "panel2": "#382D1D",
        "text": "#F2E4CB",
        "muted": "#CBBCA0",
        "gold": "#CFA65D",
        "rose": "#986B62",
        "green": "#707C5D",
        "vine": "#647052",
        "border": "#786347",
    },

    "Poison Garden": {
        "bg": "#0D120C",
        "panel": "#182017",
        "panel2": "#273025",
        "text": "#F2E7D1",
        "muted": "#C1C7B5",
        "gold": "#D2AD5E",
        "rose": "#A86F91",
        "green": "#7C9B67",
        "vine": "#668256",
        "border": "#526A4E",
    },
}

if st.session_state.theme not in THEMES:
    st.session_state.theme = "Gothic Library"

T = THEMES[st.session_state.theme]

# ============================================================
# CSS
# ============================================================

st.markdown(
    f"""
<style>

@import url('https://fonts.googleapis.com/css2?family=Cormorant+Garamond:wght@400;500;600;700&family=Libre+Baskerville:wght@400;700&display=swap');

html, body, [class*="css"] {{
    font-family: "Libre Baskerville", Georgia, serif;
}}

.stApp {{
    background:
        radial-gradient(
            circle at 50% -10%,
            {T["panel2"]} 0%,
            {T["bg"]} 55%
        );
    color: {T["text"]};
}}

.block-container {{
    max-width: 1450px;
    padding: 25px 45px 80px;
}}

h1, h2, h3, h4 {{
    font-family: "Cormorant Garamond", Georgia, serif !important;
}}

p, span, label {{
    font-family: "Libre Baskerville", Georgia, serif;
}}

/* ========================================================
   HEADER
   ======================================================== */

.book-header {{
    position: relative;
    text-align: center;
    padding: 15px 0 8px;
}}

.book-header h1 {{
    margin: 0;
    font-family: "Cormorant Garamond", Georgia, serif !important;
    font-size: 72px !important;
    font-weight: 600 !important;
    letter-spacing: 1px;
    color: {T["text"]} !important;
    text-shadow: 0 4px 20px rgba(0,0,0,.45);
}}

.header-vine {{
    width: 100%;
    height: 35px;
    margin: -3px auto 15px;
    color: {T["vine"]};
    text-align: center;
    font-family: "Cormorant Garamond", Georgia, serif;
    font-size: 31px;
    letter-spacing: 7px;
    white-space: nowrap;
    overflow: hidden;
}}

.header-vine span {{
    color: {T["green"]};
}}

.header-vine b {{
    color: {T["gold"]};
    font-weight: 400;
}}

/* ========================================================
   THEME SELECTOR
   ======================================================== */

.theme-heading {{
    text-align: center;
    color: {T["gold"]};
    font-family: "Cormorant Garamond", Georgia, serif;
    font-size: 24px;
    margin-bottom: 8px;
}}

div[data-baseweb="select"] {{
    font-family: "Libre Baskerville", Georgia, serif !important;
}}

div[data-baseweb="select"] > div {{
    background: #171717 !important;
    border: 1px solid {T["gold"]} !important;
    border-radius: 8px !important;
    min-height: 44px !important;
}}

div[data-baseweb="select"] span {{
    color: #FFFFFF !important;
}}

div[role="listbox"] {{
    background: #171717 !important;
    border: 1px solid {T["gold"]} !important;
}}

div[role="option"] {{
    background: #171717 !important;
    color: #FFFFFF !important;
}}

div[role="option"] span {{
    color: #FFFFFF !important;
}}

div[role="option"]:hover {{
    background: #3A2A31 !important;
}}

/* ========================================================
   STATS
   ======================================================== */

.stats {{
    display: flex;
    justify-content: center;
    gap: 70px;
    margin: 35px 0 40px;
}}

.stat {{
    text-align: center;
}}

.stat-number {{
    font-family: "Cormorant Garamond", Georgia, serif;
    font-size: 44px;
    color: {T["gold"]};
    line-height: 1;
}}

.stat-label {{
    margin-top: 5px;
    font-size: 9px;
    letter-spacing: 2px;
    text-transform: uppercase;
    color: {T["muted"]};
}}

/* ========================================================
   FILTER AREA
   ======================================================== */

.filter-label {{
    color: {T["gold"]};
    font-family: "Cormorant Garamond", Georgia, serif;
    font-size: 19px;
    margin-bottom: 5px;
}}

div[data-baseweb="input"] > div {{
    background: {T["panel"]} !important;
    border: 1px solid {T["border"]} !important;
}}

div[data-baseweb="input"] input {{
    color: {T["text"]} !important;
}}

.stTextInput input::placeholder {{
    color: {T["muted"]} !important;
}}

/* ========================================================
   TREE
   ======================================================== */

.tree-title {{
    text-align: center;
    margin: 25px 0 8px;
}}

.tree-title h2 {{
    font-family: "Cormorant Garamond", Georgia, serif !important;
    font-size: 48px !important;
    font-weight: 600 !important;
    color: {T["text"]} !important;
    margin: 0;
}}

.tree-subtitle {{
    text-align: center;
    font-family: "Cormorant Garamond", Georgia, serif;
    font-size: 19px;
    font-style: italic;
    color: {T["muted"]};
    margin-bottom: 35px;
}}

.root-node {{
    text-align: center;
    margin-bottom: 35px;
}}

.root-node span {{
    display: inline-block;
    padding: 8px 30px;
    border-top: 1px solid {T["gold"]};
    border-bottom: 1px solid {T["gold"]};
    font-family: "Cormorant Garamond", Georgia, serif;
    font-size: 28px;
    color: {T["gold"]};
}}

/* ========================================================
   STREAMLIT BUTTONS USED AS TREE NODES
   ======================================================== */

.stButton > button {{
    background: transparent !important;
    border: none !important;
    color: {T["text"]} !important;
    box-shadow: none !important;
    font-family: "Cormorant Garamond", Georgia, serif !important;
    transition: all .15s ease;
}}

.stButton > button:hover {{
    color: {T["gold"]} !important;
    border: none !important;
}}

.author-button > button {{
    font-size: 31px !important;
    font-weight: 600 !important;
    text-align: left !important;
}}

.series-button > button {{
    font-size: 26px !important;
    color: {T["gold"]} !important;
    text-align: left !important;
}}

.book-button > button {{
    font-size: 20px !important;
    text-align: left !important;
}}

/* ========================================================
   TREE BRANCHES
   ======================================================== */

.author-branch {{
    margin: 0 0 20px 35px;
    padding: 0 0 10px 28px;
    border-left: 1px solid {T["vine"]};
}}

.series-branch {{
    margin: 0 0 15px 32px;
    padding-left: 26px;
    border-left: 1px solid {T["border"]};
}}

.book-list {{
    margin-left: 32px;
    padding-left: 25px;
    border-left: 1px solid {T["vine"]};
}}

/* ========================================================
   BOOK CARDS
   ======================================================== */

.book-card {{
    display: flex;
    align-items: center;
    gap: 18px;
    margin: 8px 0;
    padding: 11px 15px;
    background: linear-gradient(
        90deg,
        {T["panel"]},
        rgba(0,0,0,0)
    );
    border-bottom: 1px solid {T["border"]};
    border-radius: 4px;
}}

.book-cover {{
    width: 48px;
    height: 70px;
    object-fit: cover;
    flex-shrink: 0;
    border: 1px solid {T["gold"]};
    box-shadow: 3px 5px 14px rgba(0,0,0,.45);
}}

.no-cover {{
    width: 48px;
    height: 70px;
    flex-shrink: 0;
    display: flex;
    justify-content: center;
    align-items: center;
    background: {T["panel2"]};
    border: 1px solid {T["border"]};
    color: {T["gold"]};
    font-size: 22px;
}}

.book-title {{
    font-family: "Cormorant Garamond", Georgia, serif;
    font-size: 24px;
    color: {T["text"]};
}}

.book-meta {{
    font-size: 10px;
    color: {T["muted"]};
    margin-top: 3px;
}}

.favorite {{
    color: {T["rose"]};
    font-size: 20px;
}}

/* ========================================================
   EMPTY STATE
   ======================================================== */

.empty {{
    text-align: center;
    padding: 70px 20px;
}}

.empty h2 {{
    font-family: "Cormorant Garamond", Georgia, serif !important;
    font-size: 48px !important;
    color: {T["text"]} !important;
}}

.empty p {{
    color: {T["muted"]};
}}

</style>
""",
    unsafe_allow_html=True,
)

# ============================================================
# HELPERS
# ============================================================

def clean(value):
    if value is None:
        return ""

    if pd.isna(value):
        return ""

    return str(value).strip()


def find_column(columns, possible_names):
    lowered = {
        str(c).strip().lower(): c
        for c in columns
    }

    for name in possible_names:
        if name.lower() in lowered:
            return lowered[name.lower()]

    return None


def get_series_info(title):
    title = clean(title)

    patterns = [
        r"\(([^()]*)#\s*(\d+(?:\.\d+)?)\)",
        r"\(([^()]*)book\s*(\d+(?:\.\d+)?)\)",
        r"\[([^\[\]]*)#\s*(\d+(?:\.\d+)?)\]",
        r"\[([^\[\]]*)book\s*(\d+(?:\.\d+)?)\]",
    ]

    for pattern in patterns:

        match = re.search(
            pattern,
            title,
            flags=re.IGNORECASE
        )

        if match:

            series = match.group(1).strip()

            try:
                number = float(match.group(2))
            except Exception:
                number = None

            return series, number

    return "Standalone", None


def normalize_isbn(value):
    return re.sub(
        r"[^0-9Xx]",
        "",
        clean(value)
    )


@st.cache_data(show_spinner=False)
def find_cover(title, author, isbn):

    isbn = normalize_isbn(isbn)

    try:

        if isbn:

            url = (
                "https://covers.openlibrary.org/"
                f"b/isbn/{isbn}-M.jpg"
            )

            response = requests.get(
                url,
                timeout=8
            )

            if (
                response.status_code == 200
                and len(response.content) > 1000
            ):
                return url

        response = requests.get(
            "https://openlibrary.org/search.json",
            params={
                "title": title,
                "author": author,
                "limit": 1,
            },
            timeout=8
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
                        f"b/id/{cover_id}-M.jpg"
                    )

    except Exception:
        pass

    return ""


def convert_goodreads(df):

    title_col = find_column(
        df.columns,
        ["Title"]
    )

    author_col = find_column(
        df.columns,
        ["Author", "Authors"]
    )

    isbn_col = find_column(
        df.columns,
        ["ISBN13", "ISBN"]
    )

    rating_col = find_column(
        df.columns,
        ["My Rating", "Rating"]
    )

    shelf_col = find_column(
        df.columns,
        ["Exclusive Shelf", "Shelf"]
    )

    date_read_col = find_column(
        df.columns,
        ["Date Read"]
    )

    date_added_col = find_column(
        df.columns,
        ["Date Added"]
    )

    year_col = find_column(
        df.columns,
        [
            "Original Publication Year",
            "Original Publication Date"
        ]
    )

    genre_col = find_column(
        df.columns,
        ["Genre", "Genres"]
    )

    if title_col is None:
        raise ValueError(
            "The CSV does not contain a Goodreads 'Title' column."
        )

    rows = []

    for _, row in df.iterrows():

        title = clean(
            row.get(title_col)
        )

        if not title:
            continue

        author = (
            clean(row.get(author_col))
            if author_col
            else "Unknown Author"
        )

        isbn = (
            clean(row.get(isbn_col))
            if isbn_col
            else ""
        )

        # --------------------------------------------
        # Rating
        # --------------------------------------------

        rating = 0

        if rating_col:

            try:

                rating = float(
                    row.get(rating_col)
                )

            except Exception:
                rating = 0

        # --------------------------------------------
        # Goodreads shelf
        # --------------------------------------------

        shelf = ""

        if shelf_col:
            shelf = clean(
                row.get(shelf_col)
            ).lower()

        if shelf == "read":
            status = "Read"

        elif "currently" in shelf:
            status = "Currently Reading"

        elif "want" in shelf:
            status = "Want to Read"

        else:
            status = (
                shelf.title()
                if shelf
                else "Want to Read"
            )

        # --------------------------------------------
        # Date
        # --------------------------------------------

        date_value = ""

        if date_read_col:
            date_value = clean(
                row.get(date_read_col)
            )

        if not date_value and date_added_col:
            date_value = clean(
                row.get(date_added_col)
            )

        if not date_value and year_col:
            date_value = clean(
                row.get(year_col)
            )

        # --------------------------------------------
        # Genre
        # --------------------------------------------

        genre = "Uncategorized"

        if genre_col:

            genre_value = clean(
                row.get(genre_col)
            )

            if genre_value:
                genre = genre_value

        # --------------------------------------------
        # Series
        # --------------------------------------------

        series, series_number = get_series_info(
            title
        )

        rows.append(
            {
                "Title": title,
                "Author": author or "Unknown Author",
                "Series": series,
                "Series Number": series_number,
                "ISBN": isbn,
                "Rating": rating,
                "Status": status,
                "Genre": genre,
                "Date": date_value,
            }
        )

    result = pd.DataFrame(rows)

    if result.empty:
        return result

    result["DateSort"] = pd.to_datetime(
        result["Date"],
        errors="coerce"
    )

    return result


def safe_key(value):
    return re.sub(
        r"[^A-Za-z0-9]+",
        "_",
        str(value)
    ).strip("_")


def make_book_id(book):
    return (
        clean(book["Title"])
        + "||"
        + clean(book["Author"])
        + "||"
        + clean(book["ISBN"])
    )


def stars(rating):

    try:

        value = int(float(rating))

        if value > 0:
            return "★" * value

    except Exception:
        pass

    return ""


def display_book(book):

    title = clean(book["Title"])
    author = clean(book["Author"])
    status = clean(book["Status"])
    genre = clean(book["Genre"])
    rating = stars(book["Rating"])

    number = ""

    try:

        if pd.notna(book["Series Number"]):

            n = float(
                book["Series Number"]
            )

            if n.is_integer():
                number = f"{int(n)}. "
            else:
                number = f"{n}. "

    except Exception:
        pass

    book_id = make_book_id(book)

    is_favorite = (
        book_id
        in st.session_state.favorites
    )

    if is_favorite:
        favorite_symbol = "♥"
    else:
        favorite_symbol = "♡"

    cover = ""

    # Covers are intentionally loaded here rather than
    # during CSV import so a large Goodreads library
    # doesn't fail because one cover lookup times out.

    cover_url = find_cover(
        title,
        author,
        book["ISBN"]
    )

    if cover_url:

        cover = (
            f'<img class="book-cover" '
            f'src="{html.escape(cover_url)}">'
        )

    else:

        cover = (
            '<div class="no-cover">✦</div>'
        )

    col1, col2 = st.columns(
        [0.88, 0.12]
    )

    with col1:

        st.markdown(
            f"""
<div class="book-card">
{cover}
<div>
<div class="book-title">{html.escape(number + title)}</div>
<div class="book-meta">
{html.escape(status)}
 ·
{html.escape(genre)}
{(" · " + html.escape(rating)) if rating else ""}
</div>
</div>
</div>
""",
            unsafe_allow_html=True
        )

    with col2:

        if st.button(
            favorite_symbol,
            key="fav_" + safe_key(book_id),
            help=(
                "Remove from favorites"
                if is_favorite
                else "Add to favorites"
            )
        ):

            if is_favorite:
                st.session_state.favorites.remove(
                    book_id
                )
            else:
                st.session_state.favorites.add(
                    book_id
                )

            st.rerun()


def render_books(book_df):

    if book_df.empty:
        return

    sorted_books = book_df.copy()

    sorted_books["_number"] = pd.to_numeric(
        sorted_books["Series Number"],
        errors="coerce"
    )

    sorted_books = sorted_books.sort_values(
        ["_number", "Title"],
        na_position="last"
    )

    for _, book in sorted_books.iterrows():
        display_book(book)


def render_series(author, series_name, series_books):

    series_key = (
        safe_key(author)
        + "__"
        + safe_key(series_name)
    )

    open_now = (
        series_key
        in st.session_state.open_series
    )

    arrow = "⌄" if open_now else "›"

    st.markdown(
        '<div class="series-branch">',
        unsafe_allow_html=True
    )

    if st.button(
        f"{arrow}  {series_name}   ·   {len(series_books)} books",
        key="series_button_" + series_key
    ):

        if open_now:
            st.session_state.open_series.remove(
                series_key
            )
        else:
            st.session_state.open_series.add(
                series_key
            )

        st.rerun()

    if open_now:

        st.markdown(
            '<div class="book-list">',
            unsafe_allow_html=True
        )

        render_books(series_books)

        st.markdown(
            '</div>',
            unsafe_allow_html=True
        )

    st.markdown(
        '</div>',
        unsafe_allow_html=True
    )


# ============================================================
# HEADER
# ============================================================

st.markdown(
    """
<div class="book-header">
<h1>My Book Tree</h1>
</div>

<div class="header-vine">
<span>❧</span> ── ❧ ── <b>✦</b> ── ❧ ── <span>❧</span>
</div>
""",
    unsafe_allow_html=True
)

# ============================================================
# THEME
# ============================================================

st.markdown(
    '<div class="theme-heading">Choose Your Library</div>',
    unsafe_allow_html=True
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
# STATS
# ============================================================

books = st.session_state.books

total_books = len(books)

total_authors = (
    books["Author"].nunique()
    if not books.empty
    else 0
)

total_series = (
    books.loc[
        books["Series"] != "Standalone",
        "Series"
    ].nunique()
    if not books.empty
    else 0
)

total_read = (
    int(
        (books["Status"] == "Read").sum()
    )
    if not books.empty
    else 0
)

total_favorites = len(
    st.session_state.favorites
)

st.markdown(
    f"""
<div class="stats">
<div class="stat">
<div class="stat-number">{total_books}</div>
<div class="stat-label">Books</div>
</div>

<div class="stat">
<div class="stat-number">{total_authors}</div>
<div class="stat-label">Authors</div>
</div>

<div class="stat">
<div class="stat-number">{total_series}</div>
<div class="stat-label">Series</div>
</div>

<div class="stat">
<div class="stat-number">{total_read}</div>
<div class="stat-label">Read</div>
</div>

<div class="stat">
<div class="stat-number">{total_favorites}</div>
<div class="stat-label">Favorites</div>
</div>
</div>
""",
    unsafe_allow_html=True
)

# ============================================================
# TABS
# ============================================================

tree_tab, import_tab = st.tabs(
    [
        "🌿  My Book Tree",
        "📚  Import Library"
    ]
)

# ============================================================
# TREE
# ============================================================

with tree_tab:

    if books.empty:

        st.markdown(
            """
<div class="empty">
<h2>Your tree is waiting to grow.</h2>
<p>Import your Goodreads library from the Import Library tab.</p>
</div>
""",
            unsafe_allow_html=True
        )

    else:

        # ----------------------------------------------------
        # FILTERS
        # ----------------------------------------------------

        search_col, status_col, genre_col, sort_col = st.columns(
            [2.3, 1.15, 1.2, 1.4]
        )

        with search_col:

            search = st.text_input(
                "Search",
                placeholder="Search by title, author, or series...",
                label_visibility="collapsed"
            )

        with status_col:

            status_filter = st.selectbox(
                "Status",
                [
                    "All Books",
                    "Read",
                    "Currently Reading",
                    "Want to Read",
                    "Favorites",
                ],
                label_visibility="collapsed"
            )

        with genre_col:

            genre_values = sorted(
                books["Genre"]
                .fillna("Uncategorized")
                .astype(str)
                .unique(),
                key=lambda x: x.lower()
            )

            genre_filter = st.selectbox(
                "Genre",
                ["All Genres"] + genre_values,
                label_visibility="collapsed"
            )

        with sort_col:

            sort_filter = st.selectbox(
                "Sort",
                [
                    "Author A–Z",
                    "Author Z–A",
                    "Title A–Z",
                    "Title Z–A",
                    "Newest",
                    "Oldest",
                    "Highest Rated",
                    "Lowest Rated",
                ],
                label_visibility="collapsed"
            )

        filtered = books.copy()

        # ----------------------------------------------------
        # SEARCH
        # ----------------------------------------------------

        if search:

            q = search.lower()

            title_match = (
                filtered["Title"]
                .astype(str)
                .str.lower()
                .str.contains(
                    q,
                    na=False,
                    regex=False
                )
            )

            author_match = (
                filtered["Author"]
                .astype(str)
                .str.lower()
                .str.contains(
                    q,
                    na=False,
                    regex=False
                )
            )

            series_match = (
                filtered["Series"]
                .astype(str)
                .str.lower()
                .str.contains(
                    q,
                    na=False,
                    regex=False
                )
            )

            filtered = filtered[
                title_match
                | author_match
                | series_match
            ]

        # ----------------------------------------------------
        # STATUS
        # ----------------------------------------------------

        if status_filter == "Favorites":

            filtered = filtered[
                filtered.apply(
                    lambda row:
                    make_book_id(row)
                    in st.session_state.favorites,
                    axis=1
                )
            ]

        elif status_filter != "All Books":

            filtered = filtered[
                filtered["Status"]
                == status_filter
            ]

        # ----------------------------------------------------
        # GENRE
        # ----------------------------------------------------

        if genre_filter != "All Genres":

            filtered = filtered[
                filtered["Genre"]
                == genre_filter
            ]

        # ----------------------------------------------------
        # SORT
        # ----------------------------------------------------

        if sort_filter == "Author A–Z":

            filtered = filtered.sort_values(
                "Author",
                key=lambda x:
                x.astype(str).str.lower()
            )

        elif sort_filter == "Author Z–A":

            filtered = filtered.sort_values(
                "Author",
                ascending=False,
                key=lambda x:
                x.astype(str).str.lower()
            )

        elif sort_filter == "Title A–Z":

            filtered = filtered.sort_values(
                "Title",
                key=lambda x:
                x.astype(str).str.lower()
            )

        elif sort_filter == "Title Z–A":

            filtered = filtered.sort_values(
                "Title",
                ascending=False,
                key=lambda x:
                x.astype(str).str.lower()
            )

        elif sort_filter == "Newest":

            filtered = filtered.sort_values(
                "DateSort",
                ascending=False,
                na_position="last"
            )

        elif sort_filter == "Oldest":

            filtered = filtered.sort_values(
                "DateSort",
                ascending=True,
                na_position="last"
            )

        elif sort_filter == "Highest Rated":

            filtered = filtered.sort_values(
                "Rating",
                ascending=False,
                na_position="last"
            )

        elif sort_filter == "Lowest Rated":

            filtered = filtered.sort_values(
                "Rating",
                ascending=True,
                na_position="last"
            )

        # ----------------------------------------------------
        # TREE HEADER
        # ----------------------------------------------------

        st.markdown(
            """
<div class="tree-title">
<h2>Your Library</h2>
</div>

<div class="tree-subtitle">
Author → Series → Book
</div>

<div class="root-node">
<span>My Reading Tree</span>
</div>
""",
            unsafe_allow_html=True
        )

        # ----------------------------------------------------
        # AUTHORS
        # ----------------------------------------------------

        authors = sorted(
            filtered["Author"]
            .fillna("Unknown Author")
            .astype(str)
            .unique(),
            key=lambda x: x.lower()
        )

        for author in authors:

            author_books = filtered[
                filtered["Author"]
                .fillna("Unknown Author")
                .astype(str)
                == author
            ].copy()

            author_key = safe_key(
                author
            )

            author_open = (
                author_key
                in st.session_state.open_authors
            )

            arrow = (
                "⌄"
                if author_open
                else "›"
            )

            st.markdown(
                '<div class="author-branch">',
                unsafe_allow_html=True
            )

            if st.button(
                f"{arrow}  {author}   ·   {len(author_books)} books",
                key="author_button_" + author_key
            ):

                if author_open:

                    st.session_state.open_authors.remove(
                        author_key
                    )

                    # Also close the author's series
                    for key in list(
                        st.session_state.open_series
                    ):

                        if key.startswith(
                            author_key + "__"
                        ):
                            st.session_state.open_series.remove(
                                key
                            )

                else:

                    # Only one author open at a time
                    st.session_state.open_authors = {
                        author_key
                    }

                st.rerun()

            if author_open:

                series_names = sorted(
                    author_books["Series"]
                    .fillna("Standalone")
                    .astype(str)
                    .unique(),
                    key=lambda x: x.lower()
                )

                for series_name in series_names:

                    series_books = author_books[
                        author_books["Series"]
                        .fillna("Standalone")
                        .astype(str)
                        == series_name
                    ].copy()

                    if series_name == "Standalone":

                        standalone_key = (
                            author_key
                            + "__Standalone"
                        )

                        standalone_open = (
                            standalone_key
                            in st.session_state.open_series
                        )

                        arrow = (
                            "⌄"
                            if standalone_open
                            else "›"
                        )

                        st.markdown(
                            '<div class="series-branch">',
                            unsafe_allow_html=True
                        )

                        if st.button(
                            f"{arrow}  Standalone Books   ·   {len(series_books)}",
                            key="standalone_" + author_key
                        ):

                            if standalone_open:

                                st.session_state.open_series.remove(
                                    standalone_key
                                )

                            else:

                                st.session_state.open_series.add(
                                    standalone_key
                                )

                            st.rerun()

                        if standalone_open:

                            st.markdown(
                                '<div class="book-list">',
                                unsafe_allow_html=True
                            )

                            render_books(
                                series_books
                            )

                            st.markdown(
                                '</div>',
                                unsafe_allow_html=True
                            )

                        st.markdown(
                            '</div>',
                            unsafe_allow_html=True
                        )

                    else:

                        render_series(
                            author,
                            series_name,
                            series_books
                        )

            st.markdown(
                '</div>',
                unsafe_allow_html=True
            )

        if filtered.empty:

            st.markdown(
                """
<div class="empty">
<h2>No books found.</h2>
<p>Try changing your search or filters.</p>
</div>
""",
                unsafe_allow_html=True
            )

# ============================================================
# IMPORT
# ============================================================

with import_tab:

    st.markdown(
        """
<div class="tree-title">
<h2>Grow Your Book Tree</h2>
</div>

<div class="tree-subtitle">
Import your Goodreads library
</div>
""",
        unsafe_allow_html=True
    )

    uploaded_file = st.file_uploader(
        "Goodreads CSV",
        type=["csv"],
        help="Upload the CSV exported from Goodreads.",
        label_visibility="collapsed"
    )

    if uploaded_file is not None:

        if st.button(
            "🌿  Import My Books",
            type="primary"
        ):

            try:

                with st.spinner(
                    "Reading your library..."
                ):

                    raw = pd.read_csv(
                        uploaded_file,
                        low_memory=False
                    )

                    imported = convert_goodreads(
                        raw
                    )

                if imported.empty:

                    st.error(
                        "I found the file, but no books could be imported."
                    )

                else:

                    # Preserve existing favorites
                    old_favorites = (
                        st.session_state.favorites
                    )

                    st.session_state.books = (
                        imported
                    )

                    # Remove favorites that no longer exist
                    valid_ids = {
                        make_book_id(row)
                        for _, row
                        in imported.iterrows()
                    }

                    st.session_state.favorites = {
                        book_id
                        for book_id
                        in old_favorites
                        if book_id in valid_ids
                    }

                    st.session_state.open_authors = set()
                    st.session_state.open_series = set()

                    st.success(
                        f"Successfully imported {len(imported):,} books."
                    )

                    st.rerun()

            except Exception as error:

                st.error(
                    "There was a problem reading your Goodreads file."
                )

                st.exception(error)

    # --------------------------------------------------------
    # CURRENT LIBRARY
    # --------------------------------------------------------

    if not books.empty:

        st.markdown(
            f"""
<div class="tree-subtitle">
Your current tree contains {len(books):,} books.
</div>
""",
            unsafe_allow_html=True
        )

        if st.button(
            "Clear Imported Library"
        ):

            st.session_state.books = pd.DataFrame()
            st.session_state.open_authors = set()
            st.session_state.open_series = set()
            st.session_state.favorites = set()

            st.rerun()
