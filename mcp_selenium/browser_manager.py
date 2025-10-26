import os
import uuid
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options

class BrowserManager:
    def __init__(self):
        self.sessions: dict[str, webdriver.Chrome] = {}
        self.current_session: str | None = None

    def start_browser(self, browser: str, headless: bool = False, args=None):
        driver_path = os.getenv("SELENIUM_DRIVER_PATH", "./drivers/chromedriver.exe")
        binary_path = os.getenv("SELENIUM_BINARY_PATH")

        options = Options()
        if headless:
            options.add_argument("--headless=new")
        if args:
            for arg in args:
                options.add_argument(arg)
        if binary_path:
            options.binary_location = binary_path

        service = Service(driver_path)
        driver = webdriver.Chrome(service=service, options=options)

        session_id = f"{browser}_{uuid.uuid4().hex[:8]}"
        self.sessions[session_id] = driver
        self.current_session = session_id
        return session_id

    def get_active_driver(self):
        if not self.current_session or self.current_session not in self.sessions:
            raise RuntimeError("No active browser session")
        return self.sessions[self.current_session]

    def close_active_session(self):
        if self.current_session:
            driver = self.sessions.pop(self.current_session, None)
            if driver:
                driver.quit()
            self.current_session = None
