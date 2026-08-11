import streamlit as st
import pandas as pd
import re
import html
import requests

st.set_page_config(
    page_title="My Book Tree",
    page_icon="🌿",
    layout="wide"
)

# ============================================================
# THEMES
# ============================================================

THEMES = {
    "Midnight Garden": {
        "background": "#11131A",
        "surface": "#1D2029",
        "surface2": "#292D3A",
        "text": "#F7EBDD",
        "muted": "#C9BCB4",
        "accent": "#D8AD63",
        "accent2": "#B889A7",
        "branch": "#796652",
        "leaf": "#78916F",
    },
    "Burgundy Library": {
        "background": "#190B11",
        "surface": "#29121B",
        "surface2": "#3B1A27",
        "text": "#FAEBDD",
        "muted": "#D0B6B5",
        "accent": "#D9A75D",
        "accent2": "#D0788B",
        "branch": "#805445",
        "leaf": "#728562",
    },
    "Sapphire Study": {
        "background": "#08131F",
        "surface": "#102437",
        "surface2": "#183651",
        "text": "#F7EEDC",
        "muted": "#BCCAD5",
        "accent": "#DAB65F",
        "accent2": "#8EA8D1",
        "branch": "#637889",
        "leaf": "#6E9185",
    },
    "Poison Garden": {
        "background": "#10150F",
        "surface": "#192319",
        "surface2": "#293629",
        "text": "#F4EAD6",
        "muted": "#C1C9B7",
        "accent": "#D5B45D",
        "accent2": "#A982A1",
        "branch": "#68745A",
        "leaf": "#7A9C67",
    },
    "Gothic Romance": {
        "background": "#140B16",
        "surface": "#221223",
        "surface2": "#361A34",
        "text": "#F8E8E3",
        "muted": "#CEB8C4",
        "accent": "#D7A95D",
        "accent2": "#C66D92",
        "branch": "#82566B",
        "leaf": "#71866B",
    },
    "Autumn Reading Room": {
        "background": "#17100B",
        "surface": "#291A11",
        "surface2": "#3C2517",
        "text": "#F7E7CF",
        "muted": "#CFBBA2",
        "accent": "#D7A04D",
        "accent2": "#B97065",
        "branch": "#88613F",
        "leaf": "#72815C",
    },
}

if "theme" not in st.session_state:
    st.session_state.theme = "Midnight Garden"

if "books" not in st.session_state:
    st.session_state.books = pd.DataFrame()

if "open_authors" not in st.session_state:
    st.session_state.open_authors = set()

if "open_series" not in st.session_state:
    st.session_state.open_series = set()

if st.session_state.theme not in THEMES:
    st.session_state.theme = "Midnight Garden"

theme = THEMES[st.session_state.theme]

# ============================================================
# CSS
# ============================================================

