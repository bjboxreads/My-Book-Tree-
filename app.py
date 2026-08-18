import streamlit as st
import pandas as pd
import requests
import re
import html
import os
import shutil
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


def normalize_library_columns(df):
    """Make sure a DataFrame has exactly LIBRARY_COLUMNS, in
    order, filling in any missing ones. Used any time a
    DataFrame comes from somewhere that might not have every
    column (a fresh CSV, the data editor's '+' row, etc)."""
    df = df.copy()
    for column in LIBRARY_COLUMNS:
        if column not in df.columns:
            df[column] = "" if column != "Favorite" else False
    return df[LIBRARY_COLUMNS]


def save_library(df):
    """Write the current library to the local CSV save file.
    Called after every add / import / edit / delete so nothing
    is lost between sessions. Keeps a one-step-back backup of
    the previous save, as a safety net against accidental
    deletions or bad edits."""
    try:
        if os.path.exists(LIBRARY_FILE):
            try:
                shutil.copy(LIBRARY_FILE, LIBRARY_BACKUP_FILE)
            except Exception:
                pass
        df.to_csv(LIBRARY_FILE, index=False)
    except Exception:
        # Saving is best-effort — a failed write (e.g. read-only
        # filesystem) shouldn't crash the app.
        pass


def load_library():
    """Load the saved library from disk, if it exists. Returns
    an empty (correctly-columned) DataFrame otherwise."""
    if os.path.exists(LIBRARY_FILE):
        try:
            df = pd.read_csv(LIBRARY_FILE)

            df = normalize_library_columns(df)

            # Booleans round-trip through CSV as the strings
            # "True"/"False" — read_csv doesn't always infer
            # that back to a real bool, so convert explicitly.
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


def clean_author_series(df):
    """Fill blank/NaN Author and Series with consistent
    placeholders. Used by BOTH trees (Books tab + Book Tree tab)
    so a book with a missing author shows up the same way in
    both places instead of silently disappearing from one of
    them (pandas' groupby drops NaN groups by default)."""
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
    """Same idea as clean_author_series but for Genre, returned
    as a standalone cleaned Series rather than mutating the
    library's actual Genre column — grouping by genre shouldn't
    change what's shown on a book's own pill (which reads Genre
    straight from the row) for books that happen to have a
    blank genre."""
    return (
        series.fillna("")
        .astype(str)
        .str.strip()
        .replace(["", "nan", "None"], "Unknown Genre")
    )


# ============================================================
# SHARED TREE CSS — used by both the Books tab tree and the
# Book Tree tab's author grid, so the pill look stays identical
# everywhere. Both trees are pure CSS <details>/<summary>
# structures now (see note below on the Book Tree tab) — no
# Streamlit rerun happens on expand/collapse, so opening an
# author or series is instant and doesn't repaint anything else
# on the page. That's what fixes the choppiness: a button-driven
# expand used to trigger a fragment rerun (a real round trip to
# the server) every single click; a <details> tag just toggles
# in the browser.
#
# A few small "subtle whimsy" touches live here too: pills lift
# slightly on hover, the arrow rotates open instead of swapping
# glyphs, and newly-revealed content eases in instead of
# popping.
# ============================================================

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

/* Small favorite-toggle heart pinned to the corner of a book
   pill. Kept intentionally tiny so it doesn't disturb the
   pill's existing layout — it overlays rather than taking up
   its own row/column. */
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

