import os
import subprocess
import sys
import time

import paho.mqtt.client as mqtt
from audio import AudioHandler


def check_mosquitto():
    try:
        result = subprocess.run(['systemctl', 'is-active', 'mosquitto'], capture_output=True, text=True)
        return result.returncode == 0
    except:
        return False

def test_mqtt():
    def on_connect(client, userdata, flags, rc):
        if rc == 0:
            client.subscribe("test/topic")
            client.publish("test/topic", "test")

    def on_message(client, userdata, msg):
        userdata['received'] = True

    client = mqtt.Client()
    received = {'received': False}
    client.on_connect = on_connect
    client.on_message = on_message
    client.userdata_set(received)
    try:
        client.connect("localhost", 1883, 5)
        client.loop_start()
        time.sleep(2)
        client.loop_stop()
        return received['received']
    except:
        return False

def test_audio_devices():
    try:
        audio = AudioHandler(config={
            'audio': {'device_a': 1, 'device_b': 2},
            'session': {'duration': 10, 'num_tracks': 5}
        })
        return True
    except Exception as e:
        print(f"Audio device error: {e}")
        return False

def test_play_success():
    try:
        audio = AudioHandler(config={
            'audio': {'device_a': 1, 'device_b': 2},
            'session': {'duration': 10, 'num_tracks': 5}
        })
        audio.play_wav('audio/success.wav', audio.device_a_out)
        return True
    except Exception as e:
        print(f"Play success error: {e}")
        return False

def test_loopback():
    # Simple loopback: record and check if data is present
    try:
        audio = AudioHandler(config={
            'audio': {'device_a': 1, 'device_b': 2},
            'session': {'duration': 10, 'num_tracks': 5}
        })
        stream_in = audio.p.open(format=audio.format, channels=audio.channels, rate=audio.rate,
                                 input=True, input_device_index=audio.device_a_in, frames_per_buffer=audio.chunk)
        data = stream_in.read(audio.chunk)
        stream_in.stop_stream()
        stream_in.close()
        # Check if data has non-zero values
        import struct
        samples = struct.unpack('<' + 'h' * audio.chunk, data)
        return max(samples) > 100  # Some threshold
    except Exception as e:
        print(f"Loopback test error: {e}")
        return False

def main():
    tests = [
        ("Mosquitto running", check_mosquitto),
        ("MQTT pub/sub", test_mqtt),
        ("Audio devices", test_audio_devices),
        ("Play success.wav", test_play_success),
        ("Mic loopback", test_loopback)
    ]

    results = []
    for name, func in tests:
        print(f"Testing {name}...")
        result = func()
        results.append((name, result))
        print(f"{'PASS' if result else 'FAIL'}")

    print("\nSummary:")
    all_pass = True
    for name, result in results:
        status = "PASS" if result else "FAIL"
        print(f"{name}: {status}")
        if not result:
            all_pass = False

    if all_pass:
        print("All tests PASSED. Ready for demo.")
        return 0
    else:
        print("Some tests FAILED. Check setup.")
        return 1

if __name__ == "__main__":
    sys.exit(main())