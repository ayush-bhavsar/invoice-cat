import pandas as pd
import pickle
import os
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.naive_bayes import MultinomialNB
from sklearn.pipeline import make_pipeline
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score

def train_model():
    print("--- Starting Model Training ---")
    
    # 1. Load Data
    data_path = os.path.join("data", "labeled_data.csv")
    if not os.path.exists(data_path):
        print(f"Error: Data file not found at {data_path}")
        return

    df = pd.read_csv(data_path)
    print(f"Loaded dataset with {len(df)} rows.")

    # 2. Prepare Feature (X) and Target (y)
    X = df['text']
    y = df['category']

    # 3. Create a Pipeline
    # CountVectorizer converts text to a matrix of token counts
    # MultinomialNB is a standard classifier for text data
    model = make_pipeline(CountVectorizer(), MultinomialNB())

    # 4. Train the Model (Fit)
    # Since dataset is tiny, we just train on all of it for this demo. 
    # In real life, use train_test_split.
    model.fit(X, y)
    print("Model trained successfully.")

    # 5. Test Prediction (Self check)
    test_text = ["google cloud platform bill"]
    prediction = model.predict(test_text)[0]
    print(f"Test Prediction for '{test_text[0]}': {prediction}")

    # 6. Save the Model
    model_dir = "models"
    os.makedirs(model_dir, exist_ok=True)
    model_path = os.path.join(model_dir, "classifier.pkl")
    
    with open(model_path, 'wb') as f:
        pickle.dump(model, f)
    
    print(f"Model saved to {model_path}")

if __name__ == "__main__":
    train_model()
