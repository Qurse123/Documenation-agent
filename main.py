# Doc Agent - Entry Point
from services.screenshot import capture_screenshot

# Test screenshot capture
print("Capturing screenshot...")
screenshot = capture_screenshot()
print(f"Saved to: {screenshot['path']}")
print(f"Timestamp: {screenshot['timestamp']}")
