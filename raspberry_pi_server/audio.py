import pyaudio
import wave
import threading
import time
import alsaaudio

class AudioHandler:
    def __init__(self):
        self.p = pyaudio.PyAudio()
        self.chunk = 1024
        self.format = pyaudio.paInt16
        self.channels = 1
        self.rate = 44100

        self.device_a_out = None
        self.device_a_in = None
        self.device_b_out = None
        self.device_b_in = None
        self._discover_devices()

        self.streams = {}
        self.bridging = False

    def _discover_devices(self):
        usb_devices = []
        for i in range(self.p.get_device_count()):
            info = self.p.get_device_info_by_index(i)
            name = info.get('name', '').lower()
            if 'usb' in name and (info.get('maxInputChannels', 0) > 0 or info.get('maxOutputChannels', 0) > 0):
                usb_devices.append(i)
        if len(usb_devices) < 2:
            raise RuntimeError(f"Need at least 2 USB audio devices, found {len(usb_devices)}")
        self.device_a_in = self.device_a_out = usb_devices[0]
        self.device_b_in = self.device_b_out = usb_devices[1]
        print(f"Station A: Device {usb_devices[0]}")
        print(f"Station B: Device {usb_devices[1]}")

    def list_devices(self):
        info = self.p.get_host_api_info_by_index(0)
        numdevices = info.get('deviceCount')
        for i in range(0, numdevices):
            if (self.p.get_device_info_by_host_api_device_index(0, i).get('maxInputChannels')) > 0:
                print("Input Device id ", i, " - ", self.p.get_device_info_by_host_api_device_index(0, i).get('name'))
            if (self.p.get_device_info_by_host_api_device_index(0, i).get('maxOutputChannels')) > 0:
                print("Output Device id ", i, " - ", self.p.get_device_info_by_host_api_device_index(0, i).get('name'))

    def play_wav(self, filename, device_index):
        try:
            wf = wave.open(filename, 'rb')
            stream = self.p.open(format=self.p.get_format_from_width(wf.getsampwidth()),
                                 channels=wf.getnchannels(),
                                 rate=wf.getframerate(),
                                 output=True,
                                 output_device_index=device_index)
            data = wf.readframes(self.chunk)
            while data:
                stream.write(data)
                data = wf.readframes(self.chunk)
            stream.stop_stream()
            stream.close()
            wf.close()
        except Exception as e:
            print(f"Error playing {filename}: {e}")

    def start_bridging(self):
        if self.bridging:
            return
        self.bridging = True

        # Input streams
        self.stream_a_in = self.p.open(format=self.format,
                                       channels=self.channels,
                                       rate=self.rate,
                                       input=True,
                                       input_device_index=self.device_a_in,
                                       frames_per_buffer=self.chunk)
        self.stream_b_in = self.p.open(format=self.format,
                                       channels=self.channels,
                                       rate=self.rate,
                                       input=True,
                                       input_device_index=self.device_b_in,
                                       frames_per_buffer=self.chunk)

        # Output streams
        self.stream_a_out = self.p.open(format=self.format,
                                        channels=self.channels,
                                        rate=self.rate,
                                        output=True,
                                        output_device_index=self.device_a_out,
                                        frames_per_buffer=self.chunk)
        self.stream_b_out = self.p.open(format=self.format,
                                        channels=self.channels,
                                        rate=self.rate,
                                        output=True,
                                        output_device_index=self.device_b_out,
                                        frames_per_buffer=self.chunk)

        # Start threads
        threading.Thread(target=self.bridge_a_to_b, daemon=True).start()
        threading.Thread(target=self.bridge_b_to_a, daemon=True).start()

    def bridge_a_to_b(self):
        while self.bridging:
            try:
                data = self.stream_a_in.read(self.chunk)
                self.stream_b_out.write(data)
            except Exception as e:
                print(f"Error in A to B: {e}")
                break

    def bridge_b_to_a(self):
        while self.bridging:
            try:
                data = self.stream_b_in.read(self.chunk)
                self.stream_a_out.write(data)
            except Exception as e:
                print(f"Error in B to A: {e}")
                break

    def stop_bridging(self):
        self.bridging = False
        time.sleep(0.1)  # Allow threads to stop
        if hasattr(self, 'stream_a_in'):
            self.stream_a_in.stop_stream()
            self.stream_a_in.close()
        if hasattr(self, 'stream_b_in'):
            self.stream_b_in.stop_stream()
            self.stream_b_in.close()
        if hasattr(self, 'stream_a_out'):
            self.stream_a_out.stop_stream()
            self.stream_a_out.close()
        if hasattr(self, 'stream_b_out'):
            self.stream_b_out.stop_stream()
            self.stream_b_out.close()

    def __del__(self):
        self.p.terminate()