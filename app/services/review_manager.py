from app.integrations.gemini_client import generate_review_reply
from app.integrations.gbp_client import get_unreplied_reviews, reply_to_review

DRY_RUN = False


def process_unreplied_reviews(account_location: str):
    unreplied = get_unreplied_reviews(account_location)

    if not unreplied:
        print("No reviews to reply to.")
        return

    print(f"Found {len(unreplied)} unreplied review(s).")

    for review in unreplied:
        reviewer_name = review.get("reviewer", {}).get("displayName", "Customer")
        rating = review.get("starRating", "UNKNOWN")
        review_text = review.get("comment", "")
        review_name = review.get("name")

        reply_text = generate_review_reply(reviewer_name, rating, review_text)

        if DRY_RUN:
            print("---")
            print(f"Reviewer: {reviewer_name} | Rating: {rating}")
            print(f"Review: {review_text}")
            print(f"Generated reply: {reply_text}")
        else:
            reply_to_review(review_name, reply_text)
            print(f"Replied to {reviewer_name}'s review.")


if __name__ == "__main__":
    account_location = "accounts/117897107069643471601/locations/5159737380424683697"
    process_unreplied_reviews(account_location)