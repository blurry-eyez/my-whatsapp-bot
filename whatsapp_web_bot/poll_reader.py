import time
import re
from datetime import datetime
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from driver import get_driver

# --- CONFIGURATION ---
TARGET_BATCHES = ["Batch 22", "Batch 23", "Batch 24", "Batch 25"]

def get_todays_poll_title():
    today = datetime.now().strftime("%d/%m/%Y")
    return f"Whole day Absent for {today}"

def clean_phone(text):
    text = text.replace("~", "").strip()
    digits_only = re.sub(r"\D", "", text)
    if text.startswith("+") and len(digits_only) > 9:
        return digits_only
    return text

def parse_count(text):
    match = re.search(r'\d+', text)
    return int(match.group()) if match else 0

def find_scrollable_element(driver, parent_container):
    """
    Scans the parent container to find the actual scrollable DIV.
    Returns the WebElement that has a scrollbar.
    """
    # 1. Try generic copyable-area first (Standard WhatsApp)
    try:
        candidates = parent_container.find_elements(By.XPATH, ".//div[contains(@class, 'copyable-area')]")
        if candidates:
            # Return the last one (usually the top-most view)
            return candidates[-1]
    except:
        pass

    # 2. Fallback: Search ALL divs for one that is scrollable
    # This is heavy but 100% accurate.
    script = """
    var parent = arguments[0];
    var allDivs = parent.getElementsByTagName('div');
    for (var i = 0; i < allDivs.length; i++) {
        var d = allDivs[i];
        if (d.scrollHeight > d.clientHeight && d.clientHeight > 0) {
            return d;
        }
    }
    return null;
    """
    return driver.execute_script(script, parent_container)

def read_poll_votes():
    driver = get_driver()
    wait = WebDriverWait(driver, 20)
    final_votes = []
    
    target_title = get_todays_poll_title()
    print(f"[Poll] Target: '{target_title}'")

    try:
        # --- PHASE 1: OPEN SIDEBAR ---
        poll_card = wait.until(EC.presence_of_element_located(
            (By.XPATH, f'//div[contains(@aria-label, "{target_title}")]')
        ))
        driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});", poll_card)
        time.sleep(1)

        message_bubble = poll_card.find_element(By.XPATH, "./ancestor::div[contains(@class, 'message-out') or contains(@class, 'message-in') or @data-id][1]")
        view_votes_btn = message_bubble.find_element(By.XPATH, ".//div[text()='View votes'] | .//button[.//div[text()='View votes']]")
        driver.execute_script("arguments[0].click();", view_votes_btn)
        
        print("[Poll] Sidebar Opening...")
        time.sleep(3) 

        # --- PHASE 2: METRICS ---
        # Get the main sidebar wrapper (the Drawer)
        # We look for the "Poll details" header to anchor ourselves
        try:
            header = wait.until(EC.presence_of_element_located((By.XPATH, "//div[contains(@title, 'Poll details')] | //span[text()='Poll details']")))
            sidebar_drawer = header.find_element(By.XPATH, "./ancestor::div[contains(@class, 'copyable-area')]/..")
        except:
            print("[!] Critical: Sidebar structure changed.")
            return []

        # Find the scrollable box for the MAIN list
        main_scroll_box = find_scrollable_element(driver, sidebar_drawer)
        if not main_scroll_box:
            print("[!] Critical: Could not find main scroll box.")
            return []

        # --- PHASE 3: BATCH PROCESSING ---
        
        for batch_name in TARGET_BATCHES:
            print(f"\n--- Processing: {batch_name} ---")
            
            # Reset scroll
            driver.execute_script("arguments[0].scrollTop = 0", main_scroll_box)
            time.sleep(0.5)
            
            # Find Batch Header
            try:
                batch_header = None
                for _ in range(5):
                    try:
                        batch_header = main_scroll_box.find_element(By.XPATH, f".//span[contains(text(), '{batch_name}')]")
                        break
                    except:
                        driver.execute_script("arguments[0].scrollTop += 400", main_scroll_box)
                        time.sleep(0.5)
                
                if not batch_header:
                    print(f"   [!] Header not found (0 votes).")
                    continue
                    
                driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});", batch_header)
                time.sleep(1)
                
                # Metrics
                container = batch_header.find_element(By.XPATH, "./ancestor::div[2]") 
                count_element = container.find_element(By.XPATH, ".//span[contains(text(), 'votes')]")
                batch_expected = parse_count(count_element.text)
                print(f"   [Metrics] Expected: {batch_expected}")
            except:
                print(f"   [!] Error reading metrics.")
                continue

            if batch_expected == 0: continue

            # Check for See All
            try:
                see_all_btn = container.find_element(By.XPATH, ".//button[.//span[contains(text(), 'See all')]]")
                has_see_all = True
            except:
                has_see_all = False

            extracted_names = []

            if has_see_all:
                print("   [Mode] Drill-down...")
                driver.execute_script("arguments[0].click();", see_all_btn)
                time.sleep(3) # Wait for animation
                
                try:
                    # --- CRITICAL FIX: FIND THE *NEW* SCROLLABLE DIV ---
                    # When 'See all' opens, it's a new layer. We must find the SCROLLABLE div inside that layer.
                    # We look for the sidebar drawer again (it might be the same parent or a new one)
                    # A robust way is to find the LAST copyable-area added to DOM
                    
                    sub_scroll = None
                    # Retry finding the scrollable element a few times as DOM settles
                    for _ in range(3):
                        # We search the entire body for the active drawer
                        sub_scroll = find_scrollable_element(driver, driver.find_element(By.TAG_NAME, "body"))
                        # Verify this is NOT the main_scroll_box (it should be different)
                        if sub_scroll and sub_scroll != main_scroll_box:
                            break
                        time.sleep(1)
                    
                    if not sub_scroll:
                        print("   [!] Could not find 'See all' scroll container. Using main fallback.")
                        sub_scroll = main_scroll_box

                    # --- SMART SCRAPER WITH FIXED SCROLL ---
                    attempts = 0
                    while len(extracted_names) < batch_expected and attempts < 10:
                        new_names = scrape_virtual_list_items(driver, sub_scroll)
                        
                        # Merge Unique
                        current_set = set(extracted_names)
                        for n in new_names: current_set.add(n)
                        extracted_names = list(current_set)
                        
                        if len(extracted_names) >= batch_expected:
                            break
                        
                        print(f"      -> Found {len(extracted_names)}/{batch_expected}... Scrolling (Attempt {attempts+1})")
                        
                        # --- ROBUST SCROLL ACTION ---
                        # 1. JS Scroll
                        driver.execute_script("arguments[0].scrollTop += 450", sub_scroll)
                        # 2. Keyboard Scroll (Force browser to recognize action)
                        try:
                            sub_scroll.click() # Focus
                            ActionChains(driver).send_keys(Keys.PAGE_DOWN).perform()
                        except: pass
                        
                        time.sleep(1.5) 
                        attempts += 1
                    
                    # Back
                    back_btn = driver.find_element(By.XPATH, "//button[@aria-label='Back']")
                    driver.execute_script("arguments[0].click();", back_btn)
                    time.sleep(2.5)
                    
                    # Refresh Main Ref
                    main_scroll_box = find_scrollable_element(driver, sidebar_drawer)
                    
                except Exception as e:
                    print(f"   [!] Error: {e}")
                    ActionChains(driver).send_keys(Keys.ESCAPE).perform()
            else:
                print("   [Mode] Inline...")
                extracted_names = scrape_inline_names(container, batch_name)

            found_count = len(extracted_names)
            if found_count == batch_expected:
                print(f"   [✓] MATCH: Found {found_count}/{batch_expected}")
            else:
                print(f"   [!] MISMATCH: Found {found_count}/{batch_expected}")
            
            for name in extracted_names:
                final_votes.append({
                    "name": name.replace("~", "").strip(),
                    "phone": clean_phone(name),
                    "option": batch_name,
                    "timestamp": "N/A"
                })

        # --- PHASE 4: CLOSE ---
        try:
            close_btn = driver.find_element(By.XPATH, "//button[@aria-label='Close']")
            driver.execute_script("arguments[0].click();", close_btn)
        except:
            ActionChains(driver).send_keys(Keys.ESCAPE).perform()

        print(f"\n[Final] Total Scraped: {len(final_votes)}")
        return final_votes

    except Exception as e:
        print(f"[!] Error: {e}")
        return []

