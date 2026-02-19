"""
Event metrics and telemetry for Blind Date.
Generate daily reports, track statistics, export data.
"""

import json
import time
from collections import defaultdict
from dataclasses import asdict, dataclass
from datetime import datetime
from typing import Dict, List


@dataclass
class DailyReport:
    """Daily aggregated statistics."""
    date: str
    total_participants: int
    total_matches: int
    match_rate: float  # matches / participants
    avg_sync_time_ms: float
    fastest_sync_ms: int
    slowest_sync_ms: int
    most_popular_track: int
    peak_hour: int
    uptime_percent: float
    errors_count: int

class MetricsCollector:
    """Collect and aggregate event metrics."""
    
    def __init__(self):
        self.matches = []
        self.errors = []
        self.sync_times = []
        self.track_count = defaultdict(int)
        self.hourly_matches = defaultdict(int)
        self.start_time = time.time()
        self.downtime_seconds = 0
    
    def record_match(self, station_a: str, station_b: str, sync_ms: int, track: int):
        """Record a successful match."""
        self.matches.append({
            'time': datetime.now().isoformat(),
            'station_a': station_a,
            'station_b': station_b,
            'sync_time_ms': sync_ms,
            'track': track,
        })
        self.sync_times.append(sync_ms)
        self.track_count[track] += 1
        
        hour = datetime.now().hour
        self.hourly_matches[hour] += 1
    
    def record_error(self, error_type: str, details: str):
        """Record system error."""
        self.errors.append({
            'time': datetime.now().isoformat(),
            'type': error_type,
            'details': details,
        })
    
    def record_downtime(self, seconds: int):
        """Record system downtime."""
        self.downtime_seconds += seconds
    
    def generate_daily_report(self) -> DailyReport:
        """Generate end-of-day report."""
        if not self.matches:
            return DailyReport(
                date=datetime.now().strftime('%Y-%m-%d'),
                total_participants=0,
                total_matches=0,
                match_rate=0.0,
                avg_sync_time_ms=0,
                fastest_sync_ms=0,
                slowest_sync_ms=0,
                most_popular_track=0,
                peak_hour=0,
                uptime_percent=100.0,
                errors_count=len(self.errors),
            )
        
        # Calculate uptime
        total_seconds = time.time() - self.start_time
        uptime_percent = 100 * (1 - self.downtime_seconds / total_seconds) if total_seconds > 0 else 100
        
        # Find peak hour
        peak_hour = max(self.hourly_matches, key=self.hourly_matches.get) if self.hourly_matches else 0
        
        return DailyReport(
            date=datetime.now().strftime('%Y-%m-%d'),
            total_participants=len(set(m['station_a'] for m in self.matches) | 
                                   set(m['station_b'] for m in self.matches)),
            total_matches=len(self.matches),
            match_rate=len(self.matches) / max(len(set(m['station_a'] for m in self.matches) | 
                                                     set(m['station_b'] for m in self.matches)), 1),
            avg_sync_time_ms=sum(self.sync_times) / len(self.sync_times),
            fastest_sync_ms=min(self.sync_times),
            slowest_sync_ms=max(self.sync_times),
            most_popular_track=max(self.track_count, key=self.track_count.get),
            peak_hour=peak_hour,
            uptime_percent=uptime_percent,
            errors_count=len(self.errors),
        )
    
    def export_json(self, filename: str):
        """Export all metrics to JSON."""
        report = self.generate_daily_report()
        data = {
            'report': asdict(report),
            'matches': self.matches,
            'errors': self.errors,
            'track_distribution': dict(self.track_count),
            'hourly_breakdown': dict(self.hourly_matches),
        }
        with open(filename, 'w') as f:
            json.dump(data, f, indent=2)

metrics = MetricsCollector()

def setup_metrics_routes(app):
    """Add metrics endpoints to Flask app."""
    from flask import jsonify
    
    @app.route('/api/v1/reports/today')
    def get_today_report():
        """Get today's metrics."""
        report = metrics.generate_daily_report()
        return jsonify(asdict(report))
    
    @app.route('/api/v1/metrics/sync-histogram')
    def get_sync_histogram():
        """Return sync time histogram."""
        bins = [0, 50, 100, 150, 200, 500]
        counts = [0] * len(bins)
        
        for sync_time in metrics.sync_times:
            for i, b in enumerate(bins):
                if sync_time < b:
                    counts[i] += 1
                    break
        
        return jsonify({
            'bins': [f'<{b}ms' for b in bins],
            'counts': counts,
        })
    
    @app.route('/api/v1/metrics/export')
    def export_metrics():
        """Export full metrics as JSON."""
        report = metrics.generate_daily_report()
        return jsonify(asdict(report))
