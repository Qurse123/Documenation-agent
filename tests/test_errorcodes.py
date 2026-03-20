"""
Tests for Errorcodes/codes.py — AppError class and message lookup.
"""
import pytest
from Errorcodes.codes import (
    AppError,
    AUDIO_NO_DEFAULT_MIC,
    AUDIO_CHANNELS_UNSUPPORTED,
    TRANSCRIPTION_FILE_NOT_FOUND,
    TRANSCRIPTION_FILE_READ,
    NOTION_NOT_CONFIGURED,
    NOTION_FILE_UPLOAD_FAILED,
)


def test_known_code_returns_message():
    err = AppError(AUDIO_NO_DEFAULT_MIC)
    assert "microphone" in str(err).lower()


def test_format_kwargs_interpolated():
    err = AppError(TRANSCRIPTION_FILE_NOT_FOUND, path="/tmp/audio.wav")
    assert "/tmp/audio.wav" in str(err)


def test_detail_kwarg_interpolated():
    err = AppError(TRANSCRIPTION_FILE_READ, detail="permission denied")
    assert "permission denied" in str(err)


def test_channels_kwarg_interpolated():
    err = AppError(AUDIO_CHANNELS_UNSUPPORTED, channels=2)
    assert "2" in str(err)


def test_unknown_code_falls_back_to_code_string():
    err = AppError("UNKNOWN_999")
    assert str(err) == "UNKNOWN_999"


def test_app_error_is_exception():
    err = AppError(NOTION_NOT_CONFIGURED)
    assert isinstance(err, Exception)


def test_code_attribute_accessible():
    err = AppError(AUDIO_NO_DEFAULT_MIC)
    assert err.code == AUDIO_NO_DEFAULT_MIC


def test_notion_upload_failed_with_detail():
    err = AppError(NOTION_FILE_UPLOAD_FAILED, detail="503 Service Unavailable")
    assert "503 Service Unavailable" in str(err)


def test_raising_app_error():
    with pytest.raises(AppError) as exc_info:
        raise AppError(AUDIO_NO_DEFAULT_MIC)
    assert exc_info.value.code == AUDIO_NO_DEFAULT_MIC
