<<<<<<< HEAD
# invoice-cat

A modern invoice management system.
=======
# 🧾 Invoice-IQ — Smart Invoice Processing System

A powerful automated invoice processing system built with Python, Flask, and Tesseract OCR. This application extracts key financial data from invoice images and PDFs, categorizes items using AI-powered classification (Neural Network + Gemini LLM), and provides a rich analytics dashboard with interactive charts and reports.

## Project Overview

This project implements an intelligent invoice management system that:

*   **Extracts Data**: Automatically pulls Invoice ID, Date, Total Amount, Seller/Client names, Tax IDs, and IBAN details from invoices.
*   **Supports Multiple Formats**: Processes JPG, PNG, JPEG, PDF, and TIFF invoice files — including multi-page PDFs.
*   **Hybrid AI Classification**: Uses a trained Neural Network (TensorFlow/Keras) for fast local classification, with Google Gemini LLM as an intelligent fallback for unknown invoice formats.
*   **Multi-Format OCR**: Employs heuristic regex extraction for known invoice structures and falls back to Gemini-powered extraction when OCR quality is low.
*   **Analytics Dashboard**: Provides a full-featured analytics page with KPI cards, 8+ interactive charts (Chart.js), anomaly detection, data completeness tracking, and a sortable/searchable data table.
*   **Batch Processing**: Processes multiple invoices with batch tracking, individual batch reports, and batch-aware downloads.
*   **Generates Reports**: Consolidates extracted data into CSV files for easy accounting and supports PDF export of analytics.
*   **CSV Upload for Analysis**: Upload any CSV report directly to the analytics dashboard for instant visual analysis.
*   **Provides Intuitive UI**: Modern, responsive multi-page web interface with a landing page, upload page, how-it-works guide, and analytics dashboard.

## Technology Stack

*   **Backend Framework**: Flask (Python)
*   **OCR Engine**: Tesseract OCR
*   **AI / ML Classification**:
    *   TensorFlow / Keras (Feedforward Neural Network — primary classifier)
    *   Google Gemini API (LLM fallback for classification & extraction)
    *   Scikit-learn (TF-IDF Vectorization, Label Encoding)
*   **PDF Processing**: PyMuPDF (fitz)
*   **Data Processing**: Pandas, NumPy, Regular Expressions
*   **Frontend**: HTML5, CSS3, Vanilla JavaScript, Chart.js
*   **Data Storage**: CSV (File-based)
*   **Environment Management**: python-dotenv

## Prerequisites

Before you begin, ensure you have the following installed:

