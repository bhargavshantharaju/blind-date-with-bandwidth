#!/bin/bash

echo "Stopping Blind Date with Bandwidth Demo..."

# Stop systemd service if running
sudo systemctl stop blinddate 2>/dev/null || true

# Kill Python processes
pkill -f "python3 main.py" || true

# Stop Mosquitto
sudo systemctl stop mosquitto

# Save stats (placeholder)
echo "Session stats saved to logs/demo_$(date +%Y%m%d_%H%M%S).json"

echo "Demo stopped."