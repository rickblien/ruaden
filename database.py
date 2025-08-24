import sqlite3
from typing import Optional, List, Dict, Any
from config import DB_NAME

class DatabaseManager:
    @staticmethod
    def normalize_name(name: str) -> str:
        """Normalize inventory/recipe names for comparison."""
        return name.strip().lower() if isinstance(name, str) else ""
    @staticmethod
    def get_db_conn():
        conn = sqlite3.connect(DB_NAME)
        conn.row_factory = sqlite3.Row
        return conn

    @staticmethod
    def validate_user_id(user_id: int) -> bool:
        with DatabaseManager.get_db_conn() as conn:
            cur = conn.cursor()
            cur.execute("SELECT id FROM users WHERE id = ?", (user_id,))
            return cur.fetchone() is not None

    @staticmethod
    def verify_login(username: str, password: str) -> Optional[int]:
        with DatabaseManager.get_db_conn() as conn:
            cur = conn.cursor()
            cur.execute("SELECT id FROM users WHERE username = ? AND password = ?", (username, password))
            result = cur.fetchone()
            return result[0] if result else None

    @staticmethod
    def create_user(username: str, password: str, security_question: str, security_answer: str) -> tuple[bool, str]:
        try:
            with DatabaseManager.get_db_conn() as conn:
                cur = conn.cursor()
                cur.execute("INSERT INTO users (username, password, security_question, security_answer) VALUES (?, ?, ?, ?)",
                            (username, password, security_question, security_answer))
                conn.commit()
                return True, "User created successfully."
        except sqlite3.IntegrityError:
            return False, "Username already exists."

    @staticmethod
    def reset_password(username: str, security_answer: str, new_password: str) -> bool:
        with DatabaseManager.get_db_conn() as conn:
            cur = conn.cursor()
            cur.execute("SELECT id FROM users WHERE username = ? AND security_answer = ?", (username, security_answer))
            user = cur.fetchone()
            if user:
                cur.execute("UPDATE users SET password = ? WHERE id = ?", (new_password, user[0]))
                conn.commit()
                return True
            return False

    @staticmethod
    def list_inventory(user_id: int) -> List[Dict[str, Any]]:
        with DatabaseManager.get_db_conn() as conn:
            cur = conn.cursor()
            cur.execute("SELECT id, name, quantity, unit FROM inventory WHERE user_id = ?", (user_id,))
            return [dict(row) for row in cur.fetchall()]

    @staticmethod
    def upsert_inventory(user_id: int, name: str, quantity: float, unit: str) -> bool:
        with DatabaseManager.get_db_conn() as conn:
            cur = conn.cursor()
            cur.execute("SELECT id FROM inventory WHERE user_id = ? AND name = ? AND unit = ?", (user_id, name, unit))
            row = cur.fetchone()
            if row:
                cur.execute("UPDATE inventory SET quantity = ? WHERE id = ?", (quantity, row[0]))
            else:
                cur.execute("INSERT INTO inventory (user_id, name, quantity, unit) VALUES (?, ?, ?, ?)",
                            (user_id, name, quantity, unit))
            conn.commit()
            return True

    @staticmethod
    def update_inventory_item(item_id: int, name: str, quantity: float, unit: str) -> bool:
        with DatabaseManager.get_db_conn() as conn:
            cur = conn.cursor()
            cur.execute("UPDATE inventory SET name = ?, quantity = ?, unit = ? WHERE id = ?",
                        (name, quantity, unit, item_id))
            conn.commit()
            return cur.rowcount > 0

    @staticmethod
    def delete_inventory(item_id: int) -> bool:
        with DatabaseManager.get_db_conn() as conn:
            cur = conn.cursor()
            cur.execute("DELETE FROM inventory WHERE id = ?", (item_id,))
            conn.commit()
            return cur.rowcount > 0

    @staticmethod
    def list_recipes(user_id: int) -> List[Dict[str, Any]]:
        with DatabaseManager.get_db_conn() as conn:
            cur = conn.cursor()
            cur.execute("SELECT id, title, category, instructions FROM recipes WHERE user_id = ?", (user_id,))
            recipes = [dict(row) for row in cur.fetchall()]
            for recipe in recipes:
                cur.execute("SELECT name, quantity, unit FROM ingredients WHERE recipe_id = ?", (recipe["id"],))
                recipe["ingredients"] = [dict(row) for row in cur.fetchall()]
            return recipes

    @staticmethod
    def create_recipe_from_table(user_id: int, title: str, category: str, instructions: str, ingredients: List[Dict[str, Any]], recipe_id: Optional[int] = None) -> bool:
        with DatabaseManager.get_db_conn() as conn:
            cur = conn.cursor()
            if recipe_id:
                cur.execute("UPDATE recipes SET title = ?, category = ?, instructions = ? WHERE id = ? AND user_id = ?",
                            (title, category, instructions, recipe_id, user_id))
                if cur.rowcount == 0:
                    return False
                cur.execute("DELETE FROM ingredients WHERE recipe_id = ?", (recipe_id,))
            else:
                cur.execute("INSERT INTO recipes (user_id, title, category, instructions) VALUES (?, ?, ?, ?)",
                            (user_id, title, category, instructions))
                recipe_id = cur.lastrowid
            for ing in ingredients:
                cur.execute("INSERT INTO ingredients (recipe_id, name, quantity, unit) VALUES (?, ?, ?, ?)",
                            (recipe_id, ing["name"], ing["quantity"], ing["unit"]))
            conn.commit()
            return True

    @staticmethod
    def delete_recipe(recipe_id: int) -> bool:
        with DatabaseManager.get_db_conn() as conn:
            cur = conn.cursor()
            cur.execute("DELETE FROM ingredients WHERE recipe_id = ?", (recipe_id,))
            cur.execute("DELETE FROM recipes WHERE id = ?", (recipe_id,))
            conn.commit()
            return cur.rowcount > 0

    @staticmethod
    def get_recipe_by_title(user_id: int, title: str) -> Optional[Dict[str, Any]]:
        with DatabaseManager.get_db_conn() as conn:
            cur = conn.cursor()
            cur.execute(
                "SELECT id, title, category, instructions FROM recipes WHERE user_id = ? AND title = ?",
                (user_id, title)
            )
            recipe = cur.fetchone()
            if recipe:
                recipe_dict = dict(recipe)
                cur.execute("SELECT name, quantity, unit FROM ingredients WHERE recipe_id = ?", (recipe_dict["id"],))
                recipe_dict["ingredients"] = [dict(row) for row in cur.fetchall()]
                return recipe_dict
            return None

    @staticmethod
    def validate_name(name: str) -> bool:
        return bool(name and all(c.isalnum() or c.isspace() for c in name))
    
    

conn = sqlite3.connect("ruaden.db")
cursor = conn.cursor()
cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        password TEXT NOT NULL,
        security_question TEXT NOT NULL,
        security_answer TEXT NOT NULL
    )
""")
cursor.execute("""
    CREATE TABLE IF NOT EXISTS recipes (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        title TEXT NOT NULL,
        category TEXT,
        instructions TEXT,
        FOREIGN KEY (user_id) REFERENCES users(id)
    )
""")
cursor.execute("""
    CREATE TABLE IF NOT EXISTS ingredients (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        recipe_id INTEGER,
        name TEXT NOT NULL,
        quantity REAL NOT NULL,
        unit TEXT NOT NULL,
        FOREIGN KEY (recipe_id) REFERENCES recipes(id)
    )
""")
cursor.execute("""
    CREATE TABLE IF NOT EXISTS inventory (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        name TEXT NOT NULL,
        quantity REAL NOT NULL,
        unit TEXT NOT NULL,
        FOREIGN KEY (user_id) REFERENCES users(id)
    )
""")
conn.commit()
conn.close()