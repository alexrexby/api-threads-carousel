"""
Routes Package Initialization
Blueprint registration and API routing management
"""

import logging
from flask import Blueprint
from flask_restful import Api

def register_blueprints(app):
    """
    Register all blueprints with the Flask application
    
    Args:
        app: Flask application instance
    """
    
    logger = logging.getLogger(__name__)
    
    # Create main API blueprint
    api_bp = Blueprint('api', __name__, url_prefix=app.config['API_PREFIX'])
    api = Api(api_bp)
    
    # Import and register resources
    try:
        from .carousel import CarouselGenerateResource, ConfigGenerateResource
        from .health import HealthResource, StatusResource
        from .docs import DocumentationResource
        
        # Carousel endpoints
        api.add_resource(
            CarouselGenerateResource, 
            '/generate-carousel',
            endpoint='generate_carousel'
        )
        
        api.add_resource(
            ConfigGenerateResource,
            '/generate-config', 
            endpoint='generate_config'
        )
        
        # Health and status endpoints
        api.add_resource(
            HealthResource,
            '/health',
            endpoint='health'
        )
        
        api.add_resource(
            StatusResource,
            '/status',
            endpoint='status'
        )
        
        # Documentation endpoint
        api.add_resource(
            DocumentationResource,
            '/docs',
            endpoint='docs'
        )
        
        logger.info("API resources registered successfully")
        
    except ImportError as e:
        logger.error(f"Failed to import API resources: {e}")
        raise
    
    # Register the API blueprint
    app.register_blueprint(api_bp)
    logger.info(f"API blueprint registered at {app.config['API_PREFIX']}")
    
    # Register additional blueprints if needed
    register_additional_blueprints(app)

def register_additional_blueprints(app):
    """
    Register additional blueprints for specific functionality
    
    Args:
        app: Flask application instance
    """
    
    logger = logging.getLogger(__name__)
    
    # Example: Admin blueprint (uncomment if needed)
    # try:
    #     from .admin import admin_bp
    #     app.register_blueprint(admin_bp, url_prefix='/admin')
    #     logger.info("Admin blueprint registered")
    # except ImportError:
    #     logger.warning("Admin blueprint not available")
    
    # Example: Webhook blueprint (uncomment if needed)
    # try:
    #     from .webhooks import webhooks_bp
    #     app.register_blueprint(webhooks_bp, url_prefix='/webhooks')
    #     logger.info("Webhooks blueprint registered")
    # except ImportError:
    #     logger.warning("Webhooks blueprint not available")
    
    logger.debug("Additional blueprints registration completed")
