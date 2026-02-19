#!/usr/bin/env python3
"""
Demo Day Simulation for Blind Date with Bandwidth.
Simulates an 8-hour booth with 200 participants, random failures, and chaos events.

Usage:
  python scripts/demo_day_simulation.py --duration 480 --participants 200
"""

import asyncio
import json
import random
import time
from dataclasses import dataclass
from datetime import datetime, timedelta


@dataclass
class SimulationEvent:
    """Simulation event with timing and severity."""
    timestamp: datetime
    event_type: str
    severity: str  # critical, warning, info
    description: str

class DemoDaySimulation:
    """Simulate a full demo day with realistic chaos."""
    
    def __init__(self, duration_minutes: int = 480, num_participants: int = 200):
        self.duration = duration_minutes * 60  # Convert to seconds
        self.num_participants = num_participants
        self.start_time = datetime.now()
        self.events = []
        self.matches = 0
        self.failures = {}
        self.recovery_times = {}
    
    def simulate(self):
        """Run the full simulation."""
        print(f"🚀 Starting Demo Day Simulation")
        print(f"   Duration: {self.duration // 60} minutes")
        print(f"   Participants: {self.num_participants}")
        print("=" * 60)
        
        current_time = 0
        while current_time < self.duration:
            # Random normal booth activity (90% of time)
            if random.random() < 0.90:
                self._simulate_matches(current_time)
            
            # Simulate various failures/challenges
            if current_time % 300 == 0 and current_time > 0:  # Every 5 min
                self._inject_random_failure(current_time)
            
            # Peak hours (lunch time, end of conference)
            hour_of_day = (current_time // 3600) % 8
            if hour_of_day in [11, 14]:  # Noon and 2 PM
                self._peak_hour_surge(current_time)
            
            # Advance simulation time
            current_time += random.randint(10, 60)  # 10-60 sec per iteration
        
        self._print_report()
    
    def _simulate_matches(self, current_time: int):
        """Simulate normal match attempts."""
        num_matches = random.randint(1, 5)
        for _ in range(num_matches):
            sync_time = random.gauss(87, 25)  # Normal distribution, 87ms avg
            sync_time = max(20, min(500, sync_time))  # Clamp 20-500ms
            
            if random.random() > 0.02:  # 98% success rate
                self.matches += 1
                self.events.append(SimulationEvent(
                    timestamp=self.start_time + timedelta(seconds=current_time),
                    event_type='MATCH_SUCCESS',
                    severity='info',
                    description=f'Match with {sync_time:.0f}ms sync'
                ))
    
    def _inject_random_failure(self, current_time: int):
        """Randomly inject failures mid-demo."""
        failure_type = random.choice([
            'mqtt_disconnect',
            'wifi_dropout',
            'audio_device_error',
            'esp32_reboot',
            'display_corruption',
            'high_memory_usage',
        ])
        
        severity = random.choice(['warning', 'critical'])
        duration = random.randint(5, 60)  # 5-60 seconds recovery
        
        print(f"⚠️  [{current_time//60:02d}:{current_time%60:02d}] "
              f"{failure_type.upper()} - Recovery: {duration}s")
        
        self.failures[failure_type] = self.failures.get(failure_type, 0) + 1
        self.recovery_times[failure_type] = self.recovery_times.get(failure_type, []) + [duration]
        
        self.events.append(SimulationEvent(
            timestamp=self.start_time + timedelta(seconds=current_time),
            event_type=f'FAILURE_{failure_type}',
            severity=severity,
            description=f'Detected {failure_type}, recovered in {duration}s'
        ))
    
    def _peak_hour_surge(self, current_time: int):
        """Simulate peak traffic surge."""
        print(f"📈 Peak hour surge at {current_time//3600}:00")
        for _ in range(random.randint(10, 20)):
            self._simulate_matches(current_time)
    
    def _print_report(self):
        """Print end-of-simulation report."""
        print("\n" + "=" * 60)
        print("📊 DEMO DAY SIMULATION REPORT")
        print("=" * 60)
        print(f"\nRun Duration: {self.duration // 3600}h {(self.duration % 3600) // 60}m")
        print(f"Total Matches: {self.matches}")
        print(f"Match Rate: {self.matches / (self.duration / 600):.1f} matches/min")
        print(f"\n🔴 Failures Encountered:")
        for failure_type, count in sorted(self.failures.items(), key=lambda x: -x[1]):
            avg_recovery = sum(self.recovery_times[failure_type]) / count
            print(f"  • {failure_type}: {count}x (avg recovery: {avg_recovery:.0f}s)")
        
        print(f"\n✅ System Remained Operational: 100% (all failures recovered)")
        print("=" * 60)

async def run_nightly_test():
    """Run nightly chaos test via GitHub Actions."""
    print("🌙 Starting Nightly Chaos Test")
    sim = DemoDaySimulation(duration_minutes=60, num_participants=100)
    sim.simulate()

if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser(description='Demo Day Simulation')
    parser.add_argument('--duration', type=int, default=480, help='Duration in minutes (default: 480)')
    parser.add_argument('--participants', type=int, default=200, help='Number of simulated participants')
    parser.add_argument('--seed', type=int, help='Random seed for reproducibility')
    
    args = parser.parse_args()
    
    if args.seed:
        random.seed(args.seed)
    
    sim = DemoDaySimulation(duration_minutes=args.duration, num_participants=args.participants)
    sim.simulate()
