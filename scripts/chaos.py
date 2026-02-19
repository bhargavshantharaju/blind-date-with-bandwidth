#!/usr/bin/env python3
"""
Chaos Injection Tool for Blind Date with Bandwidth.
Simulate system failures to test resilience.

Usage:
  python scripts/chaos.py --fault mqtt_disconnect --duration 30
  python scripts/chaos.py --fault wifi_flaky --duration 60 --intensity 0.8
"""

import argparse
import signal
import subprocess
import sys
import time
from enum import Enum


class FaultType(Enum):
    """Available fault injection types."""
    MQTT_DISCONNECT = 'mqtt_disconnect'
    MQTT_SLOW = 'mqtt_slow'
    WIFI_DROPOUT = 'wifi_dropout'
    WIFI_FLAKY = 'wifi_flaky'
    NETWORK_LATENCY = 'network_latency'
    SERVICE_CRASH = 'service_crash'
    MEMORY_PRESSURE = 'memory_pressure'
    CPU_SPIKE = 'cpu_spike'
    AUDIO_GLITCH = 'audio_glitch'

class ChaosEngine:
    """Inject chaos into running system."""
    
    def __init__(self, fault_type: FaultType, duration_seconds: int, intensity: float = 1.0):
        self.fault = fault_type
        self.duration = duration_seconds
        self.intensity = min(1.0, max(0.0, intensity))
        self.start_time = time.time()
        self.running = False
    
    def start(self):
        """Begin chaos injection."""
        self.running = True
        print(f"⚡ Starting CHAOS INJECTION: {self.fault.value}")
        print(f"   Duration: {self.duration}s | Intensity: {self.intensity:.0%}")
        print("   Press Ctrl+C to stop")
        print("=" * 50)
        
        try:
            if self.fault == FaultType.MQTT_DISCONNECT:
                self._inject_mqtt_disconnect()
            elif self.fault == FaultType.MQTT_SLOW:
                self._inject_mqtt_slow()
            elif self.fault == FaultType.WIFI_DROPOUT:
                self._inject_wifi_dropout()
            elif self.fault == FaultType.WIFI_FLAKY:
                self._inject_wifi_flaky()
            elif self.fault == FaultType.NETWORK_LATENCY:
                self._inject_network_latency()
            elif self.fault == FaultType.SERVICE_CRASH:
                self._inject_service_crash()
            elif self.fault == FaultType.MEMORY_PRESSURE:
                self._inject_memory_pressure()
            elif self.fault == FaultType.CPU_SPIKE:
                self._inject_cpu_spike()
            elif self.fault == FaultType.AUDIO_GLITCH:
                self._inject_audio_glitch()
        finally:
            self.stop()
    
    def _inject_mqtt_disconnect(self):
        """Simulate MQTT broker disconnect."""
        stop_cmd = 'sudo systemctl stop mosquitto'
        start_cmd = 'sudo systemctl start mosquitto'
        
        print(f"🔴 Stopping MQTT broker...")
        subprocess.run(stop_cmd, shell=True, capture_output=True)
        
        time.sleep(self.duration * self.intensity)
        
        print(f"🟢 Restarting MQTT broker...")
        subprocess.run(start_cmd, shell=True, capture_output=True)
        time.sleep(5)  # Wait for broker to settle
    
    def _inject_mqtt_slow(self):
        """Simulate slow MQTT responses with latency."""
        print(f"🐌 Adding MQTT latency ({self.duration}s)...")
        # Add 500ms+ latency to MQTT port (1883)
        latency_ms = int(500 * self.intensity)
        cmd = f'sudo tc qdisc add dev eth0 root netem delay {latency_ms}ms'
        subprocess.run(cmd, shell=True, capture_output=True)
        
        time.sleep(self.duration)
        
        print(f"🟢 Removing latency...")
        subprocess.run('sudo tc qdisc del dev eth0 root', shell=True, capture_output=True)
    
    def _inject_wifi_dropout(self):
        """Simulate catastrophic WiFi loss."""
        print(f"📡 Simulating WiFi dropout...")
        down_cmd = 'sudo ifconfig wlan0 down'
        up_cmd = 'sudo ifconfig wlan0 up'
        
        subprocess.run(down_cmd, shell=True, capture_output=True)
        time.sleep(self.duration * self.intensity)
        subprocess.run(up_cmd, shell=True, capture_output=True)
        
        print(f"✅ WiFi restored")
        time.sleep(10)  # Wait for reconnection
    
    def _inject_wifi_flaky(self):
        """Simulate unreliable WiFi with packet loss."""
        print(f"📡 Inducing WiFi packet loss ({self.intensity:.0%})...")
        loss_percent = int(100 * self.intensity)
        cmd = f'sudo tc qdisc add dev wlan0 root netem loss {loss_percent}%'
        subprocess.run(cmd, shell=True, capture_output=True)
        
        time.sleep(self.duration)
        
        subprocess.run('sudo tc qdisc del dev wlan0 root', shell=True, capture_output=True)
        print(f"✅ WiFi packet loss removed")
    
    def _inject_network_latency(self):
        """Simulate high network latency."""
        print(f"🌍 Adding {int(500*self.intensity)}ms network latency...")
        latency_ms = int(500 * self.intensity)
        cmd = f'sudo tc qdisc add dev eth0 root netem delay {latency_ms}ms 20ms'
        subprocess.run(cmd, shell=True, capture_output=True)
        
        time.sleep(self.duration)
        subprocess.run('sudo tc qdisc del dev eth0 root', shell=True, capture_output=True)
    
    def _inject_service_crash(self):
        """Simulate Flask dashboard crash and restart."""
        print(f"💥 Crashing dashboard service...")
        subprocess.run('sudo systemctl stop blind-date', shell=True, capture_output=True)
        
        time.sleep(self.duration * self.intensity)
        
        print(f"🟢 Restarting dashboard...")
        subprocess.run('sudo systemctl start blind-date', shell=True, capture_output=True)
    
    def _inject_memory_pressure(self):
        """Simulate high memory usage (via memory hog process)."""
        print(f"💾 Creating memory pressure ({int(100*self.intensity)}MB)...")
        mem_mb = int(100 * self.intensity)
        cmd = f'python3 -c "import numpy; x = numpy.zeros(({mem_mb}*1024*1024//8,)); __import__(\'time\').sleep({self.duration})"'
        process = subprocess.Popen(cmd, shell=True)
        
        process.wait()
        print(f"✅ Memory pressure released")
    
    def _inject_cpu_spike(self):
        """Simulate high CPU usage."""
        print(f"🔥 Inducing CPU spike... (stress-ng required)")
        cmd = f'stress-ng --cpu 2 --timeout {self.duration}s'
        subprocess.run(cmd, shell=True, capture_output=True)
    
    def _inject_audio_glitch(self):
        """Simulate audio device errors."""
        print(f"🎵 Simulating audio device errors...")
        # Restart audio service
        subprocess.run('sudo systemctl restart alsa-utils', shell=True, capture_output=True)
        time.sleep(2)
        
        time.sleep(self.duration * self.intensity)
        print(f"✅ Audio system recovered")
    
    def stop(self):
        """Stop chaos injection."""
        self.running = False
        elapsed = time.time() - self.start_time
        print("\n" + "=" * 50)
        print(f"⏹️  CHAOS INJECTION STOPPED")
        print(f"   Duration: {elapsed:.1f}s")
        print(f"   Next: Check logs for recovery evidence")
        print("=" * 50)

def main():
    parser = argparse.ArgumentParser(
        description='Chaos Engineering Tool for Blind Date with Bandwidth'
    )
    parser.add_argument(
        '--fault',
        type=str,
        required=True,
        choices=[f.value for f in FaultType],
        help='Type of fault to inject'
    )
    parser.add_argument(
        '--duration',
        type=int,
        default=30,
        help='Duration in seconds (default: 30)'
    )
    parser.add_argument(
        '--intensity',
        type=float,
        default=1.0,
        help='Severity of fault (0.0-1.0, default: 1.0)'
    )
    
    args = parser.parse_args()
    
    fault_type = FaultType(args.fault)
    chaos = ChaosEngine(fault_type, args.duration, args.intensity)
    
    def signal_handler(sig, frame):
        print("\n⚠️  Interrupted by user")
        chaos.stop()
        sys.exit(0)
    
    signal.signal(signal.SIGINT, signal_handler)
    
    chaos.start()

if __name__ == '__main__':
    main()
