#ifndef CONFIG_H
#define CONFIG_H

// WiFi Configuration
#define WIFI_SSID "your_wifi_ssid"
#define WIFI_PASS "your_wifi_password"

// MQTT Configuration
#define MQTT_BROKER_IP "raspberry_pi_ip"
#define MQTT_PORT 1883
#define MQTT_USER ""
#define MQTT_PASS ""

// Pin Configuration
#define BUTTON_PIN 4
#define LED_PIN 2

// Timing Configuration
#define DEBOUNCE_MS 50
#define HEARTBEAT_INTERVAL_MS 30000
#define WIFI_RECONNECT_DELAY_MS 1000
#define MQTT_RECONNECT_DELAY_MS 5000

// Debug Configuration
#define DEBUG_LEVEL 1  // 0=OFF, 1=INFO, 2=WARN, 3=ERROR

// Session Configuration
#define SESSION_TIMEOUT_MS 30000

#endif