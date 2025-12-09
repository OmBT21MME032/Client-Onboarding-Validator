import pandas as pd
import numpy as np
from datetime import datetime
import re
import os

# --- CONFIGURATION ---
INPUT_FILE = 'large_input_data.csv'
OUTPUT_FOLDER = 'processed_reports'
MIN_INVESTMENT = 500000 

if not os.path.exists(OUTPUT_FOLDER):
    os.makedirs(OUTPUT_FOLDER)

# --- VALIDATION LOGIC (Same as before) ---
def calculate_age(dob_str):
    try:
        dob = datetime.strptime(str(dob_str), '%Y-%m-%d')
        today = datetime.now()
        return today.year - dob.year - ((today.month, today.day) < (dob.month, dob.day))
    except:
        return -1 

def is_valid_email(email):
    if pd.isna(email): return False
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, str(email)))

def validate_client_row(row):
    errors = []
    
    # 1. Age Check
    age = calculate_age(row['DOB'])
    if age == -1: errors.append("Invalid DOB")
    elif age < 18: errors.append(f"Minor (Age: {age})")

    # 2. Tax ID Check
    if pd.isna(row['Tax_ID']) or row['Tax_ID'] == 'MISSING': errors.append("Missing Tax ID")
    elif len(str(row['Tax_ID'])) != 10: errors.append("Invalid Tax ID")

    # 3. Email Check
    if not is_valid_email(row['Email']): errors.append("Invalid Email")

    # 4. Investment Check
    try:
        amount = float(row['Investment_Amount'])
        if amount < MIN_INVESTMENT: errors.append(f"Below Min (₹{amount})")
    except: errors.append("Invalid Amount")

    if not errors: return "PASS", "Verified"
    else: return "FAIL", "; ".join(errors)

# --- MAIN EXECUTION ---
def main():
    print("--- GENERATING ADVANCED EXCEL REPORT ---")
    
    # Load Data
    try:
        df = pd.read_csv(INPUT_FILE)
    except FileNotFoundError:
        print(f"ERROR: {INPUT_FILE} not found.")
        return

    # Run Validation
    df['Validation_Status'], df['Error_Details'] = zip(*df.apply(validate_client_row, axis=1))
    
    # Add Timestamp (Audit Trail)
    df['Audit_Timestamp'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # --- THE UPGRADE: EXPORT TO EXCEL WITH FORMATTING ---
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_file = f"{OUTPUT_FOLDER}/SMA_Onboarding_Report_{timestamp}.xlsx"

    # Create a Pandas Excel Writer using XlsxWriter as the engine
    writer = pd.ExcelWriter(output_file, engine='xlsxwriter')
    
    # Write the dataframe to Excel
    df.to_excel(writer, sheet_name='Onboarding_Status', index=False)

    # Get the workbook and worksheet objects
    workbook  = writer.book
    worksheet = writer.sheets['Onboarding_Status']

    # --- DEFINE FORMATS (The "Professional Look") ---
    
    # Header Format: Dark Blue background, White text, Bold (BlackRock Colors)
    header_fmt = workbook.add_format({
        'bold': True,
        'text_wrap': True,
        'valign': 'top',
        'fg_color': '#203764', # Corporate Blue
        'font_color': '#FFFFFF',
        'border': 1
    })

    # Status: Green (Pass)
    pass_fmt = workbook.add_format({'bg_color': '#C6EFCE', 'font_color': '#006100'})
    
    # Status: Red (Fail)
    fail_fmt = workbook.add_format({'bg_color': '#FFC7CE', 'font_color': '#9C0006'})

    # --- APPLY FORMATS ---

    # 1. Apply Header Format
    for col_num, value in enumerate(df.columns.values):
        worksheet.write(0, col_num, value, header_fmt)

    # 2. Auto-Adjust Column Widths (So text is readable)
    for i, col in enumerate(df.columns):
        # Find max length of data in column to set width
        column_len = max(df[col].astype(str).map(len).max(), len(col)) + 2
        worksheet.set_column(i, i, column_len)

    # 3. Conditional Formatting (The Magic)
    # Highlight 'Validation_Status' column: Green if PASS, Red if FAIL
    # We find the index of the 'Validation_Status' column
    status_col_idx = df.columns.get_loc("Validation_Status")
    
    # Apply logic to the whole column (from row 1 to end)
    worksheet.conditional_format(1, status_col_idx, len(df), status_col_idx,
                                 {'type': 'cell',
                                  'criteria': '==',
                                  'value': '"PASS"',
                                  'format': pass_fmt})
    
    worksheet.conditional_format(1, status_col_idx, len(df), status_col_idx,
                                 {'type': 'cell',
                                  'criteria': '==',
                                  'value': '"FAIL"',
                                  'format': fail_fmt})

    # Save
    writer.close()
    
    print(f"✅ PROFESSIONAL REPORT GENERATED: {output_file}")
    print("Open the Excel file to see the color-coding!")

if __name__ == "__main__":
    main()