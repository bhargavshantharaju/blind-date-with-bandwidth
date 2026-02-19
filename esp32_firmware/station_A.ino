#include <WiFi.h>
#include <PubSubClient.h>
#include <ArduinoJson.h>

// WiFi credentials
const char* ssid = "your_wifi_ssid";
const char* password = "your_wifi_password";

// MQTT broker
const char* mqtt_server = "raspberry_pi_ip"; // IP of Raspberry Pi
const int mqtt_port = 1883;
const char* mqtt_user = "";
const char* mqtt_pass = "";

// Station ID
#define STATION_ID "A"

// Pins
const int buttonPin = 4; // GPIO pin for button
const int ledPin = 2;    // GPIO pin for LED

// MQTT topics
const char* lock_topic = "blinddate/lock";
const char* status_topic = "blinddate/status";

WiFiClient espClient;
PubSubClient client(espClient);

volatile bool buttonPressed = false;
unsigned long lastDebounceTime = 0;
unsigned long debounceDelay = 50;
int lastButtonState = HIGH;
bool matched = false;

void IRAM_ATTR buttonISR() {
  buttonPressed = true;
}

void setup() {
  Serial.begin(115200);
  pinMode(buttonPin, INPUT_PULLUP);
  pinMode(ledPin, OUTPUT);
  attachInterrupt(digitalPinToInterrupt(buttonPin), buttonISR, FALLING);

  setup_wifi();
  client.setServer(mqtt_server, mqtt_port);
  client.setCallback(callback);
}

void setup_wifi() {
  delay(10);
  Serial.println();
  Serial.print("Connecting to ");
  Serial.println(ssid);

  WiFi.begin(ssid, password);

  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }

  Serial.println("");
  Serial.println("WiFi connected");
  Serial.println("IP address: ");
  Serial.println(WiFi.localIP());
}

void callback(char* topic, byte* payload, unsigned int length) {
  Serial.print("Message arrived [");
  Serial.print(topic);
  Serial.print("] ");
  String message;
  for (int i = 0; i < length; i++) {
    message += (char)payload[i];
  }
  Serial.println(message);

  if (String(topic) == status_topic) {
    DynamicJsonDocument doc(1024);
    deserializeJson(doc, message);
    if (doc["station"] == STATION_ID) {
      matched = doc["matched"];
    }
  }
}

void reconnect() {
  while (!client.connected()) {
    Serial.print("Attempting MQTT connection...");
    if (client.connect(("ESP32_" + String(STATION_ID)).c_str(), mqtt_user, mqtt_pass)) {
      Serial.println("connected");
      client.subscribe(status_topic);
    } else {
      Serial.print("failed, rc=");
      Serial.print(client.state());
      Serial.println(" try again in 5 seconds");
      delay(5000);
    }
  }
}

void loop() {
  if (!client.connected()) {
    reconnect();
  }
  client.loop();

  // LED feedback
  if (matched) {
    digitalWrite(ledPin, HIGH); // Solid on
  } else {
    // Slow blink
    digitalWrite(ledPin, millis() / 1000 % 2);
  }

  // Handle button press
  if (buttonPressed) {
    unsigned long currentTime = millis();
    if (currentTime - lastDebounceTime > debounceDelay) {
      lastDebounceTime = currentTime;
      // Generate random track ID 1-5
      int track = random(1, 6);
      // Publish JSON
      DynamicJsonDocument doc(1024);
      doc["station"] = STATION_ID;
      doc["track"] = track;
      doc["timestamp"] = currentTime;
      String output;
      serializeJson(doc, output);
      client.publish(lock_topic, output.c_str());
      Serial.println("Published: " + output);
    }
    buttonPressed = false;
  }
}