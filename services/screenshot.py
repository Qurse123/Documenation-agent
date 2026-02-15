import base64
from io import BytesIO
from datetime import datetime
from PIL import ImageGrab
from memory.state import Screenshot


def capture_screenshot() -> Screenshot:
    """
    Capture the current screen and return it as in-memory base64 data.
    Nothing is written to disk — the image stays in memory and flows
    directly to the LLM and then to Notion.
    """
    image = ImageGrab.grab()

    # Encode to PNG bytes in memory
    buffer = BytesIO()
    image.save(buffer, format="PNG")
    b64_data = base64.b64encode(buffer.getvalue()).decode("utf-8")

    return {
        "image_data": b64_data,
        "timestamp": datetime.now().isoformat(),
        "description": "",
    }
