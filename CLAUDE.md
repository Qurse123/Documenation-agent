# Doc Agent — Project context for Claude

## Project overview

Doc Agent is a Python app that records the user's screen (pyautogui) and voice, transcribes audio with Whisper, generates step-by-step documentation with GPT-4o Vision, and publishes to Notion via OAuth and the File Upload API. Tech stack: Python 3.x, async (asyncio), LangChain/OpenAI, Jinja2, httpx, pyautogui, sounddevice, NumPy. Optional: Stagehand/Playwright in `services/browser.py` for browser-based capture.

## Common commands

- **Run a full doc session (record → transcribe → generate → publish):** `python services/entrypoint/main.py` (then Ctrl+C to stop and trigger pipeline).
- **Run the API server:** `uvicorn services.APIs.api:app --reload`
- **Worker (idle process for externally triggered sessions):** `python worker.py`.
- **Environment:** Ensure `.env` has required vars; run from project root with venv activated (`source venv/bin/activate`).
- **Verification:** After editing the pipeline, run `python services/entrypoint/main.py` and trigger a short session with Ctrl+C to confirm docs and Notion publish.

## Architecture and conventions

**Directory map (source only):**

- `services/entrypoint/main.py` — Entry point for full session; `worker.py` — Idle worker.
- `services/APIs/api.py` — FastAPI server (used by the Electron frontend).
- `services/` — Screenshot (`screenshot.py`), audio (`audio.py`), browser (`browser.py`), doc generation (`doc_generator.py`), Notion publish (`notion_service.py`), Notion OAuth (`notion_auth.py`).
- `managers/session_manager.py` — Recording lifecycle (start/stop session, screenshot loop, transcript).
- `memory/state.py` — TypedDicts: `Screenshot`, `DocAgentState` (screenshots in memory as base64 PNG, not on disk).
- `prompts/doc_agent.jinja2` — LLM prompt template (transcript + screenshot metadata); images sent separately via Vision API.
- `Errorcodes/codes.py` — App error codes (e.g. NOTION_008, NOTION_009).

**Data flow:** SessionManager captures screenshots (with change detection) and audio → on stop: transcribe → doc_generator builds prompt from template and sends transcript + images to GPT-4o → notion_service uploads images, parses markdown to blocks, creates page.

**Conventions:** Async for I/O-bound work; `load_dotenv()` in services that need env; state is a single `DocAgentState` dict during a session.

## Non-default / project-specific rules

- **Single source of env:** Use project root `.env` only; do not rely on `venv/.env`.
- **Screenshots:** Stored in memory as base64 in `Screenshot["image_data"]`; never write screenshot PNGs to disk in the main flow.
- **Notion:** Doc generator must output `[Screenshot N]` on its own line for image insertion; `notion_service.py` uses regex to replace with Notion image blocks.
- **Prompt changes:** Edit `prompts/doc_agent.jinja2`; do not hardcode the documentation instructions in Python.

## Common gotchas

- **Required env vars:** `OPENAI_API_KEY` (or `MODEL_API_KEY`) for LLM and optional Stagehand; `NOTION_CLIENT_ID`, `NOTION_CLIENT_SECRET`, `NOTION_REDIRECT_URI` for Notion OAuth. Missing Notion vars cause auth to fail with messages pointing to `.env`.
- **macOS:** Screen capture uses pyautogui (and optionally Stagehand/Playwright); audio uses sounddevice — ensure mic permissions and correct device if needed.
- **Session state:** `DocAgentState` is created in `SessionManager.start_session()` and returned from `agent.stop()`; do not assume a global state object exists before `start_session()`.
