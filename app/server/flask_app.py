"""
Flask Background Server for 24/7 Uptime
"""

from flask import Flask, jsonify
import logging

logger = logging.getLogger(__name__)


def create_app():
    """
    Create and configure Flask application.
    
    Returns:
        Flask: Flask application instance
    """
    app = Flask(__name__)
    
    @app.route('/', methods=['GET'])
    def health_check():
        """Health check endpoint."""
        return jsonify({
            "status": "online",
            "service": "Discord Manager Bot",
            "version": "1.0.0"
        }), 200
    
    @app.route('/status', methods=['GET'])
    def status():
        """Get bot status."""
        return jsonify({
            "status": "running",
            "uptime": "active"
        }), 200
    
    @app.route('/ping', methods=['GET'])
    def ping():
        """Ping endpoint for uptime monitoring."""
        return jsonify({"ping": "pong"}), 200
    
    @app.errorhandler(404)
    def not_found(error):
        """Handle 404 errors."""
        return jsonify({"error": "Not found"}), 404
    
    @app.errorhandler(500)
    def server_error(error):
        """Handle 500 errors."""
        logger.error(f"Server error: {error}")
        return jsonify({"error": "Internal server error"}), 500
    
    return app
