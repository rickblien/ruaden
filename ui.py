import streamlit as st
import html
from datetime import datetime, date
import csv
import io
from typing import Optional
from database import DatabaseManager
from utils import VALID_UNITS, validate_unit
from config import APP_TITLE_EN, APP_TITLE_VI
import logging

# Logging setup
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def inject_css():
    st.markdown(
        """
        <style>
            .block-container {padding-top: 2rem; padding-bottom: 2rem; max-width: 980px;}
            .stTextInput > div > div > input,
            .stNumberInput > div > div > input,
            textarea {
                border-radius: 12px !important;
                border: 1px solid #e6e6e6 !important;
                padding: .55rem .8rem !important;
            }
            .stButton > button {
                background:#111 !important; color:#fff !important; border:none !important;
                border-radius: 14px !important; padding:.55rem 1rem !important; font-weight: 500 !important;
                transition: transform .12s ease, opacity .12s ease;
            }
            .stButton > button:hover {transform: translateY(-1px); opacity:.95}
            table {border-collapse: collapse; width:100%}
            th, td {padding: 8px 10px; border-bottom: 1px solid #eee}
            th {color:#666; font-weight: 600}
            td {color:#222}
            .stTabs [data-baseweb="tab-list"] {gap: .25rem}
            .stTabs [data-baseweb="tab"] {padding: .6rem 1rem}
            .streamlit-expanderHeader {font-weight:600}
            @media (max-width: 600px) {
                .block-container {padding: 1rem;}
                .stButton > button {width: 100%; margin-bottom: 0.5rem;}
            }
        </style>
        """,
        unsafe_allow_html=True,
    )

