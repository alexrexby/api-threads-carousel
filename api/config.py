"""
Application Configuration
Centralized configuration management for different environments
"""

import os
from datetime import timedelta

class Config:
    """Base configuration class"""
    
    # Flask configuration
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production'
    DEBUG = os.environ.get('FLASK_DEBUG', 'False').lower() == 'true'
    TESTING = False
    
    # API configuration
    API_VERSION = 'v1'
    API_PREFIX = f'/api/{API_VERSION}'
    
    # Server configuration
    HOST = os.environ.get('API_HOST', '0.0.0.0')
    PORT = int(os.environ.get('API_PORT', 5000))
    
    # OpenAI configuration
    OPENAI_API_KEY = os.environ.get('OPENAI_API_KEY')
    OPENAI_MODEL = os.environ.get('OPENAI_MODEL', 'gpt-3.5-turbo')
    OPENAI_MAX_TOKENS = int(os.environ.get('OPENAI_MAX_TOKENS', 1000))
    
    # Image generation settings
    MAX_SLIDES = int(os.environ.get('MAX_SLIDES', 20))
    DEFAULT_IMAGE_WIDTH = int(os.environ.get('DEFAULT_IMAGE_WIDTH', 1080))
    DEFAULT_IMAGE_HEIGHT = int(os.environ.get('DEFAULT_IMAGE_HEIGHT', 1080))
    MAX_IMAGE_SIZE = int(os.environ.get('MAX_IMAGE_SIZE', 10 * 1024 * 1024))  # 10MB
    
    # Font configuration
    DEFAULT_FONT_SIZE = int(os.environ.get('DEFAULT_FONT_SIZE', 44))
    DEFAULT_TITLE_FONT_SIZE = int(os.environ.get('DEFAULT_TITLE_FONT_SIZE', 56))
    FONT_PATH = os.environ.get('FONT_PATH', 'fonts/')
    
    # Text processing
    MAX_TEXT_LENGTH = int(os.environ.get('MAX_TEXT_LENGTH', 10000))
    SLIDE_SEPARATOR = os.environ.get('SLIDE_SEPARATOR', '========')
    
    # Rate limiting
    RATE_LIMIT_PER_MINUTE = int(os.environ.get('RATE_LIMIT_PER_MINUTE', 60))
    RATE_LIMIT_PER_HOUR = int(os.environ.get('RATE_LIMIT_PER_HOUR', 1000))
    
    # Caching (if Redis is used)
    CACHE_TYPE = os.environ.get('CACHE_TYPE', 'simple')
    CACHE_DEFAULT_TIMEOUT = int(os.environ.get('CACHE_DEFAULT_TIMEOUT', 3600))
    REDIS_URL = os.environ.get('REDIS_URL', 'redis://localhost:6379/0')
    
    # Background jobs (if Celery is used)
    CELERY_BROKER_URL = os.environ.get('CELERY_BROKER_URL', 'redis://localhost:6379/0')
    CELERY_RESULT_BACKEND = os.environ.get('CELERY_RESULT_BACKEND', 'redis://localhost:6379/0')
    
    # Monitoring and logging
    LOG_LEVEL = os.environ.get('LOG_LEVEL', 'INFO')
    SENTRY_DSN = os.environ.get('SENTRY_DSN')
    
    # Security
    MAX_CONTENT_LENGTH = int(os.environ.get('MAX_CONTENT_LENGTH', 16 * 1024 * 1024))  # 16MB
    
    # Social media platform specifications
    PLATFORM_SPECS = {
        'instagram_post': {'width': 1080, 'height': 1080, 'aspect_ratio': '1:1'},
        'instagram_story': {'width': 1080, 'height': 1920, 'aspect_ratio': '9:16'},
        'linkedin': {'width': 1080, 'height': 1080, 'aspect_ratio': '1:1'},
        'tiktok': {'width': 1080, 'height': 1350, 'aspect_ratio': '4:5'},
        'twitter': {'width': 1024, 'height': 512, 'aspect_ratio': '2:1'},
        'facebook': {'width': 1200, 'height': 630, 'aspect_ratio': '1.91:1'}
    }
    
    # Default carousel configuration
    DEFAULT_CONFIG = {
        'background_color': '#ffffff',
        'text_color': '#000000',
        'font_size': DEFAULT_FONT_SIZE,
        'title_font_size': DEFAULT_TITLE_FONT_SIZE,
        'padding': 80,
        'corner_radius': 0,
        'add_page_numbers': False,
        'add_logo_text': False,
        'logo_text': '',
        'platform': 'instagram_post'
    }
    
    @staticmethod
    def init_app(app):
        """Initialize application with this configuration"""
        pass

class DevelopmentConfig(Config):
    """Development configuration"""
    DEBUG = True
    LOG_LEVEL = 'DEBUG'

class ProductionConfig(Config):
    """Production configuration"""
    DEBUG = False
    LOG_LEVEL = 'INFO'
    
    @classmethod
    def init_app(cls, app):
        Config.init_app(app)
        
        # Log to stderr in production
        import logging
        from logging import StreamHandler
        file_handler = StreamHandler()
        file_handler.setLevel(logging.INFO)
        app.logger.addHandler(file_handler)

class TestingConfig(Config):
    """Testing configuration"""
    TESTING = True
    DEBUG = True
    LOG_LEVEL = 'DEBUG'

# Configuration mapping
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}
