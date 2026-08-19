import streamlit as st
import pandas as pd
import requests
import re
import html
import os
import shutil
import time
from concurrent.futures import ThreadPoolExecutor, as_completed


# ============================================================
# LOCAL PERSISTENCE — save/load the library to a CSV file next
# to this script, so the library survives closing the browser
# tab or restarting the app instead of needing to be
# re-imported every time.
# ============================================================

LIBRARY_FILE = os.path.join(
    os.path.dirname(os.path.abspath(__file__)),
    "storyspire_library.csv",
)

LIBRARY_BACKUP_FILE = LIBRARY_FILE + ".bak"

LIBRARY_COLUMNS = [
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
    "Tags",
    "Publisher",
    "Pages",
    "Date Read",
]


TEXT_LIBRARY_COLUMNS = [
    "Title",
    "Author",
    "Series",
    "Genre",
    "ISBN",
    "Status",
    "Cover",
    "Description",
    "Tags",
    "Publisher",
    "Pages",
    "Date Read",
]


def normalize_library_columns(df):
    """Make sure a DataFrame has exactly LIBRARY_COLUMNS, in
    order, filling in any missing ones. Used any time a
    DataFrame comes from somewhere that might not have every
    column (a fresh CSV, the data editor's '+' row, etc).

    Also forces every text column to a plain string dtype. This
    matters because when a column is entirely empty (e.g. no
    book has a Description or Genre yet), pandas infers it as
    float64 (all-NaN) rather than text. On newer pandas, later
    assigning a real string into a float64 column (e.g.
    library.loc[i, "Genre"] = "Fantasy") raises a TypeError
    instead of silently upcasting — which is what was breaking
    the cover/description/genre fetch buttons."""
    df = df.copy()
    for column in LIBRARY_COLUMNS:
        if column not in df.columns:
            df[column] = "" if column != "Favorite" else False
    df = df[LIBRARY_COLUMNS]
    for column in TEXT_LIBRARY_COLUMNS:
        df[column] = df[column].astype(object)
        df[column] = df[column].apply(
            lambda v: ""
            if (v is None or (isinstance(v, float) and pd.isna(v)))
            else str(v)
        )
        df[column] = df[column].replace(["nan", "None"], "")
    return df


def save_library(df):
    """Write the current library to the local CSV save file."""
    try:
        if os.path.exists(LIBRARY_FILE):
            try:
                shutil.copy(LIBRARY_FILE, LIBRARY_BACKUP_FILE)
            except Exception:
                pass
        df.to_csv(LIBRARY_FILE, index=False)
    except Exception:
        pass


def load_library():
    """Load the saved library from disk, if it exists."""
    if os.path.exists(LIBRARY_FILE):
        try:
            df = pd.read_csv(LIBRARY_FILE)
            df = normalize_library_columns(df)
            df["Favorite"] = (
                df["Favorite"]
                .astype(str)
                .str.strip()
                .str.lower()
                .isin(["true", "1", "1.0"])
            )
            return df
        except Exception:
            pass
    return pd.DataFrame(columns=LIBRARY_COLUMNS)


def clean_isbn(raw):
    """Clean a raw ISBN cell into digits (+ optional trailing X)."""
    s = str(raw).strip()
    if s.lower() in ("nan", "none"):
        return ""
    s = re.sub(r'^="?', '', s)
    s = re.sub(r'"?$', '', s)
    s = re.sub(r'[^0-9Xx]', '', s)
    return s.upper()


def clean_author_series(df):
    """Fill blank/NaN Author and Series with consistent placeholders."""
    df = df.copy()
    df["Author"] = (
        df["Author"]
        .fillna("Unknown Author")
        .astype(str)
        .replace(["", "nan", "None"], "Unknown Author")
    )
    df["Series"] = (
        df["Series"]
        .fillna("Standalone")
        .astype(str)
        .replace(["", "nan", "None"], "Standalone")
    )
    return df


def clean_genre_column(series):
    """Same idea as clean_author_series but for Genre."""
    return (
        series.fillna("")
        .astype(str)
        .str.strip()
        .replace(["", "nan", "None"], "Unknown Genre")
    )


TREE_CSS = """
<style>
.book-ancestry-tree {
    animation: atreeFadeIn .35s ease;
}
@keyframes atreeFadeIn {
    from { opacity: 0; }
    to { opacity: 1; }
}

.book-ancestry-tree summary,
.atree-author-grid summary {
    cursor: pointer;
    list-style: none;
}
.book-ancestry-tree summary::-webkit-details-marker,
.atree-author-grid summary::-webkit-details-marker {
    display: none;
}
.book-ancestry-tree summary::marker,
.atree-author-grid summary::marker {
    content: "";
}

.atree-author {
    margin: 22px 0;
}

.atree-arrow {
    display: inline-block;
    margin-right: 4px;
    transition: transform .2s ease;
}
details[open] > summary .atree-arrow {
    transform: rotate(90deg);
}

.atree-pill {
    display: block;
    width: 100%;
    box-sizing: border-box;
    background: linear-gradient(135deg, var(--surface), var(--surface2));
    color: var(--text);
    border: 1px solid var(--surface2);
    border-radius: 12px 5px 12px 5px;
    font-family: "Libre Baskerville", Georgia, serif;
    font-size: 1rem;
    box-shadow: 0 2px 6px rgba(0,0,0,.12);
    padding: 0.5rem 1rem;
    transition: transform .15s ease, box-shadow .15s ease,
        background .15s ease, border-color .15s ease;
}
.atree-pill:hover {
    background: linear-gradient(135deg, var(--surface2), var(--card));
    border-color: var(--accent);
    box-shadow: 0 4px 12px rgba(0,0,0,.22);
    transform: translateY(-2px);
}
summary .atree-pill {
    cursor: pointer;
}
.atree-pill-book {
    margin: 6px 0;
    position: relative;
}
.atree-pill-book-cover {
    display: flex;
    align-items: center;
    gap: 10px;
}
.atree-cover {
    width: 36px;
    height: 52px;
    object-fit: cover;
    border-radius: 3px 8px 3px 8px;
    border: 1px solid var(--accent);
    flex-shrink: 0;
}

.atree-fav-heart {
    position: absolute;
    top: 6px;
    right: 10px;
    font-size: 15px;
    line-height: 1;
    text-decoration: none;
    color: var(--accent);
    opacity: 0.85;
    z-index: 2;
    transition: transform .15s ease, opacity .15s ease;
    cursor: pointer;
}
.atree-fav-heart:hover {
    opacity: 1;
    transform: scale(1.2);
}

.atree-series-row {
    display: flex;
    flex-wrap: wrap;
    gap: 14px;
    padding: 12px 0 4px 35px;
}
.atree-series {
    flex: 1 1 230px;
    min-width: 210px;
}

.atree-books {
    margin-top: 8px;
}

details[open] > .atree-series-row,
details[open] > .atree-books {
    animation: atreeReveal .22s ease;
}
@keyframes atreeReveal {
    from { opacity: 0; transform: translateY(-6px); }
    to { opacity: 1; transform: translateY(0); }
}

.atree-author-grid {
    display: grid;
    grid-template-columns: repeat(4, 1fr);
    gap: 14px;
    margin-bottom: 8px;
}
.atree-author-grid .atree-author {
    margin: 0;
}
.atree-author-grid .atree-author[open] {
    grid-column: 1 / -1;
}
.atree-author-grid .atree-pill {
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
}
.atree-author-grid .atree-author[open] .atree-pill {
    white-space: normal;
}

@media (max-width: 900px) {
    .atree-author-grid { grid-template-columns: repeat(2, 1fr); }
}
@media (max-width: 600px) {
    .atree-author-grid { grid-template-columns: 1fr; }
}

.atree-letter-divider {
    display: flex;
    align-items: center;
    gap: 10px;
    margin: 26px 0 10px 0;
}
.atree-letter-divider .letter {
    font-family: "Cormorant Garamond", Georgia, serif;
    font-size: 20px;
    color: var(--accent);
    min-width: 26px;
}
.atree-letter-divider .rule {
    flex: 1;
    height: 1px;
    background: linear-gradient(90deg, var(--line), transparent);
    opacity: 0.6;
}
</style>
"""