TEXT = {
    "English": {
        "app_title": APP_TITLE_EN,
        "login": "🔐 Login",
        "username": "Username",
        "password": "Password",
        "login_button": "Login",
        "register": "🆕 Register",
        "sec_question": "Security Question (for password reset)",
        "sec_answer": "Security Answer",
        "create_account": "Create Account",
        "reset_password": "♻️ Reset Password",
        "new_password": "New Password",
        "reset_button": "Reset Password",
        "inventory": "📦 Inventory",
        "your_stock": "Your Stock",
        "no_ingredients": "No ingredients yet.",
        "recipes": "📖 Recipes",
        "your_recipes": "Your Recipes",
        "no_recipes": "No recipes yet.",
        "feasibility": "✅ Feasibility & Shopping",
        "create_recipes_first": "Create recipes first.",
        "you_can_cook": "Recipe Feasibility and Shopping List",
        "none_yet": "None yet.",
        "all_available": "All ingredients available.",
        "cook": "Cook",
        "missing_something": "Missing Ingredients",
        "all_feasible": "All recipes are feasible 🎉",
        "add_to_shopping": "Add missing to Shopping List for",
        "shopping_list": "🛒 Shopping List",
        "empty_list": "Your shopping list is empty.",
        "update_inventory": "Update Inventory from Shopping List",
        "logout": "Logout",
        "unit_tips": "Unit tips: use g, kg, ml, l, tsp, tbsp, cup, piece, cái, pcs, lạng, chén, bát.",
        "language": "Language",
        "error_required": "All fields are required.",
        "error_title_required": "Title is required.",
        "error_ingredients_required": "At least one valid ingredient is required.",
        "error_invalid_unit": "Invalid unit. Please choose from the dropdown.",
        "error_negative_qty": "Quantity cannot be negative.",
        "error_invalid_name": "Ingredient name must be alphanumeric with spaces, no special characters.",
        "low_inventory": "Low inventory alert: This ingredient is below 10% of required.",
        "purchased": "Purchased",
        "add_ingredient": "Add Ingredient",
        "ingredient_name": "Ingredient Name",
        "quantity": "Quantity",
        "unit": "Unit",
        # "refresh_inventory": "Refresh Inventory",  # Removed
        "duplicate_ingredient": "Ingredient already exists in inventory.",
        "add_recipe": "Add Recipe",
        "recipe_title": "Recipe Title",
        "category": "Category",
        "instructions": "Instructions",
        "save_recipe": "Save Recipe",
        # "refresh_recipes": "Refresh Recipes",  # Removed
        "duplicate_recipe": "A recipe with this title already exists.",
        "download_all_csv": "Download All Recipes as CSV",
        "delete_recipe": "Delete Recipe",
        "confirm_delete": "Are you sure you want to delete the recipe '{title}'? This action cannot be undone.",
        "delete_success": "Deleted recipe '{title}'.",
        "delete_failed": "Failed to delete recipe '{title}'.",
        "deleting": "Deleting '{title}'...",
        "update_recipe": "Update Recipe",
        "update_success": "Updated recipe '{title}'.",
        "update_failed": "Failed to update recipe '{title}'."
    },
    "Tiếng Việt": {
        "app_title": APP_TITLE_VI,
        "login": "🔐 Đăng nhập",
        "username": "Tên đăng nhập",
        "password": "Mật khẩu",
        "login_button": "Đăng nhập",
        "register": "🆕 Đăng ký",
        "sec_question": "Câu hỏi bảo mật (để đặt lại mật khẩu)",
        "sec_answer": "Câu trả lời bảo mật",
        "create_account": "Tạo tài khoản",
        "reset_password": "♻️ Đặt lại mật khẩu",
        "new_password": "Mật khẩu mới",
        "reset_button": "Đặt lại mật khẩu",
        "inventory": "📦 Kho",
        "your_stock": "Kho của bạn",
        "no_ingredients": "Chưa có nguyên liệu.",
        "recipes": "📖 Công thức",
        "your_recipes": "Công thức của bạn",
        "no_recipes": "Chưa có công thức.",
        "feasibility": "✅ Khả thi & Mua sắm",
        "create_recipes_first": "Tạo công thức trước.",
        "you_can_cook": "Khả thi và Danh sách mua sắm",
        "none_yet": "Chưa có.",
        "all_available": "Tất cả nguyên liệu có sẵn.",
        "cook": "Nấu",
        "missing_something": "Nguyên liệu còn thiếu",
        "all_feasible": "Tất cả công thức đều khả thi 🎉",
        "add_to_shopping": "Thêm thiếu vào Danh sách mua sắm cho",
        "shopping_list": "🛒 Danh sách mua sắm",
        "empty_list": "Danh sách mua sắm của bạn trống.",
        "update_inventory": "Cập nhật kho từ Danh sách mua sắm",
        "logout": "Đăng xuất",
        "unit_tips": "Mẹo đơn vị: sử dụng g, kg, ml, l, tsp, tbsp, cup, piece, cái, pcs, lạng, chén, bát.",
        "language": "Ngôn ngữ",
        "error_required": "Tất cả các trường đều bắt buộc.",
        "error_title_required": "Tiêu đề là bắt buộc.",
        "error_ingredients_required": "Ít nhất một nguyên liệu là bắt buộc.",
        "error_invalid_unit": "Đơn vị không hợp lệ. Vui lòng chọn từ danh sách.",
        "error_negative_qty": "Số lượng không thể âm.",
        "error_invalid_name": "Tên nguyên liệu phải là chữ và số, có thể có khoảng trắng, không có ký tự đặc biệt.",
        "low_inventory": "Cảnh báo kho thấp: Nguyên liệu này dưới 10% yêu cầu.",
        "purchased": "Đã mua",
        "add_ingredient": "Thêm Nguyên Liệu",
        "ingredient_name": "Tên Nguyên Liệu",
        "quantity": "Số Lượng",
        "unit": "Đơn Vị",
        # "refresh_inventory": "Làm Mới Kho",  # Removed
        "duplicate_ingredient": "Nguyên liệu đã tồn tại trong kho.",
        "add_recipe": "Thêm Công Thức",
        "recipe_title": "Tiêu Đề Công Thức",
        "category": "Danh Mục",
        "instructions": "Hướng Dẫn",
        "save_recipe": "Lưu Công Thức",
        # "refresh_recipes": "Làm Mới Công Thức",  # Removed
        "duplicate_recipe": "Công thức với tiêu đề này đã tồn tại.",
        "download_all_csv": "Tải Tất Cả Công Thức dưới dạng CSV",
        "delete_recipe": "Xóa Công Thức",
        "confirm_delete": "Bạn có chắc chắn muốn xóa công thức '{title}'? Hành động này không thể hoàn tác.",
        "delete_success": "Đã xóa công thức '{title}'.",
        "delete_failed": "Không thể xóa công thức '{title}'.",
        "deleting": "Đang xóa '{title}'...",
        "update_recipe": "Cập Nhật Công Thức",
        "update_success": "Đã cập nhật công thức '{title}'.",
        "update_failed": "Không thể cập nhật công thức '{title}'."
    }
}

