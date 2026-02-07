## Overview
AI Documentation Agent

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
│  - Stagehand for browser interaction        │
│  - Screenshot capture                       │
│  - Audio transcription (Whisper?)           │
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

