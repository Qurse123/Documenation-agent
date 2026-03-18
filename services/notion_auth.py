"""
Notion Authentication
=====================
Reads the NOTION_TOKEN internal integration secret from .env.
No OAuth flow needed — just set NOTION_TOKEN in your .env file.
"""

import logging
import os

from dotenv import load_dotenv

from Errorcodes.codes import AppError

load_dotenv()

logger = logging.getLogger(__name__)


async def authenticate() -> str:
    """
    Return the Notion internal integration token from the environment.

    Raises AppError("NOTION_NOT_CONFIGURED") if NOTION_TOKEN is not set.
    """
    token = os.getenv("NOTION_TOKEN")
    if not token:
        raise AppError("NOTION_NOT_CONFIGURED")
    logger.info("Notion token loaded from environment.")
    return token
