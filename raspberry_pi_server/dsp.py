"""
Digital Signal Processing module for audio quality enhancement.
Implements noise gate, AGC, echo cancellation, and filtering.
"""

import logging
import threading
from collections import deque
from typing import Tuple

import numpy as np
from scipy import signal

logger = logging.getLogger(__name__)

class NoiseGate:
    """Suppresses audio below threshold (-40dB)."""
    
    def __init__(self, threshold_db=-40, attack_ms=5, release_ms=100, sample_rate=44100):
        self.threshold_db = threshold_db
        self.threshold_linear = 10 ** (threshold_db / 20.0)
        self.attack_samples = int(attack_ms * sample_rate / 1000)
        self.release_samples = int(release_ms * sample_rate / 1000)
        self.sample_rate = sample_rate
        self.gate_open = False
        self.samples_since_change = 0
    
    def process(self, audio: np.ndarray) -> np.ndarray:
        """Apply noise gate to audio."""
        rms = np.sqrt(np.mean(audio ** 2))
        above_threshold = rms > self.threshold_linear
        
        if above_threshold and not self.gate_open:
            self.samples_since_change = 0
            self.gate_open = True
        elif not above_threshold and self.gate_open:
            self.samples_since_change = 0
            self.gate_open = False
        else:
            self.samples_since_change += len(audio)
        
        if self.gate_open:
            return audio
        else:
            return audio * 0

class AutomaticGainControl:
    """Normalize audio level automatically."""
    
    def __init__(self, target_rms=0.1, attack_ms=10, release_ms=500, sample_rate=44100):
        self.target_rms = target_rms
        self.sample_rate = sample_rate
        self.attack_coeff = np.exp(-1 / (attack_ms * sample_rate / 1000))
        self.release_coeff = np.exp(-1 / (release_ms * sample_rate / 1000))
        self.gain = 1.0
    
    def process(self, audio: np.ndarray) -> np.ndarray:
        """Apply AGC to audio."""
        rms = np.sqrt(np.mean(audio ** 2)) + 1e-8
        target_gain = self.target_rms / rms
        
        if target_gain > self.gain:
            self.gain = self.attack_coeff * self.gain + (1 - self.attack_coeff) * target_gain
        else:
            self.gain = self.release_coeff * self.gain + (1 - self.release_coeff) * target_gain
        
        self.gain = np.clip(self.gain, 0.5, 4.0)  # Limit gain range
        return audio * self.gain

class EchoCanceller:
    """Simple echo cancellation via LMS adaptive filter."""
    
    def __init__(self, delay_ms=50, filter_len=512, sample_rate=44100):
        self.delay_samples = int(delay_ms * sample_rate / 1000)
        self.filter_len = filter_len
        self.sample_rate = sample_rate
        self.outgoing_buffer = deque(maxlen=self.delay_samples + filter_len)
        self.weights = np.zeros(filter_len)
        self.step_size = 0.01
    
    def process(self, incoming: np.ndarray, outgoing: np.ndarray) -> np.ndarray:
        """Cancel echo from outgoing audio in incoming signal."""
        # Build buffer of outgoing audio with delay
        for sample in outgoing:
            self.outgoing_buffer.append(sample)
        
        if len(self.outgoing_buffer) < self.filter_len:
            return incoming
        
        # LMS adaptive filter: update weights and estimate echo
        echo_estimate = np.zeros_like(incoming)
        for i in range(len(incoming)):
            if len(self.outgoing_buffer) >= self.filter_len:
                x = np.array(list(self.outgoing_buffer)[-self.filter_len:])
                echo_estimate[i] = np.dot(self.weights, x)
                error = incoming[i] - echo_estimate[i]
                self.weights += self.step_size * error * x
        
        return incoming - echo_estimate * 0.8

class AudioFilter:
    """Low-pass and band-pass filtering."""
    
    def __init__(self, sample_rate=44100):
        self.sample_rate = sample_rate
        # Design low-pass filter: cutoff at 8kHz
        self.b_lp, self.a_lp = signal.butter(4, 8000, fs=sample_rate, btype='low')
        # Design band-pass filter: 300Hz - 3400Hz (telephone effect)
        self.b_bp, self.a_bp = signal.butter(4, [300, 3400], fs=sample_rate, btype='band')
        
        # State for IIR filtering
        self.zi_lp = signal.lfilter_zi(self.b_lp, self.a_lp)
        self.zi_bp = signal.lfilter_zi(self.b_bp, self.a_bp)
    
    def lowpass(self, audio: np.ndarray) -> np.ndarray:
        """Apply low-pass filter."""
        filtered, self.zi_lp = signal.lfilter(self.b_lp, self.a_lp, audio, zi=self.zi_lp)
        return filtered
    
    def bandpass_telephone(self, audio: np.ndarray) -> np.ndarray:
        """Apply telephone effect (bandpass 300-3400Hz)."""
        filtered, self.zi_bp = signal.lfilter(self.b_bp, self.a_bp, audio, zi=self.zi_bp)
        return filtered

class AudioLevelMeter:
    """Measure RMS audio levels for visualization."""
    
    def __init__(self, window_ms=100, sample_rate=44100):
        self.window_samples = int(window_ms * sample_rate / 1000)
        self.sample_rate = sample_rate
        self.buffer = deque(maxlen=self.window_samples)
    
    def measure(self, audio: np.ndarray) -> float:
        """Return RMS level in dB."""
        for sample in audio:
            self.buffer.append(sample)
        
        if len(self.buffer) < self.window_samples:
            return -60.0
        
        rms = np.sqrt(np.mean(np.array(self.buffer) ** 2)) + 1e-10
        return max(-60.0, min(0.0, 20 * np.log10(rms)))

class DSPPipeline:
    """Complete DSP pipeline: noise gate → AGC → echo cancel → filter."""
    
    def __init__(self, sample_rate=44100, telephone_mode=False):
        self.sample_rate = sample_rate
        self.telephone_mode = telephone_mode
        self.noise_gate = NoiseGate(sample_rate=sample_rate)
        self.agc = AutomaticGainControl(sample_rate=sample_rate)
        self.echo_canceller = EchoCanceller(sample_rate=sample_rate)
        self.filter = AudioFilter(sample_rate=sample_rate)
        self.level_meter = AudioLevelMeter(sample_rate=sample_rate)
        self.lock = threading.Lock()
    
    def process_incoming(self, incoming: np.ndarray, outgoing: np.ndarray = None) -> Tuple[np.ndarray, float]:
        """Process incoming voice audio through DSP chain."""
        with self.lock:
            audio = incoming.astype(np.float32) / 32768.0
            
            # Noise gate
            audio = self.noise_gate.process(audio)
            
            # AGC
            audio = self.agc.process(audio)
            
            # Echo cancellation
            if outgoing is not None:
                outgoing_f = outgoing.astype(np.float32) / 32768.0
                audio = self.echo_canceller.process(audio, outgoing_f)
            
            # Filtering
            if self.telephone_mode:
                audio = self.filter.bandpass_telephone(audio)
            else:
                audio = self.filter.lowpass(audio)
            
            # Metering
            level_db = self.level_meter.measure(audio)
            
            # Convert back to int16
            audio = np.clip(audio * 32768.0, -32768, 32767).astype(np.int16)
            return audio, level_db
