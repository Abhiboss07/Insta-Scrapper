import os
from dotenv import load_dotenv
load_dotenv()

API_KEY = os.getenv("GOOGLE_API_KEY")
CX = os.getenv("GOOGLE_CX")
INSTALOADER_SESSION_FILE = os.getenv("INSTALOADER_SESSION_FILE") or None

# Basic validation helper
def validate():
    missing = []
    if not API_KEY or API_KEY == "your_api_key_here":
        missing.append("GOOGLE_API_KEY")
    if not CX or CX == "your_custom_search_engine_id":
        missing.append("GOOGLE_CX")
    return missing
