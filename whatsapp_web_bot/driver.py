from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options

import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CHROME_PROFILE = os.path.join(BASE_DIR, "chrome_profile")


_driver = None


def get_driver():
    global _driver

    if _driver is not None:
        return _driver

    options = Options()
    options.add_argument(f"--user-data-dir={CHROME_PROFILE}")
    options.add_argument("--profile-directory=Default")
    options.add_argument("--start-maximized")
    options.add_argument("--disable-notifications")
    options.add_argument("--disable-infobars")

    service = Service()

    _driver = webdriver.Chrome(
        service=service,
        options=options
    )

    _driver.get("https://web.whatsapp.com")
    return _driver
