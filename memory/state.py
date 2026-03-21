from typing import TypedDict, List


class Screenshot(TypedDict):
    image_data: str              # Base64-encoded PNG image data (kept in memory, never saved to disk)
    timestamp: str
    description: str


class AudioRecording(TypedDict):
    path: str
    timestamp: str
    duration_seconds: float


class DocAgentState(TypedDict):
    screenshots: List[Screenshot]  ## list of Screenshot dicts (image_data, timestamp, description)
    transcript: str                ## voice transcript
    documentation: str             ## AI generated documentation based on screenshot + transcript
    notion_page_url: str           ## URL of the published Notion page