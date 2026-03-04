import asyncio
import logging
from datetime import datetime
from typing import Optional

from memory.state import DocAgentState, Screenshot
from services.screenshot import capture_screenshot
from services.audio import start_recording, stop_recording, transcribe_audio
from services import browser

logger = logging.getLogger(__name__)


class SessionManager:
    """
    Manages the documentation recording lifecycle.
    
    Coordinates screenshot capture and audio recording,
    accumulates state, and returns completed session data
    for the agent to generate documentation from.
    """

    def __init__(self, screenshot_interval: float = 5.0):
        """
        Args:
            screenshot_interval: Seconds between automatic screenshots.
        """
        self._state: Optional[DocAgentState] = None
        self._screenshot_interval = screenshot_interval
        self._screenshot_task: Optional[asyncio.Task] = None
        self._is_running = False

    @property
    def is_recording(self) -> bool:
        return self._is_running

    async def start_session(self) -> None:
        """
        Start a documentation session.
        Begins audio recording and periodic screenshot capture.
        """
        if self._is_running:
            logger.warning("Session already running, ignoring start request.")
            return

        # Initialize fresh state
        self._state = {
            "screenshots": [],
            "transcript": "",
            "is_recording": True,
            "documentation": "",
            "notion_page_url": "",
        }

        # Launch browser session
        await browser.start_session()

        # Start audio recording
        start_recording()

        # Start periodic screenshot capture as async task
        self._is_running = True
        self._screenshot_task = asyncio.create_task(self._screenshot_loop())

        logger.info("Session started at %s", datetime.now().isoformat())

    async def stop_session(self) -> DocAgentState:
        """
        Stop the documentation session.
        Stops audio, transcribes audio, and returns the completed state.
        """
        if not self._is_running or self._state is None:
            raise RuntimeError("No active session to stop.")

        # Stop screenshot loop
        self._is_running = False
        if self._screenshot_task is not None:
            self._screenshot_task.cancel()
            try:
                await self._screenshot_task
            except asyncio.CancelledError:
                pass
            self._screenshot_task = None

        # Close browser session
        await browser.close_session()

        # Stop audio and get recording
        audio_recording = stop_recording()

        # Transcribe the audio
        logger.info("Transcribing audio...")
        transcript = transcribe_audio(audio_recording["path"])

        # Update state with final data
        self._state["transcript"] = transcript
        self._state["is_recording"] = False

        captured_count = len(self._state["screenshots"])
        logger.info(
            "Session ended. %d screenshots captured, transcript length: %d chars",
            captured_count,
            len(transcript),
        )

        return self._state

    async def take_manual_screenshot(self) -> Optional[Screenshot]:
        """Take a screenshot on demand (outside of automatic interval)."""
        if not self._is_running or self._state is None:
            logger.warning("Cannot take screenshot — no active session.")
            return None

        captured = await capture_screenshot()
        self._state["screenshots"].append(captured)
        logger.info("Manual screenshot captured. Total: %d", len(self._state["screenshots"]))
        return captured

    async def _screenshot_loop(self) -> None:
        """Async loop that captures screenshots at regular intervals."""
        while self._is_running:
            try:
                captured = await capture_screenshot()
                if self._state is not None:
                    self._state["screenshots"].append(captured)
                    logger.info(
                        "Screenshot #%d captured",
                        len(self._state["screenshots"]),
                    )
            except Exception as e:
                logger.error("Screenshot capture failed: %s", e)

            await asyncio.sleep(self._screenshot_interval)
