import streamlit as st
import pandas as pd

# Define styles
st.markdown(
    """
    <style>
        .book-card {
            padding: 20px;
            border-radius: 10px;
            box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
            background: linear-gradient(135deg, #f8f9fa, #dee2e6);
            margin-bottom: 20px;
            color: #333;
        }

        .book-title {
            font-size: 24px;
            font-weight: bold;
            margin-bottom: 10px;
        }

        .book-author {
            font-size: 14px;
            color: #555; /* Adjusted for better readability */
        }

        .section-title {
            font-size: 30px;
            font-weight: bold;
            color: #333;
            margin-bottom: 20px;
        }

        .hr-divider {
            margin-top: 20px;
            margin-bottom: 20px;
            border: none;
            height: 1px;
            background-color: #ccc;
        }

        .custom-container {
            width: 90%;
        }
    </style>
    """,
    unsafe_allow_html=True
)

# Mock user data
user_books = pd.DataFrame({
    "Title": ["Book 1", "Book 2", "Book 3", "Book 1", "Book 2", "Book 3"],
    "Author": ["Author 1", "Author 2", "Author 3", "Author 1", "Author 2", "Author 3"],
    "Progress": ["Started", "Not Started", "Completed", "Started", "Not Started", "Completed"]
})

recommended_books = pd.DataFrame({
    "Title": ["Recommended Book 1", "Recommended Book 2", "Recommended Book 3"],
    "Author": ["Author 4", "Author 5", "Author 6"]
})

def display_books_as_cards(books, section_title):
    # st.markdown(
    #     f"<div class='section-title'>{section_title}</div>",
    #     unsafe_allow_html=True
    # )
    st.markdown(
        "<div style='display: flex; flex-wrap: wrap;'>",
        unsafe_allow_html=True
    )
    for i, book in books.iterrows():
        progress_text = ""
        if "Progress" in book:
            progress_text = f"<div class='book-author'>Progress: {book['Progress']}</div>"

        st.markdown(
            f"""
            <div class="book-card" style="margin-right: 20px;">
                <div class="book-title">{book['Title']}</div>
                <div class="book-author">Author: {book['Author']}</div>
                {progress_text}
            </div>
            """,
            unsafe_allow_html=True
        )
    st.markdown("</div>", unsafe_allow_html=True)



def update_progress(selected_book, new_progress):
    for i, book in user_books.iterrows():
        if book["Title"] == selected_book:
            user_books.at[i, "Progress"] = new_progress

def app():
    st.title("Library Management System")

    col1, col2 = st.columns(2)

    with col1:
        with st.expander("Your Books", expanded=True):
            with st.container():
                st.markdown("<div style='max-height: 100px; overflow-y: scroll;'>", unsafe_allow_html=True)
                display_books_as_cards(user_books, "Your Books")
                st.markdown("</div>", unsafe_allow_html=True)

    with col2:
        with st.expander("Recommended Books", expanded=True):
            with st.container():
                st.markdown("<div style='max-height: 400px; overflow-y: scroll;'>", unsafe_allow_html=True)
                display_books_as_cards(recommended_books, "Recommended Books")
                st.markdown("</div>", unsafe_allow_html=True)

    selected_book = st.selectbox("Select a book to update progress:", user_books["Title"])
    new_progress = st.selectbox("Update progress:", ["Started", "Not Started", "Completed"])

    if st.button("Update Progress"):
        update_progress(selected_book, new_progress)
        st.success("Progress updated successfully!")

    st.markdown("<hr class='hr-divider'>", unsafe_allow_html=True)

if __name__ == "__main__":
    app()
