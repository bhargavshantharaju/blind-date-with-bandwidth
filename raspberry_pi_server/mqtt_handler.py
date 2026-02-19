import paho.mqtt.client as mqtt
import json
import threading
import ssl
import os
from typing import Callable, Dict, Any

class MQTTHandler:
    """Handles MQTT communication with reconnect logic, TLS, and auth."""

    def __init__(self, config: Dict[str, Any], on_message: Callable[[str, Dict], None]):
        self.config = config
        self.on_message = on_message
        self.client = mqtt.Client()
        self.client.on_connect = self._on_connect
        self.client.on_message = self._on_message
        self.client.on_disconnect = self._on_disconnect
        self.client.will_set("blinddate/status", json.dumps({"status": "offline"}), retain=True)
        
        # TLS and auth
        self.client.tls_set(ca_certs=os.getenv('MQTT_CA_CERT', self.config['mqtt'].get('ca_cert')), tls_version=ssl.PROTOCOL_TLS)
        self.client.username_pw_set(os.getenv('MQTT_USER'), os.getenv('MQTT_PASS'))
        
        self.connected = False
        self.lock = threading.Lock()

    def _on_connect(self, client, userdata, flags, rc):
        if rc == 0:
            self.connected = True
            self.client.subscribe("blinddate/lock")
            self.client.subscribe("blinddate/heartbeat")
            self.client.subscribe("blinddate/status")
            print("MQTT connected")
        else:
            print(f"MQTT connection failed: {rc}")

    def _on_message(self, client, userdata, msg):
        try:
            payload = json.loads(msg.payload.decode())
            validated = self.on_message(msg.topic, payload)
            if validated is None:
                # Validation failed, payload rejected
                pass
        except json.JSONDecodeError:
            print(f"Invalid JSON: {msg.payload}")

    def _on_disconnect(self, client, userdata, rc):
        self.connected = False
        print("MQTT disconnected")

    def connect(self):
        try:
            self.client.connect(self.config['mqtt']['broker'], self.config['mqtt']['port'], 60)
            self.client.loop_start()
        except Exception as e:
            print(f"MQTT connect error: {e}")

    def publish(self, topic: str, payload: Dict[str, Any]):
        with self.lock:
            if self.connected:
                self.client.publish(topic, json.dumps(payload))
            else:
                print("MQTT not connected, message dropped")

    def disconnect(self):
        self.client.loop_stop()
        self.client.disconnect()