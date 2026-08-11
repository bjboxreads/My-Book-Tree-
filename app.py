"""My Book Tree — ancestry-style book library."""

import io
import re
import html
import hashlib
import unicodedata
from urllib.parse import quote_plus

import pandas as pd
import requests
import streamlit as st


st.set_page_config(
    page_title="My Book Tree",
    page_icon="🌿",
    layout="wide",
    initial_sidebar_state="collapsed",
)

APP_VERSION = "1.0.0"

THEMES = {
    "Velvet Conservatory": {
        "bg": "#160F16",
        "surface": "#211622",
        "surface_2": "#2D1B2B",
        "ink": "#F7EAF0",
        "muted": "#C9AEBB",
        "accent": "#D46A8A",
        "accent_2": "#4E9A78",
        "line": "#A54E70",
        "node": "#2A1725",
        "leaf": "#E8B4C8",
        "shadow": "rgba(0,0,0,.38)",
        "font_head": "Cormorant Garamond",
        "font_body": "Lora",
    },
    "Midnight Library": {
        "bg": "#0C1220",
        "surface": "#121B2D",
        "surface_2": "#18243A",
        "ink": "#EEF2FF",
        "muted": "#AAB7D4",
        "accent": "#8D7BE7",
        "accent_2": "#5EA7C7",
        "line": "#6357A5",
        "node": "#141F34",
        "leaf": "#B8B0F2",
        "shadow": "rgba(0,0,0,.45)",
        "font_head": "Cinzel",
        "font_body": "Libre Baskerville",
    },
    "Oxblood & Rose": {
        "bg": "#1A0C0E",
        "surface": "#281316",
        "surface_2": "#35191E",
        "ink": "#F8E9E5",
        "muted": "#D1A8A4",
        "accent": "#C34D62",
        "accent_2": "#8D6A86",
        "line": "#884052",
        "node": "#2A1115",
        "leaf": "#E0A0AA",
        "shadow": "rgba(0,0,0,.43)",
        "font_head": "Playfair Display",
        "font_body": "Lora",
    },
    "Enchanted Garden": {
        "bg": "#091711",
        "surface": "#10251C",
        "surface_2": "#173126",
        "ink": "#EEF6EA",
        "muted": "#B3CBB6",
        "accent": "#B37BC4",
        "accent_2": "#55A477",
        "line": "#5F8F70",
        "node": "#11291F",
        "leaf": "#C69BD0",
        "shadow": "rgba(0,0,0,.42)",
        "font_head": "Libre Baskerville",
        "font_body": "Cormorant Garamond",
    },
    "Sapphire Study": {
        "bg": "#0B101A",
        "surface": "#111B29",
        "surface_2": "#18283B",
        "ink": "#EDF5FA",
        "muted": "#A8C0D0",
        "accent": "#4E91B8",
        "accent_2": "#A65F93",
        "line": "#3C6D8A",
        "node": "#102235",
        "leaf": "#8FC2DD",
        "shadow": "rgba(0,0,0,.46)",
        "font_head": "Bodoni Moda",
        "font_body": "Libre Baskerville",
    },
}

STATUS_LABELS = {
    "read": "Read",
    "currently-reading": "Currently Reading",
    "to-read": "Want to Read",
}

SORT_OPTIONS = [
    "Author A–Z",
    "Author Z–A",
    "Title A–Z",
    "Title Z–A",
    "Highest rated",
    "Lowest rated",
    "Newest",
    "Oldest",
    "Read",
    "Currently Reading",
    "Want to Read",
]


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
        return ""

    return text


def normalize_key(value):
    text = (
        unicodedata.normalize("NFKD", safe_text(value))
        .encode("ascii", "ignore")
        .decode()
    )

    text = re.sub(
        r"[^a-z0-9]+",
        " ",
        text.lower(),
    ).strip()

    return text


def first_nonempty(row, names):
    for name in names:
        if name in row.index:
            value = safe_text(row[name])

            if value:
                return value

    return ""


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


def parse_date(value):
    text = safe_text(value)

    if not text:
        return pd.NaT

    return pd.to_datetime(
        text,
        errors="coerce",
    )


def parse_series_from_title(title):
    title = safe_text(title)

    patterns = [
        r"^(.*?)\s*\(\s*[^)]*(?:series|#)\s*#?\s*(\d+(?:\.\d+)?)\s*\)\s*$",
        r"^(.*?)\s*,\s*(?:book|novel)\s+(\d+(?:\.\d+)?)\s*$",
        r"^(.*?)\s+(?:book|#)\s*(\d+(?:\.\d+)?)\s*$",
        r"^(.*?)\s*#\s*(\d+(?:\.\d+)?)\s*$",
    ]

    for pattern in patterns:
        match = re.match(
            pattern,
            title,
            flags=re.IGNORECASE,
        )

        if match:
            series = match.group(1).strip(" -–—")
            number = parse_number(match.group(2))

            if series and number is not None:
                return series, number

    return "", None


def detect_series(row):
    series = first_nonempty(
        row,
        [
            "Series",
            "series",
            "Series Name",
            "series_name",
            "SeriesName",
            "Series Title",
        ],
    )

    number = first_nonempty(
        row,
        [
            "Series Number",
            "Series #",
            "series_number",
            "series number",
            "Book #",
            "Book Number",
        ],
    )

    parsed_number = (
        parse_number(number)
        if number
        else None
    )

    if series:
        return series, parsed_number

    title = first_nonempty(
        row,
        [
            "Title",
            "title",
        ],
    )

    return parse_series_from_title(title)


def detect_genre(row):
    explicit = first_nonempty(
        row,
        [
            "Genre",
            "Genres",
            "genre",
            "genres",
            "Primary Genre",
            "Genre(s)",
        ],
    )

    if explicit:
        return explicit.split(",")[0].strip()

    return ""


