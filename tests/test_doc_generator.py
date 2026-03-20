"""
Tests for services/doc_generator.py — vision message construction.

ChatOpenAI and the Jinja2 template are not invoked; we test the
message-building logic directly.
"""

from langchain_core.messages import HumanMessage

from services.doc_generator import _build_vision_messages
from memory.state import DocAgentState, Screenshot


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _make_state(screenshots=None, transcript="") -> DocAgentState:
    return {
        "screenshots": screenshots or [],
        "transcript": transcript,
        "is_recording": False,
        "documentation": "",
        "notion_page_url": "",
    }


def _make_screenshot(b64: str = "aGVsbG8=") -> Screenshot:
    return {
        "image_data": b64,
        "timestamp": "2024-01-01T00:00:00",
        "description": "",
    }


# ---------------------------------------------------------------------------
# _build_vision_messages
# ---------------------------------------------------------------------------

def _content(messages: list[HumanMessage]) -> list[dict]:
    """Extract content as list[dict] with a type narrowing cast."""
    raw = messages[0].content
    assert isinstance(raw, list)
    return raw  # type: ignore[return-value]


def test_no_screenshots_produces_one_text_block():
    state = _make_state()
    messages = _build_vision_messages(state, "Generate documentation")

    assert len(messages) == 1
    content = _content(messages)
    assert len(content) == 1
    assert content[0]["type"] == "text"
    assert content[0]["text"] == "Generate documentation"


def test_one_screenshot_produces_text_plus_one_image_block():
    state = _make_state(screenshots=[_make_screenshot()])
    content = _content(_build_vision_messages(state, "prompt"))

    assert len(content) == 2
    assert content[0]["type"] == "text"
    assert content[1]["type"] == "image_url"


def test_two_screenshots_produce_text_plus_two_image_blocks():
    state = _make_state(screenshots=[_make_screenshot(), _make_screenshot()])
    content = _content(_build_vision_messages(state, "prompt"))

    assert len(content) == 3
    assert content[1]["type"] == "image_url"
    assert content[2]["type"] == "image_url"


def test_image_url_uses_base64_data_uri():
    b64 = "dGVzdGRhdGE="
    state = _make_state(screenshots=[_make_screenshot(b64)])
    content = _content(_build_vision_messages(state, "prompt"))

    url = content[1]["image_url"]["url"]
    assert url == f"data:image/png;base64,{b64}"


def test_image_detail_is_low():
    state = _make_state(screenshots=[_make_screenshot()])
    content = _content(_build_vision_messages(state, "prompt"))

    detail = content[1]["image_url"]["detail"]
    assert detail == "low"


def test_returns_human_message():
    state = _make_state()
    messages = _build_vision_messages(state, "prompt")
    assert isinstance(messages[0], HumanMessage)


def test_empty_prompt_text_still_produces_text_block():
    state = _make_state()
    content = _content(_build_vision_messages(state, ""))
    assert content[0]["type"] == "text"
    assert content[0]["text"] == ""


def test_screenshot_order_preserved():
    shots = [_make_screenshot("Zmlyc3Q="), _make_screenshot("c2Vjb25k")]
    state = _make_state(screenshots=shots)
    content = _content(_build_vision_messages(state, "prompt"))

    assert "Zmlyc3Q=" in content[1]["image_url"]["url"]
    assert "c2Vjb25k" in content[2]["image_url"]["url"]
