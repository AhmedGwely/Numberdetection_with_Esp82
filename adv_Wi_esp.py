import cv2
import pytesseract
import re
import pandas as pd
import os
import time
import requests
from datetime import datetime
import numpy as np

# Tesseract executable path
pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

# ESP8266 IP (update if needed)
esp_ip = "http://192.168.1.12/trigger"

# Output paths
excel_file = "numbers.xlsx"
image_dir = "captured_images"
os.makedirs(image_dir, exist_ok=True)

# Create Excel file if it doesn't exist
if not os.path.exists(excel_file):
    pd.DataFrame(columns=["Detected Numbers"]).to_excel(excel_file, index=False)

# Enhanced OCR processing
def enhance_and_extract_numbers(frame):
    # Convert to grayscale
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    # Enhance contrast
    gray = cv2.equalizeHist(gray)

    # Blur to reduce noise
    blur = cv2.GaussianBlur(gray, (3, 3), 0)

    # Adaptive thresholding
    thresh = cv2.adaptiveThreshold(
        blur, 255, cv2.ADAPTIVE_THRESH_MEAN_C,
        cv2.THRESH_BINARY_INV, 15, 8
    )

    # Dilation to make lines thicker
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (2, 2))
    dilated = cv2.dilate(thresh, kernel, iterations=1)

    # Resize image (2x)
    processed = cv2.resize(dilated, None, fx=2, fy=2, interpolation=cv2.INTER_LINEAR)

    # OCR config for digits only
    config = r'--oem 3 --psm 6 -c tessedit_char_whitelist=0123456789'
    text = pytesseract.image_to_string(processed, config=config)
    numbers_only = re.findall(r'\d+', text)

    # Show for debugging
    cv2.imshow("Processed for OCR", processed)
    cv2.waitKey(2000)
    cv2.destroyAllWindows()

    print("🔢 Extracted Numbers:", numbers_only)
    return numbers_only

# Main capture + save function
def capture_and_extract_numbers():
    cap = cv2.VideoCapture(0)
    ret, frame = cap.read()
    if not ret:
        print("❌ Failed to capture image")
        return

    # Save original image
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    image_filename = os.path.join(image_dir, f"capture_{timestamp}.jpg")
    cv2.imwrite(image_filename, frame)
    print(f"📸 Image saved: {image_filename}")

    # Run enhanced OCR
    numbers_only = enhance_and_extract_numbers(frame)

    # Save to Excel
    if numbers_only:
        df_existing = pd.read_excel(excel_file)
        for num in numbers_only:
            df_existing = pd.concat(
                [df_existing, pd.DataFrame([[num]], columns=["Detected Numbers"])],
                ignore_index=True
            )
        df_existing.to_excel(excel_file, index=False)
        print("✅ Numbers saved to Excel.")

    # Show original frame briefly
    cv2.imshow("Captured Frame", frame)
    cv2.waitKey(1000)
    cv2.destroyAllWindows()
    cap.release()

# Main loop — Poll ESP8266
print("📡 Waiting for ESP8266 (Wi-Fi mode)...")                                           
while True:
    try:
        response = requests.get(esp_ip, timeout=2)
        result = response.text.strip().lower()
        print("📥 From ESP:", result)
        if result == 'start':
            capture_and_extract_numbers()
        time.sleep(1)
    except Exception as e:
        print("❗ Error:", e)
        time.sleep(2)