/* ---- Book Tree tab: author grid ----
   Closed groups sit four to a row. Opening one expands its
   grid cell to the full row width so the nested series/book
   pills below it get real room instead of being squeezed into
   a quarter-width sliver. */
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
    Shared by both trees so a book looks identical everywhere.

    Also carries a small clickable heart in the corner that
    toggles the book's Favorite flag (via a ?toggle_fav=<row id>
    link, since these trees are static HTML — see the query-param
    handling near the top of the script)."""

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


# ============================================================
# ANCESTRY TREE (Books tab) — now with covers
# ============================================================

def display_ancestry_tree(df, group_by="Author"):
    # Clean data: fill empty Author with 'Unknown Author' and
    # empty Series with 'Standalone' (shared helper so this
    # matches the Book Tree tab exactly — otherwise a book with
    # a blank author would silently vanish here, since
    # groupby() drops NaN groups by default).
    df = clean_author_series(df)

    # group_by picks the top-level grouping: normally "Author",
    # or "Genre" to organize the same tree by genre instead.
    # Series stays as the second level either way, so the shape
    # of the tree (and every pill's look) is unchanged — only
    # which field the top pill groups on changes.
    if group_by == "Genre":
        group_col = clean_genre_column(df["Genre"])
        group_icon = "🏷️"
    else:
        group_col = df["Author"]
        group_icon = "🗼"

    # Build the entire tree as ONE html string instead of looping
    # st.expander / st.columns / st.write per author/series/book.
    # Each Streamlit widget call used to add several wrapper <div>s
    # (stLayoutWrapper, stVerticalBlock, stHorizontalBlock,
    # stElementContainer) — with hundreds of books that multiplied
    # into tens of thousands of DOM nodes. <details>/<summary> gives
    # native collapse/expand for free, with no JS and no extra nodes.
    parts = ['<div class="book-ancestry-tree">']

    for group_value, group_df in df.groupby(group_col):
        parts.append(
            f'<details class="atree-author">'
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
            parts.append(
                f'<details class="atree-series">'
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

    st.html(TREE_CSS + ''.join(parts))


# ============================================================
# PAGE
# ============================================================

st.set_page_config(
    page_title="StorySpire",
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
    st.session_state.library = load_library()

# ------------------------------------------------------------
# FAVORITE TOGGLE — handles clicks on the little heart icon in
# the tree pills. Those are plain <a href="?toggle_fav=..."> a
# links (the trees are static HTML, so there's no Python click
# handler to attach otherwise) — this picks up the query param
# on the resulting rerun, flips that row's Favorite flag, saves,
# and clears the URL so refreshing the page doesn't re-toggle it.
# Note: because this triggers a real rerun, any open sections of
# the tree will re-collapse, the same as clicking any other
# button on the page would.
# ------------------------------------------------------------

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

# ============================================================
# CSS
# ============================================================

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

    /* "spire" renders lighter-weight and a touch softer than
       "Story" — same case throughout (it's one word,
       "Storyspire", not "StorySpire"), the weight/color shift
       just keeps the two halves legible at a glance without
       resorting to a second capital letter. */
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

    /* ---- Clickable stat cards (Books / Read / Unread / Favorites /
       Authors / Series) — each jumps somewhere useful, so a real
       card + hover-lift is an honest affordance here. ---- */
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

# ============================================================
# HEADER
# ============================================================

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

# ============================================================
# THEME
# ============================================================

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


@st.cache_data(show_spinner=False)
def get_description(title, author=""):
    """Fetch a short book description from Google Books — this
    is what topic/theme search (e.g. searching "Christmas") runs
    against, so a book turns up even when the title itself
    doesn't mention the theme."""

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

                description = (
                    items[0]
                    .get("volumeInfo", {})
                    .get("description", "")
                )

                if description:
                    return description.strip()

    except Exception:
        pass

    return ""


def fetch_row_metadata(title, author, isbn, want_cover, want_description):
    """Fetch a cover and/or description for one row in a single
    worker call, so the import ThreadPoolExecutor can do both at
    once instead of two separate passes."""

    cover = get_cover(title, author, isbn) if want_cover else ""
    description = get_description(title, author) if want_description else ""

    return cover, description


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

