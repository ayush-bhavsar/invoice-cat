# Smart Invoice Project

A powerful automated invoice processing system built with Python, Flask, and Tesseract OCR. This application extracts key financial data from invoice images, categorizes items using machine learning, and generates detailed CSV reports.

## Project Overview

This project implements an intelligent invoice management system that:

*   **Extracts Data**: Automatically pulls Invoice ID, Date, Total Amount, and Tax/IBAN details.
*   **Classifies Items**: Uses a trained machine learning model to categorize line items (e.g., "Food", "Transport").
*   **Generates Reports**: Consolidates data into CSV files for easy accounting.
*   **Provides Intuitive UI**: Simple drag-and-drop web interface for file uploads.
*   **Support Batch Processing**: Designed to handle multiple invoices efficiently.

## Technology Stack

*   **Backend Framework**: Flask (Python)
*   **OCR Engine**: Tesseract OCR
*   **Machine Learning**: Scikit-learn (SVM Classifier)
*   **Data Processing**: Pandas, Regular Expressions
*   **Frontend**: HTML5, CSS3, Vanilla JavaScript
*   **Data Storage**: CSV (File-based)

## Prerequisites

Before you begin, ensure you have the following installed:

1.  **Python 3.8+**: [Download Here](https://www.python.org/downloads/)
2.  **Tesseract OCR**:
    *   **Windows**: [Download Installer](https://github.com/UB-Mannheim/tesseract/wiki) (Add to PATH during installation)
    *   **Linux**: `sudo apt install tesseract-ocr`
    *   **macOS**: `brew install tesseract`

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
*   `flask`, `flask-cors` (Web Server)
*   `pytesseract`, `Pillow` (Image Processing)
*   `pandas`, `scikit-learn` (Data Analysis & ML)

**Step 2: Start the Server**

Run the following command:

```bash
python server.py
```

**Step 3: Access the Application**

Open your browser and navigate to:
`http://127.0.0.1:5000/`

## Project Structure

```
SmartInvoiceProject/
├── server.py               # Main Flask application
├── ocr_engine.py           # Core logic for OCR extraction
├── classifier.py           # Machine learning model for categorization
├── generate_training_data.py # Script to create synthetic training data
├── run.bat                 # Windows auto-start script
├── requirements.txt        # Python dependencies
├── README.md               # Project documentation
├── frontend/               # Web Interface
│   ├── index.html
│   ├── style.css
│   └── script.js
├── invoices/               # Upload directory (Auto-created)
├── output/                 # Generated Reports (Auto-created)
└── training_data/          # ML Training resources
    └── categories.csv
```

## Usage

1.  **Upload**: Drag and drop an invoice image (JPG, PNG) into the web interface.
2.  **Verify**: View the extracted data and the predicted category.
3.  **Save**: Click "Save to Database" to append the data to the CSV report.
4.  **Download**: Use the "Download Report" button to get the consolidated `final_detailed_report.csv`.

## Troubleshooting

**Common Issues:**

*   **"Tesseract Not Found"**:
    *   Ensure Tesseract is installed.
    *   Add Tesseract to your system PATH.
    *   Or manually set the path in `ocr_engine.py`:
        ```python
        pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
        ```

*   **"ModuleNotFoundError"**:
    *   Run `pip install -r requirements.txt` again to ensure all packages are installed.

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

**Copyright © 2025 Manav Patel**

- **Modify:** Not permitted without explicit permission
- **Contributions:** Welcome, but require prior approval from the repository owner
- **Viewing:** Allowed for educational/reference purposes only

See the [LICENSE](LICENSE) file for full terms and conditions.

**License created by:** Manav Patel

*(Because we're generous like that, or maybe just too tired to argue)*