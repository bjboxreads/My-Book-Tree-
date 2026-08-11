import streamlit as st

def display_ancestry_tree(df):
    # 1. Clean data: Fill empty Series with 'Standalone'
    df['Series'] = df['Series'].fillna('Standalone').replace('', 'Standalone')
    
    # 2. Iterate through each Author (The Trunk)
    for author, author_df in df.groupby('Author'):
        # Creating the main trunk expander (Closed by default)
        with st.expander(f"🌳 {author}", expanded=False):
            
            # 3. Get all Series for this specific author
            series_list = author_df['Series'].unique()
            
            # 4. Create Columns so Series appear side-by-side (Siblings)
            # This makes the "ancestry" horizontal row
            cols = st.columns(len(series_list))
            
            for i, series in enumerate(series_list):
                with cols[i]:
                    # 5. Create a branch for each Series (Closed by default)
                    with st.expander(f"📂 {series}", expanded=False):
                        
                        # 6. List the Books vertically underneath (The Kids)
                        series_books = author_df[author_df['Series'] == series]
                        for _, book in series_books.iterrows():
                            # You can use st.info or st.write here
                            st.write(f"📖 {book['Title']}")

# Usage:
# if not df.empty:
#     display_ancestry_tree(df)
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
# THEMES
# ============================================================

THEMES = {
    "Enchanted Library": {
        "page": "#071B18",
        "surface": "#0E2924",
        "surface2": "#164239",
        "card": "#1C5146",
        "text": "#FFF7DE",
        "muted": "#C7D8CF",
        "accent": "#D8A93A",
        "accent2": "#6FB39A",
        "line": "#B9822C",
    },
    "Midnight & Gold": {
        "page": "#071426",
        "surface": "#0D2340",
        "surface2": "#15365D",
        "card": "#1C4774",
        "text": "#FFF7E1",
        "muted": "#C7D5E5",
        "accent": "#E5B94D",
        "accent2": "#75B5D4",
        "line": "#B8862F",
    },
    "Victorian Rose": {
        "page": "#180B16",
        "surface": "#2A1024",
        "surface2": "#421735",
        "card": "#592044",
        "text": "#FFF4F5",
        "muted": "#DEC8D0",
        "accent": "#E36A83",
        "accent2": "#C79AD7",
        "line": "#A83F5C",
    },
    "Autumn Manor": {
        "page": "#24130A",
        "surface": "#38200F",
        "surface2": "#5A3015",
        "card": "#70401D",
        "text": "#FFF1D5",
        "muted": "#DCC4A1",
        "accent": "#E2A33D",
        "accent2": "#C9663C",
        "line": "#A84F2B",
    },
    "Moonlit Library": {
        "page": "#0C0A20",
        "surface": "#151235",
        "surface2": "#211C51",
        "card": "#30276A",
        "text": "#FFF8E7",
        "muted": "#D1CAE7",
        "accent": "#E8C34D",
        "accent2": "#8B73D1",
        "line": "#6851A8",
    },
    "Secret Garden": {
        "page": "#08252A",
        "surface": "#0E3B42",
        "surface2": "#14565D",
        "card": "#1C6B70",
        "text": "#FFF6DF",
        "muted": "#C9D9D4",
        "accent": "#F0BD4D",
        "accent2": "#F27A63",
        "line": "#D65D4B",
    },
    "Old World Library": {
        "page": "#172322",
        "surface": "#243633",
        "surface2": "#36504A",
        "card": "#49665D",
        "text": "#FFF3D8",
        "muted": "#D2D5C6",
        "accent": "#D8A84A",
        "accent2": "#A9B86B",
        "line": "#B47B31",
    },
    "Spellbound": {
        "page": "#111225",
        "surface": "#1B1E3A",
        "surface2": "#292E59",
        "card": "#353B76",
        "text": "#FFFFFF",
        "muted": "#D0D3E9",
        "accent": "#F4C84D",
        "accent2": "#6AD6D0",
        "line": "#A66CDB",
    },
    "Velvet & Crimson": {
        "page": "#210D0D",
        "surface": "#351313",
        "surface2": "#531B1B",
        "card": "#6A2524",
        "text": "#FFF4DF",
        "muted": "#DCC8B4",
        "accent": "#E3B34B",
        "accent2": "#D57958",
        "line": "#A83E32",
    },
}

