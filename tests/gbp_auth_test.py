from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
import json

SCOPES = ["https://www.googleapis.com/auth/business.manage"]
CLIENT_SECRET_FILE = "client_secret_833190832222-l6n0n5l01egbjslrfdvhid5mh6u17b99.apps.googleusercontent.com.json"

flow = InstalledAppFlow.from_client_secrets_file(CLIENT_SECRET_FILE,SCOPES)
creds = flow.run_local_server(port=0)

with open("gbp_token.json",'w') as token_file:
    token_file.write(creds.to_json())

account_service = build("mybusinessaccountmanagement","v1",credentials=creds)
accounts = account_service.accounts().list().execute()
print("ACCOUNTS:",json.dumps(accounts,indent=2))

account_id = "accounts/117897107069643471601"

location_service = build("mybusinessbusinessinformation", "v1", credentials=creds)
locations = location_service.accounts().locations().list(
    parent=account_id,
    readMask="name,title,storefrontAddress,phoneNumbers,categories"
).execute()
print("LOCATIONS:", json.dumps(locations, indent=2))