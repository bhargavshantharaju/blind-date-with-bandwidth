"""
Daily report generation template.
Auto-generates YYYY-MM-DD_report.md in docs/reports/
"""

REPORT_TEMPLATE = """# Blind Date with Bandwidth - Daily Report
## {date}

**Event Venue**: IEEE ComSoc Booth {location}

### Executive Summary

- **Total Participants**: {total_participants}
- **Total Matches**: {total_matches}
- **Match Success Rate**: {match_rate:.1%}
- **Average Sync Time**: {avg_sync_time_ms:.1f}ms
- **System Uptime**: {uptime_percent:.1f}%
- **Errors Logged**: {errors_count}

### Performance Metrics

| Metric | Value |
|--------|-------|
| Fastest Sync | {fastest_sync_ms}ms |
| Slowest Sync | {slowest_sync_ms}ms |
| Median Sync | {median_sync_ms}ms |
| 95th Percentile | {p95_sync_ms}ms |
| Most Popular Track | Track {most_popular_track} |

### Timeline

**Peak Activity**: {peak_hour}:00 - {peak_hour}:59
- {peak_matches} matches in peak hour
- {peak_participants} unique participants

### Track Distribution

```
Track 1 (Electric Pulse):    ████████ {track_1_count} matches
Track 2 (Cosmic Journey):    ██████ {track_2_count} matches
Track 3 (Urban Rhythm):      ███████ {track_3_count} matches
Track 4 (Ethereal Waves):    ██████████ {track_4_count} matches
Track 5 (Retro Synth):       █████ {track_5_count} matches
```

### Technical Notes

- WiFi dropouts: {wifi_dropouts}
- MQTT reconnections: {mqtt_reconnects}
- Audio device failures: {audio_failures}
- Critical errors: {critical_errors}

### Lessons Learned

**What Worked Well:**
- [Auto-populated from event logs]

**Areas for Improvement:**
- [Auto-populated from event logs]

### Next Event Checklist

- [ ] Increase WiFi signal strength
- [ ] Monitor OLED power consumption
- [ ] Pre-test all 5 audio tracks
- [ ] Verify MQTT TLS certificates
- [ ] Run full tournament bracket test

---
Generated: {generation_time}
Report Version: 1.0
"""

def generate_daily_report(metrics, location: str = "Unknown"):
    """Generate markdown report."""
    report = metrics.generate_daily_report()
    
    # Calculate percentiles
    sync_times = sorted(metrics.sync_times)
    n = len(sync_times)
    median_idx = n // 2
    p95_idx = int(0.95 * n)
    
    content = REPORT_TEMPLATE.format(
        date=report.date,
        location=location,
        total_participants=report.total_participants,
        total_matches=report.total_matches,
        match_rate=report.match_rate,
        avg_sync_time_ms=report.avg_sync_time_ms,
        uptime_percent=report.uptime_percent,
        errors_count=report.errors_count,
        fastest_sync_ms=report.fastest_sync_ms,
        slowest_sync_ms=report.slowest_sync_ms,
        median_sync_ms=sync_times[median_idx] if sync_times else 0,
        p95_sync_ms=sync_times[p95_idx] if sync_times else 0,
        most_popular_track=report.most_popular_track,
        peak_hour=report.peak_hour,
        peak_matches=max(metrics.hourly_matches.values()) if metrics.hourly_matches else 0,
        peak_participants=0,  # Would need per-hour tracking
        track_1_count=metrics.track_count.get(1, 0),
        track_2_count=metrics.track_count.get(2, 0),
        track_3_count=metrics.track_count.get(3, 0),
        track_4_count=metrics.track_count.get(4, 0),
        track_5_count=metrics.track_count.get(5, 0),
        wifi_dropouts=0,
        mqtt_reconnects=0,
        audio_failures=0,
        critical_errors=0,
        generation_time=datetime.now().isoformat(),
    )
    
    return content
