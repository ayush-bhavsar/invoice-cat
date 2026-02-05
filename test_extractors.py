import unittest
from src.extractors import extract_date, extract_amount, clean_text_for_ml

class TestExtractors(unittest.TestCase):
    
    def test_extract_date(self):
        text1 = "Invoice Date: 12/01/2024 due shortly"
        self.assertEqual(extract_date(text1), "2024-12-01")
        
        text2 = "Purchase made on 2023-05-20 in London"
        self.assertEqual(extract_date(text2), "2023-05-20")
        
        text3 = "Date: 15 Jan 2025"
        self.assertEqual(extract_date(text3), "2025-01-15")
        
        text_no_date = "There is no date here"
        self.assertIsNone(extract_date(text_no_date))

    def test_extract_amount(self):
        text1 = "Total: $550.00"
        self.assertEqual(extract_amount(text1), 550.00)
        
        text2 = "Items: $50.00, $20.00. Total due: $70.00"
        self.assertEqual(extract_amount(text2), 70.00) # Should pick max
        
        text3 = "Price £1,200.50"
        self.assertEqual(extract_amount(text3), 1200.50)
        
    def test_clean_text(self):
        raw = "Invoice #1234!!  -- Total: $500."
        cleaned = clean_text_for_ml(raw)
        self.assertEqual(cleaned, "invoice 1234 total 500")

if __name__ == '__main__':
    unittest.main()
