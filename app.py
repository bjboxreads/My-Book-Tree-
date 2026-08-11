```python
import streamlit as st
import pandas as pd
import requests
import re
import html
import time

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
# THEMES
# ============================================================

THEMES = {
    "Midnight Library": {
        "bg": "#111522",
        "paper": "#1B2030",
        "paper2": "#252B3D",
        "text": "#F6EEDC",
        "soft": "#D5CCBB",
        "gold": "#D6AF58",
        "branch": "#9E7D48",
        "leaf": "#789B82",
        "pink": "#C47E91",
    },

    "Enchanted Garden": {
        "bg": "#101A18",
        "paper": "#1A2B27",
        "paper2": "#274039",
        "text": "#FFF2D9",
        "soft": "#D8D1BE",
        "gold": "#D7B55A",
        "branch": "#927444",
        "leaf": "#82A878",
        "pink": "#D48791",
    },

    "Gothic Romance": {
        "bg": "#180E18",
        "paper": "#281429",
        "paper2": "#3C1D3B",
        "text": "#FFF0E9",
        "soft": "#D8C5CC",
        "gold": "#D9AE56",
        "branch": "#956048",
        "leaf": "#768F73",
        "pink": "#D77891",
    },

    "Dark Academia": {
        "bg": "#15130F",
        "paper": "#252018",
        "paper2": "#383025",
        "text": "#F4E8CE",
        "soft": "#D0C2A7",
        "gold": "#C9A24E",
        "branch": "#8D6C3F",
        "leaf": "#687B62",
        "pink": "#AA706C",
    },

    "Victorian Conservatory": {
        "bg": "#0D1B1A",
        "paper": "#17302C",
        "paper2": "#24463F",
        "text": "#FFF3DC",
        "soft": "#D4CFB9",
        "gold": "#D5AD54",
        "branch": "#927548",
        "leaf": "#769D82",
        "pink": "#C77D85",
    },

    "Poison Garden": {
        "bg": "#130F18",
        "paper": "#21182B",
        "paper2": "#352344",
        "text": "#F8EBDD",
        "soft": "#D7C4D2",
        "gold": "#D2AA53",
        "branch": "#875D68",
        "leaf": "#708B70",
        "pink": "#D67A9A",
    },

    "Sapphire & Gold": {
        "bg": "#0A1424",
        "paper": "#12243A",
        "paper2": "#1D3855",
        "text": "#FFF2D5",
        "soft": "#CAD3DC",
        "gold": "#DAB252",
        "branch": "#7F6A45",
        "leaf": "#638C88",
        "pink": "#C7798D",
    },

    "Rosewood Reading Room": {
        "bg": "#1B1110",
        "paper": "#2C1A18",
        "paper2": "#442723",
        "text": "#FFF0DA",
        "soft": "#D7C3B1",
        "gold": "#D5A64E",
        "branch": "#906346",
        "leaf": "#75866B",
        "pink": "#CA7780",
    },
}

# ============================================================
# SESSION STATE
# ============================================================

if "theme" not in st.session_state:
    st.session_state.theme = "Midnight Library"

# Prevent the old KeyError from surviving a code update
if st.session_state.theme not in THEMES:
    st.session_state.theme = "Midnight Library"

if "library" not in st.session_state:
    st.session_state.library = pd.DataFrame()

if "loading_seen" not in st.session_state:
    st.session_state.loading_seen = False

if "open_authors" not in st.session_state:
    st.session_state.open_authors = set()

if "open_series" not in st.session_state:
    st.session_state.open_series = set()

theme = THEMES[st.session_state.theme]

# ============================================================
# CSS
# ============================================================

st.markdown(
    f"""
<style>

@import url(
'https://fonts.googleapis.com/css2?family=Cormorant+Garamond:wght@400;500;600;700'
'&family=EB+Garamond:ital,wght@0,400;0,500;0,600;1,400;1,500'
'&family=Libre+Baskerville:wght@400;700'
);

:root {{
    --bg: {theme["bg"]};
    --paper: {theme["paper"]};
    --paper2: {theme["paper2"]};
    --text: {theme["text"]};
    --soft: {theme["soft"]};
    --gold: {theme["gold"]};
    --branch: {theme["branch"]};
    --leaf: {theme["leaf"]};
    --pink: {theme["pink"]};
}}

html,
body,
.stApp,
[data-testid="stAppViewContainer"] {{
    background: var(--bg) !important;
    color: var(--text) !important;
}}

.block-container {{
    max-width: 1500px !important;
    padding: 25px 45px 70px !important;
}}

* {{
    box-sizing: border-box;
}}

h1, h2, h3, h4, h5, h6 {{
    font-family: "Cormorant Garamond", Georgia, serif !important;
    color: var(--text) !important;
}}

p, label, span {{
    font-family: "EB Garamond", Georgia, serif;
    color: var(--text);
}}

/* TITLE */

.title-area {{
    text-align: center;
    margin: 15px auto 30px;
}}

.title {{
    font-family: "Cormorant Garamond", Georgia, serif;
    font-size: 64px;
    line-height: .9;
    font-weight: 600;
    color: var(--text);
}}

.subtitle {{
    margin-top: 12px;
    font-family: "Libre Baskerville", Georgia, serif;
    font-size: 10px;
    letter-spacing: .22em;
    text-transform: uppercase;
    color: var(--soft);
}}

.ornament {{
    width: 270px;
    height: 25px;
    margin: 20px auto 0;
    position: relative;
}}

.ornament::before {{
    content: "";
    position: absolute;
    left: 0;
    right: 0;
    top: 12px;
    height: 1px;
    background: var(--gold);
}}

.ornament::after {{
    content: "❧  ✦  ❧";
    position: absolute;
    left: 50%;
    transform: translateX(-50%);
    top: -1px;
    padding: 0 14px;
    background: var(--bg);
    color: var(--gold);
    font-size: 19px;
}}

/* LOADING SCREEN */

.loading {{
    position: fixed;
    inset: 0;
    z-index: 9999;
    background: var(--bg);
    display: flex;
    align-items: center;
    justify-content: center;
}}

.loading-inner {{
    width: 90%;
    max-width: 1100px;
    text-align: center;
}}

.loading-word {{
    font-family: "Cormorant Garamond", Georgia, serif;
    font-size: 44px;
    font-style: italic;
    color: var(--text);
    margin-bottom: 25px;
}}

.vine {{
    position: relative;
    height: 120px;
    width: 100%;
}}

.vine-main {{
    position: absolute;
    left: 1%;
    top: 57px;
    width: 98%;
    height: 5px;
    background: var(--branch);
    border-radius: 100%;
    animation: grow 2.4s ease-out forwards;
}}

@keyframes grow {{
    from {{ transform: scaleX(0); }}
    to {{ transform: scaleX(1); }}
}}

.vine-leaf {{
    position: absolute;
    width: 22px;
    height: 38px;
    background: var(--leaf);
    border-radius: 100% 0 100% 0;
    opacity: 0;
    animation: leafappear .45s ease forwards;
}}

.leaf1 {{ left: 12%; top: 35px; transform: rotate(-38deg); animation-delay: .45s; }}
.leaf2 {{ left: 25%; top: 66px; transform: rotate(42deg); animation-delay: .75s; }}
.leaf3 {{ left: 40%; top: 31px; transform: rotate(-34deg); animation-delay: 1s; }}
.leaf4 {{ right: 39%; top: 68px; transform: rotate(40deg); animation-delay: 1.3s; }}
.leaf5 {{ right: 24%; top: 30px; transform: rotate(-37deg); animation-delay: 1.6s; }}
.leaf6 {{ right: 11%; top: 65px; transform: rotate(43deg); animation-delay: 1.9s; }}

@keyframes leafappear {{
    from {{ opacity: 0; transform: scale(.2); }}
    to {{ opacity: 1; }}
}}

.loading-flower {{
    position: absolute;
    left: 50%;
    top: 35px;
    transform: translateX(-50%);
    color: var(--pink);
    font-size: 30px;
    opacity: 0;
    animation: flowerappear 1s ease forwards;
    animation-delay: 1.1s;
}}

@keyframes flowerappear {{
    to {{ opacity: 1; }}
}}

/* THEME SELECTOR */

.theme-heading {{
    text-align: center;
    font-family: "Cormorant Garamond", Georgia, serif;
    font-size: 23px;
    color: var(--gold);
    margin-bottom: 7px;
}}

div[data-baseweb="select"] > div {{
    background: #181818 !important;
    border: 1px solid #D6AF58 !important;
    border-radius: 6px !important;
}}

div[data-baseweb="select"] span {{
    color: #FFFFFF !important;
}}

div[role="listbox"] {{
    background: #181818 !important;
    border: 1px solid #D6AF58 !important;
}}

div[role="option"] {{
    color: #FFFFFF !important;
    background: #181818 !important;
    font-family: "EB Garamond", Georgia, serif !important;
}}

div[role="option"] * {{
    color: #FFFFFF !important;
}}

div[role="option"]:hover {{
    background: #3A3A3A !important;
}}

/* COUNTS */

.library-counts {{
    display: flex;
    justify-content: center;
    gap: 55px;
    margin: 30px auto 40px;
    text-align: center;
}}

.count-number {{
    display: block;
    font-family: "Cormorant Garamond", Georgia, serif;
    font-size: 36px;
    color: var(--gold);
}}

.count-label {{
    display: block;
    margin-top: 4px;
    font-family: "Libre Baskerville", Georgia, serif;
    font-size: 8px;
    letter-spacing: .15em;
    text-transform: uppercase;
    color: var(--soft);
}}

/* SEARCH */

.tools {{
    border-top: 1px solid var(--branch);
    border-bottom: 1px solid var(--branch);
    padding: 18px 0;
    margin-bottom: 35px;
}}

.tool-title {{
    text-align: center;
    font-family: "Cormorant Garamond", Georgia, serif;
    font-size: 25px;
    font-style: italic;
    color: var(--gold);
    margin-bottom: 12px;
}}

div[data-baseweb="input"] > div {{
    background: var(--paper) !important;
    border: 1px solid var(--branch) !important;
}}

div[data-baseweb="input"] input {{
    color: var(--text) !important;
    font-family: "EB Garamond", Georgia, serif !important;
}}

div[data-baseweb="input"] input::placeholder {{
    color: var(--soft) !important;
}}

/* TREE */

.tree-title {{
    text-align: center;
    font-family: "Cormorant Garamond", Georgia, serif;
    font-size: 40px;
    color: var(--text);
}}

.tree-subtitle {{
    text-align: center;
    font-family: "EB Garamond", Georgia, serif;
    color: var(--soft);
    font-size: 16px;
    margin-bottom: 35px;
}}

.tree-root {{
    text-align: center;
    margin-bottom: 45px;
}}

.root-label {{
    display: inline-block;
    padding: 8px 25px;
    border-top: 1px solid var(--gold);
    border-bottom: 1px solid var(--gold);
    font-family: "Cormorant Garamond", Georgia, serif;
    font-size: 26px;
    color: var(--gold);
}}

/* AUTHOR */

.author-wrap {{
    position: relative;
    margin: 0 0 22px 25px;
    padding-left: 30px;
}}

.author-wrap::before {{
    content: "";
    position: absolute;
    left: 6px;
    top: 0;
    bottom: -22px;
    width: 1px;
    background: var(--branch);
}}

.author-wrap::after {{
    content: "";
    position: absolute;
    left: 6px;
    top: 25px;
    width: 24px;
    height: 1px;
    background: var(--branch);
}}

.author-name {{
    display: inline-block;
    padding: 3px 12px;
    background: var(--bg);
    font-family: "Cormorant Garamond", Georgia, serif;
    font-size: 29px;
    font-weight: 600;
    color: var(--text);
}}

.author-count {{
    margin-left: 8px;
    font-family: "EB Garamond", Georgia, serif;
    font-size: 14px;
    color: var(--soft);
}}

/* SERIES */

.series-wrap {{
    position: relative;
    margin: 8px 0 8px 80px;
    padding-left: 30px;
}}

.series-wrap::before {{
    content: "";
    position: absolute;
    left: 5px;
    top: -10px;
    bottom: -10px;
    width: 1px;
    background: var(--branch);
}}

.series-wrap::after {{
    content: "";
    position: absolute;
    left: 5px;
    top: 23px;
    width: 25px;
    height: 1px;
    background: var(--branch);
}}

.series-name {{
    display: inline-block;
    background: var(--bg);
    padding: 2px 10px;
    font-family: "Cormorant Garamond", Georgia, serif;
    font-size: 24px;
    font-weight: 600;
    color: var(--gold);
}}

.series-count {{
    margin-left: 7px;
    font-family: "EB Garamond", Georgia, serif;
    font-size: 13px;
    color: var(--soft);
}}

/* BOOK */

.book-wrap {{
    position: relative;
    margin: 8px 0 8px 145px;
    padding-left: 28px;
}}

.book-wrap::before {{
    content: "";
    position: absolute;
    left: 5px;
    top: -10px;
    bottom: -10px;
    width: 1px;
    background: var(--branch);
}}

.book-wrap::after {{
    content: "";
    position: absolute;
    left: 5px;
    top: 34px;
    width: 23px;
    height: 1px;
    background: var(--branch);
}}

.book-info {{
    display: flex;
    align-items: center;
    gap: 13px;
}}

.book-cover {{
    width: 48px;
    height: 70px;
    object-fit: cover;
    border: 1px solid var(--gold);
    box-shadow: 3px 4px 12px rgba(0,0,0,.35);
}}

.book-cover-placeholder {{
    width: 48px;
    height: 70px;
    border: 1px solid var(--branch);
    display: flex;
    align-items: center;
    justify-content: center;
    color: var(--soft);
}}

.book-title {{
    font-family: "Cormorant Garamond", Georgia, serif;
    font-size: 21px;
    font-weight: 600;
    color: var(--text);
}}

.book-details {{
    font-family: "EB Garamond", Georgia, serif;
    font-size: 13px;
    color: var(--soft);
}}

.status-read {{
    color: var(--leaf);
}}

.status-current {{
    color: var(--gold);
}}

.status-want {{
    color: var(--pink);
}}

/* TREE BUTTONS */

.stButton > button {{
    background: transparent !important;
    border: none !important;
    color: var(--text) !important;
    font-family: "Cormorant Garamond", Georgia, serif !important;
    font-size: 21px !important;
    box-shadow: none !important;
}}

.stButton > button:hover {{
    color: var(--gold) !important;
    background: transparent !important;
    border: none !important;
}}

/* TABS */

button[data-baseweb="tab"] {{
    font-family: "Cormorant Garamond", Georgia, serif !important;
    font-size: 20px !important;
    color: var(--soft) !important;
}}

button[data-baseweb="tab"][aria-selected="true"] {{
    color: var(--gold) !important;
}}

@media (max-width: 800px) {{

    .block-container {{
        padding: 20px 15px 50px !important;
    }}

    .title {{
        font-size: 46px;
    }}

    .library-counts {{
        gap: 20px;
    }}

    .book-wrap {{
        margin-left: 70px;
    }}

    .series-wrap {{
        margin-left: 40px;
    }}

    .author-wrap {{
        margin-left: 10px;
    }}
}}

</style>
""",
    unsafe_allow_html=True,
)

# ============================================================
# COVER LOOKUP
# ============================================================

@st.cache_data(show_spinner=False)
def find_cover(title, author, isbn):

    isbn = re.sub(r"\D", "", str(isbn))

    if isbn:

        url = f"https://covers.openlibrary.org/b/isbn/{isbn}-L.jpg"

        try:

            r = requests.get(url, timeout=8)

            if r.status_code == 200 and len(r.content) > 1000:
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

            docs = r.json().get("docs", [])

            if docs:

                cover_id = docs[0].get("cover_i")

                if cover_id:

                    return f"https://covers.openlibrary.org/b/id/{cover_id}-L.jpg"

    except Exception:
        pass

    return ""


# ============================================================
# GENRE
# ============================================================

@st.cache_data(show_spinner=False)
def find_genre(title, author):

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

            items = r.json().get("items", [])

            if items:

                categories = (
                    items[0]
                    .get("volumeInfo", {})
                    .get("categories", [])
                )

                if categories:

                    text = categories[0]

                    preferred = [
                        "Romance",
                        "Fantasy",
                        "Mystery",
                        "Thriller",
                        "Horror",
                        "Science Fiction",
                        "Historical",
                        "Biography",
                        "Memoir",
                        "History",
                        "Contemporary",
                        "Paranormal",
                        "Crime",
                        "Young Adult",
                    ]

                    for genre in preferred:

                        if genre.lower() in text.lower():
                            return genre

                    return text.split("/")[-1].strip()

    except Exception:
        pass

    return "Uncategorized"


# ============================================================
# SERIES HELPERS
# ============================================================

def get_series(title):

    patterns = [
        r"\(([^()]*)#\s*\d+(?:\.\d+)?[^()]*\)",
        r"\(([^()]*)Book\s+\d+(?:\.\d+)?[^()]*\)",
        r"\[([^\[\]]*)#\s*\d+(?:\.\d+)?[^\[\]]*\]",
        r"\[([^\[\]]*)Book\s+\d+(?:\.\d+)?[^\[\]]*\]",
    ]

    for pattern in patterns:

        match = re.search(
            pattern,
            str(title),
            re.I
        )

        if match:

            result = match.group(1)

            result = re.sub(
                r"#\s*\d+(?:\.\d+)?",
                "",
                result,
                flags=re.I
            )

            result = re.sub(
                r"Book\s+\d+(?:\.\d+)?",
                "",
                result,
                flags=re.I
            )

            result = result.strip(" ,-:")

            if result:
                return result

    return "Standalone"


def get_series_number(title):

    patterns = [
        r"#\s*(\d+(?:\.\d+)?)",
        r"Book\s+(\d+(?:\.\d+)?)",
        r"Vol(?:ume)?\.?\s+(\d+(?:\.\d+)?)",
    ]

    for pattern in patterns:

        match = re.search(
            pattern,
            str(title),
            re.I
        )

        if match:

            try:
                return float(match.group(1))
            except Exception:
                pass

    return None


# ============================================================
# RENDER BOOK
# IMPORTANT: THIS IS DEFINED BEFORE IT IS CALLED
# ============================================================

def render_book(book, numbered=False):

    number = book.get("Series Number")

    prefix = ""

    if numbered and pd.notna(number):

        try:

            if float(number).is_integer():
                prefix = f"{int(number)}. "
            else:
                prefix = f"{number}. "

        except Exception:
            pass

    title = html.escape(
        str(book.get("Title", ""))
    )

    genre = html.escape(
        str(book.get("Genre", ""))
    )

    status = str(
        book.get("Status", "")
    )

    if status == "Read":
        status_class = "status-read"
    elif status == "Currently Reading":
        status_class = "status-current"
    else:
        status_class = "status-want"

    rating = book.get("My Rating")
    rating_text = ""

    if pd.notna(rating):

        try:

            if float(rating) > 0:

                rating_text = (
                    " · "
                    + "★" * int(float(rating))
                )

        except Exception:
            pass

    cover = str(
        book.get("Cover", "") or ""
    )

    if cover:

        image_html = (
            f'<img class="book-cover" '
            f'src="{html.escape(cover)}">'
        )

    else:

        image_html = (
            '<div class="book-cover-placeholder">✦</div>'
        )

    st.markdown(
        f"""
        <div class="book-wrap">

            <div class="book-info">

                {image_html}

                <div>

                    <div class="book-title">
                        {prefix}{title}
                    </div>

                    <div class="book-details">

                        <span class="{status_class}">
                            {html.escape(status)}
                        </span>

                        &nbsp;·&nbsp;

                        {genre}

                        {rating_text}

                    </div>

                </div>

            </div>

        </div>
        """,
        unsafe_allow_html=True,
    )


# ============================================================
# IMPORT CSV
# ============================================================

def import_csv(uploaded):

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

    lookup = {
        str(c).lower().strip(): c
        for c in df.columns
    }

    def column(*names):

        for name in names:

            if name.lower() in lookup:
                return lookup[name.lower()]

        return None

    title_col = column("title")
    author_col = column("author", "authors")
    isbn_col = column("isbn13", "isbn")
    rating_col = column("my rating", "rating")
    shelf_col = column("exclusive shelf", "shelf")

    if not title_col:

        st.error(
            "I couldn't find a Title column in this CSV."
        )

        return False

    records = []

    for _, row in df.iterrows():

        title = str(
            row.get(title_col, "")
        ).strip()

        if not title or title.lower() == "nan":
            continue

        author = "Unknown Author"

        if author_col:

            author = str(
                row.get(author_col, "")
            ).strip()

        isbn = ""

        if isbn_col:

            isbn = re.sub(
                r"\D",
                "",
                str(row.get(isbn_col, ""))
            )

        rating = None

        if rating_col:

            try:
                rating = float(
                    row.get(rating_col)
                )
            except Exception:
                pass

        status = "Want to Read"

        if shelf_col:

            shelf = str(
                row.get(shelf_col, "")
            ).lower()

            if "currently" in shelf:
                status = "Currently Reading"

            elif shelf == "read":
                status = "Read"

        records.append(
            {
                "Title": title,
                "Author": author,
                "Series": get_series(title),
                "Series Number": get_series_number(title),
                "ISBN": isbn,
                "My Rating": rating,
                "Status": status,
                "Favorite": False,
                "Cover": "",
                "Genre": "Uncategorized",
                "Date Read": "",
            }
        )

    books = pd.DataFrame(records)

    if books.empty:

        st.error(
            "No books were found in the file."
        )

        return False

    progress = st.progress(0)

    for i in range(len(books)):

        title = books.loc[i, "Title"]
        author = books.loc[i, "Author"]
        isbn = books.loc[i, "ISBN"]

        books.loc[i, "Cover"] = find_cover(
            title,
            author,
            isbn
        )

        books.loc[i, "Genre"] = find_genre(
            title,
            author
        )

        progress.progress(
            (i + 1) / len(books)
        )

    progress.empty()

    st.session_state.library = books
    st.session_state.open_authors = set()
    st.session_state.open_series = set()

    return True


# ============================================================
# LOADING SCREEN
# ============================================================

if not st.session_state.loading_seen:

    st.markdown(
        """
        <div class="loading">

            <div class="loading-inner">

                <div class="loading-word">
                    Growing your library...
                </div>

                <div class="vine">

                    <div class="vine-main"></div>

                    <div class="vine-leaf leaf1"></div>
                    <div class="vine-leaf leaf2"></div>
                    <div class="vine-leaf leaf3"></div>
                    <div class="vine-leaf leaf4"></div>
                    <div class="vine-leaf leaf5"></div>
                    <div class="vine-leaf leaf6"></div>

                    <div class="loading-flower">
                        ✿
                    </div>

                </div>

            </div>

        </div>
        """,
        unsafe_allow_html=True,
    )

    time.sleep(2.4)

    st.session_state.loading_seen = True
    st.rerun()


# ============================================================
# HEADER
# ============================================================

st.markdown(
    """
    <div class="title-area">

        <div class="title">
            My Book Tree
        </div>

        <div class="subtitle">
            Where every story has a branch
        </div>

        <div class="ornament"></div>

    </div>
    """,
    unsafe_allow_html=True,
)


# ============================================================
# THEME SELECTOR
# ============================================================

st.markdown(
    '<div class="theme-heading">Choose Your Reading Room</div>',
    unsafe_allow_html=True,
)

selected_theme = st.selectbox(
    "Theme",
    list(THEMES.keys()),
    index=list(THEMES.keys()).index(
        st.session_state.theme
    ),
    label_visibility="collapsed",
)

if selected_theme != st.session_state.theme:

    st.session_state.theme = selected_theme
    st.rerun()


# ============================================================
# LIBRARY
# ============================================================

library = st.session_state.library

total_books = len(library)

authors_count = (
    library["Author"].nunique()
    if not library.empty
    else 0
)

series_count = (
    library[
        library["Series"] != "Standalone"
    ]["Series"].nunique()
    if not library.empty
    else 0
)

read_count = (
    len(
        library[
            library["Status"] == "Read"
        ]
    )
    if not library.empty
    else 0
)

st.markdown(
    f"""
    <div class="library-counts">

        <div>
            <span class="count-number">
                {total_books}
            </span>
            <span class="count-label">
                Books
            </span>
        </div>

        <div>
            <span class="count-number">
                {authors_count}
            </span>
            <span class="count-label">
                Authors
            </span>
        </div>

        <div>
            <span class="count-number">
                {series_count}
            </span>
            <span class="count-label">
                Series
            </span>
        </div>

        <div>
            <span class="count-number">
                {read_count}
            </span>
            <span class="count-label">
                Read
            </span>
        </div>

    </div>
    """,
    unsafe_allow_html=True,
)


# ============================================================
# TABS
# ============================================================

tree_tab, all_tab, import_tab, add_tab = st.tabs(
    [
        "🌿 Book Tree",
        "Books",
        "Import",
        "Add a Book",
    ]
)


# ============================================================
# TREE
# ============================================================

with tree_tab:

    if library.empty:

        st.markdown(
            """
            <div style="
                text-align:center;
                padding:80px 20px;
            ">

                <div style="
                    font-family:'Cormorant Garamond',serif;
                    font-size:42px;
                    color:var(--text);
                ">
                    Your tree is waiting.
                </div>

                <div style="
                    font-family:'EB Garamond',serif;
                    font-size:18px;
                    color:var(--soft);
                    margin-top:10px;
                ">
                    Import your Goodreads library
                    to begin growing it.
                </div>

            </div>
            """,
            unsafe_allow_html=True,
        )

    else:

        # SEARCH AND FILTERS

        st.markdown(
            """
            <div class="tools">

                <div class="tool-title">
                    Find something in your library
                </div>

            </div>
            """,
            unsafe_allow_html=True,
        )

        c1, c2, c3 = st.columns([2, 1, 1])

        with c1:

            search = st.text_input(
                "Search",
                placeholder="Title, author, series or genre...",
                label_visibility="collapsed",
            )

        with c2:

            status = st.selectbox(
                "Status",
                [
                    "All",
                    "Read",
                    "Currently Reading",
                    "Want to Read",
                ],
                label_visibility="collapsed",
            )

        with c3:

            sort = st.selectbox(
                "Sort",
                [
                    "Author A–Z",
                    "Author Z–A",
                    "Title A–Z",
                    "Title Z–A",
                    "Highest Rated",
                    "Lowest Rated",
                ],
                label_visibility="collapsed",
            )

        filtered = library.copy()

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
                |
                filtered["Genre"]
                .astype(str)
                .str.lower()
                .str.contains(q, na=False)
            )

            filtered = filtered[mask]

        if status != "All":

            filtered = filtered[
                filtered["Status"] == status
            ]

        if sort == "Author A–Z":

            filtered = filtered.sort_values(
                "Author",
                key=lambda x:
                x.astype(str).str.lower()
            )

        elif sort == "Author Z–A":

            filtered = filtered.sort_values(
                "Author",
                ascending=False,
                key=lambda x:
                x.astype(str).str.lower()
            )

        elif sort == "Title A–Z":

            filtered = filtered.sort_values(
                "Title",
                key=lambda x:
                x.astype(str).str.lower()
            )

        elif sort == "Title Z–A":

            filtered = filtered.sort_values(
                "Title",
                ascending=False,
                key=lambda x:
                x.astype(str).str.lower()
            )

        elif sort == "Highest Rated":

            filtered = filtered.sort_values(
                "My Rating",
                ascending=False,
                na_position="last"
            )

        elif sort == "Lowest Rated":

            filtered = filtered.sort_values(
                "My Rating",
                na_position="last"
            )

        # TREE TITLE

        st.markdown(
            """
            <div class="tree-title">
                Your Library
            </div>

            <div class="tree-subtitle">
                Author → Series → Books
            </div>

            <div class="tree-root">
                <div class="root-label">
                    The Beginning
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        # AUTHORS

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
            ]

            author_id = re.sub(
                r"[^a-zA-Z0-9]",
                "_",
                author
            )

            is_open = (
                author_id
                in st.session_state.open_authors
            )

            clicked = st.button(
                ("⌄  " if is_open else "›  ")
                + author,
                key=f"author_{author_id}",
            )

            if clicked:

                if is_open:

                    st.session_state.open_authors.remove(
                        author_id
                    )

                else:

                    st.session_state.open_authors.add(
                        author_id
                    )

                st.rerun()

            st.markdown(
                f"""
                <div class="author-wrap">

                    <span class="author-name">
                        {html.escape(author)}
                    </span>

                    <span class="author-count">
                        {len(author_books)}
                        {"book" if len(author_books) == 1 else "books"}
                    </span>

                </div>
                """,
                unsafe_allow_html=True,
            )

            if not is_open:
                continue

            # SERIES

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

                    st.markdown(
                        f"""
                        <div class="series-wrap">

                            <span class="series-name">
                                Standalone Books
                            </span>

                            <span class="series-count">
                                {len(series_books)}
                            </span>

                        </div>
                        """,
                        unsafe_allow_html=True,
                    )

                    for _, book in series_books.iterrows():
                        render_book(book, False)

                    continue

                series_id = (
                    author_id
                    + "_"
                    + re.sub(
                        r"[^a-zA-Z0-9]",
                        "_",
                        series_name
                    )
                )

                series_open = (
                    series_id
                    in st.session_state.open_series
                )

                clicked = st.button(
                    ("⌄  " if series_open else "›  ")
                    + series_name,
                    key=f"series_{series_id}",
                )

                if clicked:

                    if series_open:

                        st.session_state.open_series.remove(
                            series_id
                        )

                    else:

                        st.session_state.open_series.add(
                            series_id
                        )

                    st.rerun()

                st.markdown(
                    f"""
                    <div class="series-wrap">

                        <span class="series-name">
                            {html.escape(series_name)}
                        </span>

                        <span class="series-count">
                            {len(series_books)}
                            {"book" if len(series_books) == 1 else "books"}
                        </span>

                    </div>
                    """,
                    unsafe_allow_html=True,
                )

                if not series_open:
                    continue

                series_books = series_books.sort_values(
                    ["Series Number", "Title"],
                    na_position="last"
                )

                for _, book in series_books.iterrows():
                    render_book(book, True)


# ============================================================
# ALL BOOKS
# ============================================================

with all_tab:

    st.header("All Books")

    if library.empty:

        st.write("Your library is empty.")

    else:

        view = st.radio(
            "Show",
            [
                "All",
                "Read",
                "Currently Reading",
                "Want to Read",
            ],
            horizontal=True
        )

        books = library.copy()

        if view != "All":

            books = books[
                books["Status"] == view
            ]

        books = books.sort_values(
            "Title",
            key=lambda x:
            x.astype(str).str.lower()
        )

        for _, book in books.iterrows():

            render_book(
                book,
                False
            )


# ============================================================
# IMPORT
# ============================================================

with import_tab:

    st.header("Import Your Library")

    st.write(
        "Upload your Goodreads CSV or another compatible book-list CSV."
    )

    uploaded = st.file_uploader(
        "Choose your CSV file",
        type=["csv"]
    )

    if uploaded:

        st.write(
            f"Ready: **{uploaded.name}**"
        )

        if st.button(
            "🌿 Grow My Book Tree",
            type="primary"
        ):

            with st.spinner(
                "Finding your books, covers and genres..."
            ):

                success = import_csv(uploaded)

            if success:

                st.success(
                    f"Added {len(st.session_state.library)} books to your library."
                )

                st.rerun()


# ============================================================
# ADD BOOK
# ============================================================

with add_tab:

    st.header("Add a Book")

    with st.form("new_book"):

        title = st.text_input("Title")
        author = st.text_input("Author")

        series = st.text_input(
            "Series",
            placeholder="Leave blank for standalone"
        )

        number = st.number_input(
            "Series number",
            min_value=0.0,
            value=0.0,
            step=0.5
        )

        genre = st.text_input("Genre")

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

        isbn = st.text_input("ISBN")

        favorite = st.checkbox(
            "Favorite"
        )

        submit = st.form_submit_button(
            "Add Book"
        )

        if submit:

            if not title or not author:

                st.error(
                    "Please enter both a title and author."
                )

            else:

                if not genre:
                    genre = find_genre(
                        title,
                        author
                    )

                new_book = {
                    "Title": title,
                    "Author": author,
                    "Series":
                        series
                        if series
                        else "Standalone",
                    "Series Number":
                        number
                        if number
                        else None,
                    "ISBN": isbn,
                    "My Rating":
                        rating
                        if rating
                        else None,
                    "Status": status,
                    "Favorite": favorite,
                    "Cover": find_cover(
                        title,
                        author,
                        isbn
                    ),
                    "Genre": genre,
                    "Date Read": "",
                }

                st.session_state.library = pd.concat(
                    [
                        st.session_state.library,
                        pd.DataFrame([new_book]),
                    ],
                    ignore_index=True
                )

                st.success(
                    f"{title} was added to your tree."
                )

                st.rerun()
```
