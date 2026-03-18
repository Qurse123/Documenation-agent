"""
Central error codes for the application.
Raise AppError with a code; messages are looked up from ERROR_MESSAGES.
"""

# Audio error codes
AUDIO_NO_DEFAULT_MIC = "AUDIO_001"
AUDIO_CHANNELS_UNSUPPORTED = "AUDIO_002"
AUDIO_SYSTEM_ACCESS = "AUDIO_003"
AUDIO_START_RECORDING = "AUDIO_004"
AUDIO_START_RECORDING_GENERIC = "AUDIO_005"
AUDIO_NO_RECORDING = "AUDIO_006"

# Transcription error codes
TRANSCRIPTION_FILE_NOT_FOUND = "TRANSCRIPTION_001"
TRANSCRIPTION_AUTH_FAILED = "TRANSCRIPTION_002"
TRANSCRIPTION_RATE_LIMIT = "TRANSCRIPTION_003"
TRANSCRIPTION_CONNECTION = "TRANSCRIPTION_004"
TRANSCRIPTION_API_ERROR = "TRANSCRIPTION_005"
TRANSCRIPTION_FILE_READ = "TRANSCRIPTION_006"

# Notion error codes
NOTION_NOT_CONFIGURED = "NOTION_001"
NOTION_FILE_UPLOAD_FAILED = "NOTION_006"
NOTION_PAGE_CREATION_FAILED = "NOTION_007"

ERROR_MESSAGES = {
    AUDIO_NO_DEFAULT_MIC: (
        "No default microphone found. Please connect a microphone and set it as the default input."
    ),
    AUDIO_CHANNELS_UNSUPPORTED: (
        "Default microphone does not support {channels} channel(s). Check your audio device settings."
    ),

    AUDIO_START_RECORDING: (
        "Failed to start recording. Ensure the microphone is enabled and you have granted access."
    ),
    AUDIO_START_RECORDING_GENERIC: "Failed to start recording: {detail}",
    AUDIO_NO_RECORDING: (
        "No audio was recorded. Ensure the microphone was active and you started recording before stopping."
    ),
    TRANSCRIPTION_FILE_NOT_FOUND: "Audio file not found: {path}",
    TRANSCRIPTION_AUTH_FAILED: (
        "OpenAI API authentication failed. Check that OPENAI_API_KEY is set correctly in your .env file."
    ),
    TRANSCRIPTION_RATE_LIMIT: (
        "OpenAI API rate limit exceeded. Wait a moment and try again."
    ),
    TRANSCRIPTION_CONNECTION: (
        "Could not connect to OpenAI. Check your network connection and try again."
    ),
    TRANSCRIPTION_API_ERROR: "OpenAI API error: {detail}",
    TRANSCRIPTION_FILE_READ: "Could not read audio file: {detail}",
    # Notion errors
    NOTION_NOT_CONFIGURED: (
        "Notion not configured. Add NOTION_TOKEN to your .env file."
    ),
    NOTION_FILE_UPLOAD_FAILED: "Failed to upload screenshot to Notion: {detail}",
    NOTION_PAGE_CREATION_FAILED: "Failed to create Notion page: {detail}",
}


class AppError(Exception):
    """Application error with a specific code. Use codes from this module."""

    def __init__(self, code: str, **format_kwargs):
        self.code = code
        message = ERROR_MESSAGES.get(code, code)
        if format_kwargs:
            message = message.format(**format_kwargs)
        super().__init__(message)
