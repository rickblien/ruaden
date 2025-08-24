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
            .block-container {
                padding-top: 5rem; /* Push content lower */
                padding-bottom: 2rem;
                max-width: 980px;
            }
            .stTextInput > div > div > input,
            .stNumberInput > div > div > input,
            textarea {
                border-radius: 12px !important;
                border: 1px solid #e6e6e6 !important;
                padding: .55rem .8rem !important;
            }
            .stButton > button {
                background: #111 !important;
                color: #fff !important;
                border: none !important;
                border-radius: 14px !important;
                padding: .55rem 1rem !important;
                font-weight: 500 !important;
                transition: transform .12s ease, opacity .12s ease;
            }
            .stButton > button:hover {
                transform: translateY(-1px);
                opacity: .95;
            }
            table {
                border-collapse: collapse;
                width: 100%;
            }
            th, td {
                padding: 8px 10px;
                border-bottom: 1px solid #eee;
            }
            th {
                color: #666;
                font-weight: 600;
            }
            td {
                color: #222;
            }
            .stTabs [data-baseweb="tab-list"] {
                gap: .25rem;
                margin-top: 1rem; /* Lower tabs */
            }
            .stTabs [data-baseweb="tab"] {
                padding: .6rem 1rem;
            }
            .streamlit-expanderHeader {
                font-weight: 600;
            }
            #topbar-account {
                margin-bottom: 1rem; /* Prevent overlap */
            }
            @media (max-width: 600px) {
                .block-container {
                    padding-top: 4rem; /* Adjusted for mobile */
                    padding-left: 1rem;
                    padding-right: 1rem;
                }
                .stButton > button {
                    width: 100%;
                    margin-bottom: 0.5rem;
                }
                .stTabs [data-baseweb="tab-list"] {
                    margin-top: 0.5rem; /* Adjusted for mobile */
                }
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
        "error_title_required": "Recipe title is required.",
        "error_ingredients_required": "At least one ingredient is required.",
        "duplicate_recipe": "A recipe with this title already exists.",
        "error_invalid_name": "Invalid ingredient name",
        "error_invalid_unit": "Invalid unit",
        "error_negative_qty": "Quantity must be positive.",
        "save_recipe": "Save Recipe",
        "update_recipe": "Update Recipe",
        "delete_recipe": "Delete Recipe",
        "update_success": "Recipe '{title}' updated successfully.",
        "delete_success": "Recipe '{title}' deleted successfully.",
        "update_failed": "Failed to update recipe '{title}'.",
        "delete_failed": "Failed to delete recipe '{title}'.",
        "deleting": "Deleting recipe '{title}'",
        "purchased": "Inventory updated with purchased items.",
        "not_logged_in": "You must be logged in to access this page.",
    },
    "Vietnamese": {
        "app_title": APP_TITLE_VI,
        "login": "🔐 Đăng nhập",
        "username": "Tên người dùng",
        "password": "Mật khẩu",
        "login_button": "Đăng nhập",
        "register": "🆕 Đăng ký",
        "sec_question": "Câu hỏi bảo mật (để đặt lại mật khẩu)",
        "sec_answer": "Câu trả lời bảo mật",
        "create_account": "Tạo tài khoản",
        "reset_password": "♻️ Đặt lại mật khẩu",
        "new_password": "Mật khẩu mới",
        "reset_button": "Đặt lại mật khẩu",
        "inventory": "📦 Kho hàng",
        "your_stock": "Kho của bạn",
        "no_ingredients": "Chưa có nguyên liệu.",
        "recipes": "📖 Công thức",
        "your_recipes": "Công thức của bạn",
        "no_recipes": "Chưa có công thức.",
        "feasibility": "✅ Tính khả thi & Mua sắm",
        "create_recipes_first": "Hãy tạo công thức trước.",
        "you_can_cook": "Tính khả thi công thức và Danh sách mua sắm",
        "none_yet": "Chưa có.",
        "all_available": "Tất cả nguyên liệu đều có sẵn.",
        "cook": "Nấu ăn",
        "missing_something": "Thiếu nguyên liệu",
        "all_feasible": "Tất cả công thức đều khả thi 🎉",
        "add_to_shopping": "Thêm nguyên liệu thiếu vào Danh sách mua sắm cho",
        "shopping_list": "🛒 Danh sách mua sắm",
        "empty_list": "Danh sách mua sắm của bạn trống.",
        "update_inventory": "Cập nhật kho từ Danh sách mua sắm",
        "logout": "Đăng xuất",
        "unit_tips": "Mẹo đơn vị: sử dụng g, kg, ml, l, tsp, tbsp, cup, piece, cái, pcs, lạng, chén, bát.",
        "language": "Ngôn ngữ",
        "error_title_required": "Tiêu đề công thức là bắt buộc.",
        "error_ingredients_required": "Cần ít nhất một nguyên liệu.",
        "duplicate_recipe": "Công thức với tiêu đề này đã tồn tại.",
        "error_invalid_name": "Tên nguyên liệu không hợp lệ",
        "error_invalid_unit": "Đơn vị không hợp lệ",
        "error_negative_qty": "Số lượng phải dương.",
        "save_recipe": "Lưu công thức",
        "update_recipe": "Cập nhật công thức",
        "delete_recipe": "Xóa công thức",
        "update_success": "Công thức '{title}' được cập nhật thành công.",
        "delete_success": "Công thức '{title}' đã xóa thành công.",
        "update_failed": "Không thể cập nhật công thức '{title}'.",
        "delete_failed": "Không thể xóa công thức '{title}'.",
        "deleting": "Đang xóa công thức '{title}'",
        "purchased": "Kho được cập nhật với các mặt hàng đã mua.",
        "not_logged_in": "Bạn phải đăng nhập để truy cập trang này.",
    }
}

