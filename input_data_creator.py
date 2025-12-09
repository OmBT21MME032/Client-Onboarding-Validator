import pandas as pd
import numpy as np
import random
from datetime import datetime, timedelta

# --- CONFIGURATION ---
NUM_ROWS = 200  # Generates 200 dummy clients
OUTPUT_FILE = 'large_input_data.csv'

# Setup random seed so results are consistent
random.seed(42)
np.random.seed(42)

# Helper Lists
first_names = ['Aarav', 'Vihaan', 'Aditya', 'Sai', 'Rohan', 'Priya', 'Diya', 'Ananya', 'Isha', 'Sana', 'Rahul', 'John', 'Alice', 'Bob']
last_names = ['Sharma', 'Verma', 'Gupta', 'Singh', 'Patel', 'Reddy', 'Nair', 'Kumar', 'Doe', 'Smith', 'Iyer']
domains = ['gmail.com', 'yahoo.co.in', 'outlook.com', 'blackrock.com', 'bad-email']

def generate_random_dob():
    """Generates a random DOB. Occasionally generates a MINOR (under 18)."""
    if random.random() < 0.15: # 15% chance of being a minor
        start_date = datetime.now() - timedelta(days=365*17)
        end_date = datetime.now()
    else:
        start_date = datetime.now() - timedelta(days=365*70)
        end_date = datetime.now() - timedelta(days=365*19)
    
    # Calculate the range in days
    time_between_dates = end_date - start_date
    days_between_dates = time_between_dates.days
    
    # Generate random number of days
    random_number_of_days = random.randrange(days_between_dates)
    
    # THE FIX IS HERE: Convert integer to timedelta before adding
    random_date = start_date + timedelta(days=random_number_of_days)
    
    return random_date.date()

def generate_tax_id():
    """Generates a PAN. Occasionally generates INVALID ones."""
    # 10% chance of missing PAN
    if random.random() < 0.10:
        return np.nan
    # 10% chance of invalid length
    if random.random() < 0.10:
        return "ABC123" 
    
    # Generate valid-looking PAN (5 chars + 4 digits + 1 char)
    chars = "".join(random.choices("ABCDEFGHIJKLMNOPQRSTUVWXYZ", k=5))
    digits = "".join(random.choices("0123456789", k=4))
    last = random.choice("ABCDEFGHIJKLMNOPQRSTUVWXYZ")
    return f"{chars}{digits}{last}"

def generate_investment():
    """Generates investment amount. Occasionally below 5 Lakhs."""
    if random.random() < 0.10: # 10% chance of being too poor
        return random.randint(10000, 499999)
    else:
        return random.randint(500000, 50000000)

# --- MAIN GENERATION LOOP ---
print(f"Generating {NUM_ROWS} dummy client records...")

data = []
for i in range(101, 101 + NUM_ROWS):
    f_name = random.choice(first_names)
    l_name = random.choice(last_names)
    full_name = f"{f_name} {l_name}"
    
    dob = generate_random_dob()
    tax_id = generate_tax_id()
    inv_amt = generate_investment()
    
    # Generate Email (with some intentional errors)
    if random.random() < 0.05:
        email = f"{f_name}.{l_name}@" # Invalid email
    else:
        email = f"{f_name.lower()}.{l_name.lower()}@{random.choice(domains)}"

    risk = random.choice(['High', 'Medium', 'Low'])
    country = random.choice(['India', 'USA', 'UK', 'Singapore'])

    data.append([i, full_name, dob, tax_id, email, inv_amt, risk, country])

# Create DataFrame
columns = ['Client_ID', 'Full_Name', 'DOB', 'Tax_ID', 'Email', 'Investment_Amount', 'Risk_Profile', 'Country']
df = pd.DataFrame(data, columns=columns)

# Save to CSV
df.to_csv(OUTPUT_FILE, index=False)
print(f"✅ SUCCESS: Generated '{OUTPUT_FILE}' with {NUM_ROWS} rows.")