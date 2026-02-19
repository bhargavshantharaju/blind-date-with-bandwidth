#define STATION_ID "A"
#include <WiFi.h>
#include <WiFiClientSecure.h>
#include <PubSubClient.h>
#include <ArduinoJson.h>
#include <ArduinoOTA.h>
#include <Adafruit_SSD1306.h>
#include <Adafruit_GFX.h>
#include <Wire.h>
#include "../shared/config.h"

// MQTT topics
const char* lock_topic = "blinddate/lock";
const char* status_topic = "blinddate/status";
const char* heartbeat_topic = "blinddate/heartbeat";

WiFiClientSecure espClient;
PubSubClient client(espClient);

Adafruit_SSD1306 display(128, 64, &Wire, OLED_RESET);

volatile bool buttonPressed = false;
unsigned long lastDebounceTime = 0;
unsigned long lastHeartbeatTime = 0;
unsigned long lastWiFiReconnect = 0;
unsigned long lastMQTTReconnect = 0;
bool matched = false;
int wifiReconnectAttempts = 0;
int currentTrack = 0;
unsigned long sessionStart = 0;

// Debug logging
#define LOG_INFO(msg) if (DEBUG_LEVEL >= 1) Serial.println("[INFO] " msg)
#define LOG_WARN(msg) if (DEBUG_LEVEL >= 2) Serial.println("[WARN] " msg)
#define LOG_ERROR(msg) if (DEBUG_LEVEL >= 3) Serial.println("[ERROR] " msg)

// LED states
enum LedState { SCANNING, LOCKED, CONNECTED, ERROR };
LedState currentLedState = SCANNING;

void IRAM_ATTR buttonISR() {
  buttonPressed = true;
}

void setLedState(LedState state) {
  currentLedState = state;
}

void updateLed() {
  unsigned long now = millis();
  switch (currentLedState) {
    case SCANNING:
      digitalWrite(LED_PIN, (now / 1000) % 2);  // Slow blink
      digitalWrite(VIBRATION_PIN, LOW);
      display.clearDisplay();
      display.setCursor(0,0);
      display.println("SCANNING...");
      display.display();
      break;
    case LOCKED:
      digitalWrite(LED_PIN, (now / 250) % 2);   // Fast blink
      digitalWrite(VIBRATION_PIN, HIGH);  // Vibrate when locked
      display.clearDisplay();
      display.setCursor(0,0);
      display.println("LOCKED");
      display.setCursor(0,20);
      display.printf("Track: %d", currentTrack);
      if (sessionStart > 0) {
        int countdown = 30 - (now - sessionStart) / 1000;
        if (countdown > 0) {
          display.setCursor(0,40);
          display.printf("Time: %d", countdown);
        }
      }
      display.display();
      break;
    case CONNECTED:
      digitalWrite(LED_PIN, HIGH);              // Solid on
      digitalWrite(VIBRATION_PIN, LOW);
      display.clearDisplay();
      display.setCursor(0,0);
      display.println("SYNCED!");
      display.display();
      break;
    case ERROR:
      // SOS pattern
      int pattern = (now / 150) % 19;
      digitalWrite(LED_PIN, (pattern < 3 || (pattern >= 6 && pattern < 9) || (pattern >= 12 && pattern < 15)));
      digitalWrite(VIBRATION_PIN, (now / 500) % 2);  // Fast vibrate on error
      display.clearDisplay();
      display.setCursor(0,0);
      display.println("ERROR");
      display.display();
      break;
  }
}

void setup() {
  Serial.begin(115200);
  LOG_INFO("Starting Blind Date Station " STATION_ID);

  pinMode(BUTTON_PIN, INPUT_PULLUP);
  pinMode(LED_PIN, OUTPUT);
  pinMode(VIBRATION_PIN, OUTPUT);
  attachInterrupt(digitalPinToInterrupt(BUTTON_PIN), buttonISR, FALLING);

  // Initialize OLED
  Wire.begin(OLED_SDA, OLED_SCL);
  if(!display.begin(SSD1306_SWITCHCAPVCC, 0x3C)) {
    LOG_ERROR("SSD1306 allocation failed");
    for(;;);
  }
  display.clearDisplay();
  display.setTextSize(2);
  display.setTextColor(SSD1306_WHITE);
  display.setCursor(0,0);
  display.println("SCANNING...");
  display.display();

  setup_wifi();
  setup_ota();
  espClient.setCACert(MQTT_CA_CERT);
  client.setServer(MQTT_BROKER_IP, MQTT_PORT);
  client.setCallback(callback);
}

