import os
from flask import Flask, request, jsonify, send_from_directory
from werkzeug.utils import secure_filename
from flask_cors import CORS 
import pandas as pd

# Import our custom modules
try:
    from ocr_engine import extract_invoice_data
    from classifier import predict_category
except ImportError:
    print("Error imports. Run from project root.")

app = Flask(__name__, static_folder='frontend')
CORS(app) # Enable CORS just in case

# Configuration
UPLOAD_FOLDER = os.path.join(os.getcwd(), 'invoices')
OUTPUT_FOLDER = os.path.join(os.getcwd(), 'output') # Explicitly define output folder
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(OUTPUT_FOLDER, exist_ok=True) # Ensure it exists

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['OUTPUT_FOLDER'] = OUTPUT_FOLDER # Save to config

@app.route('/')
def serve_index():
    return send_from_directory('frontend', 'index.html')

# Serve other static files (css, js) from frontend folder
@app.route('/<path:path>')
def serve_static(path):
    return send_from_directory('frontend', path)

@app.route('/upload-page')
def serve_upload_page():
    return send_from_directory('frontend', 'upload.html')

@app.route('/how-it-works')
def serve_how_it_works():
    return send_from_directory('frontend', 'how_it_works.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400

    if file:
        filename = secure_filename(file.filename)
        save_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(save_path)
        
        print(f"Processing {filename}...")

        # 1. OCR Extraction
        try:
            raw_data_list = extract_invoice_data(save_path)
        except Exception as e:
            print(f"OCR Error: {e}")
            return jsonify({'error': f"OCR Error: {str(e)}"}), 500

        if not raw_data_list:
            return jsonify({'error': "OCR extracted no data"}), 400

        # 2. Classification
        from collections import Counter
        from classifier import predict_categories_batch
        classification_method = request.args.get('method', 'local_nn')
        
        response_data_list = []

        for p_idx, raw_data in enumerate(raw_data_list):
            votes = []
            if raw_data.get('product_descriptions'):
                cats = predict_categories_batch(raw_data['product_descriptions'], method=classification_method)
                for cat in cats:
                    if cat != "Other":
                        votes.append(cat)
            
            main_category = "Uncategorized"
            if votes:
                main_category = Counter(votes).most_common(1)[0][0]
            elif raw_data.get('product_descriptions'): 
                 main_category = "Other"

            # 3. Save to CSV
            if request.args.get('save') == 'true':
                batch_id = request.args.get('batch_id')
                print(f"Saving to CSV. Batch ID: {batch_id} (Page {p_idx+1})")
                save_row_to_csv({
                    "Invoice No": raw_data.get('invoice_id'),
                    "Date": raw_data.get('date'),
                    "Seller Name": raw_data.get('seller_name'),
                    "Client Name": raw_data.get('client_name'),
                    "Seller Tax ID": raw_data.get('seller_tax_id'),
                    "Seller IBAN": raw_data.get('seller_iban', ''), 
                    "Client Tax ID": raw_data.get('client_tax_id'),
                    "Total Amount": raw_data.get('total_amount'),
                    "Category": main_category
                }, batch_id)

            response_data_list.append({
                "filename": filename if len(raw_data_list) == 1 else f"{filename} (Page {p_idx+1})",
                "date": raw_data.get('date', 'Unknown'),
                "total_amount": raw_data.get('total_amount', '0.00'),
                "category": main_category
            })

        return jsonify(response_data_list)

def save_row_to_csv(data, batch_id=None):
    # 1. Save to Main Report (Archive)
    OUTPUT_CSV = os.path.join(app.config['OUTPUT_FOLDER'], 'final_detailed_report.csv')
    header = not os.path.exists(OUTPUT_CSV)
    df = pd.DataFrame([data])
    try:
        df.to_csv(OUTPUT_CSV, mode='a', header=header, index=False)
    except Exception as e:
        print(f"Error saving to main report: {e}")
        
    # 2. Save to Batch Report (if batch_id exists)
    if batch_id:
        BATCH_CSV = os.path.join(app.config['OUTPUT_FOLDER'], f'report_{batch_id}.csv')
        batch_header = not os.path.exists(BATCH_CSV)
        try:
            print(f"Writing to batch report: {BATCH_CSV}")
            df.to_csv(BATCH_CSV, mode='a', header=batch_header, index=False)
        except Exception as e:
            print(f"Error saving to batch report: {e}")

@app.route('/download_report')
def download_report():
    batch_id = request.args.get('batch_id')
    print(f"Download requested for batch_id: {batch_id}")
    
    if batch_id:
        filename = f'report_{batch_id}.csv'
        path = os.path.join(app.config['OUTPUT_FOLDER'], filename)
        if os.path.exists(path):
             print(f"Serving batch report: {path}")
             return send_from_directory(app.config['OUTPUT_FOLDER'], filename, as_attachment=True)
        else:
            print(f"Batch report not found: {path}")
    
    # Fallback to main report
    print("Serving fallback main report")
    OUTPUT_CSV = os.path.join(app.config['OUTPUT_FOLDER'], 'final_detailed_report.csv')
    if not os.path.exists(OUTPUT_CSV):
        return "Report file not found.", 404
        
    return send_from_directory(app.config['OUTPUT_FOLDER'], 'final_detailed_report.csv', as_attachment=True)


if __name__ == '__main__':
    print("Starting Smart Invoice Server...")
    print(f"Upload Folder: {UPLOAD_FOLDER}")
    print(f"Output Folder: {OUTPUT_FOLDER}")
    app.run(debug=True, port=5000)
