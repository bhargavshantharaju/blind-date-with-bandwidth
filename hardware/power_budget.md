# Power Budget Analysis

## Component Power Consumption

### Microcontroller & Connectivity

| Component | State | Current (mA) | Notes |
|-----------|-------|--------------|-------|
| ESP32 (CPU) | Active, 240MHz | 240 | Both cores running |
| ESP32 | Light sleep | 10 | WiFi off |
| ESP32 | Deep sleep | 0.01 | Ultra low power |
| WiFi (active tx) | Transmitting | 225 | At full power |
| WiFi (listen) | Scanning/receiving | 80 | Monitoring for packets |

### Display & Visual Output

| Component | State | Current (mA) | Notes |
|-----------|-------|--------------|-------|
| SSD1306 OLED | Full brightness (all white) | 25 | 128x64 pixels on |
| SSD1306 | Typical mixed content | 15 | Dashboard display |
| SSD1306 | Low brightness (10%) | 5 | Minimal visibility |
| Regular LED | On (20mA standard) | 20 | Blue/white LED |
| NeoPixel RGB | Full white | 60 | All channels max |
| NeoPixel RGB | One pair color (e.g., red) | 20 | Single color |

### Audio & Haptics

| Component | State | Current (mA) | Notes |
|-----------|-------|--------------|-------|
| Vibration motor | Full vibration | 150 | Peak current |
| Vibration motor | Gentle pulse | 50 | 30% duty cycle |
| Headphones (32Ω) | Playing audio | 40 | (Depends on impedance) |
| Headphones (80Ω) | Playing audio | 20 | Higher impedance = more efficient |

## System Power Scenarios

### Scenario 1: Idle Scanning
**Station waiting for lock, listening for MQTT**

```
ESP32 (WiFi listen)              80 mA
OLED display (dim, "SCANNING")   8 mA
LED slow blink                   10 mA (averaged)
NeoPixel (pair color)            15 mA

TOTAL IDLE POWER:              113 mA
```

### Scenario 2: Matched & Streaming Audio
**Both stations locked, voice bridging active**

```
ESP32 (active, maintaining session)  240 mA
WiFi (periodic sync packets)        100 mA (averaged)
OLED display (bright, "SYNCED!")     20 mA
LED fast blink                       15 mA (averaged)
Vibration motor (pulsing)            30 mA (averaged)
Headphones (audio stream)            40 mA
NeoPixel (bright color)              25 mA

TOTAL ACTIVE POWER:               470 mA
```

### Scenario 3: Peak Demand
**All systems at maximum simultaneously**

```
ESP32 (full CPU)                   240 mA
WiFi (transmitting)                225 mA
OLED (full brightness)              25 mA
LED (on max)                        20 mA
Vibration motor (full)             150 mA
Headphones (loud audio)             40 mA
NeoPixel (full white)               60 mA

TOTAL PEAK POWER:                 760 mA
```

## Power Supply Recommendations

### Standard Deployment (Wall/Fixed Power)

```
Supply: 5V / 2A USB Power Adapter
Connector: USB-C (preferred) or Micro-USB

Recommended brands:
  - Anker PowerCore (any model with 2A output)
  - Samsung 25W
  - Apple 20W
  
Cable: USB-C 2.0, AWG 20 or better (minimize voltage drop)
```

### Mobile/Demo Booth (Battery Powered)

```
Supply: 5000mAh USB Power Bank
Supply Voltage: 5V (standard)

Charging time:     ~2.5 hours (with 2A charger)
Runtime (idle):    ~44 hours   (5000mAh / 113mA)
Runtime (mixed):   ~11 hours   (5000mAh / 470mA ~= avg peak)
Runtime (peak):    ~6.5 hours  (5000mAh / 760mA)
```

### IEEE Demo Day Duration
**Assuming 8-hour event with mixed activity pattern:**

```
Timeline:
  00:00-01:00   Idle setup/testing              ~113 mA avg
  01:00-08:00   Active demos (60% active/40% idle)
                Weighted avg: 0.6 × 470 + 0.4 × 113 = 380 mA

Total energy: 8 hours × 380 mA = 3,040 mAh
5000 mAh battery capacity:       ✓ Sufficient with margin
```

## Electrical Design Considerations

### Voltage Regulation

```
5V Input → [1000µF bulk cap] → Voltage Regulator → 3.3V output

Recommended regulator: LDO (Low Dropout)
  - AMS1117 (stable, proven)
  - LD1117 (automotive grade)
  - SPX3819 (lower dropout, less heat)

Max dropout: 0.5V at 500mA
Minimum input: 3.8V (with 3.3V output)
Heat dissipation: (Vin - Vout) × Iout = (5 - 3.3) × 0.5A = 0.85W

With proper thermal design, no heatsink needed. Mount on copper pour.
```

### Bulk Capacitor Sizing

```
Purpose: Stabilize 5V rail during transient loads (motor startup, WiFi tx)

Minimum calculation:
  ΔI(di/dt) during motor startup: ~150mA / 100µs = 1500 A/s
  ΔV allowed: ~0.2V
  C = ΔI / (dV/dt) = 1500 A/s / (0.2V) = 7500 µF

Recommended: 1000µF (conservative, low-cost aluminum electrolytic)
Alternative: 2x 470µF (redundancy, better ESR)

ESR must be <50 mΩ at 100kHz for effective ripple filtering.
```

### Current Path Optimization

```
Power distribution best practices:
  1. All ground returns to GND plane
  2. 5V tracks ≥0.5mm width (for 1A+)
  3. Decoupling caps within 5mm of component VDD
  4. Motor/LED drivers close to power supply
  5. WiFi module isolated on separate power domain if possible
  
Motor current spike mitigation:
  - 100µF cap near motor driver gate
  - Slow PWM ramp-up (avoid sudden 150mA surge)
```

## Thermal Dissipation

### Heat Generation
```
Linear regulator:
  P = (Vin - Vout) × Iout = (5 - 3.3) × 0.5 = 0.85W
  This is acceptable for standard 5mm regulator IC.

Continuous operation: Regulator ≈ 50°C above ambient
Peak operation:       Regulator ≈ 70°C above ambient (still safe, <125°C max)

Thermal management:
  - Mount on copper pour (large ground plane)
  - No heatsink required for 0.85W
  - Ensure adequate airflow (4mm ventilation holes on enclosure)
```

## Efficiency Analysis

```
System efficiency (5V in to 3.3V out at 500mA):
  Output power:  3.3V × 0.5A = 1.65W
  Input power:   5.0V × 0.5A = 2.50W
  Efficiency:    1.65 / 2.50 = 66%

This is reasonable for an LDO regulator. Alternatives:
  - Switching buck-converter: ~85% (more complex)
  - Best compromise: LDO for simplicity + low EMI
```

## Long-Term Monitoring

### Power Consumption Log
For each demo session, record:
```
[timestamp] idle_mA active_mA peak_mA battery_level notes
[10:15] 115 470 580 100% "Session 1 - good sync"
[11:00] 120 475 590 85%  "Session 2 - normal"
[12:30] 118 480 600 70%  "Session 3 - battery warming"
```

This data helps predict battery life and identify component failures early.

## Summary

| Metric | Value |
|--------|-------|
| Idle power | ~113 mA |
| Active power | ~470 mA (typical event) |
| Peak power | ~760 mA (all systems max) |
| Recommended PSU | 5V/2A (wall) or 5000mAh USB (battery) |
| 8-hour event battery | ✓ Sufficient |
| Regulator dissipation | <1W (no heatsink needed) |
| System efficiency | ~66% (LDO) |
