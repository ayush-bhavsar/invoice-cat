import requests
import os

# Create a dummy image file
with open('test_image.jpg', 'wb') as f:
    f.write(b'\x00' * 100) # Dummy content, OCR will fail but request should reach server

url = 'http://127.0.0.1:5000/upload?save=true&batch_id=test12345'
files = {'file': open('test_image.jpg', 'rb')}

try:
    print(f"Sending request to {url}...")
    response = requests.post(url, files=files)
    print(f"Status Code: {response.status_code}")
    print(f"Response: {response.text}")
except Exception as e:
    print(f"Connection Failed: {e}")
