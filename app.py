STAT_FILTER_MAP = {
    "Books": "All",
    "Read": "Read",
    "Unread": "Want to Read",
    "Favorites": "Favorites",
}

# Authors/Series jump to the Book Tree tab instead of filtering
# the Books tab, since the tree is already grouped by author
# and series.
STAT_TAB_MAP = {
    "Authors": "tree",
    "Series": "tree",
}

columns = st.columns(6)

stats = [
    (total, "Books"),
    (authors, "Authors"),
    (series_count, "Series"),
    (read_count, "Read"),
    (unread_count, "Unread"),
    (favorites, "Favorites"),
]

for col, (number, label) in zip(columns, stats):

    with col:

        with st.container(key=f"statclick_{safe_id(label)}"):

            if st.button(
                f"{number}\n{label}",
                key=f"stat_btn_{safe_id(label)}",
                use_container_width=True,
            ):
                if label in STAT_FILTER_MAP:
                    st.session_state.stat_filter = STAT_FILTER_MAP[label]
                    st.session_state.active_tab = "books"
                else:
                    st.session_state.active_tab = STAT_TAB_MAP[label]
                    # Only "Series" narrows the tree to books
                    # that are actually in a series; "Authors"
                    # shows the tree unfiltered.
                    st.session_state.tree_series_only = (label == "Series")
                st.rerun()
