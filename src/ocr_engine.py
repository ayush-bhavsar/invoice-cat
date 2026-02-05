import pytesseract
from PIL import Image
import cv2
import os

# NOTE: You must have Tesseract-OCR installed on your system.
# If 'tesseract' is not in your PATH, uncomment and set the line below:
# pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

def extract_text(image_input):
    """
    Extracts text from a given image (numpy array or file path) using Tesseract OCR.
    """
    try:
        # If input is a string path, load it using cv2 to ensure it exists
        if isinstance(image_input, str):
            if not os.path.exists(image_input):
                return f"Error: File {image_input} not found."
            # We can pass the path directly to pytesseract, or load it
            # Pytesseract handles paths well, but passing the image object gives more control
            text = pytesseract.image_to_string(Image.open(image_input))
        else:
            # Assume it's a numpy array (OpenCV image)
            # Pytesseract expects RGB, OpenCV is BGR
            rgb_image = cv2.cvtColor(image_input, cv2.COLOR_BGR2RGB)
            text = pytesseract.image_to_string(rgb_image)
    except pytesseract.TesseractNotFoundError:
        return "Error: Tesseract is not installed or not in PATH. Please install it."
    except Exception as e:
        return f"Error during OCR: {str(e)}"
        
    return text
