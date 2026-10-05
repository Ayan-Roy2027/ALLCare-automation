import random
from datetime import datetime, timedelta
from pathlib import Path
from google.cloud import storage         

from app.services.review_manager import process_unreplied_reviews
from app.integrations.gemini_client import (
    generate_post_caption1,
    generate_post_caption2,
    generate_picture,
    pic_prompt1,
    pic_prompt2,
    SERVICES,
)
from app.integrations.img_bb_client import upload_image_and_get_url
from app.integrations.gbp_client import create_local_post
from app.integrations.facebook_client import post_photo as post_to_facebook
from app.integrations.instagram_client import post_photo as post_to_instagram
from app.services.seo_audit import run_seo_audit

DRY_RUN = False
  

ACCOUNT_LOCATION = "accounts/117897107069643471601/locations/5159737380424683697"
LOCATION_NAME = "locations/5159737380424683697"

AUDIT_STATE_FILE = Path(__file__).parent / "data" / "last_seo_audit.txt"

BUCKET_NAME = "allcare-automation-state"
SYNCED_FILES = ["app/db/allcare.db", "app/data/last_seo_audit.txt", "gbp_token.json"]


def download_state():
    client = storage.Client()
    bucket = client.bucket(BUCKET_NAME)
    for filepath in SYNCED_FILES:
        blob = bucket.blob(filepath)
        if blob.exists():
            Path(filepath).parent.mkdir(parents=True, exist_ok=True)
            blob.download_to_filename(filepath)


def upload_state():
    client = storage.Client()
    bucket = client.bucket(BUCKET_NAME)
    for filepath in SYNCED_FILES:
        if Path(filepath).exists():
            bucket.blob(filepath).upload_from_filename(filepath)


def should_run_weekly_audit() -> bool:
    if not AUDIT_STATE_FILE.exists():
        return True
    try:
        last_run = datetime.fromisoformat(AUDIT_STATE_FILE.read_text().strip())
    except ValueError:
        return True
    return datetime.now() - last_run >= timedelta(days=7)


def mark_audit_ran():
    AUDIT_STATE_FILE.parent.mkdir(parents=True, exist_ok=True)
    AUDIT_STATE_FILE.write_text(datetime.now().isoformat())


def generate_todays_content():
    is_special_day = datetime.now().weekday() in (5, 2)  # 5=Saturday, 2=Wednesday

    if is_special_day:
        print("Today is Saturday/Wednesday — generating all-services content.")
        caption = generate_post_caption1(services=SERVICES)
        local_filename = generate_picture(pic_prompt1)
    else:
        service = random.choice(SERVICES)
        print(f"Today's focus service: {service}")
        caption = generate_post_caption2(service=service)
        local_filename = generate_picture(pic_prompt2(service))

    return caption, local_filename


def post_everywhere(caption: str, photo_url: str):
    if DRY_RUN:
        print("DRY RUN — would post this caption + image to GMB, Facebook, Instagram:")
        print(f"Caption: {caption}")
        print(f"Photo URL: {photo_url}")
        return

    try:
        result = create_local_post(ACCOUNT_LOCATION, caption, photo_url)
        print(f"GMB posted. ID: {result.get('name')}")
    except Exception as e:
        print(f"GMB post failed: {e}")

    try:
        result = post_to_facebook(photo_url, caption)
        print(f"Facebook posted. ID: {result.get('id')}")
    except Exception as e:
        print(f"Facebook post failed: {e}")

    try:
        result = post_to_instagram(photo_url, caption)
        print(f"Instagram posted. ID: {result.get('id')}")
    except Exception as e:
        print(f"Instagram post failed: {e}")


def main():
    download_state()
    print("=== Step 1: Reviews ===")
    process_unreplied_reviews(ACCOUNT_LOCATION)  # prints its own "No reviews to reply to." if empty

    print("\n=== Step 2: Daily content ===")
    caption, local_filename = generate_todays_content()
    photo_url = upload_image_and_get_url(local_filename)
    print(f"Image uploaded: {photo_url}")
    post_everywhere(caption, photo_url)

    print("\n=== Step 3: Weekly SEO audit ===")
    if should_run_weekly_audit():
        run_seo_audit(LOCATION_NAME)
        mark_audit_ran()
    else:
        print("SEO audit not due yet (runs once every 7 days).")

    print("\n=== Done for today ===")
    upload_state()

if __name__ == "__main__":
    main()