import os
import streamlit as st
from supabase import create_client, Client
from dotenv import load_dotenv, find_dotenv

load_dotenv(find_dotenv())

DB_PASS = os.getenv("SUPABASE_PASS")
DB_URI = (
    f"postgresql://postgres:{DB_PASS}@db.yujtuocdlrnqnknhxiap.supabase.co:5432/postgres"
)

url: str = os.environ.get("SUPABASE_URL")
key: str = os.environ.get("SUPABASE_KEY")


def app():
    st.title("Welcome to InnoLibrary")

    if "user_email" not in st.session_state:
        st.session_state.user_email = ""
    if "user_id" not in st.session_state:
        st.session_state.user_id = ""

    def login():
        try:
            supabase: Client = create_client(url, key)
            user = supabase.auth.sign_in_with_password(
                {"email": email, "password": password}
            )
            st.success("Login Sucessfull!")
            st.session_state.user_id = user.user.id
            st.session_state.user_email = user.user.email

            st.session_state.signed_out = True
            st.session_state.sign_out = True

        except:
            st.warning("Login Failed")

    def logout():
        st.session_state.signed_out = False
        st.session_state.sign_out = False

    if "signed_out" not in st.session_state:
        st.session_state.signed_out = False
    if "sign_out" not in st.session_state:
        st.session_state.sign_out = False

    if not st.session_state["signed_out"]:
        choice = st.selectbox("Login/Signup", ["Login", "Sign Up"])

        if choice == "Login":
            email = st.text_input("Username")
            password = st.text_input("Password", type="password")

            st.button("Login", on_click=login)

        else:
            email = st.text_input("Username")
            password = st.text_input("Password", type="password")
            confirm_password = st.text_input("Confirm Password", type="password")

            if st.button("Create My Account"):
                supabase: Client = create_client(url, key)
                res = supabase.auth.sign_up(
                    {
                        "email": email,
                        "password": password,
                    }
                )

                st.success(
                    "Account created successfully! Please Check Inbox and Verify!"
                )
                st.markdown(
                    "Login once verified!"
                )

    if st.session_state.sign_out:
        st.text("Email Id: " + st.session_state.user_email)
        st.text("User Id: " + st.session_state.user_id)
        st.button("Sign out", on_click=logout)
