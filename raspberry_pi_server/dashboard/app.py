from flask import Flask, render_template, jsonify, request
from flask_socketio import SocketIO, emit
import json
import time
from typing import Dict, Any

app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins="*")

# Global state
state: Dict[str, Any] = {
    'station_a': {'state': 'idle', 'track': 0, 'online': False},
    'station_b': {'state': 'idle', 'track': 0, 'online': False},
    'sync_count': 0,
    'avg_sync_time': 0.0,
    'current_state': 'idle',
    'countdown': 0,
    'events': []
}

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/status')
def get_status():
    return jsonify(state)

@app.route('/api/stats')
def get_stats():
    return jsonify({
        'sync_count': state['sync_count'],
        'avg_sync_time': state['avg_sync_time']
    })

@app.route('/admin/reset', methods=['POST'])
def admin_reset():
    token = request.headers.get('Authorization')
    if token != f"Bearer {app.config.get('ADMIN_TOKEN', 'changeme')}":
        return jsonify({'error': 'Unauthorized'}), 401
    reset_system()
    return jsonify({'status': 'reset'})

@app.route('/admin/config', methods=['POST'])
def admin_config():
    token = request.headers.get('Authorization')
    if token != f"Bearer {app.config.get('ADMIN_TOKEN', 'changeme')}":
        return jsonify({'error': 'Unauthorized'}), 401
    # Placeholder for config update
    return jsonify({'status': 'config updated'})

@socketio.on('connect')
def handle_connect():
    emit('status_update', state)

def update_state(updates: Dict[str, Any]):
    global state
    state.update(updates)
    socketio.emit('status_update', state)

def add_event(event: str, data: Dict[str, Any]):
    state['events'].append({
        'time': time.time(),
        'event': event,
        'data': data
    })
    if len(state['events']) > 50:
        state['events'] = state['events'][-50:]
    update_state({})

def reset_system():
    global state
    state = {
        'station_a': {'state': 'idle', 'track': 0, 'online': False},
        'station_b': {'state': 'idle', 'track': 0, 'online': False},
        'sync_count': 0,
        'avg_sync_time': 0.0,
        'current_state': 'idle',
        'countdown': 0,
        'events': []
    }
    update_state(state)