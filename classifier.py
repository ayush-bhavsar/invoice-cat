import os
import joblib
import tensorflow as tf
import numpy as np

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

def predict_category(product_name):
    """
    Predict the category of a line item using the trained Neural Network.
    Returns the predicted category as a string.
    """
    if _model is None or _vectorizer is None or _label_encoder is None:
        return "Unknown"
        
    try:
        # Preprocess input text via the loaded TF-IDF vectorizer
        X = _vectorizer.transform([product_name]).toarray()
        
        # Predict class probabilities
        predictions = _model.predict(X, verbose=0)
        
        # Get highest probability class index
        predicted_index = np.argmax(predictions, axis=1)[0]
        
        # Inverse transform to get original categorical label
        category = _label_encoder.inverse_transform([predicted_index])[0]
        return category
        
    except Exception as e:
        print(f"Prediction error for '{product_name}': {e}")
        return "Unknown"