# ============================================================
# SESSION STATE
# ============================================================

if "theme" not in st.session_state:
    st.session_state.theme = "Enchanted Library"

if "library" not in st.session_state:
    st.session_state.library = pd.DataFrame(
        columns=[
            "Title",
            "Author",
            "Series",
            "Series Number",
            "Genre",
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

    @import url(
        'https://fonts.googleapis.com/css2?family=Berkshire+Swash&family=Libre+Baskerville:wght@400;700&display=swap'
    );

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
                ellipse at 50% -10%,
                var(--surface2) 0%,
                var(--page) 65%
            ) !important;
        color: var(--text) !important;
    }}

    .block-container {{
        max-width: 1400px;
        padding-top: 1.5rem;
        padding-bottom: 4rem;
    }}

    h1, h2, h3, h4 {{
        font-family: "Berkshire Swash", Georgia, serif !important;
        color: var(--text) !important;
    }}

    p, label {{
        color: var(--text) !important;
    }}

    .book-header {{
        text-align: center;
        margin-top: 72px !important;
    }}

    .book-header-title {{
        font-family: "Berkshire Swash", Georgia, serif !important;
        font-size: clamp(48px, 6vw, 76px);
        color: var(--accent) !important;
        text-shadow: 0 3px 12px rgba(0,0,0,0.35);
    }}

    .theme-heading {{
        font-family: "Berkshire Swash", Georgia, serif;
        font-size: 25px;
        color: var(--text);
        margin-bottom: 7px;
    }}

    div[data-baseweb="select"] > div {{
        background: #171717 !important;
        border: 2px solid var(--accent) !important;
        border-radius: 10px !important;
    }}

    div[data-baseweb="select"] span {{
        color: #FFFFFF !important;
    }}

    div[data-baseweb="input"] > div {{
        background: var(--surface) !important;
        border-color: var(--line) !important;
        border-radius: 8px !important;
    }}

    div[data-baseweb="input"] input {{
        color: var(--text) !important;
    }}

    .stButton > button {{
        background: linear-gradient(
            135deg,
            var(--surface),
            var(--surface2)
        ) !important;
        color: var(--text) !important;
        border: 1px solid var(--accent) !important;
        border-radius: 18px 5px 18px 5px !important;
        font-family: "Libre Baskerville", Georgia, serif !important;
        box-shadow: 0 3px 10px rgba(0,0,0,.18) !important;
        transition: all .15s ease !important;
    }}

    .stButton > button:hover {{
        background: linear-gradient(
            135deg,
            var(--surface2),
            var(--card)
        ) !important;
        border-color: var(--accent) !important;
        box-shadow: 0 4px 14px rgba(0,0,0,.25) !important;
    }}

    .stat-card {{
        background: var(--card);
        border: 1px solid var(--accent);
        border-radius: 24px 7px 24px 7px;
        padding: 18px 10px;
        text-align: center;
        position: relative;
        box-shadow: 0 6px 18px rgba(0,0,0,.18);
    }}

    .stat-card::before {{
        content: "❧  ❦  ❧";
        display: block;
        color: var(--accent);
        font-size: 18px;
        line-height: 1;
        margin-bottom: 4px;
    }}

    .stat-number {{
        font-family: "Berkshire Swash", Georgia, serif;
        font-size: 38px;
        color: var(--accent);
    }}

    .stat-label {{
        font-family: "Libre Baskerville", Georgia, serif;
        color: var(--text);
        font-size: 10px;
        text-transform: uppercase;
        letter-spacing: .08em;
    }}

    .tree-root {{
        width: 300px;
        margin: 0 auto 45px;
        padding: 18px;
        background: var(--accent);
        color: var(--page);
        text-align: center;
        border-radius: 5px 28px 5px 28px;
        position: relative;
    }}

    .tree-root:after {{
        content: "";
        position: absolute;
        width: 2px;
        height: 45px;
        background: var(--accent);
        left: 50%;
        bottom: -45px;
    }}

    .tree-root-title {{
        font-family: "Berkshire Swash", Georgia, serif;
        font-size: 34px;
    }}

    .tree-root-count {{
        font-family: "Libre Baskerville", Georgia, serif;
        font-size: 11px;
    }}

    .author-branch {{
        position: relative;
        margin: 25px 0;
        padding-left: 35px;
        border-left: 3px solid var(--accent);
    }}

    .author-card {{
        background: linear-gradient(90deg, var(--surface), transparent);
        border-radius: 0 18px 0 0;
        padding: 13px 18px;
    }}

    .author-name {{
        font-family: "Berkshire Swash", Georgia, serif;
        font-size: 29px;
    }}

    .author-count {{
        color: var(--muted);
        font-family: "Libre Baskerville", Georgia, serif;
        font-size: 10px;
    }}

    .series-branch {{
        margin: 18px 0 18px 45px;
        padding-left: 25px;
        border-left: 2px solid var(--accent2);
    }}

    .series-card {{
        background: linear-gradient(90deg, var(--surface2), transparent);
        border-radius: 0 15px 0 0;
        padding: 11px 15px;
    }}

    .series-name {{
        font-family: "Berkshire Swash", Georgia, serif;
        font-size: 24px;
    }}

    .series-count {{
        color: var(--muted);
        font-family: "Libre Baskerville", Georgia, serif;
        font-size: 10px;
    }}

    .book-branch {{
        margin: 8px 0 8px 35px;
        padding: 10px 14px;
        background: linear-gradient(90deg, var(--card), transparent);
        border-left: 2px solid var(--line);
        border-radius: 0 12px 0 0;
    }}

    .book-title {{
        font-family: "Berkshire Swash", Georgia, serif;
        font-size: 21px;
        color: var(--text);
    }}

    .book-meta {{
        color: var(--muted);
        font-family: "Libre Baskerville", Georgia, serif;
        font-size: 10px;
        margin-top: 4px;
    }}

    .book-cover {{
        width: 55px;
        height: 80px;
        object-fit: cover;
        border-radius: 3px 10px 3px 10px;
        border: 1px solid var(--accent);
    }}

    .stCheckbox label {{
        color: var(--text) !important;
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
        <div class="book-header-title">My Book Tree</div>
    </div>
    """
)

# ============================================================
# THEME
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

    isbn = re.sub(r"\D", "", str(isbn))

    # Try ISBN first
    if isbn:

        url = (
            f"https://covers.openlibrary.org/"
            f"b/isbn/{isbn}-L.jpg"
        )

        try:
            response = requests.get(
                url,
                timeout=8,
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
                [],
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

    # Google Books fallback
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
                [],
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
                        "https://",
                    )

    except Exception:
        pass

    return ""


# ============================================================
# SERIES DETECTION
# ============================================================

def detect_series(title):

    text = str(title)

    patterns = [
        r"\(([^()]*)#\s*(\d+(?:\.\d+)?)\)",
        r"\[([^\[\]]*)#\s*(\d+(?:\.\d+)?)\]",
        r"\(([^()]*)\bBook\s+(\d+(?:\.\d+)?)\)",
        r"\[([^\[\]]*)\bBook\s+(\d+(?:\.\d+)?)\]",
    ]

    for pattern in patterns:

        match = re.search(
            pattern,
            text,
            re.IGNORECASE,
        )

        if match:

            series = match.group(1)

            series = re.sub(
                r",?\s*#\s*\d+(?:\.\d+)?",
                "",
                series,
                flags=re.IGNORECASE,
            )

            series = re.sub(
                r"\bBook\s+\d+(?:\.\d+)?",
                "",
                series,
                flags=re.IGNORECASE,
            )

            series = re.sub(
                r"\s+",
                " ",
                series,
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
            re.IGNORECASE,
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
        str(text),
    )


# ============================================================
# IMPORT BOOKS
# ============================================================

def import_books(uploaded_file):

# --------------------------------------------------------
# READ CSV
# --------------------------------------------------------

    try:

            uploaded_file.seek(0)

            df = pd.read_csv(
                uploaded_file,
                low_memory=False,
            )

    except Exception: 

        try:

            uploaded_file.seek(0)

            df = pd.read_csv(
                uploaded_file,
                encoding="latin-1",
                low_memory=False,
            )

        except Exception as error:

            st.error(
                f"Could not read this CSV file: {error}"
            )

            return False

    # --------------------------------------------------------
    # FIND COLUMNS
    # --------------------------------------------------------

    columns = {
        str(column).strip().lower(): column
        for column in df.columns
    }

    def find_column(names):

        for name in names:

            if name.lower() in columns:
                return columns[name.lower()]

        return None

    title_col = find_column(
        [
            "title",
            "book title",
        ]
    )

    author_col = find_column(
        [
            "author",
            "authors",
        ]
    )

    isbn_col = find_column(
        [
            "isbn13",
            "isbn",
            "isbn 13",
        ]
    )

    rating_col = find_column(
        [
            "my rating",
            "rating",
        ]
    )

    shelf_col = find_column(
        [
            "exclusive shelf",
            "shelf",
            "status",
        ]
    )

    genre_col = find_column(
        [
            "genre",
            "genres",
            "primary genre",
            "genre(s)",
        ]
    )

    series_col = find_column(
        [
            "series",
            "series name",
        ]
    )

    series_number_col = find_column(
        [
            "series number",
            "series no",
            "book number",
        ]
    )

    # --------------------------------------------------------
    # TITLE IS REQUIRED
    # --------------------------------------------------------

    if not title_col:

        st.error(
            "I couldn't find a Title column in this CSV."
        )

        st.write(
            "Columns found in your file:"
        )

        st.write(
            list(df.columns)
        )

        return False

    # --------------------------------------------------------
    # BUILD BOOK LIST
    # --------------------------------------------------------

    books = []

    for _, row in df.iterrows():

        title = str(
            row.get(
                title_col,
                "",
            )
        ).strip()

        if (
            not title
            or title.lower() == "nan"
        ):
            continue

        # AUTHOR

        author = "Unknown Author"

        if author_col:

            author = str(
                row.get(
                    author_col,
                    "",
                )
            ).strip()

        if (
            not author
            or author.lower() == "nan"
        ):
            author = "Unknown Author"

        # ISBN

        isbn = ""

        if isbn_col:

            isbn = re.sub(
                r"\D",
                "",
                str(
                    row.get(
                        isbn_col,
                        "",
                    )
                ),
            )

        # GENRE

        genre = ""

        if genre_col:

            genre = str(
                row.get(
                    genre_col,
                    "",
                )
            ).strip()

            if genre.lower() == "nan":
                genre = ""

        # SERIES

        if series_col:

            series = str(
                row.get(
                    series_col,
                    "",
                )
            ).strip()

            if (
                not series
                or series.lower() == "nan"
            ):
                series = detect_series(
                    title
                )

        else:

            series = detect_series(
                title
            )

        if not series:
            series = "Standalone"

        # SERIES NUMBER

        series_number = None

        if series_number_col:

            try:

                value = row.get(
                    series_number_col
                )

                if pd.notna(value):

                    series_number = float(
                        value
                    )

            except Exception:
                pass

        if series_number is None:

            series_number = (
                detect_series_number(
                    title
                )
            )

        # RATING

        rating = None

        if rating_col:

            try:

                value = row.get(
                    rating_col
                )

                if pd.notna(value):

                    rating = float(
                        value
                    )

            except Exception:
                pass

        # STATUS

        status = "Want to Read"

        if shelf_col:

            shelf = str(
                row.get(
                    shelf_col,
                    "",
                )
            ).strip().lower()

            if (
                "currently" in shelf
                or "currently-reading" in shelf
            ):

                status = "Currently Reading"

            elif (
                shelf == "read"
                or shelf == "finished"
                or (
                    "read" in shelf
                    and "to-read" not in shelf
                )
            ):

                status = "Read"

            elif (
                "to-read" in shelf
                or "want" in shelf
                or "wishlist" in shelf
            ):

                status = "Want to Read"

        books.append(
            {
                "Title": title,
                "Author": author,
                "Series": series,
                "Series Number": series_number,
                "Genre": genre,
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

    # --------------------------------------------------------
    # MAKE DATAFRAME
    # --------------------------------------------------------

    new_library = pd.DataFrame(
        books
    )

    if new_library.empty:

        st.error(
            "No books were found in the file."
        )

        return False

    # --------------------------------------------------------
    # SAVE BOOKS BEFORE COVER SEARCH
    # --------------------------------------------------------

    st.session_state.library = (
        new_library
    )

    st.session_state.open_authors = set()
    st.session_state.open_series = set()

    # --------------------------------------------------------
    # FIND COVERS
    # --------------------------------------------------------

    total_books = len(
        new_library
    )

    progress = st.progress(
        0
    )

    for i in range(
        total_books
    ):

        try:

            cover = get_cover(
                new_library.loc[
                    i,
                    "Title",
                ],
                new_library.loc[
                    i,
                    "Author",
                ],
                new_library.loc[
                    i,
                    "ISBN",
                ],
            )

            new_library.loc[
                i,
                "Cover",
            ] = cover

        except Exception:

            new_library.loc[
                i,
                "Cover",
            ] = ""

        progress.progress(
            (i + 1)
            / total_books
        )

    progress.empty()

    # --------------------------------------------------------
    # SAVE FINAL LIBRARY
    # --------------------------------------------------------

    st.session_state.library = (
        new_library
    )

    return True


# ============================================================
# DATA
# ============================================================

library = st.session_state.library

total = len(
    library
)

authors = (
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

favorites = (
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

columns = st.columns(
    5
)

stats = [
    (total, "Books"),
    (authors, "Authors"),
    (series_count, "Series"),
    (read_count, "Read"),
    (favorites, "Favorites"),
]

for col, (
    number,
    label,
) in zip(
    columns,
    stats,
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
        "🌳 Book Tree",
        "📚 Books",
        "➕ Add Book",
        "📥 Import",
    ]
)

# ============================================================
# BOOK TREE
# ============================================================

# ============================================================
# BOOK TREE
# ============================================================

with tree_tab:

    st.subheader("Search My Book Tree")

    search = st.text_input(
        "Search",
        placeholder="Search by author, title, series, genre, or ISBN...",
        label_visibility="collapsed",
    )

    st.caption(
        "Searches authors, titles, series, genres, and ISBNs."
    )

    # --------------------------------------------------------
    # FILTER BOOKS
    # --------------------------------------------------------

    filtered = library.copy()

    if search.strip():

        q = search.strip().lower()

        searchable = (
            filtered["Title"].fillna("").astype(str)
            + " "
            + filtered["Author"].fillna("").astype(str)
            + " "
            + filtered["Series"].fillna("").astype(str)
            + " "
            + filtered["Genre"].fillna("").astype(str)
            + " "
            + filtered["ISBN"].fillna("").astype(str)
        ).str.lower()

        filtered = filtered[
            searchable.str.contains(
                q,
                na=False,
                regex=False,
            )
        ]

    # --------------------------------------------------------
    # EMPTY TREE
    # --------------------------------------------------------

    if filtered.empty:

        if library.empty:

            st.info(
                "Your tree is empty. "
                "Import your library or add your first book."
            )

        else:

            st.info(
                f'No books matched "{search}".'
            )

    else:

        # ----------------------------------------------------
        # TREE TITLE
        # ----------------------------------------------------

        st.html(
            """
            <div style="
                text-align:center;
                margin:20px 0 30px 0;
            ">
                <div style="
                    font-family:'Berkshire Swash', Georgia, serif;
                    font-size:34px;
                    color:var(--accent);
                ">
                    🌳 My Library
                </div>
            </div>
            """
        )

        # ----------------------------------------------------
        # AUTHORS
        # ONLY AUTHOR NAMES ARE VISIBLE HERE
        # ----------------------------------------------------

        author_list = sorted(
            filtered["Author"]
            .fillna("Unknown Author")
            .astype(str)
            .unique(),
            key=lambda x: x.lower(),
        )

        for author in author_list:

            author_id = safe_id(author)

            author_books = filtered[
                filtered["Author"]
                .fillna("Unknown Author")
                .astype(str)
                == author
            ].copy()

            # -----------------------------------------------
            # AUTHOR DROPDOWN
            # -----------------------------------------------

            with st.expander(
                f"🌿 {author}",
                expanded=False,
            ):

                # -------------------------------------------
                # SERIES FOR THIS AUTHOR
                # -------------------------------------------

                author_books["Series"] = (
                    author_books["Series"]
                    .fillna("Standalone")
                    .replace(
                        ["", "nan", "None"],
                        "Standalone",
                    )
                )

                series_list = sorted(
                    author_books["Series"]
                    .astype(str)
                    .unique(),
                    key=lambda x: x.lower(),
                )

                for series in series_list:

                    series_books = author_books[
                        author_books["Series"].astype(str)
                        == series
                    ].copy()

                    # ---------------------------------------
                    # SERIES DROPDOWN
                    # ---------------------------------------

                    if series == "Standalone":

                        series_label = "📖 Standalone Books"

                    else:

                        series_label = f"📚 {series}"

                    with st.expander(
                        series_label,
                        expanded=False,
                    ):

                        # -----------------------------------
                        # SORT BOOKS BY SERIES NUMBER
                        # -----------------------------------

                        if "Series Number" in series_books.columns:

                            series_books["_sort"] = pd.to_numeric(
                                series_books["Series Number"],
                                errors="coerce",
                            )

                            series_books = (
                                series_books
                                .sort_values(
                                    "_sort",
                                    na_position="last",
                                )
                            )

                        # -----------------------------------
                        # BOOKS
                        # -----------------------------------

                        for _, book in series_books.iterrows():

                            title = str(
                                book.get(
                                    "Title",
                                    "",
                                )
                            )

                            cover = str(
                                book.get(
                                    "Cover",
                                    "",
                                )
                                or ""
                            )

                            status = str(
                                book.get(
                                    "Status",
                                    "",
                                )
                                or ""
                            )

                            genre = str(
                                book.get(
                                    "Genre",
                                    "",
                                )
                                or ""
                            )

                            series_number = book.get(
                                "Series Number",
                                None,
                            )

                            # -------------------------------
                            # BOOK NUMBER
                            # -------------------------------

                            number_text = ""

                            if pd.notna(series_number):

                                try:

                                    number = float(
                                        series_number
                                    )

                                    if number.is_integer():

                                        number_text = (
                                            f"Book {int(number)}"
                                        )

                                    else:

                                        number_text = (
                                            f"Book {number:g}"
                                        )

                                except Exception:

                                    number_text = ""

                            # -------------------------------
                            # BOOK META
                            # -------------------------------

                            meta_parts = []

                            if number_text:
                                meta_parts.append(
                                    number_text
                                )

                            if status:
                                meta_parts.append(
                                    status
                                )

                            if genre:
                                meta_parts.append(
                                    genre
                                )

                            meta = " · ".join(
                                meta_parts
                            )

                            # -------------------------------
                            # DISPLAY BOOK
                            # -------------------------------

                            if cover:

                                st.html(
                                    f"""
                                    <div style="
                                        margin:8px 0 8px 25px;
                                        padding:10px 14px;
                                        background:
                                            linear-gradient(
                                                90deg,
                                                var(--card),
                                                transparent
                                            );
                                        border-left:
                                            2px solid var(--line);
                                        border-radius:
                                            0 12px 0 0;
                                        display:flex;
                                        gap:14px;
                                        align-items:center;
                                    ">

                                        <img
                                            src="{html.escape(cover)}"
                                            style="
                                                width:55px;
                                                height:80px;
                                                object-fit:cover;
                                                border-radius:
                                                    3px 10px 3px 10px;
                                                border:
                                                    1px solid var(--accent);
                                            "
                                        >

                                        <div>

                                            <div style="
                                                font-family:
                                                    'Berkshire Swash',
                                                    Georgia,
                                                    serif;
                                                font-size:20px;
                                                color:var(--text);
                                            ">
                                                📖 {html.escape(title)}
                                            </div>

                                            <div style="
                                                color:var(--muted);
                                                font-family:
                                                    'Libre Baskerville',
                                                    Georgia,
                                                    serif;
                                                font-size:10px;
                                                margin-top:4px;
                                            ">
                                                {html.escape(meta)}
                                            </div>

                                        </div>

                                    </div>
                                    """
                                )

                            else:

                                st.html(
                                    f"""
                                    <div style="
                                        margin:8px 0 8px 25px;
                                        padding:10px 14px;
                                        background:
                                            linear-gradient(
                                                90deg,
                                                var(--card),
                                                transparent
                                            );
                                        border-left:
                                            2px solid var(--line);
                                        border-radius:
                                            0 12px 0 0;
                                    ">

                                        <div style="
                                            font-family:
                                                'Berkshire Swash',
                                                Georgia,
                                                serif;
                                            font-size:20px;
                                            color:var(--text);
                                        ">
                                            📖 {html.escape(title)}
                                        </div>

                                        <div style="
                                            color:var(--muted);
                                            font-family:
                                                'Libre Baskerville',
                                                Georgia,
                                                serif;
                                            font-size:10px;
                                            margin-top:4px;
                                        ">
                                            {html.escape(meta)}
                                        </div>

                                    </div>
                                    """
                                )
```

# ============================================================
# BOOKS TAB
# ============================================================

# ============================================================
# BOOKS TAB
# ============================================================

with books_tab:

    if library.empty:

        st.info("No books yet.")

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
            key="unique_books_radio",
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

        display_ancestry_tree(books)


# ============================================================
# ADD BOOK
# ============================================================
        
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
            placeholder=(
                "Leave blank for standalone"
            ),
        )

        number = st.number_input(
            "Series number",
            min_value=0.0,
            value=0.0,
            step=0.5,
        )

        genre = st.text_input(
            "Genre",
            placeholder=(
                "Fantasy, Romance, Mystery..."
            ),
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
            ],
        )

        rating = st.slider(
            "Rating",
            0,
            5,
            0,
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
                    isbn,
                )

                new_book = {
                    "Title": title.strip(),
                    "Author": author.strip(),
                    "Series": actual_series,
                    "Series Number": (
                        number
                        if number
                        else None
                    ),
                    "Genre": genre.strip(),
                    "ISBN": re.sub(
                        r"\D",
                        "",
                        isbn,
                    ),
                    "My Rating": (
                        rating
                        if rating
                        else None
                    ),
                    "Status": status,
                    "Favorite": favorite,
                    "Cover": cover,
                    "Description": "",
                    "Publisher": "",
                    "Pages": "",
                    "Date Read": "",
                }

                st.session_state.library = (
                    pd.concat(
                        [
                            st.session_state.library,
                            pd.DataFrame(
                                [new_book]
                            ),
                        ],
                        ignore_index=True,
                    )
                )

                st.success(
                    f'"{title}" was added to your tree!'
                )

                st.rerun()


# ============================================================
# IMPORT TAB
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
        type=["csv"],
        key="book_library_uploader",
    )

    if uploaded is not None:

        st.success(
            f"✓ {uploaded.name} uploaded successfully"
        )

        st.caption(
            f"File size: {uploaded.size:,} bytes"
        )

        if st.button(
            "🌳 Build My Book Tree",
            use_container_width=True,
            type="primary",
        ):

            with st.spinner(
                "Reading your book list..."
            ):

                success = import_books(
                    uploaded
                )

            if success:

                st.success(
                    f"✓ Successfully imported "
                    f"{len(st.session_state.library)} books!"
                )

                st.rerun()
