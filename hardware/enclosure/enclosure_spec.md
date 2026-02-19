# Hardware Enclosure Specification

## Blind Date with Bandwidth - Station Box

### Dimensions
- **Width**: 150mm
- **Depth**: 100mm
- **Height**: 60mm
- **Wall thickness**: 3mm

### Materials
**Primary**: 3mm black acrylic (laser cut) or 3D printed PLA
**Finish**: Matte black with cyan accent trim (1-2mm strips on edges)
**Hardware**: M3 stainless steel bolts, acrylic cement

### Panel Layout

#### Front Face
- **Display**: SSD1306 OLED centered, 28mm x 28mm cutout
  - Position: 61mm from left, 16mm from top
  - Bezel: thin black frame around display
- **Button**: Illuminated push button (16mm diameter)
  - Position: centered below display, 45mm from top
  - LED ring color: changes with pair assignment (red, blue, green, etc.)
- **Headphone Jack**: 3.5mm stereo
  - Position: 120mm from left, 30mm from top
  - Label: "OUT"

#### Back Face
- **Cable Management**: 3x labeled cable ports
  - USB-C power (center)
  - 3.5mm audio input (left)
  - Future expansion (right)
- **Velcro strips**: Internal (not visible) for cable routing

#### Bottom Face
- **Ventilation**: 4x 5mm holes in 10mm spacing pattern
- **Feet**: 4x silicone bumpers (self-adhesive, 8mm diameter)
- **Reset button**: Small reed switch hole (optional, for NVS reset)

#### Top Face
- **Branding**: Engraved "BLIND DATE\nWITH BANDWIDTH"
  - Font: 14pt, sans-serif, 1.5mm deep
  - Position: centered, 3mm from rear edge
- **IEEE ComSoc logo**: 30mm x 30mm etched area (rear corner)
  - File: `hardware/enclosure/ieee_logo.svg`

#### Left & Right Faces
- **Cyan accent strips**: 2mm wide, full height
- **Mounting holes**: For wall mounting (optional)

### Interior Layout
- **PCB mounting**: 4x M3 standoffs, 15mm height
  - Layout: PCB centered, 10mm from bottom
  - Airflow: bottom ventilation holes align with PCB
- **Battery**: 5000mAh USB power bank (fits alongside PCB)
  - Cable: internal USB-C routed to backplate
- **Thermal**: ensure >50mm clearance above hottest component (ESP32)

### Assembly Notes
- Assemble body first (4 walls + bottom), test fit PCB
- Mount display and button on front panel separately
- Install backplate last
- Use acrylic cement on joints, clamp 24 hours
- Silicone bumpers applied after assembly cure

### 3D Printing (PLA Alternative)
- Print supports on interior corners
- 20% infill sufficient
- 0.2mm layer height for smooth OLED window
- Print time: ~8-10 hours per enclosure
- Post-process: sand with 400-grit, paint matte black

### Cost Breakdown
- Laser cut acrylic: ~$15 per unit (qty 10+)
- 3D printing: ~$12 per unit (material) + labor
- Hardware: $2
- Labels/branding: $1
- **Total per unit**: $18-30 (depending on method)