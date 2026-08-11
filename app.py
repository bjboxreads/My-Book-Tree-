import streamlit as st
import pandas as pd
import requests
import re
import html
import json
from collections import defaultdict

# ============================================================
# PAGE
# ============================================================

st.set_page_config(
    page_title="My Book Tree",
    page_icon="📚",
    layout="wide"
)

# ============================================================
# COLOR THEMES
# ============================================================

THEMES = {
    "Classic": {
        "background": "#F4F1EA",
        "panel": "#FFFFFF",
        "node": "#FFFFFF",
        "node_border": "#41695F",
        "text": "#263832",
        "secondary": "#68746E",
        "line": "#41695F",
        "accent": "#C58A3A",
        "accent_text": "#FFFFFF",
        "input_bg": "#FFFFFF",
    },

    "Botanical": {
        "background": "#E7F0E2",
        "panel": "#F9FCF6",
        "node": "#FFFFFF",
        "node_border": "#39734C",
        "text": "#173B27",
        "secondary": "#567361",
        "line": "#39734C",
        "accent": "#D18A28",
        "accent_text": "#FFFFFF",
        "input_bg": "#FFFFFF",
    },

    "Blue & Gold": {
        "background": "#E6EEF8",
        "panel": "#FFFFFF",
        "node": "#FFFFFF",
        "node_border": "#24558A",
        "text": "#142E4A",
        "secondary": "#58708A",
        "line": "#3E6F9F",
        "accent": "#C58B25",
        "accent_text": "#FFFFFF",
        "input_bg": "#FFFFFF",
    },

    "Berry": {
        "background": "#F7E6EE",
        "panel": "#FFF9FC",
        "node": "#FFFFFF",
        "node_border": "#A52D62",
        "text": "#40152B",
        "secondary": "#795168",
        "line": "#A52D62",
        "accent": "#E08A39",
        "accent_text": "#FFFFFF",
        "input_bg": "#FFFFFF",
    },

    "Jewel": {
        "background": "#DDF1EE",
        "panel": "#F9FFFE",
        "node": "#FFFFFF",
        "node_border": "#087B73",
        "text": "#103F3B",
        "secondary": "#52716D",
        "line": "#087B73",
        "accent": "#D49A2A",
        "accent_text": "#FFFFFF",
        "input_bg": "#FFFFFF",
    },

    "Night Garden": {
        "background": "#111C2B",
        "panel": "#1B2A3D",
        "node": "#24364B",
        "node_border": "#70B88A",
        "text": "#F5F3EA",
        "secondary": "#B7C6C1",
        "line": "#70B88A",
        "accent": "#E1AA42",
        "accent_text": "#182017",
        "input_bg": "#24364B",
    },

    "Warm Library": {
        "background": "#F3E5D0",
        "panel": "#FFF8EC",
        "node": "#FFFDF8",
        "node_border": "#A64A2F",
        "text": "#3A2119",
        "secondary": "#76594B",
        "line": "#A64A2F",
        "accent": "#D28B27",
        "accent_text": "#FFFFFF",
        "input_bg": "#FFFFFF",
    },
}

# ============================================================
# SESSION STATE
# ============================================================

if "theme" not in st.session_state:
    st.session_state.theme = "Classic"

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
            "Date Read"
        ]
    )

theme = THEMES[st.session_state.theme]

# ============================================================
# GLOBAL CSS
# ============================================================

