import os
import joblib
import tensorflow as tf
import numpy as np

from dotenv import load_dotenv
import google.generativeai as genai

# Load environment variables (API Keys)
load_dotenv()

# Configure Gemini
GEMINI_API_KEY = os.environ.get("LLM_API_KEY")
if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)

# Paths to the saved model and preprocessors
MODEL_PATH = 'nn_model.keras'
VECTORIZER_PATH = 'vectorizer.pkl'
ENCODER_PATH = 'label_encoder.pkl'

_model = None
_vectorizer = None
_label_encoder = None

def load_resources():
    global _model, _vectorizer, _label_encoder
    try:
        if os.path.exists(MODEL_PATH) and os.path.exists(VECTORIZER_PATH) and os.path.exists(ENCODER_PATH):
            _model = tf.keras.models.load_model(MODEL_PATH)
            _vectorizer = joblib.load(VECTORIZER_PATH)
            _label_encoder = joblib.load(ENCODER_PATH)
        else:
            print("Warning: NN model or preprocessors missing. Please run train_nn.py first.")
    except Exception as e:
        print(f"Error loading model resources: {e}")

# Load at startup
load_resources()

def predict_gemini_batch(product_names):
    if not GEMINI_API_KEY:
        print("Error: LLM_API_KEY not found in environment.")
        return None
        
    if not product_names:
        return []
        
    try:
        model = genai.GenerativeModel('gemini-2.5-flash') # Using fast model for categorization
        
        # We need to give it the list of exact categories you expect
        valid_categories = [
            "Hardware", "Books & Media", "Furniture", "Services", "Electronics", 
            "Clothing", "Kitchen", "Office Supplies", "Beverages", "Other"
        ]
        
        items_text = "\n".join([f"{i+1}. {name}" for i, name in enumerate(product_names)])
        
        prompt = f"""
        You are an expert invoice processing AI. 
        Categorize the following list of line items extracted from an invoice into exactly ONE of the following valid categories:
        {valid_categories}
        
        Line items:
        {items_text}
        
        Rules:
        - Output ONLY a valid JSON array of strings representing the category for each line item in the exact same order.
        - Output NOTHING except the JSON array. Do not use markdown blocks like ```json.
        - Valid JSON format example: ["Office Supplies", "Hardware", "Other"]
        - If an item does not neatly fit, use "Other".
        """
        
        response = model.generate_content(prompt)
        text = response.text.strip()
        
        if text.startswith("```json"):
            text = text[7:]
        if text.startswith("```"):
            text = text[3:]
        if text.endswith("```"):
            text = text[:-3]
        text = text.strip()
        
        import json
        try:
            categories = json.loads(text)
        except json.JSONDecodeError:
            print(f"Failed to parse Gemini JSON output: {text}")
            return None
            
        if len(categories) != len(product_names):
            print(f"Warning: Gemini returned {len(categories)} categories for {len(product_names)} items.")
            while len(categories) < len(product_names):
                categories.append("Unknown")
            categories = categories[:len(product_names)]
            
        final_categories = []
        for cat in categories:
            if cat in valid_categories:
                final_categories.append(cat)
            else:
                # Fallback check
                found = False
                for valid in valid_categories:
                    if valid.lower() in cat.lower():
                        final_categories.append(valid)
                        found = True
                        break
                if not found:
                    final_categories.append("Other")
                    
        return final_categories
            
    except Exception as e:
        print(f"Gemini API Error during batch processing: {e}")
        return None

def predict_categories_batch(product_names, method='local_nn'):
    """
    Predict the categories of a list of line items using either the trained local NN or Gemini LLM.
    Returns a list of predicted category strings.
    """
    if not product_names:
        return []
        
    if method == 'gemini':
        print(f"Using Gemini to categorize {len(product_names)} items in batch.")
        result = predict_gemini_batch(product_names)
        if result is not None:
            return result
        print("Gemini failed or rate-limited. Seamlessly falling back to local_nn...")

    # Fallback to local NN batch (much faster)
    if _model is None or _vectorizer is None or _label_encoder is None:
        return ["Unknown"] * len(product_names)
        
    try:
        X = _vectorizer.transform(product_names).toarray()
        predictions = _model.predict(X, verbose=0)
        predicted_indices = np.argmax(predictions, axis=1)
        categories = _label_encoder.inverse_transform(predicted_indices)
        return list(categories)
    except Exception as e:
        print(f"Batch prediction error: {e}")
        return ["Unknown"] * len(product_names)

def predict_category(product_name, method='local_nn'):
    """
    Predict the category of a line item using either the trained local NN or Gemini LLM.
    Returns the predicted category as a string.
    """
    return predict_categories_batch([product_name], method)[0]