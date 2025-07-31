import cv2
import easyocr
import paho.mqtt.client as mqtt
import re
import pandas as pd
import os
import time
from datetime import datetime

# MQTT broker and topic configuration
broker_ip = "192.168.1.22"
topic = "cam1/esp"

# Port label for saving in CSV
port_name = "CAM1"

# Paths for saving images and CSV data
csv_file = "truck_num.csv"
image_dir = "captured_images"
os.makedirs(image_dir, exist_ok=True)

# Create CSV file if it doesn't exist
if not os.path.exists(csv_file):
    pd.DataFrame(columns=["port", "number"]).to_csv(csv_file, index=False)

# Initialize EasyOCR reader
reader = easyocr.Reader(['en'], gpu=False)


def extract_numbers_with_easyocr(image):
    results = reader.readtext(image)
    numbers = []

    for (bbox, text, prob) in results:
        digits = re.findall(r'\d+', text)
        if digits:
            numbers.extend(digits)

            (top_left, top_right, bottom_right, bottom_left) = bbox
            top_left = tuple(map(int, top_left))
            bottom_right = tuple(map(int, bottom_right))
            cv2.rectangle(image, top_left, bottom_right, (0, 255, 0), 2)
            cv2.putText(image, text, (top_left[0], top_left[1] - 10),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)

    return numbers, image


def capture_and_extract_numbers():
    cap = cv2.VideoCapture(0)

    # Give the camera time to warm up
    time.sleep(3)
    for _ in range(5):
        cap.read()

    # Capture frame
    ret, frame = cap.read()
    if not ret:
        print(" Failed to capture image")
        return

    numbers_only, annotated_image = extract_numbers_with_easyocr(frame)
    print(" Extracted Numbers:", numbers_only)

    # Save annotated image with timestamp and number in filename
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{numbers_only[0] if numbers_only else 'capture'}_{timestamp}.jpg"
    image_path = os.path.join(image_dir, filename)
    cv2.imwrite(image_path, annotated_image)
    print(f" Annotated image saved: {image_path}")

    # Save numbers to CSV if any detected
    if numbers_only:
        df_existing = pd.read_csv(csv_file)
        for num in numbers_only:
            df_existing = pd.concat(
                [df_existing, pd.DataFrame([[port_name, num]], columns=["port", "number"])],
                ignore_index=True
            )
            client.publish("cam1/esp", num)  # ✅ Publish detected number via MQTT
        df_existing.to_csv(csv_file, index=False)
        print(" Numbers saved to CSV.")

    # Show the result for 2 seconds
    cap.release()
    cv2.imshow("Result", annotated_image)
    cv2.waitKey(2000)
    cv2.destroyAllWindows()


# Variables to control MQTT message cooldown
last_processed_time = 0
cooldown_seconds = 10


# MQTT callback for received messages
def on_message(client, userdata, msg):
    global last_processed_time
    payload = msg.payload.decode().strip().lower()
    now = time.time()
    if payload == 'start' and (now - last_processed_time) >= cooldown_seconds:
        last_processed_time = now
        print("From ESP: start → capturing")
        capture_and_extract_numbers()
    else:
        print(" Ignored (cooldown or invalid)")


# Setup and start MQTT client
client = mqtt.Client()
client.on_message = on_message

print("Connecting to MQTT...")
client.connect(broker_ip, 1883, 60)
client.subscribe(topic)
print(f"Subscribed to {topic}")

client.loop_forever()
