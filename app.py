import streamlit as st
import pandas as pd
import re
import html
import requests

# ============================================================
# PAGE SETUP
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
    "Midnight Garden": {
        "background": "#11131A",
        "surface": "#1B1D27",
        "surface2": "#252836",
        "text": "#F7EBDD",
        "muted": "#C8BDB5",
        "accent": "#D8AD63",
        "accent2": "#A97C9A",
        "branch": "#88705B",
        "leaf": "#78917B",
        "cover_bg": "#302A35",
    },

    "Burgundy Library": {
        "background": "#190C12",
        "surface": "#2A111A",
        "surface2": "#3B1825",
        "text": "#FAEBDD",
        "muted": "#D0B8B5",
        "accent": "#D7A75A",
        "accent2": "#C8788A",
        "branch": "#8E6353",
        "leaf": "#718568",
        "cover_bg": "#351B24",
    },

    "Sapphire Study": {
        "background": "#08131F",
        "surface": "#102337",
        "surface2": "#17324B",
        "text": "#F7EEDC",
        "muted": "#BFCBD5",
        "accent": "#D9B45A",
        "accent2": "#879FCA",
        "branch": "#687A87",
        "leaf": "#688C82",
        "cover_bg": "#1A3045",
    },

    "Poison Garden": {
        "background": "#10150F",
        "surface": "#182218",
        "surface2": "#253124",
        "text": "#F4EAD6",
        "muted": "#C2C9B8",
        "accent": "#D4B35B",
        "accent2": "#A77D9B",
        "branch": "#707B5D",
        "leaf": "#789B68",
        "cover_bg": "#202B20",
    },

    "Gothic Romance": {
        "background": "#140C16",
        "surface": "#211222",
        "surface2": "#321A32",
        "text": "#F8E8E3",
        "muted": "#CEB8C2",
        "accent": "#D5A75A",
        "accent2": "#C36E91",
        "branch": "#80566A",
        "leaf": "#71866C",
        "cover_bg": "#2A182B",
    },

    "Autumn Reading Room": {
        "background": "#17100C",
        "surface": "#281A12",
        "surface2": "#3A2417",
        "text": "#F7E7CF",
        "muted": "#D0BDA5",
        "accent": "#D6A04F",
        "accent2": "#B86F65",
        "branch": "#896342",
        "leaf": "#71825F",
        "cover_bg": "#332015",
    },
}

# ============================================================
# SESSION STATE
# ============================================================

if "theme" not in st.session_state:
    st.session_state.theme = "Midnight Garden"

if st.session_state.theme not in THEMES:
    st.session_state.theme = "Midnight Garden"

if "books" not in st.session_state:
    st.session_state.books = pd.DataFrame()

if "open_authors" not in st.session_state:
    st.session_state.open_authors = set()

if "open_series" not in st.session_state:
    st.session_state.open_series = set()

theme = THEMES[st.session_state.theme]

# ============================================================
# GLOBAL STYLE
# ============================================================

