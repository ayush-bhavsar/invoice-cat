import os
import pytesseract
from pytesseract import Output
from PIL import Image
import re

# Uncomment if Tesseract is not in your PATH:
# pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

try:
    import fitz  # PyMuPDF
    PYMUPDF_AVAILABLE = True
except ImportError:
    PYMUPDF_AVAILABLE = False
    print("Warning: PyMuPDF not installed. PDF support disabled. Run: pip install PyMuPDF")

PDF_RENDER_DPI = 150


def _pdf_to_images(pdf_path):
    """Convert each page of a PDF to a PIL Image at PDF_RENDER_DPI."""
    if not PYMUPDF_AVAILABLE:
        raise RuntimeError("PyMuPDF is required for PDF support. Run: pip install PyMuPDF")

    images = []
    doc = fitz.open(pdf_path)
    scale = PDF_RENDER_DPI / 72.0
    mat = fitz.Matrix(scale, scale)
    for page in doc:
        pix = page.get_pixmap(matrix=mat)
        img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
        images.append(img)
    doc.close()
    return images


def _get_images_from_file(file_path):
    """Return a list of PIL Images from an image file or a PDF."""
    ext = os.path.splitext(file_path)[1].lower()
    if ext == '.pdf':
        return _pdf_to_images(file_path)
    else:
        return [Image.open(file_path)]


def _extract_from_image(img):
    """Run OCR extraction on a single PIL Image. Returns a data dict."""
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

    # 1. Structure Finding (Start and End of Table)
    items_y_threshold = height
    total_y_location = height

    for i in range(n_boxes):
        text = ocr_data['text'][i].strip()

        if "ITEMS" in text.upper():
            items_y_threshold = ocr_data['top'][i]

        if any(x in text.lower() for x in ["total", "subtotal", "amount due", "gross worth"]):
            if ocr_data['top'][i] > items_y_threshold:
                if ocr_data['top'][i] < total_y_location:
                    total_y_location = ocr_data['top'][i]

    # 2. Extract Total Amount
    if total_y_location != height:
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

    # 3. Main Loop
    prod_blacklist = ["description", "qty", "um", "net", "price", "vat", "gross", "worth", "total", "summary", "no.", "items"]
    name_blacklist = ["date", "issue", "invoice", "no:", "number", "id", "tax", "iban", "page", "seller:", "client:", "to:", "from:"]

    seller_lines = []
    client_lines = []

    for i in range(n_boxes):
        text = ocr_data['text'][i].strip()
        if not text: continue

        x = ocr_data['left'][i]
        y = ocr_data['top'][i]
        text_lower = text.lower()

        # ID & Date
        if "invoice" in text_lower:
            if i + 1 < n_boxes:
                if "no" in ocr_data['text'][i+1].lower() and i + 2 < n_boxes:
                    data["invoice_id"] = ocr_data['text'][i+2]
                elif ":" in text:
                    data["invoice_id"] = text.split(":")[-1]
        if re.search(r'\d{2}/\d{2}/\d{4}', text):
            data["date"] = text

        # Header Zone
        if 100 < y < items_y_threshold:
            if re.match(r'\d{3}-\d{2}-\d{4}', text):
                if x < (width / 2): data["seller_tax_id"] = text
                else: data["client_tax_id"] = text
            if "GB" in text and len(text) > 10 and re.search(r'\d', text):
                if x < (width / 2): data["seller_iban"] = text

            is_blacklisted = any(b in text_lower for b in name_blacklist)
            is_date = bool(re.search(r'\d{2}/\d{2}/\d{4}', text))
            if not is_blacklisted and not is_date:
                if x < (width / 2):
                    if not re.search(r'\d', text): seller_lines.append(text)
                else:
                    if not re.search(r'\d', text): client_lines.append(text)

        # Products
        if y > items_y_threshold and y < total_y_location:
            if any(bad in text_lower for bad in prod_blacklist): continue
            if re.match(r'^[\d.,\s%$]+$', text): continue
            if len(text) > 3:
                data["product_descriptions"].append(text)

    if seller_lines: data["seller_name"] = " ".join(seller_lines[:3]).replace("of ", "")
    if client_lines: data["client_name"] = " ".join(client_lines[:3])

    return data


def extract_invoice_data(file_path):
    print(f"   Scanning: {file_path}...")

    try:
        images = _get_images_from_file(file_path)
    except Exception as e:
        print(f"Error opening file: {e}")
        return []

    ext = os.path.splitext(file_path)[1].lower()
    if ext == '.pdf':
        print(f"   PDF detected: {len(images)} page(s)")

    pages_data = []
    for idx, img in enumerate(images):
        if ext == '.pdf':
            print(f"   Processing page {idx + 1}/{len(images)}...")
        try:
            page_data = _extract_from_image(img)
            pages_data.append(page_data)
        except Exception as e:
            print(f"   Error on page {idx + 1}: {e}")

    return pages_data