def book_pill_html(book):
    """One book's pill — cover thumbnail (if we have one), title,
    status, genre, with a left-edge stripe colored by status.

    The small star in the corner toggles the book's Favorite flag
    via a ?toggle_fav=<row id> link — raw HTML injected through
    st.html has no other way to call back into the Python app
    without reintroducing a real Streamlit widget per book (which
    is what the whole tree structure below is built to avoid)."""

    title = html.escape(str(book.get('Title', '')))
    status = html.escape(str(book.get('Status', '') or ''))
    genre = html.escape(str(book.get('Genre', '') or ''))
    cover = str(book.get('Cover', '') or '')

    label = f'📖 {title}'
    if status:
        label += f' — {status}'
    if genre:
        label += f' · {genre}'

    stripe_color = status_stripe_color(book.get('Status', ''))

    row_id = book.name if book.name is not None else ''
    is_favorite = bool(book.get('Favorite', False))
    heart_symbol = "★" if is_favorite else "☆"
    heart_html = (
        f'<a class="atree-fav-heart" href="?toggle_fav={row_id}" '
        f'title="Toggle favorite">{heart_symbol}</a>'
    )

    if cover:
        return (
            f'<div class="atree-pill atree-pill-book '
            f'atree-pill-book-cover" '
            f'style="border-left:4px solid {stripe_color};">'
            f'{heart_html}'
            f'<img class="atree-cover" '
            f'src="{html.escape(cover)}" loading="lazy">'
            f'<span>{label}</span>'
            f'</div>'
        )

    return (
        f'<div class="atree-pill atree-pill-book" '
        f'style="border-left:4px solid {stripe_color};">'
        f'{heart_html}'
        f'{label}</div>'
    )


def tree_open_state_script(tree_id):
    return (
        '<svg style="position:absolute;width:0;height:0" '
        'onload="(function(){'
        'try{'
        "var container=document.getElementById('atree-" + tree_id + "');"
        'if(!container)return;'
        'var stored;'
        "try{stored=JSON.parse(localStorage.getItem('storyspire_open_sections')||'[]');}"
        'catch(e){stored=[];}'
        'var openSet=new Set(stored);'
        "var els=container.querySelectorAll('details[data-tkey]');"
        'els.forEach(function(el){'
        "var key=el.getAttribute('data-tkey');"
        "if(openSet.has(key))el.setAttribute('open','');"
        "el.addEventListener('toggle',function(){"
        'try{'
        'var s;'
        "try{s=new Set(JSON.parse(localStorage.getItem('storyspire_open_sections')||'[]'));}"
        'catch(e){s=new Set();}'
        'if(el.open){s.add(key);}else{s.delete(key);}'
        "localStorage.setItem('storyspire_open_sections',JSON.stringify(Array.from(s)));"
        '}catch(e){}'
        '});'
        '});'
        '}catch(e){}'
        '})()" />'
    )


def display_ancestry_tree(df, group_by="Author", tree_id="books"):
    df = clean_author_series(df)

    if group_by == "Genre":
        group_col = clean_genre_column(df["Genre"])
        group_icon = "🏷️"
    else:
        group_col = df["Author"]
        group_icon = "🗼"

    parts = [f'<div class="book-ancestry-tree" id="atree-{tree_id}">']

    for group_value, group_df in df.groupby(group_col):
        group_key = (
            f"{tree_id}:{group_by}:group:"
            f"{html.escape(str(group_value))}"
        )
        parts.append(
            f'<details class="atree-author" data-tkey="{group_key}">'
            f'<summary>'
            f'<span class="atree-pill"><span class="atree-arrow">▸</span>'
            f'{group_icon} {html.escape(str(group_value))} '
            f'({len(group_df)})</span>'
            f'</summary>'
            f'<div class="atree-series-row">'
        )

        series_list = group_df['Series'].unique()

        for series in series_list:
            series_books = group_df[group_df['Series'] == series]
            series_key = f"{group_key}:series:{html.escape(str(series))}"
            parts.append(
                f'<details class="atree-series" data-tkey="{series_key}">'
                f'<summary>'
                f'<span class="atree-pill"><span class="atree-arrow">▸</span>'
                f'📂 {html.escape(str(series))} '
                f'({len(series_books)})</span>'
                f'</summary>'
                f'<div class="atree-books">'
            )
            for _, book in series_books.iterrows():
                parts.append(book_pill_html(book))
            parts.append('</div></details>')

        parts.append('</div></details>')

    parts.append('</div>')
    parts.append(tree_open_state_script(tree_id))

    st.html(TREE_CSS + ''.join(parts))


st.set_page_config(
    page_title="StorySpire",
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="collapsed",
)

