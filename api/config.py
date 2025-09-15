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
    
    # Google Fonts configuration
    GOOGLE_FONTS_API_KEY = os.environ.get('GOOGLE_FONTS_API_KEY')
    DEFAULT_FONT_FAMILY = os.environ.get('DEFAULT_FONT_FAMILY', 'Inter')
    DEFAULT_FONT_WEIGHT = os.environ.get('DEFAULT_FONT_WEIGHT', '400')
    TITLE_FONT_WEIGHT = os.environ.get('TITLE_FONT_WEIGHT', '600')
    
    # Image generation settings
    MAX_SLIDES = int(os.environ.get('MAX_SLIDES', 20))
    DEFAULT_IMAGE_WIDTH = int(os.environ.get('DEFAULT_IMAGE_WIDTH', 1080))
    DEFAULT_IMAGE_HEIGHT = int(os.environ.get('DEFAULT_IMAGE_HEIGHT', 1080))
    MAX_IMAGE_SIZE = int(os.environ.get('MAX_IMAGE_SIZE', 10 * 1024 * 1024))  # 10MB
    
    # Font configuration
    DEFAULT_FONT_SIZE = int(os.environ.get('DEFAULT_FONT_SIZE', 44))
    DEFAULT_TITLE_FONT_SIZE = int(os.environ.get('DEFAULT_TITLE_FONT_SIZE', 56))
    FONT_PATH = os.environ.get('FONT_PATH', 'fonts/')
    FONTS_CACHE_DIR = os.environ.get('FONTS_CACHE_DIR', 'fonts/cache/')
    
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
    
    # Google Fonts популярные шрифты по категориям
    POPULAR_FONTS = {
        'sans-serif': [
            {'family': 'Inter', 'weights': ['300', '400', '500', '600', '700'], 'description': 'Modern, clean, excellent readability'},
            {'family': 'Roboto', 'weights': ['300', '400', '500', '700'], 'description': 'Google\'s signature font, versatile'},
            {'family': 'Open Sans', 'weights': ['300', '400', '600', '700'], 'description': 'Friendly, readable, professional'},
            {'family': 'Lato', 'weights': ['300', '400', '700'], 'description': 'Elegant, humanist sans-serif'},
            {'family': 'Montserrat', 'weights': ['300', '400', '500', '600', '700'], 'description': 'Modern, geometric, bold'},
            {'family': 'Poppins', 'weights': ['300', '400', '500', '600', '700'], 'description': 'Rounded, friendly, modern'},
            {'family': 'Source Sans Pro', 'weights': ['300', '400', '600', '700'], 'description': 'Clean, technical, reliable'},
            {'family': 'Nunito', 'weights': ['300', '400', '600', '700'], 'description': 'Rounded, warm, friendly'},
            {'family': 'Raleway', 'weights': ['300', '400', '500', '600', '700'], 'description': 'Elegant, sophisticated'},
            {'family': 'Work Sans', 'weights': ['300', '400', '500', '600', '700'], 'description': 'Optimized for screens'}
        ],
        'serif': [
            {'family': 'Playfair Display', 'weights': ['400', '500', '600', '700'], 'description': 'Elegant, high contrast, luxury'},
            {'family': 'Merriweather', 'weights': ['300', '400', '700'], 'description': 'Readable, traditional, trustworthy'},
            {'family': 'Lora', 'weights': ['400', '500', '600', '700'], 'description': 'Contemporary, calligraphic'},
            {'family': 'Crimson Text', 'weights': ['400', '600', '700'], 'description': 'Classic, academic, readable'},
            {'family': 'EB Garamond', 'weights': ['400', '500', '600', '700'], 'description': 'Classic, elegant, scholarly'},
            {'family': 'Libre Baskerville', 'weights': ['400', '700'], 'description': 'Traditional, reliable, classic'},
        ],
        'display': [
            {'family': 'Oswald', 'weights': ['300', '400', '500', '600', '700'], 'description': 'Bold, condensed, impactful'},
            {'family': 'Bebas Neue', 'weights': ['400'], 'description': 'Strong, condensed, attention-grabbing'},
            {'family': 'Anton', 'weights': ['400'], 'description': 'Bold, condensed, powerful'},
            {'family': 'Righteous', 'weights': ['400'], 'description': 'Bold, friendly, rounded'},
        ]
    }
    
    # Default carousel configuration with Google Fonts
    DEFAULT_CONFIG = {
        'background_color': '#ffffff',
        'text_color': '#000000',
        'font_family': DEFAULT_FONT_FAMILY,
        'font_weight': DEFAULT_FONT_WEIGHT,
        'title_font_weight': TITLE_FONT_WEIGHT,
        'font_size': DEFAULT_FONT_SIZE,
        'title_font_size': DEFAULT_TITLE_FONT_SIZE,
        'padding': 80,
        'corner_radius': 0,
        'line_spacing': 1.2,
        'text_align': 'left',
        'add_page_numbers': False,
        'add_logo_text': False,
        'logo_text': '',
        'platform': 'instagram_post'
    }
    
    # Font configurations by platform
    PLATFORM_FONT_CONFIGS = {
        'instagram_post': {
            'recommended_fonts': ['Inter', 'Poppins', 'Montserrat'],
            'font_size_range': (40, 60),
            'title_size_range': (56, 80)
        },
        'instagram_story': {
            'recommended_fonts': ['Inter', 'Roboto', 'Open Sans'],
            'font_size_range': (45, 65),
            'title_size_range': (60, 85)
        },
        'linkedin': {
            'recommended_fonts': ['Inter', 'Source Sans Pro', 'Lato'],
            'font_size_range': (42, 58),
            'title_size_range': (58, 75)
        },
        'tiktok': {
            'recommended_fonts': ['Poppins', 'Nunito', 'Montserrat'],
            'font_size_range': (44, 64),
            'title_size_range': (60, 82)
        }
    }
    
    @staticmethod
    def init_app(app):
        """Initialize application with this configuration"""
        # Создать директории для шрифтов
        font_dirs = [
            app.config.get('FONT_PATH', 'fonts/'),
            app.config.get('FONTS_CACHE_DIR', 'fonts/cache/')
        ]
        
        for font_dir in font_dirs:
            if not os.path.exists(font_dir):
                os.makedirs(font_dir, exist_ok=True)

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
    # Use local fonts for testing, not Google Fonts
    GOOGLE_FONTS_API_KEY = None

# Configuration mapping
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}
