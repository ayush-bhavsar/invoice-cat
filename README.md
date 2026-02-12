# Invoice Processing System 🧾

Automated invoice processing system using Google Gemini Vision API (Free Tier). Extracts data from invoice images and categorizes them automatically.

## Features ✨

- 📄 **Batch Processing**: Process hundreds of invoices automatically
- 🤖 **AI-Powered**: Uses Gemini Vision API for accurate extraction
- 🏷️ **Auto-Categorization**: Classifies invoices into 9 business categories
- 💾 **Progress Saving**: Resume processing if interrupted
- 📊 **CSV Export**: Structured dataset output
- 🆓 **Free Tier Optimized**: Respects Gemini API rate limits
- 📈 **Real-time Progress**: Live updates during processing

## Categories Supported

- Office Supplies
- Technology/IT Equipment
- Professional Services
- Marketing/Advertising
- Travel & Accommodation
- Utilities
- Maintenance & Repairs
- Food & Beverages
- Other

## Prerequisites

1. Python 3.8 or higher
2. Google Gemini API key (FREE)

## Setup Instructions

### 1. Get Your Free Gemini API Key

1. Visit: https://makersuite.google.com/app/apikey
2. Sign in with your Google account
3. Click "Create API Key"
4. Copy your API key

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Configure API Key

**Option A: Environment Variable (Recommended)**
```bash
# Windows (PowerShell)
$env:GEMINI_API_KEY="your_api_key_here"

# Windows (CMD)
set GEMINI_API_KEY=your_api_key_here

# Linux/Mac
export GEMINI_API_KEY="your_api_key_here"
```

**Option B: .env File**
```bash
# Copy example file
cp .env.example .env

# Edit .env and add your API key
GEMINI_API_KEY=your_actual_api_key_here
```

**Option C: Enter When Prompted**
The script will ask for your API key if not found.

### 4. Prepare Your Invoices

Place all invoice images in the `invoices/` folder:
```
ocr/
├── invoices/
│   ├── invoice001.jpg
│   ├── invoice002.jpg
│   └── ...
```

Supported formats: JPG, JPEG, PNG, GIF, BMP, TIFF

## Usage

### Basic Usage

```bash
python process_invoices.py
```

### Test Mode (Process First 5 Files)

```bash
python process_invoices.py
# When prompted, type 'y' for test mode
```

### Check Output

Results are saved in the `output/` folder:
```
output/
├── invoice_data.csv       # Main dataset
├── processing.log         # Detailed logs
└── progress.json          # Resume capability
```

## Output Format

The CSV file contains:
- `invoice_file`: Original filename
- `invoice_number`: Extracted invoice number
- `date`: Invoice date (MM/DD/YYYY)
- `seller`: Vendor/seller name
- `client`: Customer/client name
- `category`: Assigned category
- `confidence`: Classification confidence (high/medium/low)
- `items_found`: List of items/services
- `reasoning`: Why this category was chosen
- `total_amount`: Total invoice amount

## Rate Limits (Free Tier)

- **15 requests per minute**
- **1,500 requests per day**
- Script automatically adds 4-second delays between requests
- 500 images = ~33 minutes processing time

## Resume Capability

If processing is interrupted:
- Progress is automatically saved after each file
- Simply run the script again - it will skip already processed files
- Check `output/progress.json` to see what's been processed

## Troubleshooting

### "No API key found"
- Make sure you set the environment variable correctly
- Or enter it when prompted

### "Rate limit exceeded"
- Free tier: 15 requests/minute, 1500/day
- Wait a few minutes and run again
- Script will resume from where it stopped

### "No image files found"
- Check that images are in the `invoices/` folder
- Verify file extensions (jpg, png, etc.)

### "JSON parsing error"
- Usually temporary - the script will continue
- Failed files are logged in `output/processing.log`
- You can manually review and reprocess them

## Project Structure

```
ocr/
├── invoices/                  # Input folder (your images)
├── output/                    # Results folder
│   ├── invoice_data.csv      # Final dataset
│   ├── processing.log        # Processing logs
│   └── progress.json         # Resume data
├── process_invoices.py       # Main script
├── requirements.txt          # Dependencies
├── .env.example              # API key template
└── README.md                 # This file
```

## Example Output

```csv
invoice_file,invoice_number,date,seller,client,category,confidence,items_found,reasoning,total_amount
batch1-0371.jpg,39652805,03/20/2020,Lewis and Sons,Hancock LLC,Technology/IT Equipment,high,computer,Single computer purchase - IT hardware,329.99
```

## Tips for Best Results

1. **Good Image Quality**: Clear, well-lit images work best
2. **Standard Formats**: JPG and PNG are most reliable
3. **Test First**: Always run test mode on 5 files before processing 500
4. **Monitor Logs**: Watch `output/processing.log` for issues
5. **Backup**: Keep original images safe

## Cost Estimate

✅ **FREE** with Gemini 1.5 Flash
- Up to 1,500 invoices per day
- No credit card required

## Performance

- **Speed**: ~4 seconds per invoice (free tier rate limit)
- **Accuracy**: High for standard invoice formats
- **Capacity**: 500 images in ~33 minutes

## Support

If you encounter issues:
1. Check `output/processing.log` for detailed error messages
2. Verify your API key is valid
3. Ensure images are readable and not corrupted
4. Try processing a small batch first (5-10 files)

## License

Feel free to use and modify for your needs!

---

**Ready to process 500 invoices? Let's go! 🚀**