THEMES = {
    "Emerald Grimoire": {
        "page": "#051614", "surface": "#0C2B24", "surface2": "#124A3C",
        "card": "#1B6650", "text": "#FFFBEF", "muted": "#B9D4C6",
        "accent": "#F2C14E", "accent2": "#3FCDA8", "line": "#E0972E",
    },
    "Gilded Midnight": {
        "page": "#04101F", "surface": "#0A2242", "surface2": "#123B6E",
        "card": "#1B5493", "text": "#FFF9E8", "muted": "#B7CBE8",
        "accent": "#FFC94D", "accent2": "#4FC3E8", "line": "#E8A426",
    },
    "Velvet Rose": {
        "page": "#170512", "surface": "#2E0A24", "surface2": "#4F1140",
        "card": "#731B5C", "text": "#FFF3F8", "muted": "#E3BFD2",
        "accent": "#FF6F91", "accent2": "#C77DFF", "line": "#E23E75",
    },
    "Autumn Ember": {
        "page": "#1C0D04", "surface": "#361708", "surface2": "#5E2A0C",
        "card": "#873F13", "text": "#FFF4DE", "muted": "#E8C79A",
        "accent": "#FFB238", "accent2": "#FF6A3D", "line": "#D9601F",
    },
    "Moonlit Violet": {
        "page": "#08071A", "surface": "#12103A", "surface2": "#221D66",
        "card": "#362D93", "text": "#FFFAEE", "muted": "#C9C2ED",
        "accent": "#FFD54F", "accent2": "#9D7BFF", "line": "#7A5CE0",
    },
    "Verdant Garden": {
        "page": "#04191C", "surface": "#093733", "surface2": "#0E5652",
        "card": "#157A70", "text": "#FFFAE9", "muted": "#BFE0D6",
        "accent": "#FFCD3C", "accent2": "#FF7A5C", "line": "#E85A3E",
    },
    "Old World Atlas": {
        "page": "#0F1A18", "surface": "#1C2F2A", "surface2": "#2E4C41",
        "card": "#456B55", "text": "#FFF6DC", "muted": "#D2DABF",
        "accent": "#F0BB4E", "accent2": "#B7D25C", "line": "#D68C2E",
    },
    "Arcane Spell": {
        "page": "#080916", "surface": "#151637", "surface2": "#232463",
        "card": "#332F94", "text": "#FFFFFF", "muted": "#C9C9F2",
        "accent": "#FFD23F", "accent2": "#4FE8DD", "line": "#B15CFF",
    },
    "Scarlet Manor": {
        "page": "#180505", "surface": "#340A0A", "surface2": "#5C1010",
        "card": "#831A1A", "text": "#FFF6E8", "muted": "#EFC7B0",
        "accent": "#FFC145", "accent2": "#FF7D5C", "line": "#E33A2E",
    },
    "Obsidian Vale": {
        "page": "#050505", "surface": "#0F0D0D", "surface2": "#1A1616",
        "card": "#241E1E", "text": "#F2EDEA", "muted": "#8C8080",
        "accent": "#8A1F2B", "accent2": "#9C9C9C", "line": "#5C141C",
    },
}

if (
    "theme" not in st.session_state
    or st.session_state.theme not in THEMES
):
    st.session_state.theme = "Emerald Grimoire"

if "library" not in st.session_state:
    st.session_state.library = load_library()

if "toggle_fav" in st.query_params:

    _fav_raw = st.query_params["toggle_fav"]

    try:
        _fav_idx = int(_fav_raw)

        if _fav_idx in st.session_state.library.index:

            _current = bool(
                st.session_state.library.loc[_fav_idx, "Favorite"]
            )

            st.session_state.library.loc[_fav_idx, "Favorite"] = (
                not _current
            )

            save_library(st.session_state.library)

    except (ValueError, TypeError):
        pass

    st.query_params.clear()
    st.rerun()

theme = THEMES[st.session_state.theme]

st.html(
    f"""
    <style>

    @import url(
        'https://fonts.googleapis.com/css2?family=Cormorant+Garamond:wght@600;700&family=Libre+Baskerville:wght@400;700&display=swap'
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
        font-family: "Cormorant Garamond", Georgia, serif !important;
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
        font-family: "Cormorant Garamond", Georgia, serif !important;
        font-size: clamp(48px, 6vw, 76px);
        font-weight: 700;
        color: var(--accent) !important;
        text-shadow: 0 3px 12px rgba(0,0,0,0.35);
        animation: bookTitleRise .6s ease;
    }}

    .book-header-title .title-spire {{
        font-weight: 400;
        color: var(--accent2) !important;
    }}

    @keyframes bookTitleRise {{
        from {{ opacity: 0; transform: translateY(6px); }}
        to {{ opacity: 1; transform: translateY(0); }}
    }}

    .book-header-tagline {{
        font-family: "Libre Baskerville", Georgia, serif !important;
        font-style: italic;
        font-size: 15px;
        color: var(--muted) !important;
        margin-top: 6px;
        animation: bookTitleRise .9s ease;
    }}

    .theme-heading {{
        font-family: "Cormorant Garamond", Georgia, serif;
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
        border-radius: 14px 5px 14px 5px !important;
        font-family: "Libre Baskerville", Georgia, serif !important;
        font-size: 0.85rem !important;
        line-height: 1.2 !important;
        padding: 0.35rem 0.8rem !important;
        min-height: 0 !important;
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
        transform: translateY(-1px) !important;
    }}

    [class*="st-key-statclick_"] {{
        background: var(--card);
        border: 1px solid var(--accent);
        border-radius: 16px;
        box-shadow: 0 4px 12px rgba(0,0,0,.18);
        cursor: pointer;
        transition: transform .15s ease, box-shadow .15s ease;
    }}
    [class*="st-key-statclick_"]:hover {{
        transform: translateY(-2px);
        box-shadow: 0 6px 16px rgba(0,0,0,.24);
    }}
    [class*="st-key-statclick_"] button {{
        background: transparent !important;
        border: none !important;
        box-shadow: none !important;
        color: var(--text) !important;
        font-family: "Libre Baskerville", Georgia, serif !important;
        white-space: pre-line !important;
        line-height: 1.4 !important;
        padding: 16px 6px !important;
        width: 100%;
        cursor: pointer;
    }}
    [class*="st-key-statclick_"] button:hover {{
        background: var(--surface2) !important;
        cursor: pointer;
        transform: none !important;
    }}
    [class*="st-key-statclick_"] button p {{
        font-size: 13px !important;
    }}
    [class*="st-key-statclick_"] button p:first-line {{
        font-family: "Cormorant Garamond", Georgia, serif !important;
        font-size: 26px !important;
        color: var(--accent) !important;
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
        font-family: "Cormorant Garamond", Georgia, serif;
        font-size: 34px;
    }}

    .tree-root-count {{
        font-family: "Libre Baskerville", Georgia, serif;
        font-size: 11px;
    }}

    .stCheckbox label {{
        color: var(--text) !important;
    }}

    </style>
    """
)

st.html(
    """
    <div class="book-header">
        <div class="book-header-title">Story<span class="title-spire">Spire</span></div>
        <div class="book-header-tagline">
            a library that rises one story at a time
        </div>
    </div>
    """
)

st.html(
    '<div class="theme-heading">Choose your library theme</div>'
)

