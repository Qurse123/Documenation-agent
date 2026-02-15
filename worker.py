"""
Doc Agent Worker come back to this I still dont think its right 
================
Entry point for ./gradlew runWorker

Boots the agent process and streams all logs to the terminal.
The worker does NOT run sessions itself — sessions are triggered
by external components (Stagehand, API, etc.). This is purely
the process host and log stream.
"""

import asyncio
import logging
import sys
from services.agent import DocAgent


def setup_logging() -> None:
    """Configure the root logger so every module's logs flow to stdout."""
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
        stream=sys.stdout,
    )


async def main() -> None:
    logger = logging.getLogger("worker")

    agent = DocAgent(screenshot_interval=5.0)

    logger.info("Doc Agent worker started. Waiting for session triggers...")

    # Keep the process alive — sessions will be triggered externally
    try:
        while True:
            await asyncio.sleep(1)
    except KeyboardInterrupt:
        logger.info("Worker shutting down.")


if __name__ == "__main__":
    setup_logging()
    asyncio.run(main())
