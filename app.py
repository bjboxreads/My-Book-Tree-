import streamlit as st
import pandas as pd
import requests
import json
import re
import uuid
from datetime import date
from pathlib import Path

# ============================================================
# My Book Tree — Streamlit version
# ============================================================

st.set_page_config(
    page_title="My Book Tree",
    page_icon="🌳",
    layout="centered",
    initial_sidebar_state="collapsed",
)

DATA_FILE = Path("books.json")

THEMES = {
    "emerald": {
        "label": "Emerald Athenaeum",
        "bg": "#0c1f16",
        "bg2": "#173321",
        "surface": "#152b1d",
        "surface2": "#1c3826",
        "primary": "#2d6a4f",
        "primaryLight": "#4f9c78",
        "accent": "#d4af37",
        "accentSoft": "#eeda9a",
        "text": "#f1e9d2",
        "muted": "#a8c3b0",
        "border": "#3d6b4f",
        "trunk": "#4a3728",
        "leaf": "#4f7a63",
        "leafDark": "#24402f",
        "flower": "#d4af37",
    },
    "rose": {
        "label": "Midnight Rose",
        "bg": "#210c15",
        "bg2": "#3a1626",
        "surface": "#2c101c",
        "surface2": "#3d1625",
        "primary": "#7a1f3d",
        "primaryLight": "#b0446a",
        "accent": "#d9a6a1",
        "accentSoft": "#f0c9c2",
        "text": "#f5e6ea",
        "muted": "#c99aa8",
        "border": "#5c2438",
        "trunk": "#3d2418",
        "leaf": "#6b2c42",
        "leafDark": "#39131f",
        "flower": "#e3bdb8",
    },
    "sapphire": {
        "label": "Sapphire Chronicles",
        "bg": "#081522",
        "bg2": "#152338",
        "surface": "#0f1d30",
        "surface2": "#182a45",
        "primary": "#1d4e89",
        "primaryLight": "#3d76bd",
        "accent": "#c9d6e8",
        "accentSoft": "#e7edf8",
        "text": "#e8eef7",
        "muted": "#9fb3cc",
        "border": "#2a4870",
        "trunk": "#2f2419",
        "leaf": "#274472",
        "leafDark": "#0f1d30",
        "flower": "#dce6f4",
    },
    "amethyst": {
        "label": "Amethyst Grimoire",
        "bg": "#170b25",
        "bg2": "#2a1640",
        "surface": "#1e0f34",
        "surface2": "#2e1747",
        "primary": "#6b3fa0",
        "primaryLight": "#9a6ecb",
        "accent": "#c9a660",
        "accentSoft": "#e5cb8f",
        "text": "#ede4f7",
        "muted": "#b79fd4",
        "border": "#4a2a6e",
        "trunk": "#3d2818",
        "leaf": "#5b3a7a",
        "leafDark": "#241238",
        "flower": "#d8bd7a",
    },
}

STATUS_OPTIONS = [
    "Want to Read",
    "Currently Reading",
    "Read",
]

FILTERS = [
    "All",
    "Favorites",
    "Read",
    "Currently Reading",
    "Want to Read",
]


# ============================================================
# HELPERS
# ============================================================

def uid():
    return uuid.uuid4().hex


def empty_book(**overrides):
    book = {
        "id": uid(),
        "title": "",
        "author": "",
        "series": "",
        "seriesNumber": "",
        "genre": "",
        "isbn": "",
        "rating": 0,
        "status": "Want to Read",
        "favorite": False,
        "cover": "",
        "description": "",
        "publisher": "",
        "pages": "",
        "dateRead": "",
    }

    book.update(overrides)
    return book


def load_books():
    if not DATA_FILE.exists():
        return []

    try:
        data = json.loads(
            DATA_FILE.read_text(encoding="utf-8")
        )

        if isinstance(data, list):
            return data

        return []

    except Exception:
        return []


def save_books(books):
    DATA_FILE.write_text(
        json.dumps(
            books,
            indent=2,
            ensure_ascii=False
        ),
        encoding="utf-8"
    )


