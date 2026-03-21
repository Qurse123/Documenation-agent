## Overview
AI Documentation Agent — records your screen, generates step-by-step docs with GPT-4o Vision, and publishes them to Notion.

## Setup

**1. Clone and install**
```bash
git clone <repo-url> && cd doc-agent
python -m venv venv && source venv/bin/activate
pip install -r requirements.txt
cd frontend && npm install && cd ..
```

**2. Configure environment**
```bash
cp .env.example .env
```
Open `.env` and fill in:
- `OPENAI_API_KEY` — your OpenAI API key
- `NOTION_CLIENT_ID` — Notion OAuth Client ID
- `NOTION_CLIENT_SECRET` — Notion OAuth Client Secret
- `NOTION_REDIRECT_URI` — callback URL, must match your Notion settings exactly (example: `http://localhost:3000/callback`)

**3. Create a Notion public integration**
1. Go to [notion.so/my-integrations](https://www.notion.so/my-integrations)
2. Create a **Public** integration
3. Copy your **OAuth Client ID** and **OAuth Client Secret** into `.env`
4. Add your callback URL (for example `http://localhost:3000/callback`) to the integration's Redirect URIs
5. Set the exact same URL as `NOTION_REDIRECT_URI` in `.env`


**5. Run**
```bash
# Terminal 1 — backend
source venv/bin/activate && uvicorn api:app --reload

# Terminal 2 — frontend
cd frontend && npm run electron:dev
```

**6. Connect Notion once per app session**
1. In the floating app, click **Connect Notion**
2. Complete OAuth in the browser
3. Return to the app and wait for the Notion dot to turn green
4. Click **Start Documentation Mode**

If you see `ERR_CONNECTION_REFUSED` during OAuth callback, your backend is not running on the same host/port as `NOTION_REDIRECT_URI`.

---

## Releasing

1. Ensure all changes are merged to `main` and CI is green.
2. Create and push a version tag:
   ```bash
   git tag v1.0.0
   git push origin v1.0.0
   ```
3. Ensure you increment the tags in the (vX.Y.Z+1) format
4. GitHub Actions builds and packages the macOS `.dmg` automatically.
5. The release appears at your repo's **Releases** page.

> **Note:** The `.dmg` ships the Electron frontend. Users also need to run the Python backend locally (`uvicorn api:app --reload`). The app connects to `http://localhost:8000`.

---

## Architecture

```
┌─────────────────────────────────────────────┐
│  Frontend (Button UI)                       │
│  - Start/Stop documentation mode            │
└─────────────────────┬───────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────┐
│  Screen/Voice Capture Layer                 │          
│  - Screenshot capture using pyautogui       │
│  - Audio transcription using whisper        │
└─────────────────────┬───────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────┐
│  AI Agent (OpenAI)                          │
│  - Analyzes screenshots + transcript        │
│  - Generates structured documentation       │
└─────────────────────┬───────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────┐
│  Notion API                                 │
│  - Creates documentation pages              │
└─────────────────────────────────────────────┘
```