theme_choice = st.selectbox(
    "Library theme",
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


def _http_get_with_backoff(url, params=None, timeout=4, max_retries=2):
    """requests.get with basic exponential backoff on HTTP 429."""

    delay = 0.5

    for attempt in range(max_retries + 1):

        try:
            response = requests.get(url, params=params, timeout=timeout)
        except Exception:
            return None

        if response.status_code == 429 and attempt < max_retries:
            time.sleep(delay)
            delay *= 2
            continue

        return response

    return None


def _metadata_cache():
    """Session-scoped cache of fetch_book_metadata() results."""

    if "book_metadata_cache" not in st.session_state:
        st.session_state.book_metadata_cache = {}

    return st.session_state.book_metadata_cache


def fetch_book_metadata(title, author="", isbn=""):
    """Fetch cover, description, genre, publisher, and page count
    for one book in a single external request wherever possible."""

    isbn = clean_isbn(isbn)
    clean_title = clean_title_for_lookup(title)

    cache_key = isbn if isbn else f"{clean_title.lower()}|{str(author).lower()}"

    cache = _metadata_cache()

    if cache_key in cache:
        return cache[cache_key]

    result = {
        "cover": "",
        "description": "",
        "genre": "",
        "publisher": "",
        "pages": "",
    }

    query = f"isbn:{isbn}" if isbn else f"{clean_title} {author}"

    response = _http_get_with_backoff(
        "https://www.googleapis.com/books/v1/volumes",
        params={"q": query, "maxResults": 1},
        timeout=4,
    )

    if response is not None and response.status_code == 200:

        items = response.json().get("items", [])

        if items:

            info = items[0].get("volumeInfo", {})

            image = info.get("imageLinks", {}).get("thumbnail")
            if image:
                result["cover"] = image.replace("http://", "https://")

            description = info.get("description", "")
            if description:
                result["description"] = description.strip()

            categories = info.get("categories", [])
            if categories:
                genre = str(categories[0]).split("/")[0].strip()
                if genre:
                    result["genre"] = genre

            publisher = info.get("publisher", "")
            if publisher:
                result["publisher"] = publisher.strip()

            page_count = info.get("pageCount")
            if page_count:
                result["pages"] = page_count

    if not result["cover"] or not result["genre"]:

        ol_response = _http_get_with_backoff(
            "https://openlibrary.org/search.json",
            params={
                "title": clean_title,
                "author": author,
                "fields": "cover_i,subject",
                "limit": 1,
            },
            timeout=4,
        )

        if ol_response is not None and ol_response.status_code == 200:

            docs = ol_response.json().get("docs", [])

            if docs:

                if not result["cover"]:
                    cover_id = docs[0].get("cover_i")
                    if cover_id:
                        result["cover"] = (
                            "https://covers.openlibrary.org/"
                            f"b/id/{cover_id}-L.jpg"
                        )

                if not result["genre"]:
                    subjects = docs[0].get("subject", [])
                    if subjects:
                        genre = str(subjects[0]).strip()
                        if genre:
                            result["genre"] = genre

    cache[cache_key] = result

    return result


def get_cover(title, author="", isbn=""):
    return fetch_book_metadata(title, author, isbn).get("cover", "")


def get_description(title, author=""):
    return fetch_book_metadata(title, author, "").get("description", "")


def get_genre(title, author=""):
    return fetch_book_metadata(title, author, "").get("genre", "")


def fetch_row_metadata(
    title,
    author,
    isbn,
    current_genre,
    want_cover,
    want_description,
    want_genre,
):
    """Fetch cover / description / genre for one row in a single
    worker call."""

    if not (want_cover or want_description or want_genre):
        return "", "", ""

    metadata = fetch_book_metadata(title, author, isbn)

    cover = metadata["cover"] if want_cover else ""
    description = metadata["description"] if want_description else ""

    genre = ""
    if want_genre and not str(current_genre).strip():
        genre = metadata["genre"]

    return cover, description, genre


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


def clean_title_for_lookup(title):
    """Strip Goodreads-style series annotations before an API search."""

    text = str(title)

    patterns = [
        r"\([^()]*#\s*\d+(?:\.\d+)?[^()]*\)",
        r"\[[^\[\]]*#\s*\d+(?:\.\d+)?[^\[\]]*\]",
        r"\([^()]*\bBook\s+\d+(?:\.\d+)?[^()]*\)",
        r"\[[^\[\]]*\bBook\s+\d+(?:\.\d+)?[^\[\]]*\]",
    ]

    for pattern in patterns:
        text = re.sub(pattern, "", text, flags=re.IGNORECASE)

    return re.sub(r"\s+", " ", text).strip(" ,-:")


def safe_id(text):

    return re.sub(
        r"[^a-zA-Z0-9_-]",
        "_",
        str(text),
    )


STATUS_STRIPE = {
    "Read": "var(--accent2)",
    "Currently Reading": "var(--accent)",
    "Want to Read": "var(--muted)",
}


def status_stripe_color(status):
    return STATUS_STRIPE.get(str(status).strip(), "var(--muted)")


def load_dataframe(uploaded_file):
    """Returns a pandas DataFrame with at least a Title column,
    or None (with st.error already shown) if it couldn't be read."""

    name = uploaded_file.name.lower()

    if name.endswith(".csv"):
        try:
            uploaded_file.seek(0)
            return pd.read_csv(uploaded_file, low_memory=False)
        except Exception:
            try:
                uploaded_file.seek(0)
                return pd.read_csv(
                    uploaded_file,
                    encoding="latin-1",
                    low_memory=False,
                )
            except Exception as error:
                st.error(f"Could not read this CSV file: {error}")
                return None

    elif name.endswith((".xlsx", ".xls")):
        try:
            uploaded_file.seek(0)
            return pd.read_excel(uploaded_file)
        except Exception as error:
            st.error(f"Could not read this Excel file: {error}")
            return None

    elif name.endswith(".txt"):
        try:
            uploaded_file.seek(0)
            raw = uploaded_file.read().decode("utf-8", errors="ignore")
            rows = []
            for line in raw.splitlines():
                line = line.strip()
                if not line:
                    continue
                parts = re.split(
                    r"\s+-\s+|\s+by\s+",
                    line,
                    maxsplit=1,
                    flags=re.IGNORECASE,
                )
                if len(parts) == 2:
                    rows.append(
                        {"Title": parts[0].strip(), "Author": parts[1].strip()}
                    )
                else:
                    rows.append({"Title": line, "Author": ""})
            if not rows:
                st.error("No lines found in this text file.")
                return None
            return pd.DataFrame(rows)
        except Exception as error:
            st.error(f"Could not read this text file: {error}")
            return None

    elif name.endswith(".pdf"):
        try:
            uploaded_file.seek(0)
            import pypdf

            reader = pypdf.PdfReader(uploaded_file)
            lines = []
            for page in reader.pages:
                text = page.extract_text() or ""
                lines.extend(text.splitlines())

            rows = []
            for line in lines:
                line = line.strip()
                if not line or len(line) < 3:
                    continue
                parts = re.split(
                    r"\s+-\s+|\s+by\s+",
                    line,
                    maxsplit=1,
                    flags=re.IGNORECASE,
                )
                if len(parts) == 2:
                    rows.append(
                        {"Title": parts[0].strip(), "Author": parts[1].strip()}
                    )
                else:
                    rows.append({"Title": line, "Author": ""})

            if not rows:
                st.error("No readable text found in this PDF.")
                return None
            return pd.DataFrame(rows)
        except ImportError:
            st.error(
                "PDF import needs the `pypdf` package — "
                "add `pypdf` to requirements.txt."
            )
            return None
        except Exception as error:
            st.error(f"Could not read this PDF file: {error}")
            return None

    else:
        st.error("Unsupported file type.")
        return None


def import_books(
    uploaded_file,
    fetch_covers=True,
    fetch_descriptions=False,
    fetch_genres=False,
    merge=True,
):

    df = load_dataframe(uploaded_file)

    if df is None:
        return {"success": False}

    columns = {
        str(column).strip().lower(): column
        for column in df.columns
    }

    def find_column(names):

        for name in names:

            if name.lower() in columns:
                return columns[name.lower()]

        return None

    title_col = find_column(["title", "book title"])
    author_col = find_column(["author", "authors"])
    isbn13_col = find_column(["isbn13", "isbn 13"])
    isbn_col = find_column(["isbn"])
    rating_col = find_column(["my rating", "rating"])
    shelf_col = find_column(["exclusive shelf", "shelf", "status"])
    genre_col = find_column(["genre", "genres", "primary genre", "genre(s)"])
    series_col = find_column(["series", "series name"])
    series_number_col = find_column(["series number", "series no", "book number"])
    tags_col = find_column(["tags", "keywords", "themes"])

    if not title_col:

        st.error(
            "I couldn't find a Title column in this file."
        )

        st.write(
            "Columns found in your file:"
        )

        return {"success": False}

    books = []

    for _, row in df.iterrows():

        title = str(row.get(title_col, "")).strip()

        if not title or title.lower() == "nan":
            continue

        author = "Unknown Author"

        if author_col:
            author = str(row.get(author_col, "")).strip()

        if not author or author.lower() == "nan":
            author = "Unknown Author"

        isbn13 = (
            clean_isbn(row.get(isbn13_col, ""))
            if isbn13_col
            else ""
        )

        isbn10 = (
            clean_isbn(row.get(isbn_col, ""))
            if isbn_col
            else ""
        )

        isbn = isbn13 or isbn10

        genre = ""

        if genre_col:
            genre = str(row.get(genre_col, "")).strip()
            if genre.lower() == "nan":
                genre = ""

        tags = ""

        if tags_col:
            tags = str(row.get(tags_col, "")).strip()
            if tags.lower() == "nan":
                tags = ""

        if series_col:

            series = str(row.get(series_col, "")).strip()

            if not series or series.lower() == "nan":
                series = detect_series(title)

        else:

            series = detect_series(title)

        if not series:
            series = "Standalone"

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

                value = row.get(rating_col)

                if pd.notna(value):

                    parsed_rating = float(value)

                    if parsed_rating > 0:
                        rating = parsed_rating

            except Exception:
                pass

        status = "Want to Read"

        if shelf_col:

            shelf = str(row.get(shelf_col, "")).strip().lower()

            if "currently" in shelf or "currently-reading" in shelf:
                status = "Currently Reading"

            elif (
                shelf == "read"
                or shelf == "finished"
                or ("read" in shelf and "to-read" not in shelf)
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
                "Tags": tags,
                "Publisher": "",
                "Pages": "",
                "Date Read": "",
            }
        )

    imported_df = pd.DataFrame(books)

    if imported_df.empty:
        st.error("No books were found in the file.")
        return {"success": False}

    existing = st.session_state.library.copy()

    def make_key(title, author):
        return (
            str(title).strip().lower(),
            str(author).strip().lower(),
        )

    if merge and not existing.empty:

        existing_keys = {
            make_key(t, a)
            for t, a in zip(existing["Title"], existing["Author"])
        }

        is_new_mask = imported_df.apply(
            lambda row: make_key(row["Title"], row["Author"]) not in existing_keys,
            axis=1,
        )

        new_rows = imported_df[is_new_mask].reset_index(drop=True)

        skipped_count = len(imported_df) - len(new_rows)

        combined = pd.concat([existing, new_rows], ignore_index=True)

        cover_fetch_start = len(existing)

    else:

        new_rows = imported_df
        skipped_count = 0
        combined = imported_df.reset_index(drop=True)
        cover_fetch_start = 0

    added_count = len(new_rows)

    combined = normalize_library_columns(combined)

    st.session_state.library = combined

    save_library(combined)

    if (
        (not fetch_covers and not fetch_descriptions and not fetch_genres)
        or added_count == 0
    ):
        return {
            "success": True,
            "added": added_count,
            "skipped": skipped_count,
        }

    cover_indices = list(
        range(cover_fetch_start, cover_fetch_start + added_count)
    )

    combined["Cover"] = combined["Cover"].astype(object)
    combined["Description"] = combined["Description"].astype(object)
    combined["Genre"] = combined["Genre"].astype(object)

    progress = st.progress(0)

    done = 0

    with ThreadPoolExecutor(max_workers=10) as executor:

        future_to_index = {
            executor.submit(
                fetch_row_metadata,
                combined.loc[i, "Title"],
                combined.loc[i, "Author"],
                combined.loc[i, "ISBN"],
                combined.loc[i, "Genre"],
                fetch_covers,
                fetch_descriptions,
                fetch_genres,
            ): i
            for i in cover_indices
        }

        for future in as_completed(future_to_index):

            i = future_to_index[future]

            try:
                cover, description, genre = future.result()
            except Exception:
                cover, description, genre = "", "", ""

            if fetch_covers:
                combined.loc[i, "Cover"] = cover

            if fetch_descriptions:
                combined.loc[i, "Description"] = description

            if fetch_genres and genre:
                combined.loc[i, "Genre"] = genre

            done += 1

            progress.progress(done / added_count)

    progress.empty()

    st.session_state.library = combined

    save_library(combined)

    return {
        "success": True,
        "added": added_count,
        "skipped": skipped_count,
    }