def parse_series_from_title(raw_title):
    raw_title = str(raw_title or "").strip()

    match = re.match(
        r"^(.*?)\s*\(([^,()]+),\s*#?([\d.]+)\)\s*$",
        raw_title
    )

    if match:
        return (
            match.group(1).strip(),
            match.group(2).strip(),
            match.group(3).strip()
        )

    return raw_title, "", ""


def clean_isbn(isbn):
    return re.sub(
        r"[^0-9Xx]",
        "",
        str(isbn or "")
    )


# ============================================================
# BOOK LOOKUP
# ============================================================

@st.cache_data(show_spinner=False)
def fetch_cover_by_isbn(isbn):

    clean = clean_isbn(isbn)

    if not clean:
        return None

    try:
        url = "https://openlibrary.org/api/books"

        params = {
            "bibkeys": f"ISBN:{clean}",
            "format": "json",
            "jscmd": "data",
        }

        response = requests.get(
            url,
            params=params,
            timeout=8
        )

        response.raise_for_status()

        entry = response.json().get(
            f"ISBN:{clean}"
        )

        if entry and entry.get("cover"):

            cover = entry["cover"]

            return (
                cover.get("large")
                or cover.get("medium")
                or cover.get("small")
            )

    except Exception:
        pass

    return None


@st.cache_data(show_spinner=False)
def fetch_from_google_books(
    title,
    author,
    isbn
):

    try:

        clean = clean_isbn(isbn)

        if clean:

            query = f"isbn:{clean}"

        else:

            query = f"intitle:{title or ''}"

            if author:
                query += f"+inauthor:{author}"

        response = requests.get(
            "https://www.googleapis.com/books/v1/volumes",
            params={
                "q": query,
                "maxResults": 1
            },
            timeout=8
        )

        response.raise_for_status()

        items = response.json().get(
            "items",
            []
        )

        if not items:
            return None

        info = items[0].get(
            "volumeInfo",
            {}
        )

        links = info.get(
            "imageLinks",
            {}
        )

        cover = (
            links.get("thumbnail")
            or links.get("smallThumbnail")
            or ""
        )

        if cover:
            cover = cover.replace(
                "http://",
                "https://"
            )

        return {
            "cover": cover,
            "description": info.get(
                "description",
                ""
            ),
            "publisher": info.get(
                "publisher",
                ""
            ),
            "pages": info.get(
                "pageCount",
                ""
            ),
            "genre": (
                info.get("categories")
                or [""]
            )[0],
        }

    except Exception:
        return None


def lookup_book_info(book):

    cover = fetch_cover_by_isbn(
        book.get("isbn", "")
    )

    extra = None

    if not cover:

        extra = fetch_from_google_books(
            book.get("title", ""),
            book.get("author", ""),
            book.get("isbn", "")
        )

        if extra:
            cover = extra.get("cover")

    return cover, extra


def map_goodreads_shelf(shelf):

    s = str(
        shelf or ""
    ).lower()

    if "currently" in s:
        return "Currently Reading"

    if "read" in s:
        return "Read"

    return "Want to Read"


# ============================================================
# TREE
# ============================================================

def build_tree(books):

    authors = {}

    for book in books:

        author = (
            book.get("author") or ""
        ).strip()

        if not author:
            author = "Unknown Author"

        if author not in authors:

            authors[author] = {
                "name": author,
                "series": {},
                "standalone": []
            }

        series = (
            book.get("series") or ""
        ).strip()

        if series:

            authors[author]["series"].setdefault(
                series,
                []
            ).append(book)

        else:

            authors[author]["standalone"].append(
                book
            )

    result = []

    for author in authors.values():

        for books_in_series in author["series"].values():

            def series_sort(book):

                number = str(
                    book.get("seriesNumber") or ""
                )

                try:
                    return float(number)

                except Exception:
                    return 0

            books_in_series.sort(
                key=series_sort
            )

        result.append(author)

    return sorted(
        result,
        key=lambda a: a["name"].lower()
    )


def stars_html(rating):

    try:
        rating = int(rating or 0)
    except Exception:
        rating = 0

    return "".join(
        "★" if i <= rating else "☆"
        for i in range(1, 6)
    )


# ============================================================
# CSS
# ============================================================

