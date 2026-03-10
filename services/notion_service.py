"""
Notion Service
==============
Handles publishing documentation to Notion.

Responsibilities:
    - Upload screenshots to Notion via their File Upload API
    - Parse LLM-generated markdown into Notion block objects
    - Create a Notion page with text and image blocks in the right places
"""

import base64
import logging
import re
from typing import Any

import httpx

from memory.state import DocAgentState
from services.notion_auth import authenticate
from Errorcodes.codes import AppError

logger = logging.getLogger(__name__)

NOTION_API_BASE = "https://api.notion.com/v1"
NOTION_VERSION = "2025-09-03"


def _notion_headers(access_token: str) -> dict:
    """Standard headers for Notion REST API calls."""
    return {
        "Authorization": f"Bearer {access_token}",
        "Notion-Version": NOTION_VERSION,
    }


# --- Screenshot upload ---

async def upload_screenshot(image_data: str, index: int, access_token: str) -> str:
    """
    Upload a single screenshot to Notion via the File Upload API.

    Args:
        image_data: Base64-encoded PNG data.
        index: Screenshot number (for the filename).
        access_token: Notion OAuth access token.

    Returns:
        The file_upload ID to reference in image blocks.
    """
    filename = f"screenshot_{index}.png"
    headers = _notion_headers(access_token)

    async with httpx.AsyncClient() as client:
        # Step 1: Create file upload object
        create_resp = await client.post(
            f"{NOTION_API_BASE}/file_uploads",
            json={"filename": filename, "content_type": "image/png"},
            headers={**headers, "Content-Type": "application/json"},
        )

        if create_resp.status_code != 200:
            raise AppError("NOTION_008", detail=f"Create failed: {create_resp.status_code} {create_resp.text}")

        upload_obj = create_resp.json()
        upload_id = upload_obj["id"]
        upload_url = upload_obj.get("upload_url", f"{NOTION_API_BASE}/file_uploads/{upload_id}/send")

        # Step 2: Send the actual file bytes (POST, not PATCH; don't set Content-Type — httpx handles multipart boundary)
        png_bytes = base64.b64decode(image_data)
        send_resp = await client.post(
            f"{NOTION_API_BASE}/file_uploads/{upload_id}/send",
            files={"file": (filename, png_bytes, "image/png")},
            headers={"Authorization": f"Bearer {access_token}", "Notion-Version": NOTION_VERSION},
        )

        if send_resp.status_code != 200:
            raise AppError("NOTION_008", detail=f"Send failed: {send_resp.status_code} {send_resp.text}")

        logger.info("Uploaded screenshot %d to Notion (file_upload: %s)", index, upload_id)
        return upload_id


async def upload_all_screenshots(state: DocAgentState, access_token: str) -> dict[int, str]:
    """
    Upload all screenshots from the session to Notion.

    Returns:
        Dict mapping screenshot number (1-based) to Notion file_upload ID.
    """
    upload_ids: dict[int, str] = {}

    for i, shot in enumerate(state["screenshots"]):
        try:
            upload_id = await upload_screenshot(shot["image_data"], i + 1, access_token)
            upload_ids[i + 1] = upload_id
        except Exception as e:
            logger.error("Failed to upload screenshot %d: %s", i + 1, e)

    logger.info("Uploaded %d / %d screenshots to Notion.", len(upload_ids), len(state["screenshots"]))
    return upload_ids


# --- Markdown to Notion blocks parser ---                                  

"""
This is Regex or regular expression --> this will capture patterns in text to save
In this case re.complie = reusable object basically intialzie your pattern detector then 
r" is raw string, \\[ is literal bracket, screenshot matches the word, \\s+ is one or more spaces
(\\d+) captures 1 or more digits

so the pattern we are looking for should be:

[Screenshot 1]
[Screenshot 42]
[Screenshot     9]
"""

_SCREENSHOT_PATTERN = re.compile(r"\[Screenshot\s+(\d+)\]", re.IGNORECASE) 


def _text_to_rich_text(text: str) -> list[dict[str, Any]]:
    """Convert a plain string to Notion rich_text array."""
    if not text.strip():
        return []
    return [{"type": "text", "text": {"content": text.strip()}}]


def _heading_block(text: str, level: int) -> dict[str, Any]:
    """Create a Notion heading block (level 1, 2, or 3)."""
    heading_type = f"heading_{min(level, 3)}"
    return {
        "object": "block",
        "type": heading_type,
        heading_type: {"rich_text": _text_to_rich_text(text)},
    }


def _paragraph_block(text: str) -> dict[str, Any]:
    """Create a Notion paragraph block."""
    return {
        "object": "block",
        "type": "paragraph",
        "paragraph": {"rich_text": _text_to_rich_text(text)},
    }


def _numbered_list_block(text: str) -> dict[str, Any]:
    """Create a Notion numbered list item block."""
    return {
        "object": "block",
        "type": "numbered_list_item",
        "numbered_list_item": {"rich_text": _text_to_rich_text(text)},
    }


def _bulleted_list_block(text: str) -> dict[str, Any]:
    """Create a Notion bulleted list item block."""
    return {
        "object": "block",
        "type": "bulleted_list_item",
        "bulleted_list_item": {"rich_text": _text_to_rich_text(text)},
    }


def _image_block(file_upload_id: str) -> dict[str, Any]:
    """Create a Notion image block referencing an uploaded file."""
    return {
        "object": "block",
        "type": "image",
        "image": {
            "type": "file_upload",
            "file_upload": {"id": file_upload_id},
        },
    }


