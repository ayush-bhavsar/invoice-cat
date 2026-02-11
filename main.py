import os
import pandas as pd
from collections import Counter
from ocr_engine import extract_invoice_data
from classifier import predict_category

def main():
    # 1. Setup Folders
    input_folder = 'invoices'
    output_folder = 'output'
    os.makedirs(output_folder, exist_ok=True)

    final_report = []

    # 2. Find Images
    files = [f for f in os.listdir(input_folder) if f.lower().endswith(('.jpg', '.png'))]
    print(f"Found {len(files)} invoices to process.\n")

    # 3. Process Each File
    for filename in files:
        print(f"--- Processing {filename} ---")
        image_path = os.path.join(input_folder, filename)
        
        # A. EXTRACT DATA
        raw_data = extract_invoice_data(image_path)
        
        if not raw_data:
            print(f"   Skipping {filename} (OCR Failed)")
            continue

        # B. DETERMINE CATEGORY (Majority Rule)
        votes = []
        if raw_data['product_descriptions']:
            # 1. Vote for every product
            for product in raw_data['product_descriptions']:
                cat = predict_category(product)
                votes.append(cat)
                # Uncomment next line to see the votes in real-time
                # print(f"      [Vote] {product} -> {cat}")

            # 2. Count Votes
            if votes:
                # most_common(1) returns the top winner: [('Electronics', 3)]
                winner = Counter(votes).most_common(1)[0][0]
                main_category = winner
            else:
                main_category = "Uncategorized"
        else:
            main_category = "Uncategorized"

        print(f"   => ID: {raw_data['invoice_id']} | Winner: {main_category}")

        # C. BUILD ROW
        final_report.append({
            "Invoice No": raw_data['invoice_id'],
            "Date": raw_data['date'],
            "Seller Name": raw_data['seller_name'],
            "Client Name": raw_data['client_name'],
            "Seller Tax ID": raw_data['seller_tax_id'],
            "Seller IBAN": raw_data['seller_iban'],
            "Client Tax ID": raw_data['client_tax_id'],
            "Total Amount": raw_data['total_amount'],
            "Category": main_category
        })

    # 4. Save Report
    if final_report:
        df = pd.DataFrame(final_report)
        output_path = os.path.join(output_folder, 'final_detailed_report.csv')
        
        try:
            df.to_csv(output_path, index=False)
            print(f"\nSUCCESS! Detailed report saved to: {output_path}")
            print(df[["Invoice No", "Total Amount", "Category"]].head())
        except PermissionError:
            print(f"\nERROR: Please CLOSE the Excel file and run again.")
    else:
        print("No invoices processed.")

if __name__ == "__main__":
    main()