def inject_css(theme):

    st.markdown(
        f"""
        <style>

        @import url(
          'https://fonts.googleapis.com/css2?family=Berkshire+Swash&family=Cormorant+Garamond:ital,wght@0,400;0,600;0,700;1,500&family=EB+Garamond:ital,wght@0,400;0,600;1,400&display=swap'
        );

        .stApp {{
            background:
              radial-gradient(
                ellipse 900px 500px at 50% 0%,
                {theme["bg2"]},
                {theme["bg"]} 65%
              );

            color: {theme["text"]};
        }}

        .block-container {{
            max-width: 900px;
            padding-top: 1.2rem;
            padding-bottom: 5rem;
        }}

        html,
        body,
        [class*="css"] {{
            font-family: 'EB Garamond', serif;
        }}

        h1,
        h2,
        h3 {{
            font-family:
                'Berkshire Swash',
                cursive !important;

            color:
                {theme["accentSoft"]}
                !important;
        }}

        .book-title {{
            font-family:
                'Cormorant Garamond',
                serif;

            font-size: 1.2rem;
            font-weight: 700;

            color:
                {theme["text"]};
        }}

        .muted {{
            color:
                {theme["muted"]};

            font-style: italic;
        }}

        .ornate {{
            border:
                1px solid {theme["border"]};

            border-radius: 18px;

            padding: 24px;

            background:
                linear-gradient(
                    180deg,
                    {theme["surface"]},
                    {theme["surface2"]}
                );

            box-shadow:
                0 0 0 1px
                rgba(212,175,55,.18),

                0 18px 40px
                rgba(0,0,0,.45),

                inset 0 0 40px
                rgba(0,0,0,.25);

            margin:
                12px 0 22px;
        }}

        .tree-root,
        .tree-author,
        .tree-series {{
            border:
                1px solid {theme["accent"]};

            border-radius: 12px;

            padding: 10px 16px;

            margin: 7px 0;

            background:
                linear-gradient(
                    135deg,
                    {theme["surface2"]},
                    {theme["surface"]}
                );

            text-align: center;
        }}

        .tree-root {{
            border-width: 2px;

            font-family:
                'Berkshire Swash',
                cursive;

            font-size: 1.3rem;

            color:
                {theme["accentSoft"]};
        }}

        .tree-author {{
            font-family:
                'Cormorant Garamond',
                serif;

            font-size: 1.08rem;

            font-weight: 700;
        }}

        .tree-series {{
            border-color:
                {theme["border"]};

            font-family:
                'Cormorant Garamond',
                serif;

            font-style: italic;
        }}

        .stat {{
            display: inline-flex;

            flex-direction: column;

            justify-content: center;

            align-items: center;

            width: 100px;
            height: 100px;

            border:
                2px solid {theme["accent"]};

            border-radius: 50%;

            background:
                radial-gradient(
                    circle at 32% 28%,
                    {theme["surface2"]},
                    {theme["surface"]} 70%
                );

            box-shadow:
                0 6px 16px
                rgba(0,0,0,.4),

                inset 0 0 14px
                rgba(0,0,0,.35);

            margin: 4px;
        }}

        .stat-value {{
            font-family:
                'Berkshire Swash',
                cursive;

            color:
                {theme["accentSoft"]};

            font-size: 1.35rem;
        }}

        .stat-label {{
            color:
                {theme["muted"]};

            text-transform: uppercase;

            letter-spacing: 1px;

            font-size: .65rem;
        }}

        .book-card {{
            border:
                1px solid {theme["border"]};

            border-radius: 12px;

            padding: 12px;

            margin: 7px 0;

            background:
                rgba(0,0,0,.14);
        }}

        .cover {{
            max-width: 90px;
            max-height: 135px;

            border-radius:
                2px 5px 5px 2px;

            box-shadow:
                3px 5px 14px
                rgba(0,0,0,.55);
        }}

        div[data-testid="stButton"] button,
        div[data-testid="stDownloadButton"] button {{
            border-radius:
                999px !important;

            border:
                1px solid
                {theme["border"]}
                !important;

            font-family:
                'Cormorant Garamond',
                serif !important;
        }}

        div[data-testid="stButton"]
        button[kind="primary"] {{
            background:
                linear-gradient(
                    135deg,
                    {theme["primary"]},
                    {theme["primaryLight"]}
                ) !important;

            border-color:
                {theme["accent"]}
                !important;

            color:
                white !important;
        }}

        div[data-testid="stTextInput"] input,
        div[data-testid="stTextArea"] textarea,
        div[data-testid="stNumberInput"] input {{
            background:
                transparent !important;

            color:
                {theme["text"]}
                !important;
        }}

        div[data-baseweb="select"] > div {{
            background:
                {theme["surface"]}
                !important;

            color:
                {theme["text"]}
                !important;

            border-color:
                {theme["border"]}
                !important;
        }}

        .stExpander {{
            border-color:
                {theme["border"]}
                !important;

            background:
                rgba(0,0,0,.08);
        }}

        </style>
        """,
        unsafe_allow_html=True
    )


