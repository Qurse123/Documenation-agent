from typing import TypedDict, List


class Screenshot(TypedDict):
    path: str
    timestamp: str
    description: str


class DocAgentState(TypedDict):
    screenshots: List[str]  ## bunch of urls 
    transcript: str         ## voice transcipt  
    is_recording: bool      ## memory should presist only when is_recording is set to true    
    documentation: str      ## AI generated documenation based on screenshot + transcipt