st.markdown(
    f"""
<style>

@import url(
'https://fonts.googleapis.com/css2?family=Cormorant+Garamond:wght@500;600;700'
'&family=DM+Sans:wght@400;500;600;700'
);

html, body, [class*="css"] {{
    font-family: "DM Sans", sans-serif;
}}

.stApp {{
    background: {theme["background"]};
    color: {theme["text"]};
}}

.block-container {{
    max-width: 1500px;
    padding-top: 2rem;
}}

h1, h2, h3 {{
    font-family: "Cormorant Garamond", Georgia, serif !important;
    color: {theme["text"]} !important;
}}

.hero {{
    text-align: center;
    padding: 25px 0 15px 0;
}}

.hero h1 {{
    font-size: 58px;
    margin: 0;
    font-weight: 700;
}}

.hero p {{
    color: {theme["secondary"]};
    font-size: 18px;
    margin-top: 5px;
}}

.stat {{
    background: {theme["panel"]};
    border-radius: 16px;
    padding: 16px;
    text-align: center;
    border: 1px solid {theme["node_border"]}55;
}}

.stat-number {{
    font-family: "Cormorant Garamond", Georgia, serif;
    font-size: 32px;
    font-weight: 700;
    color: {theme["text"]};
}}

.stat-label {{
    color: {theme["secondary"]};
    font-size: 12px;
    text-transform: uppercase;
    letter-spacing: .08em;
}}

.tree-wrapper {{
    background: {theme["panel"]};
    border-radius: 20px;
    padding: 30px;
    margin-top: 20px;
    overflow-x: auto;
    border: 1px solid {theme["node_border"]}55;
}}

input, textarea {{
    color: {theme["text"]} !important;
}}

</style>
""",
    unsafe_allow_html=True
)