def get_text(key: str) -> str:
    lang = st.session_state.get("language", "English")
    return TEXT.get(lang, TEXT["English"]).get(key, key)

def language_selector():
    st.session_state.language = st.selectbox(
        "🌐 Choose Language / Chọn ngôn ngữ",
        ["English", "Tiếng Việt"],
        index=0 if st.session_state.get("language", "English") == "English" else 1,
        key="lang_selector",
    )

def current_user_id() -> Optional[int]:
    user_id = st.session_state.get("user_id")
    if not user_id:
        st.error(get_text("error_required"))
        return None
    if not DatabaseManager.validate_user_id(user_id):
        st.error(get_text("error_required"))
        return None
    return user_id

def login_view():
    st.subheader(get_text("login"))
    with st.form("login_form", clear_on_submit=False):
        username = st.text_input(get_text("username"))
        password = st.text_input(get_text("password"), type="password")
        submitted = st.form_submit_button(get_text("login_button"))
    if submitted:
        if not username or not password:
            st.error(get_text("error_required"))
        else:
            uid = DatabaseManager.verify_login(username, password)
            if uid:
                # Clear all session state except for user_id, username, and language
                language = st.session_state.get("language", "English")
                st.session_state.clear()
                st.session_state.user_id = uid
                st.session_state.username = username
                st.session_state.language = language
                st.success("Logged in.")
                st.rerun()
            else:
                st.error("Invalid credentials.")
def clear_session_state():
    st.session_state.clear()

def register_view():
    st.subheader(get_text("register"))
    with st.form("register_form", clear_on_submit=False):
        username = st.text_input(get_text("username"))
        password = st.text_input(get_text("password"), type="password")
        sec_q = st.text_input(get_text("sec_question"))
        sec_a = st.text_input(get_text("sec_answer"), type="password")
        submitted = st.form_submit_button(get_text("create_account"))
    if submitted:
        if not username or not password or not sec_q or not sec_a:
            st.error(get_text("error_required"))
        else:
            ok, msg = DatabaseManager.create_user(username, password, sec_q, sec_a)
            if ok:
                st.success(msg)
            else:
                st.error(msg)

def auth_gate_tabs():
    st.markdown(f"# {get_text('app_title')}")
    language_selector()
    tab_login, tab_register = st.tabs([get_text("login").split(" ")[1], get_text("register").split(" ")[1]])
    with tab_login:
        login_view()
    with tab_register:
        register_view()

def topbar_account():
    left, right = st.columns([6, 1])
    with left:
        username = st.session_state.get("username", "Guest")
        st.markdown(f"### {get_text('app_title')} (Logged in as: {username})")
    with right:
        if st.button(get_text("logout")):
            st.session_state.user_id = None
            st.session_state.username = None
            st.rerun()

