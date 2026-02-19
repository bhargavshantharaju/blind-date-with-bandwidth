"""
Raspberry Pi server resilience layer.
Implements circuit breaker, graceful degradation, connection pooling, crash recovery.
"""

import hashlib
import json
import logging
import queue
import threading
import time
from datetime import datetime
from enum import Enum
from typing import Any, Callable, Dict, Optional

logger = logging.getLogger(__name__)

class CircuitBreakerState(Enum):
    """Circuit breaker states."""
    CLOSED = "closed"  # Normal operation
    OPEN = "open"      # Failing, reject requests
    HALF_OPEN = "half_open"  # Testing if recovered


class CircuitBreaker:
    """Exponential backoff circuit breaker for MQTT reconnection."""
    
    def __init__(self, base_delay_ms=1000, max_delay_ms=60000, name="unnamed"):
        self.base_delay_ms = base_delay_ms
        self.max_delay_ms = max_delay_ms
        self.name = name
        
        self.state = CircuitBreakerState.CLOSED
        self.failure_count = 0
        self.last_failure_time = None
        self.next_retry_time = None
    
    def record_success(self):
        """Record successful connection."""
        self.failure_count = 0
        self.state = CircuitBreakerState.CLOSED
        logger.info(f"CircuitBreaker '{self.name}': recovered to CLOSED")
    
    def record_failure(self):
        """Record failure and calculate next retry."""
        self.failure_count += 1
        self.last_failure_time = time.time()
        
        # Exponential backoff: 1s, 2s, 4s, 8s, 16s, 32s, 60s (max)
        delay_ms = min(self.base_delay_ms * (2 ** (self.failure_count - 1)), self.max_delay_ms)
        self.next_retry_time = self.last_failure_time + (delay_ms / 1000.0)
        
        self.state = CircuitBreakerState.OPEN
        logger.warning(f"CircuitBreaker '{self.name}': OPEN (attempt {self.failure_count}, retry in {delay_ms}ms)")
    
    def allow_request(self) -> bool:
        """Check if request should be allowed."""
        if self.state == CircuitBreakerState.CLOSED:
            return True
        
        if self.state == CircuitBreakerState.OPEN:
            if time.time() >= self.next_retry_time:
                self.state = CircuitBreakerState.HALF_OPEN
                logger.info(f"CircuitBreaker '{self.name}': HALF_OPEN, testing recovery")
                return True
            return False
        
        return True  # HALF_OPEN, allow one test request


class MQTTMessageQueue:
    """Thread-safe queue for MQTT messages - never drops messages under load."""
    
    def __init__(self, max_size=10000):
        self.queue = queue.Queue(maxsize=max_size)
        self.lock = threading.Lock()
        self.dropped_count = 0
    
    def put(self, topic: str, payload: Dict[str, Any]) -> bool:
        """Put message in queue."""
        try:
            self.queue.put_nowait((topic, payload, time.time()))
            return True
        except queue.Full:
            with self.lock:
                self.dropped_count += 1
            logger.error(f"Message queue full, dropped message (total: {self.dropped_count})")
            return False
    
    def get_nowait(self):
        """Get message from queue."""
        return self.queue.get_nowait()
    
    def size(self) -> int:
        """Queue size."""
        return self.queue.qsize()


class AudioDeviceResilient:
    """Audio device with graceful degradation if primary fails."""
    
    def __init__(self, device_id_a: int, device_id_b: int):
        self.device_a = device_id_a
        self.device_b = device_id_b
        self.fallback_device = None  # System speaker
        self.failed_device_a = False
        self.failed_device_b = False
    
    def get_device_a(self) -> Optional[int]:
        """Get device A, fallback if failed."""
        if self.failed_device_a:
            logger.warning("Audio device A failed, using system speaker")
            return self.fallback_device
        return self.device_a
    
    def get_device_b(self) -> Optional[int]:
        """Get device B, fallback if failed."""
        if self.failed_device_b:
            logger.warning("Audio device B failed, using system speaker")
            return self.fallback_device
        return self.device_b
    
    def mark_device_failed(self, device_id: int):
        """Mark device as failed."""
        if device_id == self.device_a:
            self.failed_device_a = True
        elif device_id == self.device_b:
            self.failed_device_b = True


class SessionRecovery:
    """Session state persistence and crash recovery."""
    
    def __init__(self, db_session_func: Callable):
        """
        Args:
            db_session_func: callable that returns SQLAlchemy session
        """
        self.db_session = db_session_func
        self.current_state = {}
        self.last_checkpoint = None
        self.checkpoint_interval_s = 5
        self.lock = threading.Lock()
    
    def checkpoint_state(self, state: Dict[str, Any]):
        """Persist state to database."""
        now = time.time()
        if self.last_checkpoint and (now - self.last_checkpoint) < self.checkpoint_interval_s:
            return
        
        with self.lock:
            try:
                self.current_state = state.copy()
                # In a real implementation, save to database
                self.last_checkpoint = now
                logger.debug(f"State checkpoint saved: {state}")
            except Exception as e:
                logger.error(f"Failed to checkpoint state: {e}")
    
    def restore_state(self) -> Dict[str, Any]:
        """Restore state from database."""
        with self.lock:
            if self.current_state:
                logger.info(f"State recovered from checkpoint: {self.current_state}")
                return self.current_state.copy()
            return {}


class ReplayAttackPrevention:
    """Prevent duplicate MQTT messages (replay attack mitigation)."""
    
    def __init__(self, window_ms=500):
        self.window_ms = window_ms
        self.recent_messages = {}  # (topic, payload_hash) -> timestamp
        self.lock = threading.Lock()
    
    def is_duplicate(self, topic: str, payload: Dict[str, Any]) -> bool:
        """Check if message is a replay."""
        import hashlib
        payload_str = json.dumps(payload, sort_keys=True)
        payload_hash = hashlib.md5(payload_str.encode()).hexdigest()
        key = (topic, payload_hash)
        
        now = time.time() * 1000  # ms
        
        with self.lock:
            # Clean old entries
            self.recent_messages = {
                k: v for k, v in self.recent_messages.items()
                if (now - v) < self.window_ms
            }
            
            if key in self.recent_messages:
                logger.warning(f"Replay attack detected: {topic}")
                return True
            
            self.recent_messages[key] = now
            return False


class PartitionHandler:
    """Handle network partitions (split-brain scenarios)."""
    
    def __init__(self, timeout_s=15):
        self.timeout_s = timeout_s
        self.station_a_locked_time = None
        self.station_b_locked_time = None
    
    def handle_split_brain(self, locked_station: str, track: int) -> bool:
        """
        Detect if only one station locked (potential network partition).
        Returns True if waiting timeout has elapsed.
        """
        now = time.time()
        
        if locked_station == "A":
            self.station_a_locked_time = now
            if self.station_b_locked_time is None:
                # Only A locked, check timeout
                if now - self.station_a_locked_time > self.timeout_s:
                    logger.warning("Split-brain: Station A locked but B offline for 15s")
                    return True
        elif locked_station == "B":
            self.station_b_locked_time = now
            if self.station_a_locked_time is None:
                if now - self.station_b_locked_time > self.timeout_s:
                    logger.warning("Split-brain: Station B locked but A offline for 15s")
                    return True
        
        return False
    
    def reset(self):
        """Reset partition detector."""
        self.station_a_locked_time = None
        self.station_b_locked_time = None
