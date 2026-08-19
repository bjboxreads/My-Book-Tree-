"""
StorySpire — data layer, pandas-free.

Same logic as the Streamlit version (CSV persistence, ISBN cleaning,
series detection, Google Books / OpenLibrary metadata fetching,
Goodreads/StoryGraph import parsing for CSV/XLSX/TXT/PDF) but
rewritten without pandas -- pandas has C extensions that don't
compile for Android in the Flet/Flutter build.

The library is a plain list of dicts (one dict per book) instead of
a DataFrame. Each book dict has exactly LIBRARY_COLUMNS as keys.
"""

import csv
import os
import re
import shutil
import time
import requests
from concurrent.futures import ThreadPoolExecutor, as_completed

LIBRARY_FILE = os.path.join(
    os.path.dirname(os.path.abspath(__file__)),
    "storyspire_library.csv",
)
LIBRARY_BACKUP_FILE = LIBRARY_FILE + ".bak"

LIBRARY_COLUMNS = [
    "Title", "Author", "Series", "Series Number", "Genre", "ISBN",
    "My Rating", "Status", "Favorite", "Cover", "Description", "Tags",
    "Publisher", "Pages", "Publication Date", "Date Read",
]

GENERIC_GENRE_TERMS = {"fiction", "nonfiction", "non-fiction", "general"}

# Identify ourselves to OpenLibrary / Google Books. OpenLibrary in
# particular throttles/blocks requests with no User-Agent much more
# aggressively than ones that identify the app.
HTTP_HEADERS = {
    "User-Agent": "StorySpire/1.0 (personal book library app; contact: n/a)",
}

# ============================================================
# THEMES — same 10 palettes as the Streamlit app. Keys match
# the CSS custom-property names used there (page/surface/
# surface2/card/text/muted/accent/accent2/line) so the rest of
# the UI code can stay palette-agnostic.
# ============================================================

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

STATUS_STRIPE = {
    "Read": "accent2",
    "Currently Reading": "accent",
    "Want to Read": "muted",
}


def blank_book():
    book = {col: "" for col in LIBRARY_COLUMNS}
    book["Favorite"] = False
    return book


def normalize_book(book):
    out = blank_book()
    out.update({k: v for k, v in book.items() if k in LIBRARY_COLUMNS})
    for col in LIBRARY_COLUMNS:
        if col == "Favorite":
            v = out[col]
            out[col] = (
                str(v).strip().lower() in ("true", "1", "1.0", "yes")
                if isinstance(v, str) else bool(v)
            )
        else:
            v = out[col]
            out[col] = "" if v is None else str(v)
            if out[col] in ("nan", "None"):
                out[col] = ""
    return out


def save_library(library):
    try:
        if os.path.exists(LIBRARY_FILE):
            try:
                shutil.copy(LIBRARY_FILE, LIBRARY_BACKUP_FILE)
            except Exception:
                pass
        with open(LIBRARY_FILE, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=LIBRARY_COLUMNS)
            writer.writeheader()
            for book in library:
                writer.writerow(normalize_book(book))
    except Exception:
        pass


def load_library():
    if os.path.exists(LIBRARY_FILE):
        try:
            with open(LIBRARY_FILE, "r", newline="", encoding="utf-8") as f:
                reader = csv.DictReader(f)
                return [normalize_book(row) for row in reader]
        except Exception:
            pass
    return []


def clean_isbn(raw):
    s = str(raw).strip()
    if s.lower() in ("nan", "none"):
        return ""
    s = re.sub(r'^="?', '', s)
    s = re.sub(r'"?$', '', s)
    s = re.sub(r'[^0-9Xx]', '', s)
    return s.upper()


def clean_author(value):
    v = str(value or "").strip()
    return v if v and v.lower() not in ("nan", "none") else "Unknown Author"


def clean_series(value):
    v = str(value or "").strip()
    return v if v and v.lower() not in ("nan", "none") else "Standalone"


def clean_genre(value):
    v = str(value or "").strip()
    return v if v and v.lower() not in ("nan", "none") else "Unknown Genre"