# ============================================================
# TREE DISPLAY
# ============================================================

def show_tree(tree):

    st.markdown(
        '<div class="ornate">',
        unsafe_allow_html=True
    )

    st.markdown(
        '<div class="tree-root">🌳 My Library</div>',
        unsafe_allow_html=True
    )

    if not tree:

        st.markdown(
            """
            <div
                style="text-align:center;padding:40px"
                class="muted"
            >
                Your tree awaits its first leaf<br>
                Add a book to begin growing your library.
            </div>
            """,
            unsafe_allow_html=True
        )

    for author in tree:

        series_list = list(
            author["series"].items()
        )

        total = (
            len(author["standalone"])
            + sum(
                len(v)
                for _, v in series_list
            )
        )

        with st.expander(
            f"🪶 {author['name']}  ·  {total} books",
            expanded=False
        ):

            for series_name, series_books in series_list:

                with st.expander(
                    f"📖 {series_name}  ·  {len(series_books)} books",
                    expanded=False
                ):

                    for book in series_books:
                        show_book_line(book)

            for book in author["standalone"]:
                show_book_line(book)

    st.markdown(
        "</div>",
        unsafe_allow_html=True
    )


def show_book_line(book):

    cols = st.columns(
        [1, 4, 1]
    )

    with cols[0]:

        if book.get("cover"):
            st.image(
                book["cover"],
                width=58
            )

        else:
            st.markdown("📕")

    with cols[1]:

        title = book.get(
            "title",
            "Untitled"
        )

        vol = ""

        if book.get("seriesNumber"):
            vol = (
                f" · Vol. "
                f"{book['seriesNumber']}"
            )

        st.markdown(
            f"""
            <div class="book-title">
                {title}{vol}
            </div>

            <div class="muted">
                {book.get("genre") or "Unclassified"}
                ·
                {stars_html(book.get("rating", 0))}
            </div>
            """,
            unsafe_allow_html=True
        )

    with cols[2]:

        st.caption(
            book.get(
                "status",
                ""
            )
        )


# ============================================================
# BOOK FORM
# ============================================================

