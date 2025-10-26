from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

class ElementActions:
    def __init__(self, driver):
        self.driver = driver

    def _locator(self, by, value):
        strategies = {
            "id": By.ID,
            "css": By.CSS_SELECTOR,
            "xpath": By.XPATH,
            "name": By.NAME,
            "class": By.CLASS_NAME,
            "tag": By.TAG_NAME
        }
        return strategies[by.lower()], value

    def find_element(self, by, value, timeout=10):
        return WebDriverWait(self.driver, timeout).until(
            EC.presence_of_element_located(self._locator(by, value))
        )

    def click(self, by, value, timeout=10):
        el = self.find_element(by, value, timeout)
        el.click()

    def send_keys(self, by, value, text, timeout=10):
        el = self.find_element(by, value, timeout)
        el.clear()
        el.send_keys(text)