def detect_status(row):
    shelf = first_nonempty(
        row,
        [
            "Exclusive Shelf",
            "exclusive shelf",
            "Status",
            "status",
        ],
    )

    shelf_key = normalize_key(shelf).replace(
        " ",
        "-",
    )

    if shelf_key in {
        "read",
        "currently-reading",
        "to-read",
        "want-to-read",
    }:
        if shelf_key == "currently-reading":
            return "currently-reading"

        if shelf_key in {
            "to-read",
            "want-to-read",
        }:
            return "to-read"

        return "read"

    text = " ".join(
        first_nonempty(
            row,
            [name],
        )
        for name in [
            "Bookshelves",
            "bookshelves",
            "Exclusive Shelf",
            "exclusive shelf",
        ]
    ).lower()

    if (
        "currently-reading" in text
        or "currently reading" in text
    ):
        return "currently-reading"

    if (
        "read" in text
        and "to-read" not in text
        and "want-to-read" not in text
    ):
        return "read"

    return "to-read"


def clean_author(value):
    return re.sub(
        r"\s+",
        " ",
        safe_text(value),
    ).strip()


def clean_title(value):
    return re.sub(
        r"\s+",
        " ",
        safe_text(value),
    ).strip()


def book_id(row, index):
    raw = first_nonempty(
        row,
        [
            "Book Id",
            "book_id",
            "ISBN13",
            "ISBN",
            "Title",
        ],
    )

    if not raw:
        raw = f"row-{index}"

    return hashlib.sha1(
        f"{raw}-{index}".encode("utf-8")
    ).hexdigest()[:12]


def normalize_goodreads_dataframe(df):
    if df.empty:
        return pd.DataFrame()

    records = []

    for index, row in df.iterrows():
        title = clean_title(
            first_nonempty(
                row,
                [
                    "Title",
                    "title",
                ],
            )
        )

        author = clean_author(
            first_nonempty(
                row,
                [
                    "Author",
                    "author",
                    "Author Name",
                ],
            )
        )

        if not title and not author:
            continue

        series, series_number = detect_series(row)
        genre = detect_genre(row)
        status = detect_status(row)

        rating = parse_number(
            first_nonempty(
                row,
                [
                    "My Rating",
                    "my rating",
                    "Rating",
                    "rating",
                ],
            )
        )

        avg_rating = parse_number(
            first_nonempty(
                row,
                [
                    "Average Rating",
                    "average rating",
                ],
            )
        )

        date_read = parse_date(
            first_nonempty(
                row,
                [
                    "Date Read",
                    "date read",
                    "Date Added",
                ],
            )
        )

        year = parse_number(
            first_nonempty(
                row,
                [
                    "Original Publication Year",
                    "Year Published",
                    "year",
                ],
            )
        )

        cover = first_nonempty(
            row,
            [
                "Cover URL",
                "cover_url",
                "Cover",
                "cover",
            ],
        )

        records.append(
            {
                "id": book_id(row, index),
                "title": title or "Untitled",
                "author": author or "Unknown Author",
                "series": series,
                "series_number": series_number,
                "genre": genre or "Uncategorized",
                "status": status,
                "rating": (
                    rating
                    if rating is not None
                    else 0.0
                ),
                "avg_rating": (
                    avg_rating
                    if avg_rating is not None
                    else 0.0
                ),
                "date": date_read,
                "year": (
                    int(year)
                    if year is not None and year > 0
                    else None
                ),
                "cover": cover,
            }
        )

    return pd.DataFrame(records)


@st.cache_data(ttl=60 * 60 * 24)
def enrich_openlibrary(title, author):
    query = (
        f"title:{title} author:{author}"
    )

    url = "https://openlibrary.org/search.json"

    try:
        response = requests.get(
            url,
            params={
                "q": query,
                "limit": 5,
                "fields": (
                    "title,author_name,cover_i,"
                    "subject,genre,series,"
                    "first_publish_year"
                ),
            },
            timeout=8,
            headers={
                "User-Agent": "My-Book-Tree/1.0"
            },
        )

        response.raise_for_status()

        data = response.json()
        docs = data.get(
            "docs",
            [],
        )

        if not docs:
            return {
                "cover": "",
                "genre": "",
                "series": "",
            }

        title_key = normalize_key(title)
        author_key = normalize_key(author)

        ranked = []

        for doc in docs:
            doc_title = normalize_key(
                doc.get(
                    "title",
                    "",
                )
            )

            doc_authors = " ".join(
                doc.get(
                    "author_name"
                )
                or []
            )

            doc_author_key = normalize_key(
                doc_authors
            )

            title_score = int(
                bool(
                    title_key
                    and (
                        title_key == doc_title
                        or title_key in doc_title
                        or doc_title in title_key
                    )
                )
            )

            author_score = int(
                bool(
                    author_key
                    and (
                        author_key == doc_author_key
                        or author_key in doc_author_key
                        or doc_author_key in author_key
                    )
                )
            )

            ranked.append(
                (
                    title_score + author_score,
                    doc,
                )
            )

        ranked.sort(
            key=lambda item: item[0],
            reverse=True,
        )

        doc = ranked[0][1]

        subjects = doc.get(
            "subject"
        ) or []

        genres = doc.get(
            "genre"
        ) or []

        genre = (
            genres[0]
            if genres
            else (
                subjects[0]
                if subjects
                else ""
            )
        )

        series_values = doc.get(
            "series"
        ) or []

        if isinstance(
            series_values,
            str,
        ):
            series_values = [
                series_values
            ]

        series = (
            series_values[0]
            if series_values
            else ""
        )

        cover_id = doc.get(
            "cover_i"
        )

        cover = (
            f"https://covers.openlibrary.org/"
            f"b/id/{cover_id}-L.jpg"
            if cover_id
            else ""
        )

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
        return {
            "cover": "",
            "genre": "",
            "series": "",
        }