def fetch_missing_covers():
    """Fetch covers only for rows that don't have one yet."""

    library = st.session_state.library

    library["Cover"] = library["Cover"].astype(object)

    missing = library[library["Cover"].fillna("") == ""]

    if missing.empty:
        st.info("Every book already has a cover.")
        return

    total = len(missing)
    progress = st.progress(0)
    done = 0
    found = 0

    with ThreadPoolExecutor(max_workers=10) as executor:

        future_to_index = {
            executor.submit(
                get_cover,
                library.loc[i, "Title"],
                library.loc[i, "Author"],
                library.loc[i, "ISBN"],
            ): i
            for i in missing.index
        }

        for future in as_completed(future_to_index):
            i = future_to_index[future]
            try:
                cover = future.result()
            except Exception:
                cover = ""
            if cover:
                found += 1
            library.loc[i, "Cover"] = cover
            done += 1
            progress.progress(done / total)

    progress.empty()
    st.session_state.library = library
    save_library(library)

    if found == total:
        st.session_state.fetch_result_message = (
            "success", f"✓ Found covers for all {total} book(s)!"
        )
    elif found:
        st.session_state.fetch_result_message = (
            "warning",
            f"Found covers for {found} of {total} book(s). "
            f"The other {total - found} had no cover available "
            f"from OpenLibrary or Google Books, or the lookup was "
            f"rate-limited — try again in a bit.",
        )
    else:
        st.session_state.fetch_result_message = (
            "error",
            f"Couldn't find covers for any of the {total} "
            f"book(s) checked — neither OpenLibrary nor Google "
            f"Books had matches, or requests are being "
            f"rate-limited. Try again in a bit.",
        )


