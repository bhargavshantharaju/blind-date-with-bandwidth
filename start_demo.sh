#!/bin/bash
set -e

echo "Starting Blind Date with Bandwidth Demo..."

# Check dependencies
echo "Checking dependencies..."
command -v mosquitto >/dev/null 2>&1 || { echo "Mosquitto not installed. Run ./install.sh first."; exit 1; }
python3 -c "import paho.mqtt.client" >/dev/null 2>&1 || { echo "Python dependencies not installed."; exit 1; }

# Start Mosquitto
echo "Starting Mosquitto..."
sudo systemctl start mosquitto
sleep 2

# Check MQTT
echo "Testing MQTT..."
python3 -c "
import paho.mqtt.client as mqtt
import time
def on_msg(client, userdata, msg): userdata[0] = True
client = mqtt.Client()
received = [False]
client.on_message = on_msg
client.userdata = received
client.connect('localhost', 1883, 5)
client.subscribe('test')
client.publish('test', 'ping')
client.loop_start()
time.sleep(1)
client.loop_stop()
if not received[0]: exit(1)
print('MQTT OK')
" || { echo "MQTT test failed."; exit 1; }

# Check audio devices
echo "Checking audio devices..."
aplay -l | grep -q "card" || { echo "No audio output devices found."; exit 1; }
arecord -l | grep -q "card" || { echo "No audio input devices found."; exit 1; }

# Run self test
echo "Running self test..."
python3 self_test.py || { echo "Self test failed."; exit 1; }

# Generate audio if needed
if [ ! -f audio_clips/success.wav ]; then
    echo "Generating audio files..."
    python3 -c "from audio import AudioHandler; AudioHandler({})"
fi

# Start demo
echo "Launching demo..."
python3 main.py &
MAIN_PID=$!

# Wait
sleep 5

# Get IP
IP=$(hostname -I | awk '{print $1}')
echo "Demo started successfully!"
echo "Dashboard: http://$IP:5000"
echo "Press Ctrl+C to stop."

# Wait
wait $MAIN_PID