```python
import io
import re
import hashlib
import unicodedata
from typing import Dict, List, Optional, Tuple

import pandas as pd
import requests
import streamlit as st


# ============================================================
# PAGE SETUP
# ============================================================

st.set_page_config(
    page_title="My Book Tree",
    page_icon="🌿",
    layout="wide",
    initial_sidebar_state="expanded",
)


# ============================================================
# THEMES
# ============================================================

THEMES = {
    "Velvet Conservatory": {
        "background": "#160F16",
        "surface": "#211622",
        "surface_alt": "#2C1A2B",
        "text": "#F7EAF0",
        "muted": "#C8AEBB",
        "accent": "#D36A8A",
        "accent_2": "#4E9A78",
        "border": "#74405A",
        "branch": "#87516A",
        "shadow": "rgba(0,0,0,.45)",
        "heading": "Cormorant Garamond",
        "body": "Lora",
    },
    "Midnight Library": {
        "background": "#0B101A",
        "surface": "#111B2B",
        "surface_alt": "#18243A",
        "text": "#EEF2FF",
        "muted": "#AAB7D4",
        "accent": "#9684EF",
        "accent_2": "#5EA7C7",
        "border": "#4C4B79",
        "branch": "#5F6598",
        "shadow": "rgba(0,0,0,.5)",
        "heading": "Cinzel",
        "body": "Libre Baskerville",
    },
    "Oxblood & Rose": {
        "background": "#190A0D",
        "surface": "#281216",
        "surface_alt": "#35191E",
        "text": "#F8E9E5",
        "muted": "#D0A5A2",
        "accent": "#C94F66",
        "accent_2": "#966A86",
        "border": "#75404B",
        "branch": "#8C4C58",
        "shadow": "rgba(0,0,0,.5)",
        "heading": "Playfair Display",
        "body": "Lora",
    },
    "Enchanted Garden": {
        "background": "#091610",
        "surface": "#10241B",
        "surface_alt": "#173126",
        "text": "#EEF6EA",
        "muted": "#B3CBB6",
        "accent": "#B77BC8",
        "accent_2": "#5AAA7B",
        "border": "#47735B",
        "branch": "#5D8C6C",
        "shadow": "rgba(0,0,0,.48)",
        "heading": "Libre Baskerville",
        "body": "Cormorant Garamond",
    },
    "Sapphire Study": {
        "background": "#090F18",
        "surface": "#101A28",
        "surface_alt": "#17283A",
        "text": "#EDF5FA",
        "muted": "#A8C0D0",
        "accent": "#4E94BE",
        "accent_2": "#A85D96",
        "border": "#3D637C",
        "branch": "#4A7892",
        "shadow": "rgba(0,0,0,.5)",
        "heading": "Bodoni Moda",
        "body": "Libre Baskerville",
    },
}


# ============================================================
# SESSION STATE
# ============================================================

def initialize_state():
    defaults = {
        "books": pd.DataFrame(),
        "theme": "Velvet Conservatory",
        "library_loaded": False,
        "library_source": "",
        "upload_hash": None,
    }

    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value


initialize_state()


# ============================================================
# CSS
# ============================================================

def apply_theme(theme: dict):

    st.markdown(
        f"""
        <style>

        @import url('https://fonts.googleapis.com/css2?family=Bodoni+Moda:wght@400;500;600&family=Cinzel:wght@400;500;600&family=Cormorant+Garamond:wght@400;500;600;700&family=Libre+Baskerville:wght@400;700&family=Lora:wght@400;500;600&family=Playfair+Display:wght@400;500;600;700&display=swap');

        :root {{
            --bg: {theme["background"]};
            --surface: {theme["surface"]};
            --surface-alt: {theme["surface_alt"]};
            --text: {theme["text"]};
            --muted: {theme["muted"]};
            --accent: {theme["accent"]};
            --accent2: {theme["accent_2"]};
            --border: {theme["border"]};
            --branch: {theme["branch"]};
            --shadow: {theme["shadow"]};
        }}

        html,
        body,
        [data-testid="stAppViewContainer"],
        [data-testid="stAppViewContainer"] > .main {{
            background: var(--bg) !important;
        }}

        [data-testid="stHeader"] {{
            background: transparent !important;
        }}

        .block-container {{
            max-width: 1450px;
            padding-top: 1rem;
            padding-bottom: 4rem;
        }}

        /* GENERAL TEXT */

        p,
        label,
        .stMarkdown,
        .stCaption {{
            color: var(--text);
        }}

        h1,
        h2,
        h3 {{
            font-family: '{theme["heading"]}', Georgia, serif !important;
            color: var(--text) !important;
        }}

        /* HEADER */

        .book-tree-header {{
            text-align: center;
            padding: 1.5rem 0 1rem;
        }}

        .book-tree-eyebrow {{
            color: var(--accent);
            text-transform: uppercase;
            letter-spacing: .32em;
            font-size: .68rem;
            font-weight: 600;
            margin-bottom: .7rem;
        }}

        .book-tree-title {{
            font-family: '{theme["heading"]}', Georgia, serif;
            font-size: clamp(3.2rem, 7vw, 6.5rem);
            line-height: .95;
            font-weight: 500;
            color: var(--text);
            margin: 0;
            text-shadow: 0 8px 30px var(--shadow);
        }}

        .book-tree-subtitle {{
            font-family: '{theme["body"]}', Georgia, serif;
            color: var(--muted);
            font-size: 1rem;
            margin-top: .8rem;
            letter-spacing: .08em;
        }}

        .vine {{
            width: min(650px, 80%);
            height: 40px;
            margin: .7rem auto 0;
            position: relative;
        }}

        .vine::before {{
            content: "";
            position: absolute;
            left: 5%;
            right: 5%;
            top: 18px;
            border-top: 2px solid var(--accent2);
            border-radius: 50%;
            transform: rotate(-1deg);
        }}

        .vine::after {{
            content: "❧   ❦   ❧";
            position: absolute;
            left: 50%;
            top: 2px;
            transform: translateX(-50%);
            color: var(--accent2);
            font-size: 1.1rem;
            letter-spacing: .5rem;
        }}

        /* STATISTICS */

        .stats {{
            display: flex;
            justify-content: center;
            gap: clamp(2rem, 7vw, 6rem);
            flex-wrap: wrap;
            margin: .5rem 0 2rem;
        }}

        .stat {{
            text-align: center;
            min-width: 90px;
        }}

        .stat-number {{
            display: block;
            font-family: '{theme["heading"]}', Georgia, serif;
            color: var(--accent);
            font-size: 2rem;
            line-height: 1;
        }}

        .stat-label {{
            display: block;
            color: var(--muted);
            font-size: .65rem;
            letter-spacing: .17em;
            text-transform: uppercase;
            margin-top: .4rem;
        }}

        /* SIDEBAR */

        [data-testid="stSidebar"] {{
            background:
                linear-gradient(
                    180deg,
                    var(--surface),
                    var(--bg)
                ) !important;
            border-right: 1px solid var(--border);
        }}

        [data-testid="stSidebar"] * {{
            color: var(--text);
        }}

        /* CONTROLS */

        .control-heading {{
            font-family: '{theme["heading"]}', Georgia, serif;
            font-size: 1.4rem;
            color: var(--text);
            margin: .5rem 0 .8rem;
        }}

        div[data-baseweb="select"] > div {{
            background: var(--surface) !important;
            border: 1px solid var(--border) !important;
            color: var(--text) !important;
            border-radius: 10px !important;
        }}

        div[data-baseweb="select"] span {{
            color: var(--text) !important;
        }}

        ul[role="listbox"] {{
            background: var(--surface-alt) !important;
            border: 1px solid var(--border) !important;
        }}

        li[role="option"] {{
            background: var(--surface-alt) !important;
            color: var(--text) !important;
        }}

        li[role="option"]:hover {{
            background: var(--surface) !important;
            color: var(--accent) !important;
        }}

        .stTextInput > div > div {{
            background: var(--surface) !important;
            border: 1px solid var(--border) !important;
            border-radius: 10px !important;
        }}

        .stTextInput input {{
            color: var(--text) !important;
            background: transparent !important;
        }}

        .stTextInput input::placeholder {{
            color: var(--muted) !important;
        }}

        /* TREE */

        .tree-introduction {{
            text-align: center;
            color: var(--muted);
            font-family: '{theme["body"]}', Georgia, serif;
            font-size: .78rem;
            letter-spacing: .16em;
            text-transform: uppercase;
            margin: 1.5rem 0 .8rem;
        }}

        .tree-root {{
            text-align: center;
            margin-bottom: 1.3rem;
        }}

        .tree-root-title {{
            display: inline-block;
            font-family: '{theme["heading"]}', Georgia, serif;
            font-size: 1.5rem;
            color: var(--accent);
            padding: .4rem 2rem .6rem;
            border-bottom: 1px solid var(--border);
        }}

        /* EXPANDERS */

        [data-testid="stExpander"] {{
            background: transparent !important;
            border: none !important;
            margin-bottom: .45rem;
        }}

        [data-testid="stExpander"] details {{
            background: transparent !important;
            border: none !important;
        }}

        [data-testid="stExpander"] summary {{
            background:
                linear-gradient(
                    90deg,
                    var(--surface),
                    var(--surface-alt)
                ) !important;
            border: 1px solid var(--border) !important;
            border-radius: 18px 34px 18px 34px !important;
            color: var(--text) !important;
            padding: .7rem 1.1rem !important;
            box-shadow: 0 6px 20px var(--shadow);
            transition: .2s ease;
        }}

        [data-testid="stExpander"] summary:hover {{
            border-color: var(--accent) !important;
            transform: translateX(3px);
        }}

        [data-testid="stExpander"] summary p {{
            color: var(--text) !important;
            font-family: '{theme["heading"]}', Georgia, serif !important;
            font-size: 1.05rem !important;
        }}

        [data-testid="stExpander"] > div {{
            border-left: 2px solid var(--branch) !important;
            margin-left: 1.4rem;
            padding-left: 1.1rem !important;
        }}

        /* BOOKS */

        .book-row {{
            display: flex;
            align-items: center;
            gap: 1rem;
            padding: .75rem .5rem;
            margin: .25rem 0;
            border-bottom: 1px solid var(--border);
        }}

        .book-cover {{
            width: 52px;
            height: 74px;
            object-fit: cover;
            border-radius: 3px 8px 8px 3px;
            box-shadow: 4px 6px 15px var(--shadow);
            border: 1px solid var(--border);
            flex-shrink: 0;
        }}

        .book-placeholder {{
            width: 52px;
            height: 74px;
            display: flex;
            align-items: center;
            justify-content: center;
            background: var(--surface-alt);
            color: var(--accent);
            border: 1px solid var(--border);
            border-radius: 3px 8px 8px 3px;
            flex-shrink: 0;
            font-family: '{theme["heading"]}', Georgia, serif;
            font-size: 1.5rem;
        }}

        .book-details {{
            min-width: 0;
        }}

        .book-title {{
            font-family: '{theme["heading"]}', Georgia, serif;
            color: var(--text);
            font-size: 1.05rem;
            font-weight: 600;
        }}

        .book-meta {{
            color: var(--muted);
            font-family: '{theme["body"]}', Georgia, serif;
            font-size: .75rem;
            margin-top: .25rem;
        }}

        .book-status {{
            display: inline-block;
            border: 1px solid var(--border);
            border-radius: 20px;
            padding: .1rem .5rem;
            margin-left: .4rem;
            font-size: .62rem;
        }}

        .book-rating {{
            color: var(--accent);
            margin-left: .45rem;
        }}

        /* BUTTONS */

        .stButton > button {{
            background: transparent !important;
            color: var(--text) !important;
            border: 1px solid var(--border) !important;
            border-radius: 999px !important;
        }}

        .stButton > button:hover {{
            color: var(--accent) !important;
            border-color: var(--accent) !important;
        }}

        /* FILE UPLOADER */

        [data-testid="stFileUploader"] section {{
            background: var(--surface) !important;
            border-color: var(--border) !important;
        }}

        /* DIVIDER */

        hr {{
            border-color: var(--border) !important;
        }}

        /* MOBILE */

        @media (max-width: 700px) {{
            .block-container {{
                padding-left: .7rem;
                padding-right: .7rem;
            }}

            .book-tree-title {{
                font-size: 3.2rem;
            }}

            .stats {{
                gap: 1.5rem;
            }}
        }}

        </style>
        """,
        unsafe_allow_html=True,
    )


# ============================================================
# DATA HELPERS
# ============================================================

def safe_text(value, default=""):
    if value is None:
        return default

    try:
        if pd.isna(value):
            return default
    except (TypeError, ValueError):
        pass

    text = str(value).strip()

    if text.lower() in {"nan", "none", "null"}:
        return default

    return text


def normalize_text(value):
    text = safe_text(value)

    text = unicodedata.normalize("NFKD", text)

    text = (
        text.encode("ascii", "ignore")
        .decode()
    )

    text = re.sub(
        r"[^a-zA-Z0-9]+",
        " ",
        text,
    )

    return text.lower().strip()


def parse_number(value):
    text = safe_text(value)

    match = re.search(
        r"\d+(?:\.\d+)?",
        text,
    )

    if not match:
        return None

    try:
        return float(match.group())
    except ValueError:
        return None


def find_column(
    df: pd.DataFrame,
    possible_names: List[str],
):
    normalized = {
        normalize_text(column): column
        for column in df.columns
    }

    for name in possible_names:
        key = normalize_text(name)

        if key in normalized:
            return normalized[key]

    return None


def get_value(
    row: pd.Series,
    possible_names: List[str],
):
    columns = list(row.index)

    normalized_columns = {
        normalize_text(column): column
        for column in columns
    }

    for name in possible_names:
        key = normalize_text(name)

        if key in normalized_columns:
            value = safe_text(
                row[normalized_columns[key]]
            )

            if value:
                return value

    return ""


# ============================================================
# SERIES DETECTION
# ============================================================

def detect_series(
    row: pd.Series,
) -> Tuple[str, Optional[float]]:

    series = get_value(
        row,
        [
            "Series",
            "Series Name",
            "Series Title",
        ],
    )

    number = get_value(
        row,
        [
            "Series Number",
            "Series #",
            "Book Number",
            "Book #",
        ],
    )

    series_number = (
        parse_number(number)
        if number
        else None
    )

    if series:
        return series, series_number

    title = get_value(
        row,
        ["Title"],
    )

    patterns = [
        r"^(.*?)\s*\(\s*[^)]*?(?:book|series)\s*#?\s*(\d+(?:\.\d+)?)\s*\)$",
        r"^(.*?)\s+(?:book|#)\s*(\d+(?:\.\d+)?)$",
        r"^(.*?)\s*,\s*(?:book|novel)\s+(\d+(?:\.\d+)?)$",
        r"^(.*?)\s*#\s*(\d+(?:\.\d+)?)$",
    ]

    for pattern in patterns:
        match = re.match(
            pattern,
            title,
            flags=re.IGNORECASE,
        )

        if match:
            name = match.group(1).strip()

            if name:
                return (
                    name,
                    float(match.group(2)),
                )

    return "", None


# ============================================================
# STATUS / GENRE
# ============================================================

def detect_status(row: pd.Series) -> str:

    shelf = get_value(
        row,
        [
            "Exclusive Shelf",
            "Status",
        ],
    )

    shelf_key = normalize_text(shelf)

    if "currently" in shelf_key:
        return "Currently Reading"

    if shelf_key == "read":
        return "Read"

    if "read" in shelf_key and "to read" not in shelf_key:
        return "Read"

    return "Want to Read"


def detect_genre(row: pd.Series) -> str:

    genre = get_value(
        row,
        [
            "Genre",
            "Genres",
            "Primary Genre",
        ],
    )

    if genre:
        return genre.split(",")[0].strip()

    return "Uncategorized"


# ============================================================
# GOODREADS IMPORT
# ============================================================

def normalize_goodreads_csv(
    dataframe: pd.DataFrame,
) -> pd.DataFrame:

    records = []

    for index, row in dataframe.iterrows():

        title = get_value(
            row,
            ["Title"],
        )

        author = get_value(
            row,
            [
                "Author",
                "Author Name",
            ],
        )

        if not title and not author:
            continue

        series, series_number = detect_series(row)

        rating = parse_number(
            get_value(
                row,
                [
                    "My Rating",
                    "Rating",
                ],
            )
        )

        year = parse_number(
            get_value(
                row,
                [
                    "Original Publication Year",
                    "Year Published",
                ],
            )
        )

        cover = get_value(
            row,
            [
                "Cover URL",
                "Cover",
            ],
        )

        records.append(
            {
                "id": hashlib.sha1(
                    f"{index}-{title}-{author}".encode()
                ).hexdigest(),
                "title": title or "Untitled",
                "author": author or "Unknown Author",
                "series": series,
                "series_number": series_number,
                "genre": detect_genre(row),
                "status": detect_status(row),
                "rating": (
                    rating
                    if rating is not None
                    else 0.0
                ),
                "year": (
                    int(year)
                    if year is not None and year > 0
                    else None
                ),
                "cover": cover,
            }
        )

    return pd.DataFrame(
        records,
        columns=[
            "id",
            "title",
            "author",
            "series",
            "series_number",
            "genre",
            "status",
            "rating",
            "year",
            "cover",
        ],
    )


# ============================================================
# OPEN LIBRARY
# ============================================================

@st.cache_data(
    ttl=86400,
    show_spinner=False,
)
def lookup_openlibrary(
    title: str,
    author: str,
) -> dict:

    try:

        response = requests.get(
            "https://openlibrary.org/search.json",
            params={
                "title": title,
                "author": author,
                "limit": 5,
            },
            timeout=8,
            headers={
                "User-Agent": (
                    "My-Book-Tree/1.0 "
                    "(personal library app)"
                )
            },
        )

        response.raise_for_status()

        docs = response.json().get(
            "docs",
            [],
        )

        if not docs:
            return {}

        best = docs[0]

        cover = ""

        cover_id = best.get("cover_i")

        if cover_id:
            cover = (
                "https://covers.openlibrary.org/"
                f"b/id/{cover_id}-L.jpg"
            )

        subjects = best.get("subject") or []
        genres = best.get("genre") or []

        genre = ""

        if genres:
            genre = genres[0]
        elif subjects:
            genre = subjects[0]

        series = ""

        series_values = best.get("series") or []

        if series_values:
            series = series_values[0]

        return {
            "cover": cover,
            "genre": genre,
            "series": series,
        }

    except (
        requests.RequestException,
        ValueError,
        TypeError,
    ):
        return {}


def enrich_books(
    dataframe: pd.DataFrame,
    limit: int = 75,
) -> pd.DataFrame:

    if dataframe.empty:
        return dataframe

    result = dataframe.copy()
    checked = 0

    for index in result.index:

        missing_cover = not safe_text(
            result.at[index, "cover"]
        )

        missing_genre = (
            safe_text(
                result.at[index, "genre"]
            )
            == "Uncategorized"
        )

        missing_series = not safe_text(
            result.at[index, "series"]
        )

        if not (
            missing_cover
            or missing_genre
            or missing_series
        ):
            continue

        if checked >= limit:
            break

        info = lookup_openlibrary(
            safe_text(
                result.at[index, "title"]
            ),
            safe_text(
                result.at[index, "author"]
            ),
        )

        if missing_cover and info.get("cover"):
            result.at[index, "cover"] = info["cover"]

        if missing_genre and info.get("genre"):
            result.at[index, "genre"] = info["genre"]

        if missing_series and info.get("series"):
            result.at[index, "series"] = info["series"]

        checked += 1

    return result


# ============================================================
# DEMO LIBRARY
# ============================================================

def create_demo_library():

    demo = [
        (
            "Lillian Lark",
            "The Witches' Oath",
            "The Monstrous Series",
            1,
            "Fantasy Romance",
            "Read",
            5,
        ),
        (
            "Lillian Lark",
            "The Gargoyle's Captive",
            "The Monstrous Series",
            2,
            "Fantasy Romance",
            "Currently Reading",
            4,
        ),
        (
            "Lillian Lark",
            "The Coven's Promise",
            "The Monstrous Series",
            3,
            "Fantasy Romance",
            "Want to Read",
            0,
        ),
        (
            "Lillian Lark",
            "A House of Salt",
            "",
            None,
            "Fantasy Romance",
            "Read",
            5,
        ),
        (
            "Emily Wilde",
            "Emily Wilde's Encyclopaedia of Faeries",
            "Emily Wilde",
            1,
            "Fantasy",
            "Read",
            5,
        ),
        (
            "Emily Wilde",
            "Emily Wilde's Map of the Otherlands",
            "Emily Wilde",
            2,
            "Fantasy",
            "Want to Read",
            0,
        ),
        (
            "T. Kingfisher",
            "Nettle & Bone",
            "",
            None,
            "Fantasy",
            "Read",
            4,
        ),
        (
            "T. Kingfisher",
            "A Sorceress Comes to Call",
            "",
            None,
            "Fantasy",
            "Currently Reading",
            5,
        ),
        (
            "V. E. Schwab",
            "A Darker Shade of Magic",
            "Shades of Magic",
            1,
            "Fantasy",
            "Read",
            5,
        ),
        (
            "V. E. Schwab",
            "A Gathering of Shadows",
            "Shades of Magic",
            2,
            "Fantasy",
            "Want to Read",
            0,
        ),
    ]

    records = []

    for number, item in enumerate(demo):

        (
            author,
            title,
            series,
            series_number,
            genre,
            status,
            rating,
        ) = item

        records.append(
            {
                "id": f"demo-{number}",
                "title": title,
                "author": author,
                "series": series,
                "series_number": series_number,
                "genre": genre,
                "status": status,
                "rating": float(rating),
                "year": None,
                "cover": "",
            }
        )

    return pd.DataFrame(records)


# ============================================================
# FILTERING
# ============================================================

def filter_books(
    dataframe: pd.DataFrame,
    search: str,
    genre: str,
    status: str,
    sort_by: str,
) -> pd.DataFrame:

    if dataframe.empty:
        return dataframe

    result = dataframe.copy()

    search_value = normalize_text(search)

    if search_value:

        mask = (
            result["title"]
            .map(normalize_text)
            .str.contains(
                search_value,
                na=False,
                regex=False,
            )
            |
            result["author"]
            .map(normalize_text)
            .str.contains(
                search_value,
                na=False,
                regex=False,
            )
            |
            result["series"]
            .map(normalize_text)
            .str.contains(
                search_value,
                na=False,
                regex=False,
            )
            |
            result["genre"]
            .map(normalize_text)
            .str.contains(
                search_value,
                na=False,
                regex=False,
            )
        )

        result = result[mask]

    if genre != "All Genres":
        result = result[
            result["genre"] == genre
        ]

    if status != "All Statuses":
        result = result[
            result["status"] == status
        ]

    if sort_by == "Author A–Z":

        result = result.sort_values(
            ["author", "title"],
            key=lambda s:
                s.str.lower()
                if s.dtype == "object"
                else s,
        )

    elif sort_by == "Author Z–A":

        result = result.sort_values(
            ["author", "title"],
            ascending=[False, True],
            key=lambda s:
                s.str.lower()
                if s.dtype == "object"
                else s,
        )

    elif sort_by == "Title A–Z":

        result = result.sort_values(
            "title",
            key=lambda s: s.str.lower(),
        )

    elif sort_by == "Title Z–A":

        result = result.sort_values(
            "title",
            ascending=False,
            key=lambda s: s.str.lower(),
        )

    elif sort_by == "Highest Rated":

        result = result.sort_values(
            "rating",
            ascending=False,
        )

    elif sort_by == "Lowest Rated":

        result = result.sort_values(
            "rating",
            ascending=True,
        )

    elif sort_by == "Newest":

        result = result.sort_values(
            "year",
            ascending=False,
            na_position="last",
        )

    elif sort_by == "Oldest":

        result = result.sort_values(
            "year",
            ascending=True,
            na_position="last",
        )

    elif sort_by in {
        "Read",
        "Currently Reading",
        "Want to Read",
    }:

        result = result[
            result["status"] == sort_by
        ]

    return result


# ============================================================
# BOOK DISPLAY
# ============================================================

def stars(rating) -> str:

    try:
        value = float(rating)
    except (
        TypeError,
        ValueError,
    ):
        value = 0

    if value <= 0:
        return "Not rated"

    rounded = max(
        0,
        min(
            5,
            round(value),
        ),
    )

    return (
        "★" * rounded
        + "☆" * (5 - rounded)
    )


def render_book(book: dict):

    cover = safe_text(
        book.get("cover")
    )

    title = safe_text(
        book.get(
            "title",
            "Untitled",
        )
    )

    genre = safe_text(
        book.get(
            "genre",
            "Uncategorized",
        )
    )

    status = safe_text(
        book.get(
            "status",
            "Want to Read",
        )
    )

    rating = book.get(
        "rating",
        0,
    )

    series_number = book.get(
        "series_number"
    )

    number_text = ""

    if (
        series_number is not None
        and not pd.isna(series_number)
    ):
        try:
            number_text = (
                f"Book {float(series_number):g}"
            )
        except (
            TypeError,
            ValueError,
        ):
            number_text = ""

    if cover:

        image = (
            f'<img class="book-cover" '
            f'src="{cover}" '
            f'alt="Book cover">'
        )

    else:

        image = (
            '<div class="book-placeholder">'
            "✦"
            "</div>"
        )

    display_title = title

    if number_text:
        display_title += f" · {number_text}"

    st.markdown(
        f"""
        <div class="book-row">

            {image}

            <div class="book-details">

                <div class="book-title">
                    {display_title}
                </div>

                <div class="book-meta">

                    {genre}

                    <span class="book-status">
                        {status}
                    </span>

                    <span class="book-rating">
                        {stars(rating)}
                    </span>

                </div>

            </div>

        </div>
        """,
        unsafe_allow_html=True,
    )


# ============================================================
# TREE
# ============================================================

def build_tree(
    dataframe: pd.DataFrame,
) -> Dict:

    tree = {}

    if dataframe.empty:
        return tree

    authors = sorted(
        dataframe["author"]
        .dropna()
        .unique(),
        key=str.lower,
    )

    for author in authors:

        author_df = dataframe[
            dataframe["author"] == author
        ]

        series = {}
        standalone = []

        for _, row in author_df.iterrows():

            record = row.to_dict()

            series_name = safe_text(
                record.get("series")
            )

            if series_name:

                series.setdefault(
                    series_name,
                    [],
                ).append(record)

            else:

                standalone.append(record)

        for series_name in series:

            series[series_name] = sorted(
                series[series_name],
                key=lambda book: (
                    book.get("series_number") is None,
                    book.get("series_number")
                    if book.get("series_number") is not None
                    else 9999,
                    safe_text(
                        book.get("title")
                    ).lower(),
                ),
            )

        tree[author] = {
            "series": dict(
                sorted(
                    series.items(),
                    key=lambda item:
                        item[0].lower(),
                )
            ),
            "standalone": sorted(
                standalone,
                key=lambda book:
                    safe_text(
                        book.get("title")
                    ).lower(),
            ),
        }

    return tree


def render_tree(
    dataframe: pd.DataFrame,
):

    tree = build_tree(dataframe)

    if not tree:

        st.markdown(
            """
            <div style="
                text-align:center;
                padding:5rem 1rem;
                color:var(--muted);
                font-family:'Cormorant Garamond',serif;
                font-size:1.5rem;
            ">
                No books match your search.
            </div>
            """,
            unsafe_allow_html=True,
        )

        return

    st.markdown(
        """
        <div class="tree-introduction">
            Your literary family tree
        </div>

        <div class="tree-root">
            <div class="tree-root-title">
                🌿 My Library
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    for author, author_data in tree.items():

        total_author_books = (
            sum(
                len(books)
                for books in author_data["series"].values()
            )
            + len(author_data["standalone"])
        )

        book_word = (
            "book"
            if total_author_books == 1
            else "books"
        )

        author_label = (
            f"✦  {author}  ·  "
            f"{total_author_books} {book_word}"
        )

        with st.expander(
            author_label,
            expanded=False,
        ):

            series_data = author_data["series"]

            for series_name, books in series_data.items():

                book_word = (
                    "book"
                    if len(books) == 1
                    else "books"
                )

                series_label = (
                    f"❧  {series_name}  ·  "
                    f"{len(books)} {book_word}"
                )

                with st.expander(
                    series_label,
                    expanded=False,
                ):

                    for book in books:
                        render_book(book)

            standalone = author_data["standalone"]

            if standalone:

                book_word = (
                    "book"
                    if len(standalone) == 1
                    else "books"
                )

                with st.expander(
                    (
                        f"❦  Standalone Books  ·  "
                        f"{len(standalone)} {book_word}"
                    ),
                    expanded=False,
                ):

                    for book in standalone:
                        render_book(book)


# ============================================================
# HEADER
# ============================================================

def render_header(
    dataframe: pd.DataFrame,
):

    total = len(dataframe)

    authors = (
        dataframe["author"].nunique()
        if not dataframe.empty
        else 0
    )

    series = (
        dataframe[
            dataframe["series"]
            .astype(str)
            .str.strip()
            != ""
        ]["series"].nunique()
        if not dataframe.empty
        else 0
    )

    read = (
        int(
            (
                dataframe["status"]
                == "Read"
            ).sum()
        )
        if not dataframe.empty
        else 0
    )

    st.markdown(
        """
        <div class="book-tree-header">

            <div class="book-tree-eyebrow">
                A Literary Family Tree
            </div>

            <div class="book-tree-title">
                My Book Tree
            </div>

            <div class="book-tree-subtitle">
                Authors · Series · Stories
            </div>

            <div class="vine"></div>

        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown(
        f"""
        <div class="stats">

            <div class="stat">
                <span class="stat-number">
                    {total}
                </span>
                <span class="stat-label">
                    Books
                </span>
            </div>

            <div class="stat">
                <span class="stat-number">
                    {authors}
                </span>
                <span class="stat-label">
                    Authors
                </span>
            </div>

            <div class="stat">
                <span class="stat-number">
                    {series}
                </span>
                <span class="stat-label">
                    Series
                </span>
            </div>

            <div class="stat">
                <span class="stat-number">
                    {read}
                </span>
                <span class="stat-label">
                    Read
                </span>
            </div>

        </div>
        """,
        unsafe_allow_html=True,
    )


# ============================================================
# CONTROLS
# ============================================================

def render_controls(
    dataframe: pd.DataFrame,
) -> pd.DataFrame:

    if dataframe.empty:
        return dataframe

    genres = sorted(
        [
            safe_text(value)
            for value in dataframe["genre"]
            .dropna()
            .unique()
            if safe_text(value)
        ],
        key=str.lower,
    )

    genre_options = [
        "All Genres"
    ] + genres

    status_options = [
        "All Statuses",
        "Read",
        "Currently Reading",
        "Want to Read",
    ]

    sort_options = [
        "Author A–Z",
        "Author Z–A",
        "Title A–Z",
        "Title Z–A",
        "Highest Rated",
        "Lowest Rated",
        "Newest",
        "Oldest",
        "Read",
        "Currently Reading",
        "Want to Read",
    ]

    st.markdown(
        '<div class="control-heading">Find a Book</div>',
        unsafe_allow_html=True,
    )

    c1, c2, c3, c4 = st.columns(
        [2.2, 1, 1, 1.4]
    )

    with c1:

        search = st.text_input(
            "Search",
            placeholder=(
                "Title, author, series, genre..."
            ),
        )

    with c2:

        genre = st.selectbox(
            "Genre",
            genre_options,
        )

    with c3:

        status = st.selectbox(
            "Status",
            status_options,
        )

    with c4:

        sort_by = st.selectbox(
            "Sort",
            sort_options,
        )

    return filter_books(
        dataframe,
        search,
        genre,
        status,
        sort_by,
    )


# ============================================================
# SIDEBAR
# ============================================================

def render_sidebar():

    with st.sidebar:

        st.markdown(
            "# 🌿 My Book Tree"
        )

        st.caption(
            "Your library, arranged like "
            "a literary family tree."
        )

        st.divider()

        st.markdown(
            "### Appearance"
        )

        theme_names = list(THEMES.keys())

        current_theme = st.session_state.get(
            "theme",
            theme_names[0],
        )

        if current_theme not in theme_names:
            current_theme = theme_names[0]

        selected_theme = st.selectbox(
            "Choose a bookish theme",
            theme_names,
            index=theme_names.index(
                current_theme
            ),
            key="theme_choice",
        )

        if selected_theme != st.session_state.theme:

            st.session_state.theme = selected_theme

            st.rerun()

        st.divider()

        st.markdown(
            "### Your Library"
        )

        uploaded = st.file_uploader(
            "Import Goodreads CSV",
            type=["csv"],
        )

        if uploaded is not None:

            file_hash = hashlib.sha1(
                uploaded.getvalue()
            ).hexdigest()

            previous_hash = (
                st.session_state.get(
                    "upload_hash"
                )
            )

            if file_hash != previous_hash:

                try:

                    uploaded_df = pd.read_csv(
                        io.BytesIO(
                            uploaded.getvalue()
                        )
                    )

                    normalized = (
                        normalize_goodreads_csv(
                            uploaded_df
                        )
                    )

                    if normalized.empty:

                        st.error(
                            "I couldn't find any "
                            "recognizable books in "
                            "that CSV."
                        )

                    else:

                        st.session_state.books = normalized
                        st.session_state.library_loaded = True
                        st.session_state.library_source = uploaded.name
                        st.session_state.upload_hash = file_hash

                        st.rerun()

                except Exception as error:

                    st.error(
                        f"Could not read CSV: {error}"
                    )

        if st.session_state.library_loaded:

            st.caption(
                f"Loaded from: "
                f"{st.session_state.library_source}"
            )

            if st.button(
                "Find missing covers & genres",
                use_container_width=True,
            ):

                with st.spinner(
                    "Looking up book information..."
                ):

                    st.session_state.books = enrich_books(
                        st.session_state.books
                    )

                st.success(
                    "Finished checking the library."
                )

        else:

            st.caption(
                "A sample library is shown until "
                "you import your Goodreads CSV."
            )

        st.divider()

        if st.button(
            "Use sample library",
            use_container_width=True,
        ):

            st.session_state.books = (
                create_demo_library()
            )

            st.session_state.library_loaded = False
            st.session_state.library_source = "Sample library"
            st.session_state.upload_hash = None

            st.rerun()


# ============================================================
# MAIN
# ============================================================

def main():

    theme_name = st.session_state.get(
        "theme",
        "Velvet Conservatory",
    )

    if theme_name not in THEMES:

        theme_name = "Velvet Conservatory"

        st.session_state.theme = theme_name

    theme = THEMES[theme_name]

    apply_theme(theme)

    render_sidebar()

    books = st.session_state.get("books")

    if not isinstance(
        books,
        pd.DataFrame,
    ) or books.empty:

        books = create_demo_library()

        if not st.session_state.library_loaded:
            st.session_state.books = books

    render_header(books)

    filtered_books = render_controls(
        books
    )

    st.divider()

    render_tree(filtered_books)

    st.markdown(
        """
        <div style="
            text-align:center;
            color:var(--muted);
            margin-top:3rem;
            font-size:.75rem;
            letter-spacing:.08em;
        ">
            ❦  My Book Tree  ❦
        </div>
        """,
        unsafe_allow_html=True,
    )


if __name__ == "__main__":
    main()
```
