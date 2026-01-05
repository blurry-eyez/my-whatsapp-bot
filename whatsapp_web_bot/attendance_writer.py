import os
import csv
from datetime import datetime
from fpdf import FPDF

REPORT_DIR = "reports"
if not os.path.exists(REPORT_DIR):
    os.makedirs(REPORT_DIR)

def clean_text(text):
    """
    Sanitizes text for FPDF (Latin-1).
    """
    if not text: return "Unknown"
    
    # Map common special chars to ASCII
    replacements = {
        '\u202f': ' ', '’': "'", '“': '"', '”': '"', '–': '-',
        '~': '', '…': '...'
    }
    for old, new in replacements.items():
        text = text.replace(old, new)
    
    # Filter non-latin characters
    try:
        return text.encode('latin-1', 'replace').decode('latin-1')
    except:
        return ''.join([c if ord(c) < 128 else '?' for c in text])

class PDF(FPDF):
    def header(self):
        self.set_font('Arial', 'B', 15)
        self.cell(0, 10, 'Daily Attendance Report', 0, 1, 'C')
        self.ln(5)

    def footer(self):
        self.set_y(-15)
        self.set_font('Arial', 'I', 8)
        self.cell(0, 10, f'Page {self.page_no()}', 0, 0, 'C')

def generate_daily_pdf(votes):
    # 1. Generate Timestamped Filenames
    now = datetime.now()
    date_str = now.strftime("%d-%m-%Y")
    time_str = now.strftime("%H%M") # e.g., 1430
    
    filename_base = f"Daily_Absent_Report_{date_str}_{time_str}"
    path_pdf = os.path.join(REPORT_DIR, f"{filename_base}.pdf")
    path_csv = os.path.join(REPORT_DIR, f"{filename_base}.csv")

    # 2. CSV Backup
    try:
        with open(path_csv, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(["Batch", "Name", "Phone"])
            for v in votes:
                writer.writerow([v['option'], v['name'], v['phone']])
        print(f"[Report] CSV Saved: {path_csv}")
    except Exception as e:
        print(f"[!] CSV Failed: {e}")

    # 3. PDF Generation
    try:
        pdf = PDF()
        pdf.add_page()
        pdf.set_font("Arial", size=12)

        pdf.cell(0, 10, f"Date: {date_str} (Generated at {now.strftime('%I:%M %p')})", ln=True, align='C')
        pdf.ln(5)

        total_absent = len(votes)
        pdf.set_font("Arial", 'B', 12)
        pdf.cell(0, 10, f"Total Absent: {total_absent}", ln=True)
        pdf.ln(5)

        # Grouping
        grouped = {}
        target_batches = ["Batch 22", "Batch 23", "Batch 24", "Batch 25"]
        for b in target_batches: grouped[b] = []
        
        for v in votes:
            opt = v.get('option', 'Other')
            if opt in grouped: grouped[opt].append(v)
            else: 
                if 'Other' not in grouped: grouped['Other'] = []
                grouped['Other'].append(v)

        for batch, voters in grouped.items():
            if not voters: continue
                
            # Batch Header
            pdf.set_fill_color(220, 230, 255)
            pdf.set_font("Arial", 'B', 12)
            safe_batch = clean_text(batch)
            pdf.cell(0, 10, f"{safe_batch} ({len(voters)})", ln=True, fill=True)
            
            # Table Header
            pdf.set_font("Arial", 'B', 10)
            pdf.set_fill_color(240, 240, 240)
            pdf.cell(15, 8, "#", 1, 0, 'C', True)
            pdf.cell(110, 8, "Name", 1, 0, 'L', True)
            pdf.cell(65, 8, "Phone / ID", 1, 1, 'L', True)

            # Rows
            pdf.set_font("Arial", size=10)
            for i, voter in enumerate(voters, 1):
                name = clean_text(voter.get('name', ''))
                phone = clean_text(voter.get('phone', ''))
                
                pdf.cell(15, 8, str(i), 1, 0, 'C')
                pdf.cell(110, 8, name, 1, 0, 'L')
                pdf.cell(65, 8, phone, 1, 1, 'L')
            
            pdf.ln(5)

        pdf.output(path_pdf)
        print(f"[Report] PDF Saved: {path_pdf}")
        return os.path.abspath(path_pdf)

    except Exception as e:
        print(f"[!] PDF Generation Failed: {e}")
        return None