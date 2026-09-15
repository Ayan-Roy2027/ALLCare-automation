import json
import logging
from google import genai
from app.config import GEMINI_API_KEY
import logging 
from google.genai import types
from PIL import Image
from io import BytesIO


_client = genai.Client(api_key=GEMINI_API_KEY)

logger =  logging.getLogger(__name__)

MODEL_NAME = 'gemini-3.6-flash'



def generate_text(prompt:str)-> str:
    """
    Send a plain prompt to Gemini and return the raw text response.
    Used for things like SEO copy rewrites and review reply drafts.
    """
    
    if not prompt or not prompt.strip():
        raise ValueError('Prompt cannot be empty....')
    
    try:
        response = _client.models.generate_content(model=MODEL_NAME,contents=prompt)
        return response.text

    except Exception as e:
        logger.error(f"Gemini generation of text failed {e}")
        raise


def generate_json(prompt:str)->dict:
    """
    Send a prompt that instructs Gemini to return structured JSON, and
    parse it into a Python dict. Used for lead extraction, categorization, etc.
 
    Defensively strips markdown code fences, since the model sometimes
    wraps JSON output in ```json ... ``` even when told not to.
    """
    if not prompt or not prompt.strip():
        raise ValueError('Prompt cannot be empty...')

    json_instruction = (
        "\n\nReturn ONLY valid JSON. No markdown formatting, no code fences, "
        "no explanation text before or after the JSON."
    )

    full_prompt = prompt + json_instruction

    try:
        response = _client.models.generate_content(model=MODEL_NAME,contents=full_prompt)
        raw_text = response.text.strip()
    except Exception as e:
        logger.error(f'Gemini_json call failed {e}')
        raise

    # Defensive cleanup: strip ```json ... ``` or ``` ... ``` fences if present
    if raw_text.startswith("```"):
        raw_text = raw_text.strip("`")
        if raw_text.lower().startswith("json"):
            raw_text = raw_text[4:].strip()
    
    try:
        return json.loads(raw_text)
    
    except json.JSONDecodeError as e:
        logger.error(f'Failed to parse Gemini response as JSON: {e}\n Raw response: {raw_text}')
        raise ValueError(f'Gemini did not return valid response ". Raw response: {raw_text}') from e



def generate_review_reply(reviewer_name:str,rating:str,review_text:str) -> str:
    prompt = f"""
You are replying on behalf of Allcare Corporation, a leading security system and IT infrastructure supplier based in Kolkata, to a customer review on their Google Business Profile.

Review Details:

Reviewer Name: {reviewer_name}

Star Rating: {rating}

Review Text: "{review_text}"

Instructions:

Write a short, warm, and professional reply (2–4 sentences).

Address the reviewer by name.

If positive (4–5 stars): Thank them genuinely, reference what they mentioned if applicable, and naturally incorporate 1–2 subtle local SEO terms (e.g., "CCTV installation in Kolkata," "IT infrastructure solutions," "security system supplier in West Bengal," or "Kolkata tech support").

If negative or critical (1–3 stars): Acknowledge their concern sincerely without getting defensive or making excuses, mention our commitment to top-tier security and IT services in Kolkata, and invite them to reach out directly to make things right.

Do not invent fictional details (names, dates, prices) not found in the review.

ALSO TRY TO PROMOTE THESE PRODUCTS OF ALL CARE local seo
(Tally Installation,Printers and scanner installtion,CCTV Installation,Biometric Installation,Fire Alarm Installation,Epbex & Intercom Installtion,Networking,WIFI Installation,Server & Workstation Installtion,UPS Installtion,Desktop & laptop installtion)

Output ONLY the raw response text — no preamble, no meta-commentary, and no surrounding quotation marks.
"""
    return generate_text(prompt)





def generate_post_caption(services:list[str], pincodes: list[str]) -> str:

    prompt = f"""
You are writing a short Google Business Profile post for Allcare Corporation, a security
system and IT infrastructure supplier based in Kolkata, West Bengal.

Today's service focus: {f"add all the services somehow {services}"}
Service-area pincodes to reference naturally (do not list all of them, just weave in 1-2
relevant ones if it reads naturally, otherwise mention "West Bengal" generally): {pincodes}
also try to add near me keywords from random 5 pincode area names

Write a short, engaging post caption (5-10 sentences, under 2000 characters).
- Naturally mention relevant local SEO terms (Kolkata, West Bengal, the specific service).
- End with 3-5 relevant hashtags combining the service and location
  (e.g. #CCTVInstallationKolkata #ITSupportWestBengal) — do not claim they are "trending",
  just make them specific and locally relevant.
- Don't invent specific offers, prices, or claims not given to you.
- Output ONLY the caption text, no preamble, no quotation marks.
"""
    return generate_text(prompt)


def generate_picture(prompt: str) -> str:
    """Send prompt to Gemini, save the generated image, return its filename."""
    if not prompt:
        raise ValueError("Prompt cannot be empty....")

    client = genai.Client()
    response = client.models.generate_content(
        model="gemini-3.1-flash-image",
        contents=[prompt],
    )

    for part in response.candidates[0].content.parts:
        if part.inline_data is not None:
            image = Image.open(BytesIO(part.inline_data.data))
            filename = "nano_banana_post.png"
            image.save(filename)
            return filename

    raise RuntimeError("No image returned in Gemini response.")

if __name__ == "__main__":
    caption = generate_post_caption(services=SERVICES,pincodes=SERVICE_PINCODES)
    print(caption)