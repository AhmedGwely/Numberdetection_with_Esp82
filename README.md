# 🚚 Number Detection with ESP8266 + OpenCV

This project combines **ESP8266**, **MQTT**, and **OpenCV (EasyOCR / Tesseract)**  
to automatically detect **truck/car numbers** from camera images and send them to a **PC server** for processing and storage.

---

## 📌 Features

- ESP8266 triggers number detection via a **button press**.
- Two modes supported:
  - **MQTT Mode (EasyOCR)** → ESP8266 publishes `"start"` to MQTT broker → PC captures + detects numbers.
  - **HTTP Polling Mode (Tesseract)** → PC polls ESP8266 server for `"start"` signal.
- Numbers are:
  - Extracted from camera images using **OCR**.
  - Annotated on captured images.
  - Saved into **CSV** (MQTT mode) or **Excel** (HTTP mode).
  - Published back to **MQTT topic** for other consumers.
- Easy to extend for multiple cameras/ports.

---

## 🛠️ Hardware Requirements

- ESP8266 (NodeMCU or Wemos D1 Mini)
- Push button (connected to `D5 / GPIO14`)
- USB Camera (connected to PC / Laptop running detection scripts)
- MQTT Broker (e.g., **Mosquitto**)

---

## 🧩 Software Requirements

- Python 3.8+
- [Tesseract OCR](https://github.com/tesseract-ocr/tesseract) (for `adv_Wi_esp.py`)
- MQTT Broker (e.g., `mosquitto`)

Install Python dependencies:

```bash
pip install -r requirements.txt
```
# 📂 Repository Structure

- Numberdetection_with_Esp82/
  - │── CarNumberDetecton.py     # EasyOCR + MQTT workflow
  - │── adv_Wi_esp.py            # Tesseract + HTTP polling workflow
  - │── wifi_esp_cam.ino         # ESP8266 firmware (button → MQTT publish) 
  - │── mosquitto.conf           # Example MQTT broker config
  - |── truck_num.csv            # CSV log file (detected numbers in MQTT mode)
  - │── numbers.xlsx             # Excel log file (detected numbers in HTTP mode)
  - │── requirements.txt         # Python dependencies list
  - │── captured_images/         # Folder for saving annotated images
  - │── README.md                # Project documentation
--- 

## 1️⃣ MQTT Mode (with EasyOCR)

**Workflow:**

1. **ESP8266** button press → publishes `"start"` to topic `cam1/esp`.
2. **PC script (`CarNumberDetecton.py`)**:
   - Subscribes to MQTT.
   - Captures image from webcam.
   - Extracts numbers via **EasyOCR**.
   - Saves results to **`truck_num.csv`**.
   - Publishes detected number(s) back to MQTT.
  
## 2️⃣ HTTP Mode (with Tesseract)

**Workflow:**

1. **ESP8266** hosts simple web server.  
2. **PC script (`adv_Wi_esp.py`)**:
   - Polls ESP8266 endpoint.
   - Captures + preprocesses image.
   - Extracts digits with **Tesseract OCR**.
   - Saves results to **`numbers.xlsx`**.

**Run:**

```bash
python adv_Wi_esp.py
```

--- 
# 📑 Output Samples

 ### CSV (MQTT mode): 

``` bash
   port,number
   CAM1,760
   CAM1,2020
   CAM1,7580
```

### Excel (HTTP mode):

- Detected Numbers

``` bash
    1111
    2222
    758
```


--- 

# 🔧 ESP8266 Setup

Upload wifi_esp_cam.ino using Arduino IDE / PlatformIO.

   **Pinout:**

  -  D5 (GPIO14) → Push Button

  - Internal Pull-Up enabled

### Configurable Parameters:
```bash
const char* ssid = "Your_WiFi_Name";
const char* password = "Your_WiFi_Password";
const char* mqtt_server = "192.168.1.22";  // Broker IP
```

👉 When button pressed → ESP8266 publishes "start" to topic cam1/esp.




# 👨‍💻 Author

- **Ahmed Gwely**  
- Passionate about Computer Vision, Embedded Systems, and AI-driven IoT.  
- 🌐 [LinkedIn Profile](https://www.linkedin.com/in/ahmed-gwely-2589611b0/)  

