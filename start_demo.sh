#!/bin/bash

echo "Starting Blind Date with Bandwidth Demo..."

# Start Mosquitto
echo "Starting Mosquitto..."
sudo systemctl start mosquitto
sleep 2

# Run self test
echo "Running self test..."
python3 self_test.py
if [ $? -ne 0 ]; then
    echo "Self test failed. Aborting."
    exit 1
fi

# Generate audio files if not exist
if [ ! -f audio/success.wav ]; then
    echo "Generating audio files..."
    cd audio
    python3 generate_audio.py
    cd ..
fi

# Launch main
echo "Launching main server..."
python3 main.py &
MAIN_PID=$!

# Wait a bit
sleep 5

# Get IP
IP=$(hostname -I | awk '{print $1}')
echo "Demo started successfully!"
echo "Dashboard: http://$IP:5000"
echo "Press Ctrl+C to stop."

# Wait for main
wait $MAIN_PID