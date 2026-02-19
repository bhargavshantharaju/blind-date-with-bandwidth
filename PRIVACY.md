# Privacy Policy for Blind Date with Bandwidth

## Data Collection

We collect **NO personal data**. Here's what we do NOT store:

- ❌ No names or identities
- ❌ No email addresses
- ❌ No phone numbers
- ❌ No audio recordings or samples
- ❌ No user profiles or history
- ❌ No cookies or tracking pixels
- ❌ No third-party connections

## What We DO Record (Session-Only)

During a single event session, we temporarily track:

- **Match Results**: Station ID, track selection, sync time (ms), winner
  - *Retention*: Cleared at event end
  - *Purpose*: Display leaderboard, tournament bracket

- **System Health**: Error logs, WiFi events, MQTT heartbeat
  - *Retention*: 24 hours, then deleted
  - *Purpose*: Debugging, event reporting

- **Anonymized Aggregate Stats**: Total matches, average sync time, peak hour
  - *Retention*: Permanent (used in IEEE ComSoc reports)
  - *Purpose*: Demonstrate technical performance

## User Consent

This project is displayed at IEEE conference booths where attendees physically interact with hardware. By selecting a track and participating:

1. You consent to match attempt logging (cleared at event end)
2. You understand no audio is recorded or stored
3. You accept anonymized stats may be published in papers

**Explicit Consent Toggle**: Spectator display shows:
> ✓ I consent to participate (checkbox)
> Data will not be stored after event ends.

## Security

- ✓ MQTT uses TLS encryption
- ✓ Flask endpoints require TOTP authentication (admin only)
- ✓ Replay attacks prevented (500ms deduplication window)
- ✓ No external API calls (fully offline-capable)
- ✓ Open-source code auditable on GitHub

## Compliance

- ✓ GDPR: No personal data collection = no GDPR obligations
- ✓ CCPA: Not subject (no consumer profiling)
- ✓ IEEE Policy: Demo device, one-time use only
- ✓ Fair Use: Open hardware, derivable for research

## Questions?

Contact: [repository maintainer email]
CERN-OHL-S v2 licensed hardware - fully inspectable design.
