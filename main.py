import os
import pandas as pd
from collections import Counter
from ocr_engine import extract_invoice_data
# --- FIX IS HERE: Changed back to 'classifier' ---
from classifier import predict_category 

def main():
    # 1. Setup Folders
    input_folder = 'invoices'
    output_folder = 'output'
    os.makedirs(output_folder, exist_ok=True)
    
    # Define Output Path
    output_path = os.path.join(output_folder, 'final_detailed_report.csv')

    # --- RESET STEP ---
    # Since we are appending, we must delete the old file first to start fresh.
    if os.path.exists(output_path):
        try:
            os.remove(output_path)
            print(f"Old report removed. Starting fresh: {output_path}")
        except PermissionError:
            print(f"ERROR: Please CLOSE {output_path} in Excel and run again.")
            return

    # 2. Find Images
    files = [f for f in os.listdir(input_folder) if f.lower().endswith(('.jpg', '.png', '.jpeg'))]
    print(f"Found {len(files)} invoices to process.\n")

    # 3. Process Each File (and Save Immediately)
    for filename in files:
        print(f"--- Processing {filename} ---")
        image_path = os.path.join(input_folder, filename)
        
        # A. EXTRACT DATA
        raw_data = extract_invoice_data(image_path)
        
        if not raw_data:
            print(f"   Skipping {filename} (OCR Failed)")
            continue

        # B. DETERMINE CATEGORY
        votes = []
        if raw_data['product_descriptions']:
            for product in raw_data['product_descriptions']:
                cat = predict_category(product)
                votes.append(cat)
                
                # Optional: Keep X-Ray on if you want to see logic
                # print(f"      [X-RAY] Found Word: '{product}' --> Voted: {cat}")

        if votes:
            # FIX: Filter out "Other" noise. Valid categories should win even if minority.
            meaningful_votes = [v for v in votes if str(v) != "Other"]
            
            if meaningful_votes:
                winner = Counter(meaningful_votes).most_common(1)[0][0]
                main_category = str(winner)
            else:
                # If everything is Other, then it's Other.
                main_category = "Other"
        else:
            main_category = "Uncategorized"

        print(f"   => ID: {raw_data['invoice_id']} | Winner: {main_category}")

        # C. PREPARE SINGLE ROW
        current_row = {
            "Invoice No": raw_data['invoice_id'],
            "Date": raw_data['date'],
            "Seller Name": raw_data['seller_name'],
            "Client Name": raw_data['client_name'],
            "Seller Tax ID": raw_data['seller_tax_id'],
            "Seller IBAN": raw_data['seller_iban'],
            "Client Tax ID": raw_data['client_tax_id'],
            "Total Amount": raw_data['total_amount'],
            "Category": main_category
        }

        # D. SAVE IMMEDIATELY (The Incremental Fix)
        df_current = pd.DataFrame([current_row])
        
        # Logic: 
        # - mode='a' means APPEND (add to bottom).
        # - header=... If file doesn't exist, write header. If it does, skip header.
        write_header = not os.path.exists(output_path)
        
        try:
            df_current.to_csv(output_path, mode='a', header=write_header, index=False)
            print(f"   [Saved] Row added to CSV.")
        except PermissionError:
            print(f"   [ERROR] Could not save row. Is the CSV open?")

    print(f"\nSUCCESS! All processing complete. Data saved in {output_path}")

if __name__ == "__main__":
    main()