def get_text(key):
    lang = st.session_state.get("language", "English")
    logger.debug(f"Retrieving text for key '{key}' in language '{lang}'")
    if lang not in TEXT:
        logger.warning(f"Language '{lang}' not found, falling back to English")
        lang = "English"
    text = TEXT[lang].get(key, key)
    if text == key:
        logger.warning(f"Text key '{key}' not found in language '{lang}'")
    return text

def current_user_id():
    return st.session_state.get("user_id")

def auth_gate_tabs():
    # Ensure language is initialized
    if "language" not in st.session_state:
        st.session_state.language = "English"
        logger.debug("Initialized language to 'English' in auth_gate_tabs")

    # Language selection dropdown
    current_lang = st.session_state.language
    lang = st.selectbox(
        get_text("language"),
        ["English", "Vietnamese"],
        index=["English", "Vietnamese"].index(current_lang) if current_lang in ["English", "Vietnamese"] else 0,
        key="language_select_login"
    )
    if lang != st.session_state.language:
        logger.info(f"Language changed to '{lang}' on login page")
        st.session_state.language = lang
        st.rerun()

    # Precompute tab titles to ensure they reflect the current language
    tab_titles = [
        get_text("login"),
        get_text("register"),
        get_text("reset_password")
    ]
    tabs = st.tabs(tab_titles)
    
    with tabs[0]:
        with st.form("login_form"):
            username = st.text_input(get_text("username"))
            password = st.text_input(get_text("password"), type="password")
            if st.form_submit_button(get_text("login_button")):
                user_id = DatabaseManager.verify_login(username, password)
                if user_id:
                    st.session_state.user_id = user_id
                    st.session_state.username = username
                    st.success(get_text("login_button") + " successful!")
                    logger.info(f"User '{username}' logged in with user_id={user_id}")
                    st.rerun()
                else:
                    st.error("Invalid username or password.")
                    logger.warning(f"Failed login attempt for username '{username}'")
    
    with tabs[1]:
        with st.form("register_form"):
            username = st.text_input(get_text("username"))
            password = st.text_input(get_text("password"), type="password")
            sec_question = st.text_input(get_text("sec_question"))
            sec_answer = st.text_input(get_text("sec_answer"), type="password")
            if st.form_submit_button(get_text("create_account")):
                success, message = DatabaseManager.create_user(username, password, sec_question, sec_answer)
                if success:
                    st.success(message)
                    logger.info(f"User '{username}' registered successfully")
                    st.rerun()
                else:
                    st.error(message)
                    logger.warning(f"Failed to register user '{username}': {message}")
    
    with tabs[2]:
        with st.form("reset_password_form"):
            username = st.text_input(get_text("username"))
            sec_answer = st.text_input(get_text("sec_answer"), type="password")
            new_password = st.text_input(get_text("new_password"), type="password")
            if st.form_submit_button(get_text("reset_button")):
                if DatabaseManager.reset_password(username, sec_answer, new_password):
                    st.success("Password reset successfully!")
                    logger.info(f"Password reset for user '{username}'")
                    st.rerun()
                else:
                    st.error("Invalid username or security answer.")
                    logger.warning(f"Failed password reset for username '{username}'")

