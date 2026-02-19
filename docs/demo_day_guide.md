# Demo Day Guide

## Pre-Demo Setup

- [ ] Run `./install.sh` on fresh Pi
- [ ] Flash ESP32 stations with Arduino IDE
- [ ] Test `./start_demo.sh`
- [ ] Connect headphones and mics
- [ ] Open dashboard on tablet

## Operator Script

### Introduction (30 seconds)
"Welcome to Blind Date with Bandwidth! This interactive demo shows how wireless devices synchronize and establish communication channels. Two participants will try to match audio signals to open a live voice connection."

### During Demo
- Encourage visitors to press buttons
- Explain LED states: "Slow blink = searching, fast blink = locked, solid = connected"
- Point out dashboard: "See the real-time status and sync statistics"

### For Judges
- "This demonstrates networking concepts like handshake protocols and session establishment"
- "The random track IDs simulate frequency hopping in wireless networks"
- "Audio bridging shows real-time duplex communication"

### Common Issues
- No match: "Try pressing at the same time!"
- Audio lag: "Real-time systems have latency challenges"
- ESP32 offline: "Reconnect WiFi, check power"

## Post-Demo

- Run `./stop_demo.sh`
- Note visitor feedback
- Reset for next group