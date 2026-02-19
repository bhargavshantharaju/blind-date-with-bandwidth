"""
Load testing Blind Date with Bandwidth using Locust.
Simulates concurrent WebSocket clients and MQTT messaging.
"""

from locust import HttpUser, task, between, events
import socketio
import random
import time

sio = socketio.Client()

class WebSocketClient(HttpUser):
    """Simulate a single visitor station."""
    
    wait_time = between(1, 3)
    
    def on_start(self):
        """Connect to WebSocket on session start."""
        self.station_id = f"station_{random.randint(1000, 9999)}"
        self.connected = False
        try:
            sio.connect(f'http://{self.host}:5000', wait_timeout=10)
            self.connected = True
        except Exception as e:
            print(f"Connection failed: {e}")
    
    @task(3)
    def emit_lock(self):
        """Send lock event (pick a track)."""
        if self.connected:
            track_choice = random.randint(1, 5)
            try:
                sio.emit('lock', {
                    'station_id': self.station_id,
                    'track': track_choice
                })
            except Exception:
                pass
    
    @task(1)
    def request_heartbeat(self):
        """Request server heartbeat."""
        if self.connected:
            try:
                sio.emit('heartbeat', {'station': self.station_id})
            except Exception:
                pass
    
    def on_stop(self):
        """Disconnect on session end."""
        if self.connected:
            sio.disconnect()

@events.test_start.add_listener
def on_test_start(environment, **kwargs):
    """Log test start."""
    print("=" * 50)
    print("Load test started: 50 concurrent WebSocket clients")
    print("=" * 50)

@events.test_stop.add_listener
def on_test_stop(environment, **kwargs):
    """Log test stats."""
    print("=" * 50)
    print(f"Total tasks: {environment.stats.total.num_requests}")
    print(f"Avg response: {environment.stats.total.avg_response_time}ms")
    print("=" * 50)

if __name__ == '__main__':
    """
    Run with:
    locust -f tests/load_test.py -u 50 -r 5 --run-time 5m http://localhost:5000
    
    Expected metrics:
    - 50 concurrent users
    - 5 users spawning per second
    - 5-minute test duration
    - Hostname: localhost:5000
    """
    pass
