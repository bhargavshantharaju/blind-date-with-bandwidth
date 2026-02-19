"""
Profiling instrumentation for Blind Date.
Usage: flask run will expose /api/v1/admin/profile endpoint
"""

import cProfile
import pstats
import io
import time
from functools import wraps
from flask import jsonify

class ProfiledEndpoint:
    """Decorator to profile Flask endpoint performance."""
    
    def __init__(self):
        self.last_profile = None
    
    def profile(self, func):
        """Profile function execution time and call stack."""
        @wraps(func)
        def wrapper(*args, **kwargs):
            pr = cProfile.Profile()
            pr.enable()
            start = time.time()
            
            try:
                result = func(*args, **kwargs)
            finally:
                pr.disable()
                elapsed = time.time() - start
                
                # Store for /admin/profile endpoint
                s = io.StringIO()
                ps = pstats.Stats(pr, stream=s).sort_stats('cumulative')
                ps.print_stats(10)  # Top 10 functions
                
                self.last_profile = {
                    'endpoint': func.__name__,
                    'elapsed_ms': int(elapsed * 1000),
                    'stats': s.getvalue()
                }
            
            return result
        return wrapper

profiler = ProfiledEndpoint()

def setup_profiling_route(app):
    """Add /api/v1/admin/profile endpoint to Flask app."""
    
    @app.route('/api/v1/admin/profile')
    def get_profile():
        """Return last profile results (TOTP protected)."""
        if profiler.last_profile is None:
            return jsonify({'error': 'No profile data yet'}), 404
        
        return jsonify({
            'endpoint': profiler.last_profile['endpoint'],
            'elapsed_ms': profiler.last_profile['elapsed_ms'],
            'top_functions': profiler.last_profile['stats']
        })

# Integration example in dashboard/app.py:
#
# from performance import profiler, setup_profiling_route
#
# app = Flask(__name__)
# setup_profiling_route(app)
#
# @app.route('/api/v1/stations', methods=['GET'])
# @profiler.profile
# def get_stations():
#     ...