def detect_series(title):
    text = str(title)
    patterns = [
        r"\(([^()]*)#\s*(\d+(?:\.\d+)?)\)",
        r"\[([^\[\]]*)#\s*(\d+(?:\.\d+)?)\]",
        r"\(([^()]*)\bBook\s+(\d+(?:\.\d+)?)\)",
        r"\[([^\[\]]*)\bBook\s+(\d+(?:\.\d+)?)\]",
    ]
    for pattern in patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            series = match.group(1)
            series = re.sub(r",?\s*#\s*\d+(?:\.\d+)?", "", series, flags=re.IGNORECASE)
            series = re.sub(r"\bBook\s+\d+(?:\.\d+)?", "", series, flags=re.IGNORECASE)
            series = re.sub(r"\s+", " ", series).strip(" ,-:")
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
        match = re.search(pattern, str(title), re.IGNORECASE)
        if match:
            try:
                return float(match.group(1))
            except Exception:
                pass
    return None


def clean_title_for_lookup(title):
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


def status_stripe_color(status):
    """Returns a THEME key ('accent'/'accent2'/'muted') — caller
    resolves it against the active palette."""
    return STATUS_STRIPE.get(str(status).strip(), "muted")


# ============================================================
# METADATA LOOKUP (Google Books + OpenLibrary), unchanged logic
# from the Streamlit version.
# ============================================================

_metadata_cache = {}


def _http_get_with_backoff(url, params=None, timeout=6, max_retries=3):
    delay = 0.75
    for attempt in range(max_retries + 1):
        try:
            response = requests.get(
                url, params=params, timeout=timeout, headers=HTTP_HEADERS
            )
        except Exception:
            if attempt < max_retries:
                time.sleep(delay)
                delay *= 2
                continue
            return None
        if response.status_code in (429, 500, 502, 503) and attempt < max_retries:
            time.sleep(delay)
            delay *= 2
            continue
        return response
    return None


def _normalize_for_key(text):
    text = str(text or "").strip().lower()
    text = re.sub(r"[^\w\s]", "", text)
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def _metadata_cache_key(title, author, isbn):
    isbn = clean_isbn(isbn)
    if isbn:
        return f"isbn:{isbn}"
    return f"ta:{_normalize_for_key(clean_title_for_lookup(title))}|{_normalize_for_key(author)}"


def _pick_genre_from_categories(categories):
    for category in categories:
        parts = [p.strip() for p in str(category).split("/") if p.strip()]
        for part in reversed(parts):
            if part.lower() not in GENERIC_GENRE_TERMS:
                return part
        if parts:
            return parts[0]
    return ""


def _pick_genre_from_subjects(subjects):
    for subject in subjects:
        subject = str(subject).strip()
        if subject and subject.lower() not in GENERIC_GENRE_TERMS and len(subject) < 40:
            return subject
    return ""


def _google_books_lookup(query):
    response = _http_get_with_backoff(
        "https://www.googleapis.com/books/v1/volumes",
        params={"q": query, "maxResults": 1},
    )
    if response is None or response.status_code != 200:
        return None
    try:
        items = response.json().get("items", [])
    except Exception:
        return None
    return items[0].get("volumeInfo", {}) if items else None


def _openlibrary_lookup(title="", author="", isbn=""):
    if isbn:
        response = _http_get_with_backoff(f"https://openlibrary.org/isbn/{isbn}.json")
        if response is None or response.status_code != 200:
            return None
        try:
            edition = response.json()
        except Exception:
            return None
        if not edition:
            return None

        # An ISBN edition record almost never carries "subject"
        # itself -- subjects live on the parent Work. Follow the
        # work link so genre can actually be filled from ISBN
        # lookups instead of always coming back empty.
        subjects = []
        works = edition.get("works") or []
        if works:
            work_key = works[0].get("key")
            if work_key:
                work_response = _http_get_with_backoff(
                    f"https://openlibrary.org{work_key}.json"
                )
                if work_response is not None and work_response.status_code == 200:
                    try:
                        work_data = work_response.json()
                        subjects = work_data.get("subjects", []) or []
                    except Exception:
                        subjects = []

        covers = edition.get("covers") or []
        return {
            "cover_i": covers[0] if covers else None,
            "subject": subjects,
            "publisher": edition.get("publishers") or [],
            "number_of_pages_median": edition.get("number_of_pages"),
            "first_publish_year": edition.get("publish_date"),
        }

    response = _http_get_with_backoff(
        "https://openlibrary.org/search.json",
        params={
            "title": title, "author": author,
            "fields": "cover_i,subject,publisher,first_publish_year,number_of_pages_median",
            "limit": 1,
        },
    )
    if response is None or response.status_code != 200:
        return None
    try:
        docs = response.json().get("docs", [])
    except Exception:
        return None
    return docs[0] if docs else None


