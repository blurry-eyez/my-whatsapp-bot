import time
import schedule
from datetime import datetime
from db import init_db, save_daily_attendance
from driver import get_driver
from config import GROUP_NAME, ADMIN_NUMBER
from poll_reader import read_poll_votes
from attendance_writer import generate_daily_pdf
from server import get_public_link  # Updated import
import whatsapp_ops as ops

def job_evening_polls():
    """Runs at 8:00 PM"""
    print(f"\n[JOB] Starting Evening Routine ({datetime.now().strftime('%H:%M')})")
    try:
        ops.run_evening_routine()
        print("[✓] Evening routine finished.")
    except Exception as e:
        print(f"[!] Evening job failed: {e}")

def job_morning_report():
    """Runs at 8:30 AM"""
    print(f"\n[JOB] Starting Morning Report ({datetime.now().strftime('%H:%M')})")
    try:
        # 1. Open Group & Read Data
        ops.open_chat(GROUP_NAME)
        time.sleep(5) 
        votes = read_poll_votes()
        
        if not votes:
            print("[!] No votes found today.")
            return

        # 2. Save to Database
        save_daily_attendance(votes)

        # 3. Generate PDF
        pdf_path = generate_daily_pdf(votes)
        
        if pdf_path:
            # 4. Host & Get Link
            print("[...] Hosting file via Cloudflare...")
            link = get_public_link(pdf_path)
            
            if link:
                # 5. Send Link to Admin
                ops.open_chat(ADMIN_NUMBER)
                
                msg = (
                    f"🔔 *Absentee Report - {datetime.now().strftime('%d/%m/%Y')}*\n"
                    f"-------------------\n"
                    f"📄 Download PDF:\n"
                    f"{link}"
                )
                ops.send_message(msg)
                print("[✓] Report link sent to Admin.")
            else:
                print("[!] Server/Tunnel failed, could not send report.")

    except Exception as e:
        print(f"[!] Morning job failed: {e}")

def main():
    print("[INIT] Starting WhatsApp Attendance Bot...")
    init_db()
    get_driver()
    
    # Schedule Jobs
    schedule.every().day.at("20:00").do(job_evening_polls)
    schedule.every().day.at("08:30").do(job_morning_report)

    print("[✓] Bot is online and waiting.")
    print(f"    - Current Time: {datetime.now().strftime('%H:%M')}")

    while True:
        schedule.run_pending()
        time.sleep(30)

if __name__ == "__main__":
    main()