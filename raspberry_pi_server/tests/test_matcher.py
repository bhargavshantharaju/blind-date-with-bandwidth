import pytest
from unittest.mock import Mock, patch
from matcher import Matcher, State

def test_matcher_initial_state():
    matcher = Matcher({}, lambda e, d: None)
    assert matcher.state == State.IDLE

def test_matcher_lock_and_match():
    events = []
    matcher = Matcher({'session': {'duration': 90}}, lambda e, d: events.append((e, d)))

    matcher.handle_lock('A', 1, 1000)
    assert matcher.state == State.LOCKED_A

    matcher.handle_lock('B', 1, 1000)
    assert matcher.state == State.MATCHED
    assert ('matched', {'track': 1}) in events

def test_matcher_mismatch():
    events = []
    matcher = Matcher({}, lambda e, d: events.append((e, d)))

    matcher.handle_lock('A', 1, 1000)
    matcher.handle_lock('B', 2, 1000)
    assert matcher.state == State.SCANNING
    assert ('mismatch', {}) in events

def test_matcher_timeout():
    events = []
    matcher = Matcher({'session': {'duration': 0}}, lambda e, d: events.append((e, d)))

    matcher.handle_lock('A', 1, 1000)
    matcher.handle_lock('B', 1, 1000)
    matcher.check_timeout()
    assert ('timeout', {}) in events