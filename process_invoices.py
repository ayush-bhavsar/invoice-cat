"""
Invoice Processing System using Gemini API (Free Tier)
Processes invoice images, extracts data, and categorizes them automatically.
"""

import os
import time
import json
import csv
from pathlib import Path
from typing import List, Dict, Optional
import google.generativeai as genai
from PIL import Image
from datetime import datetime
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('output/processing.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class InvoiceProcessor:
    """Process invoices using Gemini Vision API"""

    # Category definitions
    CATEGORIES = [
        "Office Supplies",
        "Technology/IT Equipment",
        "Professional Services",
        "Marketing/Advertising",
        "Travel & Accommodation",
        "Utilities",
        "Maintenance & Repairs",
        "Food & Beverages",
        "Other"
    ]

    # Gemini API rate limits for free tier
    REQUESTS_PER_MINUTE = 15
    DELAY_BETWEEN_REQUESTS = 60 / REQUESTS_PER_MINUTE  # ~4 seconds

    def __init__(self, api_key: str, input_folder: str = "invoices", output_folder: str = "output"):
        """
        Initialize the invoice processor

        Args:
            api_key: Google Gemini API key
            input_folder: Folder containing invoice images
            output_folder: Folder for output files
        """
        self.api_key = api_key
        self.input_folder = Path(input_folder)
        self.output_folder = Path(output_folder)
        self.output_folder.mkdir(exist_ok=True)

        # Configure Gemini
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel('gemini-1.5-flash')

        # Progress tracking
        self.processed_count = 0
        self.failed_count = 0
        self.results = []

        # Resume capability
        self.progress_file = self.output_folder / "progress.json"
        self.output_csv = self.output_folder / "invoice_data.csv"

        logger.info("Invoice Processor initialized")
        logger.info(f"Input folder: {self.input_folder}")
        logger.info(f"Output folder: {self.output_folder}")

    def get_prompt(self) -> str:
        """Get the analysis prompt for Gemini"""
        categories_list = "\n   - ".join(self.CATEGORIES)

        return f"""You are an invoice categorization assistant.

Analyze this invoice image and:

1. Extract key information:
   - Invoice number
   - Date of issue
   - Seller name
   - Client name
   - All item descriptions
   - Total amount (gross worth)

2. Categorize this invoice into ONE of these categories:
   - {categories_list}

3. Provide your response in this EXACT JSON format (no markdown, no code blocks, just pure JSON):
{{
  "invoice_number": "extracted number",
  "date": "MM/DD/YYYY",
  "seller": "seller name",
  "client": "client name",
  "category": "selected category name",
  "confidence": "high/medium/low",
  "items_found": ["item 1", "item 2", "item 3"],
  "reasoning": "brief explanation of why this category was chosen",
  "total_amount": "numeric value only"
}}

Base your categorization primarily on the description of goods/services in the invoice, not just the vendor name.
Respond ONLY with valid JSON, no additional text."""

    def analyze_invoice(self, image_path: Path) -> Optional[Dict]:
        """
        Analyze a single invoice image

        Args:
            image_path: Path to the invoice image

        Returns:
            Dictionary with extracted data or None if failed
        """
        try:
            logger.info(f"Processing: {image_path.name}")

            # Load image
            image = Image.open(image_path)

            # Get prompt
            prompt = self.get_prompt()

            # Call Gemini API
            response = self.model.generate_content([prompt, image])

            # Parse response
            response_text = response.text.strip()

            # Remove markdown code blocks if present
            if response_text.startswith("```json"):
                response_text = response_text.replace("```json", "").replace("```", "").strip()
            elif response_text.startswith("```"):
                response_text = response_text.replace("```", "").strip()

            # Parse JSON
            data = json.loads(response_text)

            # Add filename
            data['invoice_file'] = image_path.name

            logger.info(f"✓ Successfully processed: {image_path.name}")
            logger.info(f"  Category: {data.get('category', 'Unknown')}")
            logger.info(f"  Amount: ${data.get('total_amount', '0')}")

            return data

        except json.JSONDecodeError as e:
            logger.error(f"✗ JSON parsing error for {image_path.name}: {e}")
            logger.error(f"  Response: {response_text[:200]}")
            return None
        except Exception as e:
            logger.error(f"✗ Error processing {image_path.name}: {e}")
            return None

    def load_progress(self) -> List[str]:
        """Load list of already processed files"""
        if self.progress_file.exists():
            with open(self.progress_file, 'r') as f:
                progress = json.load(f)
                logger.info(f"Resuming: {len(progress.get('processed', []))} files already processed")
                return progress.get('processed', [])
        return []

    def save_progress(self, processed_files: List[str]):
        """Save progress to file"""
        with open(self.progress_file, 'w') as f:
            json.dump({
                'processed': processed_files,
                'last_updated': datetime.now().isoformat()
            }, f, indent=2)

    def save_results(self):
        """Save results to CSV"""
        if not self.results:
            logger.warning("No results to save")
            return

        # Define CSV columns
        fieldnames = [
            'invoice_file', 'invoice_number', 'date', 'seller', 'client',
            'category', 'confidence', 'items_found', 'reasoning', 'total_amount'
        ]

        # Write CSV
        with open(self.output_csv, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()

            for result in self.results:
                # Convert items list to string
                row = result.copy()
                if isinstance(row.get('items_found'), list):
                    row['items_found'] = ', '.join(row['items_found'])
                writer.writerow(row)

        logger.info(f"✓ Results saved to: {self.output_csv}")

    def process_all(self, max_files: Optional[int] = None):
        """
        Process all invoice images in the input folder

        Args:
            max_files: Maximum number of files to process (None for all)
        """
        # Get all image files
        image_extensions = {'.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff'}
        image_files = [
            f for f in self.input_folder.iterdir()
            if f.is_file() and f.suffix.lower() in image_extensions
        ]

        if not image_files:
            logger.error(f"No image files found in {self.input_folder}")
            return

        # Load progress
        processed_files = self.load_progress()

        # Filter out already processed files
        remaining_files = [f for f in image_files if f.name not in processed_files]

        if max_files:
            remaining_files = remaining_files[:max_files]

        total_files = len(remaining_files)
        logger.info(f"\n{'='*60}")
        logger.info(f"Starting invoice processing")
        logger.info(f"Total files to process: {total_files}")
        logger.info(f"Estimated time: {total_files * self.DELAY_BETWEEN_REQUESTS / 60:.1f} minutes")
        logger.info(f"{'='*60}\n")

        start_time = time.time()

        # Process each file
        for idx, image_file in enumerate(remaining_files, 1):
            logger.info(f"\n[{idx}/{total_files}] Processing {image_file.name}")

            # Analyze invoice
            result = self.analyze_invoice(image_file)

            if result:
                self.results.append(result)
                processed_files.append(image_file.name)
                self.processed_count += 1
            else:
                self.failed_count += 1

            # Save progress after each file
            self.save_progress(processed_files)
            self.save_results()

            # Rate limiting for free tier
            if idx < total_files:  # Don't delay after last file
                logger.info(f"⏳ Waiting {self.DELAY_BETWEEN_REQUESTS:.1f}s (rate limiting)...")
                time.sleep(self.DELAY_BETWEEN_REQUESTS)

        # Final summary
        elapsed_time = time.time() - start_time
        logger.info(f"\n{'='*60}")
        logger.info(f"Processing Complete!")
        logger.info(f"{'='*60}")
        logger.info(f"✓ Successfully processed: {self.processed_count}")
        logger.info(f"✗ Failed: {self.failed_count}")
        logger.info(f"⏱ Total time: {elapsed_time / 60:.1f} minutes")
        logger.info(f"📄 Output file: {self.output_csv}")
        logger.info(f"{'='*60}\n")


def main():
    """Main entry point"""
    print("\n" + "="*60)
    print("Invoice Processing System - Gemini API (Free Tier)")
    print("="*60 + "\n")

    # Get API key
    api_key = os.getenv('GEMINI_API_KEY')

    if not api_key:
        print("⚠️  GEMINI_API_KEY not found in environment variables")
        api_key = input("Please enter your Gemini API key: ").strip()

        if not api_key:
            print("❌ API key is required. Exiting...")
            return

    # Configuration
    input_folder = "invoices"
    output_folder = "output"

    # Optional: limit number of files for testing
    print("\nConfiguration:")
    print(f"  Input folder: {input_folder}")
    print(f"  Output folder: {output_folder}")

    test_mode = input("\nTest mode (process only first 5 files)? [y/N]: ").strip().lower()
    max_files = 5 if test_mode == 'y' else None

    # Create processor
    processor = InvoiceProcessor(
        api_key=api_key,
        input_folder=input_folder,
        output_folder=output_folder
    )

    # Confirm
    print("\n" + "="*60)
    if max_files:
        print(f"Ready to process {max_files} invoices (TEST MODE)")
    else:
        print("Ready to process ALL invoices")
    print("="*60)

    confirm = input("\nPress ENTER to start or Ctrl+C to cancel...")

    # Process
    processor.process_all(max_files=max_files)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️  Processing interrupted by user")
    except Exception as e:
        print(f"\n\n❌ Error: {e}")
        logger.exception("Fatal error")
