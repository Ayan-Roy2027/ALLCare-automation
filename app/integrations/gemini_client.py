import json
import logging
from google import genai
import app.config
import logging 

_client = genai.Client()

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



if __name__ == "__main__":
    # Quick standalone test — run with: python -m app.integrations.gemini_client
    logging.basicConfig(level=logging.INFO)
 
    print("--- Test 1: plain text generation ---")
    text_result = generate_text("Write a direct reply to this review. Output only the final reply text and nothing else.Review=All Care Corporation theke amar bari-te CCTV camera installation korano hoyeche.Kaaj khub poripati, wiring clean ebong camera quality excellent.Time-to-time kaaj shesh koreche ebong behaviour khub bhalo.")
    print(text_result)
 
    print("\n--- Test 2: structured JSON extraction ---")
    extraction_prompt = (
        "Extract the customer's name and neighborhood from this message, "
        "and return as JSON with keys 'name','location','service_required'and 'date',if something is not present return none to that value:\n\n"
        "\"Hi I'm Amit, I live near Garia and need a CCTV setup.\""
    )
    json_result = generate_json(extraction_prompt)
    print(json_result)
    print(f"Type check: {type(json_result)}")  # should be <class 'dict'>