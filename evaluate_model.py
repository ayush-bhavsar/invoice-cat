import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import SGDClassifier
from sklearn.metrics import classification_report

df = pd.read_csv('training_data/categories.csv')
X = df['description']
y = df['category']

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

vectorizer = TfidfVectorizer(ngram_range=(1, 2))
X_train_vec = vectorizer.fit_transform(X_train)
clf = SGDClassifier()
clf.fit(X_train_vec, y_train)

X_test_vec = vectorizer.transform(X_test)
y_pred = clf.predict(X_test_vec)


print(classification_report(y_test, y_pred))