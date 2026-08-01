import os
from app.config import WHATSAPP_TOKEN,WHATSAPP_BUSINESS_ACCOUNT_ID,RECIPIENT_NUMBER,WHATSAPP_PHONE_NUMBER_ID
import requests

API_VERSION = "v25.0"
BASE_URL = f"https://graph.facebook.com/{API_VERSION}/{WHATSAPP_PHONE_NUMBER_ID}/messages"

def send_template_message(to: str=RECIPIENT_NUMBER,template_name:str='Hello_world',language_code:str ='en_US')->dict:
    """
    Send a pre-approved WhatsApp template message.
    Required for the FIRST message in a conversation (welcome messages, sales alerts, etc.)
    since WhatsApp doesn't allow free-form business-initiated messages.
 
    to: recipient number in international format, no '+', e.g. '919876543210'
    """
    if not to or not to.strip():
        raise ValueError('Recipient number cannot be empty...')
    
    headers = {
        "Authorization": f"Bearer {WHATSAPP_TOKEN}",
        "Content-Type" :  "application/json"
    }

    payload = {
        "messaging_product" : "whatsapp",
        "to" : to,
        "type" : "template",
        "template" : {
            "name" : template_name,
            "language" : {"code":language_code},
        },
    }

    response = requests.post(url=BASE_URL,headers=headers,json=payload)

    if response.status_code != 200:
        raise RuntimeError(f'Whatsapp API failed , ERROR CODE:{response.status_code},text={response.text}')
    
    return response.json()

def send_text_message(to:str,body:str)->dict:
    """
    Send a free-form text message.
    Only works WITHIN the 24-hour window after the user has messaged you first —
    used for the chatbot's ongoing replies, not the initial outbound message.
    """
    if not body or not body.strip():
        raise ValueError("Message body cannot be empty")
    if not to or not to.strip():
        print("Recipient number cannot be empty....")
    
    headers = {
        "Authorization": f"Bearer {WHATSAPP_TOKEN}",
        "Content-Type" :  "application/json"
    }

    payload = {
        "messaging_product": "whatsapp",
        "to": to,
        "type": "text",
        "text": {"body": body},
    }

    response = requests.post(url=BASE_URL,headers=headers,json=payload)

    if response.status_code != 200:
        raise RuntimeError(f'Whatsapp API failed , Error code : {response.status_code},text:{response.text}')

    return response.json()


