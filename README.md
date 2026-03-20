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
- `NOTION_TOKEN` — your Notion integration secret (see below)
- `NOTION_PAGE_ID` — (optional) ID of the Notion page to post docs under

**3. Create a Notion integration**
1. Go to [notion.so/my-integrations](https://www.notion.so/my-integrations)
2. Click **New integration** → give it a name → click **Submit**
3. Copy the **Internal Integration Secret** → paste as `NOTION_TOKEN` in `.env`

**4. Share a Notion page with your integration**
1. Open any Notion page where you want docs to appear
2. Click `···` (top right) → **Connect to** → select your integration
3. Copy the page ID from the URL (the part after the last `/`, before `?`) → paste as `NOTION_PAGE_ID` in `.env`

**5. Run**
```bash
# Terminal 1 — backend
source venv/bin/activate && uvicorn api:app --reload

# Terminal 2 — frontend
cd frontend && npm run electron:dev
```

The app opens as a floating overlay. The Notion status dot turns green once your token is detected. Click **Start Documentation Mode** to begin.

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
│  Notion MCP                                 │
│  - Creates/updates documentation pages      │
└─────────────────────────────────────────────┘
```

