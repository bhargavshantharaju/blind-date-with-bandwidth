import threading
import time
from enum import Enum
from typing import Dict, Callable, Any

class State(Enum):
    IDLE = "idle"
    SCANNING = "scanning"
    LOCKED_A = "locked_a"
    LOCKED_B = "locked_b"
    MATCHED = "matched"

class Matcher:
    """State machine for matching logic."""

    def __init__(self, config: Dict[str, Any], on_event: Callable[[str, Dict[str, Any]], None]):
        self.config = config
        self.on_event = on_event
        self.state = State.IDLE
        self.stations: Dict[str, Dict[str, Any]] = {'A': {}, 'B': {}}
        self.lock = threading.Lock()
        self.session_start = 0

    def handle_lock(self, station: str, track: int, timestamp: int):
        with self.lock:
            self.stations[station] = {'track': track, 'timestamp': timestamp}
            self._update_state()

    def _update_state(self):
        a_locked = 'track' in self.stations['A']
        b_locked = 'track' in self.stations['B']

        if not a_locked and not b_locked:
            new_state = State.IDLE
        elif a_locked and not b_locked:
            new_state = State.LOCKED_A
        elif not a_locked and b_locked:
            new_state = State.LOCKED_B
        else:
            if self.stations['A']['track'] == self.stations['B']['track']:
                new_state = State.MATCHED
                self.session_start = time.time()
                self.on_event('matched', {'track': self.stations['A']['track']})
            else:
                new_state = State.SCANNING
                self.on_event('mismatch', {})

        if new_state != self.state:
            self.state = new_state
            self.on_event('state_change', {'state': self.state.value})

    def check_timeout(self):
        with self.lock:
            if self.state == State.MATCHED:
                if time.time() - self.session_start > self.config['session']['duration']:
                    self.reset()
                    self.on_event('timeout', {})

    def reset(self):
        with self.lock:
            self.stations = {'A': {}, 'B': {}}
            self.state = State.IDLE
            self.on_event('reset', {})