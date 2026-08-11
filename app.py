# ============================================================
# My Book Tree — Streamlit version
# ============================================================

import streamlit as st
import pandas as pd
import requests
import json
import re
import uuid
from pathlib import Path


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
def fetch_from_google_books(title, author, isbn):

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

    s = str(shelf or "").lower()

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
