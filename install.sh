#!/bin/bash
set -e
echo "Installing Blind Date with Bandwidth..."

# Update system
sudo apt update && sudo apt upgrade -y

# Install dependencies
sudo apt install -y mosquitto mosquitto-clients python3 python3-pip alsa-utils

# Install Python packages
pip3 install -r requirements.txt

# Enable Mosquitto
sudo systemctl enable mosquitto

# Create systemd service
cat > blinddate.service << EOF
[Unit]
Description=Blind Date with Bandwidth Demo
After=network.target

[Service]
Type=simple
User=pi
WorkingDirectory=/home/pi/blind-date-with-bandwidth/raspberry_pi_server
ExecStart=/usr/bin/python3 main.py
Restart=always

[Install]
WantedBy=multi-user.target
EOF

sudo mv blinddate.service /etc/systemd/system/
sudo systemctl enable blinddate

echo "Installation complete. Run ./start_demo.sh to begin."