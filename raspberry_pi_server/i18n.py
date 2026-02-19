"""
Internationalization (i18n) setup for Blind Date.
Supports 6 languages: EN, ES, FR, DE, JA, HI
"""

from flask_babel import Babel, lazy_gettext
from flask import request

babel = None

def init_i18n(app):
    """Initialize Flask-Babel with supported locales."""
    global babel
    babel = Babel(app)
    
    # Supported languages
    app.config['LANGUAGES'] = {
        'en': 'English',
        'es': 'Español',
        'fr': 'Français',
        'de': 'Deutsch',
        'ja': '日本語',
        'hi': 'हिन्दी'
    }
    
    @babel.localeselector
    def get_locale():
        # Priority: URL parameter > Accept-Language header > default (en)
        if 'lang' in request.args:
            lang = request.args.get('lang')
            if lang in app.config['LANGUAGES']:
                return lang
        
        # Accept-Language header
        return request.accept_languages.best_match(app.config['LANGUAGES'].keys()) or 'en'

# String catalog for translation
UI_STRINGS = {
    'title': lazy_gettext('Blind Date with Bandwidth'),
    'subtitle': lazy_gettext('Match on Random Tracks'),
    'select_track': lazy_gettext('Select your track'),
    'waiting': lazy_gettext('Waiting for match...'),
    'matched': lazy_gettext('Match found!'),
    'mismatch': lazy_gettext('No match :('),
    'timeout': lazy_gettext('Session timeout'),
    'sync_time': lazy_gettext('Sync time'),
    'ms': lazy_gettext('ms'),
    'station': lazy_gettext('Station'),
    'leaderboard': lazy_gettext('Leaderboard'),
    'tournament': lazy_gettext('Tournament'),
    'round': lazy_gettext('Round'),
    'winner': lazy_gettext('Winner'),
    'track_1': lazy_gettext('Electric Pulse'),
    'track_2': lazy_gettext('Cosmic Journey'),
    'track_3': lazy_gettext('Urban Rhythm'),
    'track_4': lazy_gettext('Ethereal Waves'),
    'track_5': lazy_gettext('Retro Synth'),
}

# Usage in Flask templates:
# {{ _('Waiting for match...') }}
# {{ UI_STRINGS['waiting'] }}

# Usage in Python code:
# from flask_babel import gettext as _
# message = _('Sync time: %(time)dms', time=125)
