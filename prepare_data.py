import os
import cv2
import numpy as np
from sklearn.model_selection import train_test_split

# Define paths
dataset_path = 'dataset'
processed_path = 'processed_data'
os.makedirs(processed_path, exist_ok=True)

# Function to preprocess image
def preprocess_image(image_path):
    image = cv2.imread(image_path)
    if image is None:
        return None
    # Resize to 224x224
    image = cv2.resize(image, (224, 224))
    # Optional: enhance contrast or something, but keep RGB
    return image

# Collect all image paths and labels
image_paths = []
labels = []
categories = []

for root, dirs, files in os.walk(dataset_path):
    for file in files:
        if file.endswith(('.jpg', '.png', '.jpeg')):
            image_path = os.path.join(root, file)
            category = os.path.basename(root)
            if category not in categories:
                categories.append(category)
            label = categories.index(category)
            image_paths.append(image_path)
            labels.append(label)

# Save labels mapping
with open(os.path.join(processed_path, 'categories.txt'), 'w') as f:
    for i, cat in enumerate(categories):
        f.write(f"{i}: {cat}\n")

# Split into train/val/test
X_train, X_temp, y_train, y_temp = train_test_split(image_paths, labels, test_size=0.3, random_state=42)
X_val, X_test, y_val, y_test = train_test_split(X_temp, y_temp, test_size=0.5, random_state=42)

# Function to process and save
def process_and_save(file_list, labels_list, split_name):
    for file_path, label in zip(file_list, labels_list):
        category = categories[label]
        dest_dir = os.path.join(processed_path, split_name, category)
        os.makedirs(dest_dir, exist_ok=True)
        processed_image = preprocess_image(file_path)
        if processed_image is not None:
            filename = os.path.basename(file_path)
            save_path = os.path.join(dest_dir, filename)
            cv2.imwrite(save_path, processed_image)

# Process and save
process_and_save(X_train, y_train, 'train')
process_and_save(X_val, y_val, 'val')
process_and_save(X_test, y_test, 'test')

print("Data preparation complete.")