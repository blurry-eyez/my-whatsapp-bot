import time
import pandas as pd
from db import get_db, init_db
from whatsapp_ops import run_evening_routine
from main import job_morning_report

def check_database():
    print("\n--- DATABASE CONTENT ---")
    con = get_db()
    try:
        df = pd.read_sql_query("SELECT * FROM attendance", con)
        if df.empty:
            print("[!] Database is empty.")
        else:
            print(df)
    except Exception as e:
        print(f"[!] Error reading DB: {e}")
    finally:
        con.close()
    print("------------------------\n")

def menu():
    print("\n=== SYSTEM TEST MENU ===")
    print("1. Test Evening Routine (Send Polls)")
    print("2. Test Morning Routine (Read Polls -> Save DB -> Send PDF)")
    print("3. Check Database Records")
    print("4. Exit")
    
    choice = input("Enter choice (1-4): ")
    
    if choice == '1':
        print("\n[TEST] Running Evening Routine...")
        try:
            run_evening_routine()
            print("[✓] Evening routine finished.")
        except Exception as e:
            print(f"[!] Error: {e}")

    elif choice == '2':
        print("\n[TEST] Running Morning Routine...")
        print("Note: This requires a poll titled 'Whole day Absent for [Today]' to exist.")
        try:
            job_morning_report()
            print("[✓] Morning routine finished.")
        except Exception as e:
            print(f"[!] Error: {e}")

    elif choice == '3':
        check_database()

    elif choice == '4':
        return False
    
    return True

if __name__ == "__main__":
    init_db()
    while menu():
        pass