import streamlit as st
import pandas as pd
import requests
import re
import html
from concurrent.futures import ThreadPoolExecutor, as_completed


# ============================================================
# ANCESTRY TREE (Books tab) — now with covers
# ============================================================

def display_ancestry_tree(df):
    # 1. Clean data: Fill empty Series with 'Standalone'
    df = df.copy()
    df['Series'] = df['Series'].fillna('Standalone').astype(str).replace(
        ['', 'nan', 'None'], 'Standalone'
    )

    # Build the entire tree as ONE html string instead of looping
    # st.expander / st.columns / st.write per author/series/book.
    # Each Streamlit widget call used to add several wrapper <div>s
    # (stLayoutWrapper, stVerticalBlock, stHorizontalBlock,
    # stElementContainer) — with hundreds of books that multiplied
    # into tens of thousands of DOM nodes. <details>/<summary> gives
    # native collapse/expand for free, with no JS and no extra nodes.
    parts = ['<div class="book-ancestry-tree">']

    for author, author_df in df.groupby('Author'):
        parts.append(
            f'<details class="atree-author">'
            f'<summary>'
            f'<span class="atree-pill">🌳 {html.escape(str(author))} '
            f'({len(author_df)})</span>'
            f'</summary>'
            f'<div class="atree-series-row">'
        )

        series_list = author_df['Series'].unique()

        for series in series_list:
            series_books = author_df[author_df['Series'] == series]
            parts.append(
                f'<details class="atree-series">'
                f'<summary>'
                f'<span class="atree-pill">📂 '
                f'{html.escape(str(series))} '
                f'({len(series_books)})</span>'
                f'</summary>'
                f'<div class="atree-books">'
            )
            for _, book in series_books.iterrows():
                title = html.escape(str(book.get('Title', '')))
                status = html.escape(str(book.get('Status', '') or ''))
                genre = html.escape(str(book.get('Genre', '') or ''))
                cover = str(book.get('Cover', '') or '')

                label = f'📖 {title}'
                if status:
                    label += f' — {status}'
                if genre:
                    label += f' · {genre}'

                stripe_color = status_stripe_color(
                    book.get('Status', '')
                )

                if cover:
                    parts.append(
                        f'<div class="atree-pill atree-pill-book '
                        f'atree-pill-book-cover" '
                        f'style="border-left:4px solid {stripe_color};">'
                        f'<img class="atree-cover" '
                        f'src="{html.escape(cover)}" loading="lazy">'
                        f'<span>{label}</span>'
                        f'</div>'
                    )
                else:
                    parts.append(
                        f'<div class="atree-pill atree-pill-book" '
                        f'style="border-left:4px solid {stripe_color};">'
                        f'{label}</div>'
                    )
            parts.append('</div></details>')

        parts.append('</div></details>')

    parts.append('</div>')

    st.html(
        f"""
        <style>
        /* All three tree levels (author / series / book) share one
           identical pill style: same size, same font, same shape. */

        .book-ancestry-tree summary {{
            cursor: pointer;
            list-style: none;
        }}
        .book-ancestry-tree summary::-webkit-details-marker {{
            display: none;
        }}
        .book-ancestry-tree summary::marker {{
            content: "";
        }}

        .atree-author {{
            margin: 22px 0;
        }}

        .atree-pill {{
            display: block;
            width: 100%;
            box-sizing: border-box;
            background: linear-gradient(
                135deg, var(--surface), var(--surface2)
            );
            color: var(--text);
            border: 1px solid var(--surface2);
            border-radius: 12px 5px 12px 5px;
            font-family: "Libre Baskerville", Georgia, serif;
            font-size: 1rem;
            box-shadow: 0 2px 6px rgba(0,0,0,.12);
            padding: 0.5rem 1rem;
            transition: all .15s ease;
        }}
        .atree-pill:hover {{
            background: linear-gradient(
                135deg, var(--surface2), var(--card)
            );
            border-color: var(--accent);
            box-shadow: 0 3px 10px rgba(0,0,0,.2);
        }}
        summary .atree-pill {{
            cursor: pointer;
        }}
        .atree-pill-book {{
            margin: 6px 0;
        }}
        .atree-pill-book-cover {{
            display: flex;
            align-items: center;
            gap: 10px;
        }}
        .atree-cover {{
            width: 36px;
            height: 52px;
            object-fit: cover;
            border-radius: 3px 8px 3px 8px;
            border: 1px solid var(--accent);
            flex-shrink: 0;
        }}

        .atree-series-row {{
            display: flex;
            flex-wrap: wrap;
            gap: 14px;
            padding: 12px 0 4px 35px;
        }}
        .atree-series {{
            flex: 1 1 230px;
            min-width: 210px;
        }}

        .atree-books {{
            margin-top: 8px;
        }}
        </style>
        {''.join(parts)}
        """
    )


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
    "Emerald Grimoire": {
        "page": "#051614",
        "surface": "#0C2B24",
        "surface2": "#124A3C",
        "card": "#1B6650",
        "text": "#FFFBEF",
        "muted": "#B9D4C6",
        "accent": "#F2C14E",
        "accent2": "#3FCDA8",
        "line": "#E0972E",
    },
    "Gilded Midnight": {
        "page": "#04101F",
        "surface": "#0A2242",
        "surface2": "#123B6E",
        "card": "#1B5493",
        "text": "#FFF9E8",
        "muted": "#B7CBE8",
        "accent": "#FFC94D",
        "accent2": "#4FC3E8",
        "line": "#E8A426",
    },
    "Velvet Rose": {
        "page": "#170512",
        "surface": "#2E0A24",
        "surface2": "#4F1140",
        "card": "#731B5C",
        "text": "#FFF3F8",
        "muted": "#E3BFD2",
        "accent": "#FF6F91",
        "accent2": "#C77DFF",
        "line": "#E23E75",
    },
    "Autumn Ember": {
        "page": "#1C0D04",
        "surface": "#361708",
        "surface2": "#5E2A0C",
        "card": "#873F13",
        "text": "#FFF4DE",
        "muted": "#E8C79A",
        "accent": "#FFB238",
        "accent2": "#FF6A3D",
        "line": "#D9601F",
    },
    "Moonlit Violet": {
        "page": "#08071A",
        "surface": "#12103A",
        "surface2": "#221D66",
        "card": "#362D93",
        "text": "#FFFAEE",
        "muted": "#C9C2ED",
        "accent": "#FFD54F",
        "accent2": "#9D7BFF",
        "line": "#7A5CE0",
    },
    "Verdant Garden": {
        "page": "#04191C",
        "surface": "#093733",
        "surface2": "#0E5652",
        "card": "#157A70",
        "text": "#FFFAE9",
        "muted": "#BFE0D6",
        "accent": "#FFCD3C",
        "accent2": "#FF7A5C",
        "line": "#E85A3E",
    },
    "Old World Atlas": {
        "page": "#0F1A18",
        "surface": "#1C2F2A",
        "surface2": "#2E4C41",
        "card": "#456B55",
        "text": "#FFF6DC",
        "muted": "#D2DABF",
        "accent": "#F0BB4E",
        "accent2": "#B7D25C",
        "line": "#D68C2E",
    },
    "Arcane Spell": {
        "page": "#080916",
        "surface": "#151637",
        "surface2": "#232463",
        "card": "#332F94",
        "text": "#FFFFFF",
        "muted": "#C9C9F2",
        "accent": "#FFD23F",
        "accent2": "#4FE8DD",
        "line": "#B15CFF",
    },
    "Scarlet Manor": {
        "page": "#180505",
        "surface": "#340A0A",
        "surface2": "#5C1010",
        "card": "#831A1A",
        "text": "#FFF6E8",
        "muted": "#EFC7B0",
        "accent": "#FFC145",
        "accent2": "#FF7D5C",
        "line": "#E33A2E",
    },
    "Obsidian Vale": {
        "page": "#050505",
        "surface": "#0F0D0D",
        "surface2": "#1A1616",
        "card": "#241E1E",
        "text": "#F2EDEA",
        "muted": "#8C8080",
        "accent": "#8A1F2B",
        "accent2": "#9C9C9C",
        "line": "#5C141C",
    },
}

