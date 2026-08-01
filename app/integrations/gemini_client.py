import json
import logging
from google import genai
from app.config import GEMINI_API_KEY
import logging 

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



