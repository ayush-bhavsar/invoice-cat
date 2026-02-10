import pytesseract
from pytesseract import Output
from PIL import Image
import re

def extract_invoice_data(image_path):
    print(f"   Scanning with Tesseract...")

    img = Image.open(image_path)
    width, height = img.size

    ocr_data = pytesseract.image_to_data(img, output_type=Output.DICT)
    
    data = {
        "invoice_id": "Not Found",
        "date": "Not Found",
        "seller": [],
        "client": [],
        "total_amount": "0.00",
        "items_count": 0,
        "product_descriptions": []
    }

    n_boxes = len(ocr_data['text'])
    items_y_threshold = height

    for i in range(n_boxes):
        text = ocr_data['text'][i].strip()
        if "ITEMS" in text.upper():
            items_y_threshold = ocr_data['top'][i]
            break

    for i in range(n_boxes):
        text = ocr_data['text'][i].strip()

        if not text: continue
        
        x = ocr_data['left'][i]
        y = ocr_data['top'][i]
        
        text_lower = text.lower()

        if "invoice" in text_lower:
  
            if i + 1 < n_boxes:
                next_text = ocr_data['text'][i+1].strip()

                if "no" in next_text.lower() and i + 2 < n_boxes:
                     data["invoice_id"] = ocr_data['text'][i+2].strip()

                elif ":" in text:
                     data["invoice_id"] = text.split(":")[-1]

        if re.search(r'\d{2}/\d{2}/\d{4}', text):
            data["date"] = text


        if re.match(r'^\$?\d{1,3}(,\d{3})*(\.\d{2})?$', text):

             if y > items_y_threshold:

                 data["total_amount"] = text

        if 150 < y < items_y_threshold:

            if x < (width / 2): 

                if "seller" not in text_lower:
                    data["seller"].append(text)
            else:

                if "client" not in text_lower:
                    data["client"].append(text)

        blacklist = ["description", "qty", "um", "net", "price", "vat", "gross", "worth", "total", "summary"]
        if y > items_y_threshold and text_lower not in blacklist:

            if not re.match(r'^[\d.,\s%$]+$', text):

                if len(text) > 2: 
                    data["product_descriptions"].append(text)

    data["seller"] = " ".join(data["seller"])
    data["client"] = " ".join(data["client"])
    

    unique_y_rows = set()
    for i in range(n_boxes):
        if ocr_data['top'][i] > items_y_threshold and ocr_data['text'][i].strip():

             rounded_y = round(ocr_data['top'][i] / 10) * 10 
             unique_y_rows.add(rounded_y)

    data["items_count"] = max(0, len(unique_y_rows) - 3) 

    return data