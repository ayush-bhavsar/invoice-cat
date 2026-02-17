import os
import pandas as pd
from ocr_engine import extract_invoice_data

def verify_results():
    # 1. Load the Model's Answers
    try:
        df = pd.read_csv('output/final_detailed_report.csv')
        # Create a map: Invoice ID -> Category
        # We need to map filename to ID first, or just look up by ID if we trust extraction is deterministic.
        # Let's map by ID.
        report_map = dict(zip(df['Invoice No'].astype(str), df['Category']))
    except Exception as e:
        print(f"Error reading report: {e}")
        return

    # 2. Process Images to see "Ground Truth" (Product Descriptions)
    input_folder = 'invoices'
    files = sorted([f for f in os.listdir(input_folder) if f.endswith('.jpg')])
    
    print(f"{'Image':<15} | {'ID':<10} | {'Model Says':<12} | {'Products Found (First 2)'}")
    print("-" * 80)

    for filename in files:
        if "batch1" not in filename: continue
        
        image_path = os.path.join(input_folder, filename)
        
        # Extract purely to see *what* is in it
        data = extract_invoice_data(image_path)
        inv_id = str(data.get('invoice_id', 'Unknown'))
        
        predicted_cat = report_map.get(inv_id, "NOT FOUND")
        
        products = data.get('product_descriptions', [])
        product_summary = ", ".join(products[:2]) # Show first 2 items
        if len(products) > 2: product_summary += "..."
        
        print(f"{filename:<15} | {inv_id:<10} | {predicted_cat:<12} | {product_summary}")

if __name__ == "__main__":
    verify_results()