st.markdown(
    f"""
<style>

@import url(
'https://fonts.googleapis.com/css2?family=Cormorant+Garamond:wght@400;500;600;700'
'&family=Libre+Baskerville:wght@400;700'
);

:root {{
    --background: {theme["background"]};
    --surface: {theme["surface"]};
    --surface2: {theme["surface2"]};
    --text: {theme["text"]};
    --muted: {theme["muted"]};
    --accent: {theme["accent"]};
    --accent2: {theme["accent2"]};
    --branch: {theme["branch"]};
    --leaf: {theme["leaf"]};
    --cover-bg: {theme["cover_bg"]};
}}

.stApp {{
    background:
        radial-gradient(
            circle at 50% 0%,
            var(--surface2) 0%,
            var(--background) 48%
        ) !important;
    color: var(--text) !important;
}}

.block-container {{
    max-width: 1450px !important;
    padding: 30px 50px 80px !important;
}}

html, body {{
    background: var(--background) !important;
}}

h1, h2, h3, h4, h5, h6 {{
    font-family: "Cormorant Garamond", Georgia, serif !important;
}}

p, label, span, div {{
    font-family: "Libre Baskerville", Georgia, serif;
}}

/* ----------------------------------------------------------
   HEADER
---------------------------------------------------------- */

.book-title-header {{
    text-align: center;
    margin-top: 20px;
}}

.book-title-header h1 {{
    margin: 0;
    font-family: "Cormorant Garamond", Georgia, serif !important;
    font-size: 68px !important;
    font-weight: 600 !important;
    letter-spacing: .015em;
    color: var(--text) !important;
    line-height: .95;
}}

.book-title-header p {{
    margin-top: 13px;
    font-family: "Libre Baskerville", Georgia, serif;
    font-size: 10px;
    letter-spacing: .24em;
    text-transform: uppercase;
    color: var(--muted);
}}

.header-ornament {{
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 13px;
    margin: 25px auto 35px;
    color: var(--accent);
    font-family: "Cormorant Garamond", serif;
    font-size: 22px;
}}

.header-ornament::before,
.header-ornament::after {{
    content: "";
    width: 105px;
    height: 1px;
    background: var(--accent);
    opacity: .7;
}}

/* ----------------------------------------------------------
   THEME SELECTOR
---------------------------------------------------------- */

.theme-label {{
    text-align: center;
    color: var(--accent);
    font-family: "Cormorant Garamond", Georgia, serif;
    font-size: 22px;
    margin-bottom: 8px;
}}

div[data-baseweb="select"] > div {{
    background: #171717 !important;
    border: 1px solid var(--accent) !important;
    border-radius: 5px !important;
    min-height: 42px !important;
}}

div[data-baseweb="select"] span {{
    color: #FFFFFF !important;
}}

div[role="listbox"] {{
    background: #171717 !important;
    border: 1px solid var(--accent) !important;
}}

div[role="option"] {{
    background: #171717 !important;
    color: #FFFFFF !important;
    font-family: "Libre Baskerville", Georgia, serif !important;
}}

div[role="option"] * {{
    color: #FFFFFF !important;
}}

div[role="option"]:hover {{
    background: #3A3035 !important;
    color: #FFFFFF !important;
}}

/* ----------------------------------------------------------
   STATS
---------------------------------------------------------- */

.stats {{
    display: flex;
    justify-content: center;
    gap: 65px;
    margin: 35px 0 45px;
}}

.stat {{
    text-align: center;
    min-width: 85px;
}}

.stat-number {{
    display: block;
    font-family: "Cormorant Garamond", Georgia, serif;
    font-size: 38px;
    color: var(--accent);
    line-height: 1;
}}

.stat-label {{
    display: block;
    margin-top: 7px;
    font-size: 8px;
    letter-spacing: .16em;
    text-transform: uppercase;
    color: var(--muted);
}}

/* ----------------------------------------------------------
   TOOL BAR
---------------------------------------------------------- */

.toolbar {{
    border-top: 1px solid var(--branch);
    border-bottom: 1px solid var(--branch);
    padding: 18px 0;
    margin-bottom: 40px;
}}

.toolbar-title {{
    text-align: center;
    font-family: "Cormorant Garamond", Georgia, serif;
    font-style: italic;
    font-size: 25px;
    color: var(--accent);
    margin-bottom: 15px;
}}

div[data-baseweb="input"] > div {{
    background: var(--surface) !important;
    border: 1px solid var(--branch) !important;
}}

div[data-baseweb="input"] input {{
    color: var(--text) !important;
}}

div[data-baseweb="select"] {{
    color: var(--text) !important;
}}

/* ----------------------------------------------------------
   TREE ROOT
---------------------------------------------------------- */

.tree-heading {{
    text-align: center;
    margin-bottom: 40px;
}}

.tree-heading h2 {{
    margin: 0;
    font-size: 44px;
    color: var(--text);
}}

.tree-heading p {{
    margin-top: 5px;
    font-family: "Cormorant Garamond", Georgia, serif;
    font-style: italic;
    font-size: 18px;
    color: var(--muted);
}}

.tree-root {{
    text-align: center;
    margin-bottom: 45px;
}}

.tree-root span {{
    display: inline-block;
    font-family: "Cormorant Garamond", Georgia, serif;
    font-size: 27px;
    color: var(--accent);
    padding: 5px 25px 9px;
    border-top: 1px solid var(--accent);
    border-bottom: 1px solid var(--accent);
}}

/* ----------------------------------------------------------
   TREE BRANCHES
---------------------------------------------------------- */

.author-tree {{
    position: relative;
    margin: 0 auto 25px;
    padding-left: 42px;
    max-width: 1150px;
}}

.author-tree::before {{
    content: "";
    position: absolute;
    left: 10px;
    top: 0;
    bottom: 0;
    width: 1px;
    background: var(--branch);
}}

.author-line {{
    position: relative;
    display: flex;
    align-items: center;
    min-height: 48px;
}}

.author-line::before {{
    content: "";
    position: absolute;
    left: -32px;
    width: 32px;
    height: 1px;
    background: var(--branch);
}}

.author-name {{
    font-family: "Cormorant Garamond", Georgia, serif;
    font-size: 31px;
    font-weight: 600;
    color: var(--text);
}}

.author-count {{
    margin-left: 12px;
    font-size: 12px;
    color: var(--muted);
}}

.series-tree {{
    position: relative;
    margin-left: 58px;
    padding-left: 38px;
    margin-top: 4px;
    margin-bottom: 8px;
}}

.series-tree::before {{
    content: "";
    position: absolute;
    left: 7px;
    top: -10px;
    bottom: -10px;
    width: 1px;
    background: var(--branch);
}}

.series-line {{
    position: relative;
    min-height: 43px;
    display: flex;
    align-items: center;
}}

.series-line::before {{
    content: "";
    position: absolute;
    left: -31px;
    width: 31px;
    height: 1px;
    background: var(--branch);
}}

.series-name {{
    font-family: "Cormorant Garamond", Georgia, serif;
    font-size: 25px;
    font-weight: 600;
    color: var(--accent);
}}

.series-count {{
    margin-left: 10px;
    font-size: 11px;
    color: var(--muted);
}}

.book-tree {{
    position: relative;
    margin-left: 62px;
    padding-left: 35px;
}}

.book-tree::before {{
    content: "";
    position: absolute;
    left: 7px;
    top: -8px;
    bottom: -8px;
    width: 1px;
    background: var(--branch);
}}

.book-line {{
    position: relative;
    display: flex;
    align-items: center;
    gap: 14px;
    min-height: 82px;
    padding: 7px 0;
}}

.book-line::before {{
    content: "";
    position: absolute;
    left: -28px;
    width: 28px;
    height: 1px;
    background: var(--branch);
}}

.book-cover {{
    width: 43px;
    height: 64px;
    object-fit: cover;
    border: 1px solid var(--accent);
    box-shadow: 3px 5px 12px rgba(0,0,0,.4);
    flex-shrink: 0;
}}

.book-placeholder {{
    width: 43px;
    height: 64px;
    flex-shrink: 0;
    display: flex;
    align-items: center;
    justify-content: center;
    background: var(--cover-bg);
    border: 1px solid var(--branch);
    color: var(--accent);
    font-size: 18px;
}}

.book-text {{
    min-width: 0;
}}

.book-name {{
    font-family: "Cormorant Garamond", Georgia, serif;
    font-size: 21px;
    font-weight: 600;
    color: var(--text);
}}

.book-meta {{
    margin-top: 2px;
    font-size: 11px;
    color: var(--muted);
}}

.status-read {{
    color: var(--leaf);
}}

.status-current {{
    color: var(--accent);
}}

.status-want {{
    color: var(--accent2);
}}

.stButton > button {{
    background: transparent !important;
    border: none !important;
    color: var(--text) !important;
    box-shadow: none !important;
    font-family: "Cormorant Garamond", Georgia, serif !important;
    font-size: 22px !important;
    padding: 0 !important;
}}

.stButton > button:hover {{
    color: var(--accent) !important;
    border: none !important;
    background: transparent !important;
}}

/* ----------------------------------------------------------
   EMPTY STATE
---------------------------------------------------------- */

.empty {{
    text-align: center;
    padding: 70px 20px;
}}

.empty-title {{
    font-family: "Cormorant Garamond", Georgia, serif;
    font-size: 45px;
    color: var(--text);
}}

.empty-text {{
    margin-top: 10px;
    color: var(--muted);
    font-family: "Libre Baskerville", Georgia, serif;
    font-size: 14px;
}}

/* ----------------------------------------------------------
   LOADING VINE
---------------------------------------------------------- */

.loading-screen {{
    position: fixed;
    inset: 0;
    z-index: 999999;
    background: var(--background);
    display: flex;
    align-items: center;
    justify-content: center;
}}

.loading-inner {{
    width: 90%;
    text-align: center;
}}

.loading-title {{
    font-family: "Cormorant Garamond", Georgia, serif;
    font-style: italic;
    font-size: 43px;
    color: var(--text);
    margin-bottom: 30px;
}}

.vine {{
    position: relative;
    height: 110px;
    width: 100%;
}}

.vine-stem {{
    position: absolute;
    top: 54px;
    left: 2%;
    width: 96%;
    height: 3px;
    background: var(--branch);
    transform-origin: left center;
    animation: growvine 2.3s ease-out forwards;
}}

@keyframes growvine {{
    from {{ transform: scaleX(0); }}
    to {{ transform: scaleX(1); }}
}}

.vine-leaf {{
    position: absolute;
    width: 21px;
    height: 34px;
    background: var(--leaf);
    border-radius: 100% 0 100% 0;
    opacity: 0;
    animation: appearleaf .35s ease-out forwards;
}}

.leaf1 {{
    left: 12%;
    top: 29px;
    transform: rotate(-40deg);
    animation-delay: .5s;
}}

.leaf2 {{
    left: 25%;
    top: 56px;
    transform: rotate(40deg);
    animation-delay: .8s;
}}

.leaf3 {{
    left: 39%;
    top: 25px;
    transform: rotate(-40deg);
    animation-delay: 1.1s;
}}

.leaf4 {{
    right: 38%;
    top: 56px;
    transform: rotate(40deg);
    animation-delay: 1.4s;
}}

.leaf5 {{
    right: 24%;
    top: 26px;
    transform: rotate(-40deg);
    animation-delay: 1.7s;
}}

.leaf6 {{
    right: 11%;
    top: 56px;
    transform: rotate(40deg);
    animation-delay: 2s;
}}

@keyframes appearleaf {{
    from {{
        opacity: 0;
        transform: scale(.1);
    }}
    to {{
        opacity: 1;
    }}
}}

</style>
""",
    unsafe_allow_html=True,
)

