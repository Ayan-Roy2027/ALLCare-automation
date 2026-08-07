from typing import Dict
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