def fetch_book_metadata(title, author="", isbn=""):
    """Cover, description, genre, publisher, page count, and
    publication date for one book. ISBN first (most reliable),
    then title/author fallback for whatever's still missing."""

    isbn = clean_isbn(isbn)
    clean_title = clean_title_for_lookup(title)
    cache_key = _metadata_cache_key(title, author, isbn)

    if cache_key in _metadata_cache:
        return _metadata_cache[cache_key]

    result = {
        "cover": "", "description": "", "genre": "", "publisher": "",
        "pages": "", "publication_date": "", "matched_by": "none",
    }

    def fill_from_google(info):
        if not info:
            return
        if not result["cover"]:
            links = info.get("imageLinks", {})
            image = links.get("thumbnail") or links.get("smallThumbnail")
            if image:
                result["cover"] = image.replace("http://", "https://")
        if not result["description"]:
            description = info.get("description", "")
            if description:
                result["description"] = description.strip()
        if not result["genre"]:
            genre = _pick_genre_from_categories(info.get("categories", []))
            if genre:
                result["genre"] = genre
        if not result["publisher"]:
            publisher = info.get("publisher", "")
            if publisher:
                result["publisher"] = publisher.strip()
        if not result["pages"] and info.get("pageCount"):
            result["pages"] = info["pageCount"]
        if not result["publication_date"]:
            published = info.get("publishedDate", "")
            if published:
                result["publication_date"] = published.strip()

    def fill_from_openlibrary(doc):
        if not doc:
            return
        if not result["cover"]:
            cover_id = doc.get("cover_i")
            if cover_id:
                result["cover"] = f"https://covers.openlibrary.org/b/id/{cover_id}-L.jpg"
        if not result["genre"]:
            genre = _pick_genre_from_subjects(doc.get("subject", []))
            if genre:
                result["genre"] = genre
        if not result["publisher"]:
            publishers = doc.get("publisher", [])
            if publishers:
                result["publisher"] = str(publishers[0]).strip()
        if not result["pages"] and doc.get("number_of_pages_median"):
            result["pages"] = doc["number_of_pages_median"]
        if not result["publication_date"] and doc.get("first_publish_year"):
            result["publication_date"] = str(doc["first_publish_year"])

    def still_missing_fields():
        return not all([
            result["cover"], result["description"], result["genre"],
            result["publisher"], result["pages"], result["publication_date"],
        ])

    if isbn and still_missing_fields():
        info = _google_books_lookup(f"isbn:{isbn}")
        if info:
            fill_from_google(info)
            result["matched_by"] = "isbn"

    if isbn and still_missing_fields():
        doc = _openlibrary_lookup(isbn=isbn)
        if doc:
            fill_from_openlibrary(doc)
            if result["matched_by"] == "none":
                result["matched_by"] = "isbn"

    if still_missing_fields() and clean_title.strip():
        query = (
            f"intitle:{clean_title} inauthor:{author}".strip()
            if str(author).strip() else f"intitle:{clean_title}"
        )
        info = _google_books_lookup(query)
        if info:
            fill_from_google(info)
            if result["matched_by"] == "none":
                result["matched_by"] = "title_author"

    if still_missing_fields() and clean_title.strip():
        doc = _openlibrary_lookup(title=clean_title, author=author)
        if doc:
            fill_from_openlibrary(doc)
            if result["matched_by"] == "none":
                result["matched_by"] = "title_author"

    _metadata_cache[cache_key] = result
    return result