# ============================================================
# HELPER FUNCTIONS
# ============================================================

def clean_text(value):
    if pd.isna(value):
        return ""
    return str(value).strip()


def find_column(columns, choices):
    lowered = {
        str(c).strip().lower(): c
        for c in columns
    }

    for choice in choices:
        if choice.lower() in lowered:
            return lowered[choice.lower()]

    return None


def extract_series(title):
    title = clean_text(title)

    patterns = [
        r"\(([^()]*)#\s*(\d+(?:\.\d+)?)\)",
        r"\(([^()]*)book\s*(\d+(?:\.\d+)?)\)",
        r"\[([^\[\]]*)#\s*(\d+(?:\.\d+)?)\]",
        r"\[([^\[\]]*)book\s*(\d+(?:\.\d+)?)\]",
    ]

    for pattern in patterns:
        match = re.search(pattern, title, re.I)

        if match:
            series_name = match.group(1).strip()
            number = float(match.group(2))
            return series_name, number

    return "Standalone", None


@st.cache_data(show_spinner=False)
def lookup_cover(title, author, isbn):
    isbn = re.sub(r"\D", "", clean_text(isbn))

    try:
        if isbn:
            url = f"https://covers.openlibrary.org/b/isbn/{isbn}-M.jpg"

            response = requests.get(
                url,
                timeout=8
            )

            if response.status_code == 200:
                if len(response.content) > 1000:
                    return url

        response = requests.get(
            "https://openlibrary.org/search.json",
            params={
                "title": title,
                "author": author,
                "limit": 1,
            },
            timeout=8,
        )

        if response.status_code == 200:
            docs = response.json().get("docs", [])

            if docs:
                cover_id = docs[0].get("cover_i")

                if cover_id:
                    return (
                        "https://covers.openlibrary.org/"
                        f"b/id/{cover_id}-M.jpg"
                    )

    except Exception:
        pass

    return ""


