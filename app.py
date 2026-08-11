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

    "Emerald Study": {
        "page": "#061814",
        "surface": "#0D2921",
        "surface2": "#164438",
        "card": "#205A4A",
        "text": "#FFF7DF",
        "muted": "#C5D8CE",
        "accent": "#D8A93A",
        "accent2": "#75B89D",
        "line": "#B9842C",
        "button": "#143A30",
        "button_text": "#FFF7DF",
        "select_bg": "#102E26",
        "select_hover": "#245546",
    },

    "Gilded Midnight": {
        "page": "#070E1D",
        "surface": "#0D1B32",
        "surface2": "#152C4D",
        "card": "#1D3D67",
        "text": "#FFF7DF",
        "muted": "#C5D1E2",
        "accent": "#E4B94F",
        "accent2": "#6EA8D1",
        "line": "#B8862F",
        "button": "#112742",
        "button_text": "#FFF7DF",
        "select_bg": "#10233D",
        "select_hover": "#23466B",
    },

    "Velvet Rose": {
        "page": "#160A13",
        "surface": "#29101F",
        "surface2": "#41172E",
        "card": "#5A2140",
        "text": "#FFF3F5",
        "muted": "#DCC5CF",
        "accent": "#E58A9D",
        "accent2": "#C69BCF",
        "line": "#A94D6C",
        "button": "#351629",
        "button_text": "#FFF3F5",
        "select_bg": "#2A1020",
        "select_hover": "#562642",
    },

    "Autumn Hearth": {
        "page": "#211209",
        "surface": "#37200F",
        "surface2": "#563017",
        "card": "#70401F",
        "text": "#FFF0D5",
        "muted": "#DCC3A0",
        "accent": "#E3A33E",
        "accent2": "#C96A3C",
        "line": "#A9502D",
        "button": "#4A2813",
        "button_text": "#FFF0D5",
        "select_bg": "#3B2110",
        "select_hover": "#68401F",
    },

    "Moonlit Fantasy": {
        "page": "#0A081A",
        "surface": "#14112D",
        "surface2": "#211B4A",
        "card": "#302766",
        "text": "#FFF8E8",
        "muted": "#D0C9E5",
        "accent": "#E6C34D",
        "accent2": "#9276D5",
        "line": "#6851A8",
        "button": "#1C1740",
        "button_text": "#FFF8E8",
        "select_bg": "#171332",
        "select_hover": "#30256A",
    },

    "Enchanted Teal": {
        "page": "#062126",
        "surface": "#0C3840",
        "surface2": "#14545B",
        "card": "#1C6A70",
        "text": "#FFF6DF",
        "muted": "#C7D9D4",
        "accent": "#F0BD4D",
        "accent2": "#F27B65",
        "line": "#D45D4D",
        "button": "#104A52",
        "button_text": "#FFF6DF",
        "select_bg": "#0D3B43",
        "select_hover": "#1E6267",
    },

    "Old World": {
        "page": "#141D1A",
        "surface": "#24332F",
        "surface2": "#354C44",
        "card": "#49635A",
        "text": "#FFF0D2",
        "muted": "#D0D2C2",
        "accent": "#D6A84B",
        "accent2": "#A8B56E",
        "line": "#B37B32",
        "button": "#2C423B",
        "button_text": "#FFF0D2",
        "select_bg": "#273934",
        "select_hover": "#456057",
    },

    "Electric Violet": {
        "page": "#0E0D20",
        "surface": "#171735",
        "surface2": "#242553",
        "card": "#343671",
        "text": "#FFFFFF",
        "muted": "#D0D2EA",
        "accent": "#F3C94D",
        "accent2": "#65D9D3",
        "line": "#A66CDB",
        "button": "#202348",
        "button_text": "#FFFFFF",
        "select_bg": "#1B1D3C",
        "select_hover": "#34366D",
    },

    "Crimson Velvet": {
        "page": "#1E090B",
        "surface": "#341113",
        "surface2": "#52191D",
        "card": "#6A2529",
        "text": "#FFF3DE",
        "muted": "#DCC7B5",
        "accent": "#E4B44B",
        "accent2": "#D2775D",
        "line": "#A83E39",
        "button": "#451519",
        "button_text": "#FFF3DE",
        "select_bg": "#391316",
        "select_hover": "#64272A",
    },
}


