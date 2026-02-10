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

        votes = []
        if raw_data['product_descriptions']:
            for product in raw_data['product_descriptions']:
                cat = predict_category(product)
                votes.append(cat)


        if votes:

            main_category = Counter(votes).most_common(1)[0][0]
        else:
            main_category = "Uncategorized"

        print(f"   => Result: ID {raw_data['invoice_id']} | Total: {raw_data['total_amount']} | Category: {main_category}")

        final_report.append({
            "File": filename,
            "Invoice ID": raw_data['invoice_id'],
            "Date": raw_data['date'],
            "Total Amount": raw_data['total_amount'],
            "Invoice Category": main_category
        })


    if final_report:
        df = pd.DataFrame(final_report)
        output_path = os.path.join(output_folder, 'final_summary.csv')
        df.to_csv(output_path, index=False)
        print(f"\nSUCCESS! Summary saved to: {output_path}")
        print(df)
    else:
        print("No invoices processed.")

if __name__ == "__main__":
    main()