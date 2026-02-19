#!/bin/bash
set -e
echo "Installing Blind Date with Bandwidth..."

# Update system
sudo apt update && sudo apt upgrade -y

# Install dependencies
sudo apt install -y mosquitto mosquitto-clients python3 python3-pip alsa-utils openssl qrencode

# Install Python packages
cd raspberry_pi_server
pip3 install -r requirements.txt
cd ..

# Create config directory
sudo mkdir -p /etc/blinddate
sudo mkdir -p /var/lib/blinddate/archive
sudo mkdir -p /var/log/blinddate

# Generate MQTT credentials
MQTT_USER="blinddate"
MQTT_PASS=$(openssl rand -base64 12)
echo "Generated MQTT password: $MQTT_PASS"

# Store MQTT config
sudo bash -c "cat > /etc/blinddate/mqtt.conf << EOF
user $MQTT_USER
password $MQTT_PASS
EOF"
sudo chmod 600 /etc/blinddate/mqtt.conf

# Generate self-signed certificates for MQTT TLS
sudo openssl req -new -x509 -days 365 -nodes -out /etc/blinddate/ca.crt -keyout /etc/blinddate/ca.key -subj "/C=US/ST=State/L=City/O=Organization/CN=blinddate.local"
sudo chmod 600 /etc/blinddate/ca.key

# Configure Mosquitto for auth and TLS
sudo bash -c "cat > /etc/mosquitto/conf.d/blinddate.conf << EOF
listener 8883
cafile /etc/blinddate/ca.crt
certfile /etc/blinddate/ca.crt
keyfile /etc/blinddate/ca.key
require_certificate false
use_identity_as_username false

password_file /etc/blinddate/mqtt.conf
allow_anonymous false

log_dest syslog
log_type error
log_type warning
log_type notice
log_type information
EOF"

# Generate TOTP secret for admin
TOTP_SECRET=$(python3 -c "import pyotp; print(pyotp.random_base32())")
echo "TOTP Secret: $TOTP_SECRET"
echo "Scan this QR code with your authenticator app:"
python3 -c "import pyotp, qrcode; totp = pyotp.TOTP('$TOTP_SECRET'); qr = qrcode.QRCode(); qr.add_data(totp.provisioning_uri('Blind Date Admin', issuer_name='BlindDate')); qr.print_ascii()"

# Store secrets in .env
cd raspberry_pi_server
cat > .env << EOF
MQTT_USER=$MQTT_USER
MQTT_PASS=$MQTT_PASS
MQTT_CA_CERT=/etc/blinddate/ca.crt
TOTP_SECRET=$TOTP_SECRET
SECRET_KEY=$(openssl rand -hex 32)
FLASK_ENV=production
DATABASE_URL=sqlite:////var/lib/blinddate/sessions.db
BACKEND=real
HAPTIC_MODE=false
EOF
chmod 600 .env
cd ..

# Enable Mosquitto
sudo systemctl enable mosquitto
sudo systemctl restart mosquitto

# Create systemd service
cat > blinddate.service << EOF
[Unit]
Description=Blind Date with Bandwidth Demo
After=network.target mosquitto.service

[Service]
Type=simple
User=pi
WorkingDirectory=/home/pi/blind-date-with-bandwidth/raspberry_pi_server
Environment=PATH=/usr/local/bin:/usr/bin:/bin
EnvironmentFile=/home/pi/blind-date-with-bandwidth/raspberry_pi_server/.env
ExecStart=/usr/bin/python3 main.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

sudo mv blinddate.service /etc/systemd/system/
sudo systemctl enable blinddate

echo "Installation complete. Run ./start_demo.sh to begin."