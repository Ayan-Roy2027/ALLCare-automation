import requests
from app.config import FACEBOOK_PAGE_ACCESS_TOKEN,FACEBOOK_PAGE_ID

API_VERSION = 'v26.0'

def post_photo(photo_url:str,caption:str) -> dict:
    response = requests.post(
        f"https://graph.facebook.com/{API_VERSION}/{FACEBOOK_PAGE_ID}/photos",
        data={
            "url" : photo_url,
            "caption" : caption,
            "access_token" : FACEBOOK_PAGE_ACCESS_TOKEN
        },
    )

    if response.status_code != 200:
        raise RuntimeError(
            f"Facebook post failed, ERROR CODE:{response.status_code}, text={response.text}"
        )
    
    return response.json()