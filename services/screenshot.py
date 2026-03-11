"""
Screenshot Service
==================
Captures the user's actual macOS screen using pyautogui.
Includes pixel-diff change detection so the session manager
can skip near-duplicate frames.
"""

import base64
import io
import logging
from datetime import datetime
from typing import Optional

import numpy as np
import pyautogui

from memory.state import Screenshot

logger = logging.getLogger(__name__)

_prev_frame: Optional[np.ndarray] = None
CHANGE_THRESHOLD = 0.05 ## subject to change if 5% of pixels have changed


def _has_significant_change(current: np.ndarray, previous: np.ndarray) -> bool:
    """Compare two frames; return True when the mean absolute pixel
    difference (normalised to 0-1) exceeds CHANGE_THRESHOLD."""
    diff = np.abs(current.astype(np.float32) - previous.astype(np.float32))
    mean_diff = diff.mean() / 255.0
    logger.debug("Frame diff: %.4f (threshold: %.4f)", mean_diff, CHANGE_THRESHOLD)
    return mean_diff > CHANGE_THRESHOLD


async def capture_screenshot() -> Optional[Screenshot]:
    """Grab the macOS screen via pyautogui.

    Returns a Screenshot dict, or None if the frame is too similar
    to the previous capture (no significant change detected).
    """
    global _prev_frame

    img = pyautogui.screenshot()
    frame = np.array(img)

    if _prev_frame is not None and not _has_significant_change(frame, _prev_frame):
        logger.debug("Frame skipped — no significant change.")
        return None

    _prev_frame = frame

    buf = io.BytesIO()
    img.save(buf, format="PNG")
    b64_data = base64.b64encode(buf.getvalue()).decode("utf-8")

    return {
        "image_data": b64_data,
        "timestamp": datetime.now().isoformat(),
        "description": "",
    }


def reset() -> None:
    """Clear the previous frame (call at session start)."""
    global _prev_frame
    _prev_frame = None
