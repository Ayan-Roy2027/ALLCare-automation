from app.integrations.gemini_client import generate_text, generate_json


def test_generate_text_returns_nonempty_string():
    result = generate_text("Say hello in one short sentence.")
    assert isinstance(result, str)
    assert len(result.strip()) > 0


def test_generate_text_rejects_empty_prompt():
    try:
        generate_text("")
        assert False, "Expected ValueError for empty prompt"
    except ValueError:
        pass


def test_generate_json_returns_dict():
    prompt = (
        "Extract the customer's name and neighborhood from this message, "
        "and return as JSON with keys 'name' and 'location':\n\n"
        "\"Hi I'm Priya, I live near Salt Lake and need a repair.\""
    )
    result = generate_json(prompt)
    assert isinstance(result, dict)
    assert "name" in result