def import_books(
    uploaded_file,
    fetch_covers=True,
    fetch_descriptions=False,
    merge=True,
):

    # --------------------------------------------------------
    # READ FILE (csv / excel / txt / pdf)
    # --------------------------------------------------------

    df = load_dataframe(uploaded_file)

    if df is None:
        return {"success": False}

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

    tags_col = find_column(
        [
            "tags",
            "keywords",
            "themes",
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

        return {"success": False}

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

        # TAGS

        tags = ""

        if tags_col:

            tags = str(
                row.get(
                    tags_col,
                    "",
                )
            ).strip()

            if tags.lower() == "nan":
                tags = ""

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
        # Goodreads exports use 0 to mean "not yet rated", not
        # a genuine zero-star rating — treat 0 the same as
        # missing so unrated books don't show a rating at all.

        rating = None

        if rating_col:

            try:

                value = row.get(
                    rating_col
                )

                if pd.notna(value):

                    parsed_rating = float(
                        value
                    )

                    if parsed_rating > 0:
                        rating = parsed_rating

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
                "Tags": tags,
                "Publisher": "",
                "Pages": "",
                "Date Read": "",
            }
        )

    # --------------------------------------------------------
    # MAKE DATAFRAME
    # --------------------------------------------------------

    imported_df = pd.DataFrame(
        books
    )

    if imported_df.empty:

        st.error(
            "No books were found in the file."
        )

        return {"success": False}

    existing = st.session_state.library.copy()

    # --------------------------------------------------------
    # MERGE vs REPLACE
    #
    # Merge (default): keep every book already in the library
    # untouched — including manual edits, favorites, ratings,
    # and fetched covers — and only add books from this file
    # that aren't already present (matched by title + author,
    # case-insensitively). This is what makes re-importing an
    # updated Goodreads export safe now that the library
    # persists across sessions.
    #
    # Replace: wipe the library and use only what's in this
    # file, same as the old behavior.
    # --------------------------------------------------------

    def make_key(title, author):
        return (
            str(title).strip().lower(),
            str(author).strip().lower(),
        )

    if merge and not existing.empty:

        existing_keys = {
            make_key(t, a)
            for t, a in zip(
                existing["Title"], existing["Author"]
            )
        }

        is_new_mask = imported_df.apply(
            lambda row: make_key(
                row["Title"], row["Author"]
            )
            not in existing_keys,
            axis=1,
        )

        new_rows = imported_df[is_new_mask].reset_index(
            drop=True
        )

        skipped_count = len(imported_df) - len(new_rows)

        combined = pd.concat(
            [existing, new_rows],
            ignore_index=True,
        )

        cover_fetch_start = len(existing)

    else:

        new_rows = imported_df
        skipped_count = 0
        combined = imported_df.reset_index(drop=True)
        cover_fetch_start = 0

    added_count = len(new_rows)

    combined = normalize_library_columns(combined)

    # --------------------------------------------------------
    # SAVE BOOKS BEFORE COVER SEARCH
    # --------------------------------------------------------

    st.session_state.library = combined

    save_library(combined)

    if (
        (not fetch_covers and not fetch_descriptions)
        or added_count == 0
    ):
        return {
            "success": True,
            "added": added_count,
            "skipped": skipped_count,
        }

    # --------------------------------------------------------
    # FIND COVERS / DESCRIPTIONS — only for the newly-added
    # rows. Existing books already have this metadata (or a
    # deliberately-empty version from before), so there's no
    # need to re-fetch those. Descriptions are what topic/theme
    # search (e.g. "Christmas") checks against.
    # --------------------------------------------------------

    cover_indices = list(
        range(
            cover_fetch_start,
            cover_fetch_start + added_count,
        )
    )

    progress = st.progress(
        0
    )

    done = 0

    with ThreadPoolExecutor(max_workers=40) as executor:

        future_to_index = {
            executor.submit(
                fetch_row_metadata,
                combined.loc[i, "Title"],
                combined.loc[i, "Author"],
                combined.loc[i, "ISBN"],
                fetch_covers,
                fetch_descriptions,
            ): i
            for i in cover_indices
        }

        for future in as_completed(future_to_index):

            i = future_to_index[future]

            try:
                cover, description = future.result()
            except Exception:
                cover, description = "", ""

            if fetch_covers:
                combined.loc[i, "Cover"] = cover

            if fetch_descriptions:
                combined.loc[i, "Description"] = description

            done += 1

            progress.progress(
                done / added_count
            )

    progress.empty()

    # --------------------------------------------------------
    # SAVE FINAL LIBRARY
    # --------------------------------------------------------

    st.session_state.library = combined

    save_library(combined)

    return {
        "success": True,
        "added": added_count,
        "skipped": skipped_count,
    }


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
    save_library(library)
    st.success(f"✓ Fetched covers for {total} books!")


