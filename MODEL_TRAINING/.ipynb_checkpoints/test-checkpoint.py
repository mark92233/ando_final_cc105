import joblib
import pandas as pd
import numpy as np
import sys
from datetime import datetime

# 1. Load the "Big Three" Models
print("--- Initializing AI Coffee Shop Systems ---")
try:
    m1_demand = joblib.load('model1_demand_forecast.pkl')
    m2_revenue = joblib.load('model2_revenue_forecast.pkl')
    m3_inventory = joblib.load('model3_inventory_forecast.pkl')
    print("✅ All models loaded successfully.\n")
except Exception as e:
    print(f"❌ Error loading models: {e}")
    sys.exit(1)

def get_user_inputs():
    """Gathers interactive input from the user."""
    print("Please enter the following details for the forecast:")
    
    # Date Input
    while True:
        date_str = input("Enter Date (YYYY-MM-DD): ")
        try:
            dt = datetime.strptime(date_str, "%Y-%m-%d")
            break
        except ValueError:
            print("Invalid format. Please use YYYY-MM-DD.")

    # Location Input
    locations = ["Astoria", "Lower Manhattan", "Hell's Kitchen"]
    print(f"Available Locations: {locations}")
    while True:
        loc = input("Enter Store Location: ").title()
        if loc in locations:
            break
        print(f"Error: Please choose from {locations}")

    # Shift Input
    shifts = ["Morning", "Afternoon", "Evening"]
    while True:
        shf = input(f"Enter Shift {shifts}: ").capitalize()
        if shf in shifts:
            break
        print(f"Error: Please choose from {shifts}")

    # Historical Context (Previous shift performance)
    try:
        p_cups = float(input("Enter Cups Sold in previous shift: "))
        p_rev = float(input("Enter Revenue from previous shift ($): "))
    except ValueError:
        print("Invalid number. Defaulting to average values (100 cups, $350.0).")
        p_cups, p_rev = 100.0, 350.0

    return dt, loc, shf, p_cups, p_rev

# --- Main Logic ---

# 2. Get Inputs
date_obj, location, shift, prev_cups, prev_revenue = get_user_inputs()

# 3. Derive Date Features
month = date_obj.month
day_name = date_obj.strftime("%A")
is_weekend = 1 if date_obj.weekday() >= 5 else 0

# 4. Construct Initial DataFrame
input_df = pd.DataFrame([{
    'store_location': location,
    'month': month,
    'day_of_week': day_name,
    'is_weekend': is_weekend,
    'shift': shift,
    'prev_cups': prev_cups
}])

# --- THE AI CHAIN ---

# Step 1: Predict Demand (Total Cups)
pred_cups = m1_demand.predict(input_df)[0]

# Step 2: Predict Revenue
rev_input = input_df.copy()
rev_input['total_cups'] = pred_cups
rev_input['prev_revenue'] = prev_revenue
pred_revenue = m2_revenue.predict(rev_input)[0]

# Step 3: Predict Inventory (Category Breakdown)
inv_input = input_df.copy()
inv_input['total_shift_cups'] = pred_cups
# Remove 'prev_cups' if your Model 3 didn't use it, but keeping logic consistent
if 'prev_cups' in inv_input.columns:
    inv_input = inv_input.drop(columns=['prev_cups'])

pred_inventory = m3_inventory.predict(inv_input)[0]

# --- 5. PRINT THE REPORT ---
print("\n" + "="*50)
print(f"      FORECAST REPORT: {location.upper()}")
print(f"      DATE: {date_obj.strftime('%B %d, %Y')} ({day_name})")
print("="*50)

print(f"\n[DEMAND]   Predicted Volume  : {round(pred_cups)} cups")
print(f"[FINANCE]  Predicted Revenue : ${pred_revenue:,.2f}")

print("\n[INVENTORY] Recommended Stocking Levels:")
categories = [
    'Bakery', 'Branded', 'Coffee', 'Coffee_beans', 
    'Drinking_Chocolate', 'Flavours', 'Loose_Tea', 
    'Packaged_Chocolate', 'Tea'
]

# Create a clean display for inventory
for cat, qty in zip(categories, pred_inventory):
    if qty > 0.5:
        # Using bullet points for a clean UI feel
        print(f"  • {cat:18} : {max(0, round(qty))} units")

print("\n" + "="*50)
print("             End of AI Forecast")
print("="*50)