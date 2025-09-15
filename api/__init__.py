"""
API Package Initialization
Application factory pattern for Flask app creation
"""

import logging
from flask import Flask
from flask_restful import Api

from .config import Config
from .routes import register_blueprints

def create_app(config_class=Config):
    """
    Application factory function
    
    Args:
        config_class: Configuration class to use
        
    Returns:
        Flask: Configured Flask application instance
    """
    
    # Create Flask application
    app = Flask(__name__)
    
    # Load configuration
    app.config.from_object(config_class)
    
    # Configure logging
    configure_logging(app)
    
    # Register blueprints
    register_blueprints(app)
    
    # Log successful initialization
    logger = logging.getLogger(__name__)
    logger.info("Flask application created successfully")
    
    return app

def configure_logging(app):
    """
    Configure application logging
    
    Args:
        app: Flask application instance
    """
    
    # Set logging level based on debug mode
    if app.debug:
        logging.getLogger().setLevel(logging.DEBUG)
    else:
        logging.getLogger().setLevel(logging.INFO)
    
    # Create formatter
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Configure console handler
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    
    # Add handler to app logger
    app.logger.addHandler(console_handler)
    app.logger.setLevel(logging.INFO)
    
    # Log configuration
    app.logger.info(f"Logging configured - Debug: {app.debug}")
