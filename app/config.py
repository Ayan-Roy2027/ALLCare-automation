from dotenv import load_dotenv
from pathlib import Path
import os
env_path = Path(__file__).resolve().parent.parent/".env"
load_dotenv(dotenv_path=env_path)

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

if not GEMINI_API_KEY or GEMINI_API_KEY == 'your api key here':
    raise RuntimeError("There is no gemini api key given....")