def fetch_missing_descriptions():
    """Fetch descriptions only for rows that don't have one yet
    — same pattern as fetch_missing_covers, but this is what
    powers topic search (e.g. searching "Christmas")."""

    library = st.session_state.library

    missing = library[
        library["Description"].fillna("") == ""
    ]

    if missing.empty:
        st.info("Every book already has a description.")
        return

    total = len(missing)
    progress = st.progress(0)
    done = 0

    with ThreadPoolExecutor(max_workers=40) as executor:

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
            library.loc[i, "Description"] = description
            done += 1
            progress.progress(done / total)

    progress.empty()
    st.session_state.library = library
    save_library(library)
    st.success(f"✓ Fetched descriptions for {total} books!")


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
# STATS — every tile is clickable.
#   Books / Read / Unread / Favorites -> jump to the Books tab
#   pre-filtered.
#   Authors -> jumps to the Book Tree tab (already grouped by
#   author).
#   Series -> jumps to the Book Tree tab, narrowed to only
#   books that belong to an actual series (not Standalone).
# ============================================================

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
                    # Only "Series" narrows the tree to books that
                    # are actually in a series; "Authors" shows the
                    # full tree unfiltered.
                    st.session_state.tree_series_only = (
                        label == "Series"
                    )
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

# ============================================================
# BOOK TREE — AUTHOR/GENRE GRID → HORIZONTAL ANCESTRY TREE
#
# This whole tab is built as ONE html string, the same way the
# Books tab tree is, using nested <details>/<summary>. Previously
# each author/series row was an st.button that toggled
# session_state and triggered a fragment rerun — a real server
# round trip on every single click, which is what made expanding
# an author feel choppy. A <details> tag expands natively in the
# browser with zero server involvement, so it's instant no matter
# how large the library is.
#
# Groups (Author, or Genre when that grouping is picked) sit
# four to a row in a CSS grid while closed; opening one makes its
# grid cell span the full row (grid-column: 1/-1) so the
# series/book pills inside get real width instead of being
# squeezed into a quarter-column sliver.
# ============================================================

