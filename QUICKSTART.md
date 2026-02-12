# Quick Start Guide ⚡

Get started in 3 minutes!

## Step 1: Install Dependencies (30 seconds)

```bash
pip install -r requirements.txt
```

## Step 2: Get Free API Key (1 minute)

1. Go to: https://makersuite.google.com/app/apikey
2. Click "Create API Key"
3. Copy the key

## Step 3: Set API Key (30 seconds)

**Windows PowerShell:**
```powershell
$env:GEMINI_API_KEY="paste_your_key_here"
```

**Windows CMD:**
```cmd
set GEMINI_API_KEY=paste_your_key_here
```

**Linux/Mac:**
```bash
export GEMINI_API_KEY="paste_your_key_here"
```

## Step 4: Run! (30 seconds)

```bash
python process_invoices.py
```

When prompted:
- Type `y` for test mode (5 files)
- Type `n` or press Enter for full processing

## Check Results

Open `output/invoice_data.csv` - Done! ✅

---

## For 500 Images

**Time**: ~33 minutes
**Cost**: FREE (Gemini Free Tier)
**Rate**: 15 images/minute (automatic)

The script will:
- ✅ Process all files automatically
- ✅ Save progress continuously
- ✅ Resume if interrupted
- ✅ Create structured CSV output

## Troubleshooting

| Issue | Solution |
|-------|----------|
| "No API key" | Set environment variable or enter when prompted |
| "No images found" | Put images in `invoices/` folder |
| Script interrupted | Just run again - it will resume |
| Rate limit error | Wait 1 minute, then continue |

---

**That's it! 🎉**
