```python
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
    page_icon="🌿",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ============================================================
# BOOKISH THEMES
# ============================================================

THEMES = {

    "Enchanted Garden": {
        "page": "#101914",
        "surface": "#18261F",
        "surface2": "#22372C",
        "card": "#2B4436",
        "text": "#F8EFD8",
        "muted": "#C8CDBE",
        "accent": "#D6AF5A",
        "accent2": "#8FA77C",
        "line": "#9C7540",
    },

    "Midnight Rose": {
        "page": "#170D17",
        "surface": "#241324",
        "surface2": "#351A32",
        "card": "#48233F",
        "text": "#FFF0E8",
        "muted": "#D8BCCB",
        "accent": "#D9A35F",
        "accent2": "#B97891",
        "line": "#8F4F68",
    },

    "Velvet & Gold": {
        "page": "#1B1010",
        "surface": "#2B1617",
        "surface2": "#421D20",
        "card": "#57272A",
        "text": "#FFF1D7",
        "muted": "#D9C3A6",
        "accent": "#D7AA50",
        "accent2": "#B97962",
        "line": "#95612E",
    },

    "Blue Fairy Tale": {
        "page": "#0C1521",
        "surface": "#142338",
        "surface2": "#1D3450",
        "card": "#294867",
        "text": "#F8F1DE",
        "muted": "#C4CFDB",
        "accent": "#D7B45D",
        "accent2": "#82A9C4",
        "line": "#637F9B",
    },

    "Autumn Storybook": {
        "page": "#21130D",
        "surface": "#322016",
        "surface2": "#4A2B1C",
        "card": "#63402A",
        "text": "#FFF0D2",
        "muted": "#D6BFA0",
        "accent": "#D9A24E",
        "accent2": "#B96F4E",
        "line": "#8D5835",
    },

    "Secret Library": {
        "page": "#111615",
        "surface": "#1B2522",
        "surface2": "#283630",
        "card": "#35483F",
        "text": "#F6EED9",
        "muted": "#C7CEC4",
        "accent": "#C9A457",
        "accent2": "#849B87",
        "line": "#657A68",
    },

    "Victorian Rose": {
        "page": "#190E12",
        "surface": "#29151C",
        "surface2": "#3D202B",
        "card": "#552A39",
        "text": "#FFF0E7",
        "muted": "#DCC3C8",
        "accent": "#D4A15D",
        "accent2": "#B97886",
        "line": "#8F5063",
    },

    "Moonlit Garden": {
        "page": "#10101D",
        "surface": "#18192B",
        "surface2": "#272846",
        "card": "#38385D",
        "text": "#F8F0DE",
        "muted": "#CAC9D7",
        "accent": "#D6B76A",
        "accent2": "#8C89B7",
        "line": "#65638C",
    },
}

# ============================================================
# SESSION STATE
# ============================================================

if (
    "theme" not in st.session_state
    or st.session_state.theme not in THEMES
):
    st.session_state.theme = "Enchanted Garden"

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
    'https://fonts.googleapis.com/css2?family=Cormorant+Garamond:wght@500;600;700&family=Libre+Baskerville:wght@400;700&family=Italianno&display=swap'
);

/* ============================================================
   ROOT
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
}}

.stApp {{
    background:
        radial-gradient(
            ellipse at 50% -10%,
            var(--surface2) 0%,
            var(--page) 58%
        ) !important;

    color: var(--text);
}}

.block-container {{
    max-width: 1450px;
    padding-top: 0.8rem;
    padding-bottom: 4rem;
}}

/* ============================================================
   GENERAL TYPOGRAPHY
   ============================================================ */

h1, h2, h3, h4 {{
    font-family:
        "Cormorant Garamond",
        Georgia,
        serif !important;

    color: var(--text) !important;
}}

p, label {{
    color: var(--text);
}}

/* ============================================================
   HEADER
   ============================================================ */

.book-header {{
    text-align: center;
    padding:
        18px 0 0;
    position: relative;
}}

.book-header-title {{
    font-family:
        "Cormorant Garamond",
        Georgia,
        serif;

    font-size: 78px;
    line-height: .9;
    font-weight: 700;

    letter-spacing: .015em;

    color: var(--text);

    text-shadow:
        0 2px 12px rgba(0,0,0,.35);
}}

/* ornamental line under title */

.header-ornament {{
    display: flex;
    align-items: center;
    justify-content: center;

    gap: 13px;

    margin:
        12px auto 0;

    max-width: 700px;

    color: var(--accent);
}}

.header-ornament::before,
.header-ornament::after {{
    content: "";
    height: 1px;
    flex: 1;

    background:
        linear-gradient(
            90deg,
            transparent,
            var(--accent)
        );
}}

.header-ornament::after {{
    background:
        linear-gradient(
            90deg,
            var(--accent),
            transparent
        );
}}

.header-ornament-center {{
    font-family:
        "Cormorant Garamond",
        Georgia,
        serif;

    font-size: 22px;
    color: var(--accent);
}}

/* ============================================================
   THEME AREA
   ============================================================ */

.theme-heading {{
    font-family:
        "Cormorant Garamond",
        Georgia,
        serif;

    font-size: 25px;
    font-weight: 700;

    color: var(--text);

    margin:
        22px 0 5px;
}}

div[data-baseweb="select"] > div {{
    background:
        rgba(0,0,0,.18) !important;

    border:
        1px solid var(--line) !important;

    border-radius:
        4px !important;

    min-height:
        45px !important;

    box-shadow:
        0 5px 18px rgba(0,0,0,.15);
}}

div[data-baseweb="select"] span {{
    color: var(--text) !important;
}}

div[data-baseweb="select"] input {{
    color: var(--text) !important;
}}

div[role="listbox"] {{
    background:
        var(--surface) !important;

    border:
        1px solid var(--accent) !important;

    border-radius:
        4px !important;

    box-shadow:
        0 18px 45px rgba(0,0,0,.55) !important;
}}

div[role="option"] {{
    background:
        var(--surface) !important;

    color:
        var(--text) !important;

    font-family:
        "Libre Baskerville",
        Georgia,
        serif !important;

    padding:
        12px 15px !important;
}}

div[role="option"]:hover {{
    background:
        var(--surface2) !important;
}}

div[role="option"][aria-selected="true"] {{
    background:
        var(--card) !important;

    color:
        var(--accent) !important;
}}

/* ============================================================
   STATS
   ============================================================ */

.stat-card {{
    position: relative;

    background:
        linear-gradient(
            145deg,
            rgba(255,255,255,.025),
            rgba(0,0,0,.13)
        );

    border:
        none;

    border-top:
        1px solid var(--line);

    border-bottom:
        1px solid var(--line);

    padding:
        13px 8px 12px;

    text-align:
        center;

    box-shadow:
        0 7px 22px rgba(0,0,0,.12);
}}

.stat-card::before {{
    content: "✦";

    position: absolute;
    top: -10px;
    left: 50%;

    transform: translateX(-50%);

    background:
        var(--page);

    padding:
        0 8px;

    color:
        var(--accent);

    font-size:
        13px;
}}

.stat-number {{
    font-family:
        "Cormorant Garamond",
        Georgia,
        serif;

    font-size:
        38px;

    font-weight:
        700;

    color:
        var(--accent);
}}

.stat-label {{
    color:
        var(--muted);

    font-family:
        "Libre Baskerville",
        Georgia,
        serif;

    font-size:
        9px;

    text-transform:
        uppercase;

    letter-spacing:
        .16em;
}}

/* ============================================================
   TREE AREA
   ============================================================ */

.tree-area {{
    margin-top:
        25px;

    padding:
        30px 30px 36px;

    position:
        relative;

    background:
        rgba(0,0,0,.10);

    border:
        1px solid rgba(255,255,255,.05);

    box-shadow:
        inset 0 0 55px rgba(0,0,0,.12);
}}

/* ============================================================
   ROOT NODE
   ============================================================ */

.root-node {{
    width:
        320px;

    margin:
        0 auto 42px;

    padding:
        17px 25px;

    background:
        linear-gradient(
            135deg,
            var(--accent),
            #B9863B
        );

    color:
        var(--page);

    text-align:
        center;

    position:
        relative;

    box-shadow:
        0 10px 28px rgba(0,0,0,.28);

    border-radius:
        3px;
}}

.root-node::before,
.root-node::after {{
    content: "❦";

    position: absolute;

    top: 50%;

    transform:
        translateY(-50%);

    color:
        var(--page);

    font-size:
        20px;
}}

.root-node::before {{
    left:
        14px;
}}

.root-node::after {{
    right:
        14px;
}}

.root-node-title {{
    color:
        var(--page);

    font-family:
        "Cormorant Garamond",
        Georgia,
        serif;

    font-size:
        34px;

    font-weight:
        700;
}}

.root-node-small {{
    color:
        var(--page);

    font-family:
        "Libre Baskerville",
        Georgia,
        serif;

    font-size:
        10px;

    opacity:
        .78;
}}

/* ============================================================
   STREAMLIT BUTTONS USED FOR TREE CONTROLS
   ============================================================ */

.stButton > button {{
    background:
        transparent !important;

    color:
        var(--text) !important;

    border:
        none !important;

    border-bottom:
        1px solid rgba(255,255,255,.06) !important;

    border-radius:
        0 !important;

    text-align:
        left !important;

    font-family:
        "Cormorant Garamond",
        Georgia,
        serif !important;

    font-size:
        19px !important;

    font-weight:
        600 !important;

    min-height:
        40px !important;

    transition:
        all .2s ease !important;
}}

.stButton > button:hover {{
    background:
        rgba(255,255,255,.035) !important;

    color:
        var(--accent) !important;

    border-bottom-color:
        var(--line) !important;
}}

/* ============================================================
   AUTHOR
   ============================================================ */

.author-info {{
    padding:
        10px 15px 9px 18px;

    margin:
        4px 0 5px;

    border-left:
        2px solid var(--accent);

    background:
        linear-gradient(
            90deg,
            rgba(255,255,255,.035),
            transparent
        );

    position:
        relative;
}}

.author-info::before {{
    content:
        "❧";

    position:
        absolute;

    left:
        -11px;

    top:
        7px;

    color:
        var(--accent);

    background:
        var(--page);

    font-size:
        15px;
}}

.author-name {{
    font-family:
        "Cormorant Garamond",
        Georgia,
        serif;

    font-size:
        29px;

    font-weight:
        700;

    letter-spacing:
        .01em;
}}

.author-count {{
    color:
        var(--muted);

    font-family:
        "Libre Baskerville",
        Georgia,
        serif;

    font-size:
        10px;

    margin-top:
        2px;
}}

/* ============================================================
   SERIES
   ============================================================ */

.series-info {{
    margin-left:
        50px;

    padding:
        9px 15px 8px;

    border-left:
        1px solid var(--accent2);

    background:
        linear-gradient(
            90deg,
            rgba(255,255,255,.025),
            transparent
        );

    position:
        relative;
}}

.series-info::before {{
    content:
        "❧";

    position:
        absolute;

    left:
        -9px;

    top:
        7px;

    color:
        var(--accent2);

    background:
        var(--page);

    font-size:
        13px;
}}

.series-name {{
    font-family:
        "Cormorant Garamond",
        Georgia,
        serif;

    font-size:
        24px;

    font-weight:
        700;

    color:
        var(--accent2);
}}

.series-count {{
    color:
        var(--muted);

    font-family:
        "Libre Baskerville",
        Georgia,
        serif;

    font-size:
        10px;
}}

/* ============================================================
   BOOK
   ============================================================ */

.book-info {{
    margin-left:
        102px;

    margin-top:
        6px;

    padding:
        9px 14px;

    background:
        rgba(255,255,255,.025);

    border-left:
        1px solid var(--line);

    position:
        relative;
}}

.book-info::before {{
    content:
        "•";

    position:
        absolute;

    left:
        -5px;

    top:
        8px;

    color:
        var(--accent);

    background:
        var(--page);

    line-height:
        1;
}}

.book-title {{
    font-family:
        "Cormorant Garamond",
        Georgia,
        serif;

    font-size:
        21px;

    font-weight:
        700;

    color:
        var(--text);
}}

.book-meta {{
    color:
        var(--muted);

    font-family:
        "Libre Baskerville",
        Georgia,
        serif;

    font-size:
        10px;

    margin-top:
        3px;
}}

.book-cover {{
    width:
        55px;

    height:
        80px;

    object-fit:
        cover;

    border-radius:
        2px;

    border:
        1px solid var(--line);

    box-shadow:
        4px 5px 12px rgba(0,0,0,.3);
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
        3px !important;
}}

div[data-baseweb="input"] input {{
    color:
        var(--text) !important;
}}

textarea {{
    background:
        var(--surface) !important;

    color:
        var(--text) !important;
}}

.stTextInput label,
.stSelectbox label,
.stNumberInput label,
.stSlider label,
.stCheckbox label {{
    font-family:
        "Libre Baskerville",
        Georgia,
        serif !important;

    color:
        var(--muted) !important;
}}

/* ============================================================
   TABS
   ============================================================ */

button[data-baseweb="tab"] {{
    font-family:
        "Cormorant Garamond",
        Georgia,
        serif !important;

    font-size:
        18px !important;

    color:
        var(--muted) !important;
}}

button[data-baseweb="tab"][aria-selected="true"] {{
    color:
        var(--accent) !important;
}}

div[data-baseweb="tab-highlight"] {{
    background:
        var(--accent) !important;
}}

/* ============================================================
   RADIO
   ============================================================ */

div[role="radiogroup"] label {{
    color:
        var(--text) !important;

    font-family:
        "Cormorant Garamond",
        Georgia,
        serif !important;

    font-size:
        16px !important;
}}

/* ============================================================
   FORM
   ============================================================ */

.stForm {{
    border:
        none !important;

    background:
        rgba(255,255,255,.025) !important;

    padding:
        25px !important;

    box-shadow:
        0 10px 35px rgba(0,0,0,.12);
}}

/* ============================================================
   SUCCESS / INFO
   ============================================================ */

div[data-testid="stAlert"] {{
    background:
        var(--surface) !important;

    border:
        1px solid var(--line) !important;

    color:
        var(--text) !important;
}}

/* ============================================================
   DIVIDER
   ============================================================ */

hr {{
    border:
        none !important;

    border-top:
        1px solid var(--line) !important;

    opacity:
        .55;
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

    <div class="header-ornament">
        <div class="header-ornament-center">❦</div>
    </div>

</div>
"""
)

# ============================================================
# THEME PICKER
# ============================================================

st.html(
    '<div class="theme-heading">Choose your storybook world</div>'
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

        if not title or title.lower() == "nan":
            continue

        author = "Unknown Author"

        if author_col:

            author = str(
                row.get(
                    author_col,
                    ""
                )
            ).strip()

        if not author or author.lower() == "nan":
            author = "Unknown Author"

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
            "No books were found in the file."
        )

        return False

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
        "🌿 Book Tree",
        "📖 Books",
        "✦ Add Book",
        "❧ Import",
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
                .str.contains(q, na=False)
                |
                filtered["Author"]
                .fillna("")
                .astype(str)
                .str.lower()
                .str.contains(q, na=False)
                |
                filtered["Series"]
                .fillna("")
                .astype(str)
                .str.lower()
                .str.contains(q, na=False)
            ]

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

        author_list = sorted(
            filtered["Author"]
            .fillna("Unknown Author")
            .astype(str)
            .unique(),
            key=lambda x: x.lower()
        )

        for author in author_list:

            author_id = safe_id(author)

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

            series_list = sorted(
                author_books["Series"]
                .fillna("Standalone")
                .astype(str)
                .unique(),
                key=lambda x: x.lower()
            )

            for series in series_list:

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
                                                {html.escape(
                                                    str(
                                                        book.get(
                                                            "Status",
                                                            ""
                                                        )
                                                    )
                                                )}
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
                                        {html.escape(
                                            str(
                                                book.get(
                                                    "Status",
                                                    ""
                                                )
                                            )
                                        )}
                                    </div>

                                </div>
                                """
                            )

                    continue

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

                series_books = series_books.sort_values(
                    by=[
                        "Series Number",
                        "Title"
                    ],
                    na_position="last"
                )

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
                                            {html.escape(
                                                str(
                                                    book.get(
                                                        "Status",
                                                        ""
                                                    )
                                                )
                                            )}
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
                                    {html.escape(
                                        str(
                                            book.get(
                                                "Status",
                                                ""
                                            )
                                        )
                                    )}
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
```
