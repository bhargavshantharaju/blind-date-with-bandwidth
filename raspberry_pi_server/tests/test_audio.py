import pytest
from unittest.mock import patch, Mock
from audio import AudioHandler
import os

def test_audio_handler_init():
    config = {'audio': {'device_a': 1, 'device_b': 2}}
    with patch('sounddevice.InputStream'), patch('sounddevice.OutputStream'):
        handler = AudioHandler(config)
        assert handler.config == config

def test_generate_clips():
    config = {'audio': {'device_a': 1, 'device_b': 2}}
    with patch('sounddevice.InputStream'), patch('sounddevice.OutputStream'):
        handler = AudioHandler(config)
        # Check if clips are generated
        assert os.path.exists('audio_clips/success.wav')

@patch('sounddevice.play')
@patch('sounddevice.wait')
def test_play_wav(mock_wait, mock_play):
    config = {'audio': {'device_a': 1, 'device_b': 2}}
    with patch('sounddevice.InputStream'), patch('sounddevice.OutputStream'):
        handler = AudioHandler(config)
        handler.play_wav('audio_clips/success.wav', 1)
        mock_play.assert_called_once()