def topbar_account():
    if st.session_state.get("username"):
        st.markdown('<div id="topbar-account">', unsafe_allow_html=True)
        col1, col2 = st.columns([3, 1])
        with col1:
            st.write(f"Welcome, {st.session_state.username}!")
        with col2:
            if st.button(get_text("logout")):
                logger.info(f"User {st.session_state.username} logged out, clearing session state.")
                keys_to_clear = [
                    "user_id", "username", "inventory_data", "recipes_data", "shopping_list_data"
                ]
                for key in keys_to_clear:
                    if key in st.session_state:
                        del st.session_state[key]
                st.success("Logged out successfully!")
                st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

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

def feasibility_page():
    user_id = current_user_id()
    if not user_id:
        st.error(get_text("not_logged_in"))
        return
    st.header(get_text("feasibility"))
    st.subheader(get_text("you_can_cook"))
    inventory_key = f"inventory_data_{user_id}"
    recipes_key = f"recipes_data_{user_id}"
    if inventory_key not in st.session_state:
        try:
            st.session_state[inventory_key] = DatabaseManager.list_inventory(user_id)
        except Exception as e:
            logger.error(f"Error loading inventory: {e}")
            st.error("Failed to load inventory.")
            st.session_state[inventory_key] = []
    inventory = st.session_state[inventory_key]
    if recipes_key not in st.session_state:
        try:
            st.session_state[recipes_key] = DatabaseManager.list_recipes(user_id)
        except Exception as e:
            logger.error(f"Error loading recipes: {e}")
            st.error("Failed to load recipes.")
            st.session_state[recipes_key] = []
    recipes = st.session_state[recipes_key]
    def norm_name(name):
        return DatabaseManager.normalize_name(name).strip().lower()
    def norm_unit(unit):
        return unit.strip().lower()
    inventory_dict = {}
    for ing in inventory:
        if ing.get('name') and ing.get('unit'):
            key = (norm_name(ing['name']), norm_unit(ing['unit']))
            inventory_dict[key] = ing
    recipe_results = []
    for recipe in recipes:
        if 'id' not in recipe or 'title' not in recipe or 'ingredients' not in recipe:
            logger.warning(f"Skipping invalid recipe: {recipe}")
            continue
        missing = []
        matched = []
        for req_ing in recipe['ingredients']:
            req_name = norm_name(req_ing['name'])
            req_qty = req_ing.get('quantity', 0.0)
            req_unit = norm_unit(req_ing.get('unit', ''))
            inv = inventory_dict.get((req_name, req_unit))
            have_qty = inv['quantity'] if inv else 0.0
            if have_qty >= req_qty:
                matched.append({
                    "Name": req_ing['name'],
                    "Need": req_qty,
                    "Have": have_qty,
                    "Unit": req_unit,
                    "Missing": 0
                })
            else:
                missing.append({
                    "Name": req_ing['name'],
                    "Need": req_qty,
                    "Have": have_qty,
                    "Unit": req_unit,
                    "Missing": req_qty - have_qty
                })
        recipe_results.append({
            "recipe": recipe,
            "matched": matched,
            "missing": missing,
            "missing_count": len(missing)
        })
    recipe_results.sort(key=lambda x: (x["missing_count"], -len(x["matched"])))
    st.markdown("#### Select recipes to cook (least missing on top)")
    recipe_titles = [r["recipe"]["title"] for r in recipe_results]
    selected_titles = st.multiselect(
        "Select recipes to cook:",
        options=recipe_titles,
        default=[]
    )
    for r in recipe_results:
        recipe = r["recipe"]
        matched = r["matched"]
        missing = r["missing"]
        st.markdown(f"#### {recipe['title']}")
        if not missing:
            st.success(get_text("all_available"))
        else:
            st.warning(get_text("missing_something"))
            try:
                st.data_editor(missing, column_config={
                    "Name": st.column_config.TextColumn(required=True),
                    "Need": st.column_config.NumberColumn(min_value=0.0, step=0.1, required=True),
                    "Have": st.column_config.NumberColumn(min_value=0.0, step=0.1, required=True),
                    "Unit": st.column_config.SelectboxColumn(options=VALID_UNITS, required=True),
                    "Missing": st.column_config.NumberColumn(min_value=0.0, step=0.1, required=True),
                }, num_rows="fixed", key=f"missing_{recipe['id']}")
            except KeyError as e:
                logger.error(f"KeyError in data_editor: {e} for recipe {recipe.get('title')}")
                st.error(f"Error displaying missing ingredients for {recipe['title']}: Missing key {e}")
    selected_missing = []
    for r in recipe_results:
        if r["recipe"]["title"] in selected_titles:
            for m in r["missing"]:
                selected_missing.append({"Name": m["Name"], "Quantity": m["Missing"], "Unit": m["Unit"]})
    if selected_titles and selected_missing and st.button("Send missing ingredients to Shopping List"):
        st.session_state['shopping_list_data'] = selected_missing
        st.success("Missing ingredients sent to Shopping List tab.")
        st.rerun()

