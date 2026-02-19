# PCB Schematic & Wiring Reference

This document describes the station electronics for Blind Date with Bandwidth.

For those without KiCad, this Fritzing-style description provides the complete wiring guide.

## Block Diagram

```
┌─────────────────────────────────────────────┐
│                                             │
│  ┌──────────┐      ┌─────────────┐       │
│  │  ESP32   │──I2C─┤ OLED Display│       │
│  │ 32GPIO   │      └─────────────┘       │
│  │          │                             │
│  │          │──GPIO4──┐ Button w/ RC      │
│  │          │         │ filter            │
│  │          │──GPIO2──┤ LED (via Driver)  │
│  │          │──GPIO5──┤ Vibration Motor   │
│  │          │         │ (via MOSFET)      │
│  │          │──GPIO33─┤ NeoPixel RGB LED  │
│  │          │                             │
│  └──────────┘                             │
│   5V | GND                                │
│   USB-C Power                             │
│                                           │
└─────────────────────────────────────────────┘
```

## Components

### Power Supply
- **Input**: USB-C 5V/2A (from power bank or wall adapter)
- **Bulk Capacitor**: 1000µF/10V (stabilizes power rails)
- **Decoupling Caps**: 
  - 100nF on ESP32 VDD (pin 2, 15, 32, 51)
  - 10µF on 3.3V rail

### Microcontroller
- **ESP32 DevKit C v4**
  - 32-bit Xtensa dual-core
  - WiFi 802.11b/g/n
  - Built-in ADC, SPI, I2C, UART
  - 4MB flash, 8MB PSRAM

### Display
- **Adafruit SSD1306 128x64 OLED**
  - I2C interface (GPIO 21 = SDA, GPIO 22 = SCL)
  - Pull-up resistors: 4.7kΩ on both SDA and SCL
  - Address: 0x3C (default)
  - Supply: 3.3V from ESP32

### Input: Push Button
- **Button**: Standard momentary push button (PCB mount)
- **Pin**: GPIO 4
- **Debounce Circuit** (hardware RC filter):
  - 10kΩ pull-up resistor to 3.3V
  - 100nF capacitor to GND
  - Time constant: ~1ms

### Output: LED
- **Regular LED** (2mm or 5mm, optional if using NeoPixel)
- **Color**: Cyan or white
- **pin**: GPIO 2
- **Current limiting**: (220Ω resistor in series to GND)
- **Driver**: 2N2222 NPN transistor
  - Base: GPIO 2 (via 1kΩ pull-down)
  - Collector: LED anode (+3.3V)
  - Emitter: GND
  - Flyback diode: 1N4148 across LED

### Output: Vibration Motor
- **Component**: 5V vibration motor (3-4V supply for softness)
- **Pin**: GPIO 5
- **Driver**: 2N7000 N-channel MOSFET
  - Gate: GPIO 5
  - Drain: GND
  - Source: Motor return
  - Motor power: +5V
  - Flyback diode: 1N4148 across motor
  - Gate resistor: 1kΩ pull-down

### Output: NeoPixel RGB LED (Optional but recommended)
- **Component**: Adafruit Flora RGB Smart NeoPixel
- **Pin**: GPIO 33
- **Supply**: 5V with 1000µF bulk cap
- **Data line**: 470Ω resistor inline
- **Single LED sufficient** for pair identification

### Audio (External Devices)
- **Headphones**: 3.5mm stereo jack (external, no circuitry needed)
- **Microphone**: Optional USB sound card or Raspberry Pi audio interface

## Schematic (Text Notation)

```
3.3V Rail
  │
  ├─[100nF cap]─── GND (near each VDD pin)
  │
  ├─[4.7kΩ]──┬─[100nF]─── GND  (I2C SDA/SCL)
  │              │
  │          GPIO 21/22 ← I2C to OLED
  │
  └─ ESP32 VDD (pins  2, 15, 32, 51)

GPIO 4 (Input - Button)
  │
  ├─[10kΩ]─── 3.3V  (pull-up)
  │
  └─[100nF]─── GND  (debounce cap)
    │
    Button pushes to GND

GPIO 2 (Output - LED Driver)
  │
  ├─[1kΩ resistor]─ 2N2222 Base
                      │ Collector ─── LED Anode (+3.3V)
                      │ Emitter  ──── GND
                      └─[1N4148 diode]─ protects transistor

GPIO 5 (Output - Vibration Motor)
  │
  ├─[1kΩ resistor]─ 2N7000 Gate
                      │ Source (return to GND)
                      │ Drain ────── Motor GND
                      │
                      Motor Power ─ 5V
                      │
                      └─[1N4148 diode]─ flyback protection

GPIO 33 (Output - NeoPixel, optional)
  │
  ├─[470Ω resistor]─ NeoPixel Data in
  │
  5V ──[1000µF cap]─ NeoPixel Power
  │                    │
  └─ GND ────────── NeoPixel GND
```

## PCB Layout Guidelines

### Layer Stack (2-layer board)
- **Top Layer**: Signal traces, components
- **Bottom Layer**: Ground plane (continuous GND)
- **Power distribution**: 5V traces ≥ 0.5mm width

### Routing Rules
- ESP32 GPIO routing: short traces (<5mm) to connectors
- I2C traces: twisted pair routing, separated from high-switching signals
- MOSFET gate traces: short (<1cm), away from RF/WiFi noise
- Ground via placement: via every 5mm on GND traces

### Component Placement
- **ESP32**: center of board
- **OLED header**: front face mounting
- **Decoupling caps**: as close as possible to power pins
- **Motor/LED drivers**: near GPIO connections
- **Power connector**: rear/side of board

## Manufacturing

### PCB Specs
- **Size**: ~80mm x 50mm (fits in enclosure)
- **Layers**: 2
- **Thickness**: 1.6mm
- **Copper**: 1oz (standard)
- **Solder mask**: Green or black
- **Silkscreen**: White

### Assembly
- **Soldering**: reflow (lead-free recommended) or hand-solder
- **Stencil**: not required for one-off builds
- **Test**: continuity check all power/GND nodes after assembly

## BOM (Bill of Materials)

| Ref   | Part Number        | Qty | Value    | Notes |
|-------|--------------------|-----|----------|-------|
| U1    | ESP32 DevKit C v4  | 1   | -        | Main controller |
| U2    | SSD1306 module     | 1   | 128x64   | OLED display |
| Q1,Q2 | 2N2222             | 1   | -        | LED driver |
| Q3    | 2N7000             | 1   | -        | Motor driver |
| D1-D3 | 1N4148             | 3   | -        | Flyback diodes |
| R1-R5 | Resistor           | Various | See schematic | |
| C1-C5 | Capacitor          | Various | See schematic | |
| J1    | USB-C connector    | 1   | -        | Power input |
| J2    | 3.5mm jack         | 1   | -        | Audio output |
| SW1   | Push button        | 1   | -        | User input |
| LED1  | LED + NeoPixel opt | 1   | -        | Visual output |

## Testing Checklist

- [ ] Continuity between all GND nodes
- [ ] No shorts between 3.3V and GND
- [ ] No shorts between 5V and GND
- [ ] GPIO pins can source/sink 5mA
- [ ] I2C communication successful
- [ ] Button debounce working
- [ ] LED/motor responding to GPIO commands
- [ ] OLED displaying text
