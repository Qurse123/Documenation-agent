"""
Doc Agent — main entry point
=============================
Starts a documentation session, records until Ctrl+C,
then generates docs and publishes to Notion.
"""
## working
import asyncio
import logging
import signal
import sys

from services.agent import DocAgent

logger = logging.getLogger(__name__)


def setup_logging() -> None:
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
        stream=sys.stdout,
    )


async def run() -> None:
    agent = DocAgent(screenshot_interval=5.0)

    await agent.start()
    logger.info("Recording — press Ctrl+C to stop and generate documentation.")

    stop_event = asyncio.Event() ## set a async event called stop_event this event is not set to start
    loop = asyncio.get_running_loop() ## this gets the event loop running the async tasks
    loop.add_signal_handler(signal.SIGINT, stop_event.set) ## we ammend the event loop to add something that intrupts the event loop and sets the event

    await stop_event.wait() ## pause this async function until stop_event is set

    logger.info("Stopping session...")
    state = await agent.stop()

    logger.info("Documentation published to Notion: %s", state["notion_page_url"])


if __name__ == "__main__":
    setup_logging()
    asyncio.run(run())
