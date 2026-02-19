import paho.mqtt.client as mqtt
import time
import threading
import json
from audio import AudioHandler
from dashboard import app, update_state

# MQTT settings
MQTT_BROKER = "localhost"
MQTT_PORT = 1883
LOCK_TOPIC = "blinddate/lock"
STATUS_TOPIC = "blinddate/status"

# Audio
audio = AudioHandler()

# State
stations = {'A': {'state': 'Idle', 'track': 0, 'timestamp': 0},
            'B': {'state': 'Idle', 'track': 0, 'timestamp': 0}}
sync_count = 0
avg_sync_time = 0.0
session_active = False
session_start = 0

def on_connect(client, userdata, flags, rc):
    print("Connected to MQTT")
    client.subscribe(LOCK_TOPIC)

def on_message(client, userdata, msg):
    global sync_count, avg_sync_time, session_active, session_start
    try:
        payload = json.loads(msg.payload.decode())
        station = payload['station']
        track = payload['track']
        timestamp = payload['timestamp']

        print(f"Station {station} locked on track {track}")

        stations[station]['state'] = 'Scanning'
        stations[station]['track'] = track
        stations[station]['timestamp'] = timestamp
        update_state(f'station_{station.lower()}', 'Scanning')
        update_state(f'track_{station.lower()}', track)

        # Check match
        if stations['A']['track'] == stations['B']['track'] and stations['A']['track'] != 0:
            # Match
            sync_count += 1
            sync_time = (timestamp - min(stations['A']['timestamp'], stations['B']['timestamp'])) / 1000.0
            avg_sync_time = (avg_sync_time * (sync_count - 1) + sync_time) / sync_count

            print("MATCH!")
            session_active = True
            session_start = time.time()
            update_state('sync_count', sync_count)
            update_state('avg_sync_time', avg_sync_time)
            update_state('countdown', 30)
            update_state('session_start', session_start)

            # Stop music, play success, start bridging
            threading.Thread(target=handle_match, daemon=True).start()

            # Publish status
            for s in ['A', 'B']:
                status_msg = json.dumps({'station': s, 'matched': True})
                client.publish(STATUS_TOPIC, status_msg)
        else:
            # Publish not matched
            for s in ['A', 'B']:
                status_msg = json.dumps({'station': s, 'matched': False})
                client.publish(STATUS_TOPIC, status_msg)
    except Exception as e:
        print(f"Error processing message: {e}")

def handle_match():
    global session_active
    # Stop music (assume playing in another thread)
    # Play success.wav to both
            audio.play_wav('audio/success.wav', audio.device_a_out)
            audio.play_wav('audio/success.wav', audio.device_b_out)
    # Start bridging
    audio.start_bridging()

    # Wait 30 seconds
    time.sleep(30)

    # Stop bridging
    audio.stop_bridging()
    session_active = False

    # Reset
    reset_system()

def reset_system():
    global session_active
    for s in stations:
        stations[s]['state'] = 'Idle'
        stations[s]['track'] = 0
        update_state(f'station_{s.lower()}', 'Idle')
        update_state(f'track_{s.lower()}', 0)
        update_state('countdown', 0)

def play_tracks():
    tracks = [1, 2, 3, 4, 5]  # Track IDs
    while True:
        for track in tracks:
            if session_active:
                time.sleep(1)
                continue
            print(f"Playing track {track}")
            # Play to both stations
            audio.play_wav(f'audio/track{track}.wav', audio.device_a_out)
            audio.play_wav(f'audio/track{track}.wav', audio.device_b_out)
            time.sleep(1)  # Short pause

if __name__ == "__main__":
    audio.list_devices()  # For debugging

    client = mqtt.Client()
    client.on_connect = on_connect
    client.on_message = on_message
    client.connect(MQTT_BROKER, MQTT_PORT, 60)

    # Start track playing
    threading.Thread(target=play_tracks, daemon=True).start()

    # Start MQTT
    client.loop_start()

    # Start Flask
    app.run(host='0.0.0.0', port=5000, debug=False)