# Support & Getting Help

## 📕 Documentation

- **[README.md](./README.md)** - Project overview, quick start
- **[PRIVACY.md](./PRIVACY.md)** - Data handling policy
- **[SECURITY.md](./SECURITY.md)** - Security guidelines
- **[docs/](./docs/)** - Full documentation site

## 🤔 Frequently Asked Questions

**Q: I can't hear audio from my station.**
A: Check OLED display for error messages. Troubleshooting:
1. Verify USB power connection
2. Test audio with `speaker-test` on Pi
3. Check mixer levels: `alsamixer`
4. See [TROUBLESHOOTING.md](./docs/TROUBLESHOOTING.md)

**Q: WiFi keeps disconnecting.**
A: Using 2.4GHz band? Check:
1. WiFi password in `config.json`
2. MQTT broker IP address
3. Try using 5GHz if available
4. Increase transmit power: see `esp32_firmware/wifi_config.h`

**Q: How do I modify audio tracks?**
A: Edit [procedural_audio.py](./raspberry_pi_server/procedural_audio.py) or add WAV files to `audio/` directory.

**Q: Can I build this with different hardware?**
A: Yes! See [OPEN_HARDWARE.md](./OPEN_HARDWARE.md). Ensure:
- 5V power supply (≥2A)
- WiFi-capable microcontroller (ESP32 or similar)
- I2C OLED display (optional)
- 3.5mm audio jack

**Q: How do I deploy for a conference booth?**
A: See [DEPLOYMENT.md](./docs/DEPLOYMENT.md) for checklist, network setup, WiFi optimization.

## 💬 Community Support

### GitHub Discussions
Post questions, ideas, and feedback in [GitHub Discussions](https://github.com/[repo]/discussions):
- 💡 **Ideas**: New features, improvements
- 🎯 **Show and Tell**: Your builds, modifications, videos
- ❓ **Q&A**: Get help from community

### GitHub Issues
Report bugs or request features via [GitHub Issues](https://github.com/[repo]/issues):
- 🐛 **Bug**: Something isn't working
- ✨ **Feature**: Request new capability
- 📚 **Documentation**: Help improve docs

## 🔒 Security Issues

**⚠️ Do NOT open public GitHub issues for security vulnerabilities!**

Instead, email: `security@[domain]` with:
- Description of issue
- Affected component(s)
- Reproduction steps
- Suggested fix (if any)

See [SECURITY.md](./SECURITY.md#reporting-security-vulnerabilities) for full disclosure policy.

## 📧 Contact

| Purpose | Contact | Response Time |
|---------|---------|---|
| General questions | GitHub Discussions | 2-5 days |
| Bug reports | GitHub Issues | 1-3 days |
| Security issues | `security@[domain]` | 24 hours |
| Code of Conduct | `conduct@[domain]` | 24 hours |
| Talks/press | `[maintainer-email]` | 1 week |

## 🐛 Bug Reports

To help us debug faster, include:

```
**System:** Raspberry Pi 4 / ESP32 / etc
**Firmware/Software Version:** v1.x.x
**Description:** What happened?
**Reproduction Steps:**
  1. ...
  2. ...
**Expected Behavior:** What should happen?
**Actual Behavior:** What actually happened?
**Logs:** Paste relevant output from:
  - Pi: `tail -f logs/blind_date.log`
  - ESP32: Serial monitor output
  - MQTT: `mosquitto_sub -h localhost -v -t '#'`
**Screenshots/Videos:** If applicable
```

## 📦 Open Issues / Known Limitations

- Audio quality degrades with WiFi latency >100ms
- MQTT message loss possible on congested networks (workaround: use QoS 2)
- No multi-language UI support yet (Layer 18 in progress)
- ESP32 crash logs not persisted to flash (by design)

## ⏱️ Expected Response Times

- **Urgent Security Issue**: 1-2 hours
- **High Priority Bug**: 24 hours
- **Feature Request**: 1 week for triage
- **General Question**: 2-5 days

## 🎓 Learning Resources

- [Getting started with ESP32](https://randomnerdtutorials.com/esp32-introduction-tutorial/)
- [MQTT Protocol Overview](https://mqtt.org/faq)
- [Python Audio Programming](https://realpython.com/python-speech-recognition/)
- [IEEE ComSoc Resources](https://www.comsoc.org/)

## 💪 Contributing

Want to help? See [CONTRIBUTING.md](./CONTRIBUTING.md) for:
- Development setup
- Coding standards
- PR process
- How to become a maintainer

---

**Last Updated:** 2024-01-XX  
**Maintained By:** IEEE ComSoc [Chapter]
