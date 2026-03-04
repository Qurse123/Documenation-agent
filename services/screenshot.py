"""
Screenshot Service (thin wrapper)
==================================
Delegates to the Stagehand browser service for page capture.
Keeps the same async interface so session_manager.py doesn't need
to import browser.py directly.
"""

from memory.state import Screenshot
from services.browser import capture_page


async def capture_screenshot() -> Screenshot:
    """Capture the current browser page via Stagehand."""
    return await capture_page()
