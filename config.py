import os
import tempfile
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configuration
APP_TITLE_EN = "🍳 Rua Den"
APP_TITLE_VI = "🍳 Rùa Đen"
DB_PATH = os.getenv("SQLITE_DB_PATH", os.path.join(tempfile.gettempdir(), "ruaden.db"))


# Database configuration
DB_NAME = "ruaden.db"

# Application titles
APP_TITLE_EN = "What to Cook Today"
APP_TITLE_VI = "Hôm Nay Nấu Gì"