def book_form(existing=None):

    editing = existing is not None

    book = (
        existing.copy()
        if existing
        else empty_book()
    )

    st.markdown(
        '<div class="ornate">',
        unsafe_allow_html=True
    )

    st.markdown(
        f"""
        <h2 style='text-align:center'>
            {
                "Revise This Volume"
                if editing
                else "A New Leaf"
            }
        </h2>
        """,
        unsafe_allow_html=True
    )

    if book.get("cover"):

        st.image(
            book["cover"],
            width=120
        )

    with st.form(
        "book_form",
        clear_on_submit=False
    ):

        title = st.text_input(
            "Title",
            value=book.get(
                "title",
                ""
            )
        )

        author = st.text_input(
            "Author",
            value=book.get(
                "author",
                ""
            )
        )

        genre = st.text_input(
            "Genre",
            value=book.get(
                "genre",
                ""
            )
        )

        series = st.text_input(
            "Series",
            value=book.get(
                "series",
                ""
            )
        )

        series_no = st.text_input(
            "Series No.",
            value=str(
                book.get(
                    "seriesNumber",
                    ""
                )
            )
        )

        isbn = st.text_input(
            "ISBN",
            value=book.get(
                "isbn",
                ""
            )
        )

        status = st.selectbox(
            "Status",
            STATUS_OPTIONS,
            index=(
                STATUS_OPTIONS.index(
                    book.get(
                        "status",
                        "Want to Read"
                    )
                )
                if book.get("status")
                in STATUS_OPTIONS
                else 0
            )
        )

        publisher = st.text_input(
            "Publisher",
            value=book.get(
                "publisher",
                ""
            )
        )

        pages = st.text_input(
            "Pages",
            value=str(
                book.get(
                    "pages",
                    ""
                )
            )
        )

        date_read = st.text_input(
            "Date Read",
            value=book.get(
                "dateRead",
                ""
            )
        )

        favorite = st.checkbox(
            "Favorite",
            value=bool(
                book.get(
                    "favorite",
                    False
                )
            )
        )

        rating = st.slider(
            "My Rating",
            0,
            5,
            int(
                book.get(
                    "rating",
                    0
                )
            )
        )

        description = st.text_area(
            "Description",
            value=book.get(
                "description",
                ""
            )
        )

        c1, c2 = st.columns(2)

        with c1:

            lookup = st.form_submit_button(
                "✨ Find Cover"
            )

        with c2:

            save = st.form_submit_button(
                "Save to the Tree",
                type="primary"
            )

    if lookup:

        lookup_book = {
            **book,
            "title": title,
            "author": author,
            "isbn": isbn,
        }

        cover, extra = lookup_book_info(
            lookup_book
        )

        if cover or extra:

            book.update(
                {
                    "cover":
                        cover
                        or book.get(
                            "cover",
                            ""
                        ),

                    "description":
                        book.get(
                            "description"
                        )
                        or (extra or {}).get(
                            "description",
                            ""
                        ),

                    "publisher":
                        book.get(
                            "publisher"
                        )
                        or (extra or {}).get(
                            "publisher",
                            ""
                        ),

                    "pages":
                        book.get(
                            "pages"
                        )
                        or (extra or {}).get(
                            "pages",
                            ""
                        ),

                    "genre":
                        book.get(
                            "genre"
                        )
                        or (extra or {}).get(
                            "genre",
                            ""
                        ),
                }
            )

            st.session_state.lookup_result = book

            st.rerun()

        else:

            st.warning(
                "I couldn't find that book automatically."
            )

    if save and title.strip():

        updated = {
            **book,

            "title":
                title.strip(),

            "author":
                author.strip(),

            "genre":
                genre.strip(),

            "series":
                series.strip(),

            "seriesNumber":
                series_no.strip(),

            "isbn":
                isbn.strip(),

            "status":
                status,

            "publisher":
                publisher.strip(),

            "pages":
                pages.strip(),

            "dateRead":
                date_read.strip(),

            "favorite":
                favorite,

            "rating":
                rating,

            "description":
                description.strip(),
        }

        books = st.session_state.books

        found = False

        for i, old in enumerate(books):

            if old.get("id") == updated.get("id"):

                books[i] = updated

                found = True

                break

        if not found:

            books.append(updated)

        save_books(books)

        st.session_state.books = books

        st.session_state.view = "tree"

        st.session_state.editing_id = None

        st.success(
            "Saved to your tree."
        )

        st.rerun()

    st.markdown(
        "</div>",
        unsafe_allow_html=True
    )


# ============================================================
# SESSION STATE
# ============================================================

if "books" not in st.session_state:

    st.session_state.books = load_books()


if "theme_key" not in st.session_state:

    st.session_state.theme_key = "emerald"


if "view" not in st.session_state:

    st.session_state.view = "tree"


if "filter" not in st.session_state:

    st.session_state.filter = "All"


if "search" not in st.session_state:

    st.session_state.search = ""


if "editing_id" not in st.session_state:

    st.session_state.editing_id = None


theme = THEMES[
    st.session_state.theme_key
]

inject_css(theme)


# ============================================================
# HEADER
# ============================================================

top_left, top_right = st.columns(
    [4, 2]
)

