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
# WHIMSICAL BOOKISH THEMES
# ============================================================

THEMES = {

    "Enchanted Garden": {
        "page": "#17120F",
        "surface": "#211A16",
        "surface2": "#30251F",
        "card": "#3A2D24",
        "text": "#F8EBD1",
        "muted": "#CBBDA7",
        "accent": "#D8AE68",
        "accent2": "#78906A",
        "line": "#9C7950",
    },

    "Roses & Old Books": {
        "page": "#1B1015",
        "surface": "#29171E",
        "surface2": "#3B202B",
        "card": "#4A2834",
        "text": "#F8E7DC",
        "muted": "#D5BFC0",
        "accent": "#D59A9F",
        "accent2": "#9C7180",
        "line": "#A66A72",
    },

    "Moonlit Library": {
        "page": "#101522",
        "surface": "#181F30",
        "surface2": "#252D43",
        "card": "#303951",
        "text": "#F4EBD5",
        "muted": "#C4C8D0",
        "accent": "#D8B878",
        "accent2": "#7888A7",
        "line": "#857A66",
    },

    "Autumn Storybook": {
        "page": "#21150F",
        "surface": "#2D1D14",
        "surface2": "#432A1B",
        "card": "#56351F",
        "text": "#F7E6C8",
        "muted": "#D3BFA0",
        "accent": "#D49A50",
        "accent2": "#9C694B",
        "line": "#9C6039",
    },

    "Velvet & Violets": {
        "page": "#17111D",
        "surface": "#25182D",
        "surface2": "#362342",
        "card": "#493058",
        "text": "#F5E9DC",
        "muted": "#CFC0D3",
        "accent": "#C9A3C9",
        "accent2": "#84729A",
        "line": "#8F6B8D",
    },

    "Secret Conservatory": {
        "page": "#101A17",
        "surface": "#182722",
        "surface2": "#263B33",
        "card": "#355044",
        "text": "#F4E9D2",
        "muted": "#C2CDBF",
        "accent": "#D5B56B",
        "accent2": "#78977F",
        "line": "#71846B",
    },

    "Gothic Romance": {
        "page": "#160D12",
        "surface": "#24131B",
        "surface2": "#351C28",
        "card": "#482536",
        "text": "#F8E8E1",
        "muted": "#D0B9BC",
        "accent": "#C98A91",
        "accent2": "#92708A",
        "line": "#895362",
    },

    "Fairytale Library": {
        "page": "#16141B",
        "surface": "#24202A",
        "surface2": "#332E3C",
        "card": "#433B4D",
        "text": "#F8EEDC",
        "muted": "#C9C2C5",
        "accent": "#D9B875",
        "accent2": "#8D879F",
        "line": "#89765C",
    },

    "Wildflower & Ink": {
        "page": "#141817",
        "surface": "#1D2421",
        "surface2": "#2A3530",
        "card": "#39453E",
        "text": "#F4EBD8",
        "muted": "#C4C8BA",
        "accent": "#D0AA67",
        "accent2": "#829477",
        "line": "#777D63",
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

@import url('https://fonts.googleapis.com/css2?family=Cormorant+Garamond:wght@400;500;600;700&family=Libre+Baskerville:wght@400;700&family=Italianno&display=swap');

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

/* ============================================================
   PAGE
   ============================================================ */

.stApp {{
    background:
        radial-gradient(
            ellipse at 50% -10%,
            var(--surface2) 0%,
            var(--page) 58%
        );
    color: var(--text);
}}

.block-container {{
    max-width: 1450px;
    padding-top: 1rem;
    padding-bottom: 4rem;
}}

p, label, span {{
    color: var(--text);
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

.book-header {{
    position: relative;
    text-align: center;
    padding: 35px 0 25px;
}}

.book-header::before,
.book-header::after {{
    content: "❦";
    position: absolute;
    top: 43px;
    color: var(--accent);
    font-size: 25px;
    opacity: .75;
}}

.book-header::before {{
    left: 25%;
}}

.book-header::after {{
    right: 25%;
}}

.book-header-title {{
    font-family:
        "Cormorant Garamond",
        Georgia,
        serif;

    font-size: 76px;
    line-height: .9;
    font-weight: 600;
    letter-spacing: .02em;

    color: var(--text);

    text-shadow:
        0 3px 12px rgba(0,0,0,.35);
}}

.book-header-subtitle {{
    font-family:
        "Libre Baskerville",
        Georgia,
        serif;

    color: var(--muted);
    margin-top: 18px;
    font-size: 13px;
    letter-spacing: .06em;
}}

.book-header-subtitle::before {{
    content: "✦  ";
    color: var(--accent);
}}

.book-header-subtitle::after {{
    content: "  ✦";
    color: var(--accent);
}}

/* ============================================================
   THEME SELECTOR
   ============================================================ */

.theme-heading {{
    font-family:
        "Cormorant Garamond",
        Georgia,
        serif;

    font-size: 25px;
    font-weight: 600;
    color: var(--text);
    margin: 12px 0 5px;
}}

div[data-baseweb="select"] > div {{
    background: rgba(20,15,15,.45) !important;
    border: 0 !important;
    border-bottom: 1px solid var(--accent) !important;
    border-radius: 0 !important;
    min-height: 46px !important;
}}

div[data-baseweb="select"] span {{
    color: var(--text) !important;
    font-family:
        "Libre Baskerville",
        Georgia,
        serif !important;
}}

div[role="listbox"] {{
    background: #211B1A !important;
    border: 1px solid var(--accent) !important;
    border-radius: 4px !important;
}}

div[role="option"] {{
    background: #211B1A !important;
    color: #F7EBD7 !important;
    font-family:
        "Libre Baskerville",
        Georgia,
        serif !important;
    padding: 12px 15px !important;
}}

div[role="option"]:hover {{
    background: #3A302C !important;
}}

div[role="option"][aria-selected="true"] {{
    background: #554235 !important;
}}

/* ============================================================
   STATS
   ============================================================ */

.stat-card {{
    position: relative;

    background: transparent;

    padding: 14px 8px 18px;
    text-align: center;

    border: 0;
    border-bottom: 1px solid var(--line);
}}

.stat-card::after {{
    content: "❧";
    position: absolute;
    bottom: -10px;
    left: 50%;
    transform: translateX(-50%);

    background: var(--page);
    color: var(--accent);

    padding: 0 8px;
    font-size: 15px;
}}

.stat-number {{
    font-family:
        "Cormorant Garamond",
        Georgia,
        serif;

    font-size: 40px;
    font-weight: 600;
    color: var(--accent);
}}

.stat-label {{
    color: var(--muted);

    font-family:
        "Libre Baskerville",
        Georgia,
        serif;

    font-size: 9px;
    text-transform: uppercase;
    letter-spacing: .18em;
}}

/* ============================================================
   TREE AREA
   ============================================================ */

.tree-area {{
    position: relative;

    margin-top: 35px;
    padding: 35px 20px 40px;

    background:
        radial-gradient(
            ellipse at center,
            rgba(255,255,255,.025),
            transparent 70%
        );

    border-top: 1px solid var(--line);
    border-bottom: 1px solid var(--line);
}}

.tree-area::before {{
    content: "❦";
    display: block;

    text-align: center;

    color: var(--accent);
    font-size: 28px;
    margin-bottom: 8px;
}}

.tree-area::after {{
    content: "❧";
    display: block;

    text-align: center;

    color: var(--accent);
    font-size: 24px;
    margin-top: 30px;
}}

/* ============================================================
   ROOT
   ============================================================ */

.root-node {{
    position: relative;

    width: fit-content;
    min-width: 280px;

    margin: 0 auto 45px;
    padding: 10px 35px 15px;

    background: transparent;

    text-align: center;

    border-bottom: 1px solid var(--accent);
}}

.root-node::before {{
    content: "✦";
    display: block;

    color: var(--accent);
    font-size: 18px;
    margin-bottom: -2px;
}}

.root-node-title {{
    color: var(--text);

    font-family:
        "Cormorant Garamond",
        Georgia,
        serif;

    font-size: 38px;
    font-weight: 600;
    letter-spacing: .03em;
}}

.root-node-small {{
    color: var(--muted);

    font-family:
        "Libre Baskerville",
        Georgia,
        serif;

    font-size: 10px;
    letter-spacing: .08em;
}}

/* ============================================================
   TREE BUTTONS
   ============================================================ */

.stButton {{
    margin-bottom: -12px;
}}

.stButton > button {{
    background: transparent !important;
    border: 0 !important;

    color: var(--text) !important;

    font-family:
        "Cormorant Garamond",
        Georgia,
        serif !important;

    font-size: 22px !important;
    font-weight: 600 !important;

    text-align: left !important;

    box-shadow: none !important;
}}

.stButton > button:hover {{
    background: transparent !important;
    color: var(--accent) !important;
    border: 0 !important;
}}

.stButton > button:focus {{
    box-shadow: none !important;
}}

/* ============================================================
   AUTHOR
   ============================================================ */

.author-info {{
    position: relative;

    margin: 3px 0 10px;
    padding: 8px 18px 10px 28px;

    background: transparent;

    border-left: 1px solid var(--accent2);
}}

.author-info::before {{
    content: "✦";

    position: absolute;
    left: -7px;
    top: 8px;

    background: var(--page);

    color: var(--accent);

    font-size: 12px;
}}

.author-name {{
    font-family:
        "Cormorant Garamond",
        Georgia,
        serif;

    font-size: 29px;
    font-weight: 600;

    letter-spacing: .02em;
}}

.author-count {{
    color: var(--muted);

    font-family:
        "Libre Baskerville",
        Georgia,
        serif;

    font-size: 10px;
    margin-top: -2px;
}}

/* ============================================================
   SERIES
   ============================================================ */

.series-info {{
    position: relative;

    margin-left: 50px;
    padding: 8px 15px 8px 24px;

    background: transparent;

    border-left: 1px solid var(--line);
}}

.series-info::before {{
    content: "❧";

    position: absolute;
    left: -9px;
    top: 4px;

    background: var(--page);

    color: var(--accent2);

    font-size: 15px;
}}

.series-name {{
    font-family:
        "Cormorant Garamond",
        Georgia,
        serif;

    font-size: 25px;
    font-weight: 600;

    letter-spacing: .015em;
}}

.series-count {{
    color: var(--muted);

    font-family:
        "Libre Baskerville",
        Georgia,
        serif;

    font-size: 10px;
}}

/* ============================================================
   BOOKS
   ============================================================ */

.book-info {{
    position: relative;

    margin-left: 105px;
    margin-top: 9px;
    padding: 9px 12px;

    background: rgba(255,255,255,.018);

    border: 0;
    border-bottom: 1px solid rgba(255,255,255,.08);

    transition:
        transform .2s ease,
        background .2s ease;
}}

.book-info:hover {{
    transform: translateX(4px);

    background: rgba(255,255,255,.035);
}}

.book-info::before {{
    content: "•";

    position: absolute;
    left: -18px;
    top: 12px;

    color: var(--accent);
    font-size: 16px;
}}

.book-title {{
    font-family:
        "Cormorant Garamond",
        Georgia,
        serif;

    font-size: 22px;
    font-weight: 600;

    color: var(--text);
}}

.book-meta {{
    color: var(--muted);

    font-family:
        "Libre Baskerville",
        Georgia,
        serif;

    font-size: 10px;
    margin-top: 3px;
}}

.book-cover {{
    width: 55px;
    height: 80px;

    object-fit: cover;

    border-radius: 2px;

    border: 1px solid var(--line);

    box-shadow:
        3px 4px 10px rgba(0,0,0,.35);
}}

/* ============================================================
   SEARCH
   ============================================================ */

div[data-baseweb="input"] > div {{
    background: transparent !important;

    border: 0 !important;
    border-bottom: 1px solid var(--line) !important;

    border-radius: 0 !important;
}}

div[data-baseweb="input"] input {{
    color: var(--text) !important;

    font-family:
        "Libre Baskerville",
        Georgia,
        serif !important;
}}

div[data-baseweb="input"] input::placeholder {{
    color: var(--muted) !important;
}}

/* ============================================================
   TEXT INPUTS / TEXTAREAS
   ============================================================ */

textarea {{
    background: var(--surface) !important;
    color: var(--text) !important;

    border: 1px solid var(--line) !important;
    border-radius: 3px !important;
}}

/* ============================================================
   TABS
   ============================================================ */

button[data-baseweb="tab"] {{
    font-family:
        "Cormorant Garamond",
        Georgia,
        serif !important;

    font-size: 19px !important;
    color: var(--muted) !important;

    background: transparent !important;
}}

button[data-baseweb="tab"][aria-selected="true"] {{
    color: var(--accent) !important;
}}

div[data-baseweb="tab-highlight"] {{
    background: var(--accent) !important;
    height: 1px !important;
}}

/* ============================================================
   RADIO BUTTONS
   ============================================================ */

div[role="radiogroup"] label {{
    font-family:
        "Cormorant Garamond",
        Georgia,
        serif !important;

    color: var(--text) !important;
}}

/* ============================================================
   GENERAL BUTTONS
   ============================================================ */

button[kind="primary"] {{
    background: transparent !important;

    color: var(--accent) !important;

    border: 1px solid var(--accent) !important;

    border-radius: 2px !important;

    font-family:
        "Cormorant Garamond",
        Georgia,
        serif !important;

    font-size: 18px !important;
}}

button[kind="primary"]:hover {{
    background: rgba(216,174,104,.08) !important;
}}

/* ============================================================
   FILE UPLOADER
   ============================================================ */

[data-testid="stFileUploader"] {{
    border: 1px dashed var(--line);
    padding: 15px;
    background: rgba(255,255,255,.015);
}}

/* ============================================================
   DIVIDERS
   ============================================================ */

hr {{
    border: 0 !important;
    border-top: 1px solid var(--line) !important;
    opacity: .65;
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
    '<div class="theme-heading">Choose your bookish world</div>'
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

        if not title or title == "nan":
            continue

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

    new_library = pd.DataFrame(books)

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
                        {len(filtered)} books
                        ·
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
