from flask import Flask, render_template, jsonify, request
from flask_socketio import SocketIO, emit
from flask_talisman import Talisman
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
import pyotp
import json
import time
import os
from dotenv import load_dotenv
from typing import Dict, Any

load_dotenv()

app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev-secret-key')
socketio = SocketIO(app, cors_allowed_origins="*")

# Security
talisman = Talisman(app, content_security_policy=None)  # Customize CSP as needed
limiter = Limiter(app, key_func=get_remote_address)

totp = pyotp.TOTP(os.getenv('TOTP_SECRET'))

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
@limiter.limit("10 per minute")
def admin_reset():
    token = request.headers.get('X-TOTP')
    if not token or not totp.verify(token):
        return jsonify({'error': 'Invalid TOTP'}), 401
    reset_system()
    return jsonify({'status': 'reset'})

@app.route('/admin/config', methods=['POST'])
@limiter.limit("10 per minute")
def admin_config():
    token = request.headers.get('X-TOTP')
    if not token or not totp.verify(token):
        return jsonify({'error': 'Invalid TOTP'}), 401
    # Placeholder for config update
    return jsonify({'status': 'config updated'})

@app.route('/api/v1/admin/force-recover', methods=['POST'])
@limiter.limit("10 per minute")
def force_recover():
    """Manually trigger state restoration from database."""
    token = request.headers.get('Authorization', '').replace('Bearer ', '')
    if not totp.verify(token):
        return jsonify({'error': 'Invalid TOTP'}), 401
    
    # In a real implementation, restore state from database
    return jsonify({'status': 'recovery_initiated'})

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