# ============================================================
# SESSION STATE
# ============================================================

if (
    "theme" not in st.session_state
    or st.session_state.theme not in THEMES
):
    st.session_state.theme = "Emerald Study"


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

st.html(
    f"""
<style>

@import url(
    'https://fonts.googleapis.com/css2?family=Cormorant+Garamond:wght@500;600;700&family=Libre+Baskerville:wght@400;700'
);


/* ============================================================
   THEME VARIABLES
   ============================================================ */

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
    --button: {theme["button"]};
    --button-text: {theme["button_text"]};
    --select-bg: {theme["select_bg"]};
    --select-hover: {theme["select_hover"]};
}}


/* ============================================================
   PAGE
   ============================================================ */

.stApp {{
    background:
        radial-gradient(
            circle at 10% 0%,
            var(--surface2) 0%,
            var(--page) 48%,
            var(--page) 100%
        ) !important;

    color: var(--text) !important;
}}


.main {{
    background: transparent !important;
}}


.block-container {{
    max-width: 1400px;
    padding-top: 1rem;
    padding-bottom: 4rem;
}}


/* ============================================================
   TYPOGRAPHY
   ============================================================ */

h1, h2, h3, h4 {{
    font-family:
        "Cormorant Garamond",
        Georgia,
        serif !important;

    color: var(--text) !important;
}}


p, label {{
    color: var(--text) !important;
}}


/* ============================================================
   HEADER
   ============================================================ */

.book-header {{
    text-align: center;
    padding: 25px 0 30px;
}}


.book-header-title {{
    font-family:
        "Cormorant Garamond",
        Georgia,
        serif;

    font-size: 68px;
    line-height: .95;
    font-weight: 700;

    color: var(--text);
}}


.book-header-subtitle {{
    font-family:
        "Libre Baskerville",
        Georgia,
        serif;

    color: var(--muted);

    margin-top: 14px;

    font-size: 14px;
    letter-spacing: .04em;
}}


/* ============================================================
   THEME HEADING
   ============================================================ */

.theme-heading {{
    font-family:
        "Cormorant Garamond",
        Georgia,
        serif;

    font-size: 23px;
    font-weight: 700;

    color: var(--text);

    margin-bottom: 5px;
}}


/* ============================================================
   THEME SELECTOR
   ============================================================ */

/* Closed selector */

div[data-baseweb="select"] > div {{
    background: var(--select-bg) !important;

    border: 2px solid var(--accent) !important;

    border-radius: 10px !important;

    min-height: 48px !important;

    box-shadow:
        0 4px 15px rgba(0,0,0,.25) !important;
}}


div[data-baseweb="select"] span {{
    color: var(--text) !important;
    font-weight: 600 !important;
}}


div[data-baseweb="select"] input {{
    color: var(--text) !important;
}}


div[data-baseweb="select"] svg {{
    fill: var(--accent) !important;
}}


/* Open selector */

div[role="listbox"] {{
    background: {theme["select_bg"]} !important;

    border: 2px solid {theme["accent"]} !important;

    border-radius: 10px !important;

    padding: 5px !important;

    box-shadow:
        0 15px 40px rgba(0,0,0,.65) !important;
}}


div[role="option"] {{
    background: {theme["select_bg"]} !important;

    color: {theme["text"]} !important;

    padding: 12px 14px !important;

    border-radius: 7px !important;

    font-family:
        "Libre Baskerville",
        Georgia,
        serif !important;

    font-size: 14px !important;
}}


div[role="option"] *,
div[role="option"] span {{
    color: {theme["text"]} !important;
}}


div[role="option"]:hover {{
    background: {theme["select_hover"]} !important;
}}


div[role="option"][aria-selected="true"] {{
    background: {theme["accent"]} !important;
}}


div[role="option"][aria-selected="true"] *,
div[role="option"][aria-selected="true"] span {{
    color: {theme["page"]} !important;
}}


/* ============================================================
   STATS
   ============================================================ */

.stat-card {{
    background:
        linear-gradient(
            145deg,
            var(--surface2),
            var(--surface)
        );

    border: 1px solid var(--accent);

    border-radius: 12px;

    padding: 14px 8px;

    text-align: center;

    box-shadow:
        0 5px 18px rgba(0,0,0,.18);
}}


.stat-number {{
    font-family:
        "Cormorant Garamond",
        Georgia,
        serif;

    font-size: 34px;

    font-weight: 700;

    color: var(--accent);
}}


.stat-label {{
    color: var(--muted);

    font-family:
        "Libre Baskerville",
        Georgia,
        serif;

    font-size: 10px;

    text-transform: uppercase;

    letter-spacing: .12em;
}}


/* ============================================================
   TREE
   ============================================================ */

.tree-area {{
    margin-top: 25px;

    padding: 30px;

    background:
        linear-gradient(
            145deg,
            rgba(255,255,255,.025),
            rgba(0,0,0,.18)
        );

    border: 1px solid var(--line);

    border-radius: 18px;
}}


/* ============================================================
   ROOT
   ============================================================ */

.root-node {{
    width: 300px;

    margin: 0 auto 38px;

    padding: 18px 25px;

    background:
        linear-gradient(
            135deg,
            var(--accent),
            var(--accent2)
        );

    color: var(--page);

    border-radius: 50px;

    text-align: center;

    box-shadow:
        0 8px 25px rgba(0,0,0,.35);
}}


.root-node-title {{
    color: var(--page);

    font-family:
        "Cormorant Garamond",
        Georgia,
        serif;

    font-size: 32px;

    font-weight: 700;
}}


.root-node-small {{
    color: var(--page);

    font-size: 11px;

    font-weight: 700;

    opacity: .85;
}}


/* ============================================================
   AUTHOR
   ============================================================ */

.author-info {{
    padding: 10px 15px;

    margin: 8px 0;

    border-left:
        4px solid var(--accent);

    background:
        linear-gradient(
            90deg,
            var(--surface),
            rgba(0,0,0,.08)
        );

    border-radius: 0 12px 12px 0;
}}


.author-name {{
    font-family:
        "Cormorant Garamond",
        Georgia,
        serif;

    font-size: 27px;

    font-weight: 700;

    color: var(--text);
}}


.author-count {{
    color: var(--muted);

    font-size: 11px;
}}


/* ============================================================
   SERIES
   ============================================================ */

.series-info {{
    margin-left: 48px;

    padding: 10px 15px;

    border-left:
        3px solid var(--accent2);

    background: var(--surface2);

    border-radius: 0 10px 10px 0;
}}


.series-name {{
    font-family:
        "Cormorant Garamond",
        Georgia,
        serif;

    font-size: 23px;

    font-weight: 700;

    color: var(--text);
}}


.series-count {{
    color: var(--muted);

    font-size: 11px;
}}


/* ============================================================
   BOOK
   ============================================================ */

.book-info {{
    margin-left: 100px;

    margin-top: 8px;

    padding: 10px 14px;

    background:
        linear-gradient(
            135deg,
            var(--card),
            var(--surface2)
        );

    border-left:
        2px solid var(--line);

    border-radius: 0 10px 10px 0;
}}


.book-title {{
    font-family:
        "Cormorant Garamond",
        Georgia,
        serif;

    font-size: 21px;

    font-weight: 700;

    color: var(--text);
}}


.book-meta {{
    color: var(--muted);

    font-size: 11px;

    margin-top: 3px;
}}


.book-cover {{
    width: 55px;
    height: 80px;

    object-fit: cover;

    border-radius: 4px;

    border:
        1px solid var(--accent);

    box-shadow:
        0 4px 10px rgba(0,0,0,.3);
}}


/* ============================================================
   BUTTONS
   ============================================================ */

.stButton > button {{
    background:
        linear-gradient(
            135deg,
            var(--button),
            var(--surface)
        ) !important;

    color: var(--button-text) !important;

    border:
        1px solid var(--line) !important;

    border-radius:
        9px !important;

    font-weight:
        600 !important;

    transition:
        all .15s ease !important;
}}


.stButton > button:hover {{
    background:
        linear-gradient(
            135deg,
            var(--surface2),
            var(--card)
        ) !important;

    border-color:
        var(--accent) !important;

    color:
        var(--text) !important;

    transform:
        translateY(-1px);
}}


/* ============================================================
   INPUTS
   ============================================================ */

div[data-baseweb="input"] > div {{
    background:
        var(--surface) !important;

    border:
        1px solid var(--line) !important;

    border-radius:
        8px !important;
}}


div[data-baseweb="input"] input {{
    color:
        var(--text) !important;
}}


div[data-baseweb="input"] input::placeholder {{
    color:
        var(--muted) !important;

    opacity:
        .8 !important;
}}


textarea {{
    background:
        var(--surface) !important;

    color:
        var(--text) !important;

    border-color:
        var(--line) !important;
}}


/* ============================================================
   RADIO BUTTONS
   ============================================================ */

div[role="radiogroup"] label {{
    color: var(--text) !important;
}}


/* ============================================================
   CHECKBOX
   ============================================================ */

div[data-testid="stCheckbox"] label {{
    color: var(--text) !important;
}}


/* ============================================================
   TABS
   ============================================================ */

button[data-baseweb="tab"] {{
    color: var(--muted) !important;

    font-family:
        "Libre Baskerville",
        Georgia,
        serif !important;
}}


button[data-baseweb="tab"][aria-selected="true"] {{
    color: var(--accent) !important;
}}


/* ============================================================
   DIVIDERS
   ============================================================ */

hr {{
    border-color:
        var(--line) !important;
    opacity: .5;
}}


/* ============================================================
   FILE UPLOADER
   ============================================================ */

[data-testid="stFileUploader"] section {{
    background:
        var(--surface) !important;

    border:
        1px dashed var(--line) !important;

    border-radius:
        10px !important;
}}


/* ============================================================
   FORM
   ============================================================ */

[data-testid="stForm"] {{
    background:
        var(--surface) !important;

    border:
        1px solid var(--line) !important;

    border-radius:
        14px !important;

    padding:
        20px !important;
}}


/* ============================================================
   PROGRESS BAR
   ============================================================ */

div[data-testid="stProgressBar"] > div > div {{
    background:
        var(--accent) !important;
}}


/* ============================================================
   ALERTS
   ============================================================ */

div[data-testid="stAlert"] {{
    border-radius:
        10px !important;
}}


/* ============================================================
   MOBILE
   ============================================================ */

@media (max-width: 700px) {{

    .book-header-title {{
        font-size: 48px;
    }}

    .tree-area {{
        padding: 15px;
    }}

    .root-node {{
        width: 90%;
    }}

    .book-info {{
        margin-left: 45px;
    }}

    .series-info {{
        margin-left: 25px;
    }}

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

        <div class="book-header-title">
            My Book Tree
        </div>

        <div class="book-header-subtitle">
            Your books, connected from author to series to story.
        </div>

    </div>
    """
)


