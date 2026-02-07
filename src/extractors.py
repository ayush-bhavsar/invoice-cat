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
    # Regex for currency: 
    # 1. Standard US: $1,234.56
    # 2. European/Space: $ 1 234,56 or 1 234.56 or € 1.234,56
    # 3. Plain: 1234.56
    
    # Strategy: Find all numbers that look like currency, then clean them.
    # We look for patterns that end with 2 decimals.
    # The regex now optionally matches a currency symbol at the start, followed by optional space
    
    # Matches: $ 1 234,56 | 1,234.56 | 1234.56 | 1234,56
    # It allows simple spaces or commas or dots as separators
    amount_pattern = r'(?:[\$\€\£]\s?)?(\d{1,3}(?:[ .,]\d{3})*[.,]\d{2})'
    
    amounts = re.findall(amount_pattern, text)
    
    # Convert matches to float
    valid_amounts = []
    for amount in amounts:
        try:
            # Clean up the string to standard float format (1234.56)
            # Remove spaces
            clean_str = amount.replace(' ', '')
            # Replace comma with dot if it's the decimal separator (European)
            # Heuristic: if comma is at index -3 (e.g. 123,45), replace it
            if ',' in clean_str and clean_str[-3] == ',':
                 clean_str = clean_str.replace('.', '').replace(',', '.')
            else:
                 # Standard US: remove commas
                 clean_str = clean_str.replace(',', '')
            
            val = float(clean_str)
            
            # Filter out small numbers/versions (like 3.20) or years (2013.04)
            # Heuristic: Invoice totals are usually > 10.00
            if val > 10.00:
                valid_amounts.append(val)
                
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