void setup_wifi() {
  LOG_INFO("Connecting to WiFi...");
  WiFi.begin(WIFI_SSID, WIFI_PASS);
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    LOG_WARN("WiFi reconnecting...");
  }
  LOG_INFO("WiFi connected");
  LOG_INFO(WiFi.localIP().toString().c_str());
}

void setup_ota() {
  ArduinoOTA.setHostname(("BlindDate_" STATION_ID).c_str());
  ArduinoOTA.onStart([]() { LOG_INFO("OTA start"); });
  ArduinoOTA.onEnd([]() { LOG_INFO("OTA end"); });
  ArduinoOTA.onProgress([](unsigned int progress, unsigned int total) {
    Serial.printf("[OTA] %u%%\r", (progress / (total / 100)));
  });
  ArduinoOTA.onError([](ota_error_t error) {
    LOG_ERROR("OTA error");
  });
  ArduinoOTA.begin();
}

void callback(char* topic, byte* payload, unsigned int length) {
  String message;
  for (int i = 0; i < length; i++) {
    message += (char)payload[i];
  }
  LOG_INFO(("MQTT: " + String(topic) + " - " + message).c_str());

  if (String(topic) == status_topic) {
    DynamicJsonDocument doc(1024);
    deserializeJson(doc, message);
    if (doc["station"] == STATION_ID) {
      matched = doc["matched"];
      if (matched) {
        sessionStart = millis();
      } else {
        sessionStart = 0;
      }
      setLedState(matched ? CONNECTED : SCANNING);
    }
  }
}

void reconnect() {
  if (WiFi.status() != WL_CONNECTED) {
    unsigned long now = millis();
    if (now - lastWiFiReconnect > WIFI_RECONNECT_DELAY_MS * (1 << min(wifiReconnectAttempts, 5))) {
      lastWiFiReconnect = now;
      wifiReconnectAttempts++;
      LOG_WARN("WiFi reconnecting...");
      WiFi.reconnect();
    }
    return;
  }
  wifiReconnectAttempts = 0;

  if (!client.connected()) {
    unsigned long now = millis();
    if (now - lastMQTTReconnect > MQTT_RECONNECT_DELAY_MS) {
      lastMQTTReconnect = now;
      LOG_WARN("MQTT reconnecting...");
      if (client.connect(("ESP32_" STATION_ID).c_str(), MQTT_USER, MQTT_PASS)) {
        LOG_INFO("MQTT connected");
        client.subscribe(status_topic);
      } else {
        LOG_ERROR("MQTT failed");
      }
    }
  }
}

void sendHeartbeat() {
  unsigned long now = millis();
  if (now - lastHeartbeatTime > HEARTBEAT_INTERVAL_MS) {
    lastHeartbeatTime = now;
    DynamicJsonDocument doc(1024);
    doc["station"] = STATION_ID;
    doc["timestamp"] = now;
    String output;
    serializeJson(doc, output);
    client.publish(heartbeat_topic, output.c_str());
    LOG_INFO("Heartbeat sent");
  }
}

void loop() {
  ArduinoOTA.handle();
  updateLed();

  if (!client.connected() || WiFi.status() != WL_CONNECTED) {
    setLedState(ERROR);
    reconnect();
  } else {
    client.loop();
    sendHeartbeat();
  }

  // Handle button press with proper debounce
  if (buttonPressed) {
    unsigned long currentTime = millis();
    if (currentTime - lastDebounceTime > DEBOUNCE_MS) {
      lastDebounceTime = currentTime;
      // Generate random track ID 1-5
      currentTrack = random(1, 6);
      // Publish JSON
      DynamicJsonDocument doc(1024);
      doc["station"] = STATION_ID;
      doc["track"] = currentTrack;
      doc["timestamp"] = currentTime;
      String output;
      serializeJson(doc, output);
      client.publish(lock_topic, output.c_str());
      LOG_INFO(("Published: " + output).c_str());
      setLedState(LOCKED);
    }
    buttonPressed = false;
  }
}