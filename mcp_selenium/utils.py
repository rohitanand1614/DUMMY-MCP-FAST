import os, base64
from datetime import datetime

def timestamp():
    return datetime.now().strftime("%Y%m%d_%H%M%S")

def save_screenshot(driver, folder="screenshots", prefix="shot"):
    os.makedirs(folder, exist_ok=True)
    path = os.path.join(folder, f"{prefix}_{timestamp()}.png")
    driver.save_screenshot(path)
    return path

def encode_image(path):
    with open(path, "rb") as f:
        return base64.b64encode(f.read()).decode()
