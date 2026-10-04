import json
import logging
from google import genai
from app.config import GEMINI_API_KEY
import logging 
from google.genai import types
from PIL import Image
from io import BytesIO
import base64


_client = genai.Client(api_key=GEMINI_API_KEY)

logger =  logging.getLogger(__name__)

MODEL_NAME = 'gemini-3.6-flash'

logo = "logo.png"

with open(logo, "rb") as f:
        image_b64 = base64.b64encode(f.read()).decode()
SERVICES = [
    "Tally Installation",
    "Printers and Scanner Installation",
    "CCTV Installation",
    "Biometric Installation",
    "Fire Alarm Installation",
    "EPBX & Intercom Installation",
    "Networking",
    "WiFi Installation",
    "Server & Workstation Installation",
    "UPS Installation",
    "Desktop & Laptop Installation",
]
SERVICE_PINCODES = [
    "700001", "700002", "700003", "700004", "700005", "700006", "700007", "700008", "700009", "700010",
    "700011", "700012", "700013", "700014", "700015", "700016", "700017", "700018", "700019", "700020",
    "700021", "700022", "700023", "700024", "700025", "700026", "700027", "700028", "700029", "700030",
    "700031", "700032", "700033", "700034", "700035", "700036", "700037", "700038", "700039", "700040",
    "700041", "700042", "700043", "700044", "700045", "700046", "700047", "700048", "700049", "700050",
    "700051", "700052", "700053", "700054", "700055", "700056", "700057", "700058", "700059", "700060",
    "700061", "700062", "700063", "700064", "700065", "700066", "700067", "700068", "700069", "700070",
    "700071", "700072", "700073", "700074", "700075", "700076", "700077", "700078", "700079", "700080",
    "700081", "700082", "700083", "700084", "700085", "700086", "700087", "700088", "700089", "700090",
    "700091", "700092", "700093", "700094", "700095", "700096", "700097", "700098", "700099", "700100",
    "700101", "700102", "700103", "700104", "700105", "700106", "700107", "700108", "700109", "700110",
    "700111", "700112", "700113", "700114", "700115", "700116", "700117", "700118", "700119", "700120",
    "700121", "700122", "700123", "700124", "700125", "700126", "700127", "700128", "700129", "700130",
    "700131", "700132", "700133", "700134", "700135", "700136", "700137", "700048", "700055", "700056",
    "700059", "700064", "700089", "700091", "700097", "700098", "700101", "700102", "700103", "700104",
    "700105", "700106", "700110", "700113", "700119", "700120", "700121", "700122", "700123", "700124",
    "700125", "700126", "700127", "700128", "700129", "700130", "700131", "700132", "700133", "700135",
    "700136", "700137", "700138", "700139", "700140", "700141", "700142", "700143", "700144", "700145",
    "700146", "700148", "700149", "700150", "700151", "700152", "700153", "700154", "700155", "700156",
    "700157", "711101", "711102", "711103", "711104", "711105", "711106", "711107", "711108", "711109",
    "711110", "711111", "711112", "711113", "711114", "711115", "711201", "711202", "711203", "711204",
    "711205", "711206", "712101", "712102", "712103", "712104", "712105", "712121", "712123", "712124",
    "712125", "712136", "712137", "712138", "712139", "712201", "712202", "712203", "712204", "712221",
    "712222", "712223", "712232", "712233", "712234", "712235", "712245", "712246", "712247", "712248",
    "712249", "712250", "712258", "712310", "712311", "712502", "712503", "743122", "743123", "743124",
    "743125", "743126", "743127", "743128", "743129", "743130", "743133", "743134", "743135", "743136",
    "743144", "743145", "743165", "743166", "743193", "743194", "743221", "743222", "743223", "743232",
    "743233", "743234", "743235", "743244", "743245", "743247", "743248", "743249", "743251", "743252",
    "743262", "743263", "743268", "743269", "743270", "743271", "743272", "743273", "743274", "743276",
    "743286", "743287", "743288", "743289", "743290", "743291", "743292", "743293", "743294", "743295"
]

pic_prompt = f"""
Square 1:1 commercial marketing poster for "ALL CARE CORPORATION". Logo = {image_b64}.
VISUALS: A sleek tech desk in a polished server room with a softly blurred corporate office background. On the desk, display ultra-realistic 3D IT hardware: a laptop (showing Tally software), enterprise WiFi router, biometric reader, dome CCTV camera, multi-function printer, tower server with dual monitors, smoke detector, digital desk phone, and a UPS unit. 
STYLING: Professional corporate blue, crisp white, and dark metallic grey accents. Photorealistic studio lighting, sharp detail, high-resolution flyer quality.
TEXT OVERLAY: (Clean, high-contrast, professional typography)
- Header: ALL CARE CORPORATION - Your Trusted IT & Automation Partner
- Main Title: IT Infra & Automation Solutions
- Services (2-column grid with realistic icons): Tally | Printers & Scanners | CCTV | Biometric | Fire Alarm | EPBX Intercom | Networking | WiFi | Servers & Workstations | UPS | Desktop & Laptop Installations
- CTA: Upgrade & Secure Your Business Infrastructure Today!
- Footer: Call Us: +91 98362 13939 | Website: https://allcareitinfra.com/
"""

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





def generate_post_caption(services=SERVICES, pincodes= SERVICE_PINCODES) -> str:

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


def generate_picture(prompt: str):
    """Send prompt to Gemini, save the generated image, return its filename."""
    if not prompt:
        raise ValueError("Prompt cannot be empty....")

    client = genai.Client()
    response = client.models.generate_content(
        model="gemini-3.1-flash-lite-image",
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
    generate_picture(prompt=pic_prompt)