"""
Ethical design features for Blind Date.
Colorblind-safe palette, accessibility, consent management.
"""

# Colorblind-safe palette (Okabe-Ito, proven for deuteranopia & protanopia)
COLORBLIND_PALETTE = {
    'primary': '#0173B2',      # Blue (safe for all types)
    'secondary': '#DE8F05',    # Orange (high contrast with blue)
    'success': '#2CAF42',      # Green (saturated, visible)
    'warning': '#CA9161',      # Brown
    'error': '#EE7733',        # Red-orange
    'muted': '#CCCCCC',        # Gray
}

# Standard accessibility palette (for comparison)
STANDARD_PALETTE = {
    'primary': '#0066CC',      # Blue
    'secondary': '#FF6600',    # Orange
    'success': '#00AA00',      # Green
    'warning': '#FFAA00',      # Amber
    'error': '#FF0000',        # Red
    'muted': '#999999',        # Gray
}

# UI Component Contrast Ratios (WCAG AA compliant)
CONTRAST_REQUIREMENTS = {
    'text_on_white': 4.5,      # At least 4.5:1
    'ui_components': 3.0,      # At least 3:1
    'large_text': 3.0,         # Large (18pt+)
}

class AccessibilityAssets:
    """Generate accessible UI assets."""
    
    @staticmethod
    def get_color(palette_name: str, role: str) -> str:
        """Get color for given role from palette."""
        if palette_name == 'colorblind':
            palette = COLORBLIND_PALETTE
        else:
            palette = STANDARD_PALETTE
        
        return palette.get(role, '#000000')
    
    @staticmethod
    def get_neoPixel_colors() -> dict:
        """NeoPixel LED colors for tournament bracket (colorblind-safe)."""
        return {
            0: (1, 150, 200),      # Cyan - Station A
            1: (220, 120, 10),     # Orange - Station B
            2: (100, 200, 80),     # Green - Station C
            3: (180, 100, 200),    # Magenta - Station D
            4: (200, 180, 10),     # Yellow - Station E
            5: (50, 180, 230),     # Bright blue - Station F
            6: (220, 100, 100),    # Light red - Station G
            7: (150, 150, 150),    # Gray - Station H
        }

class ConsentManagement:
    """Manage participant consent for data collection."""
    
    def __init__(self):
        self.consents_given = set()  # Set of station_ids who consented
    
    def show_consent_prompt(self) -> str:
        """Display on spectator screen before joining."""
        return """
        ╔════════════════════════════════════════╗
        ║  BLIND DATE WITH BANDWIDTH             ║
        ║  IEEE ComSoc Demo                      ║
        ╚════════════════════════════════════════╝
        
        Your participation is anonymous and optional.
        
        ✓ Audio is NOT recorded or stored
        ✓ No personal data collected
        ✓ Match results displayed during event only
        ✓ Anonymized statistics may be published
        
        [ ] I consent to participate
        
        Learn more: app.local/privacy
        """
    
    def record_consent(self, station_id: str) -> bool:
        """Record participant consent."""
        self.consents_given.add(station_id)
        return True
    
    def is_consented(self, station_id: str) -> bool:
        """Check if station has consented."""
        return station_id in self.consents_given

class AccessibilityFeatures:
    """Accessibility features for UI."""
    
    @staticmethod
    def get_font_specs() -> dict:
        """Font sizing for accessibility."""
        return {
            'body': '16px',              # Minimum 16px for readability
            'heading1': '32px',          # Large heading
            'heading2': '24px',
            'small': '14px',
            'line_height': '1.5',        # Adequate spacing
        }
    
    @staticmethod
    def get_focus_indicators() -> dict:
        """High-contrast focus indicators for keyboard navigation."""
        return {
            'outline_color': '#0173B2',
            'outline_width': '3px',
            'outline_style': 'solid',
            'outline_offset': '2px',
        }
    
    @staticmethod
    def get_aria_labels() -> dict:
        """ARIA labels for screen readers."""
        return {
            'track_button': 'Select track %(track_num)s',
            'match_status': 'You matched with station %(station_id)s in %(ms)dms',
            'leaderboard': 'Leaderboard showing fastest %(count)s stations',
            'tournament': 'Tournament round %(round)d of %(total)d',
        }

# CSS Variables for easy switching
CSS_ACCESSIBILITY = """
:root {
  --color-primary: #0173B2;
  --color-secondary: #DE8F05;
  --color-text: #000000;
  --color-bg: #FFFFFF;
  --color-border: #CCCCCC;
  
  --text-size-body: 16px;
  --text-size-heading: 32px;
  --text-line-height: 1.5;
  
  --focus-outline: 3px solid #0173B2;
}

/* High contrast mode (user preference) */
@media (prefers-contrast: more) {
  :root {
    --color-text: #000000;
    --color-bg: #FFFFFF;
    --text-size-body: 18px;
  }
}

/* Reduced motion preference */
@media (prefers-reduced-motion: reduce) {
  * {
    animation: none !important;
    transition: none !important;
  }
}
"""

consent_manager = ConsentManagement()
