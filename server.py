import os
from flask import Flask, request, jsonify, send_from_directory
from werkzeug.utils import secure_filename
from flask_cors import CORS 
import pandas as pd

try:
    from ocr_engine import extract_invoice_data
    from classifier import predict_category
except ImportError:
    print("Error imports. Run from project root.")

app = Flask(__name__, static_folder='frontend')
CORS(app)

UPLOAD_FOLDER = os.path.join(os.getcwd(), 'invoices')
OUTPUT_FOLDER = os.path.join(os.getcwd(), 'output')
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['OUTPUT_FOLDER'] = OUTPUT_FOLDER

@app.route('/')
def serve_index():
    return send_from_directory('frontend', 'index.html')

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

        user_api_key = request.headers.get('X-API-Key')

        classification_method = request.args.get('method', 'local_nn')
        # Only use Gemini extraction when LLM mode is selected
        extraction_api_key = user_api_key if classification_method == 'gemini' else None

        try:
            raw_data_list = extract_invoice_data(save_path, api_key=extraction_api_key)
        except Exception as e:
            print(f"OCR Error: {e}")
            return jsonify({'error': f"OCR Error: {str(e)}"}), 500

        if not raw_data_list:
            return jsonify({'error': "OCR extracted no data"}), 400

        from collections import Counter
        from classifier import predict_categories_batch
        
        response_data_list = []

        for p_idx, raw_data in enumerate(raw_data_list):
            if raw_data.get('_extracted_by') == 'gemini' and raw_data.get('category'):
                main_category = raw_data['category']
                print(f"   Using Gemini-provided category: {main_category} (0 extra API calls)")
            else:
                votes = []
                if raw_data.get('product_descriptions'):
                    cats = predict_categories_batch(raw_data['product_descriptions'], method=classification_method, api_key=user_api_key)
                    for cat in cats:
                        if cat != "Other":
                            votes.append(cat)
                
                main_category = "Uncategorized"
                if votes:
                    main_category = Counter(votes).most_common(1)[0][0]
                elif raw_data.get('product_descriptions'): 
                     main_category = "Other"

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
                    "VAT %": raw_data.get('vat_percent', 'N/A'),
                    "Total Net Worth": raw_data.get('total_net_worth', '0.00'),
                    "Total VAT": raw_data.get('total_vat', '0.00'),
                    "Total Gross Worth": raw_data.get('total_gross_worth', '0.00'),
                    "Total Amount": raw_data.get('total_amount'),
                    "Category": main_category
                }, batch_id)

            response_data_list.append({
                "filename": filename if len(raw_data_list) == 1 else f"{filename} (Page {p_idx+1})",
                "date": raw_data.get('date', 'Unknown'),
                "total_amount": raw_data.get('total_amount', '0.00'),
                "vat_percent": raw_data.get('vat_percent', 'N/A'),
                "total_net_worth": raw_data.get('total_net_worth', '0.00'),
                "total_vat": raw_data.get('total_vat', '0.00'),
                "total_gross_worth": raw_data.get('total_gross_worth', '0.00'),
                "category": main_category
            })

        return jsonify(response_data_list)

def save_row_to_csv(data, batch_id=None):
    OUTPUT_CSV = os.path.join(app.config['OUTPUT_FOLDER'], 'final_detailed_report.csv')
    header = not os.path.exists(OUTPUT_CSV)
    df = pd.DataFrame([data])
    try:
        df.to_csv(OUTPUT_CSV, mode='a', header=header, index=False)
    except Exception as e:
        print(f"Error saving to main report: {e}")
        
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
    
    print("Serving fallback main report")
    OUTPUT_CSV = os.path.join(app.config['OUTPUT_FOLDER'], 'final_detailed_report.csv')
    if not os.path.exists(OUTPUT_CSV):
        return "Report file not found.", 404
        
    return send_from_directory(app.config['OUTPUT_FOLDER'], 'final_detailed_report.csv', as_attachment=True)


@app.route('/analytics')
def serve_analytics():
    return send_from_directory('frontend', 'analytics.html')