# ============================================================
# SESSION STATE
# ============================================================

if (
    "theme" not in st.session_state
    or st.session_state.theme not in THEMES
):
    st.session_state.theme = "Emerald Grimoire"

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
    }}

    /* ---- Clickable stat cards ---- */
    [class*="st-key-stat_"] {{
        background: var(--card);
        border: 1px solid var(--accent);
        border-radius: 16px;
        box-shadow: 0 4px 12px rgba(0,0,0,.18);
    }}
    [class*="st-key-stat_"] button {{
        background: transparent !important;
        border: none !important;
        box-shadow: none !important;
        color: var(--text) !important;
        font-family: "Libre Baskerville", Georgia, serif !important;
        white-space: pre-line !important;
        line-height: 1.4 !important;
        padding: 16px 6px !important;
        width: 100%;
    }}
    [class*="st-key-stat_"] button:hover {{
        background: var(--surface2) !important;
        cursor: pointer;
    }}
    [class*="st-key-stat_"] button p {{
        font-size: 13px !important;
    }}
    [class*="st-key-stat_"] button p:first-line {{
        font-family: "Berkshire Swash", Georgia, serif !important;
        font-size: 26px !important;
        color: var(--accent) !important;
    }}

    /* ---- Book Tree: author / series buttons ----
       Quieter than the default .stButton (thinner border, no
       heavy shadow, truncated single-line text so uneven name
       lengths don't create ragged card heights) but still using
       the theme's --line color for the border so cards don't
       wash out flat against the page background. */
    [class*="st-key-tree_author_"] button,
    [class*="st-key-tree_series_"] button {{
        background: var(--surface) !important;
        border: 1px solid var(--line) !important;
        box-shadow: 0 1px 4px rgba(0,0,0,.2) !important;
        border-radius: 10px !important;
        font-size: 0.82rem !important;
        font-weight: 600 !important;
        letter-spacing: 0.2px;
        text-align: left !important;
        white-space: nowrap;
        overflow: hidden;
        text-overflow: ellipsis;
        display: block;
        padding: 0.45rem 0.75rem !important;
    }}
    [class*="st-key-tree_author_"] button:hover,
    [class*="st-key-tree_series_"] button:hover {{
        background: var(--surface2) !important;
        border-color: var(--accent) !important;
        box-shadow: 0 2px 6px rgba(0,0,0,.28) !important;
    }}

    /* ---- Alphabet section dividers on the author grid ---- */
    .atree-letter-divider {{
        display: flex;
        align-items: center;
        gap: 10px;
        margin: 26px 0 10px 0;
    }}
    .atree-letter-divider .letter {{
        font-family: "Berkshire Swash", Georgia, serif;
        font-size: 20px;
        color: var(--accent);
        min-width: 26px;
    }}
    .atree-letter-divider .rule {{
        flex: 1;
        height: 1px;
        background: linear-gradient(
            90deg, var(--line), transparent
        );
        opacity: 0.6;
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
            # HEAD instead of GET — we only need to confirm the
            # cover exists and has real content, not download it
            # here (the <img> tag fetches it again when rendered).
            response = requests.head(
                url,
                timeout=3,
                allow_redirects=True,
            )

            content_length = int(
                response.headers.get("Content-Length", 0)
            )

            if (
                response.status_code == 200
                and content_length > 1000
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
            timeout=4,
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
            timeout=4,
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


# Left-edge stripe color per status, so read/unread/currently
# reading is visible at a glance on every book pill without
# adding extra text or icons — keeps the tree's dropdown
# structure untouched, just adds a quiet visual cue.
STATUS_STRIPE = {
    "Read": "var(--accent2)",
    "Currently Reading": "var(--accent)",
    "Want to Read": "var(--muted)",
}


def status_stripe_color(status):
    return STATUS_STRIPE.get(str(status).strip(), "var(--muted)")


# ============================================================
# FRAGMENT COMPATIBILITY SHIM
# ============================================================
# st.fragment (or the older st.experimental_fragment) makes a
# click inside it only re-render that piece of the page instead
# of the entire app — this is what makes expanding an author or
# series feel instant instead of re-running everything (all
# authors, all covers, the stats row, etc.) on every click. Falls
# back to a no-op decorator on Streamlit versions that don't have
# fragments yet, so the app still runs, just without the speedup.

if hasattr(st, "fragment"):
    fragment = st.fragment
elif hasattr(st, "experimental_fragment"):
    fragment = st.experimental_fragment
else:
    def fragment(func):
        return func


def rerun_fragment():
    """st.rerun(scope='fragment') keeps a rerun local to the
    fragment it's called from, instead of re-running the whole
    app. Older Streamlit versions don't accept the scope kwarg,
    so fall back to a plain rerun there."""
    try:
        st.rerun(scope="fragment")
    except TypeError:
        st.rerun()


# ============================================================
# FILE LOADING — csv, excel, txt, pdf -> DataFrame
# ============================================================

def load_dataframe(uploaded_file):
    """Returns a pandas DataFrame with at least a Title column,
    or None (with st.error already shown) if it couldn't be read."""

    name = uploaded_file.name.lower()

    # ---------------- CSV ----------------
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

    # ---------------- Excel ----------------
    elif name.endswith((".xlsx", ".xls")):
        try:
            uploaded_file.seek(0)
            return pd.read_excel(uploaded_file)
        except Exception as error:
            st.error(f"Could not read this Excel file: {error}")
            return None

    # ---------------- Plain text ----------------
    # One book per line. Supports "Title" or "Title - Author"
    # or "Title by Author".
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

    # ---------------- PDF ----------------
    # One book per line of extracted text, same "Title - Author"
    # / "Title by Author" heuristic as .txt.
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


# ============================================================
# IMPORT BOOKS
# ============================================================

def import_books(uploaded_file, fetch_covers=True):

    # --------------------------------------------------------
    # READ FILE (csv / excel / txt / pdf)
    # --------------------------------------------------------

    df = load_dataframe(uploaded_file)

    if df is None:
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
            "I couldn't find a Title column in this file."
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

    if not fetch_covers:
        return True

    # --------------------------------------------------------
    # FIND COVERS (in parallel — these are independent network
    # calls, so fetching them one at a time serially was the
    # main reason large imports took so long)
    # --------------------------------------------------------

    total_books = len(
        new_library
    )

    progress = st.progress(
        0
    )

    done = 0

    with ThreadPoolExecutor(max_workers=40) as executor:

        future_to_index = {
            executor.submit(
                get_cover,
                new_library.loc[i, "Title"],
                new_library.loc[i, "Author"],
                new_library.loc[i, "ISBN"],
            ): i
            for i in range(total_books)
        }

        for future in as_completed(future_to_index):

            i = future_to_index[future]

            try:
                cover = future.result()
            except Exception:
                cover = ""

            new_library.loc[i, "Cover"] = cover

            done += 1

            progress.progress(
                done / total_books
            )

    progress.empty()

    # --------------------------------------------------------
    # SAVE FINAL LIBRARY
    # --------------------------------------------------------

    st.session_state.library = (
        new_library
    )

    return True


def fetch_missing_covers():
    """Fetch covers only for rows that don't have one yet —
    used by the 'Fetch missing covers' button so a fast
    no-cover import can add covers later without re-importing."""

    library = st.session_state.library

    missing = library[
        library["Cover"].fillna("") == ""
    ]

    if missing.empty:
        st.info("Every book already has a cover.")
        return

    total = len(missing)
    progress = st.progress(0)
    done = 0

    with ThreadPoolExecutor(max_workers=40) as executor:

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
            library.loc[i, "Cover"] = cover
            done += 1
            progress.progress(done / total)

    progress.empty()
    st.session_state.library = library
    st.success(f"✓ Fetched covers for {total} books!")


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

unread_count = (
    len(
        library[
            library["Status"]
            == "Want to Read"
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
# STATS — now clickable, filters the Books tab
# ============================================================

STAT_FILTER_MAP = {
    "Books": "All",
    "Authors": "All",
    "Series": "All",
    "Read": "Read",
    "Unread": "Want to Read",
    "Favorites": "Favorites",
}

columns = st.columns(
    6
)

stats = [
    (total, "Books"),
    (authors, "Authors"),
    (series_count, "Series"),
    (read_count, "Read"),
    (unread_count, "Unread"),
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

        with st.container(key=f"stat_{safe_id(label)}"):

            if st.button(
                f"{number}\n{label}",
                key=f"stat_btn_{safe_id(label)}",
                use_container_width=True,
            ):
                st.session_state.stat_filter = STAT_FILTER_MAP[label]
                st.session_state.active_tab = "books"
                st.rerun()

# ============================================================
# NAV — replaces st.tabs(). Streamlit tabs can't be switched
# by code, which is why clicking a stat card above used to only
# show a "go click the tab yourself" hint. This is a plain
# button row bound to session_state instead, so a stat click
# can jump straight to the Books view with the filter applied.
# ============================================================

if "active_tab" not in st.session_state:
    st.session_state.active_tab = "tree"

NAV_ITEMS = [
    ("tree", "🌳 Book Tree"),
    ("books", "📚 Books"),
    ("add", "➕ Add Book"),
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

# ============================================================
# BOOK TREE — AUTHOR GRID → HORIZONTAL ANCESTRY TREE
# ============================================================

@fragment
def render_author_card(author, filtered):

    author_books = filtered[
        filtered["Author"] == author
    ].copy()

    author_id = safe_id(author)

    author_open = (
        author_id
        in st.session_state.open_authors
    )

    arrow = "▼" if author_open else "▶"

    # ------------------------------------
    # AUTHOR BUTTON
    # ------------------------------------

    if st.button(
        f"{arrow} {author} ({len(author_books)})",
        key=f"tree_author_{author_id}",
        use_container_width=True,
    ):

        if author_open:
            st.session_state.open_authors.discard(
                author_id
            )
        else:
            st.session_state.open_authors.add(
                author_id
            )

        # scope="fragment" keeps this rerun local to this
        # author's card instead of re-rendering the whole
        # page (stats row, nav, every other author card).
        rerun_fragment()

    # ------------------------------------
    # OPEN AUTHOR TREE
    # ------------------------------------

    if author_open:

        # --------------------------------
        # AUTHOR → SERIES CONNECTOR
        # --------------------------------

        st.html(
            """
            <div style="
                width:2px;
                height:20px;
                background:var(--accent);
                margin:auto;
            "></div>
            """
        )

        # --------------------------------
        # SERIES LIST — stacked vertically,
        # one per row, at the FULL width of
        # this author's column. This is what
        # keeps every series button (and every
        # author's series buttons) the same
        # size — they all match the width of
        # the author box above them, instead
        # of being subdivided into extra
        # columns nested inside an already
        # narrow author column (which is what
        # squeezed "Five Packs" into a sliver
        # last time).
        # --------------------------------

        series_list = sorted(
            author_books["Series"].unique(),
            key=lambda x: str(x).lower(),
        )

        for series in series_list:

            series_id = safe_id(
                f"{author}_{series}"
            )

            series_books = author_books[
                author_books["Series"]
                == series
            ].copy()

            series_open = (
                series_id
                in st.session_state.open_series
            )

            series_arrow = (
                "▼"
                if series_open
                else "▶"
            )

            display_series = (
                "STANDALONE"
                if series == "Standalone"
                else str(series)
            )

            # ------------------------
            # SERIES BUTTON
            # ------------------------

            if st.button(
                f"{series_arrow} "
                f"{display_series} "
                f"({len(series_books)})",
                key=f"tree_series_{series_id}",
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

                rerun_fragment()

            # ------------------------
            # BOOKS
            # ------------------------

            if not series_open:
                continue

            st.html(
                """
                <div style="
                    width:2px;
                    height:15px;
                    background:var(--line);
                    margin:auto;
                "></div>
                """
            )

            for _, book in series_books.iterrows():

                title = html.escape(
                    str(
                        book.get(
                            "Title",
                            "",
                        )
                    )
                )

                cover = str(
                    book.get(
                        "Cover",
                        "",
                    )
                    or ""
                )

                status = html.escape(
                    str(
                        book.get(
                            "Status",
                            "",
                        )
                    )
                )

                genre = html.escape(
                    str(
                        book.get(
                            "Genre",
                            "",
                        )
                        or ""
                    )
                )

                meta = status

                if genre:
                    meta += f" · {genre}"

                label = f"📖 {title}"

                if meta:
                    label += f" — {meta}"

                stripe_color = status_stripe_color(
                    book.get("Status", "")
                )

                # ----------------------------
                # BOOK — same pill shape, font,
                # and size as the author/series
                # st.button boxes above. Left
                # edge is colored by status
                # (read / currently reading /
                # want to read) so it's visible
                # at a glance.
                # ----------------------------

                if cover:

                    st.html(
                        f"""
                        <div style="
                            margin:6px 0;
                            padding:0.4rem 0.8rem;
                            box-sizing:border-box;
                            background:
                                linear-gradient(
                                    135deg,
                                    var(--surface),
                                    var(--surface2)
                                );
                            border:
                                1px solid var(--surface2);
                            border-left:
                                4px solid {stripe_color};
                            border-radius:
                                10px 5px 10px 5px;
                            box-shadow:
                                0 2px 6px
                                rgba(0,0,0,.15);
                            display:flex;
                            gap:10px;
                            align-items:center;
                            font-family:
                                'Libre Baskerville',
                                Georgia,
                                serif;
                            font-size:0.85rem;
                            color:var(--text);
                        ">
                            <img
                                src="{html.escape(cover)}"
                                loading="lazy"
                                style="
                                    width:36px;
                                    height:52px;
                                    object-fit:cover;
                                    border-radius:
                                        3px 8px 3px 8px;
                                    border:
                                        1px solid
                                        var(--accent);
                                    flex-shrink:0;
                                "
                            >
                            <span>{label}</span>
                        </div>
                        """
                    )

                else:

                    st.html(
                        f"""
                        <div style="
                            margin:6px 0;
                            padding:0.4rem 0.8rem;
                            box-sizing:border-box;
                            background:
                                linear-gradient(
                                    135deg,
                                    var(--surface),
                                    var(--surface2)
                                );
                            border:
                                1px solid var(--surface2);
                            border-left:
                                4px solid {stripe_color};
                            border-radius:
                                10px 5px 10px 5px;
                            box-shadow:
                                0 2px 6px
                                rgba(0,0,0,.15);
                            font-family:
                                'Libre Baskerville',
                                Georgia,
                                serif;
                            font-size:0.85rem;
                            color:var(--text);
                        ">
                            {label}
                        </div>
                        """
                    )


if st.session_state.active_tab == "tree":

    st.subheader("Search My Book Tree")

    search = st.text_input(
        "Search",
        placeholder="Search by author, title, series, genre, or ISBN...",
        label_visibility="collapsed",
    )

    st.caption(
        "Searches authors, titles, series, genres, and ISBNs."
    )

    tree_status_choice = st.radio(
        "Show",
        [
            "All Books",
            "Read",
            "Unread",
        ],
        horizontal=True,
        key="tree_status_radio",
    )

    filtered = library.copy()

    # --------------------------------------------------------
    # STATUS FILTER (All / Read / Unread)
    # --------------------------------------------------------

    if tree_status_choice == "Read":

        filtered = filtered[
            filtered["Status"] == "Read"
        ]

    elif tree_status_choice == "Unread":

        filtered = filtered[
            filtered["Status"] != "Read"
        ]

    # --------------------------------------------------------
    # SEARCH
    # --------------------------------------------------------

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
    # EMPTY RESULTS
    # --------------------------------------------------------

    if filtered.empty:

        if library.empty:

            st.info(
                "Your tree is empty. Import your library "
                "or add your first book."
            )

        else:

            if search.strip():
                st.info(
                    f'No books matched "{search}".'
                )
            else:
                st.info(
                    f"No books found for "
                    f'"{tree_status_choice}".'
                )

    else:

        # ----------------------------------------------------
        # CLEAN DATA
        # ----------------------------------------------------

        filtered = filtered.copy()

        filtered["Author"] = (
            filtered["Author"]
            .fillna("Unknown Author")
            .astype(str)
            .replace(
                ["", "nan", "None"],
                "Unknown Author",
            )
        )

        filtered["Series"] = (
            filtered["Series"]
            .fillna("Standalone")
            .astype(str)
            .replace(
                ["", "nan", "None"],
                "Standalone",
            )
        )

        # ----------------------------------------------------
        # MY LIBRARY ROOT — label reflects the active
        # All / Read / Unread filter so it's visually clear
        # which tree you're looking at.
        # ----------------------------------------------------

        root_label = {
            "All Books": "🌳 MY LIBRARY",
            "Read": "🌳 MY READ BOOKS",
            "Unread": "🌳 MY UNREAD BOOKS",
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
                    font-family:'Berkshire Swash', Georgia, serif;
                    font-size:24px;
                    box-shadow:0 4px 12px rgba(0,0,0,.18);
                ">
                    {root_label}
                </div>
            </div>
            """
        )

        # ----------------------------------------------------
        # AUTHOR GRID — grouped by first letter, 4 columns
        # within each letter group. The letter dividers give
        # the eye landmarks to jump to instead of scanning one
        # uniform wall of identical boxes.
        # ----------------------------------------------------

        AUTHORS_PER_ROW = 4

        author_list = sorted(
            filtered["Author"].unique(),
            key=lambda x: str(x).lower(),
        )

        # Build letter -> authors groups, preserving sort order
        letter_groups = []
        for author in author_list:
            letter = str(author).strip()[:1].upper() or "#"
            if not letter_groups or letter_groups[-1][0] != letter:
                letter_groups.append((letter, []))
            letter_groups[-1][1].append(author)

        for letter, group_authors in letter_groups:

            st.html(
                f"""
                <div class="atree-letter-divider">
                    <span class="letter">{html.escape(letter)}</span>
                    <span class="rule"></span>
                </div>
                """
            )

            for author_row_start in range(
                0, len(group_authors), AUTHORS_PER_ROW
            ):

                author_row = group_authors[
                    author_row_start:author_row_start + AUTHORS_PER_ROW
                ]

                author_cols = st.columns(AUTHORS_PER_ROW)

                for author_index, author in enumerate(author_row):

                    col = author_cols[author_index]

                    with col:
                        render_author_card(author, filtered)


# ============================================================
# BOOKS TAB
# ============================================================

elif st.session_state.active_tab == "books":

    # pick up a filter set by clicking a stat card
    if "stat_filter" in st.session_state:
        st.session_state["unique_books_radio"] = (
            st.session_state.pop("stat_filter")
        )
        st.session_state.pop("active_tab_hint", None)

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

        missing_covers = len(
            books[books["Cover"].fillna("") == ""]
        )

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


# ============================================================
# ADD BOOK
# ============================================================

elif st.session_state.active_tab == "add":

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
            value=None,
            step=0.5,
            placeholder="e.g. 1, 2.5...",
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

        st.write("Rating")

        star_click = st.feedback(
            "stars",
            key="add_book_rating",
        )

        rating = (
            star_click + 1
            if star_click is not None
            else None
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
                        if number is not None
                        else None
                    ),
                    "Genre": genre.strip(),
                    "ISBN": re.sub(
                        r"\D",
                        "",
                        isbn,
                    ),
                    "My Rating": rating,
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

elif st.session_state.active_tab == "import":

    st.header(
        "Import Your Library"
    )

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

        st.success(
            f"✓ {uploaded.name} uploaded successfully"
        )

        st.caption(
            f"File size: {uploaded.size:,} bytes"
        )

        fetch_covers_now = st.checkbox(
            "Fetch cover art during import (slower — you can "
            "fetch covers later from the Books tab instead)",
            value=False,
        )

        if st.button(
            "🌳 Grow My Book Tree",
            use_container_width=True,
            type="primary",
        ):

            with st.spinner(
                "Reading your book list..."
            ):

                success = import_books(
                    uploaded,
                    fetch_covers=fetch_covers_now,
                )

            if success:

                st.success(
                    f"✓ Successfully imported "
                    f"{len(st.session_state.library)} books!"
                )

                st.rerun()