css = f"""
<style>

@import url('https://fonts.googleapis.com/css2?family=Cormorant+Garamond:wght@400;500;600;700&family=Libre+Baskerville:wght@400;700&display=swap');

.stApp {{
    background:
        radial-gradient(
            circle at 50% 0%,
            {theme["surface2"]} 0%,
            {theme["background"]} 55%
        );
    color: {theme["text"]};
}}

.block-container {{
    max-width: 1350px;
    padding: 30px 45px 80px;
}}

h1, h2, h3, h4 {{
    font-family: "Cormorant Garamond", Georgia, serif !important;
}}

p, label {{
    font-family: "Libre Baskerville", Georgia, serif;
}}

.hero {{
    text-align: center;
    padding-top: 25px;
    margin-bottom: 15px;
}}

.hero h1 {{
    font-family: "Cormorant Garamond", Georgia, serif !important;
    font-size: 68px !important;
    font-weight: 600 !important;
    color: {theme["text"]} !important;
    margin: 0;
}}

.hero p {{
    color: {theme["muted"]};
    font-size: 11px;
    letter-spacing: 4px;
    text-transform: uppercase;
    margin-top: 10px;
}}

.ornament {{
    text-align: center;
    color: {theme["accent"]};
    font-family: "Cormorant Garamond", Georgia, serif;
    font-size: 27px;
    margin: 18px 0 30px;
}}

.theme-title {{
    text-align: center;
    color: {theme["accent"]};
    font-family: "Cormorant Garamond", Georgia, serif;
    font-size: 23px;
    margin-bottom: 8px;
}}

div[data-baseweb="select"] > div {{
    background: #181818 !important;
    border: 1px solid {theme["accent"]} !important;
    color: white !important;
}}

div[data-baseweb="select"] span {{
    color: white !important;
}}

div[role="listbox"] {{
    background: #181818 !important;
    border: 1px solid {theme["accent"]} !important;
}}

div[role="option"] {{
    background: #181818 !important;
    color: white !important;
}}

div[role="option"] * {{
    color: white !important;
}}

div[role="option"]:hover {{
    background: #3B3237 !important;
}}

.stats {{
    display: flex;
    justify-content: center;
    gap: 70px;
    margin: 35px 0 45px;
}}

.stat {{
    text-align: center;
}}

.stat-number {{
    display: block;
    font-family: "Cormorant Garamond", Georgia, serif;
    font-size: 42px;
    color: {theme["accent"]};
    line-height: 1;
}}

.stat-label {{
    display: block;
    margin-top: 7px;
    font-family: "Libre Baskerville", Georgia, serif;
    font-size: 9px;
    letter-spacing: 2px;
    text-transform: uppercase;
    color: {theme["muted"]};
}}

.section-title {{
    text-align: center;
    font-family: "Cormorant Garamond", Georgia, serif;
    font-size: 46px;
    color: {theme["text"]};
    margin-top: 15px;
}}

.section-subtitle {{
    text-align: center;
    font-family: "Cormorant Garamond", Georgia, serif;
    font-style: italic;
    font-size: 19px;
    color: {theme["muted"]};
    margin-bottom: 35px;
}}

.tree-root {{
    text-align: center;
    margin: 20px auto 40px;
}}

.tree-root span {{
    color: {theme["accent"]};
    font-family: "Cormorant Garamond", Georgia, serif;
    font-size: 27px;
    border-top: 1px solid {theme["accent"]};
    border-bottom: 1px solid {theme["accent"]};
    padding: 7px 28px;
}}

.author-block {{
    margin-left: 30px;
    padding-left: 28px;
    border-left: 1px solid {theme["branch"]};
    margin-bottom: 22px;
}}

.author-name {{
    font-family: "Cormorant Garamond", Georgia, serif;
    font-size: 31px;
    font-weight: 600;
    color: {theme["text"]};
}}

.count {{
    color: {theme["muted"]};
    font-family: "Libre Baskerville", Georgia, serif;
    font-size: 10px;
    margin-left: 10px;
}}

.series-block {{
    margin-left: 35px;
    padding-left: 25px;
    border-left: 1px solid {theme["branch"]};
    margin-top: 10px;
    margin-bottom: 15px;
}}

.series-name {{
    font-family: "Cormorant Garamond", Georgia, serif;
    font-size: 25px;
    color: {theme["accent"]};
}}

.book-block {{
    margin-left: 35px;
    padding-left: 25px;
    border-left: 1px solid {theme["branch"]};
}}

.book-row {{
    display: flex;
    align-items: center;
    min-height: 70px;
    gap: 15px;
    padding: 7px 0;
}}

.cover {{
    width: 43px;
    height: 63px;
    object-fit: cover;
    border: 1px solid {theme["accent"]};
    box-shadow: 3px 4px 12px rgba(0,0,0,.4);
}}

.no-cover {{
    width: 43px;
    height: 63px;
    display: flex;
    align-items: center;
    justify-content: center;
    background: {theme["surface2"]};
    border: 1px solid {theme["branch"]};
    color: {theme["accent"]};
}}

.book-title {{
    font-family: "Cormorant Garamond", Georgia, serif;
    font-size: 21px;
    color: {theme["text"]};
}}

.book-info {{
    font-family: "Libre Baskerville", Georgia, serif;
    font-size: 10px;
    color: {theme["muted"]};
    margin-top: 3px;
}}

.stButton > button {{
    background: transparent !important;
    border: none !important;
    color: {theme["text"]} !important;
    font-family: "Cormorant Garamond", Georgia, serif !important;
    font-size: 21px !important;
    box-shadow: none !important;
}}

.stButton > button:hover {{
    color: {theme["accent"]} !important;
}}

.empty {{
    text-align: center;
    padding: 80px 20px;
}}

.empty h2 {{
    font-family: "Cormorant Garamond", Georgia, serif;
    font-size: 46px;
    color: {theme["text"]};
}}

.empty p {{
    color: {theme["muted"]};
}}

</style>
"""

