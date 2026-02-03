import os
import tensorflow as tf
from tensorflow.keras.preprocessing.image import ImageDataGenerator
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Conv2D, MaxPooling2D, Flatten, Dense, Dropout
import numpy as np

# Paths
processed_path = 'processed_data'

# Load categories
with open(os.path.join(processed_path, 'categories.txt'), 'r') as f:
    categories = [line.strip().split(': ')[1] for line in f.readlines()]
num_classes = len(categories)

# Data generators
train_datagen = ImageDataGenerator(rescale=1./255, rotation_range=20, width_shift_range=0.2, height_shift_range=0.2, horizontal_flip=True)
val_datagen = ImageDataGenerator(rescale=1./255)
test_datagen = ImageDataGenerator(rescale=1./255)

train_generator = train_datagen.flow_from_directory(
    os.path.join(processed_path, 'train'),
    target_size=(224, 224),
    batch_size=32,
    class_mode='categorical',
    classes=categories
)

val_generator = val_datagen.flow_from_directory(
    os.path.join(processed_path, 'val'),
    target_size=(224, 224),
    batch_size=32,
    class_mode='categorical',
    classes=categories
)

test_generator = test_datagen.flow_from_directory(
    os.path.join(processed_path, 'test'),
    target_size=(224, 224),
    batch_size=32,
    class_mode='categorical',
    classes=categories
)

# Build model
model = Sequential([
    Conv2D(32, (3, 3), activation='relu', input_shape=(224, 224, 3)),
    MaxPooling2D((2, 2)),
    Conv2D(64, (3, 3), activation='relu'),
    MaxPooling2D((2, 2)),
    Conv2D(128, (3, 3), activation='relu'),
    MaxPooling2D((2, 2)),
    Flatten(),
    Dense(128, activation='relu'),
    Dropout(0.5),
    Dense(num_classes, activation='softmax')
])

model.compile(optimizer='adam', loss='categorical_crossentropy', metrics=['accuracy'])

# Train
history = model.fit(
    train_generator,
    epochs=10,
    validation_data=val_generator
)

# Evaluate
test_loss, test_acc = model.evaluate(test_generator)
print(f'Test accuracy: {test_acc}')

# Save model
model.save('invoice_categorizer.h5')

print("Model training complete.")