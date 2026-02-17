from classifier import predict_category, _trained_model
import pandas as pd

# Test strings from the invoices we saw
test_cases = [
    "6'x3' Marble Dining Table Hakik",
    "Wine Glasses Set Of 4",
    "Dell Desktop Computer Tower",
    "Beautiful Blue Dolphin Wine Bottle Stopper",
    "Used t shirt Blue",
    "Total Amount",
    "Tax ID"
]

print(f"Model Classes: {_trained_model.classes_}")

print("\n--- DETAILED DIAGNOSIS ---")
for text in test_cases:
    # 1. Prediction
    pred = predict_category(text)
    
    # 2. Confidence / Decision Function
    # SGDClassifier with 'hinge' doesn't give probabilities by default unless calibrated, 
    # but we can look at decision_function values.
    # The pipeline step 'sgdclassifier' is the second step.
    sgd = _trained_model.steps[1][1]
    vect = _trained_model.steps[0][1]
    
    # Vectorize
    vec = vect.transform([text])
    
    # Get scores
    scores = sgd.decision_function(vec)
    
    print(f"\nText: '{text}'")
    print(f"  -> Prediction: {pred}")
    
    # Show active features (words that exist in vocab)
    feature_names = vect.get_feature_names_out()
    active_indices = vec.indices
    active_words = [feature_names[i] for i in active_indices]
    print(f"  -> Recognized Words: {active_words}")
    
    # Show scores for top categories
    # classes_ matches the columns of scores (if binary) or scores is (n_samples, n_classes)
    if len(sgd.classes_) > 2:
        class_scores = zip(sgd.classes_, scores[0])
        sorted_scores = sorted(class_scores, key=lambda x: x[1], reverse=True)
        print(f"  -> Scores: {sorted_scores[:3]}")