def make_book_records(df):
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

    genre_col = find_column(
        df.columns,
        ["Genre", "Genres"]
    )

    date_col = find_column(
        df.columns,
        [
            "Date Read",
            "Date Added",
            "Date Read",
            "Original Publication Year",
        ]
    )

    if title_col is None:
        raise ValueError(
            "I couldn't find a Title column in this CSV."
        )

    records = []

    for _, row in df.iterrows():

        title = clean_text(
            row.get(title_col, "")
        )

        if not title:
            continue

        author = (
            clean_text(row.get(author_col, ""))
            if author_col
            else "Unknown Author"
        )

        isbn = (
            clean_text(row.get(isbn_col, ""))
            if isbn_col
            else ""
        )

        rating = None

        if rating_col:
            try:
                value = float(row.get(rating_col))
                if value > 0:
                    rating = value
            except Exception:
                pass

        status = "Want to Read"

        if shelf_col:
            shelf = clean_text(
                row.get(shelf_col, "")
            ).lower()

            if "currently" in shelf:
                status = "Currently Reading"
            elif shelf == "read":
                status = "Read"

        genre = (
            clean_text(row.get(genre_col, ""))
            if genre_col
            else ""
        )

        date_value = ""

        if date_col:
            date_value = clean_text(
                row.get(date_col, "")
            )

        series, number = extract_series(title)

        records.append(
            {
                "Title": title,
                "Author": author,
                "Series": series,
                "Series Number": number,
                "ISBN": isbn,
                "My Rating": rating,
                "Status": status,
                "Genre": genre or "Uncategorized",
                "Date": date_value,
                "Cover": "",
            }
        )

    return pd.DataFrame(records)


