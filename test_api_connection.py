import requests
import os
import cv2
import numpy as np

def create_test_image():
    # Create a dummy image
    img = np.ones((600, 500, 3), dtype=np.uint8) * 255
    cv2.putText(img, "INVOICE", (180, 50), cv2.FONT_HERSHEY_SIMPLEX, 1.2, (0, 0, 0), 2)
    cv2.putText(img, "Date: 12/01/2024", (50, 150), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 0), 1)
    cv2.putText(img, "Total: $500.00", (250, 400), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 0), 2)
    cv2.putText(img, "aws web services", (50, 250), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 0), 2)
    
    path = "temp_test_invoice.png"
    cv2.imwrite(path, img)
    return path

def test_api():
    url = "http://127.0.0.1:5000/upload"
    image_path = create_test_image()
    
    try:
        with open(image_path, 'rb') as f:
            files = {'file': f}
            response = requests.post(url, files=files)
        
        print(f"Status Code: {response.status_code}")
        print(f"Status Code: {response.status_code}")
        if response.status_code == 200:
            print("Response JSON:", response.json())
            print("[PASS] API Test Passed: Backend is working!")
        else:
            print("[FAIL] API Test Failed:", response.text)
            
    except requests.exceptions.ConnectionError:
        print("[FAIL] Connection Error: Is api.py running? (Run 'python src/api.py' in a separate terminal)")
    finally:
        if os.path.exists(image_path):
            os.remove(image_path)

if __name__ == "__main__":
    test_api()
