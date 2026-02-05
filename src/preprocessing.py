import cv2
import numpy as np

def load_image(image_path):
    """
    Loads an image from the specified path.
    """
    image = cv2.imread(image_path)
    if image is None:
        raise ValueError(f"Could not load image at {image_path}")
    return image

def preprocess_image(image):
    """
    Applies preprocessing steps to improve OCR accuracy:
    1. Grayscale conversion
    2. Thresholding (Binarization) to remove shadows/noise
    """
    # Convert to grayscale
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    
    # Apply binary thresholding (converting to pure black and white)
    # This helps Tesseract read text clearly against the background
    _, binary_image = cv2.threshold(gray, 150, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    
    return binary_image

def save_image(image, output_path):
    """
    Saves the processed image to disk (useful for debugging).
    """
    cv2.imwrite(output_path, image)