def shopping_list_page():
    user_id = current_user_id()
    if not user_id:
        st.error(get_text("not_logged_in"))
        return
    inventory_key = f"inventory_data_{user_id}"
    if inventory_key not in st.session_state:
        try:
            st.session_state[inventory_key] = DatabaseManager.list_inventory(user_id)
        except Exception as e:
            logger.error(f"Error loading inventory: {e}")
            st.error("Failed to load inventory.")
            st.session_state[inventory_key] = []
    inventory = st.session_state[inventory_key]
    def norm_name(name):
        return DatabaseManager.normalize_name(name).strip().lower()
    def norm_unit(unit):
        return unit.strip().lower()
    inventory_dict = {}
    for ing in inventory:
        if ing.get('name') and ing.get('unit'):
            key = (norm_name(ing['name']), norm_unit(ing['unit']))
            inventory_dict[key] = ing
    shopping_list = st.session_state.get('shopping_list_data', [])
    st.header(get_text("shopping_list"))
    if shopping_list:
        shopping_list = sorted(shopping_list, key=lambda x: x["Name"].lower())
        shopping_data = st.data_editor(
            shopping_list,
            column_config={
                "Name": st.column_config.TextColumn(required=True),
                "Quantity": st.column_config.NumberColumn(min_value=0.0, step=0.1, required=True),
                "Unit": st.column_config.SelectboxColumn(options=VALID_UNITS, required=True),
            },
            num_rows="dynamic",
            key="shopping_list_editor",
        )
        purchased_names = st.multiselect(
            "Select purchased ingredients:",
            options=[f"{item['Name']} ({item['Unit']})" for item in shopping_data],
            default=[]
        )
        if st.button(get_text("update_inventory")):
            for item in shopping_data:
                item_label = f"{item['Name']} ({item['Unit']})"
                if item_label in purchased_names:
                    inv = inventory_dict.get((norm_name(item["Name"]), norm_unit(item["Unit"])))
                    if inv:
                        new_qty = inv["quantity"] + item["Quantity"]
                        DatabaseManager.update_inventory_item(inv["id"], inv["name"], new_qty, inv["unit"])
                    else:
                        DatabaseManager.upsert_inventory(user_id, item["Name"], item["Quantity"], item["Unit"])
            st.session_state[inventory_key] = DatabaseManager.list_inventory(user_id)
            st.success(get_text("purchased"))
            st.rerun()
    else:
        st.info(get_text("empty_list"))