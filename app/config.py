from dotenv import load_dotenv
from pathlib import Path
import os
env_path = Path(__file__).resolve().parent.parent/".env"
load_dotenv(dotenv_path=env_path)

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
GBP_CLIENT_SECRET_FILE = os.getenv("GBP_CLIENT_SECRET_FILE")
GBP_TOKEN_FILE = os.getenv("GBP_TOKEN_FILE")
IMG_BB_API_KEY = os.getenv("IMG_BB_API_KEY")
FACEBOOK_PAGE_ACCESS_TOKEN = os.getenv("FACEBOOK_PAGE_ACCESS_TOKEN")
FACEBOOK_PAGE_ID = os.getenv("FACEBOOK_PAGE_ID")
INSTAGRAM_BUSINESS_ACCOUNT_ID = os.getenv("INSTAGRAM_BUSINESS_ACCOUNT_ID")

if not GEMINI_API_KEY or GEMINI_API_KEY == 'your api key here':
    raise RuntimeError("There is no gemini api key given....")

if not GBP_CLIENT_SECRET_FILE:
    raise RuntimeError("GBP_CLIENT_SECRET_FILE is not set in .env")
GBP_CLIENT_SECRET_FILE = Path(GBP_CLIENT_SECRET_FILE)

if not GBP_TOKEN_FILE:
    raise RuntimeError("GBP_TOKEN_FILE is not set in .env")
GBP_TOKEN_FILE = Path(GBP_TOKEN_FILE)

if not IMG_BB_API_KEY:
    raise RuntimeError("IMG_BB is not set in .env")
IMG_BB_API_KEY=Path(IMG_BB_API_KEY)

if not FACEBOOK_PAGE_ACCESS_TOKEN:
    raise RuntimeError("FACEBOOK_PAGE_ACCESS_TOKEN is not set in .env")
FACEBOOK_PAGE_ACCESS_TOKEN = Path(FACEBOOK_PAGE_ACCESS_TOKEN)

if not FACEBOOK_PAGE_ID:
    raise RuntimeError("FACEBOOK_PAGE_ID is not set in .env")
FACEBOOK_PAGE_ID = Path(FACEBOOK_PAGE_ID)

if not INSTAGRAM_BUSINESS_ACCOUNT_ID:
    raise RuntimeError("INSTAGRAM_BUSINESS_ACCOUNT_ID is not set in .env")
INSTAGRAM_BUSINESS_ACCOUNT_ID = Path(INSTAGRAM_BUSINESS_ACCOUNT_ID)