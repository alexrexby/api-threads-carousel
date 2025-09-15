#!/usr/bin/env python3
"""
API Threads Carousel Generator
Main application entry point
"""

import os
import logging
from flask import Flask
from flask_cors import CORS
from dotenv import load_dotenv

from api import create_app
from api.config import Config

# Load environment variables
load_dotenv()

def main():
    """Main application entry point"""
    
    # Create Flask application
    app = create_app()
    
    # Configure CORS
    CORS(app, resources={
        r"/api/*": {
            "origins": ["*"],
            "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
            "allow_headers": ["Content-Type", "Authorization"]
        }
    })
    
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Get configuration
    host = os.getenv('API_HOST', '0.0.0.0')
    port = int(os.getenv('API_PORT', 5000))
    debug = os.getenv('FLASK_DEBUG', 'False').lower() == 'true'
    
    # Health check endpoint
    @app.route('/health')
    def health_check():
        """Health check endpoint"""
        return {
            'status': 'healthy',
            'version': '1.0.0',
            'service': 'carousel-api'
        }
    
    # Root endpoint with API documentation
    @app.route('/')
    def root():
        """Root endpoint with basic API info"""
        return {
            'name': 'API Threads Carousel Generator',
            'version': '1.0.0',
            'description': 'Powerful API for generating social media carousels',
            'endpoints': {
                'health': '/health',
                'generate_carousel': '/api/v1/generate-carousel',
                'generate_config': '/api/v1/generate-config',
                'documentation': '/api/v1/docs'
            },
            'github': 'https://github.com/yourusername/api-threads-carousel',
            'support': 'support@apithreads.ru'
        }
    
    # Error handlers
    @app.errorhandler(404)
    def not_found(error):
        return {'error': 'Endpoint not found'}, 404
    
    @app.errorhandler(500)
    def internal_error(error):
        return {'error': 'Internal server error'}, 500
    
    @app.errorhandler(400)
    def bad_request(error):
        return {'error': 'Bad request'}, 400
    
    # Log startup information
    logger = logging.getLogger(__name__)
    logger.info(f"Starting Carousel API on {host}:{port}")
    logger.info(f"Debug mode: {debug}")
    logger.info(f"Environment: {os.getenv('FLASK_ENV', 'development')}")
    
    # Run the application
    try:
        app.run(
            host=host,
            port=port,
            debug=debug,
            threaded=True
        )
    except Exception as e:
        logger.error(f"Failed to start application: {e}")
        raise

if __name__ == '__main__':
    main()
