import logging
import os
import wave
from datetime import datetime
from typing import Optional

import numpy as np
import sounddevice as sd
from openai import (
    APIConnectionError,
    APIError,
    AuthenticationError,
    OpenAI,
    RateLimitError,
)

from Errorcodes.codes import (
    AppError,
    AUDIO_NO_DEFAULT_MIC,
    AUDIO_CHANNELS_UNSUPPORTED,
    AUDIO_SYSTEM_ACCESS,
    AUDIO_START_RECORDING,
    AUDIO_START_RECORDING_GENERIC,
    AUDIO_NO_RECORDING,
    TRANSCRIPTION_FILE_NOT_FOUND,
    TRANSCRIPTION_AUTH_FAILED,
    TRANSCRIPTION_RATE_LIMIT,
    TRANSCRIPTION_CONNECTION,
    TRANSCRIPTION_API_ERROR,
    TRANSCRIPTION_FILE_READ,
)
from memory.state import AudioRecording

logger = logging.getLogger(__name__)

# Directory to save audio files
AUDIO_DIR = "audio"

# Recording state
_recording = False
_frames = []
_stream: Optional[sd.InputStream] = None
_start_time: Optional[datetime] = None
_sample_rate = 44100
_channels = 1


def ensure_audio_dir() -> None:
    """Create audio directory if it doesn't exist."""
    if not os.path.exists(AUDIO_DIR):
        os.makedirs(AUDIO_DIR)


def is_recording() -> bool:
    """Check if recording is currently in progress."""
    return _recording


def _check_microphone_available() -> dict:
    """Verify a default input device exists and is usable. Returns device info dict. Raises AppError if not."""
    try:
        default_input = sd.query_devices(kind="input")
        if default_input is None:
            raise AppError(AUDIO_NO_DEFAULT_MIC)
        if default_input.get("max_input_channels", 0) < _channels:
            raise AppError(AUDIO_CHANNELS_UNSUPPORTED, channels=_channels)
        return default_input
    except sd.PortAudioError as e:
        raise AppError(AUDIO_SYSTEM_ACCESS) from e


def start_recording() -> None:
    """Start recording audio from microphone. Raises AppError if mic is unavailable."""
    global _recording, _frames, _stream, _start_time

    if _recording:
        return  # Already recording

    device_info = _check_microphone_available()
    logger.info(
        "Using input device: '%s' (index %s, %d ch, %.0f Hz)",
        device_info.get("name", "unknown"),
        device_info.get("index", "?"),
        device_info.get("max_input_channels", 0),
        device_info.get("default_samplerate", 0),
    )

    _recording = True
    _frames = []
    _start_time = datetime.now()

    def callback(indata, frames, time, status):
        if status: ## if status is truthy it will show you the status 
            logger.warning("Audio callback status: %s", status)
        if _recording:
            _frames.append(indata.copy())

    try:
        _stream = sd.InputStream(
            samplerate=_sample_rate,
            channels=_channels,
            callback=callback,
        )
        _stream.start()
    except sd.PortAudioError as e:
        _recording = False
        _stream = None
        raise AppError(AUDIO_START_RECORDING) from e
    except Exception as e:
        _recording = False
        _stream = None
        raise AppError(AUDIO_START_RECORDING_GENERIC, detail=e) from e

    logger.info("Audio recording started.")


def stop_recording() -> AudioRecording:
    """
    Stop recording and save audio to file.
    Returns an AudioRecording dict with path, timestamp, and duration.
    Raises AppError if no audio was recorded.
    """
    global _recording, _frames, _stream, _start_time

    _recording = False

    # Stop and close the stream properly
    if _stream is not None:
        _stream.stop()
        _stream.close()
        _stream = None

    # Handle empty recording
    if not _frames:
        raise AppError(AUDIO_NO_RECORDING)

    ensure_audio_dir()

    # Calculate duration
    end_time = datetime.now()
    duration = (end_time - _start_time).total_seconds() if _start_time else 0.0
    timestamp = _start_time.isoformat() if _start_time else end_time.isoformat()

    # Generate filename
    filename = f"recording_{end_time.strftime('%Y%m%d_%H%M%S')}.wav"
    filepath = os.path.join(AUDIO_DIR, filename)

    # Save as WAV file
    audio_data = np.concatenate(_frames, axis=0)

    rms = float(np.sqrt(np.mean(audio_data ** 2)))
    logger.info(
        "Audio stats — duration: %.1fs, frames: %d, RMS level: %.6f %s",
        duration,
        len(_frames),
        rms,
        "(near-silent — check mic permissions)" if rms < 0.001 else "",
    )

    with wave.open(filepath, 'wb') as wf:
        wf.setnchannels(_channels)
        wf.setsampwidth(2)  # 16-bit audio
        wf.setframerate(_sample_rate)
        wf.writeframes((audio_data * 32767).astype(np.int16).tobytes())

    logger.info("Recording saved to: %s", filepath)

    return {
        "path": filepath,
        "timestamp": timestamp,
        "duration_seconds": duration,
    }


def transcribe_audio(file_path: str) -> str:
    """
    Transcribe audio file using OpenAI Whisper API.
    Returns the transcript text.
    Raises AppError on API or file errors (auth, rate limit, network, etc.).
    """
    if not os.path.isfile(file_path):
        raise AppError(TRANSCRIPTION_FILE_NOT_FOUND, path=file_path)

    client = OpenAI()

    try:
        with open(file_path, "rb") as audio_file:
            transcript = client.audio.transcriptions.create(
                model="whisper-1",
                file=audio_file,
            )
        return transcript.text
    except AuthenticationError as e:
        raise AppError(TRANSCRIPTION_AUTH_FAILED) from e
    except RateLimitError as e:
        raise AppError(TRANSCRIPTION_RATE_LIMIT) from e
    except APIConnectionError as e:
        raise AppError(TRANSCRIPTION_CONNECTION) from e
    except APIError as e:
        raise AppError(TRANSCRIPTION_API_ERROR, detail=e) from e
    except OSError as e:
        raise AppError(TRANSCRIPTION_FILE_READ, detail=e) from e
