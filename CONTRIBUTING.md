# Contributing to Doc Agent

Thanks for your interest in contributing! Doc Agent is a local tool that records your screen and audio, transcribes speech with Whisper, generates step-by-step docs with GPT-4o Vision, and publishes them to Notion. Everything runs on your machine — no hosted server required.

## Prerequisites

- **Python 3.10+**
- **Node.js 18+** (for the Electron frontend)
- **macOS** — screen capture (PyAutoGUI) and audio (sounddevice) are currently macOS-only
- **OpenAI API key** — used for GPT-4o Vision (doc generation) and Whisper (transcription)
- **Notion internal integration token** — create one at [notion.so/my-integrations](https://www.notion.so/my-integrations)

## Local dev setup

```bash
# 1. Fork the repo on GitHub, then clone your fork
git clone https://github.com/<your-username>/doc-agent.git
cd doc-agent

# 2. Create and activate a virtual environment
python -m venv venv
source venv/bin/activate

# 3. Install Python dependencies
pip install -r requirements.txt

# 4. Install frontend dependencies
cd frontend && npm install && cd ..

# 5. Configure environment
cp .env.example .env
# Edit .env and fill in:
#   OPENAI_API_KEY=...
#   NOTION_TOKEN=...
#   NOTION_PAGE_ID=... (optional — target Notion page)
```

### Running the app

**Backend API + frontend (recommended for development):**
```bash
uvicorn api:app --reload         # backend
cd frontend && npm run electron:dev   # frontend (separate terminal)
```

**One-shot session (no frontend):**
```bash
python main.py   # press Ctrl+C to stop recording and trigger the pipeline
```

**Idle worker (waits for external session triggers):**
```bash
python worker.py
```

> **macOS permissions:** On first run, grant microphone access and screen recording permissions when prompted. Check System Settings → Privacy & Security if capture fails.

## Project structure

```
doc-agent/
│   # Entry points (run these directly)
├── main.py                 # One-shot session: record → transcribe → generate → publish
├── worker.py               # Idle worker for externally triggered sessions
├── api.py                  # FastAPI server (used by the Electron frontend)
│
│   # Internal modules (imported by entry points, not run directly)
├── services/
│   ├── agent.py            # Main DocAgent orchestrator
│   ├── screenshot.py       # Screen capture with change detection
│   ├── audio.py            # Audio recording & Whisper transcription
│   ├── doc_generator.py    # Builds LLM prompt and calls GPT-4o
│   ├── notion_service.py   # Notion image upload + page creation
│   └── notion_auth.py      # Notion auth helpers
├── managers/
│   └── session_manager.py  # Recording lifecycle, screenshot loop
├── memory/
│   └── state.py            # TypedDicts: Screenshot, DocAgentState
├── prompts/
│   └── doc_agent.jinja2    # LLM prompt template
├── Errorcodes/
│   └── codes.py            # App error codes and messages
└── frontend/               # React + Electron UI
```

## Coding conventions

- **Async everywhere** — use `async`/`await` for all I/O-bound work.
- **Screenshots in memory only** — store as base64 in `Screenshot["image_data"]`; never write PNG files to disk in the main flow.
- **Notion image markers** — doc generator must output `[Screenshot N]` on its own line; `notion_service.py` replaces these with Notion image blocks via regex.
- **Prompt changes** — edit `prompts/doc_agent.jinja2`; don't hardcode documentation instructions in Python.
- **Single `.env`** — always load from the project root `.env`; don't rely on `venv/.env`.
- **Error codes** — add new error codes and messages to `Errorcodes/codes.py`; raise them with `AppError(CODE)`.

## Making changes

> **Do not push directly to this repository.** All contributions must come through a fork and pull request.

1. **Fork** the repo on GitHub (click "Fork" in the top-right corner).
2. **Clone your fork** (not the original repo):
   ```bash
   git clone https://github.com/<your-username>/doc-agent.git
   cd doc-agent
   ```
3. **Create a branch** off `main`:
   ```bash
   git checkout -b your-feature-or-fix
   ```
4. Make your changes, following the conventions above.
5. Test manually: run a short session with `python main.py`, press Ctrl+C, and confirm docs appear in Notion.
6. Push to **your fork** and open a pull request against `main` on the original repo with a clear description of what changed and why.

## Reporting bugs / requesting features

Open a [GitHub Issue](../../issues). For bugs, include:
- What you did
- What you expected
- What actually happened (paste any error output)
- Your OS version and Python version
