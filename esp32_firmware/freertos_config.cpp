// FreeRTOS Task Priority Configuration for ESP32
// Layer 17 Performance Optimization
//
// Priority levels: 24 (highest) to 0 (lowest)
// Core affinity: 0 (protocol CPU), 1 (application CPU)

#include <freertos/FreeRTOS.h>
#include <freertos/task.h>

// ============================================
// CRITICAL REALTIME TASKS (Priority 20-24)
// ============================================
// Must respond in <50ms, preempt everything else

void buttonInterruptTask(void *param) {
    // Priority 24, Core 0 (protocol CPU handles I/O)
    // GPIO interrupt -> FIFO queue -> session lock
    // MUST respond within 5-10ms for perceived responsiveness
    while(1) {
        if (xQueueReceive(buttonQueue, &btn_event, portMAX_DELAY)) {
            handleLockButton();  // ~2ms
        }
    }
}

// ============================================
// AUDIO/TIMING TASKS (Priority 18-20)
// ============================================
// Must maintain audio timeline and sample accuracy

void audioStreamTask(void *param) {
    // Priority 20, Core 1 (application CPU)
    // 44.1kHz stereo = 22.05kHz per channel = 45.35 µs per sample
    // Buffer size: 256 samples = 5.8ms
    // Cannot allow jitter >100µs
    while(1) {
        xQueueReceive(audioFrameQueue, &frame, pdMS_TO_TICKS(1));
        playAudioFrame(frame);  // Must be <5ms
    }
}

void displayRefreshTask(void *param) {
    // Priority 18, Core 1
    // OLED i2c update ~10-15ms every 100ms
    // Can tolerate visual frame drops without audio breaking
    while(1) {
        vTaskDelay(pdMS_TO_TICKS(100));  // Update every 100ms
        updateOLED();  // ~12ms via I2C
    }
}

// ============================================
// NETWORK/CONNECTIVITY (Priority 10-15)
// ============================================
// Background tasks, can tolerate millisecond-level latency

void mqttPollTask(void *param) {
    // Priority 12, Core 1
    // MQTT heartbeat every 30s, message processing
    // Tolerates 100-500ms latency
    while(1) {
        vTaskDelay(pdMS_TO_TICKS(100));
        mqtt_handle_events();  // ~30-50ms for message handling
    }
}

void wifiSyncTask(void *param) {
    // Priority 10, Core 0
    // WiFi link monitoring, channel changes
    // Tolerates 1-5s latency
    while(1) {
        vTaskDelay(pdMS_TO_TICKS(1000));
        wiifiMonitorConnection();  // Async operation
    }
}

// ============================================
// BACKGROUND/LOGGING (Priority 1-5)
// ============================================
// Non-critical, preempted by everything

void loggingTask(void *param) {
    // Priority 1, Core 0
    // Batch write logs to flash/SPIFFS
    // Safe to starve this task
    while(1) {
        vTaskDelay(pdMS_TO_TICKS(500));
        flushLogBuffer();  // ~100ms for SPIFFS write
    }
}

// ============================================
// TASK CREATION SEQUENCE (setup.cpp)
// ============================================

void setup() {
    // Create tasks in priority order from highest to lowest
    
    // Audio (highest priority)
    xTaskCreatePinnedToCore(
        audioStreamTask,
        "audio",
        4096,           // Stack size
        NULL,
        20,             // Priority
        NULL,
        1               // Core 1 (app CPU)
    );
    
    // Display
    xTaskCreatePinnedToCore(
        displayRefreshTask,
        "display",
        2048,
        NULL,
        18,
        NULL,
        1
    );
    
    // Button
    xTaskCreatePinnedToCore(
        buttonInterruptTask,
        "button",
        1024,
        NULL,
        24,             // HIGHEST - interrupts everything
        NULL,
        0               // Core 0 (protocol CPU)
    );
    
    // MQTT
    xTaskCreatePinnedToCore(
        mqttPollTask,
        "mqtt",
        4096,
        NULL,
        12,
        NULL,
        1
    );
    
    // WiFi monitor
    xTaskCreatePinnedToCore(
        wifiSyncTask,
        "wifi",
        2048,
        NULL,
        10,
        NULL,
        0
    );
    
    // Logging (lowest)
    xTaskCreatePinnedToCore(
        loggingTask,
        "logging",
        2048,
        NULL,
        1,
        NULL,
        0
    );
}

// ============================================
// PERFORMANCE TUNING CONSIDERATIONS
// ============================================
// Stack sizes (bytes):
//   - Audio:   4096 (DSP buffers)
//   - MQTT:    4096 (JSON parsing)
//   - Display: 2048 (I2C transactions)
//   - WiFi:    2048 (network operations)
//   - Logging: 2048 (file I/O)
//   - Button:  1024 (minimal, interrupt-only)
//
// Tick rate: Default 1000Hz (1ms resolution)
// Heap: ~320KB available (32KB reserved for WiFi/BLE)
// SPIRAM: Optional 8MB chip for large audio buffers

// Watchdog monitoring:
#define WDT_TIMEOUT 5  // 5-second hardware watchdog
if (esp_task_wdt_add(NULL) != ESP_OK) {
    ESP_LOGE(TAG, "Failed to add task to WDT");
}
