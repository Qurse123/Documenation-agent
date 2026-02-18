"""
Notion OAuth Authentication
============================
Standard OAuth 2.0 Authorization Code flow for Notion.

Flow:
    1. Open browser to Notion's authorize page
    2. User logs in and grants access to their workspace
    3. Notion redirects to the configured NOTION_REDIRECT_URI with an auth code
    4. Exchange code for access_token via Basic Auth (client_id:client_secret)
    5. Store token locally for future sessions

Prerequisites:
    - Create a Public Integration at https://www.notion.so/my-integrations
    - Set redirect URI in your Notion integration settings (must match NOTION_REDIRECT_URI in .env)
    - Add NOTION_CLIENT_ID, NOTION_CLIENT_SECRET, and NOTION_REDIRECT_URI to .env
"""

import base64
import json
import logging
import os
import secrets
import webbrowser
from http.server import HTTPServer, BaseHTTPRequestHandler
from pathlib import Path
from typing import Optional
from urllib.parse import urlencode, urlparse, parse_qs

import httpx
from dotenv import load_dotenv

from Errorcodes.codes import AppError

load_dotenv()

logger = logging.getLogger(__name__)

"""
In development we use localhost as the OAuth redirect. 
In production this must be replaced with the deployed backend URL

Devlopment:
http://localhost:9876/callback
Production:
https://api.myapp.com/callback
"""

# Config from .env
NOTION_CLIENT_ID = os.getenv("NOTION_CLIENT_ID")
NOTION_CLIENT_SECRET = os.getenv("NOTION_CLIENT_SECRET")
REDIRECT_URI = os.getenv("NOTION_REDIRECT_URI", "http://localhost:9876/callback")


# Parse host and port from redirect URI for the local callback server ## keep for now
_parsed_redirect = urlparse(REDIRECT_URI)
REDIRECT_HOST = _parsed_redirect.hostname or "localhost"
REDIRECT_PORT = _parsed_redirect.port or 9876

# Notion OAuth endpoints
AUTHORIZE_URL = "https://api.notion.com/v1/oauth/authorize"
TOKEN_URL = "https://api.notion.com/v1/oauth/token"

# Token persistence
TOKEN_FILE = Path(__file__).parent.parent / ".notion_tokens.json"

# --- Local callback server ---

class _CallbackHandler(BaseHTTPRequestHandler):
    """Catches the OAuth redirect from Notion on localhost."""

    auth_code: Optional[str] = None
    received_state: Optional[str] = None
    error: Optional[str] = None

    def _respond(self, message: str):
        self.send_response(200)
        self.send_header("Content-Type", "text/html")
        self.end_headers()
        html = f"<html><body><h2>{message}</h2></body></html>"
        self.wfile.write(html.encode())

    def log_message(self, format, *args):
        pass
    
    def do_GET(self):
        parsed = urlparse(self.path)
        params = parse_qs(parsed.query)

        if "error" in params:
            _CallbackHandler.error = params["error"][0]
            self._respond("Authorization failed. You can close this tab.")
            return

        if "code" in params:
            _CallbackHandler.auth_code = params["code"][0]
            _CallbackHandler.received_state = params.get("state", [None])[0]
            self._respond("Connected to Notion! You can close this tab and return to the terminal.")
            return

        self._respond("Unexpected callback. You can close this tab.") 

def _wait_for_callback(expected_state: str) -> str:
    """Start localhost server, wait for Notion's redirect, validate state, return auth code."""
    _CallbackHandler.auth_code = None
    _CallbackHandler.received_state = None
    _CallbackHandler.error = None

    server = HTTPServer((REDIRECT_HOST, REDIRECT_PORT), _CallbackHandler)
    server.timeout = 120

    logger.info("Waiting for Notion authorization (timeout: 120s)...")
    server.handle_request()
    server.server_close()

    if _CallbackHandler.error:
        raise AppError("NOTION_AUTH_CALLBACK_ERROR", detail=_CallbackHandler.error)

    if not _CallbackHandler.auth_code:
        raise AppError("NOTION_AUTH_CALLBACK_TIMEOUT")

    if _CallbackHandler.received_state != expected_state:
        raise AppError("NOTION_AUTH_STATE_MISMATCH")

    return _CallbackHandler.auth_code


# --- Token exchange ---

async def _exchange_code(code: str) -> dict:
    """
    Exchange auth code for access_token.
    Uses HTTP Basic Auth: base64(client_id:client_secret).
    """
    credentials = f"{NOTION_CLIENT_ID}:{NOTION_CLIENT_SECRET}"
    basic_auth = base64.b64encode(credentials.encode()).decode()

    async with httpx.AsyncClient() as client:
        logger.info("Exchanging auth code for access token...")
        resp = await client.post(
            TOKEN_URL,
            json={
                "grant_type": "authorization_code",
                "code": code,
                "redirect_uri": REDIRECT_URI,
            },
            headers={
                "Authorization": f"Basic {basic_auth}",
                "Content-Type": "application/json",
            },
        )

        if resp.status_code != 200:
            raise AppError("NOTION_TOKEN_EXCHANGE_FAILED", detail=resp.text)

        tokens = resp.json()

        if "access_token" not in tokens:
            raise AppError("NOTION_TOKEN_EXCHANGE_FAILED", detail="No access_token in response")

        logger.info(
            "Notion authenticated. Workspace: %s",
            tokens.get("workspace_name", "unknown"),
        )
        return tokens

# --- Token persistence ---

def _save_token(token_data: dict) -> None:
    """Save Notion token to disk."""
    TOKEN_FILE.write_text(json.dumps(token_data, indent=2))
    logger.info("Notion token saved.")


def _load_token() -> Optional[dict]:
    """Load saved token. Returns None if not found or corrupt."""
    if not TOKEN_FILE.exists():
        logger.warning("Token file does not exist")
        return None
    try:
        data = json.loads(TOKEN_FILE.read_text())
        if "access_token" in data:
            return data
    except (json.JSONDecodeError):
        logger.warning("Corrupt token file, will re-authenticate.")


def clear_token() -> None:
    """Delete stored token (forces re-authentication on next run)."""
    if TOKEN_FILE.exists():
        TOKEN_FILE.unlink()
        logger.info("Notion token cleared.")


# --- Main entry point ---

async def authenticate() -> str:
    """
    Get a valid Notion access token.

    If a token is stored locally, returns it.
    Otherwise, opens the browser for the user to log into Notion.

    Returns:
        The access_token string.
    """
    if not NOTION_CLIENT_ID or not NOTION_CLIENT_SECRET:
        raise AppError("NOTION_NOT_CONFIGURED")

    # Check for existing token
    stored = _load_token()
    if stored:
        logger.info("Using stored Notion token.")
        return stored["access_token"]

    # No token — run the browser login flow
    state = secrets.token_hex(16)

    params = {
        "client_id": NOTION_CLIENT_ID,
        "response_type": "code",
        "owner": "user",
        "redirect_uri": REDIRECT_URI,
        "state": state,
    }
    auth_url = f"{AUTHORIZE_URL}?{urlencode(params)}"

    logger.info("Opening browser for Notion login...")
    webbrowser.open(auth_url)

    # Wait for the redirect callback
    code = _wait_for_callback(expected_state=state)

    # Exchange code for token
    token_data = await _exchange_code(code)
    _save_token(token_data)

    return token_data["access_token"]