def inventory_page():
    user_id = current_user_id()
    if not user_id:
        st.error("You must be logged in to access the inventory. Please log in.")
        return

    inventory_key = f"inventory_data_{user_id}"
    st.header(get_text("inventory"))
    st.subheader(get_text("your_stock"))

    # Add a form for manual ingredient input in an expandable frame
    with st.expander(get_text('add_ingredient'), expanded=False):
        with st.form("add_ingredient_form", clear_on_submit=True):
            name = st.text_input(get_text("ingredient_name"), placeholder="e.g., chicken")
            quantity = st.number_input(get_text("quantity"), min_value=0.0, step=0.1, value=0.0)
            unit = st.selectbox(get_text("unit"), options=VALID_UNITS)
            st.markdown(get_text("unit_tips"))
            submitted = st.form_submit_button(get_text("add_ingredient"))
            if submitted:
                if not name.strip() or not validate_unit(unit) or not DatabaseManager.validate_name(name):
                    st.error(f"{get_text('error_invalid_name')} or {get_text('error_invalid_unit')}")
                elif quantity <= 0:
                    st.error(get_text("error_negative_qty"))
                else:
                    # Check for duplicate ingredient
                    existing = DatabaseManager.list_inventory(user_id)
                    new_name_norm = DatabaseManager.normalize_name(name)
                    match = next((item for item in existing if DatabaseManager.normalize_name(item["name"]) == new_name_norm), None)
                    if match:
                        # Update existing ingredient
                        if DatabaseManager.update_inventory_item(match["id"], name, quantity, unit):
                            st.success(f"Updated {name} in inventory.")
                            st.session_state[inventory_key] = DatabaseManager.list_inventory(user_id)
                            st.rerun()
                        else:
                            st.error(f"Failed to update {name} in inventory.")
                    else:
                        if DatabaseManager.upsert_inventory(user_id, name, quantity, unit):
                            st.success(f"Added {name} to inventory.")
                            st.session_state[inventory_key] = DatabaseManager.list_inventory(user_id)
                            st.rerun()
                        else:
                            st.error(f"Failed to add {name} to inventory.")

    # Load and display inventory
    inventory_key = f"inventory_data_{user_id}"
    if inventory_key not in st.session_state:
        st.session_state[inventory_key] = DatabaseManager.list_inventory(user_id)
    inv = st.session_state[inventory_key]
    if not inv:
        st.info(get_text("no_ingredients"))
        st.warning("Your inventory is empty. Add ingredients using the form above or the table below (click '+' to add a new row). Examples: 'chicken', 'eggs'.")
    else:
        # Create editor_data with index for tracking
        editor_data = [
            {
                "_index": idx,  # Temporary index to track original rows
                "Name": r["name"],
                "Quantity": r["quantity"],
                "Unit": r["unit"],
            }
            for idx, r in enumerate(inv)
        ]
        # Sort editor_data by Name in ascending order (case-insensitive)
        editor_data = sorted(editor_data, key=lambda x: x["Name"].lower())
        # Display data editor without _index
        display_data = [{"Name": r["Name"], "Quantity": r["Quantity"], "Unit": r["Unit"]} for r in editor_data]
        edited_data = st.data_editor(
            display_data,
            column_config={
                "Name": st.column_config.TextColumn(required=True),
                "Quantity": st.column_config.NumberColumn(min_value=0.0, step=0.1, required=True),
                "Unit": st.column_config.SelectboxColumn(options=VALID_UNITS, required=True),
            },
            num_rows="dynamic",
            key=f"inventory_editor_{user_id}",
        )
        if edited_data != display_data:
            # Track processed indices to detect deletions
            processed_indices = set()
            for edited_row in edited_data:
                if not edited_row.get("Name", "").strip() or not validate_unit(edited_row.get("Unit", "")) or not DatabaseManager.validate_name(edited_row.get("Name", "")):
                    st.error(f"Invalid data in row: {get_text('error_invalid_name')} or {get_text('error_invalid_unit')}")
                    continue
                # Check for duplicate ingredient
                existing = [item for item in inv if DatabaseManager.normalize_name(item["name"]) == DatabaseManager.normalize_name(edited_row["Name"])]
                if existing and not any(r["Name"] == edited_row["Name"] for r in editor_data):
                    st.error(f"{get_text('duplicate_ingredient')} for {edited_row['Name']}")
                    continue
                # Try to match with original editor_data by index
                matching_rows = [r for r in editor_data if r["Name"] == edited_row["Name"]]
                if matching_rows:
                    # Update existing item
                    original_idx = matching_rows[0]["_index"]
                    row_id = inv[original_idx]["id"]
                    processed_indices.add(original_idx)
                    if DatabaseManager.update_inventory_item(
                        row_id,
                        edited_row["Name"],
                        edited_row["Quantity"],
                        edited_row["Unit"]
                    ):
                        st.success(f"Updated {edited_row['Name']}.")
                    else:
                        st.error(f"Failed to update inventory item {edited_row['Name']}.")
                else:
                    # New item
                    if DatabaseManager.upsert_inventory(
                        user_id,
                        edited_row["Name"],
                        edited_row["Quantity"],
                        edited_row["Unit"]
                    ):
                        st.success(f"Added {edited_row['Name']} to inventory.")
                    else:
                        st.error(f"Failed to add {edited_row['Name']} to inventory.")
            # Detect and delete removed rows
            for idx, original_row in enumerate(editor_data):
                if idx not in processed_indices:
                    row_id = inv[idx]["id"]
                    if DatabaseManager.delete_inventory(row_id):
                        st.success(f"Deleted {original_row['Name']} from inventory.")
                    else:
                        st.error(f"Failed to delete {original_row['Name']} from inventory.")
            # Removed refresh inventory data logic
            st.session_state[inventory_key] = DatabaseManager.list_inventory(user_id)
            st.rerun()

    # Add a refresh button
    # Removed refresh inventory button and logic

