// Blind Date with Bandwidth - Station Enclosure
// Parametric OpenSCAD Design
// Parameters: adjust these values to customize dimensions

// Overall dimensions (mm)
width = 150;
depth = 100;
height = 60;
wall_thickness = 3;
corner_radius = 5;

// Component cutouts
oled_width = 28;
oled_height = 28;
button_diameter = 16;
jack_diameter = 6;

// Ventilation holes
vent_hole_diameter = 5;
vent_spacing = 10;

// Color scheme
color_body = [0, 0, 0];  // Black
color_accent = [0, 0.5, 1];  // Cyan

module rounded_box(w, d, h, r, wall) {
    // Create rounded rectangular box
    minkowski() {
        cube([w - 2*r, d - 2*r, h - 2*r], center=true);
        sphere(r=r);
    }
}

module body() {
    // Outer shell
    difference() {
        rounded_box(width, depth, height, corner_radius, wall_thickness);
        
        // Hollow interior
        rounded_box(
            width - 2*wall_thickness,
            depth - 2*wall_thickness,
            height - wall_thickness, // Leave bottom
            corner_radius - wall_thickness,
            0
        );
    }
}

module front_panel() {
    difference() {
        cube([width, wall_thickness, height], center=true);
        
        // OLED display cutout (centered, 28x28mm)
        translate([0, 0, 0]) {
            cube([oled_width, wall_thickness + 1, oled_height], center=true);
        }
        
        // Button cutout (16mm diameter, centered below display)
        translate([0, -1, -(height/4)]) {
            cylinder(d=button_diameter, h=wall_thickness + 2, center=true);
        }
        
        // Headphone jack (6mm diameter)
        translate([width/2 - 20, -1, 0]) {
            cylinder(d=jack_diameter, h=wall_thickness + 2, center=true);
        }
    }
}

module back_panel() {
    difference() {
        cube([width, wall_thickness, height], center=true);
        
        // USB-C port cutout (10x8mm, centered)
        translate([0, 0, 0]) {
            cube([10, wall_thickness + 1, 8], center=true);
        }
        
        // Ventilation holes (4 holes, 5mm diameter each)
        for (i = [0:3]) {
            x_pos = -width/2 + 30 + (i * vent_spacing);
            translate([x_pos, 0, -height/2 + 10]) {
                cylinder(d=vent_hole_diameter, h=wall_thickness + 1, center=true);
            }
        }
    }
}

module side_panels() {
    // Left panel
    difference() {
        cube([wall_thickness, depth, height], center=true);
        // Mounting holes (optional)
        translate([0, depth/2 - 15, height/2 - 15]) {
            cylinder(d=3, h=wall_thickness + 1, center=true);
        }
    }
    
    // Right panel
    translate([width - wall_thickness, 0, 0]) {
        difference() {
            cube([wall_thickness, depth, height], center=true);
            translate([0, depth/2 - 15, height/2 - 15]) {
                cylinder(d=3, h=wall_thickness + 1, center=true);
            }
        }
    }
}

module bottom_panel() {
    difference() {
        cube([width, depth, wall_thickness], center=true);
        
        // Ventilation holes (arranged in 2x2 grid)
        for (x = [0:1]) {
            for (y = [0:1]) {
                x_pos = -width/4 + (x * width/2);
                y_pos = -depth/4 + (y * depth/2);
                translate([x_pos, y_pos, 0]) {
                    cylinder(d=vent_hole_diameter, h=wall_thickness + 1, center=true);
                }
            }
        }
    }
}

module accent_strips() {
    // Cyan accent strips on edges (cosmetic)
    strip_width = 2;
    
    // Top strips
    color(color_accent) {
        cube([width, strip_width, strip_width], center=true);
        translate([0, 0, height/2 - strip_width/2]) {
            cube([width, strip_width, strip_width], center=true);
        }
    }
}

module pcb_standoffs() {
    // Position and spacing for standoffs
    for (x = [0, 100]) {
        for (y = [0, 60]) {
            x_pos = -width/2 + 20 + x;
            y_pos = -depth/2 + 15 + y;
            translate([x_pos, y_pos, 0]) {
                cylinder(d=3, h=15, center=false);
            }
        }
    }
}

// Main assembly
!color(color_body) {
    body();
    front_panel();
    back_panel();
    side_panels();
    bottom_panel();
}

// Display standoffs (reference only, not part of body)
%pcb_standoffs();

// Render accent strips
%accent_strips();

// Render notes (text annotation)
echo("Enclosure dimensions: 150mm x 100mm x 60mm");
echo("Wall thickness: 3mm");
echo("PCB area: ~80mm x 50mm");
echo("Assembly: Assemble walls, install PCB with standoffs, add panels");
