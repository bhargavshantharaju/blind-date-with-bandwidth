"""
Event bus for real-time WebSocket architecture.
Central event publisher/subscriber for all demo components.
"""

import asyncio
import json
import logging
from dataclasses import dataclass, field, asdict
from typing import Callable, List, Dict, Any, Type
from datetime import datetime
from collections import deque
from enum import Enum

logger = logging.getLogger(__name__)

class EventType(Enum):
    """All event types in the system."""
    STATION_ONLINE = "station_online"
    STATION_OFFLINE = "station_offline"
    STATION_LOCKED = "station_locked"
    MATCHED = "matched"
    MISMATCH = "mismatch"
    SESSION_STARTED = "session_started"
    SESSION_ACTIVE = "session_active"
    SESSION_TIMEOUT = "session_timeout"
    AUDIO_STARTED = "audio_started"
    AUDIO_STOPPED = "audio_stopped"
    STATE_CHANGED = "state_changed"
    SYSTEM_ERROR = "system_error"
    HEARTBEAT = "heartbeat"


@dataclass
class Event:
    """Base event class."""
    type: EventType
    timestamp: float = field(default_factory=lambda: datetime.utcnow().timestamp())
    session_id: str = ""
    
    def to_json(self) -> str:
        """Serialize to JSON for WebSocket transmission."""
        return json.dumps({
            'type': self.type.value,
            'timestamp': self.timestamp,
            'session_id': self.session_id,
            'data': {k: v for k, v in asdict(self).items() 
                    if k not in ['type', 'timestamp', 'session_id']}
        })


@dataclass
class StationOnlineEvent(Event):
    """Station joined network."""
    station_id: str = ""
    
    def __post_init__(self):
        self.type = EventType.STATION_ONLINE


@dataclass
class StationOfflineEvent(Event):
    """Station left or lost connection."""
    station_id: str = ""
    
    def __post_init__(self):
        self.type = EventType.STATION_OFFLINE


@dataclass
class StationLockedEvent(Event):
    """Station locked on a track."""
    station_id: str = ""
    track_id: int = 0
    
    def __post_init__(self):
        self.type = EventType.STATION_LOCKED


@dataclass
class MatchedEvent(Event):
    """Both stations matched on same track."""
    track_id: int = 0
    sync_time_ms: int = 0
    
    def __post_init__(self):
        self.type = EventType.MATCHED


@dataclass
class MismatchEvent(Event):
    """Stations locked on different tracks."""
    station_a_track: int = 0
    station_b_track: int = 0
    
    def __post_init__(self):
        self.type = EventType.MISMATCH


@dataclass
class SessionTimeoutEvent(Event):
    """Session timer expired."""
    duration_ms: int = 0
    
    def __post_init__(self):
        self.type = EventType.SESSION_TIMEOUT


@dataclass
class AudioStartedEvent(Event):
    """Audio bridging started."""
    audio_device_a: int = 0
    audio_device_b: int = 0
    
    def __post_init__(self):
        self.type = EventType.AUDIO_STARTED


@dataclass
class StateChangedEvent(Event):
    """Demo state machine changed state."""
    old_state: str = ""
    new_state: str = ""
    
    def __post_init__(self):
        self.type = EventType.STATE_CHANGED


class EventBus:
    """
    Central event bus with asyncio support.
    Allows components to publish events and subscribers to listen.
    Maintains event history for late-joining connections.
    """
    
    def __init__(self, max_history=100):
        self.subscribers: Dict[EventType, List[Callable]] = {}
        self.event_history = deque(maxlen=max_history)
        self.lock = asyncio.Lock()
    
    def subscribe(self, event_type: EventType, callback: Callable):
        """Subscribe to an event type."""
        if event_type not in self.subscribers:
            self.subscribers[event_type] = []
        self.subscribers[event_type].append(callback)
        logger.info(f"Subscriber registered for {event_type.value}")
    
    def unsubscribe(self, event_type: EventType, callback: Callable):
        """Unsubscribe from an event type."""
        if event_type in self.subscribers:
            self.subscribers[event_type].remove(callback)
    
    async def publish(self, event: Event):
        """Publish an event to all subscribers."""
        async with self.lock:
            # Store in history
            self.event_history.append(event)
            logger.debug(f"Event published: {event.type.value}")
            
            # Notify subscribers
            if event.type in self.subscribers:
                for callback in self.subscribers[event.type]:
                    if asyncio.iscoroutinefunction(callback):
                        await callback(event)
                    else:
                        callback(event)
    
    async def publish_broadcast(self, event: Event, broadcast_fn: Callable):
        """Publish event and broadcast via WebSocket."""
        await self.publish(event)
        await broadcast_fn(event.to_json())
    
    def get_history(self) -> List[Dict[str, Any]]:
        """Get event history as list of dicts."""
        return [json.loads(e.to_json()) for e in self.event_history]
    
    def get_history_json(self) -> str:
        """Get event history as JSON string."""
        return json.dumps(self.get_history())


# Global event bus instance
event_bus = EventBus()


def create_event(event_type: EventType, **kwargs) -> Event:
    """Factory function to create typed events."""
    event_class_map = {
        EventType.STATION_ONLINE: StationOnlineEvent,
        EventType.STATION_OFFLINE: StationOfflineEvent,
        EventType.STATION_LOCKED: StationLockedEvent,
        EventType.MATCHED: MatchedEvent,
        EventType.MISMATCH: MismatchEvent,
        EventType.SESSION_TIMEOUT: SessionTimeoutEvent,
        EventType.AUDIO_STARTED: AudioStartedEvent,
        EventType.STATE_CHANGED: StateChangedEvent,
    }
    
    event_class = event_class_map.get(event_type, Event)
    return event_class(**kwargs)


# Example usage in components:
"""
# In matcher.py:
from events import event_bus, create_event, EventType

async def handle_match(station_a_track, station_b_track, sync_time_ms):
    event = create_event(
        EventType.MATCHED,
        track_id=station_a_track,
        sync_time_ms=sync_time_ms,
        session_id=current_session_id
    )
    await event_bus.publish(event)

# In dashboard app:
from events import event_bus

@socketio.on('connect')
def on_connect():
    # Send event history to newly connected client
    history = event_bus.get_history()
    emit('event_history', history)

# Setup event broadcasting
async def broadcast_event(message):
    socketio.emit('event', json.loads(message), to=request.sid, broadcast=True)

# Subscribe matcher to event bus
event_bus.subscribe(EventType.MATCHED, lambda e: logger.info(f"Match: {e}"))
"""
