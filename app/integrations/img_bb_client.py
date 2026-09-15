import base64
import requests

from app.config import IMG_BB_API_KEY


def upload_image_and_get_url(local_filename: str) -> str:
    with open(local_filename, "rb") as f:
        image_b64 = base64.b64encode(f.read()).decode()

    response = requests.post(
        "https://api.imgbb.com/1/upload",
        data={"key": IMG_BB_API_KEY, "image": image_b64},
    )

    if response.status_code != 200:
        raise RuntimeError(
            f"ImgBB upload failed, ERROR CODE:{response.status_code}, text={response.text}"
        )

    return response.json()["data"]["url"]


if __name__ == "__main__":
    # confirm you have a real generated image sitting around first
    url = upload_image_and_get_url("teest.png")
    print("Uploaded:", url)