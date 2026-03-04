"""
Doc Agent — main entry point
=============================
Starts a documentation session, records until Ctrl+C,
then generates docs and publishes to Notion.
"""

import asyncio
import logging
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

    try:
        while True:
            await asyncio.sleep(1)
    except KeyboardInterrupt:
        pass

    logger.info("Stopping session...")
    state = await agent.stop()

    logger.info("Documentation published to Notion: %s", state["notion_page_url"])


if __name__ == "__main__":
    setup_logging()
    asyncio.run(run())
