#include <ESP8266WiFi.h>
#include <PubSubClient.h>

// Wi-Fi
const char* ssid = "Ahmed Gwely";
const char* password = "##60Ahmed_Gwely_new40!!";

// MQTT Broker
const char* mqtt_server = "192.168.1.22";  // ← IP 

WiFiClient espClient;
PubSubClient client(espClient);

// the sensor
const int buttonPin = 14; // D5
unsigned long lastPress = 0;
const unsigned long cooldown = 10000;

void setup_wifi() {
  delay(10);
  Serial.println("🔌 Connecting to Wi-Fi...");
  WiFi.begin(ssid, password);

  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }
  Serial.println("\n Wi-Fi connected");
  Serial.println(WiFi.localIP());
}

void reconnect() {
  while (!client.connected()) {
    Serial.println("Connecting to MQTT...");
    if (client.connect("ESP8266Client")) {
      Serial.println("connected");
    } else {
      Serial.println("failed, rc=");
      Serial.print(client.state());
      delay(2000);
    }
  }
}

void setup() {
  pinMode(buttonPin, INPUT_PULLUP);
  Serial.begin(115200);
  setup_wifi();
  client.setServer(mqtt_server, 1883);
}

void loop() {
  if (!client.connected()) {
    reconnect();
  }
  client.loop();

  if (digitalRead(buttonPin) == LOW && millis() - lastPress > cooldown) {
    Serial.println("Button pressed → MQTT");
    client.publish("cam1/esp", "start");
    lastPress = millis();
  }
}