def fetch_missing_metadata_parallel(library, indices, want_cover=True,
                                     want_description=True, want_genre=True,
                                     want_pubinfo=True, on_progress=None):
    """Used right after an import — fills in whichever requested
    fields are still blank for the given (newly-added) indices."""
    total = len(indices)
    if total == 0:
        return {"isbn": 0, "title_author": 0, "none": 0}
    done = 0
    stats = {"isbn": 0, "title_author": 0, "none": 0}
    # Free/unauthenticated APIs (especially OpenLibrary) start
    # throttling or dropping requests hard well before 8 concurrent
    # connections, which on a big import (hundreds of books) shows
    # up as most books simply never getting a cover/genre. 4 is a
    # much safer ceiling.
    workers = min(4, max(2, total))

    with ThreadPoolExecutor(max_workers=workers) as executor:
        future_to_index = {
            executor.submit(
                fetch_book_metadata,
                library[i]["Title"], library[i]["Author"], library[i]["ISBN"],
            ): i
            for i in indices
        }
        for future in as_completed(future_to_index):
            i = future_to_index[future]
            try:
                metadata = future.result()
            except Exception:
                metadata = {}

            if want_cover and not str(library[i].get("Cover") or "").strip():
                library[i]["Cover"] = metadata.get("cover", "")
            if want_description and not str(library[i].get("Description") or "").strip():
                library[i]["Description"] = metadata.get("description", "")
            if want_genre and not str(library[i].get("Genre") or "").strip():
                library[i]["Genre"] = metadata.get("genre", "")
            if want_pubinfo:
                if not str(library[i].get("Publisher") or "").strip():
                    library[i]["Publisher"] = metadata.get("publisher", "")
                if not str(library[i].get("Pages") or "").strip():
                    library[i]["Pages"] = metadata.get("pages", "")
                if not str(library[i].get("Publication Date") or "").strip():
                    library[i]["Publication Date"] = metadata.get("publication_date", "")

            stats[metadata.get("matched_by", "none")] = stats.get(metadata.get("matched_by", "none"), 0) + 1
            done += 1
            if on_progress:
                on_progress(done, total)

    return stats


# One-field "fetch missing X" helpers, mirroring the Streamlit
# Books-tab buttons (fetch_missing_covers / _descriptions /
# _genres / _publisher_pages there).

def _missing_indices_for_field(library, field):
    if field == "pubinfo":
        return [
            i for i, b in enumerate(library)
            if not (
                str(b.get("Publisher") or "").strip()
                and str(b.get("Pages") or "").strip()
                and str(b.get("Publication Date") or "").strip()
            )
        ]
    key = {"cover": "Cover", "description": "Description", "genre": "Genre"}[field]
    return [i for i, b in enumerate(library) if not str(b.get(key) or "").strip()]


def fetch_missing_field(library, field, on_progress=None):
    """field: 'cover' | 'description' | 'genre' | 'pubinfo'.
    Mutates library in place. Returns (found, total)."""

    indices = _missing_indices_for_field(library, field)
    total = len(indices)
    if total == 0:
        return 0, 0

    found = 0
    done = 0

    def work(i):
        return i, fetch_book_metadata(
            library[i]["Title"], library[i]["Author"], library[i]["ISBN"]
        )

    with ThreadPoolExecutor(max_workers=min(4, max(2, total))) as executor:
        futures = [executor.submit(work, i) for i in indices]
        for future in as_completed(futures):
            i, metadata = future.result()
            got = False

            if field == "cover" and metadata.get("cover"):
                library[i]["Cover"] = metadata["cover"]
                got = True
            elif field == "description" and metadata.get("description"):
                library[i]["Description"] = metadata["description"]
                got = True
            elif field == "genre" and metadata.get("genre"):
                library[i]["Genre"] = metadata["genre"]
                got = True
            elif field == "pubinfo":
                if not str(library[i].get("Publisher") or "").strip() and metadata.get("publisher"):
                    library[i]["Publisher"] = metadata["publisher"]
                    got = True
                if not str(library[i].get("Pages") or "").strip() and metadata.get("pages"):
                    library[i]["Pages"] = metadata["pages"]
                    got = True
                if not str(library[i].get("Publication Date") or "").strip() and metadata.get("publication_date"):
                    library[i]["Publication Date"] = metadata["publication_date"]
                    got = True

            if got:
                found += 1
            done += 1
            if on_progress:
                on_progress(done, total)

    return found, total


# ============================================================
# IMPORT — CSV, TXT, XLSX (openpyxl, pure-Python), PDF (pypdf).
# ============================================================

