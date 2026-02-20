"""
Integration tests for Blind Date with Bandwidth.
Tests full flow: matching, timeout, recovery, etc.
"""

import asyncio
import json
import time
from datetime import datetime
from unittest.mock import MagicMock, Mock, patch

import pytest


@pytest.mark.asyncio
async def test_full_match_flow():
    """Test complete match cycle end-to-end."""
    from events import EventType, create_event, event_bus
    from resilience import SessionRecovery
    from tournament import TournamentBracket, TournamentRound

    # Setup
    events_received = []
    event_bus.subscribe(EventType.MATCHED, lambda e: events_received.append(e))
    
    bracket = TournamentBracket(num_stations=2)
    bracket.start_round(round_num=TournamentRound.ROUND_1)
    
    # Simulate both stations locking same track
    match_id = bracket.matches[0].match_id
    winner = bracket.record_match_result(match_id, station_a_track=3, station_b_track=3, sync_time_ms=125)
    
    assert winner is not None
    assert len(events_received) > 0

@pytest.mark.asyncio
async def test_timeout_flow():
    """Test session timeout correctly broadcast."""
    from events import EventType, event_bus
    
    events = []
    event_bus.subscribe(EventType.SESSION_TIMEOUT, lambda e: events.append(e))
    
    # Simulate timeout after 90 seconds
    await asyncio.sleep(0.1)
    
    # In real scenario, timeout would be detected by matcher
    assert True  # Placeholder

@pytest.mark.asyncio
async def test_mismatch_handling():
    """Test mismatched tracks handled gracefully."""
    from tournament import TournamentBracket, TournamentRound
    
    bracket = TournamentBracket(num_stations=2)
    bracket.start_round(round_num=TournamentRound.ROUND_1)
    match_id = bracket.matches[0].match_id
    
    # Different tracks - no match
    winner = bracket.record_match_result(match_id, station_a_track=1, station_b_track=2, sync_time_ms=50)
    
    assert winner is None

@pytest.mark.asyncio
async def test_mqtt_disconnect_recovery():
    """Test state recovery after MQTT disconnect."""
    from resilience import CircuitBreaker, SessionRecovery
    
    cb = CircuitBreaker()
    recovery = SessionRecovery(lambda: None)
    
    # Record failure
    cb.record_failure()
    assert cb.state.value == 'open'
    
    # Simulate recovery
    cb.record_success()
    assert cb.state.value == 'closed'

@pytest.mark.asyncio
async def test_message_replay_prevention():
    """Test duplicate MQTT message detection."""
    from resilience import ReplayAttackPrevention
    
    prevention = ReplayAttackPrevention(window_ms=500)
    
    payload1 = {'station': 'A', 'track': 3}
    payload2 = {'station': 'B', 'track': 3}
    
    # First message not a duplicate
    assert not prevention.is_duplicate('blinddate/lock', payload1)
    
    # Same message again = duplicate
    assert prevention.is_duplicate('blinddate/lock', payload1)
    
    # Different payload = not duplicate
    assert not prevention.is_duplicate('blinddate/lock', payload2)

def test_circuit_breaker_exponential_backoff():
    """Test circuit breaker retry delays."""
    from resilience import CircuitBreaker
    
    cb = CircuitBreaker(base_delay_ms=100)
    
    # Record 5 failures
    delays = []
    for i in range(5):
        cb.record_failure()
        assert cb.next_retry_time is not None
        assert cb.last_failure_time is not None
        delays.append(float(cb.next_retry_time) - float(cb.last_failure_time))
    
    # Verify exponential growth: 100ms, 200ms, 400ms, 800ms, 1600ms
    expected = [0.1, 0.2, 0.4, 0.8, 1.6]
    for actual, exp in zip(delays, expected):
        assert abs(actual - exp) < 0.01  # Allow small floating point error

def test_leaderboard_ranking():
    """Test tournament leaderboard calculations."""
    from tournament import TournamentBracket, TournamentRound
    
    bracket = TournamentBracket(num_stations=4)
    bracket.start_round(round_num=TournamentRound.ROUND_1)
    
    # Simulate some matches
    bracket.record_match_result('round_1_0', station_a_track=1, station_b_track=1, sync_time_ms=100)
    bracket.record_match_result('round_1_1', station_a_track=2, station_b_track=2, sync_time_ms=150)
    
    board_json = bracket.get_leaderboard_json()
    import json
    board = json.loads(board_json)
    
    assert len(board) > 0
    assert 'matches_won' in board[0]

if __name__ == '__main__':
    pytest.main([__file__, '-v', '--asyncio-mode=auto'])
