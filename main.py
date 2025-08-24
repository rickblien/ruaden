import streamlit as st
import sqlite3
from database import DatabaseManager
from ui import inject_css, auth_gate_tabs, topbar_account, inventory_page, recipes_page
from config import APP_TITLE_EN
from ui import shopping_list_page, feasibility_page

st.set_page_config(page_title=APP_TITLE_EN, page_icon="🍳", layout="wide")

def ensure_auth_state():
    if "user_id" not in st.session_state:
        st.session_state.user_id = None
    if "username" not in st.session_state:
        st.session_state.username = None
    if "language" not in st.session_state:
        st.session_state.language = "English"

def main():
    inject_css()
    ensure_auth_state()
    try:
        with DatabaseManager.get_db_conn() as conn:
            cur = conn.cursor()
            cur.execute("SELECT 1;")
        # Remove this line, as DatabaseManager does not have an init_db method
        # DatabaseManager.init_db()
    except sqlite3.Error as e:
        st.error(f"Database connection test failed: {e}")
        st.stop()
    if not st.session_state.user_id or not DatabaseManager.validate_user_id(st.session_state.user_id):
        auth_gate_tabs()
        return
    topbar_account()
    tabs = st.tabs(["Inventory", "Recipes", "Shopping List", "Feasibility & Shopping"])
    with tabs[0]:
        inventory_page()
    with tabs[1]:
        recipes_page()
    with tabs[2]:
        shopping_list_page()
    with tabs[3]:
        feasibility_page()

if __name__ == "__main__":

    main()