@app.route('/api/batch-list')
def api_batch_list():
    """List all available batch report files."""
    output_dir = app.config['OUTPUT_FOLDER']
    batches = []
    
    main_report = os.path.join(output_dir, 'final_detailed_report.csv')
    if os.path.exists(main_report):
        batches.append({
            'id': 'main',
            'name': 'Full Report (All Invoices)',
            'filename': 'final_detailed_report.csv'
        })
    
    for f in os.listdir(output_dir):
        if f.startswith('report_') and f.endswith('.csv'):
            batch_id = f.replace('report_', '').replace('.csv', '')
            batches.append({
                'id': batch_id,
                'name': f'Batch {batch_id}',
                'filename': f
            })
    
    return jsonify(batches)

@app.route('/api/analytics')
def api_analytics():
    """Return aggregated analytics data from a CSV report."""
    batch_id = request.args.get('batch_id')
    output_dir = app.config['OUTPUT_FOLDER']
    
    if batch_id and batch_id != 'main':
        csv_path = os.path.join(output_dir, f'report_{batch_id}.csv')
        if not os.path.exists(csv_path):
            csv_path = os.path.join(output_dir, 'final_detailed_report.csv')
    else:
        csv_path = os.path.join(output_dir, 'final_detailed_report.csv')
    
    if not os.path.exists(csv_path):
        return jsonify({'error': 'No report data found'}), 404
    
    try:
        df = pd.read_csv(csv_path)
    except Exception as e:
        return jsonify({'error': f'Failed to read CSV: {str(e)}'}), 500
    
    if df.empty:
        return jsonify({'error': 'Report is empty'}), 404
    
    df['Total Amount'] = pd.to_numeric(df['Total Amount'], errors='coerce').fillna(0)
    
    df['Parsed Date'] = pd.to_datetime(df['Date'], format='mixed', errors='coerce')
    
    summary = {
        'total_invoices': int(len(df)),
        'total_spend': round(float(df['Total Amount'].sum()), 2),
        'avg_invoice': round(float(df['Total Amount'].mean()), 2),
        'max_invoice': round(float(df['Total Amount'].max()), 2),
        'min_invoice': round(float(df['Total Amount'].min()), 2),
        'unique_sellers': int(df['Seller Name'].nunique()),
        'unique_clients': int(df['Client Name'].nunique()),
    }
    
    cat_counts = df['Category'].value_counts().to_dict()
    cat_spend = df.groupby('Category')['Total Amount'].sum().round(2).to_dict()
    cat_avg = df.groupby('Category')['Total Amount'].mean().round(2).to_dict()
    
    monthly_data = {}
    valid_dates = df.dropna(subset=['Parsed Date'])
    if not valid_dates.empty:
        valid_dates = valid_dates.copy()
        valid_dates['Month'] = valid_dates['Parsed Date'].dt.to_period('M').astype(str)
        monthly_spend = valid_dates.groupby('Month')['Total Amount'].sum().round(2)
        monthly_count = valid_dates.groupby('Month').size()
        monthly_data = {
            'labels': monthly_spend.index.tolist(),
            'spend': monthly_spend.values.tolist(),
            'count': monthly_count.values.tolist()
        }
    
    top_sellers = df.groupby('Seller Name')['Total Amount'].sum().round(2).sort_values(ascending=False).head(10)
    top_sellers_data = {
        'labels': top_sellers.index.tolist(),
        'values': top_sellers.values.tolist()
    }
    
    top_clients = df.groupby('Client Name')['Total Amount'].sum().round(2).sort_values(ascending=False).head(10)
    top_clients_data = {
        'labels': top_clients.index.tolist(),
        'values': top_clients.values.tolist()
    }
    
    missing = {
        'missing_seller_tax': int(df['Seller Tax ID'].isna().sum() + (df['Seller Tax ID'] == '').sum()),
        'missing_client_tax': int(df['Client Tax ID'].isna().sum() + (df['Client Tax ID'] == '').sum()),
        'missing_iban': int(df['Seller IBAN'].isna().sum() + (df['Seller IBAN'] == '').sum()),
        'total': int(len(df))
    }
    
    iban_countries = {}
    if 'Seller IBAN' in df.columns:
        ibans = df['Seller IBAN'].dropna()
        for iban in ibans:
            iban_str = str(iban).strip()
            if len(iban_str) >= 2:
                country = iban_str[:2].upper()
                iban_countries[country] = iban_countries.get(country, 0) + 1
    
    outliers = []
    if len(df) > 2:
        mean_amt = df['Total Amount'].mean()
        std_amt = df['Total Amount'].std()
        outlier_df = df[abs(df['Total Amount'] - mean_amt) > 2 * std_amt]
        for _, row in outlier_df.iterrows():
            outliers.append({
                'invoice_no': str(row.get('Invoice No', '')),
                'amount': round(float(row['Total Amount']), 2),
                'seller': str(row.get('Seller Name', '')),
                'category': str(row.get('Category', ''))
            })
    
    amount_distribution = {}
    if not df.empty:
        amounts = df['Total Amount']
        bins = [0, 100, 500, 1000, 5000, 10000, 50000, float('inf')]
        bin_labels = ['0-100', '100-500', '500-1K', '1K-5K', '5K-10K', '10K-50K', '50K+']
        hist = pd.cut(amounts, bins=bins, labels=bin_labels, right=False).value_counts().sort_index()
        amount_distribution = {
            'labels': hist.index.tolist(),
            'values': hist.values.tolist()
        }
    
    cat_trend = {}
    if not valid_dates.empty:
        vd = valid_dates.copy()
        pivot = vd.groupby(['Month', 'Category'])['Total Amount'].sum().round(2).unstack(fill_value=0)
        cat_trend = {
            'labels': pivot.index.tolist(),
            'datasets': {col: pivot[col].values.tolist() for col in pivot.columns}
        }
    
    raw_data = []
    for _, row in df.iterrows():
        raw_data.append({
            'invoice_no': str(row.get('Invoice No', '')),
            'date': str(row.get('Date', '')),
            'seller_name': str(row.get('Seller Name', '')),
            'client_name': str(row.get('Client Name', '')),
            'seller_tax_id': str(row.get('Seller Tax ID', '')),
            'seller_iban': str(row.get('Seller IBAN', '')),
            'client_tax_id': str(row.get('Client Tax ID', '')),
            'total_amount': round(float(row.get('Total Amount', 0)), 2),
            'category': str(row.get('Category', ''))
        })
    
    return jsonify({
        'summary': summary,
        'category_distribution': cat_counts,
        'category_spend': cat_spend,
        'category_avg': cat_avg,
        'monthly_trends': monthly_data,
        'top_sellers': top_sellers_data,
        'top_clients': top_clients_data,
        'missing_data': missing,
        'iban_countries': iban_countries,
        'outliers': outliers,
        'amount_distribution': amount_distribution,
        'category_trend': cat_trend,
        'raw_data': raw_data
    })

@app.route('/api/upload-csv', methods=['POST'])
def api_upload_csv():
    """Accept a CSV upload for manual analysis and return analytics."""
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400
    
    if not file.filename.endswith('.csv'):
        return jsonify({'error': 'Only CSV files are accepted'}), 400
    
    filename = secure_filename(file.filename)
    temp_path = os.path.join(app.config['OUTPUT_FOLDER'], f'temp_analysis_{filename}')
    file.save(temp_path)
    
    temp_id = f'temp_{filename.replace(".csv", "")}'
    
    target_path = os.path.join(app.config['OUTPUT_FOLDER'], f'report_{temp_id}.csv')
    if os.path.exists(target_path):
        os.remove(target_path)
    os.rename(temp_path, target_path)
    
    return jsonify({'batch_id': temp_id, 'message': 'CSV uploaded successfully'})


if __name__ == '__main__':
    print("Starting Smart Invoice Server...")
    print(f"Upload Folder: {UPLOAD_FOLDER}")
    print(f"Output Folder: {OUTPUT_FOLDER}")
    app.run(debug=True, port=5000)
