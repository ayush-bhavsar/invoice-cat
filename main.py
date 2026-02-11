import os
import pandas as pd
from collections import Counter
from ocr_engine import extract_invoice_data
from classifier import predict_category

def main():
    input_folder = 'invoices'
    output_folder = 'output'
    os.makedirs(output_folder, exist_ok=True)

    final_report = []

    files = [f for f in os.listdir(input_folder) if f.lower().endswith(('.jpg', '.png'))]
    print(f"Found {len(files)} invoices.\n")

    for filename in files:
        print(f"--- Processing {filename} ---")
        image_path = os.path.join(input_folder, filename)
        
        raw_data = extract_invoice_data(image_path)
        
        if not raw_data:
            continue

        # Classify
        votes = []
        if raw_data['product_descriptions']:
            for product in raw_data['product_descriptions']:
                votes.append(predict_category(product))
            main_category = Counter(votes).most_common(1)[0][0]
        else:
            main_category = "Uncategorized"

        print(f"   => ID: {raw_data['invoice_id']} | Seller: {raw_data['seller_name']}")

        # ADD NEW COLUMNS HERE
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

    if final_report:
        df = pd.DataFrame(final_report)
        output_path = os.path.join(output_folder, 'final_detailed_report.csv')
        df.to_csv(output_path, index=False)
        print(f"\nSUCCESS! Saved to: {output_path}")
        print(df[["Invoice No", "Seller Name", "Total Amount"]]) # Preview
    else:
        print("No invoices processed.")

if __name__ == "__main__":
    main()