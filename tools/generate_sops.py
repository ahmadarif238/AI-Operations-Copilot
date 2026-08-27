import os
import random
from datetime import datetime

# Try to import FPDF, fallback to text if not available
try:
    from fpdf import FPDF
    HAS_PDF = True
except ImportError:
    HAS_PDF = False
    print("FPDF not installed. Generating text files only. Run 'pip install fpdf' for PDFs.")

OUTPUT_DIR = "docs/sample_sops"
os.makedirs(OUTPUT_DIR, exist_ok=True)

SOP_TOPICS = [
    ("HR_001_Leave_Policy", "Human Resources", "Policy", """
    1. PURPOSE
    To define the guidelines for employee leave entitlements.
    
    2. SCOPE
    All full-time employees.
    
    3. POLICY
    - Annual Leave: 20 days per year.
    - Sick Leave: 10 days per year with medical certificate required for >2 days.
    - Maternity Leave: 12 weeks paid.
    - Bereavement: 3 days for immediate family.
    
    4. PROCEDURE
    Apply via the HR portal 2 weeks in advance for annual leave.
    """),
    ("IT_002_Access_Control", "IT", "Security", """
    1. PURPOSE
    To ensure secure access to company systems.
    
    2. PASSWORD POLICY
    - Minimum 12 characters.
    - Must verify MFA every 24 hours.
    - Changed every 90 days.
    
    3. ACCESS LEVELS
    - Level 1: General Staff (Email, Portal)
    - Level 2: Managers (Reports)
    - Level 3: Admins (System Config)
    """),
    ("FIN_003_Expense_Reimbursement", "Finance", "Procedure", """
    1. ELIGIBILITY
    Business related expenses pre-approved by manager.
    
    2. LIMITS
    - Meals: $50/day
    - Travel: Economy class only for flights under 6 hours.
    - Business class allowed for flights > 6 hours.
    
    3. PROCESS
    Submit receipts within 30 days of expense.
    """),
    ("OPS_004_Incident_Reporting", "Operations", "SOP", """
    1. TRIAGE
    - P1: System Down (Response: 15 mins)
    - P2: Feature Broken (Response: 1 hour)
    - P3: Minor Bug (Response: 24 hours)
    
    2. REPORTING
    Log all incidents in the AI Operations Copilot log endpoint.
    """),
    ("SAFE_005_Workplace_Safety", "Admin", "Safety", """
    In case of fire, use the nearest exit. Do not use elevators.
    Assembly point: Parking Lot B.
    Safety Officer: John Doe (ext 5555).
    """)
]

# Generate more dummy topics to reach 10
EXTRAS = [
    ("HR_006_Remote_Work", "HR", "Policy", "Employees can work remotely 2 days a week."),
    ("IT_007_Data_Retention", "IT", "Data", "Customer data kept for 7 years."),
    ("FIN_008_Procurement", "Finance", "SOP", "Purchases > $1k need 3 quotes."),
    ("OPS_009_Shift_Handover", "Operations", "SOP", "Handover must happen at 08:00 and 20:00."),
    ("HR_010_Onboarding", "HR", "Process", "Day 1: IT Setup. Day 2: HR Induction.")
]

ALL_SOPS = SOP_TOPICS + EXTRAS

def create_pdf(filename, title, content):
    if not HAS_PDF: return
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    pdf.cell(200, 10, txt=title, ln=1, align='C')
    pdf.ln(10)
    pdf.multi_cell(0, 10, txt=content)
    pdf.output(filename)

def main():
    print(f"Generating {len(ALL_SOPS)} SOPs in {OUTPUT_DIR}...")
    
    for title, dept, cat, content in ALL_SOPS:
        # Create Text File
        txt_path = os.path.join(OUTPUT_DIR, f"{title}.txt")
        with open(txt_path, "w") as f:
            f.write(f"TITLE: {title}\nDEPT: {dept}\nCATEGORY: {cat}\n\n{content}")
            
        # Create PDF File
        if HAS_PDF:
            pdf_path = os.path.join(OUTPUT_DIR, f"{title}.pdf")
            create_pdf(pdf_path, title, content)
            
    print("Done. To index these, run the app and use the Upload UI or API.")

if __name__ == "__main__":
    main()
