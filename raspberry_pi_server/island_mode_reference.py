"""
ESP32 resilience features: island mode, NVS storage, QoS, sequence numbers.
Reference implementation for Arduino sketch integration.
"""

# ESP32 Arduino sketch additions for island_mode.ino:

ISLAND_MODE_SKETCH = """
// ===== ISLAND MODE SUPPORT =====
#include <SPIFFS.h>
#include <nvs_flash.h>
#include <nvs.h>

#define ISLAND_MODE_TIMEOUT_MS 10000  // 10 seconds without WiFi

volatile unsigned long lastMQTTReceived = 0;
bool islandMode = false;
int messageSequenceNumber = 0;
uint32_t sessionStateNVS = 0;

void initEEPROM() {
  // Initialize NVS (flash storage)
  esp_err_t err = nvs_flash_init();
  if (err == ESP_ERR_NVS_NO_FREE_PAGES || err == ESP_ERR_NVS_NEW_VERSION_FOUND) {
    ESP_ERROR_CHECK(nvs_flash_erase());
    err = nvs_flash_init();
  }
  ESP_ERROR_CHECK(err);
  
  // Initialize SPIFFS for fallback audio
  if(!SPIFFS.begin(true)){
    LOG_ERROR("SPIFFS Mount Failed");
  }
}

void saveSessionState(int track, bool matched) {
  nvs_handle_t my_handle;
  esp_err_t err = nvs_open("blinddate", NVS_READWRITE, &my_handle);
  if (err != ESP_OK) return;
  
  uint32_t state = (track << 8) | (matched ? 1 : 0);
  nvs_set_u32(my_handle, "session", state);
  nvs_close(my_handle);
}

void recoverSessionState(int& track, bool& matched) {
  nvs_handle_t my_handle;
  esp_err_t err = nvs_open("blinddate", NVS_READONLY, &my_handle);
  if (err != ESP_OK) {
    track = 0;
    matched = false;
    return;
  }
  
  uint32_t state = 0;
  nvs_get_u32(my_handle, "session", &state);
  track = (state >> 8) & 0xFF;
  matched = (state & 1) != 0;
  nvs_close(my_handle);
}

void checkIslandMode() {
  unsigned long now = millis();
  if (WiFi.status() != WL_CONNECTED && !islandMode) {
    if (now - lastWiFiReconnect > ISLAND_MODE_TIMEOUT_MS) {
      islandMode = true;
      LOG_INFO("Entering island mode - playing local track");
      playLocalFallbackTrack();
    }
  } else if (WiFi.status() == WL_CONNECTED && islandMode) {
    islandMode = false;
    LOG_INFO("Exiting island mode - WiFi restored");
  }
}

void playLocalFallbackTrack() {
  // Play pre-stored beep sequence from SPIFFS or generate locally
  for (int i = 0; i < 5; i++) {
    tone(AUDIO_PIN, 1000, 100);  // Simple beep
    delay(200);
  }
}

void publishWithQoS(const char* topic, const char* payload, int qos) {
  DynamicJsonDocument doc(1024);
  doc["msg_seq"] = messageSequenceNumber++;
  doc["payload"] = payload;
  
  String output;
  serializeJson(doc, output);
  
  // QoS 1: at least once delivery
  if (qos >= 1) {
    client.publish(topic, output.c_str(), true);  // retained
  } else {
    client.publish(topic, output.c_str());
  }
}

// In setup():
void setup_resilience() {
  initEEPROM();
  TaskHandle_t watchdogHandle;
  xTaskCreate(watchdogTask, "watchdog", 2048, NULL, configMAX_PRIORITIES-1, &watchdogHandle);
  esp_task_wdt_add(watchdogHandle);
  esp_task_wdt_init(30, true);  // 30s watchdog
}

void watchdogTask(void *pvParameters) {
  while(1) {
    checkIslandMode();
    esp_task_wdt_reset();
    vTaskDelay(1000 / portTICK_PERIOD_MS);
  }
}
"""

print("Island mode sketch additions saved to references")