def render_tree_grid_html(filtered, group_by="Author"):

    parts = ['<div class="book-ancestry-tree">']

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

    # Build letter -> group-values groups, preserving sort order
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

            parts.append(
                f'<details class="atree-author">'
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

                series_books = group_books[
                    group_books["Series"] == series
                ]

                display_series = (
                    "STANDALONE"
                    if series == "Standalone"
                    else str(series)
                )

                parts.append(
                    f'<details class="atree-series">'
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
            [
                "All Books",
                "Read",
                "Unread",
            ],
            horizontal=True,
            key="tree_status_radio",
        )

    with group_col_ui:

        tree_group_choice = st.radio(
            "Organize by",
            [
                "Author",
                "Genre",
            ],
            horizontal=True,
            key="tree_group_by_radio",
        )

    # Series-only filter, set by clicking the "Series" stat tile.
    # Popped so it applies once right after the click and doesn't
    # silently keep narrowing the tree on later reruns (e.g. after
    # typing in the search box or switching the status radio).
    series_only = st.session_state.pop("tree_series_only", False)

    filtered = library.copy()

    if series_only:

        series_values = (
            filtered["Series"]
            .fillna("")
            .astype(str)
            .str.strip()
        )

        filtered = filtered[
            ~series_values.isin(["", "nan", "None", "Standalone"])
        ]

        st.caption("Showing books that belong to a series only.")

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
            + filtered["Tags"].fillna("").astype(str)
            + " "
            + filtered["Description"].fillna("").astype(str)
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
                "Your spire is just a foundation — import your "
                "library or add your first book to help it rise."
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

        filtered = clean_author_series(filtered)

        # ----------------------------------------------------
        # MY LIBRARY ROOT — label reflects the active
        # All / Read / Unread filter so it's visually clear
        # which tree you're looking at.
        # ----------------------------------------------------

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

        # ----------------------------------------------------
        # GROUP GRID — grouped by first letter of the chosen
        # grouping field (Author or Genre), four per row,
        # rendered as one static HTML tree (see note above).
        # ----------------------------------------------------

        st.html(
            TREE_CSS
            + render_tree_grid_html(filtered, group_by=tree_group_choice)
        )


# ============================================================
# BOOKS TAB
# ============================================================

elif st.session_state.active_tab == "books":

    # pick up a filter set by clicking a stat card
    if "stat_filter" in st.session_state:
        st.session_state["unique_books_radio"] = (
            st.session_state.pop("stat_filter")
        )

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

        with group_col_ui2:

            books_group_choice = st.radio(
                "Organize by",
                [
                    "Author",
                    "Genre",
                ],
                horizontal=True,
                key="books_group_by_radio",
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

            books = books[
                searchable.str.contains(
                    q,
                    na=False,
                    regex=False,
                )
            ]

        if books.empty:

            st.info(f'No books matched "{books_search}".')

        else:

            display_ancestry_tree(books, group_by=books_group_choice)

            missing_covers = len(
                books[books["Cover"].fillna("") == ""]
            )

            missing_descriptions = len(
                books[books["Description"].fillna("") == ""]
            )

            if missing_covers or missing_descriptions:

                fetch_col1, fetch_col2 = st.columns(2)

                with fetch_col1:

                    if missing_covers:

                        st.caption(
                            f"{missing_covers} book(s) shown here "
                            f"have no cover yet."
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
                            with st.spinner(
                                "Looking up descriptions..."
                            ):
                                fetch_missing_descriptions()
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

        tags = st.text_input(
            "Tags",
            placeholder=(
                "Christmas, cozy, found family..."
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
            "Add to My Spire"
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

                description = get_description(
                    title,
                    author,
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
                    "Description": description,
                    "Tags": tags.strip(),
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

                save_library(st.session_state.library)

                st.success(
                    f'"{title}" was added to your spire!'
                )

                st.rerun()


# ============================================================
# MANAGE TAB — edit any field inline, or delete rows using the
# data editor's built-in row-delete (select a row, press the
# trash icon / Delete key). Deletions require a confirm step
# before they're saved; edits and additions save right away.
# Every save also keeps a one-step-back backup file.
# ============================================================

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
                    options=[
                        "Want to Read",
                        "Currently Reading",
                        "Read",
                    ],
                ),
                "My Rating": st.column_config.NumberColumn(
                    "My Rating",
                    min_value=0,
                    max_value=5,
                    step=1,
                ),
                "Series Number": st.column_config.NumberColumn(
                    "Series #",
                    min_value=0,
                    step=0.5,
                ),
                "Favorite": st.column_config.CheckboxColumn(
                    "Favorite"
                ),
            },
        )

        # A row added through the editor's own "+" row but left
        # with no title isn't a real book yet — drop it silently
        # rather than letting it get saved as a blank entry.
        new_row_mask = ~edited.index.isin(library.index)

        blank_new_mask = new_row_mask & (
            edited["Title"].fillna("").astype(str).str.strip()
            == ""
        )

        edited_clean = edited[~blank_new_mask]

        # Rows present in the original library but missing from
        # the edited result were deleted via the trash icon —
        # these need a confirmation step before they're saved.
        removed_indices = sorted(
            set(library.index) - set(edited_clean.index)
        )

        if removed_indices:

            removed_titles = library.loc[
                removed_indices, "Title"
            ].tolist()

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

                    # Removing the editor's own state forces it
                    # to reload from the untouched library on
                    # the next run, discarding the pending delete.
                    del st.session_state["manage_library_editor"]

                    st.rerun()

        elif not edited_clean.equals(library):

            final = normalize_library_columns(
                edited_clean.reset_index(drop=True)
            )

            st.session_state.library = final
            save_library(final)
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

        if st.button(
            "🗼 Raise My Spire",
            use_container_width=True,
            type="primary",
        ):

            merge_choice = (
                import_mode == "Merge with my existing library"
            )

            with st.spinner(
                "Reading your book list..."
            ):

                result = import_books(
                    uploaded,
                    fetch_covers=fetch_covers_now,
                    fetch_descriptions=fetch_descriptions_now,
                    merge=merge_choice,
                )

            if result.get("success"):

                added = result.get("added", 0)
                skipped = result.get("skipped", 0)

                if merge_choice and skipped:

                    st.success(
                        f"✓ Added {added} new book(s). "
                        f"Skipped {skipped} already in your "
                        f"library."
                    )

                else:

                    st.success(
                        f"✓ Successfully imported {added} book(s)!"
                    )

                st.rerun()
