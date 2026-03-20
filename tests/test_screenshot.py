"""
Tests for services/screenshot.py — change detection logic and state reset.

pyautogui is not called here; we test the pure logic functions directly.
"""

import numpy as np

import services.screenshot as screenshot_module
from services.screenshot import _has_significant_change, reset, CHANGE_THRESHOLD


def setup_function():
    """Reset module state before each test."""
    reset()


# ---------------------------------------------------------------------------
# _has_significant_change
# ---------------------------------------------------------------------------

def test_identical_frames_returns_false():
    frame = np.full((100, 100, 3), 128, dtype=np.uint8)
    assert not _has_significant_change(frame, frame)


def test_black_vs_white_returns_true():
    black = np.zeros((100, 100, 3), dtype=np.uint8)
    white = np.full((100, 100, 3), 255, dtype=np.uint8)
    assert _has_significant_change(white, black)


def test_small_difference_below_threshold_returns_false():
    # diff per pixel = 5, mean_diff = 5/255 ≈ 0.0196 < CHANGE_THRESHOLD (0.02)
    current = np.full((10, 10, 3), 5, dtype=np.uint8)
    previous = np.zeros((10, 10, 3), dtype=np.uint8)
    assert not _has_significant_change(current, previous)


def test_difference_above_threshold_returns_true():
    # diff per pixel = 6, mean_diff = 6/255 ≈ 0.0235 > CHANGE_THRESHOLD (0.02)
    current = np.full((10, 10, 3), 6, dtype=np.uint8)
    previous = np.zeros((10, 10, 3), dtype=np.uint8)
    assert _has_significant_change(current, previous)


def test_single_pixel_change_in_large_frame_below_threshold():
    # One pixel changes a lot but the rest are identical → mean diff is tiny
    base = np.zeros((1000, 1000, 3), dtype=np.uint8)
    changed = base.copy()
    changed[0, 0] = [255, 255, 255]
    assert not _has_significant_change(changed, base)


def test_threshold_value_is_expected():
    # Guard against accidental threshold changes — 0.02 is the agreed value
    assert CHANGE_THRESHOLD == 0.02


# ---------------------------------------------------------------------------
# reset() — module state
# ---------------------------------------------------------------------------

def test_reset_clears_prev_frame():
    screenshot_module._prev_frame = np.zeros((10, 10, 3), dtype=np.uint8)
    reset()
    assert screenshot_module._prev_frame is None


def test_reset_on_already_none_state_is_safe():
    screenshot_module._prev_frame = None
    reset()  # should not raise
    assert screenshot_module._prev_frame is None