with top_right:

    selected_theme = st.selectbox(
        "Theme",
        list(THEMES.keys()),

        index=list(
            THEMES.keys()
        ).index(
            st.session_state.theme_key
        ),

        format_func=lambda k:
            THEMES[k]["label"],

        label_visibility="collapsed"
    )

    if (
        selected_theme
        != st.session_state.theme_key
    ):

        st.session_state.theme_key = (
            selected_theme
        )

        st.rerun()


st.markdown(
    """
    <h1
        style='
            text-align:center;
            font-size:3.7rem;
            margin-bottom:0
        '
    >
        My Book Tree
    </h1>
    """,
    unsafe_allow_html=True
)


# ============================================================
# WILLOW TREE
# ============================================================

st.markdown(
    f"""
    <div
        style="
            height:160px;
            position:relative;
            overflow:hidden;
            margin-top:-5px
        "
    >

        <svg
            viewBox="0 0 820 220"
            width="100%"
            height="100%"
        >

            <defs>

                <radialGradient id="glow">

                    <stop
                        offset="0%"
                        stop-color="{theme['accent']}"
                        stop-opacity=".18"
                    />

                    <stop
                        offset="100%"
                        stop-color="{theme['accent']}"
                        stop-opacity="0"
                    />

                </radialGradient>

            </defs>


            <ellipse
                cx="410"
                cy="85"
                rx="330"
                ry="95"
                fill="url(#glow)"
            />


            <path
                d="
                    M395 205
                    C390 160 388 120 400 45
                    L412 45
                    C422 120 420 160 418 205Z
                "
                fill="{theme['trunk']}"
            />


            <g
                fill="{theme['leaf']}"
                opacity=".9"
            >

                <circle
                    cx="410"
                    cy="60"
                    r="68"
                />

                <circle
                    cx="305"
                    cy="78"
                    r="52"
                />

                <circle
                    cx="515"
                    cy="78"
                    r="52"
                />

                <circle
                    cx="215"
                    cy="100"
                    r="40"
                />

                <circle
                    cx="605"
                    cy="100"
                    r="40"
                />

            </g>


            <g
                stroke="{theme['leaf']}"
                stroke-width="1.7"
                fill="none"
                opacity=".75"
            >

                <path
                    d="
                        M215 112
                        C200 150 220 175 210 195
                    "
                />

                <path
                    d="
                        M275 100
                        C290 145 275 170 286 205
                    "
                />

                <path
                    d="
                        M340 90
                        C330 135 350 170 340 202
                    "
                />

                <path
                    d="
                        M410 85
                        C425 130 405 165 414 210
                    "
                />

                <path
                    d="
                        M480 90
                        C465 135 485 170 478 202
                    "
                />

                <path
                    d="
                        M545 100
                        C560 145 545 170 555 205
                    "
                />

                <path
                    d="
                        M605 112
                        C620 150 600 175 610 195
                    "
                />

            </g>


            <g fill="{theme['flower']}">

                <circle
                    cx="340"
                    cy="48"
                    r="3.2"
                />

                <circle
                    cx="410"
                    cy="32"
                    r="3.2"
                />

                <circle
                    cx="480"
                    cy="48"
                    r="3.2"
                />

                <circle
                    cx="260"
                    cy="80"
                    r="3.2"
                />

                <circle
                    cx="560"
                    cy="80"
                    r="3.2"
                />

            </g>

        </svg>

    </div>
    """,
    unsafe_allow_html=True
)


# ============================================================
# STATS
# ============================================================

books = st.session_state.books

authors = len(
    {
        b.get("author")
        or "Unknown Author"
        for b in books
    }
)

series_count = len(
    {
        (
            b.get("author", ""),
            b.get("series", "")
        )

        for b in books

        if b.get("series")
    }
)

read_count = sum(
    b.get("status") == "Read"
    for b in books
)

favorite_count = sum(
    bool(
        b.get("favorite")
    )
    for b in books
)


stats = [
    ("📚", len(books), "Books"),
    ("🪶", authors, "Authors"),
    ("🌳", series_count, "Series"),
    ("✨", read_count, "Read"),
    ("♥", favorite_count, "Favorites"),
]


stat_cols = st.columns(5)


