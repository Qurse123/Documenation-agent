"""
Browser Service (Stagehand)
============================
Manages a Stagehand-controlled Chrome session in local mode.

The user does their work inside this browser. The agent observes
what's on screen via Stagehand's observe() API and takes browser-level
screenshots by connecting Playwright to the session's CDP endpoint.
"""

import base64
import logging
import os
from datetime import datetime
from typing import Any, Optional

from playwright.async_api import async_playwright, Page
from stagehand import AsyncStagehand
from dotenv import load_dotenv

from memory.state import Screenshot

load_dotenv()

logger = logging.getLogger(__name__)

_client: Optional[AsyncStagehand] = None
_session: Any = None
_playwright: Any = None
_browser: Any = None
_page: Optional[Page] = None


async def start_session() -> Any:
    """
    Launch a Stagehand-controlled Chrome browser in local mode.
    Also connects Playwright to the CDP endpoint for screenshots.
    Returns the session object for observe/act/extract calls.
    """
    global _client, _session, _playwright, _browser, _page

    if _session is not None:
        logger.warning("Browser session already running.")
        return _session

    model_api_key = os.getenv("MODEL_API_KEY") or os.getenv("OPENAI_API_KEY")

    _client = AsyncStagehand(
        server="local",
        model_api_key=model_api_key,
        local_headless=False,
    )

    _session = await _client.sessions.start(model_name="openai/gpt-4o")  # type: ignore[union-attr]
    session_id = _session.data.session_id
    cdp_url = _session.data.cdp_url
    logger.info("Stagehand browser session started: %s", session_id)

    if cdp_url:
        _playwright = await async_playwright().start()
        _browser = await _playwright.chromium.connect_over_cdp(cdp_url)
        contexts = _browser.contexts
        _page = contexts[0].pages[0] if contexts and contexts[0].pages else None
        logger.info("Playwright connected to CDP endpoint for screenshots.")
    else:
        logger.warning("No CDP URL returned — screenshots will be unavailable.")

    return _session


async def capture_page() -> Screenshot:
    """
    Take a browser screenshot and observe the DOM to get a description.

    Returns a Screenshot dict with:
        - image_data: base64-encoded PNG of the browser page
        - timestamp: ISO timestamp
        - description: what Stagehand observes on the page
    """
    if _session is None:
        raise RuntimeError("No active browser session. Call start_session() first.")

    timestamp = datetime.now().isoformat()

    b64_data = ""
    if _page is not None:
        png_bytes = await _page.screenshot(type="png")
        b64_data = base64.b64encode(png_bytes).decode("utf-8")
    else:
        logger.warning("No Playwright page available — returning empty screenshot.")

    description = ""
    try:
        observe_response = await _session.observe(
            instruction="Describe what is currently visible on this page in 1-2 sentences in way that helps a user understand as if they were going through a document"
        )
        results = observe_response.data.result
        if results:
            description = results[0].description if hasattr(results[0], "description") else str(results[0])
    except Exception as e:
        logger.warning("Observe failed, screenshot will have empty description: %s", e)

    logger.debug("Page captured. Description: %s", description[:80] if description else "(empty)")

    return {
        "image_data": b64_data,
        "timestamp": timestamp,
        "description": description,
    }


async def close_session() -> None:
    """End the Stagehand browser session and clean up."""
    global _client, _session, _playwright, _browser, _page

    if _page is not None: ## Here we are dropping the _page reference  
        _page = None

    if _browser is not None:
        try:
            await _browser.close()
        except Exception:
            pass
        _browser = None

    if _playwright is not None:
        try:
            await _playwright.stop()
        except Exception:
            pass
        _playwright = None

    if _session is not None:
        try:
            await _session.end()
            logger.info("Browser session ended.")
        except Exception as e:
            logger.error("Error closing browser session: %s", e)
        _session = None

    if _client is not None:
        try:
            await _client.close()
        except Exception:
            pass
        _client = None
