# Hardware Wiring Diagram

## ESP32 Station Wiring

```
ESP32 Dev Board
├── GPIO 4 ─── Button ─── GND
├── GPIO 2 ─── LED (220Ω) ─── GND
├── 3.3V ─── Power Supply +
├── GND ─── Power Supply -
└── USB ─── Programming/OTA
```

## Audio Connections

```
USB Audio Interface 1 (Station A)
├── USB ─── Raspberry Pi USB
├── Headphones Out ─── Station A Headphones
└── Mic In ─── Station A Microphone

USB Audio Interface 2 (Station B)
├── USB ─── Raspberry Pi USB
├── Headphones Out ─── Station B Headphones
└── Mic In ─── Station B Microphone
```

## Power Distribution

```
5V 3A Supply 1
├── + ─── ESP32 VIN
└── - ─── ESP32 GND

5V 3A Supply 2
├── + ─── ESP32 VIN (Station B)
└── - ─── ESP32 GND (Station B)

Raspberry Pi Power
└── Official 5V Supply
```

## Booth Structure

- MDF base with acrylic isolation panels
- ESP32 mounted inside with button/LED accessible
- Headphones/mic routed through panel cutouts
- Cable management with zip ties