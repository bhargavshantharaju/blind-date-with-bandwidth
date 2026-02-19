"""
Procedural audio generation module.
Generates distinctive, recognizable audio signatures without requiring pre-recorded files.
"""

import numpy as np
import wave
import os
from typing import Tuple

class ProceduralAudioGenerator:
    """Generate procedural audio tracks and effects."""
    
    def __init__(self, sample_rate=44100, duration=10):
        self.sample_rate = sample_rate
        self.duration = duration
        self.num_samples = int(sample_rate * duration)
    
    def _fade_envelope(self, audio: np.ndarray, fade_ms=50) -> np.ndarray:
        """Apply fade in/out to audio."""
        fade_samples = int(self.sample_rate * fade_ms / 1000)
        fade_in = np.linspace(0, 1, fade_samples)
        fade_out = np.linspace(1, 0, fade_samples)
        
        audio[:fade_samples] *= fade_in
        audio[-fade_samples:] *= fade_out
        return audio
    
    def _save_wav(self, audio: np.ndarray, filename: str):
        """Save audio array to WAV file."""
        os.makedirs(os.path.dirname(filename), exist_ok=True)
        audio_int = np.clip(audio * 32767, -32768, 32767).astype(np.int16)
        
        with wave.open(filename, 'w') as wav:
            wav.setnchannels(2)  # Stereo
            wav.setsampwidth(2)
            wav.setframerate(self.sample_rate)
            # Write stereo by duplicating mono channel
            stereo = np.column_stack([audio_int, audio_int])
            wav.writeframes(stereo.tobytes())
    
    def generate_track_1(self) -> np.ndarray:
        """Track 1: Rising sine sweep (100Hz → 800Hz over duration)."""
        t = np.linspace(0, self.duration, self.num_samples)
        freq_start, freq_end = 100, 800
        freq = freq_start + (freq_end - freq_start) * t / self.duration
        phase = 2 * np.pi * np.cumsum(freq) / self.sample_rate
        audio = np.sin(phase)
        return self._fade_envelope(audio)
    
    def generate_track_2(self) -> np.ndarray:
        """Track 2: Descending pentatonic arpeggio."""
        # Pentatonic notes: A4, G4, E4, D4, B3 (in Hz)
        notes = [440, 392, 330, 294, 247]
        notes_reversed = list(reversed(notes))  # Descending
        
        samples_per_note = self.num_samples // len(notes_reversed)
        audio = np.array([])
        
        for note_freq in notes_reversed:
            t = np.linspace(0, self.duration / len(notes_reversed), samples_per_note)
            note = np.sin(2 * np.pi * note_freq * t)
            audio = np.concatenate([audio, note])
        
        audio = audio[:self.num_samples]
        return self._fade_envelope(audio)
    
    def generate_track_3(self) -> np.ndarray:
        """Track 3: Rhythmic pulse pattern (morse-code style)."""
        t = np.linspace(0, self.duration, self.num_samples)
        freq = 600  # Base frequency
        carrier = np.sin(2 * np.pi * freq * t)
        
        # Morse-like on/off pattern
        pulse_rate = 4  # 4 pulses per second
        on_time = 0.15  # 150ms on
        pattern = (np.sin(2 * np.pi * pulse_rate * t) > 0).astype(float)
        
        audio = carrier * pattern
        return self._fade_envelope(audio)
    
    def generate_track_4(self) -> np.ndarray:
        """Track 4: Chord progression (harmonics of 440Hz)."""
        t = np.linspace(0, self.duration, self.num_samples)
        
        # C major chord: C (262Hz), E (330Hz), G (392Hz)
        c_freq, e_freq, g_freq = 262, 330, 392
        c = np.sin(2 * np.pi * c_freq * t) * 0.3
        e = np.sin(2 * np.pi * e_freq * t) * 0.3
        g = np.sin(2 * np.pi * g_freq * t) * 0.3
        
        audio = c + e + g
        audio /= np.max(np.abs(audio))  # Normalize
        return self._fade_envelope(audio)
    
    def generate_track_5(self) -> np.ndarray:
        """Track 5: Binaural-style dual-tone (slightly detuned)."""
        t = np.linspace(0, self.duration, self.num_samples)
        
        # Two slightly detuned sine waves
        freq1, freq2 = 440, 445  # 5Hz difference
        tone1 = np.sin(2 * np.pi * freq1 * t)
        tone2 = np.sin(2 * np.pi * freq2 * t)
        
        audio = (tone1 + tone2) * 0.5
        return self._fade_envelope(audio)
    
    def generate_success(self) -> np.ndarray:
        """Success sound: 3-note ascending chord."""
        notes = [262, 330, 392]  # C, E, G
        samples_per_note = self.num_samples // (len(notes) * 3)  # 3x faster
        audio = np.array([])
        
        for note_freq in notes:
            t = np.linspace(0, self.duration / (len(notes) * 3), samples_per_note)
            note = np.sin(2 * np.pi * note_freq * t)
            audio = np.concatenate([audio, note])
        
        audio = audio[:self.num_samples]
        return self._fade_envelope(audio, fade_ms=100)
    
    def generate_timeout(self) -> np.ndarray:
        """Timeout sound: descending wah-wah effect."""
        t = np.linspace(0, self.duration, self.num_samples)
        freq_start, freq_end = 800, 200
        freq = freq_start + (freq_end - freq_start) * t / self.duration
        phase = 2 * np.pi * np.cumsum(freq) / self.sample_rate
        audio = np.sin(phase)
        return self._fade_envelope(audio, fade_ms=100)
    
    def generate_mismatch(self) -> np.ndarray:
        """Mismatch sound: short buzzer."""
        t = np.linspace(0, 0.5, int(self.sample_rate * 0.5))  # 500ms
        freq = 1000
        audio = np.sin(2 * np.pi * freq * t)
        # Envelope: sharp attack, fast decay
        envelope = np.exp(-5 * t)
        return audio * envelope

def generate_all_clips(output_dir='audio_clips', sample_rate=44100):
    """Generate all audio clips."""
    generator = ProceduralAudioGenerator(sample_rate=sample_rate, duration=10)
    
    clips = {
        'track1.wav': generator.generate_track_1(),
        'track2.wav': generator.generate_track_2(),
        'track3.wav': generator.generate_track_3(),
        'track4.wav': generator.generate_track_4(),
        'track5.wav': generator.generate_track_5(),
        'success.wav': generator.generate_success(),
        'timeout.wav': generator.generate_timeout(),
        'mismatch.wav': generator.generate_mismatch(),
    }
    
    os.makedirs(output_dir, exist_ok=True)
    for filename, audio in clips.items():
        filepath = os.path.join(output_dir, filename)
        generator._save_wav(audio, filepath)
        print(f"Generated {filepath}")

if __name__ == "__main__":
    generate_all_clips()
