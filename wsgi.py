"""
WSGI entry point for the Flask application.
Used by Gunicorn and other WSGI servers.
"""

import os
from app import create_app

# Create Flask application instance
app = create_app(os.environ.get('FLASK_ENV', 'production'))

if __name__ == "__main__":
    app.run()