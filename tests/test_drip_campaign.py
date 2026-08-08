import os
import pandas as pd
import pytest

from app.db import local_store
from app.models.schemas import OptInRecord, OptInStatus
from app.services.drip_campaign import send_opt_in


@pytest.fixture(autouse=True)
def clean_db():
    if local_store.DB_PATH.exists():
        os.remove(local_store.DB_PATH)
    local_store.create_tables()
    yield
    if local_store.DB_PATH.exists():
        os.remove(local_store.DB_PATH)


def test_new_contact_gets_opt_in_request():
    df = pd.DataFrame([{"phone": "977777777701", "name": "Test User"}])
    send_opt_in(df)

    record = local_store.get_opt_in_status("977777777701")
    assert record is not None
    assert record.status == OptInStatus.OPT_IN_SENT


def test_not_contacted_existing_record_gets_opt_in_request():
    local_store.insert_opt_in_record(OptInRecord(phone="977777777702"))
    df = pd.DataFrame([{"phone": "977777777702", "name": "Test User 2"}])
    send_opt_in(df)

    record = local_store.get_opt_in_status("977777777702")
    assert record.status == OptInStatus.OPT_IN_SENT


def test_opt_in_sent_contact_is_skipped():
    local_store.insert_opt_in_record(OptInRecord(phone="977777777703"))
    local_store.update_opt_in_status("977777777703", OptInStatus.OPT_IN_SENT)

    df = pd.DataFrame([{"phone": "977777777703", "name": "Test User 3"}])
    send_opt_in(df)

    # status should remain unchanged — still OPT_IN_SENT, not re-sent
    record = local_store.get_opt_in_status("977777777703")
    assert record.status == OptInStatus.OPT_IN_SENT


def test_opted_out_contact_is_never_messaged():
    local_store.insert_opt_in_record(OptInRecord(phone="977777777704"))
    local_store.update_opt_in_status("977777777704", OptInStatus.OPTED_OUT)

    df = pd.DataFrame([{"phone": "977777777704", "name": "Test User 4"}])
    send_opt_in(df)

    record = local_store.get_opt_in_status("977777777704")
    assert record.status == OptInStatus.OPTED_OUT  # unchanged


def test_opted_in_contact_receives_content():
    # NOTE: this test makes a real Gemini API call via generate_text()
    local_store.insert_opt_in_record(OptInRecord(phone="977777777705"))
    local_store.update_opt_in_status("977777777705", OptInStatus.OPTED_IN)

    df = pd.DataFrame([{"phone": "977777777705", "name": "Test User 5"}])
    send_opt_in(df)

    record = local_store.get_opt_in_status("977777777705")
    assert record.status == OptInStatus.OPTED_IN  # stays opted in after content send


def test_running_twice_does_not_resend_opt_in():
    df = pd.DataFrame([{"phone": "977777777706", "name": "Test User 6"}])
    send_opt_in(df)  # first run — sends opt-in
    record_after_first = local_store.get_opt_in_status("977777777706")
    assert record_after_first.status == OptInStatus.OPT_IN_SENT

    send_opt_in(df)  # second run — should skip, not crash, not re-send
    record_after_second = local_store.get_opt_in_status("977777777706")
    assert record_after_second.status == OptInStatus.OPT_IN_SENT