def recipes_page():
    user_id = current_user_id()
    if not user_id:
        st.error("You must be logged in to access recipes. Please log in.")
        return
    st.header(get_text("recipes"))
    st.subheader(get_text("your_recipes"))

    # Load recipes
    recipes_key = f"recipes_data_{user_id}"
    if recipes_key not in st.session_state:
        st.session_state[recipes_key] = DatabaseManager.list_recipes(user_id)
    recipes = st.session_state[recipes_key]

    # Download all recipes as CSV
    if recipes:
        output = io.StringIO()
        writer = csv.writer(output, quoting=csv.QUOTE_MINIMAL)
        writer.writerow(["Recipe ID", "Title", "Category", "Instructions", "Ingredient Name", "Quantity", "Unit"])
        for r in sorted(recipes, key=lambda x: x["title"].lower()):
            for ing in r["ingredients"]:
                writer.writerow([
                    r["id"],
                    r["title"],
                    r["category"] or "",
                    r["instructions"] or "",
                    ing["name"],
                    ing["quantity"],
                    ing["unit"]
                ])
            if r["ingredients"]:
                writer.writerow([])
        csv_data = output.getvalue()
        st.download_button(
            label=get_text("download_all_csv"),
            data=csv_data,
            file_name=f"all_recipes_{date.today().isoformat()}.csv",
            mime="text/csv",
            key="download_all_recipes"
        )

    # Form for adding new recipe in an expandable frame
    with st.expander(get_text('add_recipe'), expanded=False):
        with st.form("new_recipe_form", clear_on_submit=True):
            # Initialize session state for form persistence
            if "new_recipe_title" not in st.session_state:
                st.session_state.new_recipe_title = ""
            if "new_recipe_category" not in st.session_state:
                st.session_state.new_recipe_category = ""
            if "new_recipe_instructions" not in st.session_state:
                st.session_state.new_recipe_instructions = ""
            if "new_recipe_data" not in st.session_state:
                st.session_state.new_recipe_data = [{"Name": "", "Quantity": 0.0, "Unit": VALID_UNITS[0]}]

            title = st.text_input(
                get_text("recipe_title"),
                value=st.session_state.new_recipe_title,
                placeholder="e.g., Chicken Curry",
                key="new_recipe_title_input"
            )
            category = st.text_input(
                get_text("category"),
                value=st.session_state.new_recipe_category,
                placeholder="e.g., Main Dish",
                key="new_recipe_category_input"
            )
            instructions = st.text_area(
                get_text("instructions"),
                value=st.session_state.new_recipe_instructions,
                placeholder="e.g., 1. Chop onions...\n2. Cook chicken...",
                key="new_recipe_instructions_input"
            )
            st.markdown(get_text("unit_tips"))

            # Update session state with form inputs
            if title != st.session_state.new_recipe_title:
                st.session_state.new_recipe_title = title
            if category != st.session_state.new_recipe_category:
                st.session_state.new_recipe_category = category
            if instructions != st.session_state.new_recipe_instructions:
                st.session_state.new_recipe_instructions = instructions

            # Display data editor for ingredients
            edited_data = st.data_editor(
                st.session_state.new_recipe_data,
                column_config={
                    "Name": st.column_config.TextColumn(
                        label=get_text("ingredient_name"),
                        required=True
                    ),
                    "Quantity": st.column_config.NumberColumn(
                        min_value=0.0,
                        step=0.1,
                        required=True
                    ),
                    "Unit": st.column_config.SelectboxColumn(
                        options=VALID_UNITS,
                        required=True
                    ),
                },
                num_rows="dynamic",
                key="new_recipe_ingredients",
            )

            # Update session state with edited data
            if edited_data != st.session_state.new_recipe_data:
                st.session_state.new_recipe_data = edited_data

            # Collect valid ingredients
            ingredients = [
                {"name": row["Name"], "quantity": row["Quantity"], "unit": row["Unit"]}
                for row in edited_data
                if row["Name"].strip()
            ]

            submitted = st.form_submit_button(get_text("save_recipe"))
            if submitted:
                if not title.strip():
                    st.error(get_text("error_title_required"))
                elif not ingredients:
                    st.error(get_text("error_ingredients_required"))
                else:
                    # Check for duplicate recipe title
                    existing_recipes = DatabaseManager.list_recipes(user_id)
                    if any(DatabaseManager.normalize_name(r["title"]) == DatabaseManager.normalize_name(title) for r in existing_recipes):
                        st.error(get_text("duplicate_recipe"))
                    else:
                        valid = True
                        for ing in ingredients:
                            if not ing["name"].strip() or not validate_unit(ing["unit"]) or not DatabaseManager.validate_name(ing["name"]):
                                st.error(get_text("error_invalid_name") + f" ({ing['name']})" if not ing["name"].strip() else get_text("error_invalid_unit"))
                                valid = False
                            if ing["quantity"] <= 0:
                                st.error(get_text("error_negative_qty"))
                                valid = False
                    if valid:
                        if DatabaseManager.create_recipe_from_table(user_id, title, category, instructions, ingredients):
                            st.success(f"Added recipe '{title}'.")
                            # Clear session state after successful save
                            st.session_state.pop("new_recipe_title", None)
                            st.session_state.pop("new_recipe_category", None)
                            st.session_state.pop("new_recipe_instructions", None)
                            st.session_state.pop("new_recipe_data", None)
                            # Add the new recipe to session state
                            new_recipe = DatabaseManager.get_recipe_by_title(user_id, title)
                            if new_recipe:
                                if recipes_key not in st.session_state:
                                    st.session_state[recipes_key] = []
                                st.session_state[recipes_key].append(new_recipe)
                                st.rerun()
                        else:
                            st.error(f"Failed to add recipe '{title}'.")
                            logger.error(f"Failed to add recipe '{title}' for user_id={user_id}")

    # Display existing recipes
    if not recipes:
        st.info(get_text("no_recipes"))
        st.warning("No recipes yet. Use the form above to add a new recipe (e.g., 'Chicken Curry' with ingredients like 'chicken', 'curry powder').")
    else:
        for r in sorted(recipes, key=lambda x: x["title"].lower()):
            with st.expander(f"{r['title']} ({r['category'] or 'No Category'}) - Editable"):
                # Editable fields mirroring the form
                with st.form(key=f"edit_recipe_form_{r['id']}"):
                    edit_title = st.text_input(
                        get_text("recipe_title"),
                        value=r["title"],
                        key=f"edit_title_{r['id']}"
                    )
                    edit_category = st.text_input(
                        get_text("category"),
                        value=r["category"] or "",
                        key=f"edit_category_{r['id']}"
                    )
                    edit_instructions = st.text_area(
                        get_text("instructions"),
                        value=r["instructions"] or "",
                        key=f"edit_instructions_{r['id']}"
                    )
                    st.markdown(get_text("unit_tips"))

                    # Convert ingredients to data editor format
                    edit_ingredients = [
                        {"Name": ing["name"], "Quantity": ing["quantity"], "Unit": ing["unit"]}
                        for ing in r["ingredients"]
                    ]
                    edited_data = st.data_editor(
                        edit_ingredients,
                        column_config={
                            "Name": st.column_config.TextColumn(
                                label=get_text("ingredient_name"),
                                required=True
                            ),
                            "Quantity": st.column_config.NumberColumn(
                                min_value=0.0,
                                step=0.1,
                                required=True
                            ),
                            "Unit": st.column_config.SelectboxColumn(
                                options=VALID_UNITS,
                                required=True
                            ),
                        },
                        num_rows="dynamic",
                        key=f"edit_ingredients_{r['id']}",
                    )

                    # Collect valid edited ingredients
                    ingredients = [
                        {"name": row["Name"], "quantity": row["Quantity"], "unit": row["Unit"]}
                        for row in edited_data
                        if row["Name"].strip()
                    ]

                    # Buttons side by side
                    col1, col2 = st.columns([1, 1])
                    with col1:
                        if st.form_submit_button(get_text("update_recipe")):
                            if not edit_title.strip():
                                st.error(get_text("error_title_required"))
                            elif not ingredients:
                                st.error(get_text("error_ingredients_required"))
                            else:
                                valid = True
                                for ing in ingredients:
                                    if not ing["name"].strip() or not validate_unit(ing["unit"]) or not DatabaseManager.validate_name(ing["name"]):
                                        st.error(f"Invalid ingredient: {get_text('error_invalid_name')} or {get_text('error_invalid_unit')}")
                                        valid = False
                                    if ing["quantity"] <= 0:
                                        st.error(get_text("error_negative_qty"))
                                        valid = False
                                if valid:
                                    if DatabaseManager.create_recipe_from_table(user_id, edit_title, edit_category, edit_instructions, ingredients, recipe_id=r["id"]):
                                        st.success(get_text("update_success").format(title=edit_title))
                                        # Update session state with the modified recipe
                                        updated_recipe = DatabaseManager.get_recipe_by_title(user_id, edit_title)
                                        if updated_recipe:
                                            recipes[recipes.index(r)] = updated_recipe
                                            st.session_state.recipes_data = recipes
                                        st.rerun()
                                    else:
                                        st.error(get_text("update_failed").format(title=edit_title))
                                        logger.error(f"Failed to update recipe '{edit_title}' (id={r['id']}) for user_id={user_id}")
                    with col2:
                        if st.form_submit_button(get_text("delete_recipe")):
                            st.info(get_text("deleting").format(title=r["title"]))
                            logger.info(f"Attempting to delete recipe '{r['title']}' (id={r['id']}) for user_id={user_id}")
                            if DatabaseManager.delete_recipe(r["id"]):
                                st.success(get_text("delete_success").format(title=r["title"]))
                                logger.info(f"Successfully deleted recipe '{r['title']}' (id={r['id']})")
                                st.session_state[recipes_key] = DatabaseManager.list_recipes(user_id)
                                st.rerun()
                            else:
                                st.error(get_text("delete_failed").format(title=r["title"]))
                                logger.error(f"Failed to delete recipe '{r['title']}' (id={r['id']})")

    # Removed refresh recipe button and logic