import os
from datetime import datetime
from PIL import ImageGrab
from typing import TYPE_CHECKING
from memory.state import Screenshot


# Directory to save screenshots
SCREENSHOT_DIR = "screenshots"


def ensure_screenshot_dir() -> None:
    """Create screenshots directory if it doesn't exist."""
    if not os.path.exists(SCREENSHOT_DIR):
        os.makedirs(SCREENSHOT_DIR)


def capture_screenshot() -> "Screenshot":
    """
    Capture the current screen and save it to disk.
    Returns a Screenshot dict with path, timestamp, and empty description.
    """
    ensure_screenshot_dir()
    
    # Generate timestamp and filename
    timestamp = datetime.now().isoformat()
    filename = f"screenshot_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
    filepath = os.path.join(SCREENSHOT_DIR, filename) ## join the path of the screenshot and the filename
    
    # Capture and save
    image = ImageGrab.grab()
    image.save(filepath)
    
    # Return Screenshot dict
    return {
        "path": filepath,
        "timestamp": timestamp,
        "description": ""  # To be filled by AI later
    }
