# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.0] - 2024-01-15

### Added
- Complete ESP32 firmware with OTA updates and LED state feedback
- Raspberry Pi backend with modular architecture (matcher, audio, MQTT)
- Real-time Flask-SocketIO dashboard with dark theme and animations
- Automated audio clip generation using numpy/scipy
- Full-duplex audio bridging with sounddevice
- Comprehensive test suite with pytest
- GitHub Actions CI/CD pipeline
- Detailed documentation and hardware BOM
- One-command install/start/stop scripts
- Systemd service integration

### Changed
- Migrated from PyAudio to sounddevice for better cross-platform support
- Refactored monolithic main.py into clean modules
- Improved error handling and logging throughout

### Technical Details
- Python 3.9+ compatibility
- Raspberry Pi OS Lite tested
- Arduino IDE 2.x firmware compilation
- MQTT with LWT for reliability
- WebSocket real-time updates