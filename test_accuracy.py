import sys
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

import pandas as pd
import numpy as np
import os
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'

import tensorflow as tf
tf.get_logger().setLevel('ERROR')

import joblib
from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import SGDClassifier
from sklearn.metrics import classification_report, accuracy_score


def print_header(title):
    width = 60
    print("\n" + "=" * width)
    print(f"  {title}")
    print("=" * width)


def print_section(title):
    print(f"\n{'_' * 50}")
    print(f"  {title}")
    print(f"{'_' * 50}")


def main():
    print_header("INVOICE-IQ - MODEL EVALUATION REPORT")
    print("  Evaluating classification accuracy across 10 categories")


    print_section("[Step 1] Loading Dataset")
    data = pd.read_csv('training_data/categories.csv')
    total_samples = len(data)
    categories = data['category'].unique()
    print(f"  Total samples      : {total_samples}")
    print(f"  Categories         : {len(categories)}")
    print(f"  Categories list    : {', '.join(sorted(categories))}")

    print(f"\n  Samples per category:")
    for cat, count in data['category'].value_counts().sort_index().items():
        bar = "#" * (count // 15)
        print(f"    {cat:<18} : {count:>4}  {bar}")


    print_section("[Step 2] Train/Test Split (80/20)")
    X_raw = data['description']
    y_raw = data['category']
    X_train, X_test, y_train, y_test = train_test_split(
        X_raw, y_raw, test_size=0.2, random_state=42
    )
    print(f"  Training samples   : {len(X_train)}")
    print(f"  Test samples       : {len(X_test)}")
    print(f"  Split ratio        : 80% train / 20% test")
    print(f"  Random seed        : 42 (reproducible)")

    print_section("[Step 3] Baseline Model (SGD Linear Classifier)")
    print("  Training SGD classifier with TF-IDF features...")

    baseline_vec = TfidfVectorizer(ngram_range=(1, 2))
    X_train_baseline = baseline_vec.fit_transform(X_train)
    X_test_baseline = baseline_vec.transform(X_test)

    sgd = SGDClassifier(random_state=42)
    sgd.fit(X_train_baseline, y_train)
    y_pred_sgd = sgd.predict(X_test_baseline)
    sgd_accuracy = accuracy_score(y_test, y_pred_sgd)

    print(f"\n  SGD Baseline Accuracy: {sgd_accuracy:.2%}")
    print(f"\n  Per-Category Report:")
    print(classification_report(y_test, y_pred_sgd, digits=2))


    print_section("[Step 4] Neural Network (TensorFlow/Keras)")
    print("  Loading trained model and preprocessors...")

    model = tf.keras.models.load_model('nn_model.keras')
    vectorizer = joblib.load('vectorizer.pkl')
    label_encoder = joblib.load('label_encoder.pkl')

    print(f"\n  Model Architecture:")
    print(f"    Input  -> Dense(256, ReLU) -> Dropout(0.5)")
    print(f"           -> Dense(128, ReLU) -> Dropout(0.5)")
    print(f"           -> Dense({len(label_encoder.classes_)}, Softmax)")
    print(f"    Loss     : sparse_categorical_crossentropy")
    print(f"    Optimizer: Adam")
    print(f"    TF-IDF features: {vectorizer.max_features}")


    X_test_nn = vectorizer.transform(X_test).toarray()
    predictions = model.predict(X_test_nn, verbose=0)
    predicted_indices = np.argmax(predictions, axis=1)
    y_pred_nn = label_encoder.inverse_transform(predicted_indices)
    nn_accuracy = accuracy_score(y_test, y_pred_nn)

    print(f"\n  Neural Network Accuracy: {nn_accuracy:.2%}")
    print(f"\n  Per-Category Report:")
    print(classification_report(y_test, y_pred_nn, digits=2))


    print_section("[Step 5] Prediction Confidence Analysis")
    max_probs = np.max(predictions, axis=1)

    print(f"  Average confidence : {max_probs.mean():.2%}")
    print(f"  Median confidence  : {np.median(max_probs):.2%}")
    print(f"  Min confidence     : {max_probs.min():.2%}")
    print(f"  Max confidence     : {max_probs.max():.2%}")

    thresholds = [99, 95, 90, 80, 70, 50]
    print(f"\n  Confidence Distribution:")
    for t in thresholds:
        count = (max_probs > t / 100).sum()
        pct = count / len(max_probs)
        bar = "#" * int(pct * 30)
        print(f"    > {t}% confidence : {count:>4}/{len(max_probs)}  ({pct:.1%})  {bar}")


    low_conf_mask = max_probs < 0.7
    if low_conf_mask.sum() > 0:
        print(f"\n  [!] Low-confidence predictions (<70%):")
        low_indices = np.where(low_conf_mask)[0]
        for idx in low_indices[:10]:
            actual = y_test.iloc[idx]
            predicted = y_pred_nn[idx]
            conf = max_probs[idx]
            status = "[OK]" if actual == predicted else "[X] "
            print(f"    {status} \"{X_test.iloc[idx]}\" -> {predicted} ({conf:.1%}) [actual: {actual}]")
    else:
        print(f"\n  [OK] All predictions have confidence >= 70%!")

    print_section("[Step 6] Model Comparison")
    improvement = nn_accuracy - sgd_accuracy
    print(f"""
  +---------------------------------------------+
  |  Model                     |   Accuracy     |
  |--------------------------------------------+
  |  SGD Linear (Baseline)     |   {sgd_accuracy:.2%}        |
  |  Neural Network (Primary)  |   {nn_accuracy:.2%}        |
  |--------------------------------------------+
  |  NN Improvement            |   +{improvement:.2%}       |
  +---------------------------------------------+""")

    report_dict = classification_report(y_test, y_pred_nn, output_dict=True)
    
    print_header("FINAL RESULTS SUMMARY")
    print(f"""
  [*] Neural Network Accuracy     :  {nn_accuracy:.2%}
  [*] Weighted Precision           :  {report_dict['weighted avg']['precision']:.2%}
  [*] Weighted Recall              :  {report_dict['weighted avg']['recall']:.2%}
  [*] Weighted F1-Score            :  {report_dict['weighted avg']['f1-score']:.2%}
  [*] Average Confidence           :  {max_probs.mean():.2%}
  [*] Predictions > 90% Confidence :  {(max_probs > 0.9).sum()}/{len(max_probs)} ({(max_probs > 0.9).mean():.1%})
  [*] Dataset Size                 :  {total_samples} samples
  [*] Categories                   :  {len(categories)}
  [*] NN vs Baseline Improvement   :  +{improvement:.2%}

  [+] Hybrid Pipeline: When NN confidence is low,
      Gemini LLM fallback provides additional accuracy.
""")
    print("=" * 60)
    print("  Report complete. Ready for hackathon presentation!")
    print("=" * 60)


if __name__ == '__main__':
    main()