def render_book(book):
    title = clean_text(book["Title"])
    status = clean_text(book["Status"])
    genre = clean_text(book["Genre"])

    number = book["Series Number"]

    prefix = ""

    if pd.notna(number):
        try:
            if float(number).is_integer():
                prefix = f"{int(number)}. "
            else:
                prefix = f"{number}. "
        except Exception:
            pass

    if status == "Read":
        status_class = "status-read"
    elif status == "Currently Reading":
        status_class = "status-current"
    else:
        status_class = "status-want"

    rating_text = ""

    if pd.notna(book["My Rating"]):
        try:
            rating = int(float(book["My Rating"]))
            if rating > 0:
                rating_text = " · " + ("★" * rating)
        except Exception:
            pass

    cover = clean_text(book["Cover"])

    if cover:
        image = (
            f'<img class="book-cover" '
            f'src="{html.escape(cover)}">'
        )
    else:
        image = (
            '<div class="book-placeholder">✦</div>'
        )

    st.markdown(
        f"""
        <div class="book-line">

            {image}

            <div class="book-text">

                <div class="book-name">
                    {html.escape(prefix + title)}
                </div>

                <div class="book-meta">

                    <span class="{status_class}">
                        {html.escape(status)}
                    </span>

                    · {html.escape(genre)}
                    {html.escape(rating_text)}

                </div>

            </div>

        </div>
        """,
        unsafe_allow_html=True,
    )