def load_rows_from_path(path):
    name = path.lower()

    if name.endswith(".csv"):
        try:
            with open(path, "r", newline="", encoding="utf-8", errors="ignore") as f:
                return list(csv.DictReader(f)), None
        except Exception as error:
            return None, f"Could not read this CSV file: {error}"

    elif name.endswith((".xlsx", ".xlsm")):
        try:
            import openpyxl
        except ImportError:
            return None, "Excel import needs the `openpyxl` package -- add `openpyxl` to requirements.txt."
        try:
            wb = openpyxl.load_workbook(path, read_only=True, data_only=True)
            ws = wb.active
            rows_iter = ws.iter_rows(values_only=True)
            try:
                header = [str(h).strip() if h is not None else "" for h in next(rows_iter)]
            except StopIteration:
                return None, "This Excel file has no rows."
            rows = []
            for raw_row in rows_iter:
                row = {}
                for col_name, value in zip(header, raw_row):
                    if not col_name:
                        continue
                    row[col_name] = "" if value is None else value
                if any(str(v).strip() for v in row.values()):
                    rows.append(row)
            wb.close()
            if not rows:
                return None, "No rows found in this Excel file."
            return rows, None
        except Exception as error:
            return None, f"Could not read this Excel file: {error}"

    elif name.endswith(".txt"):
        try:
            with open(path, "r", encoding="utf-8", errors="ignore") as f:
                raw = f.read()
            rows = []
            for line in raw.splitlines():
                line = line.strip()
                if not line:
                    continue
                parts = re.split(r"\s+-\s+|\s+by\s+", line, maxsplit=1, flags=re.IGNORECASE)
                if len(parts) == 2:
                    rows.append({"Title": parts[0].strip(), "Author": parts[1].strip()})
                else:
                    rows.append({"Title": line, "Author": ""})
            if not rows:
                return None, "No lines found in this text file."
            return rows, None
        except Exception as error:
            return None, f"Could not read this text file: {error}"

    elif name.endswith(".pdf"):
        try:
            import pypdf
        except ImportError:
            return None, "PDF import needs the `pypdf` package -- add `pypdf` to requirements.txt."
        try:
            reader = pypdf.PdfReader(path)
            lines = []
            for page in reader.pages:
                text = page.extract_text() or ""
                lines.extend(text.splitlines())

            rows = []
            for line in lines:
                line = line.strip()
                if not line or len(line) < 3:
                    continue
                parts = re.split(r"\s+-\s+|\s+by\s+", line, maxsplit=1, flags=re.IGNORECASE)
                if len(parts) == 2:
                    rows.append({"Title": parts[0].strip(), "Author": parts[1].strip()})
                else:
                    rows.append({"Title": line, "Author": ""})

            if not rows:
                return None, "No readable text found in this PDF."
            return rows, None
        except Exception as error:
            return None, f"Could not read this PDF file: {error}"

    else:
        return None, "Unsupported file type."


def import_books_from_rows(rows, existing_library, merge=True):
    """merge=True -> add only new (title, author) pairs, keep
    everything else untouched. merge=False -> replace the whole
    library with what's in this file."""

    if not rows:
        return None, 0, 0, [], "No books were found in the file."

    columns = {str(c).strip().lower(): c for c in rows[0].keys()}

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
        return None, 0, 0, [], "I couldn't find a Title column in this file."

    imported = []
    for row in rows:
        title = str(row.get(title_col, "")).strip()
        if not title or title.lower() == "nan":
            continue

        author = str(row.get(author_col, "")).strip() if author_col else ""
        if not author or author.lower() == "nan":
            author = "Unknown Author"

        isbn13 = clean_isbn(row.get(isbn13_col, "")) if isbn13_col else ""
        isbn10 = clean_isbn(row.get(isbn_col, "")) if isbn_col else ""
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
                if value not in (None, ""):
                    series_number = float(value)
            except Exception:
                pass
        if series_number is None:
            series_number = detect_series_number(title)

        rating = None
        if rating_col:
            try:
                value = row.get(rating_col)
                if value not in (None, ""):
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
            elif shelf == "read" or shelf == "finished" or ("read" in shelf and "to-read" not in shelf):
                status = "Read"
            elif "to-read" in shelf or "want" in shelf or "wishlist" in shelf:
                status = "Want to Read"

        book = blank_book()
        book.update({
            "Title": title, "Author": author, "Series": series,
            "Series Number": series_number if series_number is not None else "",
            "Genre": genre, "ISBN": isbn,
            "My Rating": rating if rating is not None else "",
            "Status": status, "Favorite": False, "Tags": tags,
        })
        imported.append(book)

    if not imported:
        return None, 0, 0, [], "No books were found in the file."

    def make_key(book):
        return (str(book["Title"]).strip().lower(), str(book["Author"]).strip().lower())

    if merge and existing_library:
        existing_keys = {make_key(b) for b in existing_library}
        new_rows = [b for b in imported if make_key(b) not in existing_keys]
        skipped_count = len(imported) - len(new_rows)
        combined = existing_library + new_rows
        fetch_start = len(existing_library)
    else:
        new_rows = imported
        skipped_count = 0
        combined = list(imported)
        fetch_start = 0

    added_count = len(new_rows)
    new_indices = list(range(fetch_start, fetch_start + added_count))

    return combined, added_count, skipped_count, new_indices, None
