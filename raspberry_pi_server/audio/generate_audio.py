import numpy as np
import wave
import struct
import os

def generate_tone(filename, duration, frequency, sample_rate=44100):
    t = np.linspace(0, duration, int(sample_rate * duration), False)
    tone = np.sin(frequency * 2 * np.pi * t)
    # Fade in/out to avoid clicks
    fade_len = int(sample_rate * 0.01)
    tone[:fade_len] = tone[:fade_len] * np.linspace(0, 1, fade_len)
    tone[-fade_len:] = tone[-fade_len:] * np.linspace(1, 0, fade_len)
    # Normalize
    tone = np.int16(tone * 32767)
    with wave.open(filename, 'w') as wav_file:
        wav_file.setnchannels(1)
        wav_file.setsampwidth(2)
        wav_file.setframerate(sample_rate)
        for sample in tone:
            wav_file.writeframes(struct.pack('<h', sample))

if __name__ == "__main__":
    os.chdir(os.path.dirname(__file__))
    # Success beep
    generate_tone('success.wav', 0.5, 1000)
    # Tracks
    frequencies = [300, 400, 500, 600, 700]
    for i, freq in enumerate(frequencies, 1):
        generate_tone(f'track{i}.wav', 10, freq)
    print("Audio files generated.")