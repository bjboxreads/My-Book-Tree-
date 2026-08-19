"""
StorySpire — Flet version, pandas-free.

Run locally:      flet run main.py
Build the APK:     flet build apk
"""

import flet as ft
import data

THEME = {
    "page": "#051614", "surface": "#0C2B24", "surface2": "#124A3C",
    "card": "#1B6650", "text": "#FFFBEF", "muted": "#B9D4C6",
    "accent": "#F2C14E", "accent2": "#3FCDA8", "line": "#E0972E",
}


def main(page: ft.Page):
    page.title = "StorySpire"
    page.bgcolor = THEME["page"]
    page.padding = 0
    page.scroll = ft.ScrollMode.AUTO

    state = {
        "library": data.load_library(),  # list of dicts
        "tab": "books",
    }

    body = ft.Column(expand=True, scroll=ft.ScrollMode.AUTO)

    # ---------------- shared widgets ----------------

    def stat(number, label):
        return ft.Container(
            content=ft.Column(
                [
                    ft.Text(str(number), size=22, color=THEME["accent"]),
                    ft.Text(label, size=12, color=THEME["text"]),
                ],
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                spacing=2,
            ),
            bgcolor=THEME["card"],
            border_radius=12,
            padding=14,
            expand=True,
            alignment=ft.alignment.center,
        )

    def stats_row():
        lib = state["library"]
        total = len(lib)
        authors = len({b["Author"] for b in lib}) if total else 0
        series_count = len({b["Series"] for b in lib if b["Series"] != "Standalone"}) if total else 0
        read_count = sum(1 for b in lib if b["Status"] == "Read")
        unread_count = sum(1 for b in lib if b["Status"] == "Want to Read")
        favorites = sum(1 for b in lib if b["Favorite"])
        return ft.Row(
            [
                stat(total, "Books"), stat(authors, "Authors"),
                stat(series_count, "Series"), stat(read_count, "Read"),
                stat(unread_count, "Unread"), stat(favorites, "Favorites"),
            ],
            spacing=8,
        )

    def nav_bar():
        items = [
            ("books", "📚 Books"),
            ("add", "➕ Add Book"),
            ("import", "📥 Import"),
        ]
        buttons = []
        for key, label in items:
            active = state["tab"] == key
            buttons.append(
                ft.ElevatedButton(
                    label,
                    bgcolor=THEME["accent"] if active else THEME["surface"],
                    color=THEME["page"] if active else THEME["text"],
                    on_click=lambda e, k=key: switch_tab(k),
                    expand=True,
                )
            )
        return ft.Row(buttons, spacing=8)

    def switch_tab(key):
        state["tab"] = key
        render()

    def book_card(book, idx):
        title = str(book.get("Title", ""))
        author = str(book.get("Author", ""))
        status = str(book.get("Status", ""))
        genre = str(book.get("Genre", "") or "")
        cover = str(book.get("Cover", "") or "")
        is_fav = bool(book.get("Favorite", False))

        def toggle_fav(e, i=idx):
            state["library"][i]["Favorite"] = not bool(state["library"][i]["Favorite"])
            data.save_library(state["library"])
            render()

        def open_edit(e, i=idx):
            open_edit_dialog(i)

        leading = (
            ft.Image(src=cover, width=40, height=58, fit=ft.ImageFit.COVER, border_radius=4)
            if cover else ft.Container(width=40, height=58, bgcolor=THEME["surface2"], border_radius=4)
        )

        subtitle = f"{author} — {status}"
        if genre:
            subtitle += f" · {genre}"

        return ft.Container(
            content=ft.Row(
                [
                    leading,
                    ft.Column(
                        [
                            ft.Text(title, color=THEME["text"], weight=ft.FontWeight.BOLD, size=14),
                            ft.Text(subtitle, color=THEME["muted"], size=12),
                        ],
                        expand=True,
                        spacing=2,
                    ),
                    ft.IconButton(
                        icon=ft.Icons.STAR if is_fav else ft.Icons.STAR_BORDER,
                        icon_color=THEME["accent"],
                        on_click=toggle_fav,
                    ),
                    ft.IconButton(icon=ft.Icons.EDIT, icon_color=THEME["muted"], on_click=open_edit),
                ],
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
            ),
            bgcolor=THEME["surface"],
            border_radius=10,
            padding=10,
            margin=ft.margin.only(bottom=6),
        )

    def grouped_list(books_with_idx, group_by):
        # books_with_idx: list of (idx, book) tuples, idx = position in state["library"]
        def group_key(book):
            if group_by == "Genre":
                return data.clean_genre(book.get("Genre", ""))
            return data.clean_author(book.get("Author", ""))

        groups = {}
        for idx, book in books_with_idx:
            key = group_key(book)
            groups.setdefault(key, []).append((idx, book))

        tiles = []
        for key in sorted(groups.keys(), key=lambda x: str(x).lower()):
            items = groups[key]
            tiles.append(
                ft.ExpansionTile(
                    title=ft.Text(f"{key} ({len(items)})", color=THEME["text"]),
                    bgcolor=THEME["surface2"],
                    collapsed_bgcolor=THEME["surface2"],
                    controls=[book_card(book, idx) for idx, book in items],
                )
            )
        return ft.Column(tiles, spacing=6)

    # ---------------- edit dialog ----------------

    def open_edit_dialog(idx):
        book = state["library"][idx]
        title_f = ft.TextField(label="Title", value=str(book["Title"]))
        author_f = ft.TextField(label="Author", value=str(book["Author"]))
        series_f = ft.TextField(label="Series", value=str(book["Series"]))
        genre_f = ft.TextField(label="Genre", value=str(book["Genre"]))
        status_f = ft.Dropdown(
            label="Status",
            value=str(book["Status"]),
            options=[ft.dropdown.Option(s) for s in ["Want to Read", "Currently Reading", "Read"]],
        )

        def save(e):
            state["library"][idx]["Title"] = title_f.value
            state["library"][idx]["Author"] = author_f.value
            state["library"][idx]["Series"] = series_f.value
            state["library"][idx]["Genre"] = genre_f.value
            state["library"][idx]["Status"] = status_f.value
            data.save_library(state["library"])
            page.close(dlg)
            render()

        def delete(e):
            state["library"].pop(idx)
            data.save_library(state["library"])
            page.close(dlg)
            render()

        dlg = ft.AlertDialog(
            title=ft.Text("Edit Book"),
            content=ft.Column(
                [title_f, author_f, series_f, genre_f, status_f],
                tight=True, width=350,
            ),
            actions=[
                ft.TextButton("Delete", icon=ft.Icons.DELETE, on_click=delete),
                ft.TextButton("Cancel", on_click=lambda e: page.close(dlg)),
                ft.FilledButton("Save", on_click=save),
            ],
        )
        page.open(dlg)

    # ---------------- BOOKS TAB ----------------

    def books_tab():
        search_f = ft.TextField(
            hint_text="Search title, author, series, genre, tag, ISBN...",
            bgcolor=THEME["surface"], color=THEME["text"], border_color=THEME["line"],
        )
        status_f = ft.Dropdown(
            value="All",
            width=180,
            options=[ft.dropdown.Option(s) for s in
                     ["All", "Favorites", "Read", "Currently Reading", "Want to Read"]],
        )
        group_f = ft.Dropdown(
            value="Author", width=140,
            options=[ft.dropdown.Option("Author"), ft.dropdown.Option("Genre")],
        )
        results = ft.Column()

        def apply_filters(e=None):
            lib = state["library"]
            if not lib:
                results.controls = [ft.Text("No books yet — add or import some.", color=THEME["muted"])]
                page.update()
                return

            items = list(enumerate(lib))

            if status_f.value == "Favorites":
                items = [(i, b) for i, b in items if b["Favorite"]]
            elif status_f.value != "All":
                items = [(i, b) for i, b in items if b["Status"] == status_f.value]

            q = (search_f.value or "").strip().lower()
            if q:
                def matches(b):
                    haystack = " ".join([
                        b.get("Title", ""), b.get("Author", ""), b.get("Series", ""),
                        b.get("Genre", ""), b.get("Tags", ""), b.get("ISBN", ""),
                    ]).lower()
                    return q in haystack
                items = [(i, b) for i, b in items if matches(b)]

            if not items:
                results.controls = [ft.Text(f'No books matched "{q}".' if q else "No books found.", color=THEME["muted"])]
            else:
                results.controls = [grouped_list(items, group_f.value)]
            page.update()

        search_f.on_change = apply_filters
        status_f.on_change = apply_filters
        group_f.on_change = apply_filters
        apply_filters()

        return ft.Column(
            [
                search_f,
                ft.Row([status_f, group_f], spacing=10),
                ft.Divider(color=THEME["line"]),
                results,
            ],
            spacing=10,
        )

    # ---------------- ADD TAB ----------------

    def add_tab():
        title_f = ft.TextField(label="Title", bgcolor=THEME["surface"], color=THEME["text"])
        author_f = ft.TextField(label="Author", bgcolor=THEME["surface"], color=THEME["text"])
        series_f = ft.TextField(label="Series (blank = standalone)", bgcolor=THEME["surface"], color=THEME["text"])
        genre_f = ft.TextField(label="Genre", bgcolor=THEME["surface"], color=THEME["text"])
        isbn_f = ft.TextField(label="ISBN", bgcolor=THEME["surface"], color=THEME["text"])
        status_f = ft.Dropdown(
            label="Status", value="Want to Read",
            options=[ft.dropdown.Option(s) for s in ["Want to Read", "Currently Reading", "Read"]],
        )
        fav_f = ft.Checkbox(label="Favorite", label_style=ft.TextStyle(color=THEME["text"]))
        status_text = ft.Text("", color=THEME["accent2"])

        def submit(e):
            if not title_f.value or not title_f.value.strip():
                status_text.value = "Please enter a title."
                status_text.color = "red"
                page.update()
                return
            if not author_f.value or not author_f.value.strip():
                status_text.value = "Please enter an author."
                status_text.color = "red"
                page.update()
                return

            status_text.value = "Looking up metadata..."
            status_text.color = THEME["muted"]
            page.update()

            metadata = data.fetch_book_metadata(title_f.value, author_f.value, isbn_f.value)
            actual_genre = (genre_f.value or "").strip() or metadata.get("genre", "")

            new_book = data.blank_book()
            new_book.update({
                "Title": title_f.value.strip(), "Author": author_f.value.strip(),
                "Series": (series_f.value or "").strip() or "Standalone",
                "Genre": actual_genre, "ISBN": data.clean_isbn(isbn_f.value),
                "Status": status_f.value, "Favorite": fav_f.value,
                "Cover": metadata.get("cover", ""), "Description": metadata.get("description", ""),
                "Publisher": metadata.get("publisher", ""), "Pages": metadata.get("pages", ""),
                "Publication Date": metadata.get("publication_date", ""),
            })
            state["library"].append(new_book)
            data.save_library(state["library"])

            status_text.value = f'"{new_book["Title"]}" added to your spire!'
            status_text.color = THEME["accent2"]
            title_f.value = author_f.value = series_f.value = genre_f.value = isbn_f.value = ""
            status_f.value = "Want to Read"
            fav_f.value = False
            page.update()

        return ft.Column(
            [
                ft.Text("Add a Book", size=22, color=THEME["accent"]),
                title_f, author_f, series_f, genre_f, isbn_f, status_f, fav_f,
                ft.FilledButton("Add to My Spire", on_click=submit),
                status_text,
            ],
            spacing=12,
        )

    # ---------------- IMPORT TAB ----------------

    def import_tab():
        status_text = ft.Text(
            "Upload a Goodreads CSV or plain text list (CSV recommended — "
            "Excel files aren't supported, export as CSV first).",
            color=THEME["muted"],
        )
        picked_path = {"path": None}

        def on_file_picked(e: ft.FilePickerResultEvent):
            if not e.files:
                return
            picked_path["path"] = e.files[0].path
            status_text.value = f"✓ {e.files[0].name} selected"
            status_text.color = THEME["muted"]
            page.update()

        file_picker = ft.FilePicker(on_result=on_file_picked)
        page.overlay.append(file_picker)

        def do_import(e):
            if not picked_path["path"]:
                status_text.value = "Choose a file first."
                status_text.color = "red"
                page.update()
                return

            rows, err = data.load_rows_from_path(picked_path["path"])
            if err:
                status_text.value = err
                status_text.color = "red"
                page.update()
                return

            combined, added, skipped, new_indices, err2 = data.import_books_from_rows(
                rows, state["library"], merge=True
            )
            if err2:
                status_text.value = err2
                status_text.color = "red"
                page.update()
                return

            state["library"] = combined
            data.save_library(combined)
            status_text.value = f"Fetching metadata for {added} new book(s)..."
            status_text.color = THEME["muted"]
            page.update()

            def progress(done, total):
                status_text.value = f"Looked up {done} of {total}..."
                page.update()

            data.fetch_missing_metadata_parallel(
                state["library"], new_indices, on_progress=progress
            )
            data.save_library(state["library"])

            status_text.value = f"✓ Added {added} new book(s), skipped {skipped} already in library."
            status_text.color = THEME["accent2"]
            page.update()
            render()

        return ft.Column(
            [
                ft.Text("Import Your Library", size=22, color=THEME["accent"]),
                ft.ElevatedButton(
                    "Choose File",
                    on_click=lambda e: file_picker.pick_files(allowed_extensions=["csv", "txt"]),
                ),
                ft.FilledButton("Raise My Spire", on_click=do_import),
                status_text,
            ],
            spacing=12,
        )

    # ---------------- render ----------------

    def render():
        tab = state["tab"]
        content = books_tab() if tab == "books" else add_tab() if tab == "add" else import_tab()

        body.controls = [
            ft.Container(
                content=ft.Column(
                    [
                        ft.Text(
                            "StorySpire",
                            size=40, weight=ft.FontWeight.BOLD,
                            color=THEME["accent"],
                            text_align=ft.TextAlign.CENTER,
                        ),
                        ft.Text(
                            "a library that rises one story at a time",
                            italic=True, color=THEME["muted"], size=13,
                            text_align=ft.TextAlign.CENTER,
                        ),
                    ],
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                ),
                padding=ft.padding.only(top=30, bottom=10),
                alignment=ft.alignment.center,
            ),
            ft.Container(stats_row(), padding=ft.padding.symmetric(horizontal=16)),
            ft.Container(nav_bar(), padding=ft.padding.symmetric(horizontal=16, vertical=14)),
            ft.Container(content, padding=ft.padding.symmetric(horizontal=16, vertical=6)),
        ]
        page.update()

    page.add(body)
    render()


ft.app(target=main)
