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
        "total_net_worth": "0.00",
        "total_vat": "0.00",
        "total_gross_worth": "0.00",
        "vat_percent": "N/A",
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

    # ── Extract VAT%, Net Worth, VAT, Gross Worth from the SUMMARY section ──
    summary_y = None
    for i in range(n_boxes):
        if ocr_data['text'][i].strip().upper() == 'SUMMARY':
            summary_y = ocr_data['top'][i]
            break

    if summary_y is not None:
        # Find the "Total" row in the summary section
        summary_total_y = None
        for i in range(n_boxes):
            if ocr_data['top'][i] > summary_y and ocr_data['text'][i].strip().lower() == 'total':
                summary_total_y = ocr_data['top'][i]
                break

        if summary_total_y is not None:
            # Gather all text on the Total row
            total_row_items = []
            for i in range(n_boxes):
                if abs(ocr_data['top'][i] - summary_total_y) < 25:
                    total_row_items.append(ocr_data['text'][i].strip())
            total_row_text = " ".join(total_row_items)
            amounts_in_row = re.findall(r'[\$]?\s*\d[\d\s]*[.,]\d{2}', total_row_text)
            parsed_amounts = []
            for m in amounts_in_row:
                clean_str = m.replace("$", "").replace(" ", "").replace(",", ".")
                try:
                    parsed_amounts.append(float(clean_str))
                except ValueError:
                    continue
            # Typically: Net Worth, VAT, Gross Worth (3 amounts in order)
            if len(parsed_amounts) >= 3:
                data["total_net_worth"] = f"{parsed_amounts[0]:.2f}"
                data["total_vat"] = f"{parsed_amounts[1]:.2f}"
                data["total_gross_worth"] = f"{parsed_amounts[2]:.2f}"
                data["total_amount"] = f"{parsed_amounts[2]:.2f}"
            elif len(parsed_amounts) == 2:
                data["total_net_worth"] = f"{parsed_amounts[0]:.2f}"
                data["total_gross_worth"] = f"{parsed_amounts[1]:.2f}"
                data["total_amount"] = f"{parsed_amounts[1]:.2f}"
            elif len(parsed_amounts) == 1:
                data["total_gross_worth"] = f"{parsed_amounts[0]:.2f}"
                data["total_amount"] = f"{parsed_amounts[0]:.2f}"

        # Find VAT% from the summary (look for percentage value like "10%")
        for i in range(n_boxes):
            if ocr_data['top'][i] > summary_y:
                txt = ocr_data['text'][i].strip()
                vat_match = re.match(r'^(\d+)%$', txt)
                if vat_match:
                    data["vat_percent"] = txt
                    break

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


def _extract_with_gemini_vision(img, api_key=None):
    """
    Send the actual invoice IMAGE to Gemini Vision for extraction.
    This is far more accurate than sending OCR text since the model
    can see the layout, tables, fonts, and structure directly.
    Returns a data dict with 'category' key, or None on failure.
    """
    effective_key = api_key or GEMINI_API_KEY
    if not effective_key:
        return None

    try:
        genai.configure(api_key=effective_key)
        model = genai.GenerativeModel('gemini-2.5-flash')

        prompt = """You are an expert invoice processing AI.
Analyze this invoice image carefully and extract all the information.

Return ONLY valid JSON (no markdown, no explanation), with these exact keys:
{
  "invoice_id": "the invoice number or ID",
  "date": "the invoice date in dd/mm/yyyy format",
  "seller_name": "the seller/vendor company name (who is issuing the invoice)",
  "client_name": "the buyer/client name (who is being billed)",
  "seller_tax_id": "seller tax ID / GSTIN / PAN if present",
  "client_tax_id": "client tax ID / GSTIN if present",
  "seller_iban": "seller IBAN / bank account number if present",
  "total_amount": "the final total amount as a number like 123.45 (use grand total / balance due, not subtotal)",
  "total_net_worth": "the total net worth (before tax) as a number like 123.45, or 0.00 if not found",
  "total_vat": "the total VAT/tax amount as a number like 12.34, or 0.00 if not found",
  "total_gross_worth": "the total gross worth (after tax) as a number like 135.79, or 0.00 if not found",
  "vat_percent": "the VAT percentage like '10%' or 'N/A' if not found",
  "product_descriptions": ["list", "of", "item", "descriptions", "from", "the", "invoice"],
  "category": "one of: Electronics, Furniture, Kitchen, Clothing, Beverages, Office Supplies, Books & Media, Services, Hardware, Other"
}

Rules:
- For missing fields, use "Not Found"
- For total_amount, total_net_worth, total_vat, total_gross_worth use "0.00" if not found
- For vat_percent use "N/A" if not found
- seller_name = the company ISSUING the invoice (usually at the top)
- client_name = the entity RECEIVING / being billed (labeled Bill To / Ship To / Client)
- Prefer Invoice Date over Due Date
- Prefer the FINAL total (after tax) over subtotal
- Look for the SUMMARY section at the bottom for net worth, VAT, and gross worth totals
- Output ONLY the JSON object, nothing else"""

        response = model.generate_content([prompt, img])
        text = response.text.strip()

        # Clean markdown wrapper if present
        if text.startswith("```json"):
            text = text[7:]
        if text.startswith("```"):
            text = text[3:]
        if text.endswith("```"):
            text = text[:-3]
        text = text.strip()

        result = json.loads(text)

        # Validate category
        valid_categories = [
            "Hardware", "Books & Media", "Furniture", "Services", "Electronics",
            "Clothing", "Kitchen", "Office Supplies", "Beverages", "Other"
        ]
        if result.get('category') not in valid_categories:
            result['category'] = 'Other'

        # Normalize total amount and summary fields
        for amt_field in ['total_amount', 'total_net_worth', 'total_vat', 'total_gross_worth']:
            try:
                amt = float(str(result.get(amt_field, '0')).replace(',', '').replace(' ', ''))
                result[amt_field] = f"{amt:.2f}"
            except (ValueError, TypeError):
                result[amt_field] = '0.00'

        if 'vat_percent' not in result or not result['vat_percent']:
            result['vat_percent'] = 'N/A'

        # Ensure product_descriptions is a list
        if not isinstance(result.get('product_descriptions'), list):
            result['product_descriptions'] = []

        result['_extracted_by'] = 'gemini'
        print(f"   [OK] Gemini Vision extraction+classification succeeded")
        return result

    except Exception as e:
        print(f"   [FAIL] Gemini Vision extraction failed: {e}")
        return None