def render_series(author, series_name, series_books):

    author_key = re.sub(
        r"[^a-zA-Z0-9]+",
        "_",
        author
    )

    series_key = re.sub(
        r"[^a-zA-Z0-9]+",
        "_",
        series_name
    )

    key = f"{author_key}__{series_key}"

    is_open = key in st.session_state.open_series

    arrow = "⌄" if is_open else "›"

    clicked = st.button(
        f"{arrow}  {series_name}",
        key=f"series_button_{key}",
        use_container_width=False,
    )

    if clicked:

        if is_open:
            st.session_state.open_series.remove(key)
        else:
            st.session_state.open_series.add(key)

        st.rerun()

    st.markdown(
        f"""
        <div class="series-tree">
            <div class="series-line">
                <span class="series-name">
                    {html.escape(series_name)}
                </span>
                <span class="series-count">
                    {len(series_books)}
                    {"book" if len(series_books) == 1 else "books"}
                </span>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    if not is_open:
        return

    books = series_books.copy()

    books["_number_sort"] = pd.to_numeric(
        books["Series Number"],
        errors="coerce"
    )

    books = books.sort_values(
        ["_number_sort", "Title"],
        na_position="last"
    )

    st.markdown(
        '<div class="book-tree">',
        unsafe_allow_html=True
    )

    for _, book in books.iterrows():
        render_book(book)

    st.markdown(
        '</div>',
        unsafe_allow_html=True
    )


# ============================================================
# IMPORT FUNCTION
# ============================================================

def import_library(uploaded_file):

    try:
        df = pd.read_csv(
            uploaded_file,
            low_memory=False
        )
    except Exception:
        df = pd.read_csv(
            uploaded_file,
            encoding="latin-1",
            low_memory=False
        )

    books = make_book_records(df)

    if books.empty:
        raise ValueError(
            "No books were found in the CSV."
        )

    progress = st.progress(0)

    total = len(books)

    for index in range(total):

        title = books.at[index, "Title"]
        author = books.at[index, "Author"]
        isbn = books.at[index, "ISBN"]

        books.at[index, "Cover"] = lookup_cover(
            title,
            author,
            isbn
        )

        progress.progress(
            (index + 1) / total
        )

    progress.empty()

    st.session_state.books = books
    st.session_state.open_authors = set()
    st.session_state.open_series = set()


# ============================================================
# HEADER
# ============================================================

st.markdown(
    """
    <div class="book-title-header">

        <h1>My Book Tree</h1>

        <p>
            Every author has a branch · every story has a place
        </p>

        <div class="header-ornament">
            ❧ ✦ ❧
        </div>

    </div>
    """,
    unsafe_allow_html=True,
)

# ============================================================
# THEME
# ============================================================

st.markdown(
    '<div class="theme-label">Choose Your Reading Room</div>',
    unsafe_allow_html=True,
)

theme_options = list(THEMES.keys())

selected_theme = st.selectbox(
    "Choose a theme",
    theme_options,
    index=theme_options.index(
        st.session_state.theme
    ),
    label_visibility="collapsed",
)

if selected_theme != st.session_state.theme:
    st.session_state.theme = selected_theme
    st.rerun()

# ============================================================
# STATS
# ============================================================

books = st.session_state.books

total_books = len(books)

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
        (books["Status"] == "Read").sum()
    )
    if not books.empty
    else 0
)

st.markdown(
    f"""
    <div class="stats">

        <div class="stat">
            <span class="stat-number">{total_books}</span>
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

    </div>
    """,
    unsafe_allow_html=True,
)

# ============================================================
# TABS
# ============================================================

tree_tab, import_tab = st.tabs(
    [
        "🌿  My Book Tree",
        "Import Library",
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

                <div class="empty-title">
                    Your tree is waiting to grow.
                </div>

                <div class="empty-text">
                    Import your Goodreads library to begin.
                </div>

            </div>
            """,
            unsafe_allow_html=True,
        )

    else:

        st.markdown(
            """
            <div class="toolbar">

                <div class="toolbar-title">
                    Find your next branch
                </div>

            </div>
            """,
            unsafe_allow_html=True,
        )

        search_col, genre_col, status_col, sort_col = st.columns(
            [2.2, 1.1, 1.1, 1.4]
        )

        with search_col:
            search = st.text_input(
                "Search",
                placeholder="Search your library...",
                label_visibility="collapsed",
            )

        with genre_col:

            genres = sorted(
                books["Genre"]
                .fillna("Uncategorized")
                .astype(str)
                .unique()
            )

            genre_options = ["All Genres"] + genres

            selected_genre = st.selectbox(
                "Genre",
                genre_options,
                label_visibility="collapsed",
            )

        with status_col:

            status_options = [
                "All Books",
                "Read",
                "Currently Reading",
                "Want to Read",
            ]

            selected_status = st.selectbox(
                "Status",
                status_options,
                label_visibility="collapsed",
            )

        with sort_col:

            sort_options = [
                "Author A–Z",
                "Author Z–A",
                "Title A–Z",
                "Title Z–A",
                "Highest Rated",
                "Lowest Rated",
            ]

            selected_sort = st.selectbox(
                "Sort",
                sort_options,
                label_visibility="collapsed",
            )

        filtered = books.copy()

        if search:

            query = search.lower()

            mask = (
                filtered["Title"]
                .astype(str)
                .str.lower()
                .str.contains(query, na=False)
                |
                filtered["Author"]
                .astype(str)
                .str.lower()
                .str.contains(query, na=False)
                |
                filtered["Series"]
                .astype(str)
                .str.lower()
                .str.contains(query, na=False)
                |
                filtered["Genre"]
                .astype(str)
                .str.lower()
                .str.contains(query, na=False)
            )

            filtered = filtered[mask]

        if selected_genre != "All Genres":

            filtered = filtered[
                filtered["Genre"] == selected_genre
            ]

        if selected_status != "All Books":

            filtered = filtered[
                filtered["Status"] == selected_status
            ]

        if selected_sort == "Author A–Z":

            filtered = filtered.sort_values(
                "Author",
                key=lambda x:
                x.astype(str).str.lower()
            )

        elif selected_sort == "Author Z–A":

            filtered = filtered.sort_values(
                "Author",
                ascending=False,
                key=lambda x:
                x.astype(str).str.lower()
            )

        elif selected_sort == "Title A–Z":

            filtered = filtered.sort_values(
                "Title",
                key=lambda x:
                x.astype(str).str.lower()
            )

        elif selected_sort == "Title Z–A":

            filtered = filtered.sort_values(
                "Title",
                ascending=False,
                key=lambda x:
                x.astype(str).str.lower()
            )

        elif selected_sort == "Highest Rated":

            filtered = filtered.sort_values(
                "My Rating",
                ascending=False,
                na_position="last"
            )

        elif selected_sort == "Lowest Rated":

            filtered = filtered.sort_values(
                "My Rating",
                ascending=True,
                na_position="last"
            )

        st.markdown(
            """
            <div class="tree-heading">

                <h2>Your Library</h2>

                <p>
                    Author → Series → Book
                </p>

            </div>

            <div class="tree-root">
                <span>My Reading Tree</span>
            </div>
            """,
            unsafe_allow_html=True,
        )

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

            author_key = re.sub(
                r"[^a-zA-Z0-9]+",
                "_",
                author
            )

            is_open = (
                author_key
                in st.session_state.open_authors
            )

            arrow = "⌄" if is_open else "›"

            clicked = st.button(
                f"{arrow}  {author}",
                key=f"author_button_{author_key}",
            )

            st.markdown(
                f"""
                <div class="author-tree">

                    <div class="author-line">

                        <span class="author-name">
                            {html.escape(author)}
                        </span>

                        <span class="author-count">
                            {len(author_books)}
                            {"book" if len(author_books) == 1 else "books"}
                        </span>

                    </div>

                </div>
                """,
                unsafe_allow_html=True,
            )

            if clicked:

                if is_open:
                    st.session_state.open_authors.remove(
                        author_key
                    )
                else:
                    st.session_state.open_authors.add(
                        author_key
                    )

                st.rerun()

            if not is_open:
                continue

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
                        f"{author_key}__standalone"
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

                    clicked = st.button(
                        f"{arrow}  Standalone Books",
                        key=f"standalone_{author_key}",
                    )

                    st.markdown(
                        f"""
                        <div class="series-tree">

                            <div class="series-line">

                                <span class="series-name">
                                    Standalone Books
                                </span>

                                <span class="series-count">
                                    {len(series_books)}
                                </span>

                            </div>

                        </div>
                        """,
                        unsafe_allow_html=True,
                    )

                    if clicked:

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
                            '<div class="book-tree">',
                            unsafe_allow_html=True
                        )

                        for _, book in series_books.sort_values(
                            "Title"
                        ).iterrows():

                            render_book(book)

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

# ============================================================
# IMPORT
# ============================================================

with import_tab:

    st.markdown(
        """
        <div class="tree-heading">

            <h2>Grow Your Tree</h2>

            <p>
                Import your Goodreads library
            </p>

        </div>
        """,
        unsafe_allow_html=True,
    )

    uploaded = st.file_uploader(
        "Choose your Goodreads CSV",
        type=["csv"],
    )

    if uploaded:

        st.write(
            f"**{uploaded.name}** is ready to import."
        )

        if st.button(
            "🌿  Grow My Book Tree",
            type="primary",
        ):

            with st.spinner(
                "Planting your books and finding covers..."
            ):

                try:

                    import_library(uploaded)

                    st.success(
                        f"Your tree now has "
                        f"{len(st.session_state.books)} books."
                    )

                    st.rerun()

                except Exception as error:

                    st.error(
                        f"Something went wrong while importing: {error}"
                    )
