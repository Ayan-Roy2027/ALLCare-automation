import requests
from app.config import FACEBOOK_PAGE_ACCESS_TOKEN,INSTAGRAM_BUSINESS_ACCOUNT_ID

API_VERSION = "v26.0"

def post_photo(photo_url:str,caption:str) -> dict:
    container_response=requests.post(
        f"https://graph.facebook.com/{API_VERSION}/{INSTAGRAM_BUSINESS_ACCOUNT_ID}/media",
        data={
            "image_url": photo_url,
            "caption" : caption,
            "access_token" : FACEBOOK_PAGE_ACCESS_TOKEN
        },
    )

    if container_response.status_code != 200:
        raise RuntimeError(
            f"Instagram container creation failed, ERROR CODE:{container_response.status_code}, "
            f"text={container_response.text}"
        )

    creation_id = container_response.json()["id"]

    publish_response = requests.post(
        f"https://graph.facebook.com/{API_VERSION}/{INSTAGRAM_BUSINESS_ACCOUNT_ID}/media_publish",
        data ={
            "creation_id" : creation_id,
            "access_token" : FACEBOOK_PAGE_ACCESS_TOKEN
        },
    )

    if publish_response.status_code != 200:
        raise RuntimeError(
            f"Instagram publish failed, ERROR CODE:{publish_response.status_code}, "
            f"text={publish_response.text}"
        )

    return publish_response.json()