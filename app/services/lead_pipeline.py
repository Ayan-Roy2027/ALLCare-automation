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










# if __name__ == "__main__":
#     create_tables()

#     print("=== Setup: create an active lead to assign ===")
#     handle_incoming_message(
#         phone="944444444444",
#         message_text="Hi, I'm Sneha, I need deep cleaning for my 3BHK in New Town.",
#         message_id="wamid.TESTS001"
#     )

#     print("\n=== Test A: sales replies TAKEN <valid phone> — should assign to human ===")
#     handle_sales_reply(
#         sender_phone="919000000000",  # sales team's own number
#         message_text="TAKEN 944444444444",
#         message_id="wamid.TESTS002"
#     )
#     active = get_active_lead("944444444444")
#     print(f"Lead status after assignment: {active.status} (should be human_assigned)")
#     assert active.status == LeadStatus.HUMAN_ASSIGNED
#     print("PASSED\n")

#     print("=== Test B: sales replies TAKEN <phone with no active lead> — should not crash ===")
#     handle_sales_reply(
#         sender_phone="919000000000",
#         message_text="TAKEN 999999999999",
#         message_id="wamid.TESTS003"
#     )
#     print("PASSED (no crash, printed 'no active lead' message above)\n")

#     print("=== Test C: sales replies just TAKEN with nothing after it — should not crash ===")
#     handle_sales_reply(
#         sender_phone="919000000000",
#         message_text="TAKEN",
#         message_id="wamid.TESTS004"
#     )
#     print("PASSED (no crash, nothing printed above)\n")

#     print("=== Test D: customer messages after HUMAN_ASSIGNED — bot should stay silent ===")
#     handle_incoming_message(
#         phone="944444444444",
#         message_text="Hello? Anyone there?",
#         message_id="wamid.TESTS005"
#     )
#     print("(nothing above this line should have printed for Test D)\n")

#     print("All handle_sales_reply tests passed.")






# if __name__ == "__main__":
#     create_tables()

#     print("=== Test 1: clear requirement — should create a lead ===")
#     handle_incoming_message(
#         phone="933333333333",
#         message_text="Hi, I'm Ayan, I need a CCTV installation near Baguiati for my basement.",
#         message_id="wamid.TESTA001"
#     )

#     print("\n=== Test 2: follow-up message on the SAME phone — should trigger BOT_ENGAGED reply ===")
#     handle_incoming_message(
#         phone="933333333333",
#         message_text="How much would that roughly cost?",
#         message_id="wamid.TESTA002"
#     )

#     print("\n=== Test 3: same phone, but simulate HUMAN_ASSIGNED — should stay silent ===")
#     from app.db.local_store import get_all_leads_by_phone
#     leads = get_all_leads_by_phone("933333333333")
#     update_lead_status(lead_id=leads[0].lead_id, new_status=LeadStatus.HUMAN_ASSIGNED)
#     handle_incoming_message(
#         phone="933333333333",
#         message_text="Are you still there?",
#         message_id="wamid.TESTA003"
#     )
#     print("(nothing above this line should have printed for Test 3)")