def fetch_missing_descriptions():
    """Fetch descriptions only for rows that don't have one yet."""

    library = st.session_state.library

    library["Description"] = library["Description"].astype(object)

    missing = library[library["Description"].fillna("") == ""]

    if missing.empty:
        st.info("Every book already has a description.")
        return

    total = len(missing)
    progress = st.progress(0)
    done = 0
    found = 0

    with ThreadPoolExecutor(max_workers=10) as executor:

        future_to_index = {
            executor.submit(
                get_description,
                library.loc[i, "Title"],
                library.loc[i, "Author"],
            ): i
            for i in missing.index
        }

        for future in as_completed(future_to_index):
            i = future_to_index[future]
            try:
                description = future.result()
            except Exception:
                description = ""
            if description:
                found += 1
            library.loc[i, "Description"] = description
            done += 1
            progress.progress(done / total)

    progress.empty()
    st.session_state.library = library
    save_library(library)

    if found == total:
        st.session_state.fetch_result_message = (
            "success", f"✓ Found descriptions for all {total} book(s)!"
        )
    elif found:
        st.session_state.fetch_result_message = (
            "warning",
            f"Found descriptions for {found} of {total} book(s). "
            f"The other {total - found} had none available from "
            f"Google Books, or the lookup was rate-limited — try "
            f"again in a bit.",
        )
    else:
        st.session_state.fetch_result_message = (
            "error",
            f"Couldn't find descriptions for any of the {total} "
            f"book(s) checked — Google Books had no matches, or "
            f"requests are being rate-limited. Try again in a bit.",
        )


def fetch_missing_genres():
    """Fetch genres only for rows that don't have one yet."""

    library = st.session_state.library

    library["Genre"] = library["Genre"].astype(object)

    missing = library[
        library["Genre"].fillna("").astype(str).str.strip() == ""
    ]

    if missing.empty:
        st.info("Every book already has a genre.")
        return

    total = len(missing)
    progress = st.progress(0)
    done = 0
    matched = 0

    with ThreadPoolExecutor(max_workers=10) as executor:

        future_to_index = {
            executor.submit(
                get_genre,
                library.loc[i, "Title"],
                library.loc[i, "Author"],
            ): i
            for i in missing.index
        }

        for future in as_completed(future_to_index):
            i = future_to_index[future]
            try:
                genre = future.result()
            except Exception:
                genre = ""
            if genre:
                library.loc[i, "Genre"] = genre
                matched += 1
            done += 1
            progress.progress(done / total)

    progress.empty()
    st.session_state.library = library
    save_library(library)

    if matched == total:
        st.session_state.fetch_result_message = (
            "success", f"✓ Found genres for all {total} book(s)!"
        )
    elif matched:
        st.session_state.fetch_result_message = (
            "warning",
            f"Found genres for {matched} of {total} book(s). "
            f"The other {total - matched} had no genre data "
            f"available from either Google Books or Open Library "
            f"— those will stay under \"Unknown Genre\" unless "
            f"you set them manually in Edit / Delete.",
        )
    else:
        st.session_state.fetch_result_message = (
            "error",
            f"Couldn't find genre data for any of the {total} "
            f"book(s) checked — neither Google Books nor Open "
            f"Library had matches. This can happen if titles/"
            f"authors are formatted unusually, or if requests are "
            f"being rate-limited.",
        )


library = st.session_state.library

total = len(library)

authors = library["Author"].nunique() if total else 0

series_count = (
    library[library["Series"] != "Standalone"]["Series"].nunique()
    if total
    else 0
)

read_count = (
    len(library[library["Status"] == "Read"]) if total else 0
)

unread_count = (
    len(library[library["Status"] == "Want to Read"]) if total else 0
)

favorites = (
    len(library[library["Favorite"] == True]) if total else 0
)

STAT_FILTER_MAP = {
    "Books": "All",
    "Read": "Read",
    "Unread": "Want to Read",
    "Favorites": "Favorites",
}

STAT_TAB_MAP = {
    "Authors": "tree",
    "Series": "tree",
}

columns = st.columns(6)

stats = [
    (total, "Books"),
    (authors, "Authors"),
    (series_count, "Series"),
    (read_count, "Read"),
    (unread_count, "Unread"),
    (favorites, "Favorites"),
]

for col, (number, label) in zip(columns, stats):

    with col:

        with st.container(key=f"statclick_{safe_id(label)}"):

            if st.button(
                f"{number}\n{label}",
                key=f"stat_btn_{safe_id(label)}",
                use_container_width=True,
            ):
                if label in STAT_FILTER_MAP:
                    st.session_state.stat_filter = STAT_FILTER_MAP[label]
                    st.session_state.active_tab = "books"
                else:
                    st.session_state.active_tab = STAT_TAB_MAP[label]
                    st.session_state.tree_series_only = (label == "Series")
                st.rerun()

if "active_tab" not in st.session_state:
    st.session_state.active_tab = "tree"

NAV_ITEMS = [
    ("tree", "🗼 Book Spire"),
    ("books", "📚 Books"),
    ("add", "➕ Add Book"),
    ("manage", "✏️ Edit / Delete"),
    ("import", "📥 Import"),
]

nav_cols = st.columns(len(NAV_ITEMS))

for nav_col, (tab_key, tab_label) in zip(nav_cols, NAV_ITEMS):

    with nav_col:

        is_active = st.session_state.active_tab == tab_key

        if st.button(
            tab_label,
            key=f"nav_{tab_key}",
            use_container_width=True,
            type="primary" if is_active else "secondary",
        ):
            st.session_state.active_tab = tab_key
            st.rerun()

st.html('<div style="height:14px;"></div>')


def render_tree_grid_html(filtered, group_by="Author", tree_id="spire"):

    parts = [f'<div class="book-ancestry-tree" id="atree-{tree_id}">']

    if group_by == "Genre":
        group_series = clean_genre_column(filtered["Genre"])
        group_icon = "🏷️"
    else:
        group_series = filtered["Author"]
        group_icon = "🗼"

    group_list = sorted(
        group_series.unique(),
        key=lambda x: str(x).lower(),
    )

    letter_groups = []
    for group_value in group_list:
        letter = str(group_value).strip()[:1].upper() or "#"
        if not letter_groups or letter_groups[-1][0] != letter:
            letter_groups.append((letter, []))
        letter_groups[-1][1].append(group_value)

    for letter, group_values in letter_groups:

        parts.append(
            f'<div class="atree-letter-divider">'
            f'<span class="letter">{html.escape(letter)}</span>'
            f'<span class="rule"></span>'
            f'</div>'
        )

        parts.append('<div class="atree-author-grid">')

        for group_value in group_values:

            group_books = filtered[group_series == group_value]

            group_key = (
                f"{tree_id}:{group_by}:group:"
                f"{html.escape(str(group_value))}"
            )

            parts.append(
                f'<details class="atree-author" data-tkey="{group_key}">'
                f'<summary>'
                f'<span class="atree-pill">'
                f'<span class="atree-arrow">▸</span>'
                f'{group_icon} {html.escape(str(group_value))} '
                f'({len(group_books)})</span>'
                f'</summary>'
                f'<div class="atree-series-row">'
            )

            series_list = sorted(
                group_books["Series"].unique(),
                key=lambda x: str(x).lower(),
            )

            for series in series_list:

                series_books = group_books[group_books["Series"] == series]

                display_series = (
                    "STANDALONE" if series == "Standalone" else str(series)
                )

                series_key = f"{group_key}:series:{html.escape(str(series))}"

                parts.append(
                    f'<details class="atree-series" data-tkey="{series_key}">'
                    f'<summary>'
                    f'<span class="atree-pill">'
                    f'<span class="atree-arrow">▸</span>'
                    f'{html.escape(display_series)} '
                    f'({len(series_books)})</span>'
                    f'</summary>'
                    f'<div class="atree-books">'
                )

                for _, book in series_books.iterrows():
                    parts.append(book_pill_html(book))

                parts.append('</div></details>')

            parts.append('</div></details>')

        parts.append('</div>')

    parts.append('</div>')
    parts.append(tree_open_state_script(tree_id))

    return ''.join(parts)


