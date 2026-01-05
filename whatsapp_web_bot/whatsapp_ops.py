import time
import os
from datetime import datetime, timedelta  # Added timedelta
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import StaleElementReferenceException, TimeoutException
from driver import get_driver
from config import GROUP_NAME, ADMIN_NUMBER

def filter_bmp(text):
    """Removes emojis and characters that crash Chrome/Selenium"""
    return ''.join(c for c in text if c <= '\uFFFF')

def open_chat(chat_name_or_number):
    driver = get_driver()
    wait = WebDriverWait(driver, 30)
    
    try:
        search_box = wait.until(
            EC.presence_of_element_located((By.XPATH, '//div[@contenteditable="true"][@role="textbox" and @data-tab="3"]'))
        )
        search_box.click()
        search_box.send_keys(Keys.CONTROL + "a")
        search_box.send_keys(Keys.BACKSPACE)
        time.sleep(1)
        search_box.send_keys(chat_name_or_number)
        time.sleep(2)
        search_box.send_keys(Keys.ENTER)
        wait.until(EC.presence_of_element_located((By.XPATH, '//footer//div[@contenteditable="true"]')))
        print(f"[✓] Opened chat: {chat_name_or_number}")
    except Exception as e:
        print(f"[!] Failed to open chat '{chat_name_or_number}': {e}")

def send_message(text):
    driver = get_driver()
    safe_text = filter_bmp(text)
    
    for attempt in range(3):
        try:
            box = driver.find_element(By.XPATH, '//footer//div[@contenteditable="true"][@role="textbox"]')
            box.click()
            for line in safe_text.split('\n'):
                box.send_keys(line)
                box.send_keys(Keys.SHIFT + Keys.ENTER)
            time.sleep(1)
            box.send_keys(Keys.ENTER)
            print(f"[✓] Message sent")
            return
        except StaleElementReferenceException:
            time.sleep(1)
        except Exception as e:
            print(f"[!] Failed to send message: {e}")
            return

def send_document(file_path):
    driver = get_driver()
    wait = WebDriverWait(driver, 20)
    abs_path = os.path.abspath(file_path)
    
    try:
        print(f"[...] Sending file: {os.path.basename(file_path)}")
        
        # 1. Click Attach
        attach_btn = wait.until(EC.presence_of_element_located(
            (By.XPATH, '//div[@aria-label="Attach"] | //button[@aria-label="Attach"] | //span[@data-icon="plus"] | //span[@data-icon="clip"]')
        ))
        driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});", attach_btn)
        time.sleep(0.5)
        driver.execute_script("arguments[0].click();", attach_btn)
        time.sleep(1) 
        
        # 2. Send path to input
        file_input = driver.find_element(By.XPATH, '//input[@type="file"]')
        file_input.send_keys(abs_path)
        
        # 3. Wait for Preview Window & Icon
        print("[...] Waiting for preview window...")
        try:
            icon_element = wait.until(EC.visibility_of_element_located(
                (By.XPATH, '//span[@data-icon="wds-ic-send-filled"]')
            ))
        except TimeoutException:
            print("[!] Preview window timed out. Retrying with generic selector...")
            icon_element = wait.until(EC.visibility_of_element_located(
                (By.XPATH, '//div[@aria-label="Send"]')
            ))

        time.sleep(2) 

        # --- FINAL CLICK STRATEGY: Target Parent Button ---
        print("[...] Clicking Send button...")
        try:
            send_btn = icon_element.find_element(By.XPATH, "./ancestor::div[@role='button']")
            actions = ActionChains(driver)
            actions.move_to_element(send_btn).click().perform()
            
            time.sleep(2)
            if not driver.find_elements(By.XPATH, '//span[@data-icon="wds-ic-send-filled"]'):
                print(f"[✓] File sent successfully (ActionChains)")
                return

            print("[!] ActionChains didn't close window. Trying JS Click...")
            driver.execute_script("arguments[0].click();", send_btn)
            
        except Exception as e:
            print(f"[!] Target finding failed: {e}")
            driver.execute_script("arguments[0].click();", icon_element)

        time.sleep(2)
        print(f"[✓] File upload process finished")
        
    except Exception as e:
        print(f"[!] Failed to send document: {e}")
        try:
            driver.find_element(By.TAG_NAME, 'body').send_keys(Keys.ESCAPE)
        except:
            pass

def create_poll(title, options):
    driver = get_driver()
    wait = WebDriverWait(driver, 20)
    print(f"[...] Creating poll: {title}")

    try:
        attach_btn = wait.until(EC.presence_of_element_located(
            (By.XPATH, '//div[@aria-label="Attach"] | //button[@aria-label="Attach"] | //span[@data-icon="plus"] | //span[@data-icon="clip"]')
        ))
        driver.execute_script("arguments[0].click();", attach_btn)
        time.sleep(1)

        poll_btn = wait.until(EC.presence_of_element_located(
            (By.XPATH, '//div[@aria-label="Poll"] | //span[@data-icon="poll-type"] | //span[@data-icon="poll"]')
        ))
        driver.execute_script("arguments[0].click();", poll_btn)
        time.sleep(1.5)

        textboxes = wait.until(EC.presence_of_all_elements_located(
            (By.XPATH, '//div[@role="dialog"]//div[@contenteditable="true"]')
        ))
        
        textboxes[0].send_keys(filter_bmp(title))
        time.sleep(0.5)

        for i, opt in enumerate(options):
            current_boxes = driver.find_elements(By.XPATH, '//div[@role="dialog"]//div[@contenteditable="true"]')
            idx = i + 1 if i + 1 < len(current_boxes) else -1
            current_boxes[idx].send_keys(filter_bmp(opt))
            time.sleep(0.3)

        send_btn = wait.until(EC.element_to_be_clickable(
            (By.XPATH, '//span[@data-icon="send"] | //div[@aria-label="Send"]')
        ))
        send_btn.click()
        print(f"[✓] Poll sent")
        time.sleep(2)

    except Exception as e:
        print(f"[!] Poll creation failed for '{title}': {e}")
        try:
            driver.find_element(By.TAG_NAME, 'body').send_keys(Keys.ESCAPE)
        except:
            pass

def run_evening_routine():
    print("--- Running Evening Routine ---")
    open_chat(GROUP_NAME)
    
    # Calculate TOMORROW'S date
    tomorrow = datetime.now() + timedelta(days=1)
    tomorrow_str = tomorrow.strftime("%d/%m/%Y")
    tomorrow_short = tomorrow.strftime("%d/%m")

    # Create Polls for Tomorrow
    create_poll(f"Vote for {tomorrow_str}", ["Breakfast", "No Dinner"])
    create_poll(f"Whole day Absent for {tomorrow_str}", ["Batch 22", "Batch 23", "Batch 24", "Batch 25"])
    
    # Update message to reflect correct deadline
    send_message(f"Votes are counted only till 8:00 AM tomorrow ({tomorrow_short}).")