# Security Policy for Blind Date with Bandwidth

## Reporting Security Vulnerabilities

If you discover a security vulnerability, **do not** open a public GitHub issue.

Instead:
1. Email: `[maintainer-email]@[domain]` (subject: "SECURITY: Blind Date vulnerability")
2. Include: Description, affected version, reproduction steps, suggested fix
3. **72-hour disclosure SLA**: We will respond within 3 business days

## Vulnerability Response Process

1. **Triage** (Day 1): Evaluate severity
   - Critical (10.0): RCE, auth bypass, data leak → patch immediately
   - High (7.0-9.9): Denial of service, privilege escalation → patch within 1 week
   - Medium (4.0-6.9): Information disclosure, weak crypto → patch within 2 weeks
   - Low (1.0-3.9): Minor issues, low impact → backlog

2. **Fix** (Day 2-7): Develop and test patch

3. **Disclosure** (Day 7): Release fix + advisory
   - v[X.Y.Z+1] tag on GitHub
   - Security advisory posted
   - CVE requested if critical
   - Credit reporter if desired

## Known Security Constraints

### By Design (Acceptable Risks)

- **WiFi-dependent**: Jam WiFi = system offline (mitigated by "island mode")
- **No encrypted audio**: Audio stream is plaintext (it's a public conference demo)
- **Weak random seed**: If ESP32 loses power, RNG reseeds (rare in booth)
- **No rate limiting on MQTT**: Trust LAN or provide firewall

### Mitigations Implemented

✓ **MQTT Authentication**: Username / password + TLS 1.2
✓ **Flask Admin Panel**: TOTP 2FA (RFC 6238)
✓ **Replay Attack Prevention**: 500ms deduplication window on MQTT payloads
✓ **Memory-only data**: No SQL injection vectors (sessions in-memory)
✓ **Input validation**: Pydantic models on all API endpoints
✓ **HTTPS ready**: Flask-Talisman security headers (when deployed with nginx)

### Out of Scope

- ❌ Protection against physical tampering
- ❌ Protection against WiFi jamming
- ❌ Multi-tenant isolation (single-event device)
- ❌ Credential recovery (lost TOTP seed = panel locked)

## Dependencies & Maintenance

We track security updates:
- Python deps: Renovate bot scans `requirements.txt` weekly
- ESP32 Arduino: Manual review of security advisories
- Flask/Paho-MQTT: Subscribe to security mailing lists

To check for known vulnerabilities locally:
```bash
pip install safety
safety check -r requirements.txt
```

## Deployment Security Checklist

Before deploying to a public conference:

- [ ] Change default MQTT username/password
- [ ] Generate new TOTP seed (admin authentication)
- [ ] Deploy on trusted WiFi (not open guest network)
- [ ] Enable Flask-Talisman HTTPS headers
- [ ] Review PRIVACY.md with attendees
- [ ] Verify audio stream is not recorded by booth cameras
- [ ] Test replay attack prevention with Mosquitto_pub/sub
- [ ] Run `make lint` and `make coverage` (>80% target)

## Compliance Standards

- ✓ OWASP Top 10: Input validation, auth, data protection
- ✓ CWE: SQL injection (#89), XSS (#79), CSRF (#352) all addressed
- ✓ CVSS v3.1: Used for severity rating
- ✓ IEEE ComSoc Booth Standards: Meets physical security guidelines

## Questions?

Security inquiries: `[email]`  
General queries: Use GitHub Discussions
