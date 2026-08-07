payload ={
  "entry": [
    {
      "changes": [
        {
          "value": {
            "messages": [
              {
                "from": "919876543210",
                "id": "wamid.HBgLMTIzNDU2Nzg5MAoAERgS...",
                "timestamp": "1735000000",
                "text": {
                  "body": "Hi I need a CCTV installed"
                },
                "type": "text"
              }
            ]
          }
        }
      ]
    }
  ]
}


message = payload['entry'][0]['changes'][0]['value']['messages'][0]

frm = message['type']
print(frm)

a = dict()
a['id'] = frm
print(a['id'])