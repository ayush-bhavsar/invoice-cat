import pytesseract
from pytesseract import Output
from PIL import Image
import re

def extract_invoice_data(image_path):
    print(f"   Scanning: {image_path}...")
    
    try:
        img = Image.open(image_path)
    except Exception as e:
        print(f"Error opening image: {e}")
        return {}

    ocr_data = pytesseract.image_to_data(img, output_type=Output.DICT)
    width, height = img.size
    n_boxes = len(ocr_data['text'])
    
    data = {
        "invoice_id": "Not Found",
        "date": "Not Found",
        "seller_name": "Not Found",
        "client_name": "Not Found",
        "seller_tax_id": "Not Found",
        "client_tax_id": "Not Found",
        "seller_iban": "Not Found",
        "total_amount": "0.00",
        "items_count": 0,
        "product_descriptions": []
    }

    items_y_threshold = height
    total_y_location = -1

    for i in range(n_boxes):
        text = ocr_data['text'][i].strip()
        if "ITEMS" in text.upper():
            items_y_threshold = ocr_data['top'][i]
        if "Total" in text and ocr_data['top'][i] > items_y_threshold:
            total_y_location = ocr_data['top'][i]

    if total_y_location != -1:
        line_text = []
        for i in range(n_boxes):
            if abs(ocr_data['top'][i] - total_y_location) < 20:
                line_text.append(ocr_data['text'][i])
        full_line = " ".join(line_text)
        matches = re.findall(r'\d[\d\s]*[.,]\d{2}', full_line)
        valid_amounts = []
        for m in matches:
            clean_str = m.replace(" ", "").replace(",", ".")
            try:
                valid_amounts.append(float(clean_str))
            except ValueError:
                continue
        if valid_amounts:
            data["total_amount"] = f"{max(valid_amounts):.2f}"

    prod_blacklist = ["description", "qty", "um", "net", "price", "vat", "gross", "worth", "total", "summary", "no.", "items"]

    name_blacklist = ["date", "issue", "invoice", "no:", "number", "id", "tax", "iban", "page", "seller:", "client:", "to:", "from:","of"]

    seller_lines = []
    client_lines = []

    for i in range(n_boxes):
        text = ocr_data['text'][i].strip()
        if not text: continue
        
        x = ocr_data['left'][i]
        y = ocr_data['top'][i]
        text_lower = text.lower()

        if "invoice" in text_lower:
            if i + 1 < n_boxes:
                if "no" in ocr_data['text'][i+1].lower() and i + 2 < n_boxes:
                    data["invoice_id"] = ocr_data['text'][i+2]
                elif ":" in text:
                    data["invoice_id"] = text.split(":")[-1]

        if re.search(r'\d{2}/\d{2}/\d{4}', text):
            data["date"] = text

        if 100 < y < items_y_threshold:

            if re.match(r'\d{3}-\d{2}-\d{4}', text):
                if x < (width / 2):
                    data["seller_tax_id"] = text
                else:
                    data["client_tax_id"] = text

            if "GB" in text and len(text) > 10 and re.search(r'\d', text):
                 if x < (width / 2):
                    data["seller_iban"] = text

            is_blacklisted = any(b in text_lower for b in name_blacklist)

            is_date = bool(re.search(r'\d{2}/\d{2}/\d{4}', text))
            
            if not is_blacklisted and not is_date:
                if x < (width / 2):

                    if not re.search(r'\d', text): 
                        seller_lines.append(text)
                else:

                    if not re.search(r'\d', text):
                        client_lines.append(text)

        if y > items_y_threshold:
            if any(bad in text_lower for bad in prod_blacklist): continue
            if re.match(r'^[\d.,\s%$]+$', text): continue
            if len(text) > 3:
                data["product_descriptions"].append(text)

    if seller_lines:
        data["seller_name"] = " ".join(seller_lines[:4]) 
    if client_lines:
        data["client_name"] = " ".join(client_lines[:4])

    unique_rows = set()
    for i in range(n_boxes):
        if ocr_data['top'][i] > items_y_threshold and ocr_data['text'][i].strip():
            unique_rows.add(round(ocr_data['top'][i] / 10) * 10)
    data["items_count"] = max(0, len(unique_rows) - 3)

    return data