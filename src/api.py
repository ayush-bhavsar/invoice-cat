from flask import Flask, request, jsonify
from flask_cors import CORS
import cv2
import numpy as np
import os
import pickle
import traceback

# Import our custom modules
from preprocessing import preprocess_image
from ocr_engine import extract_text
from extractors import extract_date, extract_amount, clean_text_for_ml

app = Flask(__name__)
# Enable CORS so our future Frontend (HTML/JS) can talk to this Backend
CORS(app)

# Load Model Global Variable
MODEL = None

def load_model():
    global MODEL
    model_path = os.path.join("models", "classifier.pkl")
    if os.path.exists(model_path):
        with open(model_path, "rb") as f:
            MODEL = pickle.load(f)
        print(f"[INFO] Model loaded from {model_path}")
    else:
        print("[WARNING] Model not found. Predictions will be 'Unknown'.")

@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({"status": "running", "model_loaded": MODEL is not None})

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({"error": "No file part"}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400

    try:
        # 1. Convert uploaded file to OpenCV image
        file_bytes = np.frombuffer(file.read(), np.uint8)
        image = cv2.imdecode(file_bytes, cv2.IMREAD_COLOR)

        if image is None:
             return jsonify({"error": "Invalid image format"}), 400

        # 2. Pipeline: Preprocessing -> OCR -> Extraction
        processed_image = preprocess_image(image)
        raw_text = extract_text(processed_image)

        if "Error" in raw_text:
             return jsonify({"error": raw_text}), 500

        invoice_date = extract_date(raw_text)
        total_amount = extract_amount(raw_text)

        # 3. ML Classification
        category = "Unknown"
        if MODEL:
            clean_text = clean_text_for_ml(raw_text)
            prediction = MODEL.predict([clean_text])
            category = prediction[0]

        # 4. Return JSON
        result = {
            "filename": file.filename,
            "category": category,
            "date": invoice_date,
            "total_amount": total_amount,
            # "raw_text": raw_text[:500] # Optional: Send preview of text
        }
        return jsonify(result)

    except Exception as e:
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    load_model()
    # Debug mode is fine for development
    # Debug mode is fine for development, but reloader causes issues in some envs
    app.run(debug=True, port=5000, use_reloader=False)