def enrich_missing_books(
    df,
    limit=80,
):
    if df.empty:
        return df

    result = df.copy()
    checked = 0

    for index in result.index:
        needs_cover = not safe_text(
            result.at[
                index,
                "cover",
            ]
        )

        needs_genre = (
            safe_text(
                result.at[
                    index,
                    "genre",
                ]
            )
            in {
                "",
                "Uncategorized",
            }
        )

        needs_series = not safe_text(
            result.at[
                index,
                "series",
            ]
        )

        if not (
            needs_cover
            or needs_genre
            or needs_series
        ):
            continue

        if checked >= limit:
            break

        info = enrich_openlibrary(
            result.at[
                index,
                "title",
            ],
            result.at[
                index,
                "author",
            ],
        )

        if (
            needs_cover
            and info.get("cover")
        ):
            result.at[
                index,
                "cover",
            ] = info["cover"]

        if (
            needs_genre
            and info.get("genre")
        ):
            result.at[
                index,
                "genre",
            ] = info["genre"]

        if (
            needs_series
            and info.get("series")
        ):
            result.at[
                index,
                "series",
            ] = info["series"]

        checked += 1

    return result


def get_demo_books():
    rows = [
        [
            "Lillian Lark",
            "The Witches' Oath",
            "The Monstrous Series",
            1,
            "Fantasy Romance",
            "read",
            5,
        ],
        [
            "Lillian Lark",
            "The Gargoyle's Captive",
            "The Monstrous Series",
            2,
            "Fantasy Romance",
            "currently-reading",
            4,
        ],
        [
            "Lillian Lark",
            "The Coven's Promise",
            "The Monstrous Series",
            3,
            "Fantasy Romance",
            "to-read",
            0,
        ],
        [
            "Lillian Lark",
            "A House of Salt",
            "",
            None,
            "Fantasy Romance",
            "read",
            5,
        ],
        [
            "Emily Wilde",
            "Emily Wilde's Encyclopaedia of Faeries",
            "Emily Wilde",
            1,
            "Fantasy",
            "read",
            5,
        ],
        [
            "Emily Wilde",
            "Emily Wilde's Map of the Otherlands",
            "Emily Wilde",
            2,
            "Fantasy",
            "to-read",
            0,
        ],
        [
            "T. Kingfisher",
            "Nettle & Bone",
            "",
            None,
            "Fantasy",
            "read",
            4,
        ],
        [
            "T. Kingfisher",
            "A Sorceress Comes to Call",
            "",
            None,
            "Fantasy",
            "currently-reading",
            5,
        ],
        [
            "V. E. Schwab",
            "A Darker Shade of Magic",
            "Shades of Magic",
            1,
            "Fantasy",
            "read",
            5,
        ],
        [
            "V. E. Schwab",
            "A Gathering of Shadows",
            "Shades of Magic",
            2,
            "Fantasy",
            "to-read",
            0,
        ],
    ]

    return pd.DataFrame(
        [
            {
                "id": f"demo-{i}",
                "title": row[1],
                "author": row[0],
                "series": row[2],
                "series_number": row[3],
                "genre": row[4],
                "status": row[5],
                "rating": float(row[6]),
                "avg_rating": 0.0,
                "date": pd.NaT,
                "year": None,
                "cover": "",
            }
            for i, row in enumerate(rows)
        ]
    )


def initialize_state():
    defaults = {
        "books": get_demo_books(),
        "theme": "Velvet Conservatory",
        "loaded_source": "demo",
        "active_author": None,
        "active_series": None,
        "search": "",
        "genre_filter": "All genres",
        "status_filter": "All statuses",
        "sort": "Author A–Z",
    }

    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value


def apply_filters(
    df,
    search,
    genre,
    status,
    sort,
):
    if df.empty:
        return df

    result = df.copy()

    search_norm = normalize_key(
        search
    )

    if search_norm:
        pattern = re.escape(
            search_norm
        )

        mask = (
            result["title"]
            .map(normalize_key)
            .str.contains(
                pattern,
                na=False,
            )
            | result["author"]
            .map(normalize_key)
            .str.contains(
                pattern,
                na=False,
            )
            | result["series"]
            .map(normalize_key)
            .str.contains(
                pattern,
                na=False,
            )
            | result["genre"]
            .map(normalize_key)
            .str.contains(
                pattern,
                na=False,
            )
        )

        result = result[mask]

    if genre != "All genres":
        result = result[
            result["genre"] == genre
        ]

    if status != "All statuses":
        result = result[
            result["status"] == status
        ]

    if sort == "Author A–Z":
        result = result.sort_values(
            [
                "author",
                "title",
            ],
            key=lambda s:
                s.str.lower()
                if s.dtype == "object"
                else s,
        )

    elif sort == "Author Z–A":
        result = result.sort_values(
            [
                "author",
                "title",
            ],
            ascending=[
                False,
                True,
            ],
            key=lambda s:
                s.str.lower()
                if s.dtype == "object"
                else s,
        )

    elif sort == "Title A–Z":
        result = result.sort_values(
            "title",
            key=lambda s:
                s.str.lower(),
        )

    elif sort == "Title Z–A":
        result = result.sort_values(
            "title",
            ascending=False,
            key=lambda s:
                s.str.lower(),
        )

    elif sort == "Highest rated":
        result = result.sort_values(
            [
                "rating",
                "title",
            ],
            ascending=[
                False,
                True,
            ],
        )

    elif sort == "Lowest rated":
        result = result.sort_values(
            [
                "rating",
                "title",
            ],
            ascending=[
                True,
                True,
            ],
        )

    elif sort == "Newest":
        result = result.sort_values(
            "year",
            ascending=False,
            na_position="last",
        )

    elif sort == "Oldest":
        result = result.sort_values(
            "year",
            ascending=True,
            na_position="last",
        )

    elif sort == "Read":
        result = result[
            result["status"] == "read"
        ]

    elif sort == "Currently Reading":
        result = result[
            result["status"]
            == "currently-reading"
        ]

    elif sort == "Want to Read":
        result = result[
            result["status"] == "to-read"
        ]

    return result


