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


if __name__ == "__main__":
    # Fake payload mimicking a real WhatsApp text message webhook
    fake_payload = {
        "entry": [
            {
                "changes": [
                    {
                        "value": {
                            "messages": [
                                {
                                    "from": "919876543210",
                                    "id": "wamid.TESTID123",
                                    "timestamp": "1735000000",
                                    "text": {"body": "Hi I need a CCTV installed in Garia"},
                                    "type": "text"
                                }
                            ]
                        }
                    }
                ]
            }
        ]
    }

    print("--- Test 1: valid text message payload ---")
    result = extract_message_data(fake_payload)
    print(result)
    assert result is not None
    assert result["from"] == "919876543210"
    assert result["body"] == "Hi I need a CCTV installed in Garia"
    assert result["type"] == "text"
    print("PASSED\n")

    print("--- Test 2: malformed/status-update payload ---")
    fake_status_payload = {
        "entry": [
            {
                "changes": [
                    {
                        "value": {
                            "statuses": [  # no "messages" key here
                                {"id": "wamid.TESTID456", "status": "delivered"}
                            ]
                        }
                    }
                ]
            }
        ]
    }
    result2 = extract_message_data(fake_status_payload)
    print(result2)
    assert result2 is None
    print("PASSED\n")

    print("--- Test 3: completely empty payload ---")
    result3 = extract_message_data({})
    print(result3)
    assert result3 is None
    print("PASSED\n")

    print("All whatsapp_webhook extraction tests passed.")
        