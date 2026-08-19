"""
StorySpire — Flet version.

Same app, same data, rebuilt UI. Run locally with:
    flet run main.py
Build an APK with:
    flet build apk
"""

import flet as ft
import pandas as pd
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
    page.fonts = {
        "Cormorant": "https://fonts.gstatic.com/s/cormorantgaramond/v16/co3bmX5slCNuHLi8bLeY9MK7whWMhyjYrEtI.ttf",
    }

    state = {
        "library": data.load_library(),
        "tab": "books",
    }

    body = ft.Column(expand=True, scroll=ft.ScrollMode.AUTO)

    # ---------------- shared widgets ----------------

    def stat(number, label):
        return ft.Container(
            content=ft.Column(
                [
                    ft.Text(str(number), size=22, color=THEME["accent"], font_family="Cormorant"),
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
        authors = lib["Author"].nunique() if total else 0
        series_count = lib[lib["Series"] != "Standalone"]["Series"].nunique() if total else 0
        read_count = len(lib[lib["Status"] == "Read"]) if total else 0
        unread_count = len(lib[lib["Status"] == "Want to Read"]) if total else 0
        favorites = len(lib[lib["Favorite"] == True]) if total else 0
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

    def book_card(row):
        title = str(row.get("Title", ""))
        author = str(row.get("Author", ""))
        status = str(row.get("Status", ""))
        genre = str(row.get("Genre", "") or "")
        cover = str(row.get("Cover", "") or "")
        is_fav = bool(row.get("Favorite", False))
        idx = row.name

        def toggle_fav(e, i=idx):
            state["library"].loc[i, "Favorite"] = not bool(state["library"].loc[i, "Favorite"])
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

    def grouped_list(df, group_by):
        col = df["Genre"].replace("", "Unknown Genre") if group_by == "Genre" else df["Author"]
        tiles = []
        for group_value in sorted(col.unique(), key=lambda x: str(x).lower()):
            group_df = df[col == group_value]
            tiles.append(
                ft.ExpansionTile(
                    title=ft.Text(f"{group_value} ({len(group_df)})", color=THEME["text"]),
                    bgcolor=THEME["surface2"],
                    collapsed_bgcolor=THEME["surface2"],
                    controls=[book_card(row) for _, row in group_df.iterrows()],
                )
            )
        return ft.Column(tiles, spacing=6)

    # ---------------- edit dialog ----------------

    def open_edit_dialog(idx):
        row = state["library"].loc[idx]
        title_f = ft.TextField(label="Title", value=str(row["Title"]))
        author_f = ft.TextField(label="Author", value=str(row["Author"]))
        series_f = ft.TextField(label="Series", value=str(row["Series"]))
        genre_f = ft.TextField(label="Genre", value=str(row["Genre"]))
        status_f = ft.Dropdown(
            label="Status",
            value=str(row["Status"]),
            options=[ft.dropdown.Option(s) for s in ["Want to Read", "Currently Reading", "Read"]],
        )

        def save(e):
            state["library"].loc[idx, "Title"] = title_f.value
            state["library"].loc[idx, "Author"] = author_f.value
            state["library"].loc[idx, "Series"] = series_f.value
            state["library"].loc[idx, "Genre"] = genre_f.value
            state["library"].loc[idx, "Status"] = status_f.value
            data.save_library(state["library"])
            page.close(dlg)
            render()

        def delete(e):
            state["library"] = state["library"].drop(index=idx).reset_index(drop=True)
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
            df = state["library"].copy()
            if df.empty:
                results.controls = [ft.Text("No books yet — add or import some.", color=THEME["muted"])]
                page.update()
                return

            if status_f.value == "Favorites":
                df = df[df["Favorite"] == True]
            elif status_f.value != "All":
                df = df[df["Status"] == status_f.value]

            q = (search_f.value or "").strip().lower()
            if q:
                searchable = (
                    df["Title"].fillna("").astype(str) + " " + df["Author"].fillna("").astype(str)
                    + " " + df["Series"].fillna("").astype(str) + " " + df["Genre"].fillna("").astype(str)
                    + " " + df["Tags"].fillna("").astype(str) + " " + df["ISBN"].fillna("").astype(str)
                ).str.lower()
                df = df[searchable.str.contains(q, na=False, regex=False)]

            if df.empty:
                results.controls = [ft.Text(f'No books matched "{q}".', color=THEME["muted"])]
            else:
                df = data.clean_author_series(df)
                results.controls = [grouped_list(df, group_f.value)]
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

            new_book = {
                "Title": title_f.value.strip(), "Author": author_f.value.strip(),
                "Series": (series_f.value or "").strip() or "Standalone",
                "Series Number": None, "Genre": actual_genre,
                "ISBN": data.clean_isbn(isbn_f.value), "My Rating": None,
                "Status": status_f.value, "Favorite": fav_f.value,
                "Cover": metadata.get("cover", ""), "Description": metadata.get("description", ""),
                "Tags": "", "Publisher": metadata.get("publisher", ""),
                "Pages": metadata.get("pages", ""),
                "Publication Date": metadata.get("publication_date", ""), "Date Read": "",
            }
            state["library"] = pd.concat(
                [state["library"], pd.DataFrame([new_book])], ignore_index=True
            )
            data.save_library(state["library"])

            status_text.value = f'"{new_book["Title"]}" added to your spire!'
            status_text.color = THEME["accent2"]
            title_f.value = author_f.value = series_f.value = genre_f.value = isbn_f.value = ""
            status_f.value = "Want to Read"
            fav_f.value = False
            page.update()

        return ft.Column(
            [
                ft.Text("Add a Book", size=22, color=THEME["accent"], font_family="Cormorant"),
                title_f, author_f, series_f, genre_f, isbn_f, status_f, fav_f,
                ft.FilledButton("Add to My Spire", on_click=submit),
                status_text,
            ],
            spacing=12,
        )

    # ---------------- IMPORT TAB ----------------

    def import_tab():
        status_text = ft.Text("", color=THEME["muted"])
        picked_path = {"path": None}

        def on_file_picked(e: ft.FilePickerResultEvent):
            if not e.files:
                return
            picked_path["path"] = e.files[0].path
            status_text.value = f"✓ {e.files[0].name} selected"
            page.update()

        file_picker = ft.FilePicker(on_result=on_file_picked)
        page.overlay.append(file_picker)

        def do_import(e):
            if not picked_path["path"]:
                status_text.value = "Choose a file first."
                status_text.color = "red"
                page.update()
                return

            df, err = data.load_dataframe_from_path(picked_path["path"])
            if err:
                status_text.value = err
                status_text.color = "red"
                page.update()
                return

            combined, added, skipped, new_indices, err2 = data.import_books_from_df(
                df, state["library"], merge=True
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
                ft.Text("Import Your Library", size=22, color=THEME["accent"], font_family="Cormorant"),
                ft.Text(
                    "Upload a Goodreads CSV, Excel spreadsheet, or plain text list.",
                    color=THEME["muted"],
                ),
                ft.ElevatedButton(
                    "Choose File",
                    on_click=lambda e: file_picker.pick_files(
                        allowed_extensions=["csv", "xlsx", "xls", "txt"]
                    ),
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
                            color=THEME["accent"], font_family="Cormorant",
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
