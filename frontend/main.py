import os
import streamlit as st
from streamlit_option_menu import option_menu
import home, account, upload, chatbots, chat, library

st.page_title="InnoLibrary"

class MultiApp:
    def __init__(self):
        self.apps = []

    def add_app(self, title, func):
        self.apps.append({"title": title, "function": func})

    def run(): 
        with st.sidebar:
            app = option_menu(
                menu_title="InnoLibrary ",
                options=["Home", "Account", "Library"],
                menu_icon="chat-text-fill",
                default_index=1,
            )

        if app == "Home":
            home.app()
        if app == "Account":
            account.app()
        if app == "Library":
            library.app()
        if app == "Chatbots":
            chatbots.app()
        if app == "Let's Chat":
            chat.app()

    run()