def tree_structure(df):
    structure = {}

    if df.empty:
        return structure

    for author, author_df in df.groupby(
        "author",
        sort=True,
    ):
        series_map = {}
        standalone = []

        for _, book in author_df.iterrows():
            series = safe_text(
                book["series"]
            )

            if series:
                series_map.setdefault(
                    series,
                    [],
                ).append(
                    book.to_dict()
                )
            else:
                standalone.append(
                    book.to_dict()
                )

        for name in series_map:
            series_map[name] = sorted(
                series_map[name],
                key=lambda book: (
                    book["series_number"]
                    is None,
                    (
                        book["series_number"]
                        if book["series_number"]
                        is not None
                        else 9999
                    ),
                    safe_text(
                        book["title"]
                    ).lower(),
                ),
            )

        structure[author] = {
            "series": dict(
                sorted(
                    series_map.items(),
                    key=lambda item:
                        item[0].lower(),
                )
            ),
            "standalone": sorted(
                standalone,
                key=lambda book:
                    safe_text(
                        book["title"]
                    ).lower(),
            ),
        }

    return dict(
        sorted(
            structure.items(),
            key=lambda item:
                item[0].lower(),
        )
    )


def render_global_css(theme):
    font_head = theme["font_head"]
    font_body = theme["font_body"]

    st.markdown(
        f"""
        <style>
        @import url(
            'https://fonts.googleapis.com/css2?
            family={quote_plus(font_head)}:wght@400;500;600;700&
            family={quote_plus(font_body)}:wght@400;500;600&
            display=swap'
        );

        :root {{
            --bt-bg: {theme["bg"]};
            --bt-surface: {theme["surface"]};
            --bt-surface-2: {theme["surface_2"]};
            --bt-ink: {theme["ink"]};
            --bt-muted: {theme["muted"]};
            --bt-accent: {theme["accent"]};
            --bt-accent2: {theme["accent_2"]};
            --bt-line: {theme["line"]};
            --bt-node: {theme["node"]};
            --bt-leaf: {theme["leaf"]};
            --bt-shadow: {theme["shadow"]};
        }}

        .stApp {{
            background:
                radial-gradient(
                    circle at 15% 5%,
                    color-mix(
                        in srgb,
                        var(--bt-accent) 12%,
                        transparent
                    ),
                    transparent 28%
                ),
                radial-gradient(
                    circle at 85% 20%,
                    color-mix(
                        in srgb,
                        var(--bt-accent2) 10%,
                        transparent
                    ),
                    transparent 26%
                ),
                var(--bt-bg);
            color: var(--bt-ink);
        }}

        .stApp,
        .stApp p,
        .stApp label,
        .stApp span,
        .stApp div {{
            font-family:
                '{font_body}',
                Georgia,
                serif;
        }}

        h1,
        h2,
        h3,
        .bt-title,
        .bt-author-name,
        .bt-series-name {{
            font-family:
                '{font_head}',
                Georgia,
                serif !important;
        }}

        [data-testid="stHeader"] {{
            background: transparent;
        }}

        [data-testid="stToolbar"] {{
            visibility: hidden;
        }}

        .block-container {{
            max-width: 1500px;
            padding-top: 1.2rem;
            padding-bottom: 3rem;
        }}

        .bt-hero {{
            position: relative;
            padding: 1.1rem 1rem .5rem;
            text-align: center;
        }}

        .bt-kicker {{
            color: var(--bt-accent);
            text-transform: uppercase;
            letter-spacing: .24em;
            font-size: .72rem;
            font-weight: 700;
            margin-bottom: .25rem;
        }}

        .bt-title {{
            margin: 0;
            color: var(--bt-ink);
            font-size: clamp(
                2.8rem,
                6vw,
                5.8rem
            );
            line-height: .95;
            font-weight: 600;
            text-shadow:
                0 7px 25px var(--bt-shadow);
        }}

        .bt-subtitle {{
            color: var(--bt-muted);
            font-size: 1rem;
            margin: .7rem auto 0;
            max-width: 650px;
        }}

        .bt-vine-loader {{
            height: 34px;
            position: relative;
            margin: .45rem auto .2rem;
            max-width: 680px;
            overflow: hidden;
        }}

        .bt-vine-loader::before {{
            content: "";
            position: absolute;
            left: 50%;
            top: 16px;
            width: 130%;
            height: 4px;
            border-top:
                2px solid var(--bt-accent2);
            border-radius: 50%;
            transform:
                translateX(-50%)
                rotate(-2deg);
            transform-origin: center;
            animation:
                vineGrow 2.3s ease-out both;
        }}

        .bt-vine-loader::after {{
            content: "❧  ❦  ❧";
            position: absolute;
            left: 50%;
            top: 1px;
            transform:
                translateX(-50%);
            color: var(--bt-accent2);
            letter-spacing: .9rem;
            font-size: 1.05rem;
            animation:
                leavesBloom 1.6s .6s ease-out both;
        }}

        @keyframes vineGrow {{
            from {{
                clip-path:
                    inset(0 100% 0 0);
            }}

            to {{
                clip-path:
                    inset(0 0 0 0);
            }}
        }}

        @keyframes leavesBloom {{
            from {{
                opacity: 0;
                transform:
                    translateX(-50%)
                    scale(.35);
            }}

            to {{
                opacity: 1;
                transform:
                    translateX(-50%)
                    scale(1);
            }}
        }}

        .bt-stat-row {{
            display: flex;
            justify-content: center;
            gap: clamp(
                1.5rem,
                6vw,
                5rem
            );
            margin: .4rem 0 1.2rem;
            flex-wrap: wrap;
        }}

        .bt-stat {{
            min-width: 100px;
            text-align: center;
        }}

        .bt-stat-number {{
            display: block;
            font-family:
                '{font_head}',
                Georgia,
                serif;
            font-size: 2rem;
            color: var(--bt-accent);
            line-height: 1;
        }}

        .bt-stat-label {{
            display: block;
            margin-top: .25rem;
            color: var(--bt-muted);
            font-size: .72rem;
            letter-spacing: .12em;
            text-transform: uppercase;
        }}

        .bt-controls {{
            background:
                color-mix(
                    in srgb,
                    var(--bt-surface) 82%,
                    transparent
                );
            border-top:
                1px solid
                color-mix(
                    in srgb,
                    var(--bt-line) 55%,
                    transparent
                );
            border-bottom:
                1px solid
                color-mix(
                    in srgb,
                    var(--bt-line) 55%,
                    transparent
                );
            padding: .8rem .4rem;
            margin: .6rem 0 1.2rem;
        }}

        div[data-baseweb="select"] > div,
        div[data-baseweb="input"] > div {{
            background:
                var(--bt-surface) !important;
            color:
                var(--bt-ink) !important;
            border-color:
                var(--bt-line) !important;
        }}

        div[data-baseweb="select"] *,
        div[data-baseweb="input"] * {{
            color:
                var(--bt-ink) !important;
        }}

        ul[role="listbox"] {{
            background:
                var(--bt-surface-2) !important;
            border-color:
                var(--bt-line) !important;
        }}

        li[role="option"] {{
            color:
                var(--bt-ink) !important;
            background:
                var(--bt-surface-2) !important;
        }}

        li[role="option"]:hover,
        li[role="option"][aria-selected="true"] {{
            background:
                var(--bt-node) !important;
            color:
                var(--bt-ink) !important;
        }}

        .stTextInput input {{
            color:
                var(--bt-ink) !important;
            caret-color:
                var(--bt-accent) !important;
        }}

        .stTextInput input::placeholder {{
            color:
                var(--bt-muted) !important;
            opacity: 1;
        }}

        .stButton > button {{
            border:
                1px solid var(--bt-line);
            background:
                transparent;
            color:
                var(--bt-ink);
            border-radius: 999px;
            font-family:
                '{font_body}',
                Georgia,
                serif;
            transition: .2s ease;
        }}

        .stButton > button:hover {{
            border-color:
                var(--bt-accent);
            color:
                var(--bt-accent);
            transform:
                translateY(-1px);
        }}

        .bt-tree {{
            position: relative;
            padding:
                1.2rem .4rem 2.4rem;
        }}

        .bt-tree-title {{
            text-align: center;
            font-family:
                '{font_head}',
                Georgia,
                serif;
            color:
                var(--bt-muted);
            letter-spacing: .16em;
            text-transform: uppercase;
            font-size: .68rem;
            margin-bottom: 1.1rem;
        }}

        .bt-author-branch {{
            position: relative;
            margin: 0 auto 1.2rem;
            max-width: 1250px;
            padding: .25rem 0 1rem;
        }}

        .bt-author-node {{
            position: relative;
            display: inline-flex;
            align-items: center;
            gap: .55rem;
            padding: .8rem 1.25rem;
            margin-left: 3%;
            color:
                var(--bt-ink);
            background:
                var(--bt-node);
            border:
                1px solid var(--bt-line);
            border-radius:
                60% 55% 60% 48% /
                48% 58% 45% 55%;
            box-shadow:
                0 12px 30px var(--bt-shadow);
            text-decoration: none !important;
        }}

        .bt-author-node::before {{
            content: "✦";
            color:
                var(--bt-accent);
            font-size: .8rem;
        }}

        .bt-author-node.active {{
            border-color:
                var(--bt-accent);
            box-shadow:
                0 0 0 1px var(--bt-accent),
                0 14px 34px var(--bt-shadow);
        }}

        .bt-author-name {{
            font-size: 1.2rem;
            font-weight: 600;
        }}

        .bt-children {{
            position: relative;
            margin:
                .3rem 0 0 10%;
            padding:
                1rem 0 0 3.2rem;
            border-left:
                2px solid var(--bt-line);
        }}

        .bt-children::before {{
            content: "";
            position: absolute;
            left: -2px;
            top: 0;
            width: 14px;
            height: 14px;
            border-radius: 50%;
            background:
                var(--bt-accent2);
            transform:
                translate(-50%, -50%);
            box-shadow:
                0 0 0 5px
                color-mix(
                    in srgb,
                    var(--bt-accent2) 14%,
                    transparent
                );
        }}

        .bt-series-row,
        .bt-standalone-row {{
            position: relative;
            margin: .8rem 0 1.25rem;
        }}

        .bt-series-row::before,
        .bt-standalone-row::before {{
            content: "";
            position: absolute;
            left: -3.2rem;
            top: 1.15rem;
            width: 3.2rem;
            border-top:
                2px solid var(--bt-line);
        }}

        .bt-series-node,
        .bt-standalone-node {{
            display: inline-flex;
            align-items: center;
            gap: .55rem;
            padding: .55rem .9rem;
            background:
                var(--bt-surface-2);
            border:
                1px solid var(--bt-line);
            color:
                var(--bt-ink);
            border-radius:
                48% 52% 45% 55% /
                55% 42% 58% 45%;
            text-decoration: none !important;
            box-shadow:
                0 7px 18px var(--bt-shadow);
        }}

        .bt-series-node.active {{
            border-color:
                var(--bt-accent);
        }}

        .bt-series-name {{
            font-size: 1rem;
            font-weight: 600;
        }}

        .bt-series-count {{
            color:
                var(--bt-muted);
            font-size: .72rem;
        }}

        .bt-books {{
            position: relative;
            margin:
                .45rem 0 0 1.25rem;
            padding:
                .15rem 0 .1rem 2rem;
            border-left:
                1px dashed var(--bt-line);
        }}

        .bt-book {{
            position: relative;
            display: flex;
            align-items: center;
            gap: .8rem;
            margin: .75rem 0;
            min-height: 68px;
        }}

        .bt-book::before {{
            content: "";
            position: absolute;
            left: -2rem;
            top: 50%;
            width: 2rem;
            border-top:
                1px dashed var(--bt-line);
        }}

        .bt-cover {{
            width: 48px;
            height: 68px;
            object-fit: cover;
            border-radius:
                4px 8px 8px 4px;
            border:
                1px solid
                color-mix(
                    in srgb,
                    var(--bt-accent) 55%,
                    transparent
                );
            box-shadow:
                5px 7px 14px var(--bt-shadow);
            background:
                var(--bt-surface);
            flex: 0 0 auto;
        }}

        .bt-cover-placeholder {{
            width: 48px;
            height: 68px;
            display: flex;
            align-items: center;
            justify-content: center;
            border-radius:
                4px 8px 8px 4px;
            border:
                1px solid var(--bt-line);
            background:
                linear-gradient(
                    145deg,
                    var(--bt-surface-2),
                    var(--bt-node)
                );
            color:
                var(--bt-accent);
            font-family:
                '{font_head}',
                Georgia,
                serif;
            font-size: 1.25rem;
            flex: 0 0 auto;
        }}

        .bt-book-info {{
            min-width: 0;
        }}

        .bt-book-title {{
            color:
                var(--bt-ink);
            font-family:
                '{font_head}',
                Georgia,
                serif;
            font-size: 1rem;
            font-weight: 600;
            line-height: 1.1;
        }}

        .bt-book-meta {{
            color:
                var(--bt-muted);
            font-size: .75rem;
            margin-top: .25rem;
        }}

        .bt-status {{
            display: inline-block;
            margin-left: .35rem;
            padding: .12rem .45rem;
            border:
                1px solid var(--bt-line);
            border-radius: 999px;
            font-size: .63rem;
            letter-spacing: .04em;
        }}

        .bt-stars {{
            color:
                var(--bt-accent);
            letter-spacing: .05em;
        }}

        .bt-empty {{
            text-align: center;
            padding: 4rem 1rem;
            color:
                var(--bt-muted);
            font-family:
                '{font_head}',
                Georgia,
                serif;
            font-size: 1.4rem;
        }}

        .bt-footer {{
            text-align: center;
            color:
                var(--bt-muted);
            font-size: .75rem;
            margin-top: 2.5rem;
            opacity: .8;
        }}

        @media (max-width: 700px) {{
            .bt-author-node {{
                margin-left: 1%;
            }}

            .bt-children {{
                margin-left: 4%;
                padding-left: 2.2rem;
            }}

            .bt-series-row::before,
            .bt-standalone-row::before {{
                left: -2.2rem;
                width: 2.2rem;
            }}

            .bt-book {{
                gap: .55rem;
            }}

            .bt-cover,
            .bt-cover-placeholder {{
                width: 42px;
                height: 60px;
            }}
        }}
        </style>
        """,
        unsafe_allow_html=True,
    )


