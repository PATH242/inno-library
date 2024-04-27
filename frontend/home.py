import streamlit as st

def display_books_as_cards(books, section_title):
    st.markdown(
        "<div style='display: flex; flex-wrap: wrap;'>",
        unsafe_allow_html=True
    )
    for i, book in enumerate(books):
        st.markdown(
            f"""
            <div class="book-card" style="margin-right: 20px;">
                <div class="book-title">{book['title']}</div>
                <div class="book-author">Author: {book['author']}</div>
            </div>
            """,
            unsafe_allow_html=True
        )
    st.markdown("</div>", unsafe_allow_html=True)

def app():
    st.title("Welcome to InnoLibrary")
    
    # Sample book data
    books = [
        {"title": "Book 1", "author": "Author 1"},
        {"title": "Book 2", "author": "Author 2"},
        {"title": "Book 3", "author": "Author 3"},
        {"title": "Book 4", "author": "Author 4"},
        {"title": "Book 5", "author": "Author 5"},
        {"title": "Book 6", "author": "Author 6"},
        {"title": "Book 7", "author": "Author 7"},
        {"title": "Book 8", "author": "Author 8"},
        {"title": "Book 9", "author": "Author 9"},
        {"title": "Book 10", "author": "Author 10"},
        # Add more books as needed
    ]
    
    # Pagination logic
    page_number = st.session_state.get("page_number", 0)
    page_size = 5
    total_books = len(books)
    total_pages = (total_books + page_size - 1) // page_size
    
    # Display books for the current page
    st.subheader(f"Books ({page_number * page_size + 1} - {min((page_number + 1) * page_size, total_books)} of {total_books})")
    cols = st.columns(page_size)
    for i, book in enumerate(books[page_number * page_size:(page_number + 1) * page_size]):
        with cols[i % page_size]:
            st.markdown(
                f"""
                <div class="book-card" style="margin-right: 20px;">
                <div class="book-title">{book['title']}</div>
                <div class="book-author">Author: {book['author']}</div>
                </div>
                """,
                unsafe_allow_html=True
            )
    
    # Previous and Next buttons
    st.write("")
    col1, col2, col3 = st.columns([1, 3, 1])

    previous_button = col1.button("Previous", key="previous_button_1")
    next_button = col3.button("Next", key="next_button_2")

    if previous_button and page_number > 0:
        st.session_state["page_number"] -= 1
    if next_button and page_number < total_pages - 1:
        st.session_state["page_number"] += 1

app()