def _extract_with_gemini(ocr_text, api_key=None):
    """
    Fallback: Gemini API call using OCR text (when vision is unavailable).
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
  "total_net_worth": "the total net worth (before tax) as a number like 123.45, or 0.00 if not found",
  "total_vat": "the total VAT/tax amount as a number like 12.34, or 0.00 if not found",
  "total_gross_worth": "the total gross worth (after tax) as a number like 135.79, or 0.00 if not found",
  "vat_percent": "the VAT percentage like '10%' or 'N/A' if not found",
  "product_descriptions": ["list", "of", "product", "descriptions"],
  "category": "one of: Electronics, Furniture, Kitchen, Clothing, Beverages, Office Supplies, Books & Media, Services, Hardware, Other"
}}

Rules:
- For missing fields, use "Not Found"
- For total_amount, total_net_worth, total_vat, total_gross_worth use "0.00" if not found
- For vat_percent use "N/A" if not found
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

        for amt_field in ['total_amount', 'total_net_worth', 'total_vat', 'total_gross_worth']:
            try:
                amt = float(str(result.get(amt_field, '0')).replace(',', '').replace(' ', ''))
                result[amt_field] = f"{amt:.2f}"
            except (ValueError, TypeError):
                result[amt_field] = '0.00'

        if 'vat_percent' not in result or not result['vat_percent']:
            result['vat_percent'] = 'N/A'

        if not isinstance(result.get('product_descriptions'), list):
            result['product_descriptions'] = []

        result['_extracted_by'] = 'gemini'
        print(f"   [OK] Gemini OCR-text extraction succeeded")
        return result

    except Exception as e:
        print(f"   [FAIL] Gemini OCR-text extraction failed: {e}")
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

    effective_key = api_key or GEMINI_API_KEY
    pages_data = []

    for idx, img in enumerate(images):
        if ext == '.pdf':
            print(f"   Processing page {idx + 1}/{len(images)}...")
        try:
            # ── STRATEGY: When API key is available, use Gemini Vision FIRST ──
            # Gemini Vision is far more accurate because it sees the actual image
            # layout, tables, and text directly — no OCR errors to deal with.

            if effective_key:
                print(f"   API key available — using Gemini Vision (primary)...")
                gemini_result = _extract_with_gemini_vision(img, api_key=api_key)

                if gemini_result:
                    pages_data.append(gemini_result)
                    continue
                else:
                    # Vision failed — try OCR text fallback with Gemini
                    print(f"   Vision failed — falling back to heuristic + Gemini OCR text...")
                    page_data = _extract_from_image(img)
                    raw_text = page_data.get('_raw_ocr_text', '')
                    gemini_text_result = _extract_with_gemini(raw_text, api_key=api_key)
                    if gemini_text_result:
                        pages_data.append(gemini_text_result)
                        continue
                    else:
                        # Both Gemini methods failed — use heuristic
                        print(f"   All Gemini methods failed — using heuristic result")
                        pages_data.append(page_data)
                        continue

            # ── No API key: heuristic only ──
            print(f"   No API key — using heuristic extraction only")
            page_data = _extract_from_image(img)
            quality = _extraction_quality(page_data)
            print(f"   Heuristic extraction quality: {quality}/5")
            print(f"   TIP: Enter your Gemini API key in the website for much better results")
            pages_data.append(page_data)

        except Exception as e:
            print(f"   Error on page {idx + 1}: {e}")

    return pages_data
