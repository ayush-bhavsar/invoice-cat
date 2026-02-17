import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import SGDClassifier
from sklearn.pipeline import make_pipeline

def train_model():

    try:
        data = pd.read_csv('training_data/categories.csv')
    except FileNotFoundError:
        print("Error: Could not find training_data/categories.csv")
        return None

    X_train = data['description']
    y_train = data['category']

    # IMPROVEMENT: Use N-grams (1-2 words), remove stopwords, and use Linear SVM
    model = make_pipeline(
        TfidfVectorizer(ngram_range=(1, 2), stop_words='english'),
        SGDClassifier(loss='hinge', alpha=1e-3, random_state=42)
    )

    model.fit(X_train, y_train)
    
    return model
_trained_model = train_model()

def predict_category(product_name):
    
    if _trained_model:
        prediction = _trained_model.predict([product_name])
        return prediction[0]
    return "Unknown"