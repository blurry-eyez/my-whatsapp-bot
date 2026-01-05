from bs4 import BeautifulSoup
from driver import get_driver
from datetime import datetime

def get_absent_voters():
    driver = get_driver()
    html = driver.page_source
    soup = BeautifulSoup(html, "lxml")

    voters = set()
    for span in soup.select("span[title]"):
        phone = span.get("title")
        if phone and phone.startswith("+"):
            voters.add(phone.replace("+91", ""))

    return voters