def scrape_virtual_list_items(driver, scroll_element):
    collected_names = set()
    
    # Explicit XPaths from inspection
    XPATH_SAVED   = "./div/div[2]/div[1]/div/span"
    XPATH_UNSAVED = "./div/div[2]/div[1]/div[1]/span"
    
    items = scroll_element.find_elements(By.XPATH, ".//div[@role='listitem']")
    
    for item in items:
        name_found = None
        try:
            el = item.find_element(By.XPATH, XPATH_SAVED)
            name_found = el.text
        except: pass
            
        if not name_found:
            try:
                el = item.find_element(By.XPATH, XPATH_UNSAVED)
                name_found = el.text
            except: pass
        
        # Title Fallback (For bottom items)
        if not name_found:
            try:
                el = item.find_element(By.XPATH, ".//span[@title][@dir='auto']")
                name_found = el.get_attribute("title")
            except: pass
        
        if name_found:
            name_found = name_found.strip()
            if name_found and "Yesterday" not in name_found and "Today" not in name_found and "Admin" not in name_found:
                collected_names.add(name_found)
                
    return list(collected_names)

def scrape_inline_names(container, batch_name):
    # Strict inline parser
    raw_text = container.text
    lines = raw_text.split('\n')
    valid = []
    # Filters
    ignore = ["Poll details", "See all", "votes", "vote", " at ", "Select one", batch_name, "members voted"]
    
    for line in lines:
        line = line.strip()
        if len(line) < 2: continue
        
        # Filter out numbers that look like counts "19"
        if line.isdigit() and len(line) < 3: continue
        
        is_junk = False
        for junk in ignore:
            if junk.lower() in line.lower(): is_junk = True; break
        if re.search(r'\d{1,2}:\d{2}\s?[ap]m', line.lower()): is_junk = True
        
        if not is_junk:
            valid.append(line)
    return valid