import os
import threading
import time
import wave
from typing import Optional

import numpy as np
import sounddevice as sd


class AudioHandler:
    """Handles audio playback and bridging using sounddevice."""

    def __init__(self, config: dict = None):
        if config is None:
            config = {
                'audio': {
                    'device_a': 1,
                    'device_b': 2,
                },
                'session': {'duration': 10, 'num_tracks': 5}
            }
        self.config = config
        self.chunk = 1024
        self.rate = 44100
        self.channels = 1
        self.bridging = False
        self.session_active = False
        self.streams: dict = {}
        
        # Audio device attributes
        self.device_a_out: int = int(config.get('audio', {}).get('device_a', 1))
        self.device_a_in: int = int(config.get('audio', {}).get('device_a', 1))
        self.device_b_out: int = int(config.get('audio', {}).get('device_b', 2))
        self.device_b_in: int = int(config.get('audio', {}).get('device_b', 2))
        self.format: int = 16  # 16-bit audio
        self.p = None  # PyAudio interface (optional)
        
        self._generate_clips()

    def _generate_clips(self):
        """Generate tone clips if not present."""
        clip_dir = 'audio_clips'
        os.makedirs(clip_dir, exist_ok=True)
        frequencies = [300, 400, 500, 600, 700]
        for i, freq in enumerate(frequencies, 1):
            path = os.path.join(clip_dir, f'track{i}.wav')
            if not os.path.exists(path):
                self._generate_tone(path, 10, freq)

        success_path = os.path.join(clip_dir, 'success.wav')
        if not os.path.exists(success_path):
            self._generate_tone(success_path, 0.5, 1000)

    def _generate_tone(self, filename: str, duration: float, frequency: float):
        """Generate a WAV tone file."""
        t = np.linspace(0, duration, int(self.rate * duration), False)
        tone = np.sin(frequency * 2 * np.pi * t)
        # Fade
        fade_len = int(self.rate * 0.01)
        tone[:fade_len] = tone[:fade_len] * np.linspace(0, 1, fade_len)
        tone[-fade_len:] = tone[-fade_len:] * np.linspace(1, 0, fade_len)
        tone = np.int16(tone * 32767)
        with wave.open(filename, 'w') as wav_file:
            wav_file.setnchannels(self.channels)
            wav_file.setsampwidth(2)
            wav_file.setframerate(self.rate)
            wav_file.writeframes(tone.tobytes())

    def play_wav(self, filename: str, device: int):
        """Play WAV file on specified device."""
        try:
            with wave.open(filename, 'rb') as wf:
                data = wf.readframes(wf.getnframes())
                sd.play(np.frombuffer(data, dtype=np.int16), samplerate=wf.getframerate(), device=device)
                sd.wait()
        except Exception as e:
            print(f"Error playing {filename}: {e}")

    def start_bridging(self):
        """Start audio bridging between stations."""
        if self.bridging:
            return
        self.bridging = True
        try:
            self.stream_a_in = sd.InputStream(device=self.config['audio']['device_a'], channels=self.channels, samplerate=self.rate, blocksize=self.chunk)
            self.stream_b_in = sd.InputStream(device=self.config['audio']['device_b'], channels=self.channels, samplerate=self.rate, blocksize=self.chunk)
            self.stream_a_out = sd.OutputStream(device=self.config['audio']['device_a'], channels=self.channels, samplerate=self.rate, blocksize=self.chunk)
            self.stream_b_out = sd.OutputStream(device=self.config['audio']['device_b'], channels=self.channels, samplerate=self.rate, blocksize=self.chunk)

            self.stream_a_in.start()
            self.stream_b_in.start()
            self.stream_a_out.start()
            self.stream_b_out.start()

            threading.Thread(target=self._bridge_a_to_b, daemon=True).start()
            threading.Thread(target=self._bridge_b_to_a, daemon=True).start()
        except Exception as e:
            print(f"Bridging start error: {e}")
            self.bridging = False

    def _bridge_a_to_b(self):
        while self.bridging:
            try:
                data, _ = self.stream_a_in.read(self.chunk)
                self.stream_b_out.write(data)
            except Exception as e:
                print(f"A to B error: {e}")
                break

    def _bridge_b_to_a(self):
        while self.bridging:
            try:
                data, _ = self.stream_b_in.read(self.chunk)
                self.stream_a_out.write(data)
            except Exception as e:
                print(f"B to A error: {e}")
                break

    def stop_bridging(self):
        """Stop audio bridging."""
        self.bridging = False
        time.sleep(0.1)
        for stream in [self.stream_a_in, self.stream_b_in, self.stream_a_out, self.stream_b_out]:
            if hasattr(self, stream.__name__ if hasattr(stream, '__name__') else 'stream'):
                try:
                    stream.stop()
                    stream.close()
                except:
                    pass

    def play_success_and_bridge(self):
        """Play success sound and start bridging for session duration."""
        self.session_active = True
        success_path = os.path.join('audio_clips', 'success.wav')
        threading.Thread(target=self.play_wav, args=(success_path, self.config['audio']['device_a']), daemon=True).start()
        threading.Thread(target=self.play_wav, args=(success_path, self.config['audio']['device_b']), daemon=True).start()
        time.sleep(0.5)  # Wait for success sound
        self.start_bridging()
        time.sleep(self.config['session']['duration'])
        self.stop_bridging()
        self.session_active = False

    def play_tracks_loop(self):
        """Loop playing tracks to stations."""
        tracks = list(range(1, self.config['session']['num_tracks'] + 1))
        while True:
            for track in tracks:
                if self.session_active:
                    time.sleep(1)
                    continue
                track_path = os.path.join('audio_clips', f'track{track}.wav')
                threading.Thread(target=self.play_wav, args=(track_path, self.config['audio']['device_a']), daemon=True).start()
                threading.Thread(target=self.play_wav, args=(track_path, self.config['audio']['device_b']), daemon=True).start()
                time.sleep(10)  # Track duration