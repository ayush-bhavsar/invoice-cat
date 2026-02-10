import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.naive_bayes import MultinomialNB
from sklearn.pipeline import make_pipeline

def train_model():

    try:
        data = pd.read_csv('training_data/categories.csv')
    except FileNotFoundError:
        print("Error: Could not find training_data/categories.csv")
        return None

    X_train = data['description']
    y_train = data['category']

    model = make_pipeline(TfidfVectorizer(), MultinomialNB())

    model.fit(X_train, y_train)
    
    return model

_trained_model = train_model()

def predict_category(product_name):
    
    if _trained_model:
        prediction = _trained_model.predict([product_name])
        return prediction[0]
    return "Unknown"