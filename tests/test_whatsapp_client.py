import os
import pytest

from app.integrations.whatsapp_client import send_template_message, send_text_message


def test_send_template_message_succeeds():
    recipient = os.getenv("TEST_RECIPIENT_NUMBER")
    result = send_template_message(to=recipient, template_name="hello_world", language_code="en_US")
    assert "messages" in result


def test_send_template_message_rejects_empty_recipient():
    with pytest.raises(ValueError):
        send_template_message(to="", template_name="hello_world")


def test_send_text_message_succeeds():
    # NOTE: only passes while the 24-hour free-form messaging window is open
    # (i.e. the test recipient has messaged the sandbox number within the last 24 hrs).
    # A failure here after the window closes is expected, not a code bug.
    recipient = os.getenv("TEST_RECIPIENT_NUMBER")
    result = send_text_message(to=recipient, body="Automated test message from pytest.")
    assert "messages" in result


def test_send_text_message_rejects_empty_body():
    with pytest.raises(ValueError):
        send_text_message(to=os.getenv("TEST_RECIPIENT_NUMBER"), body="")