if st.session_state.active_tab == "tree":

    st.subheader("Search My Spire")

    search = st.text_input(
        "Search",
        placeholder="Search by author, title, series, genre, tag, theme, or ISBN...",
        label_visibility="collapsed",
    )

    st.caption(
        "Searches authors, titles, series, genres, tags, "
        "descriptions, and ISBNs — try a theme like \"Christmas\"."
    )

    filter_col, group_col_ui = st.columns(2)

    with filter_col:

        tree_status_choice = st.radio(
            "Show",
            ["All Books", "Read", "Unread"],
            horizontal=True,
            key="tree_status_radio",
        )

    with group_col_ui:

        tree_group_choice = st.radio(
            "Organize by",
            ["Author", "Genre"],
            horizontal=True,
            key="tree_group_by_radio",
        )

    series_only = st.session_state.pop("tree_series_only", False)

    filtered = library.copy()

    if series_only:

        series_values = filtered["Series"].fillna("").astype(str).str.strip()

        filtered = filtered[
            ~series_values.isin(["", "nan", "None", "Standalone"])
        ]

        st.caption("Showing books that belong to a series only.")

    if tree_status_choice == "Read":
        filtered = filtered[filtered["Status"] == "Read"]

    elif tree_status_choice == "Unread":
        filtered = filtered[filtered["Status"] != "Read"]

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
            + filtered["Tags"].fillna("").astype(str)
            + " "
            + filtered["Description"].fillna("").astype(str)
            + " "
            + filtered["ISBN"].fillna("").astype(str)
        ).str.lower()

        filtered = filtered[
            searchable.str.contains(q, na=False, regex=False)
        ]

    if filtered.empty:

        if library.empty:

            st.info(
                "Your spire is just a foundation — import your "
                "library or add your first book to help it rise."
            )

        else:

            if search.strip():
                st.info(f'No books matched "{search}".')
            else:
                st.info(f"No books found for \"{tree_status_choice}\".")

    else:

        filtered = clean_author_series(filtered)

        root_label = {
            "All Books": "🗼 MY LIBRARY",
            "Read": "🗼 MY READ BOOKS",
            "Unread": "🗼 MY UNREAD BOOKS",
        }[tree_status_choice]

        st.html(
            f"""
            <div style="
                text-align:center;
                margin:20px auto 25px auto;
            ">
                <div style="
                    display:inline-block;
                    padding:10px 30px;
                    background:var(--accent);
                    color:var(--page);
                    border-radius:5px 20px 5px 20px;
                    font-family:'Cormorant Garamond', Georgia, serif;
                    font-size:24px;
                    box-shadow:0 4px 12px rgba(0,0,0,.18);
                ">
                    {root_label}
                </div>
            </div>
            """
        )

        st.html(
            TREE_CSS
            + render_tree_grid_html(filtered, group_by=tree_group_choice)
        )


elif st.session_state.active_tab == "books":

    if "fetch_result_message" in st.session_state:

        _msg_type, _msg_text = st.session_state.pop("fetch_result_message")

        if _msg_type == "success":
            st.success(_msg_text)
        elif _msg_type == "warning":
            st.warning(_msg_text)
        else:
            st.error(_msg_text)

    if "stat_filter" in st.session_state:
        st.session_state["unique_books_radio"] = st.session_state.pop("stat_filter")

    if library.empty:

        st.info("No books yet.")

    else:

        books_search = st.text_input(
            "Search books",
            placeholder="Search by author, title, series, genre, tag, theme, or ISBN...",
            label_visibility="collapsed",
            key="books_search_input",
        )

        filter_col2, group_col_ui2 = st.columns(2)

        with filter_col2:

            choice = st.radio(
                "Show",
                ["All", "Favorites", "Read", "Currently Reading", "Want to Read"],
                horizontal=True,
                key="unique_books_radio",
            )

        with group_col_ui2:

            books_group_choice = st.radio(
                "Organize by",
                ["Author", "Genre"],
                horizontal=True,
                key="books_group_by_radio",
            )

        books = library.copy()

        if choice == "Favorites":
            books = books[books["Favorite"] == True]

        elif choice != "All":
            books = books[books["Status"] == choice]

        if books_search.strip():

            q = books_search.strip().lower()

            searchable = (
                books["Title"].fillna("").astype(str)
                + " "
                + books["Author"].fillna("").astype(str)
                + " "
                + books["Series"].fillna("").astype(str)
                + " "
                + books["Genre"].fillna("").astype(str)
                + " "
                + books["Tags"].fillna("").astype(str)
                + " "
                + books["Description"].fillna("").astype(str)
                + " "
                + books["ISBN"].fillna("").astype(str)
            ).str.lower()

            books = books[searchable.str.contains(q, na=False, regex=False)]

        if books.empty:

            st.info(f'No books matched "{books_search}".')

        else:

            display_ancestry_tree(books, group_by=books_group_choice)

            missing_covers = len(books[books["Cover"].fillna("") == ""])
            missing_descriptions = len(books[books["Description"].fillna("") == ""])
            missing_genres = len(
                books[books["Genre"].fillna("").astype(str).str.strip() == ""]
            )

            if missing_covers or missing_descriptions or missing_genres:

                fetch_col1, fetch_col2, fetch_col3 = st.columns(3)

                with fetch_col1:

                    if missing_covers:

                        st.caption(
                            f"{missing_covers} book(s) shown here have no cover yet."
                        )

                        if st.button(
                            "🖼️ Fetch missing covers",
                            key="fetch_missing_covers_btn",
                        ):
                            with st.spinner("Looking up covers..."):
                                fetch_missing_covers()
                            st.rerun()

                with fetch_col2:

                    if missing_descriptions:

                        st.caption(
                            f"{missing_descriptions} book(s) shown "
                            f"here have no description yet — "
                            f"needed for topic search."
                        )

                        if st.button(
                            "📝 Fetch missing descriptions",
                            key="fetch_missing_descriptions_btn",
                        ):
                            with st.spinner("Looking up descriptions..."):
                                fetch_missing_descriptions()
                            st.rerun()

                with fetch_col3:

                    if missing_genres:

                        st.caption(
                            f"{missing_genres} book(s) shown here "
                            f"have no genre yet — that's why they're "
                            f"grouped under \"Unknown Genre\"."
                        )

                        if st.button(
                            "🏷️ Fetch missing genres",
                            key="fetch_missing_genres_btn",
                        ):
                            with st.spinner("Looking up genres..."):
                                fetch_missing_genres()
                            st.rerun()


