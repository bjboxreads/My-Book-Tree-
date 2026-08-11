# ============================================================
# TAB 1: BOOK TREE (Collapsible Tree View)
# ============================================================

with tree_tab:
    st.subheader("Search My Book Tree")
    search = st.text_input(
        "Search",
        placeholder="Search by author, title, series, genre, or ISBN...",
        label_visibility="collapsed",
    )

    filtered = library.copy()

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

        filtered = filtered[searchable.str.contains(q, na=False, regex=False)]

    if filtered.empty:
        if library.empty:
            st.info("Your tree is empty. Import your library or add your first book.")
        else:
            st.info(f'No books matched "{search}".')
    else:
        st.html(
            f"""
            <div class="tree-root">
                <div class="tree-root-title">My Library</div>
                <div class="tree-root-count">{len(filtered)} books · {filtered["Author"].nunique()} authors</div>
            </div>
            """
        )

        author_list = sorted(
            filtered["Author"].fillna("Unknown Author").astype(str).unique(),
            key=lambda x: x.lower(),
        )

        # TREE LEVEL 1: AUTHORS
        for author in author_list:
            author_books = filtered[
                filtered["Author"].fillna("Unknown Author").astype(str) == author
            ].copy()
           
            author_label = f"📁 {author} ({len(author_books)} {'book' if len(author_books) == 1 else 'books'})"

            with st.expander(author_label, expanded=bool(search.strip())):
                series_list = sorted(
                    author_books["Series"].fillna("Standalone").astype(str).unique(),
                    key=lambda x: x.lower(),
                )

                # TREE LEVEL 2: SERIES / STANDALONE
                for series in series_list:
                    series_books = author_books[
                        author_books["Series"].fillna("Standalone").astype(str) == series
                    ].copy()

                    if "Series Number" in series_books.columns:
                        series_books = series_books.sort_values(
                            by="Series Number", na_position="last"
                        )

                    series_label = f"📚 {series} ({len(series_books)} {'book' if len(series_books) == 1 else 'books'})"

                    # If it's standalone books, render them directly under the author
                    if series.lower() == "standalone":
                        st.markdown("**Standalone Titles:**")
                        for _, book in series_books.iterrows():
                            cover_html = (
                                f'<img src="{book["Cover"]}" class="book-cover"/>'
                                if book["Cover"]
                                else '<div style="width:55px;height:80px;background:var(--surface);border:1px solid var(--accent);border-radius:3px 10px 3px 10px;display:flex;align-items:center;justify-content:center;font-size:20px;">📖</div>'
                            )
                            rating_str = f" · ⭐ {book['My Rating']}/5" if pd.notna(book["My Rating"]) and book["My Rating"] else ""
                           
                            st.html(
                                f"""
                                <div class="book-branch">
                                    {cover_html}
                                    <div>
                                        <div class="book-title">{html.escape(str(book["Title"]))}</div>
                                        <div class="book-meta">Status: {html.escape(str(book["Status"]))}{rating_str}</div>
                                        <div class="book-meta">Genre: {html.escape(str(book["Genre"] or 'Uncategorized'))}</div>
                                    </div>
                                </div>
                                """
                            )
                    else:
                        # Nested expander for actual Series
                        with st.expander(series_label, expanded=bool(search.strip())):
                            # TREE LEVEL 3: BOOKS IN SERIES
                            for _, book in series_books.iterrows():
                                cover_html = (
                                    f'<img src="{book["Cover"]}" class="book-cover"/>'
                                    if book["Cover"]
                                    else '<div style="width:55px;height:80px;background:var(--surface);border:1px solid var(--accent);border-radius:3px 10px 3px 10px;display:flex;align-items:center;justify-content:center;font-size:20px;">📖</div>'
                                )
                                rating_str = f" · ⭐ {book['My Rating']}/5" if pd.notna(book["My Rating"]) and book["My Rating"] else ""
                                s_num_str = f" #{book['Series Number']}" if pd.notna(book["Series Number"]) else ""

                                st.html(
                                    f"""
                                    <div class="book-branch">
                                        {cover_html}
                                        <div>
                                            <div class="book-title">{html.escape(str(book["Title"]))}{s_num_str}</div>
                                            <div class="book-meta">Status: {html.escape(str(book["Status"]))}{rating_str}</div>
                                            <div class="book-meta">Genre: {html.escape(str(book["Genre"] or 'Uncategorized'))}</div>
                                        </div>
                                    </div>
                                    """
                                )
