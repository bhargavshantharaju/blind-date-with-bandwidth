# Blind Date with Bandwidth – IEEE ComSoc Interactive Networking Demo

## Project Overview

Blind Date with Bandwidth is an interactive communication systems demonstration for IEEE Communication Society Open Day. Two participants, visually isolated, synchronize by matching audio signals to establish a temporary voice channel. This exhibit demonstrates networking concepts like bandwidth negotiation, synchronization, and session establishment through human interaction.

## Architecture Diagram (ASCII)

```
[ESP32 Station A] --MQTT/WiFi-- [Raspberry Pi Server] --MQTT/WiFi-- [ESP32 Station B]
       |                              |
   Button + LED                  + Flask Dashboard
       |                              |
   Headphones/Mic              + PyAudio Audio Bridge
                                  + Mosquitto MQTT Broker
```

## Tech Stack

- **Hardware**: ESP32, Raspberry Pi, USB Audio Interfaces
- **Firmware**: Arduino (ESP32)
- **Backend**: Python, PyAudio, Flask
- **Networking**: MQTT (Mosquitto), WiFi
- **Audio**: ALSA, WAV generation

## Quick Start

1. Flash ESP32 with station_A.ino / station_B.ino
2. On Raspberry Pi: `./start_demo.sh`
3. Open dashboard at http://pi_ip:5000



## Contributors

- [BHARGAV S RAJ] - Lead Developer

To collaborate: fork repo or request access.

1. Introduction
Blind Date with Bandwidth is an interactive communication systems demonstration designed for IEEE Communication Society Open Day. The system simulates how wireless devices discover, synchronize, and establish communication channels. Two participants, visually isolated from each other, attempt to synchronize by selecting matching audio signals. Upon success, a temporary voice channel opens between them.

This exhibit converts abstract networking concepts such as bandwidth negotiation, synchronization, handshake protocols, and session establishment into a memorable human experience.
2. Why Blind Date with Bandwidth
Modern wireless systems continuously perform discovery, frequency matching, channel negotiation, and secure session establishment — processes invisible to everyday users.

This project was chosen because:
• It demonstrates networking principles through human interaction.
• It visualizes synchronization and channel locking.
• It is emotionally engaging and highly crowd‑pulling.
• It integrates embedded systems, networking, audio processing, and UI/UX.
• It allows fast participant turnover (2 users every 1–2 minutes).
• It creates strong spectator curiosity.

This makes it appealing both technically to jury members and experientially to visitors.
3. Communication Concepts Demonstrated
Bandwidth – Represents channel capacity. Matching songs symbolize frequency allocation.
Synchronization – Both users must align on the same signal.
Handshake Protocol – Simulates SYN–ACK style connection establishment.
Channel Establishment – Audio routing opens only after successful match.
Packet Identification – Each audio clip carries a Track ID.
Session Timeout – Voice link closes automatically.
Device Discovery – Participants act as independent network nodes.
4. System Overview
Two isolated stations are provided. Each includes headphones, microphone, LED push button, and ESP32 controller. A Raspberry Pi acts as the central server managing audio playback, matching logic, and voice routing.

When both users lock onto the same Track ID, the Raspberry Pi establishes a live voice session between them for a fixed duration.
5. Hardware Components
Per Station:
• ESP32 Development Board
• Illuminated Push Button
• Headphones with Microphone

Central System:
• Raspberry Pi 4
• Dual‑Channel USB Audio Interface
• 32GB MicroSD Card
• WiFi Network

Miscellaneous:
• 5V Power Supply
• Voltage Regulators
• Audio Cables
• Booth Structure (MDF/Acrylic)
• Internal Wiring
6. Hardware Block Diagram
 
Figure: Simplified Hardware Architecture

ESP32 Pinout:
- GPIO 4: Button input (with pull-up, interrupt on falling)
- GPIO 2: LED output

Raspberry Pi Audio:
- USB Audio Device 1: Station A (mic + headphones)
- USB Audio Device 2: Station B (mic + headphones)

7. System Operation
1. Idle – Participants wear headphones; music clips begin.
2. Scanning – Each clip has hidden Track ID.
3. Locking – Button press sends Station ID + Track ID to Raspberry Pi.
4. Matching – Raspberry Pi compares IDs.
5. Success – Music stops, confirmation sound plays, voice channel opens.
6. Timeout – Session ends automatically and system resets.