def render_header(df):
    total = len(df)

    authors = (
        df["author"].nunique()
        if not df.empty
        else 0
    )

    series_count = (
        df.loc[
            df["series"]
            .astype(str)
            .str.strip()
            != "",
            "series",
        ].nunique()
        if not df.empty
        else 0
    )

    read_count = (
        int(
            (
                df["status"]
                == "read"
            ).sum()
        )
        if not df.empty
        else 0
    )

    st.markdown(
        f"""
        <div class="bt-hero">
            <div class="bt-kicker">
                A living library
            </div>

            <div class="bt-title">
                My Book Tree
            </div>

            <div class="bt-subtitle">
                Authors at the roots · series among the branches ·
                books at the leaves
            </div>

            <div class="bt-vine-loader"></div>
        </div>

        <div class="bt-stat-row">
            <div class="bt-stat">
                <span class="bt-stat-number">
                    {total:,}
                </span>
                <span class="bt-stat-label">
                    Books
                </span>
            </div>

            <div class="bt-stat">
                <span class="bt-stat-number">
                    {authors:,}
                </span>
                <span class="bt-stat-label">
                    Authors
                </span>
            </div>

            <div class="bt-stat">
                <span class="bt-stat-number">
                    {series_count:,}
                </span>
                <span class="bt-stat-label">
                    Series
                </span>
            </div>

            <div class="bt-stat">
                <span class="bt-stat-number">
                    {read_count:,}
                </span>
                <span class="bt-stat-label">
                    Read
                </span>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def read_tree_query(structure):
    author = safe_text(
        st.query_params.get(
            "author",
            "",
        )
    )

    series = safe_text(
        st.query_params.get(
            "series",
            "",
        )
    )

    if author not in structure:
        return None, None

    if series == "__standalone__":
        return author, "__standalone__"

    if (
        series
        and series not in structure[
            author
        ]["series"]
    ):
        return author, None

    return (
        author,
        series or None,
    )


def stars(rating):
    try:
        rating = float(rating)
    except (
        TypeError,
        ValueError,
    ):
        rating = 0.0

    if rating <= 0:
        return "—"

    full = max(
        0,
        min(
            5,
            int(
                round(rating)
            ),
        ),
    )

    return (
        "★" * full
        + "☆" * (5 - full)
    )


def cover_html(book):
    cover = safe_text(
        book.get("cover")
    )

    if cover:
        return (
            '<img class="bt-cover" '
            f'src="{html.escape(cover, quote=True)}" '
            f'alt="Cover of '
            f'{html.escape(safe_text(book.get("title")))}">'
        )

    return (
        '<div class="bt-cover-placeholder">'
        "✦"
        "</div>"
    )


def book_html(book):
    title = html.escape(
        safe_text(
            book.get("title"),
            "Untitled",
        )
    )

    genre = html.escape(
        safe_text(
            book.get("genre"),
            "Uncategorized",
        )
    )

    status_key = safe_text(
        book.get("status"),
        "to-read",
    )

    status = STATUS_LABELS.get(
        status_key,
        "Want to Read",
    )

    number = book.get(
        "series_number"
    )

    number_text = ""

    if (
        isinstance(
            number,
            (int, float),
        )
        and not pd.isna(number)
    ):
        number_text = (
            f" · Book {number:g}"
        )

    try:
        rating = float(
            book.get(
                "rating",
                0,
            )
        )
    except (
        TypeError,
        ValueError,
    ):
        rating = 0.0

    return f"""
        <div class="bt-book">
            {cover_html(book)}

            <div class="bt-book-info">
                <div class="bt-book-title">
                    {title}
                    {html.escape(number_text)}
                </div>

                <div class="bt-book-meta">
                    {genre}

                    <span class="bt-status">
                        {html.escape(status)}
                    </span>

                    <span class="bt-stars">
                        {stars(rating)}
                    </span>
                </div>
            </div>
        </div>
    """


def render_tree(df):
    structure = tree_structure(df)

    if not structure:
        st.markdown(
            '<div class="bt-empty">'
            "No books match those filters."
            "</div>",
            unsafe_allow_html=True,
        )
        return

    active_author, active_series = (
        read_tree_query(structure)
    )

    parts = [
        '<div class="bt-tree">',
        '<div class="bt-tree-title">',
        "The family tree of your library",
        "</div>",
    ]

    for author, data in structure.items():
        author_active = (
            author == active_author
        )

        if author_active:
            author_url = "?"
        else:
            author_url = (
                f"?author={quote_plus(author)}"
            )

        parts.append(
            '<div class="bt-author-branch">'
        )

        parts.append(
            f'<a class="bt-author-node '
            f'{"active" if author_active else ""}" '
            f'href="{author_url}">'
            f'<span class="bt-author-name">'
            f'{html.escape(author)}'
            "</span>"
            "</a>"
        )

        if author_active:
            parts.append(
                '<div class="bt-children">'
            )

            for (
                series_name,
                books,
            ) in data["series"].items():

                series_active = (
                    series_name
                    == active_series
                )

                if series_active:
                    series_url = (
                        f"?author="
                        f"{quote_plus(author)}"
                    )
                else:
                    series_url = (
                        f"?author="
                        f"{quote_plus(author)}"
                        f"&series="
                        f"{quote_plus(series_name)}"
                    )

                count = len(books)

                parts.append(
                    '<div class="bt-series-row">'
                )

                parts.append(
                    f'<a class="bt-series-node '
                    f'{"active" if series_active else ""}" '
                    f'href="{series_url}">'

                    f'<span class="bt-series-name">'
                    f'{html.escape(series_name)}'
                    "</span>"

                    f'<span class="bt-series-count">'
                    f'{count} '
                    f'{"book" if count == 1 else "books"}'
                    "</span>"

                    "</a>"
                )

                if series_active:
                    parts.append(
                        '<div class="bt-books">'
                    )

                    for book in books:
                        parts.append(
                            book_html(book)
                        )

                    parts.append(
                        "</div>"
                    )

                parts.append(
                    "</div>"
                )

            if data["standalone"]:
                standalone_active = (
                    active_series
                    == "__standalone__"
                )

                if standalone_active:
                    standalone_url = (
                        f"?author="
                        f"{quote_plus(author)}"
                    )
                else:
                    standalone_url = (
                        f"?author="
                        f"{quote_plus(author)}"
                        "&series=__standalone__"
                    )

                parts.append(
                    '<div class="bt-standalone-row">'
                )

                parts.append(
                    f'<a class="bt-standalone-node '
                    f'{"active" if standalone_active else ""}" '
                    f'href="{standalone_url}">'

                    '<span class="bt-series-name">'
                    "Standalone Books"
                    "</span>"

                    '<span class="bt-series-count">'
                    f'{len(data["standalone"])} '
                    f'{"book" if len(data["standalone"]) == 1 else "books"}'
                    "</span>"

                    "</a>"
                )

                if standalone_active:
                    parts.append(
                        '<div class="bt-books">'
                    )

                    for book in data[
                        "standalone"
                    ]:
                        parts.append(
                            book_html(book)
                        )

                    parts.append(
                        "</div>"
                    )

                parts.append(
                    "</div>"
                )

            parts.append(
                "</div>"
            )

        parts.append(
            "</div>"
        )

    parts.append(
        "</div>"
    )

    st.markdown(
        "".join(parts),
        unsafe_allow_html=True,
    )


def load_uploaded_csv(
    uploaded_file,
):
    raw = uploaded_file.getvalue()

    try:
        df = pd.read_csv(
            io.BytesIO(raw)
        )
    except UnicodeDecodeError:
        df = pd.read_csv(
            io.BytesIO(raw),
            encoding="latin-1",
        )

    return normalize_goodreads_dataframe(
        df
    )


def render_sidebar():
    with st.sidebar:
        st.markdown(
            "## My Book Tree"
        )

        st.caption(
            "Build the tree from your "
            "Goodreads library."
        )

        uploaded = st.file_uploader(
            "Import Goodreads CSV",
            type=["csv"],
            help=(
                "Export your Goodreads library "
                "as a CSV and upload it here."
            ),
        )

        if uploaded is not None:
            file_signature = hashlib.sha1(
                uploaded.getvalue()
            ).hexdigest()

            if (
                st.session_state.get(
                    "uploaded_signature"
                )
                != file_signature
            ):
                books = load_uploaded_csv(
                    uploaded
                )

                if not books.empty:
                    with st.spinner(
                        "Bringing in missing covers, "
                        "genres, and series information…"
                    ):
                        books = enrich_missing_books(
                            books,
                            limit=60,
                        )

                    st.session_state.books = (
                        books
                    )

                    st.session_state.loaded_source = (
                        uploaded.name
                    )

                    st.session_state.uploaded_signature = (
                        file_signature
                    )

                    st.session_state.active_author = (
                        None
                    )

                    st.session_state.active_series = (
                        None
                    )

                    st.query_params.clear()

                    st.success(
                        f"Loaded {len(books):,} books."
                    )

                else:
                    st.error(
                        "That CSV did not contain "
                        "recognizable book rows."
                    )

        st.markdown("---")

        theme_names = list(
            THEMES.keys()
        )

        current_theme = (
            st.session_state.get(
                "theme",
                theme_names[0],
            )
        )

        if current_theme not in THEMES:
            current_theme = (
                theme_names[0]
            )

            st.session_state.theme = (
                current_theme
            )

        selected_theme = st.selectbox(
            "Theme",
            theme_names,
            index=theme_names.index(
                current_theme
            ),
            key="theme_selector",
        )

        if (
            selected_theme
            != st.session_state.theme
        ):
            st.session_state.theme = (
                selected_theme
            )

            st.rerun()

        if st.button(
            "Enrich missing covers & genres",
            use_container_width=True,
        ):
            with st.spinner(
                "Looking up missing book information…"
            ):
                st.session_state.books = (
                    enrich_missing_books(
                        st.session_state.books
                    )
                )

            st.success(
                "Finished checking missing information."
            )

        if st.button(
            "Return to full tree",
            use_container_width=True,
        ):
            st.query_params.clear()

            st.session_state.active_author = (
                None
            )

            st.session_state.active_series = (
                None
            )

            st.rerun()

        st.markdown("---")

        source = st.session_state.get(
            "loaded_source",
            "demo",
        )

        st.caption(
            f"Library source: {source}"
        )

        st.caption(
            f"App version {APP_VERSION}"
        )


def render_controls(df):
    if df.empty:
        return df

    genres = sorted(
        [
            genre
            for genre in df[
                "genre"
            ].dropna().unique()
            if safe_text(genre)
        ],
        key=str.lower,
    )

    genre_options = [
        "All genres"
    ] + genres

    st.markdown(
        '<div class="bt-controls">',
        unsafe_allow_html=True,
    )

    c1, c2, c3, c4 = st.columns(
        [
            2.2,
            1.2,
            1.2,
            1.5,
        ]
    )

    with c1:
        search = st.text_input(
            "Search",
            value=st.session_state.get(
                "search",
                "",
            ),
            placeholder=(
                "Search title, author, "
                "series, or genre…"
            ),
            label_visibility="collapsed",
            key="search_box",
        )

        st.session_state.search = (
            search
        )

    with c2:
        current_genre = (
            st.session_state.get(
                "genre_filter",
                "All genres",
            )
        )

        genre = st.selectbox(
            "Genre",
            genre_options,
            index=(
                genre_options.index(
                    current_genre
                )
                if current_genre
                in genre_options
                else 0
            ),
            label_visibility="collapsed",
            key="genre_box",
        )

        st.session_state.genre_filter = (
            genre
        )

    with c3:
        statuses = [
            "All statuses",
            "Read",
            "Currently Reading",
            "Want to Read",
        ]

        current_status = (
            st.session_state.get(
                "status_filter",
                "All statuses",
            )
        )

        status = st.selectbox(
            "Status",
            statuses,
            index=(
                statuses.index(
                    current_status
                )
                if current_status
                in statuses
                else 0
            ),
            label_visibility="collapsed",
            key="status_box",
        )

        st.session_state.status_filter = (
            status
        )

    with c4:
        current_sort = (
            st.session_state.get(
                "sort",
                "Author A–Z",
            )
        )

        sort = st.selectbox(
            "Sort",
            SORT_OPTIONS,
            index=(
                SORT_OPTIONS.index(
                    current_sort
                )
                if current_sort
                in SORT_OPTIONS
                else 0
            ),
            label_visibility="collapsed",
            key="sort_box",
        )

        st.session_state.sort = (
            sort
        )

    st.markdown(
        "</div>",
        unsafe_allow_html=True,
    )

    return apply_filters(
        df,
        search,
        genre,
        status,
        sort,
    )


def main():
    initialize_state()

    theme_name = st.session_state.get(
        "theme",
        "Velvet Conservatory",
    )

    if theme_name not in THEMES:
        theme_name = (
            "Velvet Conservatory"
        )

        st.session_state.theme = (
            theme_name
        )

    theme = THEMES[
        theme_name
    ]

    render_global_css(
        theme
    )

    render_sidebar()

    df = st.session_state.get(
        "books",
        pd.DataFrame(),
    )

    if not isinstance(
        df,
        pd.DataFrame,
    ):
        df = get_demo_books()
        st.session_state.books = df

    filtered = render_controls(
        df
    )

    render_header(
        filtered
    )

    render_tree(
        filtered
    )

    st.markdown(
        '<div class="bt-footer">'
        "My Book Tree · an ancestry-style "
        "library for the books you keep"
        "</div>",
        unsafe_allow_html=True,
    )


if __name__ == "__main__":
    main()
