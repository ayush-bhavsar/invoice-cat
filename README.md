# Smart Invoice Categorizer and Data Extractor

## Abstract
A machine learning application that automates invoice processing by extracting text (OCR), classifying categories (ML), and parsing entities (Regex).

## How to Run This Project

You need **two** terminals open to run this Full-Stack application.

### Terminal 1: Backend API
This powers the OCR and AI logic.
```bash
python src/api.py
```
*You should see: `Running on http://127.0.0.1:5000`*

### Terminal 2: Frontend Website
This launches the user interface.
```bash
cd frontend
python -m http.server 8000
```
*   Now open your browser to: [http://localhost:8000](http://localhost:8000)

---
### Setup (First Time Only)
1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
2. Install [Tesseract-OCR](https://github.com/UB-Mannheim/tesseract/wiki) and add to PATH.
