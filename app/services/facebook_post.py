from app.integrations.facebook_client import post_photo
from app.integrations.gemini_client import generate_post_caption
from app.integrations.instagram_client import post_photo as pic_post

# use a real image URL first — either a working imgbb link from an earlier
# upload test, or any public image URL, just to confirm the call works
test_photo_url = "https://i.ibb.co/CshwZ6hf/454acf2494d7.png"
test_caption = generate_post_caption()

# result = post_photo(test_photo_url, test_caption)
# print("Posted:", result)

result = pic_post(test_photo_url,test_caption)
print(result)