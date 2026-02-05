import os
import sys

# Add src to python path so we can import modules
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from src.preprocessing import load_image, preprocess_image, save_image
from src.ocr_engine import extract_text

def test_pipeline(image_path):
    print(f"--- Testing Invoice: {image_path} ---")
    
    # 1. Load
    try:
        img = load_image(image_path)
    except Exception as e:
        print(e)
        return

    # 2. Extract Text from Original (for comparison)
    print("\n[INFO] Extracting text from original image (Basic OCR)...")
    raw_text = extract_text(image_path)
    print(f"--- Raw Text Preview (First 100 chars) ---\n{raw_text[:100]}...\n")

    # 3. Preprocess
    print("\n[INFO] Preprocessing image (Grayscale + Thresholding)...")
    processed_img = preprocess_image(img)
    
    # Save processed image for debugging
    debug_path = "debug_processed.jpg"
    save_image(processed_img, debug_path)
    print(f"[INFO] Saved processed image to {debug_path}")

    # 4. Extract Text from Processed
    print("\n[INFO] Extracting text from processed image (Better OCR)...")
    clean_text = extract_text(processed_img)
    print(f"--- Clean Text Preview (First 100 chars) ---\n{clean_text[:100]}...\n")
    
    return clean_text

if __name__ == "__main__":
    # Look for any image in data/raw
    raw_dir = os.path.join("data", "raw")
    files = [f for f in os.listdir(raw_dir) if f.lower().endswith(('.png', '.jpg', '.jpeg'))]
    
    if not files:
        print(f"No images found in {raw_dir}. Please put a sample invoice image there to test.")
    else:
        # Test the first file found
        test_file = os.path.join(raw_dir, files[0])
        test_pipeline(test_file)
