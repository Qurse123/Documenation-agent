"""
Notion Authentication
=====================
OAuth-only Notion auth:
- NOTION_CLIENT_ID
- NOTION_CLIENT_SECRET
- NOTION_REDIRECT_URI
"""

import base64
import logging
import os
import urllib.parse

import httpx
from dotenv import load_dotenv

from Errorcodes.codes import AppError

load_dotenv()

logger = logging.getLogger(__name__)

NOTION_OAUTH_TOKEN_URL = "https://api.notion.com/v1/oauth/token"
NOTION_OAUTH_AUTHORIZE_URL = "https://api.notion.com/v1/oauth/authorize"

_oauth_access_token: str | None = None


def _env(name: str) -> str | None:
    value = os.getenv(name)
    if value is None:
        return None
    stripped = value.strip()
    return stripped or None


def oauth_mode_configured() -> bool:
    return all(
        [
            _env("NOTION_CLIENT_ID"),
            _env("NOTION_CLIENT_SECRET"),
            _env("NOTION_REDIRECT_URI"),
        ]
    )


def has_ready_access_token() -> bool:
    return _oauth_access_token is not None


def get_authorize_url(state: str) -> str:
    client_id = _env("NOTION_CLIENT_ID")
    redirect_uri = _env("NOTION_REDIRECT_URI")
    if not client_id or not redirect_uri:
        raise AppError("NOTION_NOT_CONFIGURED")

    query = urllib.parse.urlencode(
        {
            "client_id": client_id,
            "response_type": "code",
            "owner": "user",
            "redirect_uri": redirect_uri,
            "state": state,
        }
    )
    return f"{NOTION_OAUTH_AUTHORIZE_URL}?{query}"


async def exchange_code_for_token(code: str) -> str:
    client_id = _env("NOTION_CLIENT_ID")
    client_secret = _env("NOTION_CLIENT_SECRET")
    redirect_uri = _env("NOTION_REDIRECT_URI")
    if not client_id or not client_secret or not redirect_uri:
        raise AppError("NOTION_NOT_CONFIGURED")

    basic = base64.b64encode(f"{client_id}:{client_secret}".encode("utf-8")).decode("utf-8")
    headers = {
        "Authorization": f"Basic {basic}",
        "Content-Type": "application/json",
    }
    payload = {
        "grant_type": "authorization_code",
        "code": code,
        "redirect_uri": redirect_uri,
    }

    async with httpx.AsyncClient(timeout=httpx.Timeout(30.0)) as client:
        resp = await client.post(NOTION_OAUTH_TOKEN_URL, headers=headers, json=payload)
    if resp.status_code != 200:
        raise AppError("NOTION_NOT_CONFIGURED")

    token = resp.json().get("access_token")
    if not token:
        raise AppError("NOTION_NOT_CONFIGURED")

    global _oauth_access_token
    _oauth_access_token = token
    logger.info("Notion OAuth access token exchanged and cached in memory.")
    return token


async def authenticate() -> str:
    """
    Return the OAuth access token for Notion API calls.
    """
    if _oauth_access_token:
        return _oauth_access_token

    raise AppError("NOTION_NOT_CONFIGURED")
