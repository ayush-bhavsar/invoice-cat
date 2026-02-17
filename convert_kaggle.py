import pandas as pd
import json

def convert_data():
    print("Reading Flipkart Dataset...")
    
    # 1. Load the raw dataset
    # Make sure your downloaded file is named 'flipkart_com-ecommerce_sample.csv'
    # or change the name below to match your file.
    try:
        df = pd.read_csv("flipkart_com-ecommerce_sample.csv")
    except FileNotFoundError:
        print("ERROR: File 'flipkart_com-ecommerce_sample.csv' not found.")
        print("Please drag the CSV file into your project folder.")
        return

    print(f"Found {len(df)} products. Cleaning data...")

    # 2. Extract specific columns
    # We only need 'product_name' and the main 'product_category_tree'
    new_data = []

    for index, row in df.iterrows():
        description = row['product_name']
        raw_category = row['product_category_tree']
        
        # 3. Clean the Category
        # The raw data looks like: ["Clothing >> Women's Clothing >> Lingerie"]
        # We need to extract just "Clothing" or the specific sub-category.
        try:
            # Remove brackets and quotes
            clean_tree = raw_category.replace('["', '').replace('"]', '').replace('"', '')
            
            # Split by ' >> ' to get levels
            parts = clean_tree.split(' >> ')
            
            # STRATEGY: Pick the Top Level Category
            main_category = parts[0]

            # OPTIONAL: Map Flipkart categories to your specific Invoice categories
            # If Flipkart says "Footwear", we map it to "Clothing" or keep it as "Footwear"
            if main_category == "Footwear":
                main_category = "Clothing"
            elif main_category == "Pens & Stationery":
                main_category = "Office Supplies"
            elif main_category == "Computers":
                main_category = "Electronics"
            elif main_category == "Mobiles & Accessories":
                main_category = "Electronics"
            elif main_category == "Watches":
                main_category = "Electronics" # Or Accessories

            new_data.append({"description": description, "category": main_category})
            
        except:
            continue

    # 4. Create new DataFrame
    clean_df = pd.DataFrame(new_data)
    
    # 5. Append your manual "Garbage" words (Footer text fix)
    # This ensures your AI still ignores "Total" and "Tax"
    garbage_data = [
        {"description": "Total Amount", "category": "Other"},
        {"description": "Tax ID", "category": "Other"},
        {"description": "Subtotal", "category": "Other"},
        {"description": "Invoice Number", "category": "Other"},
        {"description": "Shipping Charges", "category": "Other"},
        {"description": "Grand Total", "category": "Other"},
        {"description": "Thank you for your business", "category": "Other"},
        {"description": "Authorized Signatory", "category": "Other"}
    ]
    garbage_df = pd.DataFrame(garbage_data)
    
    # Combine real products with garbage words
    final_df = pd.concat([clean_df, garbage_df], ignore_index=True)

    # 6. Save to training_data folder
    final_df.to_csv("training_data/categories.csv", index=False)
    
    print(f"SUCCESS! Converted {len(final_df)} lines.")
    print("Saved to: training_data/categories.csv")
    print(f"Sample:\n{final_df.head()}")

if __name__ == "__main__":
    convert_data()