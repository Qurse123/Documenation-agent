from typing import TypedDict, List


class Screenshot(TypedDict):
    path: str
    timestamp: str
    description: str


class AudioRecording(TypedDict):
    path: str
    timestamp: str
    duration_seconds: float


class DocAgentState(TypedDict):
    # Dict-like: use string key "screenshots" to get the list, then .append(captured) on that list.
    screenshots: List[Screenshot]  ## list of Screenshot dicts (path, timestamp, description)
    transcript: str         ## voice transcipt  
    is_recording: bool      ## memory should presist only when is_recording is set to true    
    documentation: str      ## AI generated documenation based on screenshot + transcipt