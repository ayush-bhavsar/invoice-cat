import cv2
import numpy as np
import os

def create_dummy_invoice():
    # Create a white image
    img = np.ones((600, 500), dtype=np.uint8) * 255
    
    # Define font and text
    font = cv2.FONT_HERSHEY_SIMPLEX
    
    # Add text simulating an invoice
    cv2.putText(img, "INVOICE", (180, 50), font, 1.2, (0, 0, 0), 2)
    cv2.putText(img, "Company Name: Tech Solutions", (50, 100), font, 0.7, (0, 0, 0), 1)
    cv2.putText(img, "Date: 12/01/2024", (50, 150), font, 0.7, (0, 0, 0), 1)
    cv2.putText(img, "Invoice #: INV-2024-001", (50, 190), font, 0.7, (0, 0, 0), 1)
    
    cv2.putText(img, "Item", (50, 250), font, 0.8, (0, 0, 0), 2)
    cv2.putText(img, "Price", (350, 250), font, 0.8, (0, 0, 0), 2)
    
    cv2.putText(img, "Web Development", (50, 290), font, 0.6, (0, 0, 0), 1)
    cv2.putText(img, "$500.00", (350, 290), font, 0.6, (0, 0, 0), 1)
    
    cv2.putText(img, "Hosting", (50, 320), font, 0.6, (0, 0, 0), 1)
    cv2.putText(img, "$50.00", (350, 320), font, 0.6, (0, 0, 0), 1)
    
    cv2.putText(img, "TOTAL: $550.00", (250, 400), font, 1, (0, 0, 0), 2)
    
    # Ensure directory exists
    output_dir = os.path.join("data", "raw")
    os.makedirs(output_dir, exist_ok=True)
    
    output_path = os.path.join(output_dir, "test_invoice_synthetic.png")
    cv2.imwrite(output_path, img)
    print(f"Created dummy invoice at: {output_path}")

if __name__ == "__main__":
    create_dummy_invoice()
