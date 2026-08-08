import os
import pytest

from app.db import local_store
from app.models.schemas import Lead, LeadStatus
from app.services.lead_pipeline import (
    get_active_lead,
    handle_incoming_message,
    handle_sales_reply,
)


@pytest.fixture(autouse=True)
def clean_db():
    if local_store.DB_PATH.exists():
        os.remove(local_store.DB_PATH)
    local_store.create_tables()
    yield
    if local_store.DB_PATH.exists():
        os.remove(local_store.DB_PATH)


# ---------- handle_incoming_message ----------

@pytest.mark.integration
def test_new_message_with_clear_requirement_creates_lead():
    handle_incoming_message(
        phone="911111111101",
        message_text="Hi, I need IT support for my office in Kolkata",
        message_id="wamid.test001",
    )

    lead = get_active_lead("911111111101")
    assert lead is not None
    assert lead.status == LeadStatus.BOT_ENGAGED


@pytest.mark.integration
def test_new_message_with_vague_text_creates_no_lead():
    handle_incoming_message(
        phone="911111111102",
        message_text="hello",
        message_id="wamid.test002",
    )

    lead = get_active_lead("911111111102")
    assert lead is None


def test_duplicate_message_id_is_a_no_op():
    local_store.mark_message_processed("wamid.test003")

    # if this weren't idempotent, it would try to hit Gemini and could
    # create a lead / raise on quota — instead it should return immediately
    handle_incoming_message(
        phone="911111111103",
        message_text="I need help with SEO",
        message_id="wamid.test003",
    )

    lead = get_active_lead("911111111103")
    assert lead is None


@pytest.mark.integration
def test_followup_message_on_bot_engaged_lead_does_not_create_new_lead():
    existing = Lead(
        phone="911111111104",
        name="Test User",
        category="IT Support",
        status=LeadStatus.BOT_ENGAGED,
    )
    local_store.insert_lead(existing)

    handle_incoming_message(
        phone="911111111104",
        message_text="What are your rates?",
        message_id="wamid.test004",
    )

    leads = local_store.get_all_leads_by_phone("911111111104")
    assert len(leads) == 1  # still only the one lead, no duplicate created
    assert leads[0].status == LeadStatus.BOT_ENGAGED


def test_message_on_human_assigned_lead_is_ignored():
    existing = Lead(
        phone="911111111105",
        name="Test User",
        category="IT Support",
        status=LeadStatus.HUMAN_ASSIGNED,
    )
    local_store.insert_lead(existing)

    # should silently return — no Gemini call, no new lead, no status change
    handle_incoming_message(
        phone="911111111105",
        message_text="Any update?",
        message_id="wamid.test005",
    )

    leads = local_store.get_all_leads_by_phone("911111111105")
    assert len(leads) == 1
    assert leads[0].status == LeadStatus.HUMAN_ASSIGNED


# ---------- handle_sales_reply ----------

def test_valid_taken_reply_assigns_lead_to_human():
    lead = Lead(phone="911111111106", name="Test User", category="IT Support")
    inserted = local_store.insert_lead(lead)

    handle_sales_reply(
        sender_phone="SALES_TEAM_NUMBER",
        message_text=f"TAKEN 911111111106",
        message_id="wamid.test006",
    )

    active = get_active_lead("911111111106")
    assert active is not None
    assert active.status == LeadStatus.HUMAN_ASSIGNED


def test_malformed_taken_reply_does_not_crash():
    lead = Lead(phone="911111111107", name="Test User", category="IT Support")
    local_store.insert_lead(lead)

    # "TAKEN" with no phone after it — should hit the IndexError guard, not raise
    handle_sales_reply(
        sender_phone="SALES_TEAM_NUMBER",
        message_text="TAKEN",
        message_id="wamid.test007",
    )

    active = get_active_lead("911111111107")
    assert active.status == LeadStatus.NEW  # unchanged


def test_taken_reply_for_phone_with_no_active_lead_is_a_no_op():
    # no lead exists for this phone at all
    handle_sales_reply(
        sender_phone="SALES_TEAM_NUMBER",
        message_text="TAKEN 911111111108",
        message_id="wamid.test008",
    )

    active = get_active_lead("911111111108")
    assert active is None  # nothing to update, nothing crashes


def test_duplicate_sales_reply_message_id_is_a_no_op():
    lead = Lead(phone="911111111109", name="Test User", category="IT Support")
    local_store.insert_lead(lead)
    local_store.mark_message_processed("wamid.test009")

    handle_sales_reply(
        sender_phone="SALES_TEAM_NUMBER",
        message_text="TAKEN 911111111109",
        message_id="wamid.test009",
    )

    active = get_active_lead("911111111109")
    assert active.status == LeadStatus.NEW  # never processed, so never assigned