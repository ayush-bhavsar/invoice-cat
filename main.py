import os
import pandas as pd
from collections import Counter
from ocr_engine import extract_invoice_data
from classifier import predict_categories_batch

def main():
    input_folder = 'invoices'
    output_folder = 'output'
    os.makedirs(output_folder, exist_ok=True)
    
    output_path = os.path.join(output_folder, 'final_detailed_report.csv')

    if os.path.exists(output_path):
        try:
            os.remove(output_path)
            print(f"Old report removed. Starting fresh: {output_path}")
        except PermissionError:
            print(f"ERROR: Please CLOSE {output_path} in Excel and run again.")
            return

    files = [f for f in os.listdir(input_folder) if f.lower().endswith(('.jpg', '.png', '.jpeg', '.pdf', '.tiff', '.tif'))]
    print(f"Found {len(files)} invoices to process.\n")

    for filename in files:
        print(f"--- Processing {filename} ---")
        image_path = os.path.join(input_folder, filename)
        
        raw_data_list = extract_invoice_data(image_path)
        
        if not raw_data_list:
            print(f"   Skipping {filename} (OCR Failed)")
            continue

        for p_idx, raw_data in enumerate(raw_data_list):
            page_label = f" (Page {p_idx+1})" if len(raw_data_list) > 1 else ""
            
            if raw_data.get('_extracted_by') == 'gemini' and raw_data.get('category'):
                main_category = raw_data['category']
                print(f"   => Using Gemini-provided category: {main_category}")
            else:
                votes = []
                if raw_data['product_descriptions']:
                    cats = predict_categories_batch(raw_data['product_descriptions'])
                    for cat in cats:
                        votes.append(cat)
                        
                if votes:
                    meaningful_votes = [v for v in votes if str(v) != "Other"]
                    
                    if meaningful_votes:
                        winner = Counter(meaningful_votes).most_common(1)[0][0]
                        main_category = str(winner)
                    else:
                        main_category = "Other"
                else:
                    main_category = "Uncategorized"

            print(f"   => ID: {raw_data['invoice_id']}{page_label} | Winner: {main_category}")

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

            df_current = pd.DataFrame([current_row])
            
            write_header = not os.path.exists(output_path)
            
            try:
                df_current.to_csv(output_path, mode='a', header=write_header, index=False)
                print(f"   [Saved] Row added to CSV.")
            except PermissionError:
                print(f"   [ERROR] Could not save row. Is the CSV open?")

    print(f"\nSUCCESS! All processing complete. Data saved in {output_path}")

if __name__ == "__main__":
    main()