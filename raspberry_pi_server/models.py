from pydantic import BaseModel, validator
from typing import Optional
import logging

logger = logging.getLogger(__name__)

class LockPayload(BaseModel):
    station: str
    track: int
    timestamp: int

    @validator('station')
    def station_must_be_valid(cls, v):
        if v not in ['A', 'B']:
            logger.warning(f"Rejected invalid station: {v}")
            raise ValueError('Station must be A or B')
        return v

    @validator('track')
    def track_must_be_valid(cls, v):
        if not (1 <= v <= 5):
            logger.warning(f"Rejected invalid track: {v}")
            raise ValueError('Track must be between 1 and 5')
        return v

class HeartbeatPayload(BaseModel):
    station: str
    timestamp: int

    @validator('station')
    def station_must_be_valid(cls, v):
        if v not in ['A', 'B']:
            logger.warning(f"Rejected invalid station: {v}")
            raise ValueError('Station must be A or B')
        return v

def validate_mqtt_payload(topic: str, payload: dict) -> Optional[BaseModel]:
    try:
        if topic == 'blinddate/lock':
            return LockPayload(**payload)
        elif topic == 'blinddate/heartbeat':
            return HeartbeatPayload(**payload)
        return None
    except Exception as e:
        logger.warning(f"Rejected malformed payload on {topic}: {payload} - {e}")
        return None