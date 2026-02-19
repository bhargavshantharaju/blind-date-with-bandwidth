# Open Hardware Declaration

**Blind Date with Bandwidth** is licensed under [CERN Open Hardware License v2](https://ohwr.org/cern_ohl_s_v2.txt) (CERN-OHL-S).

## What This Means

✓ **You can:**
- Build and reproduce this device for any purpose
- Modify the hardware design and share improvements
- Manufacture and sell derivatives
- Use for commercial applications

✗ **You must:**
- Distribute your changes under the same CERN-OHL-S license
- Provide access to design files (Gerber, OpenSCAD, schematics)
- Document modifications clearly
- Credit original authors

## Design Files Included

All design files are available in `hardware/` directory:

### PCB / Schematic
- `hardware/pcb/README.md` - Fritzing-style schematic in plain text
- Component-level design with all GPIO mappings
- Bill of Materials (BOM) with supplier links
- Can be converted to KiCad, Eagle, or LTspice

### Mechanical Design
- `hardware/enclosure/station_box.scad` - OpenSCAD parametric model
- Laser-cut acrylic specification (3mm walls)
- 3D-printable STL export instructions
- Cost analysis ($18-30/unit in volume)

### Electrical Specifications
- `hardware/power_budget.md` - Power consumption analysis
- Thermal stress tests
- Supply requirement calculations

## How to Reproduce

1. Order PCB from your favorite fab (Gerber files in `hardware/pcb/`)
2. Assemble per BOM (ESP32, OLED, vibration motor, I2C pull-ups)
3. 3D print or laser-cut enclosure using OpenSCAD design
4. Program ESP32 with `esp32_firmware/main.ino`
5. Deploy on Raspberry Pi running Python server

**Total cost per station**: $35-50 (quantities of 10+)
**Build time**: 2 hours assembly + 30 mins programming

## Attribution

If you modify and redistribute:

```
[Your Name] - Blind Date with Bandwidth Station v2.1
Based on [Original Authors] Blind Date with Bandwidth
Licensed under CERN-OHL-S v2
https://github.com/[repo]/hardware
```

## Support for Derivatives

We encourage community improvements! To submit changes:
1. Fork the repository
2. Create feature branch with hardware changes
3. Include photos/video of functioning device
4. Submit PR with documentation of improvements

## Funding / Production

Want to mass-produce? The CERN-OHL-S license permits manufacturing and sales of derivatives. Some manufacturers have offered:

- Pre-assembled stations ($60-80 retail)
- Educational kits ($45 with learning materials)
- Conference booth rentals (contact maintainers)
