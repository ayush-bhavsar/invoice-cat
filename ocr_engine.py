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
        "seller": [],
        "client": [],
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
                val = float(clean_str)
                valid_amounts.append(val)
            except ValueError:
                continue


        if valid_amounts:
            max_amount = max(valid_amounts)
            data["total_amount"] = f"{max_amount:.2f}" 

    blacklist = ["description", "qty", "um", "net", "price", "vat", "gross", "worth", "total", "summary", "no.", "items"]
    
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
            if x < (width / 2): 
                if "seller" not in text_lower: data["seller"].append(text)
            else: 
                if "client" not in text_lower: data["client"].append(text)

        if y > items_y_threshold:
            if any(bad_word in text_lower for bad_word in blacklist): continue
            if re.match(r'^[\d.,\s%$]+$', text): continue
            if len(text) > 3:
                data["product_descriptions"].append(text)

    data["seller"] = " ".join(data["seller"])
    data["client"] = " ".join(data["client"])

    unique_rows = set()
    for i in range(n_boxes):
        if ocr_data['top'][i] > items_y_threshold and ocr_data['text'][i].strip():
            unique_rows.add(round(ocr_data['top'][i] / 10) * 10)
    data["items_count"] = max(0, len(unique_rows) - 3)

    return data