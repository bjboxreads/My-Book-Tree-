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
    st.session_state.library = pd.DataFrame(columns=[
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
    ])

if "open_authors" not in st.session_state:
    st.session_state.open_authors = set()

if "open_series" not in st.session_state:
    st.session_state.open_series = set()

theme = THEMES[st.session_state.theme]

# ============================================================
# CSS
# ============================================================

st.html(f"""
<style>

@import url('https://fonts.googleapis.com/css2?family=Berkshire+Swash&family=Libre+Baskerville:wght@400;700&display=swap');

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
    margin-top: 60px !important; /* Force it to apply */
}}

.book-header-title {{
    font-family: "Berkshire Swash", Georgia, serif !important;
    font-size: clamp(48px, 6vw, 76px);
    
    /* Change from var(--text) to var(--accent) */
    color: var(--accent); 
    
    /* Keep the shadow to ensure it pops on light themes too */
    text-shadow: 0 3px 12px rgba(0,0,0,0.35);
}}

.willow-logo {{
    width: 100%;
    max-width: 1000px;
    height: 300px;
    margin: 0 auto 5px;
}}

.willow-logo svg {{
    width: 100%;
    height: 100%;
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
    background: var(--surface) !important;
    color: var(--text) !important;
    border: 1px solid var(--line) !important;
    border-radius: 8px !important;
    font-family: "Libre Baskerville", Georgia, serif !important;
}}

.stButton > button:hover {{
    background: var(--surface2) !important;
    border-color: var(--accent) !important;
}}

py
st.markdown(
   st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Playfair+Display:wght@700&family=Montserrat:wght@300;600&display=swap');

    .stat-card {
        position: relative;
        background: var(--surface2) !important;
        border-radius: 20px;
        padding: 30px 15px;
        border: 1px solid var(--accent) !important;
        overflow: hidden;
        text-align: center;
        transition: all 0.5s cubic-bezier(0.23, 1, 0.32, 1);
        box-shadow: 0 10px 30px rgba(0,0,0,0.3);
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
    }

    .stat-card::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        width: 100%;
        height: 4px;
        background: linear-gradient(90deg, transparent, var(--accent), transparent);
        opacity: 0.8;
    }

    .stat-card:hover {
        transform: translateY(-8px);
        background: var(--card) !important;
        border-color: var(--accent);
    }

    .stat-number {
        font-family: 'Playfair Display', serif !important;
        font-size: 52px !important;
        background: linear-gradient(180deg, var(--text) 30%, var(--accent) 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-weight: 700 !important;
        margin: 0 !important;
        line-height: 1.1 !important;
    }

    .stat-label {
        font-family: 'Montserrat', sans-serif !important;
        color: var(--muted) !important;
        font-size: 10px !important;
        text-transform: uppercase;
        letter-spacing: 4px !important;
        font-weight: 600 !important;
        margin-top: 15px;
    }
    </style>
    """, 
    unsafe_allow_html=True
)
}}

