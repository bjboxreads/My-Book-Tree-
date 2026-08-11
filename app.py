import streamlit as st
import pandas as pd
import re
import html
import requests
from urllib.parse import quote_plus

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

if "favorites" not in st.session_state:
    st.session_state.favorites = set()

# ============================================================
# THEMES
# ============================================================

THEMES = {
    "Gothic Library": {
        "bg": "#100B10",
        "surface": "#21151E",
        "surface2": "#30202B",
        "card": "#291A25",
        "text": "#F7EBDD",
        "muted": "#D4BEC8",
        "accent": "#D6AE62",
        "accent2": "#B45E78",
        "green": "#71866A",
        "line": "#785466",
        "decor": "✦  ❦  ✧  ❧  ✦",
        "font": "Cormorant Garamond",
        "mood": "gothic"
    },

    "Victorian Rose": {
        "bg": "#160B10",
        "surface": "#2A151E",
        "surface2": "#3A1E2A",
        "card": "#301923",
        "text": "#F9E8E4",
        "muted": "#D9BCBF",
        "accent": "#D8B16A",
        "accent2": "#C66C85",
        "green": "#74836A",
        "line": "#895568",
        "decor": "❀  ❦  ❀  ❧  ❀",
        "font": "Cormorant Garamond",
        "mood": "rose"
    },

    "Emerald Reading Room": {
        "bg": "#09110D",
        "surface": "#142219",
        "surface2": "#203428",
        "card": "#19291F",
        "text": "#F4E9D3",
        "muted": "#C6C7B6",
        "accent": "#D4AF62",
        "accent2": "#9C7280",
        "green": "#7E9D70",
        "line": "#55705A",
        "decor": "❧  ♣  ❦  ♣  ❧",
        "font": "Libre Baskerville",
        "mood": "emerald"
    },

    "Midnight Bookshelf": {
        "bg": "#090D17",
        "surface": "#141B2A",
        "surface2": "#202B40",
        "card": "#182235",
        "text": "#F4EBD8",
        "muted": "#C1C8D4",
        "accent": "#D6B66B",
        "accent2": "#A87593",
        "green": "#6F8B7C",
        "line": "#52647C",
        "decor": "☾  ✦  ⋆  ✧  ☽",
        "font": "Cormorant Garamond",
        "mood": "midnight"
    },

    "Dark Academia": {
        "bg": "#15110C",
        "surface": "#261F15",
        "surface2": "#382C1C",
        "card": "#2C2318",
        "text": "#F2E3C8",
        "muted": "#CCB99B",
        "accent": "#CDA55D",
        "accent2": "#9A6860",
        "green": "#727A5B",
        "line": "#786346",
        "decor": "❦  ✒  ❧  ✒  ❦",
        "font": "Libre Baskerville",
        "mood": "academia"
    },

    "Poison Garden": {
        "bg": "#09100A",
        "surface": "#152017",
        "surface2": "#263125",
        "card": "#1B291D",
        "text": "#F1E5D0",
        "muted": "#C3C7B4",
        "accent": "#D2AE61",
        "accent2": "#A96C91",
        "green": "#7D9C67",
        "line": "#526B4B",
        "decor": "❧  ✿  ☙  ✿  ❧",
        "font": "Cormorant Garamond",
        "mood": "garden"
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

:root {{
    --bg: {T["bg"]};
    --surface: {T["surface"]};
    --surface2: {T["surface2"]};
    --card: {T["card"]};
    --text: {T["text"]};
    --muted: {T["muted"]};
    --gold: {T["accent"]};
    --rose: {T["accent2"]};
    --green: {T["green"]};
    --line: {T["line"]};
}}

.stApp {{
    background:
        radial-gradient(
            ellipse at top,
            var(--surface2) 0%,
            var(--bg) 55%,
            var(--bg) 100%
        );
    color: var(--text);
}}

.block-container {{
    max-width: 1500px;
    padding: 25px 45px 90px;
}}

h1, h2, h3, h4 {{
    font-family: "Cormorant Garamond", Georgia, serif !important;
}}

p, label {{
    font-family: "Libre Baskerville", Georgia, serif;
}}

/* ============================================================
   HEADER
   ============================================================ */

.book-header {{
    text-align: center;
    position: relative;
    padding: 8px 0 0;
}}

.book-header h1 {{
    font-family: "Cormorant Garamond", Georgia, serif !important;
    font-size: 78px !important;
    line-height: .9 !important;
    font-weight: 600 !important;
    letter-spacing: 2px;
    color: var(--text) !important;
    margin: 0 !important;
    text-shadow: 0 5px 22px rgba(0,0,0,.55);
}}

.header-decoration {{
    margin: 10px auto 22px;
    color: var(--gold);
    font-family: "Cormorant Garamond", Georgia, serif;
    font-size: 27px;
    letter-spacing: 9px;
    white-space: nowrap;
    overflow: hidden;
    max-width: 100%;
}}

.header-decoration::before,
.header-decoration::after {{
    content: "";
    display: inline-block;
    width: 30%;
    vertical-align: middle;
    border-top: 1px solid var(--line);
    margin: 0 18px;
}}

/* ============================================================
   THEME
   ============================================================ */

.theme-title {{
    text-align: center;
    font-family: "Cormorant Garamond", Georgia, serif;
    font-size: 22px;
    color: var(--gold);
    margin-bottom: 5px;
}}

div[data-baseweb="select"] > div {{
    background: #171717 !important;
    border: 1px solid var(--gold) !important;
    border-radius: 7px !important;
}}

div[data-baseweb="select"] span {{
    color: #FFFFFF !important;
}}

div[role="listbox"] {{
    background: #171717 !important;
    border: 1px solid var(--gold) !important;
}}

div[role="option"] {{
    background: #171717 !important;
    color: #FFFFFF !important;
}}

div[role="option"] span {{
    color: #FFFFFF !important;
}}

div[role="option"]:hover {{
    background: #3B2A31 !important;
}}

/* ============================================================
   STATS
   ============================================================ */

.stats {{
    display: flex;
    justify-content: center;
    gap: 65px;
    margin: 35px 0 38px;
    flex-wrap: wrap;
}}

.stat {{
    text-align: center;
    min-width: 85px;
}}

.stat-number {{
    display: block;
    font-family: "Cormorant Garamond", Georgia, serif;
    font-size: 43px;
    line-height: 1;
    color: var(--gold);
}}

.stat-label {{
    display: block;
    margin-top: 6px;
    color: var(--muted);
    font-family: "Libre Baskerville", Georgia, serif;
    font-size: 9px;
    letter-spacing: 2px;
    text-transform: uppercase;
}}

/* ============================================================
   FILTERS
   ============================================================ */

.filter-heading {{
    color: var(--gold);
    font-family: "Cormorant Garamond", Georgia, serif;
    font-size: 19px;
}}

div[data-baseweb="input"] > div {{
    background: var(--surface) !important;
    border: 1px solid var(--line) !important;
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

/* ============================================================
   TREE TITLE
   ============================================================ */

.tree-heading {{
    text-align: center;
    margin: 35px 0 30px;
}}

.tree-heading h2 {{
    font-family: "Cormorant Garamond", Georgia, serif !important;
    font-size: 50px !important;
    color: var(--text) !important;
    margin-bottom: 2px !important;
}}

.tree-heading p {{
    color: var(--muted);
    font-family: "Cormorant Garamond", Georgia, serif;
    font-size: 19px;
    font-style: italic;
}}

/* ============================================================
   REAL FAMILY TREE
   ============================================================ */

.family-tree {{
    width: 100%;
    overflow-x: auto;
    padding: 20px 10px 50px;
}}

.tree-root {{
    display: flex;
    justify-content: center;
    margin-bottom: 35px;
    position: relative;
}}

.root-card {{
    position: relative;
    display: inline-block;
    padding: 13px 34px;
    background: var(--surface);
    border: 1px solid var(--gold);
    color: var(--gold);
    font-family: "Cormorant Garamond", Georgia, serif;
    font-size: 29px;
    letter-spacing: 1px;
    box-shadow: 0 10px 30px rgba(0,0,0,.3);
}}

.root-card::after {{
    content: "";
    position: absolute;
    width: 1px;
    height: 35px;
    background: var(--line);
    bottom: -36px;
    left: 50%;
}}

/* Author row */

.author-tree {{
    display: flex;
    justify-content: center;
    align-items: flex-start;
    gap: 45px;
    position: relative;
    padding-top: 38px;
}}

.author-tree::before {{
    content: "";
    position: absolute;
    top: 0;
    left: 8%;
    right: 8%;
    height: 1px;
    background: var(--line);
}}

.author-node {{
    position: relative;
    min-width: 190px;
    max-width: 280px;
    text-align: center;
}}

.author-node::before {{
    content: "";
    position: absolute;
    top: -38px;
    left: 50%;
    height: 38px;
    width: 1px;
    background: var(--line);
}}

.author-card {{
    display: inline-block;
    padding: 15px 20px;
    background: var(--surface);
    border: 1px solid var(--gold);
    color: var(--text);
    font-family: "Cormorant Garamond", Georgia, serif;
    font-size: 25px;
    font-weight: 600;
    box-shadow: 0 8px 22px rgba(0,0,0,.25);
}}

.author-count {{
    display: block;
    margin-top: 5px;
    font-family: "Libre Baskerville", Georgia, serif;
    font-size: 8px;
    text-transform: uppercase;
    letter-spacing: 1.5px;
    color: var(--muted);
}}

/* Expanded author */

.author-children {{
    position: relative;
    margin-top: 38px;
    padding-top: 35px;
}}

.author-children::before {{
    content: "";
    position: absolute;
    top: 0;
    left: 50%;
    height: 35px;
    width: 1px;
    background: var(--line);
}}

.series-row {{
    display: flex;
    justify-content: center;
    align-items: flex-start;
    gap: 28px;
    position: relative;
    padding-top: 30px;
}}

.series-row::before {{
    content: "";
    position: absolute;
    top: 0;
    left: 10%;
    right: 10%;
    height: 1px;
    background: var(--line);
}}

.series-node {{
    position: relative;
    min-width: 170px;
    max-width: 230px;
    text-align: center;
}}

.series-node::before {{
    content: "";
    position: absolute;
    top: -30px;
    left: 50%;
    height: 30px;
    width: 1px;
    background: var(--line);
}}

.series-card {{
    display: inline-block;
    padding: 11px 16px;
    background: var(--card);
    border: 1px solid var(--line);
    color: var(--gold);
    font-family: "Cormorant Garamond", Georgia, serif;
    font-size: 21px;
    box-shadow: 0 6px 18px rgba(0,0,0,.2);
}}

.book-branch {{
    margin-top: 25px;
    position: relative;
    padding-top: 27px;
}}

.book-branch::before {{
    content: "";
    position: absolute;
    top: 0;
    left: 50%;
    height: 27px;
    width: 1px;
    background: var(--line);
}}

.book-list {{
    display: flex;
    flex-direction: column;
    gap: 9px;
    min-width: 190px;
}}

.book-card {{
    display: flex;
    align-items: center;
    gap: 11px;
    text-align: left;
    padding: 9px 11px;
    background: var(--card);
    border-left: 2px solid var(--accent2);
    box-shadow: 0 5px 14px rgba(0,0,0,.2);
}}

.cover {{
    width: 42px;
    height: 62px;
    object-fit: cover;
    flex-shrink: 0;
    border: 1px solid var(--gold);
}}

.no-cover {{
    width: 42px;
    height: 62px;
    flex-shrink: 0;
    display: flex;
    justify-content: center;
    align-items: center;
    background: var(--surface2);
    color: var(--gold);
    border: 1px solid var(--line);
    font-size: 19px;
}}

.book-info {{
    min-width: 0;
}}

.book-title {{
    color: var(--text);
    font-family: "Cormorant Garamond", Georgia, serif;
    font-size: 20px;
    line-height: 1.05;
}}

.book-meta {{
    color: var(--muted);
    font-family: "Libre Baskerville", Georgia, serif;
    font-size: 8px;
    margin-top: 5px;
    line-height: 1.5;
}}

.heart {{
    color: var(--rose);
    font-size: 15px;
}}

/* ============================================================
   EMPTY / IMPORT
   ============================================================ */

.empty {{
    text-align: center;
    padding: 75px 20px;
}}

.empty h2 {{
    font-family: "Cormorant Garamond", Georgia, serif !important;
    font-size: 50px !important;
    color: var(--text) !important;
}}

.empty p {{
    color: var(--muted);
    font-family: "Libre Baskerville", Georgia, serif;
}}

.import-box {{
    max-width: 750px;
    margin: 30px auto;
    padding: 35px;
    background: var(--surface);
    border: 1px solid var(--line);
    text-align: center;
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
    try:
        if pd.isna(value):
            return ""
    except Exception:
        pass
    return str(value).strip()


def find_column(columns, names):
    lookup = {
        str(column).strip().lower(): column
        for column in columns
    }

    for name in names:
        if name.lower() in lookup:
            return lookup[name.lower()]

    return None


def series_from_title(title):
    title = clean(title)

    patterns = [
        r"\(([^()]*)\s*#\s*(\d+(?:\.\d+)?)\)",
        r"\(([^()]*)\s+book\s+(\d+(?:\.\d+)?)\)",
        r"\[([^\[\]]*)\s*#\s*(\d+(?:\.\d+)?)\]",
        r"\[([^\[\]]*)\s+book\s+(\d+(?:\.\d+)?)\]",
    ]

    for pattern in patterns:
        match = re.search(
            pattern,
            title,
            flags=re.IGNORECASE
        )

        if match:
            return (
                clean(match.group(1)),
                float(match.group(2))
            )

    return "Standalone", None


def book_id(row):
    return (
        clean(row["Title"])
        + "||"
        + clean(row["Author"])
        + "||"
        + clean(row["ISBN"])
    )


def stars(value):
    try:
        rating = int(float(value))
        if rating > 0:
            return "★" * min(rating, 5)
    except Exception:
        pass
    return ""


def cover_url(title, author, isbn):
    isbn = re.sub(
        r"[^0-9Xx]",
        "",
        clean(isbn)
    )

    try:

        if isbn:
            url = (
                "https://covers.openlibrary.org/"
                f"b/isbn/{isbn}-M.jpg"
            )

            response = requests.get(
                url,
                timeout=5
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
                "limit": 1
            },
            timeout=5
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


def import_goodreads(raw):
    title_col = find_column(
        raw.columns,
        ["Title"]
    )

    author_col = find_column(
        raw.columns,
        ["Author", "Authors"]
    )

    isbn_col = find_column(
        raw.columns,
        ["ISBN13", "ISBN"]
    )

    rating_col = find_column(
        raw.columns,
        ["My Rating", "Rating"]
    )

    shelf_col = find_column(
        raw.columns,
        ["Exclusive Shelf", "Shelf"]
    )

    read_date_col = find_column(
        raw.columns,
        ["Date Read"]
    )

    added_date_col = find_column(
        raw.columns,
        ["Date Added"]
    )

    genre_col = find_column(
        raw.columns,
        ["Genre", "Genres"]
    )

    year_col = find_column(
        raw.columns,
        [
            "Original Publication Year",
            "Original Publication Date"
        ]
    )

    if title_col is None:
        raise ValueError(
            "I couldn't find the Goodreads Title column."
        )

    rows = []

    for _, row in raw.iterrows():

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

        try:
            rating = float(
                row.get(rating_col)
            ) if rating_col else 0
        except Exception:
            rating = 0

        shelf = (
            clean(row.get(shelf_col)).lower()
            if shelf_col
            else ""
        )

        if shelf == "read":
            status = "Read"
        elif "currently" in shelf:
            status = "Currently Reading"
        elif "want" in shelf:
            status = "Want to Read"
        else:
            status = "Want to Read"

        date_value = ""

        if read_date_col:
            date_value = clean(
                row.get(read_date_col)
            )

        if not date_value and added_date_col:
            date_value = clean(
                row.get(added_date_col)
            )

        if not date_value and year_col:
            date_value = clean(
                row.get(year_col)
            )

        genre = "Uncategorized"

        if genre_col:
            possible_genre = clean(
                row.get(genre_col)
            )

            if possible_genre:
                genre = possible_genre

        series, number = series_from_title(
            title
        )

        rows.append(
            {
                "Title": title,
                "Author": author or "Unknown Author",
                "Series": series,
                "Series Number": number,
                "ISBN": isbn,
                "Rating": rating,
                "Status": status,
                "Genre": genre,
                "Date": date_value,
            }
        )

    result = pd.DataFrame(rows)

    if not result.empty:
        result["DateSort"] = pd.to_datetime(
            result["Date"],
            errors="coerce"
        )

    return result


def book_html(row):
    title = clean(row["Title"])
    author = clean(row["Author"])
    isbn = clean(row["ISBN"])
    status = clean(row["Status"])
    genre = clean(row["Genre"])

    rating = stars(row["Rating"])

    number = ""

    try:
        if pd.notna(row["Series Number"]):
            number_value = float(
                row["Series Number"]
            )

            if number_value.is_integer():
                number = f"{int(number_value)}. "
            else:
                number = f"{number_value}. "
    except Exception:
        pass

    favorite = (
        book_id(row)
        in st.session_state.favorites
    )

    heart = "♥" if favorite else ""

    image = cover_url(
        title,
        author,
        isbn
    )

    if image:

        cover = (
            f'<img class="cover" '
            f'src="{html.escape(image)}">'
        )

    else:

        cover = (
            '<div class="no-cover">✦</div>'
        )

    metadata = (
        html.escape(status)
        + " · "
        + html.escape(genre)
    )

    if rating:
        metadata += (
            " · "
            + html.escape(rating)
        )

    return f"""
<div class="book-card">
    {cover}
    <div class="book-info">
        <div class="book-title">
            {html.escape(number + title)}
            <span class="heart">{heart}</span>
        </div>
        <div class="book-meta">
            {metadata}
        </div>
    </div>
</div>
"""


def make_tree(data):
    if data.empty:
        return """
<div class="empty">
    <h2>No branches found.</h2>
    <p>Try changing your search or filters.</p>
</div>
"""

    authors = []

    grouped_authors = data.groupby(
        "Author",
        sort=True
    )

    for author, author_books in grouped_authors:

        author = clean(author)

        series_html = []

        grouped_series = author_books.groupby(
            "Series",
            sort=True
        )

        for series, series_books in grouped_series:

            series = clean(series)

            series_books = series_books.copy()

            series_books["_num"] = pd.to_numeric(
                series_books["Series Number"],
                errors="coerce"
            )

            series_books = series_books.sort_values(
                ["_num", "Title"],
                na_position="last"
            )

            books = "".join(
                book_html(row)
                for _, row in series_books.iterrows()
            )

            count = len(series_books)

            if series == "Standalone":

                series_title = "Standalone Books"

            else:

                series_title = series

            series_html.append(
                f"""
<details class="series-details">
    <summary>
        <span class="series-card">
            {html.escape(series_title)}
            <small>{count} book{"s" if count != 1 else ""}</small>
        </span>
    </summary>

    <div class="book-branch">
        <div class="book-list">
            {books}
        </div>
    </div>
</details>
"""
            )

        author_count = len(author_books)

        authors.append(
            f"""
<details class="author-details">
    <summary>
        <span class="author-card">
            {html.escape(author)}
            <span class="author-count">
                {author_count} book{"s" if author_count != 1 else ""}
            </span>
        </span>
    </summary>

    <div class="author-children">
        <div class="series-row">
            {"".join(series_html)}
        </div>
    </div>
</details>
"""
        )

    return f"""
<div class="family-tree">

    <div class="tree-root">
        <div class="root-card">
            My Book Tree
        </div>
    </div>

    <div class="author-tree">
        {"".join(authors)}
    </div>

</div>
"""


# ============================================================
# HEADER
# ============================================================

st.markdown(
    f"""
<div class="book-header">
    <h1>My Book Tree</h1>
</div>

<div class="header-decoration">
    {T["decor"]}
</div>
""",
    unsafe_allow_html=True
)

# ============================================================
# THEME SELECTOR
# ============================================================

st.markdown(
    '<div class="theme-title">Choose Your Library Theme</div>',
    unsafe_allow_html=True
)

theme = st.selectbox(
    "Theme",
    list(THEMES.keys()),
    index=list(THEMES.keys()).index(
        st.session_state.theme
    ),
    label_visibility="collapsed"
)

if theme != st.session_state.theme:
    st.session_state.theme = theme
    st.rerun()

# ============================================================
# DATA
# ============================================================

books = st.session_state.books

book_count = len(books)

author_count = (
    books["Author"].nunique()
    if not books.empty
    else 0
)

series_count = (
    books.loc[
        books["Series"] != "Standalone",
        "Series"
    ].nunique()
    if not books.empty
    else 0
)

read_count = (
    int(
        (
            books["Status"]
            == "Read"
        ).sum()
    )
    if not books.empty
    else 0
)

favorite_count = len(
    st.session_state.favorites
)

st.markdown(
    f"""
<div class="stats">

    <div class="stat">
        <span class="stat-number">{book_count}</span>
        <span class="stat-label">Books</span>
    </div>

    <div class="stat">
        <span class="stat-number">{author_count}</span>
        <span class="stat-label">Authors</span>
    </div>

    <div class="stat">
        <span class="stat-number">{series_count}</span>
        <span class="stat-label">Series</span>
    </div>

    <div class="stat">
        <span class="stat-number">{read_count}</span>
        <span class="stat-label">Read</span>
    </div>

    <div class="stat">
        <span class="stat-number">{favorite_count}</span>
        <span class="stat-label">Favorites</span>
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
        "🌿 My Book Tree",
        "📚 Import Library"
    ]
)

# ============================================================
# TREE TAB
# ============================================================

with tree_tab:

    if books.empty:

        st.markdown(
            """
<div class="empty">
    <h2>Your tree is waiting to grow.</h2>
    <p>Go to Import Library and upload your Goodreads CSV.</p>
</div>
""",
            unsafe_allow_html=True
        )

    else:

        # ----------------------------------------------------
        # SEARCH CATEGORY
        # ----------------------------------------------------

        search_type_col, search_col = st.columns(
            [1, 3]
        )

        with search_type_col:

            search_type = st.selectbox(
                "Search by",
                [
                    "All",
                    "Author",
                    "Genre",
                    "Book Title",
                    "ISBN",
                    "Series",
                ],
                label_visibility="collapsed"
            )

        with search_col:

            search_text = st.text_input(
                "Search",
                placeholder="Search your library...",
                label_visibility="collapsed"
            )

        # ----------------------------------------------------
        # SECONDARY FILTERS
        # ----------------------------------------------------

        status_col, genre_col, sort_col = st.columns(
            [1, 1, 1]
        )

        with status_col:

            status_filter = st.selectbox(
                "Reading Status",
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

            genres = sorted(
                books["Genre"]
                .fillna("Uncategorized")
                .astype(str)
                .unique(),
                key=lambda x: x.lower()
            )

            genre_filter = st.selectbox(
                "Genre",
                ["All Genres"] + genres,
                label_visibility="collapsed"
            )

        with sort_col:

            sort_filter = st.selectbox(
                "Sort",
                [
                    "Author A–Z",
                    "Author Z–A",
                    "Book Title A–Z",
                    "Book Title Z–A",
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

        if search_text:

            q = search_text.lower().strip()

            if search_type == "Author":

                filtered = filtered[
                    filtered["Author"]
                    .astype(str)
                    .str.lower()
                    .str.contains(
                        q,
                        na=False,
                        regex=False
                    )
                ]

            elif search_type == "Genre":

                filtered = filtered[
                    filtered["Genre"]
                    .astype(str)
                    .str.lower()
                    .str.contains(
                        q,
                        na=False,
                        regex=False
                    )
                ]

            elif search_type == "Book Title":

                filtered = filtered[
                    filtered["Title"]
                    .astype(str)
                    .str.lower()
                    .str.contains(
                        q,
                        na=False,
                        regex=False
                    )
                ]

            elif search_type == "ISBN":

                filtered = filtered[
                    filtered["ISBN"]
                    .astype(str)
                    .str.contains(
                        search_text.strip(),
                        na=False,
                        regex=False
                    )
                ]

            elif search_type == "Series":

                filtered = filtered[
                    filtered["Series"]
                    .astype(str)
                    .str.lower()
                    .str.contains(
                        q,
                        na=False,
                        regex=False
                    )
                ]

            else:

                mask = (
                    filtered["Author"]
                    .astype(str)
                    .str.lower()
                    .str.contains(
                        q,
                        na=False,
                        regex=False
                    )
                    |
                    filtered["Genre"]
                    .astype(str)
                    .str.lower()
                    .str.contains(
                        q,
                        na=False,
                        regex=False
                    )
                    |
                    filtered["Title"]
                    .astype(str)
                    .str.lower()
                    .str.contains(
                        q,
                        na=False,
                        regex=False
                    )
                    |
                    filtered["Series"]
                    .astype(str)
                    .str.lower()
                    .str.contains(
                        q,
                        na=False,
                        regex=False
                    )
                    |
                    filtered["ISBN"]
                    .astype(str)
                    .str.contains(
                        search_text.strip(),
                        na=False,
                        regex=False
                    )
                )

                filtered = filtered[mask]

        # ----------------------------------------------------
        # STATUS
        # ----------------------------------------------------

        if status_filter == "Favorites":

            filtered = filtered[
                filtered.apply(
                    lambda row:
                    book_id(row)
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

        elif sort_filter == "Book Title A–Z":

            filtered = filtered.sort_values(
                "Title",
                key=lambda x:
                x.astype(str).str.lower()
            )

        elif sort_filter == "Book Title Z–A":

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
        # TREE
        # ----------------------------------------------------

        st.markdown(
            """
<div class="tree-heading">
    <h2>My Book Tree</h2>
    <p>Authors branch into series, and series branch into books.</p>
</div>
""",
            unsafe_allow_html=True
        )

        st.markdown(
            make_tree(filtered),
            unsafe_allow_html=True
        )

# ============================================================
# IMPORT TAB
# ============================================================

with import_tab:

    st.markdown(
        """
<div class="tree-heading">
    <h2>Grow Your Book Tree</h2>
    <p>Bring your Goodreads library into your tree.</p>
</div>
""",
        unsafe_allow_html=True
    )

    uploaded = st.file_uploader(
        "Goodreads CSV",
        type=["csv"],
        label_visibility="collapsed"
    )

    if uploaded:

        if st.button(
            "🌿 Import My Goodreads Library",
            type="primary"
        ):

            try:

                with st.spinner(
                    "Growing your book tree..."
                ):

                    raw = pd.read_csv(
                        uploaded,
                        low_memory=False
                    )

                    imported = import_goodreads(
                        raw
                    )

                if imported.empty:

                    st.error(
                        "I found the CSV, but I couldn't find any books in it."
                    )

                else:

                    st.session_state.books = imported

                    st.success(
                        f"Your tree now has {len(imported):,} books."
                    )

                    st.rerun()

            except Exception as error:

                st.error(
                    "Something went wrong while reading the Goodreads file."
                )

                st.exception(error)

    if not books.empty:

        st.markdown(
            f"""
<div class="import-box">
    <h3>Your current library</h3>
    <p>{len(books):,} books · {books["Author"].nunique():,} authors</p>
</div>
""",
            unsafe_allow_html=True
        )

        if st.button(
            "Clear My Book Tree"
        ):

            st.session_state.books = pd.DataFrame()
            st.session_state.favorites = set()

            st.rerun()
