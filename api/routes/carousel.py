"""
Carousel Generation API Endpoints
Main endpoints for carousel generation functionality
"""

import logging
import base64
from flask import request, current_app
from flask_restful import Resource
from marshmallow import ValidationError

from ..schemas.carousel import CarouselRequestSchema, ConfigRequestSchema
from ..services.carousel_generator import CarouselGeneratorService
from ..services.ai_config_generator import AIConfigGeneratorService
from ..utils.validators import validate_request_data
from ..utils.responses import success_response, error_response

logger = logging.getLogger(__name__)

class CarouselGenerateResource(Resource):
    """
    Resource for generating carousel images from text and configuration
    """
    
    def __init__(self):
        self.carousel_service = CarouselGeneratorService()
        self.schema = CarouselRequestSchema()
    
    def post(self):
        """
        Generate carousel images from text content
        
        Request Body:
        {
            "text": "Content with slide separators",
            "config": {
                "background_color": "#ffffff",
                "text_color": "#000000",
                "font_size": 44,
                "platform": "instagram_post"
            }
        }
        
        Returns:
        {
            "success": true,
            "data": {
                "total_slides": 3,
                "images": [
                    {
                        "slide_number": 1,
                        "text": "Slide content",
                        "image": "base64_encoded_image",
                        "size": {"width": 1080, "height": 1080}
                    }
                ]
            }
        }
        """
        
        try:
            # Validate request data
            data = validate_request_data(self.schema)
            
            # Extract text and config
            text = data['text']
            config = data.get('config', {})
            
            # Apply default configuration
            final_config = {**current_app.config['DEFAULT_CONFIG'], **config}
            
            # Validate text length
            if len(text) > current_app.config['MAX_TEXT_LENGTH']:
                return error_response(
                    'Text too long',
                    f"Maximum text length is {current_app.config['MAX_TEXT_LENGTH']} characters",
                    400
                )
            
            # Generate carousel
            logger.info(f"Generating carousel with {len(text)} characters of text")
            result = self.carousel_service.generate_carousel(text, final_config)
            
            # Prepare response
            response_data = {
                'total_slides': result['total_slides'],
                'images': []
            }
            
            for i, slide_data in enumerate(result['slides']):
                # Convert image to base64
                image_base64 = base64.b64encode(slide_data['image_bytes']).decode('utf-8')
                
                response_data['images'].append({
                    'slide_number': i + 1,
                    'text': slide_data['text'],
                    'image': image_base64,
                    'size': {
                        'width': slide_data['width'],
                        'height': slide_data['height']
                    }
                })
            
            logger.info(f"Successfully generated {result['total_slides']} slides")
            
            return success_response(
                'Carousel generated successfully',
                response_data
            )
            
        except ValidationError as e:
            logger.warning(f"Validation error: {e.messages}")
            return error_response(
                'Validation failed',
                e.messages,
                400
            )
            
        except Exception as e:
            logger.error(f"Error generating carousel: {str(e)}")
            return error_response(
                'Generation failed',
                'An error occurred while generating the carousel',
                500
            )

class ConfigGenerateResource(Resource):
    """
    Resource for AI-powered configuration generation
    """
    
    def __init__(self):
        self.ai_service = AIConfigGeneratorService()
        self.schema = ConfigRequestSchema()
    
    def post(self):
        """
        Generate design configuration using AI
        
        Request Body:
        {
            "description": "Professional corporate style with blue colors",
            "platform": "linkedin",
            "additional_requirements": "Add company logo"
        }
        
        Returns:
        {
            "success": true,
            "data": {
                "config": {
                    "background_color": "#1e3d59",
                    "text_color": "#ffffff",
                    "font_size": 48
                },
                "explanation": "Generated corporate style configuration"
            }
        }
        """
        
        try:
            # Validate request data
            data = validate_request_data(self.schema)
            
            # Extract parameters
            description = data['description']
            platform = data.get('platform', 'instagram_post')
            additional_requirements = data.get('additional_requirements', '')
            
            # Check if OpenAI API key is configured
            if not current_app.config.get('OPENAI_API_KEY'):
                return error_response(
                    'AI service unavailable',
                    'OpenAI API key not configured',
                    503
                )
            
            # Generate configuration
            logger.info(f"Generating AI config for platform: {platform}")
            result = self.ai_service.generate_config(
                description=description,
                platform=platform,
                additional_requirements=additional_requirements
            )
            
            response_data = {
                'config': result['config'],
                'explanation': result['explanation'],
                'platform_specs': current_app.config['PLATFORM_SPECS'].get(platform, {})
            }
            
            logger.info("Successfully generated AI configuration")
            
            return success_response(
                'Configuration generated successfully',
                response_data
            )
            
        except ValidationError as e:
            logger.warning(f"Validation error: {e.messages}")
            return error_response(
                'Validation failed',
                e.messages,
                400
            )
            
        except Exception as e:
            logger.error(f"Error generating config: {str(e)}")
            return error_response(
                'Generation failed',
                'An error occurred while generating the configuration',
                500
            )

class CarouselFromTextResource(Resource):
    """
    Resource for generating carousel directly from text using AI config
    """
    
    def __init__(self):
        self.carousel_service = CarouselGeneratorService()
        self.ai_service = AIConfigGeneratorService()
    
    def post(self):
        """
        Generate carousel with AI-powered configuration
        
        Request Body:
        {
            "text": "Content with slide separators",
            "description": "Modern minimalist style",
            "platform": "instagram_post"
        }
        """
        
        try:
            data = request.get_json()
            
            if not data or 'text' not in data:
                return error_response(
                    'Missing required data',
                    'Text content is required',
                    400
                )
            
            text = data['text']
            description = data.get('description', 'Modern clean design')
            platform = data.get('platform', 'instagram_post')
            
            # Generate AI configuration
            if current_app.config.get('OPENAI_API_KEY'):
                config_result = self.ai_service.generate_config(
                    description=description,
                    platform=platform
                )
                config = config_result['config']
            else:
                # Fallback to default config
                config = current_app.config['DEFAULT_CONFIG'].copy()
                config.update(current_app.config['PLATFORM_SPECS'].get(platform, {}))
            
            # Generate carousel
            result = self.carousel_service.generate_carousel(text, config)
            
            # Prepare response (similar to CarouselGenerateResource)
            response_data = {
                'total_slides': result['total_slides'],
                'config_used': config,
                'images': []
            }
            
            for i, slide_data in enumerate(result['slides']):
                image_base64 = base64.b64encode(slide_data['image_bytes']).decode('utf-8')
                
                response_data['images'].append({
                    'slide_number': i + 1,
                    'text': slide_data['text'],
                    'image': image_base64,
                    'size': {
                        'width': slide_data['width'],
                        'height': slide_data['height']
                    }
                })
            
            return success_response(
                'Carousel generated successfully with AI configuration',
                response_data
            )
            
        except Exception as e:
            logger.error(f"Error in carousel generation: {str(e)}")
            return error_response(
                'Generation failed',
                str(e),
                500
            )
