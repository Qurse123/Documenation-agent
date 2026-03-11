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

