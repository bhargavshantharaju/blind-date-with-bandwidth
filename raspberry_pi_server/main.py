try:
    import yaml
except ImportError:
    raise ImportError("PyYAML required: pip install PyYAML")
import threading
import time
import os
from dotenv import load_dotenv  # noqa: E402
from mqtt_handler import MQTTHandler
from matcher import Matcher
from audio import AudioHandler
from dashboard.app import app, socketio, update_state, add_event
from models import validate_mqtt_payload

load_dotenv()

def load_config():
    with open('config.yaml', 'r') as f:
        return yaml.safe_load(f)

def on_mqtt_message(topic: str, payload: dict):
    validated = validate_mqtt_payload(topic, payload)
    if validated is None:
        return

    if topic == 'blinddate/lock':
        matcher.handle_lock(validated.station, validated.track, validated.timestamp)
    elif topic == 'blinddate/heartbeat':
        # Handle heartbeat
        add_event('heartbeat', {'station': validated.station})

def on_matcher_event(event: str, data: dict):
    if event == 'matched':
        audio.play_success_and_bridge()
        add_event('matched', data)
    elif event == 'state_change':
        update_state({'current_state': data['state']})
        add_event('state_change', data)
    elif event == 'reset':
        audio.stop_bridging()
        add_event('reset', {})

if __name__ == "__main__":
    config = load_config()
    
    # Initialize components
    mqtt_handler = MQTTHandler(config, on_mqtt_message)
    matcher = Matcher(config, on_matcher_event)
    audio = AudioHandler(config)
    
    # Connect MQTT
    mqtt_handler.connect()
    
    # Start background threads
    def timeout_checker():
        while True:
            matcher.check_timeout()
            time.sleep(1)
    
    threading.Thread(target=timeout_checker, daemon=True).start()
    threading.Thread(target=audio.play_tracks_loop, daemon=True).start()
    
    # Start Flask
    socketio.run(app, host='0.0.0.0', port=5000, debug=config.get('debug', False))