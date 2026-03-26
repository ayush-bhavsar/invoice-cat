import pandas as pd
import numpy as np
import tensorflow as tf
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense, Dropout
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.preprocessing import LabelEncoder
import joblib

def main():
    print("Loading data...")
    try:
        data = pd.read_csv('training_data/categories.csv')
    except FileNotFoundError:
        print("Error: Could not find training_data/categories.csv")
        return

    if 'item_text' in data.columns:
        X_raw = data['item_text']
    elif 'description' in data.columns:
        X_raw = data['description']
    else:
        print("Error: Could not find feature columns in CSV.")
        return
        
    y_raw = data['category']

    print("Applying TF-IDF vectorization...")
    vectorizer = TfidfVectorizer(max_features=5000, stop_words='english', ngram_range=(1, 2))
    X = vectorizer.fit_transform(X_raw).toarray()

    print("Encoding categories...")
    label_encoder = LabelEncoder()
    y = label_encoder.fit_transform(y_raw)
    
    num_classes = len(label_encoder.classes_)

    print("Building Feedforward Neural Network...")
    model = Sequential([
        Dense(256, activation='relu', input_shape=(X.shape[1],)),
        Dropout(0.5),
        Dense(128, activation='relu'),
        Dropout(0.5),
        Dense(num_classes, activation='softmax')
    ])

    model.compile(optimizer='adam', 
                  loss='sparse_categorical_crossentropy', 
                  metrics=['accuracy'])

    print("Training Model...")
    model.fit(X, y, epochs=15, batch_size=32, validation_split=0.2)

    print("Saving models to disk...")
    model.save('nn_model.keras')
    joblib.dump(vectorizer, 'vectorizer.pkl')
    joblib.dump(label_encoder, 'label_encoder.pkl')
    
    print("Done! Neural Network trained and artifacts saved.")

if __name__ == '__main__':
    main()
