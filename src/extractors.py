import re
import dateutil.parser

def extract_date(text):
    """
    Extracts the first valid date found in the text using Regex.
    Supports formats: DD/MM/YYYY, MM-DD-YYYY, YYYY/MM/DD, etc.
    """
    # Regex pattern to match common date formats
    # Matches: 12/01/2024, 12-01-2024, 2024.12.01, 12 Jan 2024
    date_pattern = r'(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})|(\d{4}[/-]\d{1,2}[/-]\d{1,2})|(\d{1,2}\s(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\s\d{2,4})'
    
    matches = re.findall(date_pattern, text)
    
    for match in matches:
        # Flatten the tuple result from findall
        date_str = next((m for m in match if m), None)
        if date_str:
            try:
                # Use dateutil to parse the string into a standard datetime object
                dt = dateutil.parser.parse(date_str)
                return dt.strftime("%Y-%m-%d") # Return standard ISO format
            except (ValueError, OverflowError):
                continue
                
    return None

def extract_amount(text):
    """
    Extracts the Total Amount from the text.
    It looks for the largest monetary value or specific keywords like "Total".
    """
    # Regex for currency: $50.00, 50.00 EUR, £50.00, 50.00
    # Looks for a number with 2 decimal places, optionally preceded by a currency symbol
    amount_pattern = r'[\$\£\€]?\s?(\d{1,3}(?:,\d{3})*(?:\.\d{2}))'
    
    amounts = re.findall(amount_pattern, text)
    
    # Convert matches to float
    valid_amounts = []
    for amount in amounts:
        try:
            # Remove commas (e.g., 1,000.00 -> 1000.00)
            clean_amount = amount.replace(',', '')
            valid_amounts.append(float(clean_amount))
        except ValueError:
            continue
            
    if not valid_amounts:
        return 0.0
        
    # Heuristic: The "Total" is often the largest number on the invoice
    return max(valid_amounts)

def clean_text_for_ml(text):
    """
    Basic text cleaning for the ML model (Step 4).
    Removes special characters and extra spaces.
    """
    # Keep only letters and numbers
    text = re.sub(r'[^a-zA-Z0-9\s]', '', text)
    # Collapse multiple spaces into one
    text = re.sub(r'\s+', ' ', text).strip()
    return text.lower()
