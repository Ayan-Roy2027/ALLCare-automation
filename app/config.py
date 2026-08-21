from dotenv import load_dotenv
from pathlib import Path
import os
env_path = Path(__file__).resolve().parent.parent/".env"
load_dotenv(dotenv_path=env_path)

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
GBP_CLIENT_SECRET_FILE = os.getenv("GBP_CLIENT_SECRET_FILE")
GBP_TOKEN_FILE = os.getenv("GBP_TOKEN_FILE")


if not GEMINI_API_KEY or GEMINI_API_KEY == 'your api key here':
    raise RuntimeError("There is no gemini api key given....")

if not GBP_CLIENT_SECRET_FILE:
    raise RuntimeError("GBP_CLIENT_SECRET_FILE is not set in .env")
GBP_CLIENT_SECRET_FILE = Path(GBP_CLIENT_SECRET_FILE)

if not GBP_TOKEN_FILE:
    raise RuntimeError("GBP_TOKEN_FILE is not set in .env")
GBP_TOKEN_FILE = Path(GBP_TOKEN_FILE)
