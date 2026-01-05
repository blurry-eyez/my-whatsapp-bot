# WhatsApp Poll Attendance Bot 🤖📊

A high-precision automation tool built with **Python** and **Selenium** to scrape, analyze, and report attendance data from WhatsApp Polls. 

This bot is specifically engineered to handle WhatsApp Web's complex DOM, including **virtual scrolling**, **dynamic loading**, and **nested "See all" modals**, ensuring 100% accuracy in vote capturing.

![Python](https://img.shields.io/badge/Python-3.10%2B-blue?style=flat&logo=python)
![Selenium](https://img.shields.io/badge/Selenium-4.x-43B02A?style=flat&logo=selenium)
![Status](https://img.shields.io/badge/Status-Production%20Ready-brightgreen)

## 🌟 Key Features

* **🎯 Targeted Poll Detection:** Automatically locates specific polls (e.g., "Whole day Absent for [Today]") within high-traffic groups.
* **📜 Virtual List Scraper:** Uses a **"Scroll & Collect"** algorithm to capture voters from WhatsApp's virtualized lists, ensuring contacts at the very bottom are never missed.
* **🔄 Smart Verification Loop:** Implements a self-correcting mechanism that compares scraped data against WhatsApp's official vote count. If numbers don't match, it automatically retries and drills down until they do.
* **🔍 Triple-Fallback Extraction:** Uses three robust strategies to extract names, ensuring compatibility with:
    * Saved Contacts (Standard DOM)
    * Unsaved Numbers (Alternative DOM)
    * Truncated Names (Title Attribute Extraction)
* **📄 Automated Reporting:** Generates professional **PDF** and **CSV** reports containing names, timestamps, and batch details, sanitized for encoding issues (emojis, special spaces).
* **🗄️ Database Integration:** Archives all attendance data into a **SQLite** database for historical tracking.

## 📂 Project Structure

```text
whatsapp-poll-bot/
├── poll_reader.py          # 🧠 CORE LOGIC: Scraper, Smart Loop, and Verification
├── attendance_writer.py    # 📄 PDF/CSV Generator with encoding sanitization
├── db.py                   # 🗄️ SQLite Database handler
├── driver.py               # 🔧 Selenium WebDriver configuration
├── test_read_report.py     # 🚀 Main entry point / Orchestrator
├── requirements.txt        # 📦 Python dependencies
└── reports/                # 📂 Output folder for generated reports



WhatsApp Poll Attendance Bot 🤖📊
A robust, automated Python bot that monitors WhatsApp Groups for specific "Absent" polls, scrapes voter data with pixel-perfect accuracy, saves records to a database, and generates daily PDF/CSV attendance reports.


🌟 Key Features
• Smart Poll Detection: Automatically locates the "Whole day Absent" poll for the current date.
• Virtual List Scraping: Handles WhatsApp's dynamic "virtual scrolling" to capture voters hidden deep in the DOM (fixing the "missing bottom items" issue).
• Triple-Fallback Strategy: Uses 3 distinct methods to extract names (Strict XPath, Title Attribute, and Text Parsing) to ensure 100% data capture.
• Self-Correcting Verification: The "Smart Loop" retries scraping automatically until the scraped count matches the poll's official vote count.
• Drill-Down Capability: Automatically clicks "See all", finds the correct scrollable container, and scrapes detailed lists for large batches.
• Robust Reporting: Generates timestamped PDF and CSV reports, handling emojis and special characters via Latin-1 sanitization.
• Automated Delivery: Hosts the report via a local tunnel (Cloudflare) and sends the link to the Admin on WhatsApp.


📂 Project Structure
├── attendance_writer.py    # Generates PDF and CSV reports with encoding fixes
├── db.py                   # SQLite database handler (saves/retrieves votes)
├── driver.py               # Selenium Webdriver configuration (Chrome)
├── poll_reader.py          # CORE LOGIC: Scraper, Smart Loop, and Validation
├── test_read_report.py     # Main entry point (Orchestrator script)
├── requirements.txt        # Python dependencies
└── reports/                # Output folder for generated PDFs and CSVs

🛠️ Prerequisites
1. Python 3.10+ installed.
2. Google Chrome browser installed.
3. Chromedriver matching your Chrome version (or let webdriver_manager handle it).
4. A WhatsApp Account logged in on the host machine.


📥 Installation
1. Clone this repository:
   git clone https://github.com/yourusername/whatsapp-poll-bot.git
   cd whatsapp-poll-bot


2. Install dependencies:
Create a requirements.txt with the following and run pip install -r requirements.txt:
  selenium
  fpdf
  webdriver_manager

3. Configure Chrome Profile:
Update driver.py to point to your Chrome User Data directory. This ensures you don't need to scan the QR code every time.
  # Example in driver.py
  options.add_argument("user-data-dir=C:\\Users\\YourName\\AppData\\Local\\Google\\Chrome\\User Data")

⚙️ Configuration
Open poll_reader.py to configure the target batches you want to track:
# Options matching the Poll Choices exactly
TARGET_BATCHES = ["Batch 22", "Batch 23", "Batch 24", "Batch 25"]



python test_read_report.py


What happens next?
1. Initialization: Chrome opens and loads WhatsApp Web.
2. Navigation: The bot opens the target group (e.g., "Rasodu").
3. Scanning: It finds today's poll (e.g., "Whole day Absent for 04/01/2026").
4. Scraping:
• It opens "View votes".
• It iterates through each batch.
• It checks the expected count (e.g., "19 votes").
• It scrapes, scrolls, and verifies until it finds all 19 voters.
5. Reporting: It generates a PDF/CSV in the reports/ folder.
6. Delivery: It sends the report link to the configured Admin contact.
🧠 Core Logic Explained
The "Smart Loop" (in poll_reader.py)
Standard scrapers fail on WhatsApp because elements are unloaded when scrolled off-screen. This project uses a verify-retry loop:

while len(extracted_names) < batch_expected and attempts < 10:
    # 1. Scrape visible items
    # 2. Scroll down specifically targeting the active container
    # 3. Merge new names with existing set
    # 4. Check if Count matches Expected

The "Triple Fallback" Strategy
To handle WhatsApp's DOM variations for saved vs. unsaved contacts:
1. Strategy A: Looks for strict div structure (Saved contacts).
2. Strategy B: Looks for alternative div structure (Unsaved contacts).
3. Strategy C: Extracts the title attribute from the span (Captures truncated names).


📄 License
This project is open-source and available for educational purposes.
Disclaimer: This bot uses Selenium to automate WhatsApp Web. Use responsibly and ensure you comply with WhatsApp's Terms of Service. Avoid spamming or rapid-fire actions that could flag your account.