elif st.session_state.active_tab == "add":

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
            value=None,
            step=0.5,
            placeholder="e.g. 1, 2.5...",
        )

        genre = st.text_input(
            "Genre",
            placeholder="Fantasy, Romance, Mystery...",
        )

        tags = st.text_input(
            "Tags",
            placeholder="Christmas, cozy, found family...",
        )

        isbn = st.text_input("ISBN")

        status = st.selectbox(
            "Status",
            ["Want to Read", "Currently Reading", "Read"],
        )

        st.write("Rating")

        star_click = st.feedback("stars", key="add_book_rating")

        rating = star_click + 1 if star_click is not None else None

        favorite = st.checkbox("Favorite")

        submit = st.form_submit_button("Add to My Spire")

        if submit:

            if not title.strip():
                st.error("Please enter a title.")

            elif not author.strip():
                st.error("Please enter an author.")

            else:

                actual_series = series.strip() if series.strip() else "Standalone"

                cover = get_cover(title, author, isbn)
                description = get_description(title, author)

                actual_genre = genre.strip()

                if not actual_genre:
                    actual_genre = get_genre(title, author)

                new_book = {
                    "Title": title.strip(),
                    "Author": author.strip(),
                    "Series": actual_series,
                    "Series Number": number if number is not None else None,
                    "Genre": actual_genre,
                    "ISBN": clean_isbn(isbn),
                    "My Rating": rating,
                    "Status": status,
                    "Favorite": favorite,
                    "Cover": cover,
                    "Description": description,
                    "Tags": tags.strip(),
                    "Publisher": "",
                    "Pages": "",
                    "Date Read": "",
                }

                st.session_state.library = pd.concat(
                    [st.session_state.library, pd.DataFrame([new_book])],
                    ignore_index=True,
                )

                save_library(st.session_state.library)

                st.success(f'"{title}" was added to your spire!')

                st.rerun()


elif st.session_state.active_tab == "manage":

    st.header("Edit / Delete Books")

    if library.empty:

        st.info("No books yet — add or import some first.")

    else:

        st.caption(
            "Edit any cell directly. To delete a book, click "
            "the row number to select it, then press the "
            "trash icon or your Delete key — you'll be asked "
            "to confirm before anything is removed."
        )

        edited = st.data_editor(
            library,
            key="manage_library_editor",
            use_container_width=True,
            num_rows="dynamic",
            column_order=[
                "Title",
                "Author",
                "Series",
                "Series Number",
                "Genre",
                "Tags",
                "Status",
                "My Rating",
                "Favorite",
                "ISBN",
            ],
            column_config={
                "Status": st.column_config.SelectboxColumn(
                    "Status",
                    options=["Want to Read", "Currently Reading", "Read"],
                ),
                "My Rating": st.column_config.NumberColumn(
                    "My Rating", min_value=0, max_value=5, step=1,
                ),
                "Series Number": st.column_config.NumberColumn(
                    "Series #", min_value=0, step=0.5,
                ),
                "Favorite": st.column_config.CheckboxColumn("Favorite"),
            },
        )

        new_row_mask = ~edited.index.isin(library.index)

        blank_new_mask = new_row_mask & (
            edited["Title"].fillna("").astype(str).str.strip() == ""
        )

        edited_clean = edited[~blank_new_mask]

        removed_indices = sorted(set(library.index) - set(edited_clean.index))

        if removed_indices:

            removed_titles = library.loc[removed_indices, "Title"].tolist()

            st.warning(
                "You're about to delete: "
                + ", ".join(f'"{t}"' for t in removed_titles)
            )

            confirm_col, cancel_col = st.columns(2)

            with confirm_col:

                if st.button(
                    "🗑️ Confirm delete",
                    key="manage_confirm_delete",
                    type="primary",
                    use_container_width=True,
                ):

                    final = normalize_library_columns(
                        edited_clean.reset_index(drop=True)
                    )

                    st.session_state.library = final
                    save_library(final)

                    del st.session_state["manage_library_editor"]

                    st.rerun()

            with cancel_col:

                if st.button(
                    "Cancel",
                    key="manage_cancel_delete",
                    use_container_width=True,
                ):

                    del st.session_state["manage_library_editor"]

                    st.rerun()

        elif not edited_clean.equals(library):

            final = normalize_library_columns(edited_clean.reset_index(drop=True))

            st.session_state.library = final
            save_library(final)
            st.rerun()


elif st.session_state.active_tab == "import":

    st.header("Import Your Library")

    st.write(
        "Upload a Goodreads CSV, StoryGraph export, Excel "
        "spreadsheet, plain text list, or PDF book list."
    )

    st.caption(
        "Text and PDF files: one book per line, formatted as "
        "\"Title\", \"Title - Author\", or \"Title by Author\"."
    )

    uploaded = st.file_uploader(
        "Choose a file",
        type=["csv", "xlsx", "xls", "pdf", "txt"],
        key="book_library_uploader",
    )

    if uploaded is not None:

        st.success(f"✓ {uploaded.name} uploaded successfully")
        st.caption(f"File size: {uploaded.size:,} bytes")

        import_mode = "Merge with my existing library"

        if not st.session_state.library.empty:

            import_mode = st.radio(
                "How should this import be applied?",
                [
                    "Merge with my existing library",
                    "Replace my entire library with this file",
                ],
                index=0,
                key="import_mode_radio",
            )

            if import_mode == "Merge with my existing library":
                st.caption(
                    "Books already in your library (matched by "
                    "title + author) are left untouched — "
                    "favorites, ratings, and covers you've set "
                    "won't be overwritten. Only new books from "
                    "this file are added."
                )
            else:
                st.caption(
                    "⚠️ This removes every book currently in "
                    "your library and replaces it with only "
                    "what's in this file."
                )

        fetch_covers_now = st.checkbox(
            "Fetch cover art during import (slower — you can "
            "fetch covers later from the Books tab instead)",
            value=False,
        )

        fetch_descriptions_now = st.checkbox(
            "Fetch descriptions during import (slower — powers "
            "topic search like \"Christmas\" or \"found family\"; "
            "you can fetch these later from the Books tab instead)",
            value=False,
        )

        fetch_genres_now = st.checkbox(
            "Fetch genres during import (slower — most files "
            "(like Goodreads exports) don't include genre data, "
            "so without this every book groups under \"Unknown "
            "Genre\"; you can fetch these later from the Books "
            "tab instead)",
            value=False,
        )

        if st.button(
            "🗼 Raise My Spire",
            use_container_width=True,
            type="primary",
        ):

            merge_choice = import_mode == "Merge with my existing library"

            with st.spinner("Reading your book list..."):

                result = import_books(
                    uploaded,
                    fetch_covers=fetch_covers_now,
                    fetch_descriptions=fetch_descriptions_now,
                    fetch_genres=fetch_genres_now,
                    merge=merge_choice,
                )

            if result.get("success"):

                added = result.get("added", 0)
                skipped = result.get("skipped", 0)

                if merge_choice and skipped:

                    st.success(
                        f"✓ Added {added} new book(s). "
                        f"Skipped {skipped} already in your library."
                    )

                else:

                    st.success(f"✓ Successfully imported {added} book(s)!")

                st.rerun()
