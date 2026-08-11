# ============================================================
# TREE
# ============================================================

with tree_tab:

    if library.empty:

        st.info(
            "Your tree is empty. "
            "Import your library or add your first book."
        )

    else:

        # ----------------------------------------------------
        # SEARCH
        # ----------------------------------------------------

        search = st.text_input(
            "Search your tree",
            placeholder="Search by author, title, genre, or ISBN...",
            key="tree_search",
        )

        filtered = library.copy()

        if search.strip():

            q = search.strip().lower()

            searchable = (
                filtered["Author"].fillna("").astype(str).str.lower().str.contains(q, na=False)
                |
                filtered["Title"].fillna("").astype(str).str.lower().str.contains(q, na=False)
                |
                filtered["ISBN"].fillna("").astype(str).str.lower().str.contains(q, na=False)
            )

            # Include Genre if your imported file has one.
            if "Genre" in filtered.columns:
                searchable = (
                    searchable
                    |
                    filtered["Genre"]
                    .fillna("")
                    .astype(str)
                    .str.lower()
                    .str.contains(q, na=False)
                )

            filtered = filtered[searchable]

        if filtered.empty:

            st.warning("No books matched your search.")

        else:

            # ------------------------------------------------
            # TREE CSS
            # ------------------------------------------------

            st.html(
                """
                <style>

                .ancestry-tree {
                    margin-top: 35px;
                    padding: 35px 15px 50px;
                    overflow-x: auto;
                }

                .library-root {
                    width: 280px;
                    margin: 0 auto 55px;
                    padding: 18px 25px;
                    background: var(--accent);
                    color: var(--page);
                    text-align: center;
                    border-radius: 6px 28px 6px 28px;
                    box-shadow: 0 8px 25px rgba(0,0,0,.25);
                    position: relative;
                }

                .library-root::after {
                    content: "";
                    position: absolute;
                    width: 2px;
                    height: 55px;
                    background: var(--line);
                    left: 50%;
                    top: 100%;
                }

                .library-root-title {
                    font-family:
                        "Berkshire Swash",
                        Georgia,
                        serif;
                    font-size: 34px;
                }

                .library-root-count {
                    font-family:
                        "Libre Baskerville",
                        Georgia,
                        serif;
                    font-size: 10px;
                    margin-top: 5px;
                    opacity: .8;
                }

                .author-tree {
                    display: flex;
                    gap: 35px;
                    justify-content: center;
                    align-items: flex-start;
                    min-width: max-content;
                    padding: 0 30px;
                }

                .author-branch {
                    width: 300px;
                    position: relative;
                    padding-top: 28px;
                }

                /*
                 * Vertical branch from library level
                 */

                .author-branch::before {
                    content: "";
                    position: absolute;
                    width: 2px;
                    height: 28px;
                    background: var(--line);
                    top: 0;
                    left: 50%;
                }

                .author-node {
                    position: relative;
                    background: var(--surface);
                    border: 2px solid var(--accent);
                    border-radius: 5px 22px 5px 22px;
                    padding: 15px 18px;
                    text-align: center;
                    box-shadow: 0 7px 20px rgba(0,0,0,.2);
                    margin-bottom: 32px;
                }

                .author-node::after {
                    content: "";
                    position: absolute;
                    width: 2px;
                    height: 32px;
                    background: var(--line);
                    left: 50%;
                    top: 100%;
                }

                .author-name {
                    font-family:
                        "Berkshire Swash",
                        Georgia,
                        serif;
                    font-size: 27px;
                    color: var(--text);
                }

                .author-count {
                    color: var(--muted);
                    font-family:
                        "Libre Baskerville",
                        Georgia,
                        serif;
                    font-size: 10px;
                    margin-top: 5px;
                }

                .author-children {
                    position: relative;
                    padding-top: 5px;
                }

                /*
                 * Horizontal branch connecting all
                 * series/standalone branches
                 */

                .author-children::before {
                    content: "";
                    position: absolute;
                    top: 0;
                    left: 12%;
                    right: 12%;
                    height: 2px;
                    background: var(--line);
                }

                .series-branch {
                    position: relative;
                    padding-top: 25px;
                    margin-bottom: 25px;
                }

                .series-branch::before {
                    content: "";
                    position: absolute;
                    width: 2px;
                    height: 25px;
                    background: var(--line);
                    left: 50%;
                    top: 0;
                }

                .series-node {
                    background: var(--surface2);
                    border: 1px solid var(--accent2);
                    border-radius: 4px 18px 4px 18px;
                    padding: 12px 15px;
                    text-align: center;
                    margin-bottom: 18px;
                }

                .series-name {
                    font-family:
                        "Berkshire Swash",
                        Georgia,
                        serif;
                    font-size: 22px;
                    color: var(--text);
                }

                .series-count {
                    color: var(--muted);
                    font-family:
                        "Libre Baskerville",
                        Georgia,
                        serif;
                    font-size: 9px;
                    margin-top: 4px;
                }

                .book-branch {
                    position: relative;
                    margin-left: 25px;
                    padding-left: 25px;
                    margin-bottom: 10px;
                    border-left: 2px solid var(--line);
                }

                .book-branch::before {
                    content: "";
                    position: absolute;
                    width: 25px;
                    height: 2px;
                    background: var(--line);
                    left: -2px;
                    top: 50%;
                }

                .tree-book {
                    background: var(--card);
                    border-radius: 4px 14px 4px 14px;
                    padding: 9px 11px;
                    display: flex;
                    gap: 10px;
                    align-items: center;
                    min-height: 62px;
                }

                .tree-book-cover {
                    width: 42px;
                    height: 62px;
                    object-fit: cover;
                    border-radius: 3px 8px 3px 8px;
                    border: 1px solid var(--accent);
                    flex-shrink: 0;
                }

                .tree-book-title {
                    font-family:
                        "Berkshire Swash",
                        Georgia,
                        serif;
                    font-size: 17px;
                    color: var(--text);
                    line-height: 1.2;
                }

                .tree-book-meta {
                    color: var(--muted);
                    font-family:
                        "Libre Baskerville",
                        Georgia,
                        serif;
                    font-size: 8px;
                    margin-top: 4px;
                }

                .standalone-node {
                    background: var(--surface2);
                    border: 1px solid var(--accent2);
                    border-radius: 4px 18px 4px 18px;
                    padding: 12px 15px;
                    text-align: center;
                    margin-bottom: 18px;
                    position: relative;
                }

                .standalone-node::before {
                    content: "";
                    position: absolute;
                    width: 2px;
                    height: 25px;
                    background: var(--line);
                    left: 50%;
                    bottom: 100%;
                }

                .standalone-title {
                    font-family:
                        "Berkshire Swash",
                        Georgia,
                        serif;
                    font-size: 21px;
                    color: var(--text);
                }

                </style>
                """
            )

            # ------------------------------------------------
            # ROOT
            # ------------------------------------------------

            st.html(
                f"""
                <div class="ancestry-tree">

                    <div class="library-root">

                        <div class="library-root-title">
                            My Library
                        </div>

                        <div class="library-root-count">
                            {len(filtered)} books ·
                            {filtered["Author"].nunique()} authors
                        </div>

                    </div>
                """
            )

            # ------------------------------------------------
            # AUTHORS
            # ------------------------------------------------

            st.html(
                '<div class="author-tree">'
            )

            author_list = sorted(
                filtered["Author"]
                .fillna("Unknown Author")
                .astype(str)
                .unique(),
                key=lambda x: x.lower(),
            )

            for author in author_list:

                author_books = filtered[
                    filtered["Author"]
                    .fillna("Unknown Author")
                    .astype(str)
                    == author
                ].copy()

                st.html(
                    f"""
                    <div class="author-branch">

                        <div class="author-node">

                            <div class="author-name">
                                {html.escape(author)}
                            </div>

                            <div class="author-count">
                                {len(author_books)}
                                {"book" if len(author_books) == 1 else "books"}
                            </div>

                        </div>

                        <div class="author-children">
                    """
                )

                # --------------------------------------------
                # SERIES
                # --------------------------------------------

                series_list = sorted(
                    author_books["Series"]
                    .fillna("Standalone")
                    .astype(str)
                    .unique(),
                    key=lambda x: x.lower(),
                )

                for series in series_list:

                    series_books = author_books[
                        author_books["Series"]
                        .fillna("Standalone")
                        .astype(str)
                        == series
                    ].copy()

                    # ----------------------------------------
                    # STANDALONES
                    # ----------------------------------------

                    if series == "Standalone":

                        for _, book in series_books.iterrows():

                            title = html.escape(
                                str(book.get("Title", ""))
                            )

                            status = html.escape(
                                str(book.get("Status", ""))
                            )

                            cover = str(
                                book.get("Cover", "") or ""
                            )

                            if cover:

                                book_html = f"""
                                <div class="book-branch">

                                    <div class="tree-book">

                                        <img
                                            class="tree-book-cover"
                                            src="{html.escape(cover)}"
                                        >

                                        <div>

                                            <div class="tree-book-title">
                                                {title}
                                            </div>

                                            <div class="tree-book-meta">
                                                {status}
                                            </div>

                                        </div>

                                    </div>

                                </div>
                                """

                            else:

                                book_html = f"""
                                <div class="book-branch">

                                    <div class="tree-book">

                                        <div>

                                            <div class="tree-book-title">
                                                {title}
                                            </div>

                                            <div class="tree-book-meta">
                                                {status}
                                            </div>

                                        </div>

                                    </div>

                                </div>
                                """

                            st.html(book_html)

                        continue

                    # ----------------------------------------
                    # SERIES NODE
                    # ----------------------------------------

                    st.html(
                        f"""
                        <div class="series-branch">

                            <div class="series-node">

                                <div class="series-name">
                                    {html.escape(series)}
                                </div>

                                <div class="series-count">
                                    {len(series_books)}
                                    {"book" if len(series_books) == 1 else "books"}
                                </div>

                            </div>
                        """
                    )

                    # ----------------------------------------
                    # BOOKS IN SERIES
                    # ----------------------------------------

                    series_books = series_books.sort_values(
                        by=[
                            "Series Number",
                            "Title",
                        ],
                        na_position="last",
                    )

                    for position, (_, book) in enumerate(
                        series_books.iterrows(),
                        1,
                    ):

                        number = book.get(
                            "Series Number"
                        )

                        if pd.notna(number):

                            try:

                                if float(number).is_integer():

                                    number_text = (
                                        f"Book {int(number)}"
                                    )

                                else:

                                    number_text = (
                                        f"Book {number}"
                                    )

                            except Exception:

                                number_text = (
                                    f"Book {position}"
                                )

                        else:

                            number_text = (
                                f"Book {position}"
                            )

                        title = html.escape(
                            str(book.get("Title", ""))
                        )

                        status = html.escape(
                            str(book.get("Status", ""))
                        )

                        cover = str(
                            book.get("Cover", "") or ""
                        )

                        if cover:

                            st.html(
                                f"""
                                <div class="book-branch">

                                    <div class="tree-book">

                                        <img
                                            class="tree-book-cover"
                                            src="{html.escape(cover)}"
                                        >

                                        <div>

                                            <div class="tree-book-title">
                                                {number_text} · {title}
                                            </div>

                                            <div class="tree-book-meta">
                                                {status}
                                            </div>

                                        </div>

                                    </div>

                                </div>
                                """
                            )

                        else:

                            st.html(
                                f"""
                                <div class="book-branch">

                                    <div class="tree-book">

                                        <div>

                                            <div class="tree-book-title">
                                                {number_text} · {title}
                                            </div>

                                            <div class="tree-book-meta">
                                                {status}
                                            </div>

                                        </div>

                                    </div>

                                </div>
                                """
                            )

                    st.html(
                        "</div>"
                    )

                st.html(
                    """
                        </div>
                    </div>
                    """
                )

            st.html(
                """
                    </div>
                </div>
                """
            )
