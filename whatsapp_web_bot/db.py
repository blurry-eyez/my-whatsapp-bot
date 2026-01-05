import sqlite3
import pandas as pd
from datetime import datetime
from config import DB_FILE

def get_db():
    return sqlite3.connect(DB_FILE)

def init_db():
    con = get_db()
    cur = con.cursor()
    # Table to store every single absence record
    cur.execute("""
    CREATE TABLE IF NOT EXISTS attendance (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        date TEXT,
        name TEXT,
        phone TEXT,
        status TEXT
    )
    """)
    con.commit()
    con.close()
    print("[✓] Database initialized")

def save_daily_attendance(votes_data):
    """
    votes_data: list of dicts [{'name': '...', 'phone': '...', 'status': 'Absent'}]
    """
    if not votes_data:
        return

    con = get_db()
    cur = con.cursor()
    today = datetime.now().strftime("%d/%m/%Y")
    
    count = 0
    for voter in votes_data:
        # Check if already exists to avoid duplicates if run twice
        cur.execute("SELECT id FROM attendance WHERE date=? AND phone=?", (today, voter['phone']))
        if not cur.fetchone():
            cur.execute("INSERT INTO attendance (date, name, phone, status) VALUES (?, ?, ?, ?)",
                        (today, voter['name'], voter['phone'], voter.get('status', 'Absent')))
            count += 1
            
    con.commit()
    con.close()
    print(f"[✓] Saved {count} new records to database.")

def get_monthly_data(month_str):
    """
    month_str: Format 'MM/YYYY' (e.g., '01/2026')
    Returns a pandas DataFrame
    """
    con = get_db()
    # Filter by date string containing the month/year
    query = f"SELECT date, name, phone, status FROM attendance WHERE date LIKE '%/{month_str}'"
    df = pd.read_sql_query(query, con)
    con.close()
    return df