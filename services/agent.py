import asyncio
import logging

from dotenv import load_dotenv

from managers.session_manager import SessionManager
from services.doc_generator import generate_documentation
from memory.state import DocAgentState

load_dotenv()

logger = logging.getLogger(__name__)


class DocAgent:
    """
    Orchestrates the full documentation workflow.

    Connects the SessionManager (recording) and DocGenerator (AI)
    to produce documentation from a user's screen session.

    Flow:
        1. start() -> begins recording (audio + screenshots)
        2. User works and speaks...
        3. stop() -> stops recording, transcribes, generates docs
        4. Returns Markdown documentation
    """

    def __init__(self, screenshot_interval: float = 5.0):
        self._session_manager = SessionManager(screenshot_interval=screenshot_interval)
        self._last_state: DocAgentState | None = None

    @property
    def is_recording(self) -> bool:
        return self._session_manager.is_recording

    @property ## because of this now you can call last_state as agent.last_state instead of agent.last_state()
    def last_state(self) -> DocAgentState | None:
        """Access the last completed session state (for inspection/debugging)."""
        return self._last_state

    async def start(self) -> None:
        """Start a documentation recording session."""
        logger.info("DocAgent: Starting documentation session...")
        await self._session_manager.start_session()
        logger.info("DocAgent: Session is live. Recording audio and capturing screenshots.")

    async def stop(self) -> str:
        """
        Stop the recording session and generate documentation.

        Returns:
            Generated Markdown documentation string.
        """
        logger.info("DocAgent: Stopping session...")

        # Stop recording and get accumulated state
        state = await self._session_manager.stop_session()
        self._last_state = state

        logger.info(
            "DocAgent: Session data collected. %d screenshots, %d chars transcript.",
            len(state["screenshots"]),
            len(state["transcript"]),
        )

        # Generate documentation from the session
        logger.info("DocAgent: Generating documentation...")
        documentation = await generate_documentation(state)

        # Store in state
        state["documentation"] = documentation

        logger.info("DocAgent: Documentation complete.")
        return documentation

    async def take_screenshot(self) -> None:
        """Manually trigger a screenshot during recording."""
        result = await self._session_manager.take_manual_screenshot()
        if result:
            logger.info("DocAgent: Manual screenshot captured.")
        else:
            logger.warning("DocAgent: Cannot take screenshot — no active session.")