def parse_markdown_to_blocks( 
    documentation: str,
    screenshot_ids: dict[int, str],
) -> list[dict[str, Any]]:
    """
    Parse LLM-generated markdown into Notion block objects.

    Handles:
        - Headings (# ## ###)
        - Numbered lists (1. 2. 3.)
        - Bulleted lists (- item)
        - Paragraphs
        - [Screenshot N] markers -> image blocks

    Args:
        documentation: Markdown string from the doc generator.
        screenshot_ids: Mapping of screenshot number to Notion file_upload ID.

    Returns:
        List of Notion block objects ready for the API.
    """
    blocks: list[dict[str, Any]] = []
    lines = documentation.split("\n")

    for line in lines:
        stripped = line.strip()

        if not stripped:
            continue

        # Check for screenshot markers anywhere in the line
        marker_match = _SCREENSHOT_PATTERN.search(stripped)
        if marker_match:
            shot_num = int(marker_match.group(1))

            # Text before the marker becomes a paragraph
            before = stripped[:marker_match.start()].strip()
            if before:
                blocks.append(_paragraph_block(before))

            # Insert the image block if we have the upload
            if shot_num in screenshot_ids:
                blocks.append(_image_block(screenshot_ids[shot_num]))
                logger.debug("Inserted image block for Screenshot %d", shot_num)
            else:
                blocks.append(_paragraph_block(f"(Screenshot {shot_num} — not available)"))

            # Text after the marker
            after = stripped[marker_match.end():].strip()
            if after:
                blocks.append(_paragraph_block(after))
            continue

        # Headings
        if stripped.startswith("### "):
            blocks.append(_heading_block(stripped[4:], 3))
        elif stripped.startswith("## "):
            blocks.append(_heading_block(stripped[3:], 2))
        elif stripped.startswith("# "):
            blocks.append(_heading_block(stripped[2:], 1))
        # Numbered list
        elif re.match(r"^\d+\.\s", stripped):
            text = re.sub(r"^\d+\.\s*", "", stripped)
            blocks.append(_numbered_list_block(text))
        # Bulleted list
        elif stripped.startswith("- "):
            blocks.append(_bulleted_list_block(stripped[2:]))
        # Horizontal rule (skip)
        elif stripped == "---":
            continue
        # Regular paragraph
        else:
            blocks.append(_paragraph_block(stripped))

    logger.info("Parsed markdown into %d Notion blocks.", len(blocks))
    return blocks

# --- Page creation ---

def _extract_title(documentation: str) -> str:
    """Pull the first heading from the markdown as the page title."""
    for line in documentation.split("\n"):
        stripped = line.strip()
        if stripped.startswith("#"):
            return stripped.lstrip("#").strip()
    return "Documentation"


async def create_notion_page(
    title: str,
    blocks: list[dict[str, Any]],
    access_token: str,
    parent_page_id: str | None = None, ## parent_page_id is an optional param that can be a string or none. Deafults to none if no value is provided 
) -> str:
    """
    Create a new Notion page with the given blocks.

    Args:
        title: Page title.
        blocks: List of Notion block objects.
        access_token: Notion OAuth access token.
        parent_page_id: Optional parent page ID. If None, creates in workspace root.

    Returns:
        URL of the created page.
    """
    headers = {**_notion_headers(access_token), "Content-Type": "application/json"}

    if parent_page_id:
        parent: dict[str, Any] = {"type": "page_id", "page_id": parent_page_id}
    else:
        parent = {"type": "workspace", "workspace": True}
    
    # Notion API limits children to 100 blocks per request
    first_batch = blocks[:100]
    remaining = blocks[100:]

    payload: dict[str, Any] = {
        "parent": parent,
        "properties": {
            "title": [{"text": {"content": title}}],
        },
        "children": first_batch,
    }

    async with httpx.AsyncClient() as client:
        logger.info("Creating Notion page: '%s' (%d blocks)...", title, len(blocks))
        resp = await client.post(
            f"{NOTION_API_BASE}/pages",
            json=payload,
            headers=headers,
        )

        if resp.status_code != 200:
            raise AppError("NOTION_009", detail=f"{resp.status_code} {resp.text}")

        page = resp.json()
        page_id = page["id"]
        page_url = page.get("url", f"https://notion.so/{page_id.replace('-', '')}")

        # Append remaining blocks in batches of 100
        for i in range(0, len(remaining), 100):
            batch = remaining[i:i + 100]
            append_resp = await client.patch(
                f"{NOTION_API_BASE}/blocks/{page_id}/children",
                json={"children": batch},
                headers=headers,
            )
            if append_resp.status_code != 200:
                logger.error("Failed to append blocks batch %d: %s", i // 100 + 2, append_resp.text)

        logger.info("Notion page created: %s", page_url)
        return page_url


# --- Main entry point ---

async def publish_to_notion(state: DocAgentState) -> str:
    """
    Publish a completed documentation session to Notion.

    1. Authenticate with Notion (OAuth, cached tokens)
    2. Upload all screenshots
    3. Parse markdown into Notion blocks with images in the right places
    4. Create the Notion page

    Args:
        state: Completed DocAgentState with documentation and screenshots.

    Returns:
        URL of the created Notion page.
    """
    logger.info("Publishing documentation to Notion...")

    # Authenticate (returns access_token string directly)
    access_token = await authenticate()

    # Upload screenshots
    screenshot_ids = await upload_all_screenshots(state, access_token)

    # Parse documentation into Notion blocks
    title = _extract_title(state["documentation"])
    blocks = parse_markdown_to_blocks(state["documentation"], screenshot_ids)

    # Create the page
    page_url = await create_notion_page(title, blocks, access_token)

    logger.info("Documentation published to Notion: %s", page_url)
    return page_url
