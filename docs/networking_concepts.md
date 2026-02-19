# Networking Concepts Demonstrated

## OSI Layer Mapping

- **Physical Layer**: WiFi radio waves, audio signals
- **Data Link Layer**: MQTT protocol, device addressing
- **Network Layer**: IP addressing, routing
- **Transport Layer**: TCP (MQTT), session establishment
- **Session Layer**: Match negotiation, session timeout
- **Presentation Layer**: JSON message formatting
- **Application Layer**: Dashboard UI, event logging

## Real-World Equivalents

| Demo Element | Networking Concept | Real Example |
|--------------|-------------------|--------------|
| Button Press | SYN packet | TCP handshake initiation |
| Track ID | Packet identifier | IP packet ID |
| Match Detection | ACK receipt | TCP three-way handshake |
| Audio Bridge | Established connection | VoIP call, HTTP session |
| Timeout | FIN packet | Connection teardown |
| LED States | Link status | Network interface indicators |

## Educational Value

This demo makes abstract concepts tangible:
- Synchronization problems in distributed systems
- Race conditions in concurrent events
- State management in protocols
- Timeout handling in unreliable networks
- Real-time requirements in communication