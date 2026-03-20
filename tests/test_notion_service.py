"""
Tests for services/notion_service.py — markdown parsing and title extraction.

These are pure-function tests; no HTTP calls are made.
"""

from services.notion_service import (
    parse_markdown_to_blocks,
    _extract_title,
    _SCREENSHOT_PATTERN,
)


# ---------------------------------------------------------------------------
# _SCREENSHOT_PATTERN regex
# ---------------------------------------------------------------------------

def test_pattern_matches_standard_marker():
    assert _SCREENSHOT_PATTERN.search("[Screenshot 1]") is not None


def test_pattern_is_case_insensitive():
    assert _SCREENSHOT_PATTERN.search("[screenshot 2]") is not None
    assert _SCREENSHOT_PATTERN.search("[SCREENSHOT 3]") is not None


def test_pattern_matches_extra_spaces():
    assert _SCREENSHOT_PATTERN.search("[Screenshot   42]") is not None


def test_pattern_no_match_on_plain_text():
    assert _SCREENSHOT_PATTERN.search("Here is some plain text.") is None


def test_pattern_captures_correct_number():
    m = _SCREENSHOT_PATTERN.search("[Screenshot 7]")
    assert m is not None
    assert m.group(1) == "7"


# ---------------------------------------------------------------------------
# parse_markdown_to_blocks — block types
# ---------------------------------------------------------------------------

def test_empty_documentation_returns_empty_list():
    assert parse_markdown_to_blocks("", {}) == []


def test_whitespace_only_returns_empty_list():
    assert parse_markdown_to_blocks("   \n\n   ", {}) == []


def test_h1_heading_block():
    blocks = parse_markdown_to_blocks("# My Guide", {})
    assert len(blocks) == 1
    assert blocks[0]["type"] == "heading_1"


def test_h2_heading_block():
    blocks = parse_markdown_to_blocks("## A Section", {})
    assert blocks[0]["type"] == "heading_2"


def test_h3_heading_block():
    blocks = parse_markdown_to_blocks("### Subsection", {})
    assert blocks[0]["type"] == "heading_3"


def test_numbered_list_item():
    blocks = parse_markdown_to_blocks("1. Click the button", {})
    assert blocks[0]["type"] == "numbered_list_item"


def test_bulleted_list_item():
    blocks = parse_markdown_to_blocks("- Open the menu", {})
    assert blocks[0]["type"] == "bulleted_list_item"


def test_plain_text_is_paragraph():
    blocks = parse_markdown_to_blocks("This is a plain sentence.", {})
    assert blocks[0]["type"] == "paragraph"


def test_horizontal_rule_is_skipped():
    blocks = parse_markdown_to_blocks("---", {})
    assert blocks == []


# ---------------------------------------------------------------------------
# parse_markdown_to_blocks — screenshot markers
# ---------------------------------------------------------------------------

def test_screenshot_marker_creates_image_block():
    ids = {1: "upload-abc123"}
    blocks = parse_markdown_to_blocks("[Screenshot 1]", ids)
    assert len(blocks) == 1
    assert blocks[0]["type"] == "image"
    assert blocks[0]["image"]["file_upload"]["id"] == "upload-abc123"


def test_screenshot_marker_lowercase_still_creates_image_block():
    ids = {2: "upload-xyz"}
    blocks = parse_markdown_to_blocks("[screenshot 2]", ids)
    assert blocks[0]["type"] == "image"


def test_screenshot_not_in_ids_creates_fallback_paragraph():
    # When the screenshot index has no upload ID, a "not available" paragraph is inserted
    blocks = parse_markdown_to_blocks("[Screenshot 99]", {})
    assert len(blocks) == 1
    assert blocks[0]["type"] == "paragraph"
    content = blocks[0]["paragraph"]["rich_text"][0]["text"]["content"]
    assert "99" in content


def test_text_before_screenshot_marker_becomes_paragraph():
    ids = {1: "upload-id"}
    blocks = parse_markdown_to_blocks("See below: [Screenshot 1]", ids)
    assert blocks[0]["type"] == "paragraph"
    assert blocks[1]["type"] == "image"


# ---------------------------------------------------------------------------
# parse_markdown_to_blocks — ordering and mixed content
# ---------------------------------------------------------------------------

def test_mixed_content_preserves_order():
    doc = (
        "# Title\n"
        "\n"
        "Some intro text\n"
        "\n"
        "1. Step one\n"
        "\n"
        "- A bullet\n"
        "\n"
        "[Screenshot 1]"
    )
    ids = {1: "upload-id"}
    blocks = parse_markdown_to_blocks(doc, ids)
    types = [b["type"] for b in blocks]
    assert types == [
        "heading_1",
        "paragraph",
        "numbered_list_item",
        "bulleted_list_item",
        "image",
    ]


def test_multiple_screenshots_inserted_at_correct_positions():
    doc = "[Screenshot 1]\nMiddle text\n[Screenshot 2]"
    ids = {1: "id-one", 2: "id-two"}
    blocks = parse_markdown_to_blocks(doc, ids)
    assert blocks[0]["type"] == "image"
    assert blocks[1]["type"] == "paragraph"
    assert blocks[2]["type"] == "image"


# ---------------------------------------------------------------------------
# _extract_title
# ---------------------------------------------------------------------------

def test_extract_title_from_h1():
    assert _extract_title("# My Step-by-Step Guide\n\nContent") == "My Step-by-Step Guide"


def test_extract_title_from_h2():
    assert _extract_title("## Section Header") == "Section Header"


def test_extract_title_no_headings_returns_default():
    assert _extract_title("Just plain text with no headings.") == "Documentation"


def test_extract_title_first_heading_wins():
    doc = "Plain text here\n# The Real Title\n## Another"
    assert _extract_title(doc) == "The Real Title"


def test_extract_title_empty_string_returns_default():
    assert _extract_title("") == "Documentation"
