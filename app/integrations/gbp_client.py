from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from app.config import GBP_CLIENT_SECRET_FILE, GBP_TOKEN_FILE

SCOPES = ["https://www.googleapis.com/auth/business.manage"]

def get_credentials():
    creds = None
    if GBP_TOKEN_FILE.exists():
        creds = Credentials.from_authorized_user_file(str(GBP_TOKEN_FILE),SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(str(GBP_CLIENT_SECRET_FILE), SCOPES)
            creds = flow.run_local_server(port=0)

        with open(GBP_TOKEN_FILE, "w") as token_file:
            token_file.write(creds.to_json())
    
    return creds

def get_location_profile(location_name: str) -> dict:
    creds = get_credentials()
    service = build("mybusinessbusinessinformation", "v1", credentials=creds)

    location = service.locations().get(
        name=location_name,
        readMask="title,storefrontAddress,phoneNumbers,websiteUri,categories"
    ).execute()

    # trim the noisy per-category metadata Google always includes
    categories = location.get("categories", {})
    clean_categories = {
        "primaryCategory": categories.get("primaryCategory", {}).get("displayName"),
        "additionalCategories": [
            c.get("displayName") for c in categories.get("additionalCategories", [])
        ],
    }
    location["categories"] = clean_categories

    return location


def list_local_posts(account_location: str) -> list[dict]:
    creds = get_credentials()
    service = build(
        "mybusiness", "v4",
        credentials=creds,
        static_discovery=False,
        discoveryServiceUrl="https://developers.google.com/my-business/samples/mybusiness_google_rest_v4p9.json",
    )

    result = service.accounts().locations().localPosts().list(
        parent=account_location
    ).execute()

    return result.get("localPosts", [])

def list_reviews(account_location: str) -> list[dict]:
    """
    account_location format: 'accounts/{account_id}/locations/{location_id}'
    """
    creds = get_credentials()
    service = build(
        "mybusiness", "v4",
        credentials=creds,
        static_discovery=False,
        discoveryServiceUrl="https://developers.google.com/my-business/samples/mybusiness_google_rest_v4p9.json",
    )

    result = service.accounts().locations().reviews().list(
        parent=account_location
    ).execute()

    return result.get("reviews", [])

def get_unreplied_reviews(account_location: str) -> list[dict]:
    all_reviews = list_reviews(account_location)
    return [r for r in all_reviews if "reviewReply" not in r]


def reply_to_review(review_name: str, reply_text: str) -> dict:
    """
    review_name: the full 'name' field from a review object,
    e.g. 'accounts/{id}/locations/{id}/reviews/{review_id}'
    """
    creds = get_credentials()
    service = build(
        "mybusiness", "v4",
        credentials=creds,
        static_discovery=False,
        discoveryServiceUrl="https://developers.google.com/my-business/samples/mybusiness_google_rest_v4p9.json",
    )

    result = service.accounts().locations().reviews().updateReply(
        name=review_name,
        body={"comment": reply_text}
    ).execute()

    return result


if __name__ == "__main__":
    creds = get_credentials()
    print("Auth OK, token valid:", creds.valid)

    location_name = "locations/5159737380424683697"
    profile = get_location_profile(location_name)
    print("PROFILE:", profile)

    account_location = "accounts/117897107069643471601/locations/5159737380424683697"


    import json
    unreplied = get_unreplied_reviews(account_location)
    if unreplied:
        print(json.dumps(unreplied[0], indent=2))
    unreplied = get_unreplied_reviews(account_location)