for col, (
    icon,
    value,
    label
) in zip(
    stat_cols,
    stats
):

    with col:

        st.markdown(
            f"""
            <div class="stat">

                <div>
                    {icon}
                </div>

                <div class="stat-value">
                    {value}
                </div>

                <div class="stat-label">
                    {label}
                </div>

            </div>
            """,
            unsafe_allow_html=True
        )


# ============================================================
# NAVIGATION
# ============================================================

nav = st.columns(4)

labels = [
    ("tree", "🌳 Book Tree"),
    ("books", "📚 All Books"),
    ("add", "＋ Add Book"),
    ("import", "↥ Import Library"),
]


for col, (
    key,
    label
) in zip(
    nav,
    labels
):

    with col:

        if st.button(
            label,
            use_container_width=True,
            type=(
                "primary"
                if st.session_state.view == key
                else "secondary"
            )
        ):

            st.session_state.view = key

            st.session_state.editing_id = None

            st.rerun()


# ============================================================
# SEARCH / FILTER
# ============================================================

if st.session_state.view in (
    "tree",
    "books"
):

    c1, c2 = st.columns(
        [3, 1]
    )

    with c1:

        st.session_state.search = (
            st.text_input(
                "Search",
                value=st.session_state.search,

                placeholder=
                "Search title, author, series, or genre…",

                label_visibility="collapsed"
            )
        )

    with c2:

        st.session_state.filter = (
            st.selectbox(
                "Filter",
                FILTERS,

                index=FILTERS.index(
                    st.session_state.filter
                ),

                label_visibility="collapsed"
            )
        )


search = (
    st.session_state.search
    .strip()
    .lower()
)

filtered = list(books)


if st.session_state.filter == "Favorites":

    filtered = [
        b
        for b in filtered
        if b.get("favorite")
    ]


elif st.session_state.filter != "All":

    filtered = [
        b
        for b in filtered
        if b.get("status")
        == st.session_state.filter
    ]


if search:

    filtered = [

        b

        for b in filtered

        if (
            search
            in str(
                b.get(
                    "title",
                    ""
                )
            ).lower()
        )

        or (
            search
            in str(
                b.get(
                    "author",
                    ""
                )
            ).lower()
        )

        or (
            search
            in str(
                b.get(
                    "series",
                    ""
                )
            ).lower()
        )

        or (
            search
            in str(
                b.get(
                    "genre",
                    ""
                )
            ).lower()
        )

    ]


# ============================================================
# TREE VIEW
# ============================================================

if st.session_state.view == "tree":

    show_tree(
        build_tree(
            filtered
        )
    )


# ============================================================
# ALL BOOKS VIEW
# ============================================================

elif st.session_state.view == "books":

    st.markdown(
        '<div class="ornate">',
        unsafe_allow_html=True
    )

    if not filtered:

        st.markdown(
            """
            <div
                class='muted'
                style='
                    text-align:center;
                    padding:35px
                '
            >
                No books match yet.
            </div>
            """,
            unsafe_allow_html=True
        )

    for book in filtered:

        cols = st.columns(
            [1, 5, 1, 1]
        )

        with cols[0]:

            if book.get("cover"):

                st.image(
                    book["cover"],
                    width=48
                )

            else:

                st.write("📕")

        with cols[1]:

            st.markdown(
                f"""
                <div class='book-title'>
                    {book.get(
                        "title",
                        "Untitled"
                    )}
                </div>

                <div class='muted'>

                    {book.get(
                        "author",
                        "Unknown Author"
                    )}

                    ·

                    {book.get(
                        "genre"
                    ) or "Unclassified"}

                    ·

                    {stars_html(
                        book.get(
                            "rating",
                            0
                        )
                    )}

                </div>
                """,
                unsafe_allow_html=True
            )

        with cols[2]:

            if st.button(
                "♥"
                if book.get("favorite")
                else "♡",

                key=f"fav_{book['id']}"
            ):

                book["favorite"] = (
                    not book.get(
                        "favorite",
                        False
                    )
                )

                save_books(books)

                st.rerun()

        with cols[3]:

            if st.button(
                "Edit",
                key=f"edit_{book['id']}"
            ):

                st.session_state.editing_id = (
                    book["id"]
                )

                st.rerun()

    st.markdown(
        "</div>",
        unsafe_allow_html=True
    )


    if st.session_state.editing_id:

        found = next(
            (
                b
                for b in books
                if b["id"]
                == st.session_state.editing_id
            ),
            None
        )

        if found:
            book_form(found)