# ============================================================
# THEME PICKER
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

    isbn = re.sub(
        r"\D",
        "",
        str(isbn)
    )

    # --------------------------------------------------------
    # ISBN COVER
    # --------------------------------------------------------

    if isbn:

        url = (
            "https://covers.openlibrary.org/b/isbn/"
            f"{isbn}-L.jpg"
        )

        try:

            r = requests.get(
                url,
                timeout=8
            )

            if (
                r.status_code == 200
                and len(r.content) > 1000
            ):

                return url

        except Exception:
            pass

    # --------------------------------------------------------
    # OPEN LIBRARY SEARCH
    # --------------------------------------------------------

    try:

        r = requests.get(
            "https://openlibrary.org/search.json",
            params={
                "title": title,
                "author": author,
                "limit": 1,
            },
            timeout=10,
        )

        if r.status_code == 200:

            docs = r.json().get(
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

    # --------------------------------------------------------
    # GOOGLE BOOKS
    # --------------------------------------------------------

    try:

        r = requests.get(
            "https://www.googleapis.com/books/v1/volumes",
            params={
                "q": f"{title} {author}",
                "maxResults": 1,
            },
            timeout=10,
        )

        if r.status_code == 200:

            items = r.json().get(
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
# SERIES HELPERS
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
            re.I
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


def safe_id(text):

    return re.sub(
        r"[^a-zA-Z0-9_-]",
        "_",
        str(text)
    )


# ============================================================
# IMPORT
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

        return None

    title_col = find_column(
        ["title", "book title"]
    )

    author_col = find_column(
        ["author", "authors"]
    )

    isbn_col = find_column(
        ["isbn13", "isbn"]
    )

    rating_col = find_column(
        ["my rating", "rating"]
    )

    shelf_col = find_column(
        [
            "exclusive shelf",
            "shelf",
            "status"
        ]
    )

    if not title_col:

        st.error(
            "I couldn't find a Title column in this CSV."
        )

        return False

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

        # ----------------------------------------------------
        # AUTHOR
        # ----------------------------------------------------

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

        # ----------------------------------------------------
        # ISBN
        # ----------------------------------------------------

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

        # ----------------------------------------------------
        # RATING
        # ----------------------------------------------------

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

        # ----------------------------------------------------
        # STATUS
        # ----------------------------------------------------

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

        # ----------------------------------------------------
        # BOOK
        # ----------------------------------------------------

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
            "No books were found in the file."
        )

        return False

    # --------------------------------------------------------
    # FIND COVERS
    # --------------------------------------------------------

    progress = st.progress(0)

    for i in range(
        len(new_library)
    ):

        new_library.loc[
            i,
            "Cover"
        ] = get_cover(
            new_library.loc[i, "Title"],
            new_library.loc[i, "Author"],
            new_library.loc[i, "ISBN"]
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
# DATA
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


favorites = (
    len(
        library[
            library["Favorite"] == True
        ]
    )
    if total
    else 0
)


# ============================================================
# STATS
# ============================================================

columns = st.columns(5)


stats = [
    (total, "Books"),
    (authors, "Authors"),
    (series_count, "Series"),
    (read_count, "Read"),
    (favorites, "Favorites"),
]


for col, (number, label) in zip(
    columns,
    stats
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
# TREE
# ============================================================

with tree_tab:

    if library.empty:

        st.info(
            "Your tree is empty. "
            "Import your library or add your first book."
        )

    else:

        search = st.text_input(
            "Search your tree",
            placeholder=(
                "Search author, series, or book..."
            )
        )

        filtered = library.copy()

        if search:

            q = search.lower()

            filtered = filtered[
                filtered["Title"]
                .fillna("")
                .astype(str)
                .str.lower()
                .str.contains(
                    q,
                    na=False
                )
                |
                filtered["Author"]
                .fillna("")
                .astype(str)
                .str.lower()
                .str.contains(
                    q,
                    na=False
                )
                |
                filtered["Series"]
                .fillna("")
                .astype(str)
                .str.lower()
                .str.contains(
                    q,
                    na=False
                )
            ]

        # ----------------------------------------------------
        # ROOT
        # ----------------------------------------------------

        st.html(
            f"""
            <div class="tree-area">

                <div class="root-node">

                    <div class="root-node-title">
                        My Library
                    </div>

                    <div class="root-node-small">
                        {len(filtered)} books ·
                        {filtered["Author"].nunique()} authors
                    </div>

                </div>

            </div>
            """
        )

        # ----------------------------------------------------
        # AUTHORS
        # ----------------------------------------------------

        author_list = sorted(
            filtered["Author"]
            .fillna("Unknown Author")
            .astype(str)
            .unique(),
            key=lambda x: x.lower()
        )

        for author in author_list:

            author_id = safe_id(
                author
            )

            author_books = filtered[
                filtered["Author"]
                .fillna("Unknown Author")
                .astype(str)
                == author
            ]

            opened = (
                author_id
                in st.session_state.open_authors
            )

            arrow = "▼" if opened else "▶"

            if st.button(
                f"{arrow}  {author}",
                key=f"author_{author_id}",
                use_container_width=True,
            ):

                if opened:

                    st.session_state.open_authors.discard(
                        author_id
                    )

                else:

                    st.session_state.open_authors.add(
                        author_id
                    )

                st.rerun()

            st.html(
                f"""
                <div class="author-info">

                    <div class="author-name">
                        {html.escape(author)}
                    </div>

                    <div class="author-count">
                        {len(author_books)}
                        {"book" if len(author_books) == 1 else "books"}
                    </div>

                </div>
                """
            )

            if not opened:
                continue

            # ------------------------------------------------
            # SERIES
            # ------------------------------------------------

            series_list = sorted(
                author_books["Series"]
                .fillna("Standalone")
                .astype(str)
                .unique(),
                key=lambda x: x.lower()
            )

            for series in series_list:

                # --------------------------------------------
                # STANDALONE
                # --------------------------------------------

                if series == "Standalone":

                    standalone_books = author_books[
                        author_books["Series"]
                        .fillna("Standalone")
                        .astype(str)
                        == "Standalone"
                    ]

                    st.html(
                        f"""
                        <div class="series-info">

                            <div class="series-name">
                                Standalone Books
                            </div>

                            <div class="series-count">
                                {len(standalone_books)}
                                {"book" if len(standalone_books) == 1 else "books"}
                            </div>

                        </div>
                        """
                    )

                    for _, book in standalone_books.iterrows():

                        cover = str(
                            book.get(
                                "Cover",
                                ""
                            ) or ""
                        )

                        title = html.escape(
                            str(
                                book.get(
                                    "Title",
                                    ""
                                )
                            )
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

                            st.html(
                                f"""
                                <div class="book-info">

                                    <div style="
                                        display:flex;
                                        gap:14px;
                                        align-items:center;
                                    ">

                                        <img
                                            class="book-cover"
                                            src="{html.escape(cover)}"
                                        >

                                        <div>

                                            <div class="book-title">
                                                {title}
                                            </div>

                                            <div class="book-meta">
                                                {status}
                                            </div>

                                        </div>

                                    </div>

                                </div>
                                """
                            )

                        else:

                            st.html(
                                f"""
                                <div class="book-info">

                                    <div class="book-title">
                                        {title}
                                    </div>

                                    <div class="book-meta">
                                        {status}
                                    </div>

                                </div>
                                """
                            )

                    continue

                # --------------------------------------------
                # SERIES ID
                # --------------------------------------------

                series_id = (
                    author_id
                    + "::"
                    + safe_id(series)
                )

                series_open = (
                    series_id
                    in st.session_state.open_series
                )

                arrow = (
                    "▼"
                    if series_open
                    else "▶"
                )

                if st.button(
                    f"{arrow}  {series}",
                    key=f"series_{series_id}",
                    use_container_width=True,
                ):

                    if series_open:

                        st.session_state.open_series.discard(
                            series_id
                        )

                    else:

                        st.session_state.open_series.add(
                            series_id
                        )

                    st.rerun()

                series_books = author_books[
                    author_books["Series"]
                    .fillna("Standalone")
                    .astype(str)
                    == series
                ].copy()

                st.html(
                    f"""
                    <div class="series-info">

                        <div class="series-name">
                            {html.escape(series)}
                        </div>

                        <div class="series-count">
                            {len(series_books)}
                            {"book" if len(series_books) == 1 else "books"}
                        </div>

                    </div>
                    """
                )

                if not series_open:
                    continue

                # --------------------------------------------
                # SORT SERIES
                # --------------------------------------------

                series_books = series_books.sort_values(
                    by=[
                        "Series Number",
                        "Title"
                    ],
                    na_position="last"
                )

                # --------------------------------------------
                # BOOKS
                # --------------------------------------------

                for position, (_, book) in enumerate(
                    series_books.iterrows(),
                    1
                ):

                    number = book.get(
                        "Series Number"
                    )

                    if pd.notna(number):

                        try:

                            if float(number).is_integer():

                                number_text = (
                                    f"Book {int(number)}"
                                )

                            else:

                                number_text = (
                                    f"Book {number}"
                                )

                        except Exception:

                            number_text = (
                                f"Book {position}"
                            )

                    else:

                        number_text = (
                            f"Book {position}"
                        )

                    cover = str(
                        book.get(
                            "Cover",
                            ""
                        ) or ""
                    )

                    title = html.escape(
                        str(
                            book.get(
                                "Title",
                                ""
                            )
                        )
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

                        st.html(
                            f"""
                            <div class="book-info">

                                <div style="
                                    display:flex;
                                    gap:14px;
                                    align-items:center;
                                ">

                                    <img
                                        class="book-cover"
                                        src="{html.escape(cover)}"
                                    >

                                    <div>

                                        <div class="book-title">
                                            {number_text}
                                            ·
                                            {title}
                                        </div>

                                        <div class="book-meta">
                                            {status}
                                        </div>

                                    </div>

                                </div>

                            </div>
                            """
                        )

                    else:

                        st.html(
                            f"""
                            <div class="book-info">

                                <div class="book-title">
                                    {number_text}
                                    ·
                                    {title}
                                </div>

                                <div class="book-meta">
                                    {status}
                                </div>

                            </div>
                            """
                        )


# ============================================================
# BOOKS
# ============================================================

with books_tab:

    if library.empty:

        st.info(
            "No books yet."
        )

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

        for index, book in books.iterrows():

            col1, col2, col3 = st.columns(
                [1, 6, 1]
            )

            with col1:

                if book.get("Cover"):

                    st.image(
                        book["Cover"],
                        width=70
                    )

            with col2:

                st.html(
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
                    </div>
                    """
                )

            with col3:

                favorite = st.checkbox(
                    "♥",
                    value=bool(
                        book.get(
                            "Favorite",
                            False
                        )
                    ),
                    key=f"fav_{index}",
                )

                if favorite != bool(
                    book.get(
                        "Favorite",
                        False
                    )
                ):

                    st.session_state.library.loc[
                        index,
                        "Favorite"
                    ] = favorite

                    st.rerun()


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
            placeholder="Leave blank for standalone"
        )

        number = st.number_input(
            "Series number",
            min_value=0.0,
            value=0.0,
            step=.5
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
            ]
        )

        rating = st.slider(
            "Rating",
            0,
            5,
            0
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
                    isbn
                )

                new_book = {
                    "Title": title.strip(),
                    "Author": author.strip(),
                    "Series": actual_series,
                    "Series Number":
                        number
                        if number
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
                }

                st.session_state.library = pd.concat(
                    [
                        st.session_state.library,
                        pd.DataFrame(
                            [new_book]
                        ),
                    ],
                    ignore_index=True
                )

                st.success(
                    f'"{title}" was added to your tree!'
                )

                st.rerun()


# ============================================================
# IMPORT
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
        type=["csv"]
    )

    if uploaded:

        if st.button(
            "Build My Book Tree"
        ):

            with st.spinner(
                "Finding your books and covers..."
            ):

                success = import_books(
                    uploaded
                )

            if success:

                st.success(
                    "Your book tree is ready!"
                )

                st.rerun()
