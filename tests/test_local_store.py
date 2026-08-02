import os
import pytest
from app.db import local_store
from app.models.schemas import Lead, LeadStatus, OptInRecord, OptInStatus


@pytest.fixture(autouse=True)
def clean_db():
    # fresh database before every test in this file
    if local_store.DB_PATH.exists():
        os.remove(local_store.DB_PATH)
    local_store.create_tables()
    yield
    if local_store.DB_PATH.exists():
        os.remove(local_store.DB_PATH)


def test_insert_and_get_lead():
    lead = Lead(phone="911111111111", name="Test User", category="IT Support")
    local_store.insert_lead(lead)
    fetched = local_store.get_lead_by_phone("911111111111")
    assert fetched is not None
    assert fetched.name == "Test User"
    assert fetched.status == LeadStatus.NEW


def test_get_lead_returns_none_if_missing():
    result = local_store.get_lead_by_phone("999999999999")
    assert result is None


def test_update_lead_status():
    lead = Lead(phone="911111111111", name="Test User")
    local_store.insert_lead(lead)
    local_store.update_lead_status("911111111111", LeadStatus.HUMAN_ASSIGNED)
    updated = local_store.get_lead_by_phone("911111111111")
    assert updated.status == LeadStatus.HUMAN_ASSIGNED


def test_insert_and_get_opt_in_record():
    record = OptInRecord(phone="922222222222")
    local_store.insert_opt_in_record(record)
    fetched = local_store.get_opt_in_status("922222222222")
    assert fetched is not None
    assert fetched.status == OptInStatus.NOT_CONTACTED


def test_update_opt_in_status():
    record = OptInRecord(phone="922222222222")
    local_store.insert_opt_in_record(record)
    local_store.update_opt_in_status("922222222222", OptInStatus.OPTED_IN)
    updated = local_store.get_opt_in_status("922222222222")
    assert updated.status == OptInStatus.OPTED_IN