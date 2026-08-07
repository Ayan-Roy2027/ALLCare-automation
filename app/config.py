from dotenv import load_dotenv
from pathlib import Path
import os
env_path = Path(__file__).resolve().parent.parent/".env"
load_dotenv(dotenv_path=env_path)

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
WHATSAPP_TOKEN = os.getenv("WHATSAPP_TOKEN")
WHATSAPP_PHONE_NUMBER_ID = os.getenv("WHATSAPP_PHONE_NUMBER_ID")
WHATSAPP_BUSINESS_ACCOUNT_ID = os.getenv("WHATSAPP_BUSINESS_ACCOUNT_ID")
RECIPIENT_NUMBER = os.getenv("TEST_RECIPIENT_NUMBER")
SALES_TEAM_NUMBER = os.getenv('SALES_TEAM_NUMBER')
WHATSAPP_VERIFY_TOKEN = os.getenv('WHATSAPP_VERIFY_TOKEN')


if not GEMINI_API_KEY or GEMINI_API_KEY == 'your api key here':
    raise RuntimeError("There is no gemini api key given....")

if not WHATSAPP_TOKEN:
    raise RuntimeError("Error, no whatsapp token is given....")
if not WHATSAPP_BUSINESS_ACCOUNT_ID:
    raise RuntimeError("Error, no whatsapp business account id....")
if not RECIPIENT_NUMBER:
    raise RuntimeError('Error, no recipient number given....')
if not WHATSAPP_PHONE_NUMBER_ID:
    raise ValueError("Error, whatsapp phone number ID is not given...")
if not SALES_TEAM_NUMBER:
    raise ValueError("Error, no sales team number detected....")
if not WHATSAPP_VERIFY_TOKEN:
    raise ValueError("Error, no whatsapp verify token detected....")