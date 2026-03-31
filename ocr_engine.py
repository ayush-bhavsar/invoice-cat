import os
import json
import sys
import shutil
import pytesseract
from pytesseract import Output
from PIL import Image
import re

# Auto-detect Tesseract on Windows if not already in PATH
if sys.platform == 'win32' and not shutil.which('tesseract'):
    _tesseract_paths = [
        r'C:\Program Files\Tesseract-OCR\tesseract.exe',
        r'C:\Program Files (x86)\Tesseract-OCR\tesseract.exe',
        os.path.join(os.environ.get('LOCALAPPDATA', ''), 'Tesseract-OCR', 'tesseract.exe'),
    ]
    for _path in _tesseract_paths:
        if os.path.exists(_path):
            pytesseract.pytesseract.tesseract_cmd = _path
            break

from dotenv import load_dotenv
import google.generativeai as genai

load_dotenv()
GEMINI_API_KEY = os.environ.get("LLM_API_KEY")
if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)

try:
    import fitz
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

        if "invoice" in text_lower:
            if i + 1 < n_boxes:
                if "no" in ocr_data['text'][i+1].lower() and i + 2 < n_boxes:
                    data["invoice_id"] = ocr_data['text'][i+2]
                elif ":" in text:
                    data["invoice_id"] = text.split(":")[-1]
        if data["date"] == "Not Found":
            date_patterns = [
                r'\b\d{2}/\d{2}/\d{4}\b',
                r'\b\d{4}-\d{2}-\d{2}\b',
                r'\b\d{2}\.\d{2}\.\d{4}\b',
                r'\b\d{2}-\d{2}-\d{4}\b',
                r'\b\d{1,2}\s+(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\s+\d{4}\b',
            ]
            if not re.match(r'^\d{3}-\d{2}-\d{4}$', text):
                for dp in date_patterns:
                    if re.search(dp, text, re.IGNORECASE):
                        data["date"] = text
                        break

        if 100 < y < items_y_threshold:
            tax_patterns = [
                r'\d{3}-\d{2}-\d{4}',
                r'\d{2}[A-Z]{5}\d{4}[A-Z]\d[A-Z\d][A-Z]',
                r'[A-Z]{2}\d{8,12}',
                r'\d{2}-\d{7}',
            ]
            for tp in tax_patterns:
                if re.match(tp, text):
                    if x < (width / 2): data["seller_tax_id"] = text
                    else: data["client_tax_id"] = text
                    break
            if re.match(r'[A-Z]{2}\d{2}[A-Z0-9]{10,30}', text):
                if x < (width / 2): data["seller_iban"] = text

            is_blacklisted = any(b in text_lower for b in name_blacklist)
            is_date = bool(re.search(r'\d{2}/\d{2}/\d{4}', text))
            if not is_blacklisted and not is_date:
                if x < (width / 2):
                    if not re.search(r'\d', text): seller_lines.append(text)
                else:
                    if not re.search(r'\d', text): client_lines.append(text)

        if y > items_y_threshold and y < total_y_location:
            if any(bad in text_lower for bad in prod_blacklist): continue
            if re.match(r'^[\d.,\s%$]+$', text): continue
            if len(text) > 3:
                data["product_descriptions"].append(text)

    if seller_lines: data["seller_name"] = " ".join(seller_lines[:3]).replace("of ", "")
    if client_lines: data["client_name"] = " ".join(client_lines[:3])

    all_text_pieces = [t for t in ocr_data['text'] if t.strip()]
    data["_raw_ocr_text"] = " ".join(all_text_pieces)

    return data


def _extraction_quality(data):
    """Score how many key fields were successfully extracted (0-5)."""
    score = 0
    if data.get('invoice_id') not in ('Not Found', None): score += 1
    if data.get('date') not in ('Not Found', None): score += 1
    if data.get('seller_name') not in ('Not Found', None): score += 1
    if data.get('client_name') not in ('Not Found', None): score += 1
    if data.get('total_amount') not in ('0.00', None): score += 1
    return score


def _extract_with_gemini(ocr_text, api_key=None):
    """
    Single Gemini API call that extracts all invoice fields AND classifies.
    Returns a data dict with 'category' key, or None on failure.
    """
    effective_key = api_key or GEMINI_API_KEY
    if not effective_key or not ocr_text or len(ocr_text.strip()) < 20:
        return None

    try:
        genai.configure(api_key=effective_key)
        model = genai.GenerativeModel('gemini-2.5-flash')

        prompt = f"""You are an expert invoice processing AI.
Below is raw OCR text extracted from an invoice image. The text may be messy or out of order.

OCR TEXT:
{ocr_text}

Extract the following fields and classify the invoice into a category.
Return ONLY valid JSON (no markdown, no explanation), with these exact keys:
{{
  "invoice_id": "the invoice number or ID",
  "date": "the invoice date in dd/mm/yyyy format",
  "seller_name": "the seller/vendor company name",
  "client_name": "the buyer/client name",
  "seller_tax_id": "seller tax ID if present",
  "client_tax_id": "client tax ID if present",
  "seller_iban": "seller IBAN if present",
  "total_amount": "total amount as a number like 123.45",
  "category": "one of: Electronics, Furniture, Kitchen, Clothing, Beverages, Office Supplies, Books & Media, Services, Hardware, Other"
}}

Rules:
- For missing fields, use "Not Found"
- For total_amount, use "0.00" if not found
- Output ONLY the JSON object, nothing else"""

        response = model.generate_content(prompt)
        text = response.text.strip()

        if text.startswith("```json"):
            text = text[7:]
        if text.startswith("```"):
            text = text[3:]
        if text.endswith("```"):
            text = text[:-3]
        text = text.strip()

        result = json.loads(text)

        valid_categories = [
            "Hardware", "Books & Media", "Furniture", "Services", "Electronics",
            "Clothing", "Kitchen", "Office Supplies", "Beverages", "Other"
        ]
        if result.get('category') not in valid_categories:
            result['category'] = 'Other'

        try:
            amt = float(str(result.get('total_amount', '0')).replace(',', ''))
            result['total_amount'] = f"{amt:.2f}"
        except (ValueError, TypeError):
            result['total_amount'] = '0.00'

        result['_extracted_by'] = 'gemini'
        print(f"   [OK] Gemini extraction+classification succeeded")
        return result

    except Exception as e:
        print(f"   [FAIL] Gemini extraction failed: {e}")
        return None


def extract_invoice_data(file_path, api_key=None):
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
            quality = _extraction_quality(page_data)
            print(f"   Heuristic extraction quality: {quality}/5")

            if quality < 3:
                print(f"   Low quality score — trying Gemini fallback...")
                raw_text = page_data.get('_raw_ocr_text', '')
                gemini_result = _extract_with_gemini(raw_text, api_key=api_key)
                if gemini_result:
                    page_data = gemini_result

            pages_data.append(page_data)
        except Exception as e:
            print(f"   Error on page {idx + 1}: {e}")

    return pages_data
