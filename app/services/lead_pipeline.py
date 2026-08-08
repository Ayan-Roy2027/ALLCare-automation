from app.db.local_store import has_processed_message,mark_message_processed,get_all_leads_by_phone,insert_lead,update_lead_status,create_tables
from app.integrations.gemini_client import generate_json,generate_text
from app.models.schemas import Lead,LeadStatus
from app.integrations.whatsapp_client import send_text_message
from app.config import SALES_TEAM_NUMBER

def get_active_lead(phone: str) -> Lead | None:
    all_leads = get_all_leads_by_phone(phone)
    for lead in all_leads:
        if lead.status != LeadStatus.CLOSED:
            return lead
    return None


def handle_incoming_message(phone: str, message_text: str , message_id : str):
    if has_processed_message(message_id):
        return 
    mark_message_processed(message_id)
    existing_lead = get_active_lead(phone)

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
        if existing_lead.status == LeadStatus.HUMAN_ASSIGNED:
            return
        
        if existing_lead.status == LeadStatus.BOT_ENGAGED:
            ongoing_reply_prompt = (
        "You are a friendly sales assistant for Allcare Corporation, an IT infrastructure "
        "and electronic security provider in Kolkata (CCTV, biometrics, automation, IT support, "
        "deep cleaning). You're in an ongoing WhatsApp conversation with a customer who already "
        "reached out about the following:\n"
        f"- Category: {existing_lead.category or 'not specified'}\n"
        f"- Requirement: {existing_lead.requirement or 'not specified'}\n"
        f"- Location: {existing_lead.location or 'not specified'}\n\n"
        "Our sales team has been notified and will contact them soon. The customer just sent "
        "a follow-up message. Reply warmly and helpfully, answering their question if you can "
        "based on what they've told us so far. If you don't have enough information to answer "
        "confidently (e.g. pricing, exact timing), let them know the sales team will confirm "
        "those details shortly rather than guessing.\n\n"
        f"Customer's new message: \"{message_text}\""
    )
            reply_text = generate_text(ongoing_reply_prompt)
            print("--- BOT REPLY (would be sent via WhatsApp) ---")
            print(reply_text)
            return


def handle_sales_reply(sender_phone: str,message_text:str,message_id:str):

    """IT ASSIGNS A HUMAN TO A LEAD WHEN CALLED WHILE A SALES PERSON MESSAGES
    WITH "TAKEN 91XXXXXXXX" """
    if has_processed_message(message_id):
        return
    mark_message_processed(message_id)
    
    if not message_text.strip().upper().startswith("TAKEN"):
        return
    
    message = message_text.strip()
    part = message.split()
    try:
        customer_phone = part[1]
    except IndexError:
        return
    active_lead = get_active_lead(phone=customer_phone)
    if active_lead is None:
        print(f"No active lead is found for {customer_phone}- nothing to assign")
        return
    
    update_lead_status(lead_id=active_lead.lead_id,new_status=LeadStatus.HUMAN_ASSIGNED)
    print("WHATSAPP MESSAGE")
    print(f"{customer_phone} is assgined to {sender_phone}....")
