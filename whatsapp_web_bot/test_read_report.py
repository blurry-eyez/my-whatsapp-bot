import time
import os
from datetime import datetime
from db import init_db, save_daily_attendance
from poll_reader import read_poll_votes
from attendance_writer import generate_daily_pdf
import whatsapp_ops as ops
from server import get_public_link  # Import our new server module
from config import GROUP_NAME, ADMIN_NUMBER

def test_morning_workflow():
    print("=== TESTING OPTION 2: SERVER + CLOUDFLARE ===")
    
    init_db()

    # 1. Open Chat
    print(f"\n[Step 1] Opening Group '{GROUP_NAME}'...")
    try:
        ops.open_chat(GROUP_NAME)
    except Exception as e:
        print(f"[!] Critical Error: {e}")
        return

    # 2. Read Votes
    print("\n[Step 2] Reading Poll Votes...")
    time.sleep(3)
    votes = read_poll_votes()
    
    if not votes:
        print("[!] No votes found.")
        return

    # 3. Save DB
    save_daily_attendance(votes)

    # 4. Generate PDF
    print("\n[Step 4] Generating PDF...")
    pdf_path = generate_daily_pdf(votes)
    
    if not pdf_path:
        print("[!] Failed to generate PDF.")
        return

    # 5. GET CLOUDFLARE LINK
    print("\n[Step 5] Starting Local Server & Tunnel...")
    # This might take 5-10 seconds the first time
    link = get_public_link(pdf_path)
    
    if not link:
        print("[!] Could not generate Cloudflare link.")
        return
    
    print(f"[✓] Generated Link: {link}")

    # 6. Send to Admin
    print(f"\n[Step 6] Sending Link to Admin ({ADMIN_NUMBER})...")
    try:
        ops.open_chat(ADMIN_NUMBER)
        
        msg = (
            f"🔔 *Absentee Report Generated*\n"
            f"Time: {datetime.now().strftime('%H:%M:%S')}\n"
            f"-------------------\n"
            f"📄 Download Report:\n"
            f"{link}"
        )
        ops.send_message(msg)
            
    except Exception as e:
        print(f"[!] Error sending to admin: {e}")

    print("\n[✓] Test Complete.")
    print("-------------------------------------------------")
    print("⚠️  KEEP THIS TERMINAL OPEN!")
    print("The Cloudflare tunnel runs inside this script.")
    print("If you close this, the link will stop working.")
    input(">>> Press ENTER to stop the server and exit... <<<")

if __name__ == "__main__":
    test_morning_workflow()