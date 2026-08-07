from app.db.local_store import has_processed_message,mark_message_processed,get_lead_by_phone,insert_lead,update_lead_status,create_tables
from app.integrations.gemini_client import generate_json,generate_text
from app.models.schemas import Lead,LeadStatus
from app.integrations.whatsapp_client import send_text_message
from app.config import SALES_TEAM_NUMBER
def handle_incoming_message(phone: str, message_text: str , message_id : str):
    if has_processed_message(message_id):
        return 
    mark_message_processed(message_id)
    existing_lead = get_lead_by_phone(phone)

    if existing_lead is None:
        extraction_prompt = (
        "Extract the following fields from this customer message, and return as JSON "
        "with keys 'name', 'category', 'requirement', 'location'. "
        "If a field isn't mentioned, use null for that field.\n\n"
        f"Message: \"{message_text}\""
        )
        extracted_data = generate_json(extraction_prompt)
        if not extracted_data.get('requirement'):
            reply_prompt = (
            "You are a friendly sales assistant for Allcare Corporation, an IT infrastructure "
            "and electronic security provider in Kolkata (CCTV, biometrics, automation, IT support, "
            "deep cleaning). A customer sent this message, but it doesn't clearly state what they need. "
            "Reply warmly and ask what service they're looking for.\n\n"
            f"Customer message: \"{message_text}\""
    )
            reply_text = generate_text(reply_prompt)
            print("--- BOT REPLY (would be sent via WhatsApp) ---")
            print(reply_text)
            return 
        new_lead = Lead(
            phone=phone,
            name=extracted_data.get("name"),
            category = extracted_data.get('category'),
            requirement = extracted_data.get('requirement'),
            location = extracted_data.get("location")
        )
        new_lead=insert_lead(new_lead)
        alert_message = (
        f"🚨 New Hot Lead 🚨\n"
        f"Name: {new_lead.name}\n"
        f"Phone: {new_lead.phone}\n"
        f"Category: {new_lead.category}\n"
        f"Requirement: {new_lead.requirement}\n"
        f"Location: {new_lead.location}"
        )
        print("--- SALES ALERT (would be sent via WhatsApp) ---")
        print(alert_message)

        welcome_message = (
            f"Hi {new_lead.name or 'there'}, thanks for reaching out to Allcare! "
            f"We've received your request and our team will contact you shortly."
        )
        print("--- CUSTOMER WELCOME MESSAGE (would be sent via WhatsApp) ---")
        print(welcome_message)
        update_lead_status(lead_id=new_lead.lead_id,new_status=LeadStatus.BOT_ENGAGED)
    else:
        pass




if __name__ == "__main__":
    create_tables()
    print("=== Test 1: clear requirement — should create a lead ===")
    handle_incoming_message(
        phone="911111111111",
        message_text="Hi, I'm Ayan, I need a CCTV installation near Baguiati for my basement.",
        message_id="wamid.TEST001"
    )

    print("\n=== Test 2: vague message — should NOT create a lead, just reply ===")
    handle_incoming_message(
        phone="922222222222",
        message_text="Hi",
        message_id="wamid.TEST002"
    )
    # confirm no lead was created for this number
    from app.db.local_store import get_lead_by_phone
    result = get_lead_by_phone("922222222222")
    print(f"Lead created for vague message? {result is not None} (should be False)")

    print("\n=== Test 3: duplicate message ID — should do nothing at all ===")
    handle_incoming_message(
        phone="911111111111",
        message_text="Hi, I'm Ayan, I need a CCTV installation near Baguiati for my basement.",
        message_id="wamid.TEST003"  # same ID as Test 1
    )
    print("(nothing above this line should have printed for Test 3)")