1.  **Python 3.8+**: [Download Here](https://www.python.org/downloads/)
2.  **Tesseract OCR**:
    *   **Windows**: [Download Installer](https://github.com/UB-Mannheim/tesseract/wiki) (Add to PATH during installation)
    *   **Linux**: `sudo apt install tesseract-ocr`
    *   **macOS**: `brew install tesseract`
3.  **Google Gemini API Key** *(optional but recommended)*: Required for LLM-powered fallback extraction and classification. Get one from [Google AI Studio](https://aistudio.google.com/).

## Installation

### Method 1: Auto-Launcher (Recommended for Windows)

The easiest way to get started is using the included automation script.

**Steps:**

1.  Double-click **`run.bat`** in the project root directory.

**What the script does:**
*   Checks for Python installation.
*   Automatically installs/updates dependencies from `requirements.txt`.
*   Starts the Flask server.
*   Keeps the window open for log viewing.

---

### Method 2: Manual Installation

If you prefer to set up the project manually or are using a non-Windows system, follow these steps:

**Step 1: Install Dependencies**

Open a terminal in the project root and run:

```bash
pip install -r requirements.txt
```

This installs:
*   `flask`, `flask-cors` (Web Server & CORS)
*   `pytesseract`, `Pillow` (OCR & Image Processing)
*   `PyMuPDF` (PDF Rendering)
*   `tensorflow`, `joblib` (Neural Network Model)
*   `pandas`, `scikit-learn`, `numpy` (Data Analysis & ML Preprocessing)
*   `google-generativeai`, `python-dotenv` (Gemini LLM Integration)

**Step 2: Configure Environment Variables**

Create a `.env` file in the project root (or edit the existing one):

```
LLM_API_KEY=your_gemini_api_key_here
```

> **Note:** The Gemini API key is optional. Without it, the system will use the local Neural Network for classification and skip LLM-based extraction fallback.

**Step 3: Train the Neural Network** *(First-time setup)*

Generate training data and train the classifier:

```bash
python generate_training_data.py
python train_nn.py
```

This creates the model files (`nn_model.keras`, `vectorizer.pkl`, `label_encoder.pkl`) needed for local classification.

**Step 4: Start the Server**

```bash
python server.py
```

**Step 5: Access the Application**

Open your browser and navigate to:
`http://127.0.0.1:5000/`

## Project Structure

```
SmartInvoiceProject/
├── server.py                 # Main Flask application & API routes
├── ocr_engine.py             # Hybrid OCR extraction (Tesseract + Gemini fallback)
├── classifier.py             # AI classification (Neural Network + Gemini LLM)
├── main.py                   # CLI batch processing entry point
├── train_nn.py               # Neural network training script
├── evaluate_model.py         # Model evaluation & metrics
├── generate_training_data.py # Synthetic training data generator
├── run.bat                   # Windows auto-start script
├── render-build.sh           # Render.com deployment script
├── requirements.txt          # Python dependencies
├── .env                      # Environment variables (API keys)
├── .gitignore                # Git ignore rules
├── LICENSE                   # Project license
├── README.md                 # Project documentation
├── nn_model.keras            # Trained neural network model
├── vectorizer.pkl            # TF-IDF vectorizer (serialized)
├── label_encoder.pkl         # Label encoder (serialized)
├── frontend/                 # Web Interface
│   ├── index.html            # Landing page
│   ├── upload.html           # Invoice upload page
│   ├── how_it_works.html     # How It Works guide
│   ├── analytics.html        # Analytics dashboard
│   ├── analytics.js          # Dashboard logic & Chart.js integration
│   ├── script.js             # Upload page logic
│   └── style.css             # Global styles
├── invoices/                 # Upload directory (Auto-created)
├── output/                   # Generated Reports (Auto-created)
└── training_data/            # ML Training resources
    └── categories.csv        # Training dataset
```

## Usage

### Web Interface

1.  **Home**: Visit the landing page for an overview and quick navigation.
2.  **Upload**: Go to the Upload page — drag & drop invoice images or PDFs (JPG, PNG, PDF, TIFF).
3.  **View Results**: See extracted data (Invoice ID, Date, Amount, Seller, Client, Tax IDs) and the AI-predicted category.
4.  **Save**: Click "Save to Database" to append the data to the CSV report.
5.  **Download**: Download individual batch reports or the consolidated `final_detailed_report.csv`.
6.  **Analytics**: Navigate to the Analytics Dashboard to visualize your invoice data with interactive charts, KPI summaries, and anomaly detection.
7.  **CSV Analysis**: Upload any CSV report directly in the Analytics page for instant visual analysis.

### CLI Batch Processing

For processing a folder of invoices without the web UI:

```bash
python main.py
```

This processes all files in the `invoices/` folder and outputs results to `output/final_detailed_report.csv`.

## Analytics Dashboard Features

The analytics dashboard provides deep insights into your invoice data:

*   📊 **KPI Cards** — Total invoices, total spend, average invoice value, highest invoice, unique sellers & clients
*   🥧 **Category Distribution** — Pie chart of invoice categories
*   📈 **Spending by Category** — Bar chart of spend per category
*   📉 **Monthly Spending Trend** — Line chart of spending over time
*   📊 **Category Trend Over Time** — Stacked area chart showing category spend evolution
*   📊 **Invoice Amount Distribution** — Histogram of invoice value ranges
*   🌍 **IBAN Country Distribution** — Geographic breakdown of seller IBANs
*   🛡️ **Data Completeness** — Compliance tracking for missing Tax IDs and IBANs
*   ⚠️ **Anomaly Detection** — Automatically flags outlier invoices (>2σ from mean)
*   📋 **Interactive Data Table** — Sortable, searchable, filterable table of all invoice records
*   📥 **PDF Export** — Export the entire dashboard as a PDF report
*   📂 **Batch Selector** — Switch between individual batch reports or the full report

## How It Works — Processing Pipeline

```
Invoice File (JPG/PNG/PDF/TIFF)
        │
        ▼
┌─────────────────────┐
│  Tesseract OCR      │ ──► Raw text extraction
└─────────────────────┘
        │
        ▼
┌─────────────────────┐
│  Heuristic Parser   │ ──► Regex-based field extraction
└─────────────────────┘     (Invoice ID, Date, Amount, Tax IDs, IBAN, etc.)
        │
        ▼
┌─────────────────────┐    Low quality?     ┌──────────────────────┐
│  Quality Scoring    │ ──────────────────► │  Gemini LLM Fallback │
│  (0-5 fields)       │                     │  (Extract + Classify) │
└─────────────────────┘                     └──────────────────────┘
        │                                            │
        ▼                                            ▼
┌─────────────────────┐                    Category provided by Gemini
│  Neural Network     │
│  Classifier (TF/K)  │ ──► Category prediction
└─────────────────────┘
        │
        ▼
┌─────────────────────┐
│  CSV Report Output  │ ──► Saved to output/
└─────────────────────┘
```

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/` | Landing page |
| `GET` | `/upload-page` | Invoice upload page |
| `GET` | `/how-it-works` | How It Works page |
| `GET` | `/analytics` | Analytics dashboard |
| `POST` | `/upload` | Upload and process an invoice file |
| `GET` | `/download_report` | Download CSV report (supports `?batch_id=`) |
| `GET` | `/api/batch-list` | List all available batch reports |
| `GET` | `/api/analytics` | Get aggregated analytics JSON (supports `?batch_id=`) |
| `POST` | `/api/upload-csv` | Upload a CSV for manual analytics |

## Troubleshooting

**Common Issues:**

*   **"Tesseract Not Found"**:
    *   Ensure Tesseract is installed and added to your system PATH.
    *   Or manually set the path in `ocr_engine.py`:
        ```python
        pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
        ```

*   **"ModuleNotFoundError"**:
    *   Run `pip install -r requirements.txt` again to ensure all packages are installed.

*   **"NN model or preprocessors missing"**:
    *   Run `python generate_training_data.py` followed by `python train_nn.py` to generate and train the model.

*   **Gemini API Rate Limit Errors**:
    *   The system automatically falls back to local NN classification when Gemini is rate-limited.
    *   Reduce batch sizes or wait before retrying.

*   **PDF Processing Not Working**:
    *   Ensure `PyMuPDF` is installed: `pip install PyMuPDF`

---

*Made with ❤️ and tons of ☕.*


## Team Members

- Manav Patel
- Ayush Bhavsar
- Rudra Misrti
- Manoj Ahir
- Vraj Shah


## License

This project is proprietary software. All rights reserved.

**Copyright © 2026 Manav Patel**

- **Modify:** Not permitted without explicit permission
- **Contributions:** Welcome, but require prior approval from the repository owner
- **Viewing:** Allowed for educational/reference purposes only

See the [LICENSE](LICENSE) file for full terms and conditions.

**License created by:** Manav Patel

*(Because we're generous like that, or maybe just too tired to argue)*
>>>>>>> B3