st.markdown(css, unsafe_allow_html=True)

# ============================================================
# FUNCTIONS
# ============================================================

def clean(value):
    if pd.isna(value):
        return ""
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


def get_series(title):
    title = clean(title)

    patterns = [
        r"\((.*?)#\s*(\d+(?:\.\d+)?)\)",
        r"\((.*?)book\s*(\d+(?:\.\d+)?)\)",
        r"\[(.*?)#\s*(\d+(?:\.\d+)?)\]",
        r"\[(.*?)book\s*(\d+(?:\.\d+)?)\]",
    ]

    for pattern in patterns:
        match = re.search(pattern, title, re.IGNORECASE)

        if match:
            return (
                match.group(1).strip(),
                float(match.group(2))
            )

    return "Standalone", None


@st.cache_data(show_spinner=False)
def get_cover(title, author, isbn):

    isbn = re.sub(
        r"\D",
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
            timeout=8,
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


def convert_csv(dataframe):

    title_column = find_column(
        dataframe.columns,
        ["Title"]
    )

    author_column = find_column(
        dataframe.columns,
        ["Author", "Authors"]
    )

    isbn_column = find_column(
        dataframe.columns,
        ["ISBN", "ISBN13"]
    )

    rating_column = find_column(
        dataframe.columns,
        ["My Rating", "Rating"]
    )

    shelf_column = find_column(
        dataframe.columns,
        ["Exclusive Shelf", "Shelf"]
    )

    genre_column = find_column(
        dataframe.columns,
        ["Genre", "Genres"]
    )

    date_column = find_column(
        dataframe.columns,
        [
            "Date Read",
            "Date Added",
            "Original Publication Year"
        ]
    )

    if title_column is None:
        raise ValueError(
            "I couldn't find a Title column in the CSV."
        )

    records = []

    for _, row in dataframe.iterrows():

        title = clean(
            row.get(title_column, "")
        )

        if not title:
            continue

        author = (
            clean(row.get(author_column, ""))
            if author_column
            else "Unknown Author"
        )

        isbn = (
            clean(row.get(isbn_column, ""))
            if isbn_column
            else ""
        )

        rating = None

        if rating_column:

            try:

                value = float(
                    row.get(rating_column)
                )

                if value > 0:
                    rating = value

            except Exception:
                pass

        status = "Want to Read"

        if shelf_column:

            shelf = clean(
                row.get(shelf_column, "")
            ).lower()

            if "currently" in shelf:
                status = "Currently Reading"

            elif shelf == "read":
                status = "Read"

        genre = (
            clean(row.get(genre_column, ""))
            if genre_column
            else "Uncategorized"
        )

        date = (
            clean(row.get(date_column, ""))
            if date_column
            else ""
        )

        series, number = get_series(title)

        records.append(
            {
                "Title": title,
                "Author": author,
                "Series": series,
                "Series Number": number,
                "ISBN": isbn,
                "Rating": rating,
                "Status": status,
                "Genre": genre or "Uncategorized",
                "Date": date,
                "Cover": "",
            }
        )

    return pd.DataFrame(records)


def book_html(book):

    title = clean(book["Title"])
    status = clean(book["Status"])
    genre = clean(book["Genre"])

    number = book["Series Number"]

    number_text = ""

    if pd.notna(number):

        try:

            if float(number).is_integer():
                number_text = (
                    f"{int(number)}. "
                )
            else:
                number_text = (
                    f"{number}. "
                )

        except Exception:
            pass

    rating = ""

    if pd.notna(book["Rating"]):

        try:

            rating_number = int(
                float(book["Rating"])
            )

            if rating_number > 0:
                rating = (
                    " · " + "★" * rating_number
                )

        except Exception:
            pass

    cover = clean(book["Cover"])

    if cover:

        image = (
            f'<img class="cover" '
            f'src="{html.escape(cover)}">'
        )

    else:

        image = (
            '<div class="no-cover">✦</div>'
        )

    return f"""
<div class="book-row">
{image}
<div>
<div class="book-title">{html.escape(number_text + title)}</div>
<div class="book-info">{html.escape(status)} · {html.escape(genre)}{html.escape(rating)}</div>
</div>
</div>
"""


def render_series(author, series_name, series_books):

    key = (
        re.sub(
            r"[^A-Za-z0-9]+",
            "_",
            author
        )
        + "__"
        + re.sub(
            r"[^A-Za-z0-9]+",
            "_",
            series_name
        )
    )

    is_open = (
        key in st.session_state.open_series
    )

    arrow = "⌄" if is_open else "›"

    if st.button(
        f"{arrow}  {series_name}",
        key=f"series_{key}"
    ):

        if is_open:
            st.session_state.open_series.remove(key)
        else:
            st.session_state.open_series.add(key)

        st.rerun()

    st.markdown(
        f'<div class="series-block"><span class="series-name">{html.escape(series_name)}</span><span class="count">{len(series_books)} books</span></div>',
        unsafe_allow_html=True
    )

    if is_open:

        sorted_books = series_books.copy()

        sorted_books["_sort"] = pd.to_numeric(
            sorted_books["Series Number"],
            errors="coerce"
        )

        sorted_books = sorted_books.sort_values(
            ["_sort", "Title"],
            na_position="last"
        )

        content = ""

        for _, book in sorted_books.iterrows():
            content += book_html(book)

        st.markdown(
            f'<div class="book-block">{content}</div>',
            unsafe_allow_html=True
        )


# ============================================================
# HEADER
# ============================================================

st.markdown(
    """
<div class="hero">
<h1>My Book Tree</h1>
<p>Every author has a branch · every story has a place</p>
</div>
<div class="ornament">❧ ✦ ❧</div>
""",
    unsafe_allow_html=True
)

# ============================================================
# THEME PICKER
# ============================================================

st.markdown(
    '<div class="theme-title">Choose Your Reading Room</div>',
    unsafe_allow_html=True
)

theme_names = list(THEMES.keys())

selected_theme = st.selectbox(
    "Theme",
    theme_names,
    index=theme_names.index(
        st.session_state.theme
    ),
    label_visibility="collapsed"
)

if selected_theme != st.session_state.theme:

    st.session_state.theme = selected_theme
    st.rerun()

# ============================================================
# STATS
# ============================================================

books = st.session_state.books

book_total = len(books)

author_total = (
    books["Author"].nunique()
    if not books.empty
    else 0
)

series_total = (
    books.loc[
        books["Series"] != "Standalone",
        "Series"
    ].nunique()
    if not books.empty
    else 0
)

read_total = (
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
<span class="stat-number">{book_total}</span>
<span class="stat-label">Books</span>
</div>
<div class="stat">
<span class="stat-number">{author_total}</span>
<span class="stat-label">Authors</span>
</div>
<div class="stat">
<span class="stat-number">{series_total}</span>
<span class="stat-label">Series</span>
</div>
<div class="stat">
<span class="stat-number">{read_total}</span>
<span class="stat-label">Read</span>
</div>
</div>
""",
    unsafe_allow_html=True
)

# ============================================================
# TABS
# ============================================================

tree_tab, import_tab = st.tabs(
    ["🌿  My Book Tree", "Import Library"]
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
<p>Import your Goodreads library to begin.</p>
</div>
""",
            unsafe_allow_html=True
        )

    else:

        search_col, genre_col, status_col, sort_col = st.columns(
            [2.2, 1.1, 1.1, 1.4]
        )

        with search_col:

            search = st.text_input(
                "Search",
                placeholder="Search your library...",
                label_visibility="collapsed"
            )

        with genre_col:

            genres = sorted(
                books["Genre"]
                .fillna("Uncategorized")
                .astype(str)
                .unique()
            )

            selected_genre = st.selectbox(
                "Genre",
                ["All Genres"] + genres,
                label_visibility="collapsed"
            )

        with status_col:

            selected_status = st.selectbox(
                "Status",
                [
                    "All Books",
                    "Read",
                    "Currently Reading",
                    "Want to Read"
                ],
                label_visibility="collapsed"
            )

        with sort_col:

            selected_sort = st.selectbox(
                "Sort",
                [
                    "Author A–Z",
                    "Author Z–A",
                    "Title A–Z",
                    "Title Z–A",
                    "Highest Rated",
                    "Lowest Rated"
                ],
                label_visibility="collapsed"
            )

        filtered = books.copy()

        if search:

            q = search.lower()

            mask = (
                filtered["Title"]
                .astype(str)
                .str.lower()
                .str.contains(q, na=False)
                |
                filtered["Author"]
                .astype(str)
                .str.lower()
                .str.contains(q, na=False)
                |
                filtered["Series"]
                .astype(str)
                .str.lower()
                .str.contains(q, na=False)
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
                "Rating",
                ascending=False,
                na_position="last"
            )

        elif selected_sort == "Lowest Rated":

            filtered = filtered.sort_values(
                "Rating",
                ascending=True,
                na_position="last"
            )

        st.markdown(
            """
<div class="section-title">Your Library</div>
<div class="section-subtitle">Author → Series → Book</div>
<div class="tree-root"><span>My Reading Tree</span></div>
""",
            unsafe_allow_html=True
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
                r"[^A-Za-z0-9]+",
                "_",
                author
            )

            is_open = (
                author_key
                in st.session_state.open_authors
            )

            arrow = "⌄" if is_open else "›"

            if st.button(
                f"{arrow}  {author}   ·   {len(author_books)} books",
                key=f"author_{author_key}"
            ):

                if is_open:
                    st.session_state.open_authors.remove(
                        author_key
                    )
                else:
                    st.session_state.open_authors.add(
                        author_key
                    )

                st.rerun()

            st.markdown(
                '<div class="author-block"></div>',
                unsafe_allow_html=True
            )

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
                        author_key + "__standalone"
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

                    if st.button(
                        f"{arrow}  Standalone Books   ·   {len(series_books)}",
                        key=f"standalone_{author_key}"
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

                    st.markdown(
                        '<div class="series-block"><span class="series-name">Standalone Books</span></div>',
                        unsafe_allow_html=True
                    )

                    if standalone_open:

                        content = ""

                        for _, book in series_books.sort_values(
                            "Title"
                        ).iterrows():

                            content += book_html(book)

                        st.markdown(
                            f'<div class="book-block">{content}</div>',
                            unsafe_allow_html=True
                        )

                else:

                    render_series(
                        author,
                        series_name,
                        series_books
                    )

# ============================================================
# IMPORT TAB
# ============================================================

with import_tab:

    st.markdown(
        """
<div class="section-title">Grow Your Tree</div>
<div class="section-subtitle">Import your Goodreads library</div>
""",
        unsafe_allow_html=True
    )

    uploaded = st.file_uploader(
        "Choose your Goodreads CSV",
        type=["csv"]
    )

    if uploaded:

        if st.button(
            "🌿  Grow My Book Tree",
            type="primary"
        ):

            try:

                with st.spinner(
                    "Planting your books..."
                ):

                    raw = pd.read_csv(
                        uploaded,
                        low_memory=False
                    )

                    new_books = convert_csv(raw)

                    if new_books.empty:
                        raise ValueError(
                            "No books were found."
                        )

                    progress = st.progress(0)

                    total = len(new_books)

                    for i in range(total):

                        new_books.at[
                            i,
                            "Cover"
                        ] = get_cover(
                            new_books.at[
                                i,
                                "Title"
                            ],
                            new_books.at[
                                i,
                                "Author"
                            ],
                            new_books.at[
                                i,
                                "ISBN"
                            ]
                        )

                        progress.progress(
                            (i + 1) / total
                        )

                    progress.empty()

                    st.session_state.books = new_books
                    st.session_state.open_authors = set()
                    st.session_state.open_series = set()

                st.success(
                    f"Your tree has grown to {len(new_books)} books!"
                )

                st.rerun()

            except Exception as error:

                st.error(
                    f"Import failed: {error}"
                )