Total interaction time: ~1–2 minutes.
8. Software Architecture
ESP32 Firmware:
• Button interrupt detection
• Debounce logic
• WiFi communication
• MQTT publishing

Raspberry Pi:
• MQTT Broker
• Python backend
• ALSA/PyAudio audio engine
• Matching algorithm
• Audio routing
• Flask dashboard
9. Dashboard & UI/UX
Dashboard displays:
• Successful sync count
• Average sync time
• Live status animation
• Optional participant names

Large fonts, bright colors, and real‑time updates ensure visibility from distance, attracting crowds.
10. Educational Value
The exhibit demonstrates:
• Wireless discovery
• Synchronization importance
• Bandwidth allocation
• Secure session establishment
• Timing sensitivity in networks

It bridges theoretical communication concepts with physical human interaction.
11. Failure Modes & Mitigation
WiFi drop – Auto reconnect.
Audio latency – Buffer tuning.
Button bounce – Firmware filtering.
Power fluctuation – Regulated supplies.
Feedback – Closed headphones.
Misuse – Auto session reset.
12. Conclusion
Blind Date with Bandwidth transforms invisible networking mechanisms into an engaging, real‑world experience. By combining embedded systems, networking protocols, audio processing, and UI design, it delivers strong educational value alongside crowd attraction.

It serves as a technically sound and memorable IEEE Communication Society Open Day exhibit.

## Deployment Instructions

### Hardware Wiring
- ESP32 Station A:
  - Button: GPIO 4 to button, GND to button
  - LED: GPIO 2 to LED anode, cathode to GND via resistor
  - Power: 3.3V, GND
- ESP32 Station B: Same as A, but change #define STATION_ID "B"
- Raspberry Pi:
  - USB Audio Interface connected
  - WiFi enabled

### Raspberry Pi Setup
1. Install OS (Raspberry Pi OS Lite)
2. Update: `sudo apt update && sudo apt upgrade`
3. Install Mosquitto: `sudo apt install mosquitto mosquitto-clients`
4. Install ALSA: `sudo apt install alsa-utils`
5. Install Python: `sudo apt install python3 python3-pip`
6. Install packages: `pip3 install -r requirements.txt`
7. Configure ALSA: Edit /etc/asound.conf or use device indices in code
8. Place audio files: success.wav, track1.wav to track5.wav in raspberry_pi_server/

### Arduino Upload
1. Install Arduino IDE
2. Install ESP32 board support
3. Open blind_date_esp32.ino
4. Set STATION_ID to "A" or "B"
5. Update WiFi credentials and MQTT IP
6. Upload to ESP32

### Demo Startup
1. Start Mosquitto: `sudo systemctl start mosquitto`
2. Run server: `cd raspberry_pi_server && python3 main.py`
3. Dashboard: Open http://raspberry_pi_ip:5000 in browser
4. Power on ESP32 stations

### Troubleshooting
- Audio devices: Run `arecord -l` and `aplay -l` to find indices
- MQTT: Check `mosquitto_sub -t blinddate/lock`
- WiFi: Ensure ESP32 connects to same network as Pi
- Audio latency: Adjust chunk size in audio.py

## Quick Start

1. Flash ESP32 stations with station_A.ino and station_B.ino.
2. On Raspberry Pi: `cd raspberry_pi_server && chmod +x start_demo.sh && ./start_demo.sh`
3. Open dashboard URL in browser.

## ESP32 Flashing

1. Install Arduino IDE with ESP32 support.
2. Open station_A.ino, update WiFi and MQTT IP.
3. Upload to ESP32 A.
4. Repeat for station_B.ino on ESP32 B.

## Demo Day Checklist

- [ ] Power on Raspberry Pi and ESP32s
- [ ] Connect USB audio interfaces
- [ ] Test headphones and mics
- [ ] Run `./start_demo.sh`
- [ ] Verify dashboard loads
- [ ] Test button presses and matching

## Judge Explanation Summary

"This demo shows real-time wireless synchronization and voice channel establishment, simulating networking protocols like bandwidth negotiation and session setup. Participants match randomly generated track IDs to open a live audio bridge, demonstrating concepts invisible in modern devices."

## Emergency Recovery

- If audio fails: Check USB devices with `lsusb`, restart PyAudio.
- If MQTT fails: `sudo systemctl restart mosquitto`
- If ESP32 disconnects: Power cycle or check WiFi.
- Full reset: Kill processes, restart demo.