# ============================================================
# ADD BOOK
# ============================================================

elif st.session_state.view == "add":

    book_form()


# ============================================================
# IMPORT LIBRARY
# ============================================================

elif st.session_state.view == "import":

    st.markdown(
        '<div class="ornate">',
        unsafe_allow_html=True
    )

    st.markdown(
        """
        <h2 style='text-align:center'>
            Import Your Library
        </h2>
        """,
        unsafe_allow_html=True
    )

    st.markdown(
        """
        <p
            class='muted'
            style='text-align:center'
        >
            Bring in a CSV export from Goodreads
            or another compatible library file.
            Series, series numbers, and covers
            will be discovered automatically.
        </p>
        """,
        unsafe_allow_html=True
    )

    uploaded = st.file_uploader(
        "Choose CSV File",
        type=["csv"],
        label_visibility="collapsed"
    )

    if uploaded is not None:

        try:

            df = pd.read_csv(
                uploaded
            )

            new_books = []

            progress = st.progress(
                0
            )

            rows = len(df)

            for i, row in df.iterrows():

                raw_title = row.get(
                    "Title",
                    row.get(
                        "title",
                        ""
                    )
                )

                if (
                    pd.isna(raw_title)
                    or not str(
                        raw_title
                    ).strip()
                ):
                    continue

                (
                    title,
                    series,
                    series_no
                ) = parse_series_from_title(
                    raw_title
                )

                isbn = row.get(
                    "ISBN13",
                    row.get(
                        "ISBN",
                        row.get(
                            "isbn",
                            ""
                        )
                    )
                )

                if pd.isna(isbn):
                    isbn = ""

                isbn = re.sub(
                    r'[="]',
                    "",
                    str(isbn)
                )

                rating = row.get(
                    "My Rating",
                    row.get(
                        "Rating",
                        0
                    )
                )

                try:

                    rating = (
                        int(
                            float(
                                rating
                            )
                        )
                        if not pd.isna(
                            rating
                        )
                        else 0
                    )

                except Exception:

                    rating = 0


                book = empty_book(

                    title=title,

                    author=str(
                        row.get(
                            "Author",
                            row.get(
                                "author",
                                ""
                            )
                        )
                        or ""
                    ),

                    series=series,

                    seriesNumber=series_no,

                    genre=str(
                        row.get(
                            "Genre",
                            row.get(
                                "Bookshelves",
                                ""
                            )
                        )
                        or ""
                    ),

                    isbn=isbn,

                    rating=rating,

                    status=map_goodreads_shelf(
                        row.get(
                            "Exclusive Shelf",
                            row.get(
                                "Shelf",
                                row.get(
                                    "shelf",
                                    ""
                                )
                            )
                        )
                    ),

                    publisher=str(
                        row.get(
                            "Publisher",
                            ""
                        )
                        or ""
                    ),

                    pages=str(
                        row.get(
                            "Number of Pages",
                            row.get(
                                "Pages",
                                ""
                            )
                        )
                        or ""
                    ),

                    dateRead=str(
                        row.get(
                            "Date Read",
                            ""
                        )
                        or ""
                    ),
                )


                cover = fetch_cover_by_isbn(
                    book["isbn"]
                )

                book["cover"] = (
                    cover or ""
                )

                new_books.append(
                    book
                )

                progress.progress(
                    (i + 1)
                    / max(
                        rows,
                        1
                    )
                )


            if new_books:

                st.session_state.books.extend(
                    new_books
                )

                save_books(
                    st.session_state.books
                )

                st.success(
                    f"Woven {len(new_books)} "
                    "books into your tree."
                )

            else:

                st.warning(
                    "No usable books were found "
                    "in that CSV."
                )


        except Exception as exc:

            st.error(
                "Something went wrong reading "
                f"that file: {exc}"
            )

    st.markdown(
        "</div>",
        unsafe_allow_html=True
    )