# ============================================================
# COVER LOOKUP
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

            response = requests.get(
                url,
                timeout=8
            )

            if (
                response.status_code == 200
                and len(response.content) > 1000
            ):
                return url

        except:
            pass

    try:

        response = requests.get(
            "https://openlibrary.org/search.json",
            params={
                "title": title,
                "author": author,
                "limit": 1
            },
            timeout=10
        )

        if response.status_code == 200:

            docs = response.json().get(
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

    except:
        pass

    try:

        response = requests.get(
            "https://www.googleapis.com/books/v1/volumes",
            params={
                "q": f"{title} {author}",
                "maxResults": 1
            },
            timeout=10
        )

        if response.status_code == 200:

            items = response.json().get(
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

    except:
        pass

    return ""

# ============================================================
# SERIES DETECTION
# ============================================================

def detect_series(title):

    patterns = [

        r"\(([^()]*)#\s*\d+(?:\.\d+)?[^()]*\)",

        r"\[([^\[\]]*)#\s*\d+(?:\.\d+)?[^\[\]]*\]",

        r"\(([^()]*)\bBook\s+\d+(?:\.\d+)?[^()]*\)",

        r"\[([^\[\]]*)\bBook\s+\d+(?:\.\d+)?[^\[\]]*\]"
    ]

    for pattern in patterns:

        match = re.search(
            pattern,
            str(title),
            re.IGNORECASE
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
        r"\bVol(?:ume)?\.?\s+(\d+(?:\.\d+)?)"
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
            except:
                pass

    return None

# ============================================================
# BUILD SVG TREE
# ============================================================

def build_tree(data):

    if data.empty:

        return """
        <div style="
            padding:100px;
            text-align:center;
            font-family:DM Sans,sans-serif;
        ">
            <h2>Your tree is waiting for its books.</h2>
            <p>Import your library or add a book.</p>
        </div>
        """

    # --------------------------------------------------------
    # GROUP DATA
    # --------------------------------------------------------

    authors = {}

    for author in sorted(
        data["Author"].fillna("Unknown Author").unique(),
        key=lambda x: str(x).lower()
    ):

        author_data = data[
            data["Author"].fillna("Unknown Author")
            == author
        ]

        series_dict = {}

        for series in sorted(
            author_data["Series"]
            .fillna("Standalone")
            .unique(),
            key=lambda x: str(x).lower()
        ):

            books = author_data[
                author_data["Series"]
                .fillna("Standalone")
                == series
            ].copy()

            books = books.sort_values(
                by=[
                    "Series Number",
                    "Title"
                ],
                na_position="last"
            )

            series_dict[series] = books

        authors[author] = series_dict

    # --------------------------------------------------------
    # SVG DIMENSIONS
    # --------------------------------------------------------

    author_width = 260
    author_gap = 110
    series_width = 230
    series_gap = 55
    book_width = 180
    book_height = 240

    author_count = len(authors)

    total_width = max(
        1200,
        author_count *
        (author_width + author_gap)
    )

    total_height = 1050

    svg = []

    svg.append(
        f"""
        <svg
            width="{total_width}"
            height="{total_height}"
            viewBox="0 0 {total_width} {total_height}"
            xmlns="http://www.w3.org/2000/svg"
            style="
                background:{theme["panel"]};
                border-radius:18px;
                min-width:1100px;
            "
        >
        """
    )

    # --------------------------------------------------------
    # ROOT
    # --------------------------------------------------------

    root_x = total_width / 2
    root_y = 80

    svg.append(
        f"""
        <g>

            <rect
                x="{root_x - 150}"
                y="{root_y - 35}"
                width="300"
                height="70"
                rx="18"
                fill="{theme["accent"]}"
            />

            <text
                x="{root_x}"
                y="{root_y - 2}"
                text-anchor="middle"
                font-family="Cormorant Garamond, Georgia, serif"
                font-size="30"
                font-weight="700"
                fill="{theme["accent_text"]}"
            >
                My Book Tree
            </text>

            <text
                x="{root_x}"
                y="{root_y + 20}"
                text-anchor="middle"
                font-family="DM Sans, sans-serif"
                font-size="12"
                fill="{theme["accent_text"]}"
                opacity=".9"
            >
                {len(data)} books
            </text>

        </g>
        """
    )

    # --------------------------------------------------------
    # AUTHOR POSITIONS
    # --------------------------------------------------------

    positions = []

    if author_count == 1:

        positions = [
            root_x
        ]

    else:

        usable_width = total_width - 200

        step = usable_width / (
            author_count - 1
        )

        positions = [
            100 + i * step
            for i in range(author_count)
        ]

    author_y = 220

    # Root → authors

    for x in positions:

        svg.append(
            f"""
            <path
                d="
                    M {root_x} {root_y + 35}
                    C {root_x} 140,
                      {x} 140,
                      {x} {author_y - 45}
                "
                fill="none"
                stroke="{theme["line"]}"
                stroke-width="4"
            />
            """
        )

    # --------------------------------------------------------
    # AUTHORS
    # --------------------------------------------------------

    for author_index, (author, series_dict) in enumerate(
        authors.items()
    ):

        author_x = positions[
            author_index
        ]

        author_book_count = sum(
            len(books)
            for books in series_dict.values()
        )

        # AUTHOR NODE

        svg.append(
            f"""
            <g>

                <rect
                    x="{author_x - 125}"
                    y="{author_y - 45}"
                    width="250"
                    height="90"
                    rx="18"
                    fill="{theme["node"]}"
                    stroke="{theme["node_border"]}"
                    stroke-width="3"
                />

                <text
                    x="{author_x}"
                    y="{author_y - 7}"
                    text-anchor="middle"
                    font-family="Cormorant Garamond, Georgia, serif"
                    font-size="25"
                    font-weight="700"
                    fill="{theme["text"]}"
                >
                    {html.escape(str(author))[:28]}
                </text>

                <text
                    x="{author_x}"
                    y="{author_y + 20}"
                    text-anchor="middle"
                    font-family="DM Sans, sans-serif"
                    font-size="12"
                    fill="{theme["secondary"]}"
                >
                    {author_book_count} books
                </text>

            </g>
            """
        )

        # ----------------------------------------------------
        # SERIES POSITIONS
        # ----------------------------------------------------

        series_items = list(
            series_dict.items()
        )

        if not series_items:
            continue

        series_y = 410

        series_total = len(series_items)

        spacing = max(
            series_width + series_gap,
            250
        )

        start_x = (
            author_x
            -
            ((series_total - 1) * spacing / 2)
        )

        # Author → series trunk

        if series_total > 1:

            left = start_x
            right = (
                start_x
                +
                (series_total - 1) * spacing
            )

            svg.append(
                f"""
                <path
                    d="
                        M {author_x} {author_y + 45}
                        C {author_x} 320,
                          {author_x} 350,
                          {author_x} 365
                    "
                    fill="none"
                    stroke="{theme["line"]}"
                    stroke-width="4"
                />

                <path
                    d="
                        M {left} 365
                        L {right} 365
                    "
                    fill="none"
                    stroke="{theme["line"]}"
                    stroke-width="4"
                />
                """
            )

        else:

            svg.append(
                f"""
                <path
                    d="
                        M {author_x} {author_y + 45}
                        L {author_x} {series_y - 48}
                    "
                    fill="none"
                    stroke="{theme["line"]}"
                    stroke-width="4"
                />
                """
            )

        # ----------------------------------------------------
        # SERIES
        # ----------------------------------------------------

        for series_index, (
            series,
            books
        ) in enumerate(series_items):

            series_x = (
                start_x
                +
                series_index * spacing
            )

            if series_total > 1:

                svg.append(
                    f"""
                    <path
                        d="
                            M {series_x} 365
                            L {series_x} {series_y - 48}
                        "
                        fill="none"
                        stroke="{theme["line"]}"
                        stroke-width="4"
                    />
                    """
                )

            # SERIES NODE

            series_read = len(
                books[
                    books["Status"] == "Read"
                ]
            )

            svg.append(
                f"""
                <g>

                    <rect
                        x="{series_x - 105}"
                        y="{series_y - 45}"
                        width="210"
                        height="90"
                        rx="15"
                        fill="{theme["node"]}"
                        stroke="{theme["accent"]}"
                        stroke-width="3"
                    />

                    <text
                        x="{series_x}"
                        y="{series_y - 7}"
                        text-anchor="middle"
                        font-family="Cormorant Garamond, Georgia, serif"
                        font-size="21"
                        font-weight="700"
                        fill="{theme["text"]}"
                    >
                        {html.escape(str(series))[:25]}
                    </text>

                    <text
                        x="{series_x}"
                        y="{series_y + 19}"
                        text-anchor="middle"
                        font-family="DM Sans, sans-serif"
                        font-size="12"
                        fill="{theme["secondary"]}"
                    >
                        {series_read}/{len(books)} read
                    </text>

                </g>
                """
            )

            # ------------------------------------------------
            # BOOKS
            # ------------------------------------------------

            book_y = 700

            book_count = len(books)

            book_spacing = 200

            books_start = (
                series_x
                -
                ((book_count - 1)
                 * book_spacing / 2)
            )

            # Series → book line

            if book_count > 1:

                book_left = books_start

                book_right = (
                    books_start
                    +
                    (book_count - 1)
                    * book_spacing
                )

                svg.append(
                    f"""
                    <path
                        d="
                            M {series_x} {series_y + 45}
                            L {series_x} 625
                            L {book_left} 625
                            L {book_right} 625
                        "
                        fill="none"
                        stroke="{theme["line"]}"
                        stroke-width="3"
                    />
                    """
                )

            else:

                svg.append(
                    f"""
                    <path
                        d="
                            M {series_x} {series_y + 45}
                            L {series_x} 625
                            L {books_start} 625
                            L {books_start} {book_y - 125}
                        "
                        fill="none"
                        stroke="{theme["line"]}"
                        stroke-width="3"
                    />
                    """
                )

            for book_index, (_, book) in enumerate(
                books.iterrows()
            ):

                book_x = (
                    books_start
                    +
                    book_index * book_spacing
                )

                if book_count > 1:

                    svg.append(
                        f"""
                        <path
                            d="
                                M {book_x} 625
                                L {book_x} {book_y - 125}
                            "
                            fill="none"
                            stroke="{theme["line"]}"
                            stroke-width="3"
                        />
                        """
                    )

                title = str(
                    book.get(
                        "Title",
                        ""
                    )
                )

                title = html.escape(title)

                cover = str(
                    book.get(
                        "Cover",
                        ""
                    )
                    or ""
                )

                # ------------------------------------------------
                # BOOK NODE
                # ------------------------------------------------

                if cover:

                    svg.append(
                        f"""
                        <g>

                            <image
                                href="{html.escape(cover)}"
                                x="{book_x - 65}"
                                y="{book_y - 105}"
                                width="130"
                                height="190"
                                preserveAspectRatio="xMidYMid slice"
                                style="
                                    border-radius:6px;
                                "
                            />

                            <rect
                                x="{book_x - 70}"
                                y="{book_y - 110}"
                                width="140"
                                height="200"
                                rx="8"
                                fill="none"
                                stroke="{theme["node_border"]}"
                                stroke-width="3"
                            />

                            <text
                                x="{book_x}"
                                y="{book_y + 115}"
                                text-anchor="middle"
                                font-family="Cormorant Garamond, Georgia, serif"
                                font-size="16"
                                font-weight="700"
                                fill="{theme["text"]}"
                            >
                                {title[:22]}
                            </text>

                        </g>
                        """
                    )

                else:

                    svg.append(
                        f"""
                        <g>

                            <rect
                                x="{book_x - 70}"
                                y="{book_y - 110}"
                                width="140"
                                height="200"
                                rx="8"
                                fill="{theme["node"]}"
                                stroke="{theme["node_border"]}"
                                stroke-width="3"
                            />

                            <text
                                x="{book_x}"
                                y="{book_y - 20}"
                                text-anchor="middle"
                                font-family="Cormorant Garamond, Georgia, serif"
                                font-size="17"
                                font-weight="700"
                                fill="{theme["text"]}"
                            >
                                {title[:28]}
                            </text>

                        </g>
                        """
                    )

    svg.append("</svg>")

    return "".join(svg)

# ============================================================
# IMPORT CSV
# ============================================================

def import_books(uploaded):

    try:

        df = pd.read_csv(
            uploaded,
            low_memory=False
        )

    except:

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
                return columns[
                    name.lower()
                ]

        for name in names:

            for key, original in columns.items():

                if name.lower() in key:
                    return original

        return None

    title_col = find_column(
        [
            "Title",
            "Book Title"
        ]
    )

    author_col = find_column(
        [
            "Author",
            "Authors"
        ]
    )

    if not title_col:

        st.error(
            "I couldn't find a Title column."
        )

        return

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

        isbn_col = find_column(
            [
                "ISBN13",
                "ISBN"
            ]
        )

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

        rating_col = find_column(
            [
                "My Rating",
                "Rating"
            ]
        )

        rating = None

        if rating_col:

            try:

                rating = float(
                    row.get(
                        rating_col
                    )
                )

            except:

                rating = None

        shelf_col = find_column(
            [
                "Exclusive Shelf",
                "Shelf",
                "Status"
            ]
        )

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

        series = detect_series(
            title
        )

        books.append(
            {
                "Title": title,
                "Author": author,
                "Series": series,
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
                "Date Read": ""
            }
        )

    new_library = pd.DataFrame(
        books
    )

    if new_library.empty:

        st.error(
            "No books were found."
        )

        return

    progress = st.progress(0)

    for i in range(
        len(new_library)
    ):

        new_library.loc[
            i,
            "Cover"
        ] = get_cover(
            new_library.loc[
                i,
                "Title"
            ],
            new_library.loc[
                i,
                "Author"
            ],
            new_library.loc[
                i,
                "ISBN"
            ]
        )

        progress.progress(
            int(
                (i + 1)
                /
                len(new_library)
                * 100
            )
        )

    progress.empty()

    st.session_state.library = (
        new_library
    )

# ============================================================
# HEADER
# ============================================================

st.markdown(
    """
    <div class="hero">
        <h1>My Book Tree</h1>
        <p>
            Your books, connected like a family tree.
        </p>
    </div>
    """,
    unsafe_allow_html=True
)

# ============================================================
# THEME
# ============================================================

theme_choice = st.selectbox(
    "Choose your color scheme",
    list(THEMES.keys()),
    index=list(THEMES.keys()).index(
        st.session_state.theme
    )
)

if (
    theme_choice
    != st.session_state.theme
):

    st.session_state.theme = (
        theme_choice
    )

    st.rerun()

# ============================================================
# LIBRARY
# ============================================================

library = st.session_state.library

# ============================================================
# STATS
# ============================================================

total = len(library)

authors = (
    library["Author"].nunique()
    if total
    else 0
)

series = (
    library[
        library["Series"]
        != "Standalone"
    ]["Series"].nunique()
    if total
    else 0
)

read = (
    len(
        library[
            library["Status"]
            == "Read"
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

c1, c2, c3, c4, c5 = st.columns(5)

stats = [
    (total, "Books"),
    (authors, "Authors"),
    (series, "Series"),
    (read, "Read"),
    (favorites, "Favorites")
]

for column, (
    number,
    label
) in zip(
    [c1, c2, c3, c4, c5],
    stats
):

    with column:

        st.markdown(
            f"""
            <div class="stat">
                <div class="stat-number">
                    {number:,}
                </div>
                <div class="stat-label">
                    {label}
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )

# ============================================================
# TABS
# ============================================================

tree_tab, books_tab, add_tab, import_tab = st.tabs(
    [
        "🌳 Book Tree",
        "📚 Books",
        "➕ Add Book",
        "📥 Import Library"
    ]
)

# ============================================================
# TREE TAB
# ============================================================

with tree_tab:

    st.markdown(
        "## Your Library Tree"
    )

    if library.empty:

        st.info(
            "Import your library or add a book "
            "to create your tree."
        )

    else:

        c1, c2, c3 = st.columns(3)

        with c1:

            search = st.text_input(
                "Search the tree",
                placeholder=(
                    "Book, author, or series..."
                )
            )

        with c2:

            status_filter = st.selectbox(
                "Reading status",
                [
                    "All",
                    "Read",
                    "Currently Reading",
                    "Want to Read"
                ]
            )

        with c3:

            author_filter = st.selectbox(
                "Author",
                [
                    "All"
                ]
                +
                sorted(
                    library[
                        "Author"
                    ]
                    .dropna()
                    .unique()
                    .tolist(),
                    key=lambda x:
                    str(x).lower()
                )
            )

        filtered = library.copy()

        if search:

            q = search.lower()

            filtered = filtered[
                filtered[
                    "Title"
                ]
                .fillna("")
                .str.lower()
                .str.contains(
                    q,
                    na=False
                )
                |
                filtered[
                    "Author"
                ]
                .fillna("")
                .str.lower()
                .str.contains(
                    q,
                    na=False
                )
                |
                filtered[
                    "Series"
                ]
                .fillna("")
                .str.lower()
                .str.contains(
                    q,
                    na=False
                )
            ]

        if status_filter != "All":

            filtered = filtered[
                filtered["Status"]
                == status_filter
            ]

        if author_filter != "All":

            filtered = filtered[
                filtered["Author"]
                == author_filter
            ]

        st.markdown(
            '<div class="tree-wrapper">',
            unsafe_allow_html=True
        )

        tree_html = build_tree(
            filtered
        )

        st.components.v1.html(
            tree_html,
            height=1100,
            scrolling=True
        )

        st.markdown(
            "</div>",
            unsafe_allow_html=True
        )

# ============================================================
# BOOKS TAB
# ============================================================

with books_tab:

    st.markdown(
        "## Your Books"
    )

    if library.empty:

        st.info(
            "No books yet."
        )

    else:

        display_filter = st.radio(
            "Show",
            [
                "All",
                "Favorites",
                "Read",
                "Currently Reading",
                "Want to Read"
            ],
            horizontal=True
        )

        books = library.copy()

        if display_filter == "Favorites":

            books = books[
                books["Favorite"]
                == True
            ]

        elif display_filter != "All":

            books = books[
                books["Status"]
                == display_filter
            ]

        cols = st.columns(6)

        for i, (_, book) in enumerate(
            books.iterrows()
        ):

            with cols[
                i % 6
            ]:

                cover = book.get(
                    "Cover",
                    ""
                )

                if cover:

                    st.image(
                        cover,
                        use_container_width=True
                    )

                else:

                    st.markdown(
                        f"""
                        <div style="
                            height:220px;
                            display:flex;
                            align-items:center;
                            justify-content:center;
                            text-align:center;
                            padding:20px;
                            background:{theme["node"]};
                            border:2px solid
                                {theme["node_border"]};
                            border-radius:10px;
                            font-family:
                                'Cormorant Garamond',
                                Georgia,
                                serif;
                            font-size:20px;
                        ">
                            {html.escape(
                                str(book["Title"])
                            )}
                        </div>
                        """,
                        unsafe_allow_html=True
                    )

                st.markdown(
                    f"""
                    **{html.escape(
                        str(book["Title"])
                    )}**

                    <span style="
                        color:{theme["secondary"]};
                        font-size:13px;
                    ">
                    {html.escape(
                        str(book["Author"])
                    )}
                    </span>
                    """,
                    unsafe_allow_html=True
                )

# ============================================================
# ADD BOOK
# ============================================================

with add_tab:

    st.markdown(
        "## Add a Book"
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
            )
        )

        series_number = st.number_input(
            "Series number",
            min_value=0.0,
            value=0.0,
            step=0.5
        )

        isbn = st.text_input(
            "ISBN"
        )

        status = st.selectbox(
            "Reading status",
            [
                "Want to Read",
                "Currently Reading",
                "Read"
            ]
        )

        rating = st.slider(
            "Your rating",
            0,
            5,
            0
        )

        favorite = st.checkbox(
            "❤️ Favorite"
        )

        submitted = st.form_submit_button(
            "Add Book"
        )

        if submitted:

            if not title or not author:

                st.error(
                    "Title and author are required."
                )

            else:

                if not series:
                    series = "Standalone"

                cover = get_cover(
                    title,
                    author,
                    isbn
                )

                new_book = pd.DataFrame(
                    [{
                        "Title": title,
                        "Author": author,
                        "Series": series,
                        "Series Number":
                            series_number
                            if series_number
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
                        "Date Read": ""
                    }]
                )

                st.session_state.library = (
                    pd.concat(
                        [
                            st.session_state.library,
                            new_book
                        ],
                        ignore_index=True
                    )
                )

                st.success(
                    f'"{title}" added!'
                )

                st.rerun()

# ============================================================
# IMPORT TAB
# ============================================================

with import_tab:

    st.markdown(
        "## Import Your Library"
    )

    st.write(
        "Upload a CSV from Goodreads, StoryGraph, "
        "or another book-tracking service."
    )

    uploaded = st.file_uploader(
        "Choose CSV",
        type=["csv"]
    )

    if uploaded:

        if st.button(
            "Import Books"
        ):

            import_books(
                uploaded
            )

            st.success(
                "Your library has been imported."
            )

            st.rerun()

# ============================================================
# FOOTER
# ============================================================

st.markdown(
    f"""
    <div style="
        margin-top:60px;
        padding:20px;
        text-align:center;
        color:{theme["secondary"]};
        font-size:13px;
    ">
        My Book Tree · Built around your reading life.
    </div>
    """,
    unsafe_allow_html=True
)
