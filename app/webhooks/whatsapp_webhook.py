from fastapi import APIRouter, Request, HTTPException
from app.config import WHATSAPP_VERIFY_TOKEN, SALES_TEAM_NUMBER
from app.services.lead_pipeline import handle_incoming_message, handle_sales_reply

router = APIRouter()

def extract_message_data(payload : dict) -> dict | None:
    """
    Pulls phone number, message ID, and text out of a raw WhatsApp webhook payload.
    Returns None if this payload isn't a text message (e.g. it's a status update).
    """
    try:
        data = {}
        message = payload['entry'][0]['changes'][0]['value']['messages'][0]
        data['from'] = message['from']
        data['id']= message['id']
        data['timestamp'] = message['timestamp']
        data['body'] = message['text']['body']
        data['type'] =  message['type']
        return data
    except(KeyError,IndexError):
        return None

@router.get("/webhooks/whatsapp")
async def verify_webhook(request: Request):
    mode = request.query_params.get("hub.mode")
    token = request.query_params.get("hub.verify_token")
    challenge = request.query_params.get("hub.challenge")

    if mode == "subscribe" and token == WHATSAPP_VERIFY_TOKEN:
        return int(challenge)
    
    raise HTTPException(status_code=403,detail='Verification failed...')

@router.post("/webhooks/whatsapp")
async def receive_whatsapp_message(request : Request):
    payload = await request.json()
    data = extract_message_data(payload)

    if data is None:
        return {"status": "ignored"}
    
    sender_phone = data['from']
    message_id = data['id']
    message_text = data['body']

    if sender_phone == SALES_TEAM_NUMBER :
        handle_sales_reply(sender_phone,message_text,message_id)
    else:
        handle_incoming_message(sender_phone,message_text,message_id)
    
    return {"status":"recieved"}