.tree-container {{
    margin-top: 20px;
    padding: 35px 20px;
    border-top: 1px solid rgba(255,255,255,.12);
    border-bottom: 1px solid rgba(255,255,255,.12);
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
""")

# ============================================================
# HEADER
# ============================================================

st.html("""
<div class="book-header">
    <div class="book-header-title">My Book Tree</div>
</div>
""")

# ============================================================
# WILLOW TREE
# ============================================================

st.html("""
<div class="willow-logo">
<svg viewBox="0 0 1000 300" xmlns="http://www.w3.org/2000/svg">

<path d="M500 300 C490 245 490 200 500 155 C510 110 525 70 540 35"
fill="none" stroke="#54382E" stroke-width="30" stroke-linecap="round"/>

<path d="M505 295 C497 240 498 195 508 150 C518 105 530 70 542 38"
fill="none" stroke="#765044" stroke-width="7" stroke-linecap="round"/>

<g fill="none" stroke="#54382E" stroke-linecap="round">

<path d="M505 175 C440 135 365 105 275 95" stroke-width="14"/>
<path d="M500 195 C420 165 330 165 235 180" stroke-width="11"/>
<path d="M510 140 C465 95 430 60 400 20" stroke-width="10"/>

<path d="M515 170 C580 130 655 100 745 95" stroke-width="14"/>
<path d="M515 195 C595 165 680 165 765 180" stroke-width="11"/>
<path d="M520 135 C565 90 600 55 635 15" stroke-width="10"/>

</g>

<g fill="none" stroke="#72805C" stroke-width="4" stroke-linecap="round">

<path d="M275 95 C260 155 270 225 290 295"/>
<path d="M320 105 C305 170 315 240 335 300"/>
<path d="M365 115 C350 180 360 245 380 290"/>
<path d="M410 130 C395 185 405 240 425 280"/>
<path d="M455 145 C445 195 455 240 470 270"/>
<path d="M235 180 C225 225 235 265 250 295"/>

<path d="M745 95 C760 155 750 225 730 295"/>
<path d="M700 105 C715 170 705 240 685 300"/>
<path d="M655 115 C670 180 660 245 640 290"/>
<path d="M610 130 C625 185 615 240 595 280"/>
<path d="M565 145 C575 195 565 240 550 270"/>
<path d="M765 180 C775 225 765 265 750 295"/>

</g>

<g fill="#7D8C65">

<ellipse cx="275" cy="135" rx="7" ry="23" transform="rotate(-20 275 135)"/>
<ellipse cx="290" cy="195" rx="7" ry="24" transform="rotate(18 290 195)"/>
<ellipse cx="295" cy="250" rx="7" ry="23" transform="rotate(-15 295 250)"/>

<ellipse cx="320" cy="145" rx="7" ry="23" transform="rotate(18 320 145)"/>
<ellipse cx="335" cy="210" rx="7" ry="24" transform="rotate(-15 335 210)"/>
<ellipse cx="340" cy="265" rx="7" ry="22" transform="rotate(15 340 265)"/>

<ellipse cx="365" cy="155" rx="7" ry="23" transform="rotate(-18 365 155)"/>
<ellipse cx="380" cy="215" rx="7" ry="24" transform="rotate(15 380 215)"/>

<ellipse cx="410" cy="165" rx="7" ry="23" transform="rotate(16 410 165)"/>
<ellipse cx="425" cy="220" rx="7" ry="23" transform="rotate(-16 425 220)"/>

<ellipse cx="745" cy="135" rx="7" ry="23" transform="rotate(20 745 135)"/>
<ellipse cx="730" cy="195" rx="7" ry="24" transform="rotate(-18 730 195)"/>
<ellipse cx="725" cy="250" rx="7" ry="23" transform="rotate(15 725 250)"/>

<ellipse cx="700" cy="145" rx="7" ry="23" transform="rotate(-18 700 145)"/>
<ellipse cx="685" cy="210" rx="7" ry="24" transform="rotate(15 685 210)"/>
<ellipse cx="680" cy="265" rx="7" ry="22" transform="rotate(-15 680 265)"/>

<ellipse cx="655" cy="155" rx="7" ry="23" transform="rotate(18 655 155)"/>
<ellipse cx="640" cy="215" rx="7" ry="24" transform="rotate(-15 640 215)"/>

<ellipse cx="610" cy="165" rx="7" ry="23" transform="rotate(-16 610 165)"/>
<ellipse cx="595" cy="220" rx="7" ry="23" transform="rotate(16 595 220)"/>

</g>

<g fill="#95A574">
<ellipse cx="310" cy="125" rx="6" ry="21"/>
<ellipse cx="355" cy="190" rx="6" ry="22"/>
<ellipse cx="400" cy="140" rx="6" ry="21"/>
<ellipse cx="690" cy="125" rx="6" ry="21"/>
<ellipse cx="645" cy="190" rx="6" ry="22"/>
<ellipse cx="600" cy="140" rx="6" ry="21"/>
</g>

<g fill="#B87587">
<circle cx="310" cy="115" r="6"/>
<circle cx="320" cy="120" r="6"/>
<circle cx="315" cy="108" r="6"/>
<circle cx="305" cy="110" r="6"/>

<circle cx="400" cy="145" r="6"/>
<circle cx="410" cy="150" r="6"/>
<circle cx="405" cy="138" r="6"/>
<circle cx="395" cy="140" r="6"/>

<circle cx="690" cy="115" r="6"/>
<circle cx="700" cy="120" r="6"/>
<circle cx="695" cy="108" r="6"/>
<circle cx="685" cy="110" r="6"/>

<circle cx="600" cy="145" r="6"/>
<circle cx="610" cy="150" r="6"/>
<circle cx="605" cy="138" r="6"/>
<circle cx="595" cy="140" r="6"/>
</g>

<g fill="#E2B35E">
<circle cx="312" cy="115" r="3"/>
<circle cx="402" cy="145" r="3"/>
<circle cx="692" cy="115" r="3"/>
<circle cx="602" cy="145" r="3"/>
</g>

</svg>
</div>
""")

# ============================================================
# THEME
# ============================================================

st.html('<div class="theme-heading">Choose your bookish theme</div>')

theme_choice = st.selectbox(
    "Bookish theme",
    list(THEMES.keys()),
    index=list(THEMES.keys()).index(st.session_state.theme),
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
                    return (
                        f"https://covers.openlibrary.org/"
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

            items = r.json().get("items", [])

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
        r"\(([^()]*)#\s*(\d+(?:\.\d+)?)",
        r"\[([^\[\]]*)#\s*(\d+(?:\.\d+)?)",
        r"\(([^()]*)\bBook\s+(\d+(?:\.\d+)?)",
        r"\[([^\[\]]*)\bBook\s+(\d+(?:\.\d+)?)",
    ]

    for pattern in patterns:

        match = re.search(pattern, text, re.I)

        if match:

            series = match.group(1)

            series = re.sub(
                r",?\s*#\s*\d+(?:\.\d+)?",
                "",
                series,
                flags=re.I,
            )

            series = re.sub(
                r"\bBook\s+\d+(?:\.\d+)?",
                "",
                series,
                flags=re.I,
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
            re.I,
        )

        if match:

            try:
                return float(match.group(1))
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
# IMPORT
# ============================================================

def import_books(uploaded):

    try:
        df = pd.read_csv(
            uploaded,
            low_memory=False,
        )

    except Exception:

        uploaded.seek(0)

        df = pd.read_csv(
            uploaded,
            encoding="latin-1",
            low_memory=False,
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

    title_col = find_column([
        "title",
        "book title",
    ])

    author_col = find_column([
        "author",
        "authors",
    ])

    isbn_col = find_column([
        "isbn13",
        "isbn",
        "isbn 13",
    ])

    rating_col = find_column([
        "my rating",
        "rating",
    ])

    shelf_col = find_column([
        "exclusive shelf",
        "shelf",
        "status",
    ])

    genre_col = find_column([
        "genre",
        "genres",
        "primary genre",
        "genre(s)",
    ])

    series_col = find_column([
        "series",
        "series name",
    ])

    series_number_col = find_column([
        "series number",
        "series no",
        "book number",
    ])

    if not title_col:

        st.error(
            "I couldn't find a Title column in this CSV."
        )

        return False

    books = []

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

        if not author or author.lower() == "nan":
            author = "Unknown Author"

        isbn = ""

        if isbn_col:

            isbn = re.sub(
                r"\D",
                "",
                str(row.get(isbn_col, "")),
            )

        genre = ""

        if genre_col:

            genre = str(
                row.get(genre_col, "")
            ).strip()

            if genre.lower() == "nan":
                genre = ""

        if series_col:

            series = str(
                row.get(series_col, "")
            ).strip()

            if not series or series.lower() == "nan":
                series = detect_series(title)

        else:
            series = detect_series(title)

        series_number = None

        if series_number_col:

            try:
                value = row.get(series_number_col)

                if pd.notna(value):
                    series_number = float(value)

            except Exception:
                pass

        if series_number is None:
            series_number = detect_series_number(title)

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

            elif "read" in shelf and "to-read" not in shelf:
                status = "Read"

        books.append({
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
        })

    new_library = pd.DataFrame(books)

    if new_library.empty:

        st.error(
            "No books were found in the file."
        )

        return False

    progress = st.progress(0)

    for i in range(len(new_library)):

        new_library.loc[i, "Cover"] = get_cover(
            new_library.loc[i, "Title"],
            new_library.loc[i, "Author"],
            new_library.loc[i, "ISBN"],
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

for col, (number, label) in zip(columns, stats):

    with col:

        st.html(f"""
        <div class="stat-card">
            <div class="stat-number">{number}</div>
            <div class="stat-label">{label}</div>
        </div>
        """)

# ============================================================
# TABS
# ============================================================

tree_tab, books_tab, add_tab, import_tab = st.tabs([
    "🌳 Book Tree",
    "📚 Books",
    "➕ Add Book",
    "📥 Import",
])

# ============================================================
# BOOK TREE
# ============================================================

with tree_tab:

    # SEARCH BELONGS HERE — INSIDE BOOK TREE

    st.subheader("Search My Book Tree")

    search = st.text_input(
        "Search",
        placeholder="Search by author, title, series, genre, or ISBN...",
        label_visibility="collapsed",
    )

    st.caption(
        "Searches authors, titles, series, genres, and ISBNs."
    )

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

    if filtered.empty:

        if library.empty:

            st.info(
                "Your tree is empty. Import your library or add your first book."
            )

        else:

            st.info(
                f'No books matched "{search}".'
            )

    else:

        # ----------------------------------------------------
        # ROOT
        # ----------------------------------------------------

        st.html(f"""
        <div class="tree-container">

            <div class="tree-root">

                <div class="tree-root-title">
                    My Library
                </div>

                <div class="tree-root-count">
                    {len(filtered)} books ·
                    {filtered["Author"].nunique()} authors
                </div>

            </div>

        </div>
        """)

        # ----------------------------------------------------
        # AUTHORS
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

            opened = (
                author_id
                in st.session_state.open_authors
            )

            arrow = "▼" if opened else "▶"

            st.html(f"""
            <div class="author-branch">

                <div class="author-card">

                    <div class="author-name">
                        {html.escape(author)}
                    </div>

                    <div class="author-count">
                        {len(author_books)}
                        {"book" if len(author_books) == 1 else "books"}
                    </div>

                </div>

            </div>
            """)

            if st.button(
                f"{arrow} {author}",
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
                key=lambda x: x.lower(),
            )

            for series in series_list:

                # --------------------------------------------
                # STANDALONES
                # --------------------------------------------

                if series == "Standalone":

                    standalone_books = author_books[
                        author_books["Series"]
                        .fillna("Standalone")
                        .astype(str)
                        == "Standalone"
                    ].copy()

                    st.html(f"""
                    <div class="series-branch">

                        <div class="series-card">

                            <div class="series-name">
                                Standalone Books
                            </div>

                            <div class="series-count">
                                {len(standalone_books)}
                                {"book" if len(standalone_books) == 1 else "books"}
                            </div>

                        </div>

                    </div>
                    """)

                    for _, book in standalone_books.iterrows():

                        cover = str(
                            book.get("Cover", "") or ""
                        )

                        title = html.escape(
                            str(book.get("Title", ""))
                        )

                        status = html.escape(
                            str(book.get("Status", ""))
                        )

                        genre = html.escape(
                            str(book.get("Genre", "") or "")
                        )

                        meta = status

                        if genre:
                            meta += f" · {genre}"

                        if cover:

                            st.html(f"""
                            <div class="book-branch">

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
                                            {meta}
                                        </div>

                                    </div>

                                </div>

                            </div>
                            """)

                        else:

                            st.html(f"""
                            <div class="book-branch">

                                <div class="book-title">
                                    {title}
                                </div>

                                <div class="book-meta">
                                    {meta}
                                </div>

                            </div>
                            """)

                    continue

                # --------------------------------------------
                # SERIES BRANCH
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

                arrow = "▼" if series_open else "▶"

                series_books = author_books[
                    author_books["Series"]
                    .fillna("Standalone")
                    .astype(str)
                    == series
                ].copy()

                st.html(f"""
                <div class="series-branch">

                    <div class="series-card">

                        <div class="series-name">
                            {html.escape(series)}
                        </div>

                        <div class="series-count">
                            {len(series_books)}
                            {"book" if len(series_books) == 1 else "books"}
                        </div>

                    </div>

                </div>
                """)

                if st.button(
                    f"{arrow} {series}",
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

                if not series_open:
                    continue

                # --------------------------------------------
                # BOOKS IN SERIES
                # --------------------------------------------

                series_books = series_books.sort_values(
                    by=[
                        "Series Number",
                        "Title",
                    ],
                    na_position="last",
                )

                for position, (_, book) in enumerate(
                    series_books.iterrows(),
                    1,
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

                    title = html.escape(
                        str(book.get("Title", ""))
                    )

                    status = html.escape(
                        str(book.get("Status", ""))
                    )

                    genre = html.escape(
                        str(book.get("Genre", "") or "")
                    )

                    cover = str(
                        book.get("Cover", "") or ""
                    )

                    meta = status

                    if genre:
                        meta += f" · {genre}"

                    if cover:

                        st.html(f"""
                        <div class="book-branch">

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
                                        {number_text} · {title}
                                    </div>

                                    <div class="book-meta">
                                        {meta}
                                    </div>

                                </div>

                            </div>

                        </div>
                        """)

                    else:

                        st.html(f"""
                        <div class="book-branch">

                            <div class="book-title">
                                {number_text} · {title}
                            </div>

                            <div class="book-meta">
                                {meta}
                            </div>

                        </div>
                        """)

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
                        width=70,
                    )

            with col2:

                st.html(f"""
                <div class="book-title">
                    {html.escape(str(book["Title"]))}
                </div>

                <div class="book-meta">
                    {html.escape(str(book["Author"]))}
                    <br>
                    {html.escape(str(book["Series"]))}
                    <br>
                    {html.escape(str(book.get("Genre", "")))}
                </div>
                """)

            with col3:

                favorite = st.checkbox(
                    "♥",
                    value=bool(
                        book.get(
                            "Favorite",
                            False,
                        )
                    ),
                    key=f"fav_{index}",
                )

                if favorite != bool(
                    book.get(
                        "Favorite",
                        False,
                    )
                ):

                    st.session_state.library.loc[
                        index,
                        "Favorite",
                    ] = favorite

                    st.rerun()

# ============================================================
# ADD BOOK
# ============================================================

with add_tab:

    st.header("Add a Book")

    with st.form("add_book"):

        title = st.text_input("Title")

        author = st.text_input("Author")

        series = st.text_input(
            "Series",
            placeholder="Leave blank for standalone",
        )

        number = st.number_input(
            "Series number",
            min_value=0.0,
            value=0.0,
            step=0.5,
        )

        genre = st.text_input(
            "Genre",
            placeholder="Fantasy, Romance, Mystery..."
        )

        isbn = st.text_input("ISBN")

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

        favorite = st.checkbox("Favorite")

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

                st.session_state.library = pd.concat(
                    [
                        st.session_state.library,
                        pd.DataFrame([new_book]),
                    ],
                    ignore_index=True,
                )

                st.success(
                    f'"{title}" was added to your tree!'
                )

                st.rerun()

# ============================================================
# IMPORT TAB
# ============================================================

with import_tab:

    st.header("Import Your Library")

    st.write(
        "Upload a Goodreads CSV, StoryGraph export, "
        "or another compatible book-list CSV."
    )

    uploaded = st.file_uploader(
        "Choose your CSV",
        type=["csv"],
    )

    if uploaded:

        if st.button(
            "Build My Book Tree",
            use_container_width=True,
        ):

            with st.spinner(
                "Finding your books and covers..."
            ):

                success = import_books(uploaded)

            if success:

                st.success(
                    "Your book tree is ready!"
                )

                st.rerun()
