# Architecture

## System Overview

Blind Date with Bandwidth consists of two ESP32-based stations and a Raspberry Pi central server, communicating via MQTT over WiFi.

## Data Flow

1. ESP32 stations generate random track IDs on button press
2. MQTT publishes lock events to Raspberry Pi
3. Pi's matcher state machine detects matches
4. On match: audio bridging starts, dashboard updates
5. After timeout: system resets

## MQTT Topics

- `blinddate/lock`: Station lock events
- `blinddate/heartbeat`: Station online status
- `blinddate/status`: Match notifications
- `blinddate/result`: Match results
- `blinddate/reset`: System reset commands

## State Machine

```
IDLE → LOCKED_A → LOCKED_B → MATCHED → TIMEOUT → IDLE
     ↑            ↓
     └──── SCANNING ───┘
```

## Audio Pipeline

- Tone generation: numpy + scipy
- Playback: sounddevice
- Bridging: real-time stream forwarding
- Devices: auto-detected USB audio interfaces