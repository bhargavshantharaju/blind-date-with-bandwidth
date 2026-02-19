from flask import Flask, jsonify
import json
import time

app = Flask(__name__)

# Global state
state = {
    'station_a': 'Idle',
    'station_b': 'Idle',
    'track_a': 0,
    'track_b': 0,
    'sync_count': 0,
    'avg_sync_time': 0.0,
    'countdown': 0,
    'session_start': 0
}

@app.route('/')
def dashboard():
    html = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Blind Date Dashboard</title>
        <style>
            body { font-family: Arial, sans-serif; background-color: #f0f0f0; text-align: center; padding: 20px; }
            h1 { color: #333; font-size: 48px; }
            .stats { font-size: 36px; margin: 20px; }
            .state { font-size: 48px; margin: 20px; }
            .idle { color: gray; }
            .scanning { color: blue; }
            .matched { color: green; }
            .countdown { font-size: 72px; color: red; }
        </style>
        <script>
            function update() {
                fetch('/api/state').then(response => response.json()).then(data => {
                    document.getElementById('station_a').innerText = 'Station A: ' + data.station_a;
                    document.getElementById('station_a').className = 'state ' + data.station_a.toLowerCase();
                    document.getElementById('station_b').innerText = 'Station B: ' + data.station_b;
                    document.getElementById('station_b').className = 'state ' + data.station_b.toLowerCase();
                    document.getElementById('track_a').innerText = 'Track A: ' + data.track_a;
                    document.getElementById('track_b').innerText = 'Track B: ' + data.track_b;
                    document.getElementById('sync_count').innerText = 'Sync Count: ' + data.sync_count;
                    document.getElementById('avg_time').innerText = 'Avg Sync Time: ' + data.avg_sync_time.toFixed(2) + ' s';
                    document.getElementById('countdown').innerText = data.countdown > 0 ? data.countdown + ' s' : '';
                });
            }
            setInterval(update, 1000);
            update();
        </script>
    </head>
    <body>
        <h1>Blind Date with Bandwidth</h1>
        <div id="station_a" class="state idle">Station A: Idle</div>
        <div id="station_b" class="state idle">Station B: Idle</div>
        <div class="stats" id="track_a">Track A: 0</div>
        <div class="stats" id="track_b">Track B: 0</div>
        <div class="stats" id="sync_count">Sync Count: 0</div>
        <div class="stats" id="avg_time">Avg Sync Time: 0.00 s</div>
        <div id="countdown" class="countdown"></div>
    </body>
    </html>
    """
    return html

@app.route('/api/state')
def get_state():
    global state
    if state['countdown'] > 0:
        state['countdown'] = max(0, 30 - (time.time() - state['session_start']))
    return jsonify(state)

def update_state(key, value):
    global state
    state[key] = value