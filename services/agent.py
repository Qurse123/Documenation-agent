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

    @property
    def is_recording(self) -> bool:
        return self._session_manager.is_recording

    async def start(self) -> None:
        """Start a documentation recording session."""
        logger.info("DocAgent: Starting documentation session...")
        await self._session_manager.start_session()
        logger.info("DocAgent: Session is live. Recording audio and capturing screenshots.")

    async def stop(self) -> DocAgentState:
        """
        Stop the recording session and generate documentation.

        Returns:
            Completed DocAgentState with screenshots, transcript, and documentation.
        """
        logger.info("DocAgent: Stopping session...")

        # Stop recording and get accumulated state
        state = await self._session_manager.stop_session()

        logger.info(
            "DocAgent: Session data collected. %d screenshots, %d chars transcript.",
            len(state["screenshots"]), ## number of screenshots 
            len(state["transcript"]), ## number of charcters in the transcipt
        )

        # Generate documentation from the session
        logger.info("DocAgent: Generating documentation...")
        documentation = await generate_documentation(state)

        # Store in state
        state["documentation"] = documentation

        logger.info("DocAgent: Documentation complete.")
        return state

    async def take_screenshot(self) -> None:
        """Manually trigger a screenshot during recording."""
        result = await self._session_manager.take_manual_screenshot()
        if result:
            logger.info("DocAgent: Manual screenshot captured.")
        else:
            logger.warning("DocAgent: Cannot take screenshot — no active session.")
