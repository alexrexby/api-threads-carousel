"""
Fonts API Endpoints
API endpoints for managing Google Fonts
"""

import logging
from flask import current_app
from flask_restful import Resource
from marshmallow import ValidationError

from ..services.carousel_generator import CarouselGeneratorService
from ..utils.responses import success_response, error_response

logger = logging.getLogger(__name__)

class FontsListResource(Resource):
    """
    Resource for getting available Google Fonts
    """
    
    def __init__(self):
        self.carousel_service = CarouselGeneratorService()
    
    def get(self):
        """
        Get list of available Google Fonts
        
        Returns:
        {
            "success": true,
            "data": {
                "fonts": [
                    {
                        "family": "Inter",
                        "category": "sans-serif",
                        "variants": ["300", "400", "500", "600", "700"],
                        "description": "Modern, clean, excellent readability"
                    }
                ],
                "popular_by_category": {
                    "sans-serif": [...],
                    "serif": [...],
                    "display": [...]
                }
            }
        }
        """
        
        try:
            # Получить список Google Fonts
            google_fonts = self.carousel_service.get_available_google_fonts()
            
            # Получить популярные шрифты по категориям из конфигурации
            popular_fonts = current_app.config.get('POPULAR_FONTS', {})
            
            # Получить рекомендации по платформам
            platform_configs = current_app.config.get('PLATFORM_FONT_CONFIGS', {})
            
            response_data = {
                'fonts': google_fonts,
                'popular_by_category': popular_fonts,
                'platform_recommendations': platform_configs,
                'total_fonts': len(google_fonts)
            }
            
            return success_response(
                'Fonts list retrieved successfully',
                response_data
            )
            
        except Exception as e:
            logger.error(f"Error getting fonts list: {str(e)}")
            return error_response(
                'Failed to retrieve fonts list',
                str(e),
                500
            )

class FontPreviewResource(Resource):
    """
    Resource for generating font preview images
    """
    
    def __init__(self):
        self.carousel_service = CarouselGeneratorService()
    
    def post(self):
        """
        Generate font preview image
        
        Request Body:
        {
            "font_family": "Inter",
            "font_weight": "400",
            "text": "Sample Text",
            "background_color": "#ffffff",
            "text_color": "#000000",
            "font_size": 48
        }
        
        Returns:
        {
            "success": true,
            "data": {
                "image": "base64_encoded_image",
                "font_info": {
                    "family": "Inter",
                    "weight": "400",
                    "size": 48
                }
            }
        }
        """
        
        try:
            from flask import request
            import base64
            
            data = request.get_json()
            if not data:
                return error_response('Request data is required', status_code=400)
            
            # Параметры по умолчанию
            font_family = data.get('font_family', 'Inter')
            font_weight = data.get('font_weight', '400')
            text = data.get('text', 'Sample Text')
            bg_color = data.get('background_color', '#ffffff')
            text_color = data.get('text_color', '#000000')
            font_size = data.get('font_size', 48)
            
            # Создать конфигурацию для превью
            preview_config = {
                'background_color': bg_color,
                'text_color': text_color,
                'font_family': font_family,
                'font_weight': font_weight,
                'font_size': font_size,
                'title_font_size': font_size,
                'padding': 40,
                'corner_radius': 8,
                'text_align': 'center',
                'platform': 'custom'
            }
            
            # Подготовить шрифты
            self.carousel_service._prepare_fonts(preview_config)
            
            # Создать превью изображение
            image_bytes = self.carousel_service._create_slide_image(
                text=text,
                config=preview_config,
                width=400,
                height=200,
                slide_number=1,
                total_slides=1
            )
            
            # Конвертировать в base64
            image_base64 = base64.b64encode(image_bytes).decode('utf-8')
            
            response_data = {
                'image': image_base64,
                'font_info': {
                    'family': font_family,
                    'weight': font_weight,
                    'size': font_size
                },
                'preview_text': text
            }
            
            return success_response(
                'Font preview generated successfully',
                response_data
            )
            
        except Exception as e:
            logger.error(f"Error generating font preview: {str(e)}")
            return error_response(
                'Failed to generate font preview',
                str(e),
                500
            )

class FontRecommendationsResource(Resource):
    """
    Resource for getting font recommendations
    """
    
    def get(self):
        """
        Get font recommendations by platform or style
        
        Query Parameters:
        - platform: instagram_post, linkedin, etc.
        - style: modern, classic, elegant, etc.
        - category: sans-serif, serif, display
        
        Returns:
        {
            "success": true,
            "data": {
                "recommendations": [
                    {
                        "family": "Inter",
                        "reason": "Excellent readability for social media",
                        "weights": ["400", "600"],
                        "use_cases": ["titles", "body_text"]
                    }
                ]
            }
        }
        """
        
        try:
            from flask import request
            
            platform = request.args.get('platform', 'instagram_post')
            style = request.args.get('style', 'modern')
            category = request.args.get('category', 'sans-serif')
            
            recommendations = self._get_font_recommendations(platform, style, category)
            
            response_data = {
                'recommendations': recommendations,
                'platform': platform,
                'style': style,
                'category': category
            }
            
            return success_response(
                'Font recommendations retrieved successfully',
                response_data
            )
            
        except Exception as e:
            logger.error(f"Error getting font recommendations: {str(e)}")
            return error_response(
                'Failed to get font recommendations',
                str(e),
                500
            )
    
    def _get_font_recommendations(self, platform: str, style: str, category: str) -> list:
        """
        Generate font recommendations based on criteria
        
        Args:
            platform: Target platform
            style: Desired style
            category: Font category
            
        Returns:
            List of font recommendations
        """
        
        recommendations = []
        popular_fonts = current_app.config.get('POPULAR_FONTS', {})
        
        # Рекомендации по стилю
        style_recommendations = {
            'modern': ['Inter', 'Poppins', 'Montserrat', 'Work Sans'],
            'classic': ['Merriweather', 'Lora', 'Libre Baskerville', 'EB Garamond'],
            'elegant': ['Playfair Display', 'Raleway', 'Crimson Text', 'Lato'],
            'bold': ['Oswald', 'Bebas Neue', 'Anton', 'Righteous'],
            'friendly': ['Nunito', 'Open Sans', 'Poppins', 'Source Sans Pro'],
            'professional': ['Inter', 'Source Sans Pro', 'Lato', 'Roboto']
        }
        
        # Рекомендации по платформе
        platform_recommendations = {
            'instagram_post': ['Inter', 'Poppins', 'Montserrat', 'Nunito'],
            'instagram_story': ['Oswald', 'Bebas Neue', 'Poppins', 'Montserrat'],
            'linkedin': ['Inter', 'Source Sans Pro', 'Lato', 'Merriweather'],
            'tiktok': ['Poppins', 'Nunito', 'Oswald', 'Righteous'],
            'twitter': ['Inter', 'Roboto', 'Open Sans', 'Lato'],
            'facebook': ['Open Sans', 'Roboto', 'Lato', 'Nunito']
        }
        
        # Объединить рекомендации
        style_fonts = style_recommendations.get(style, [])
        platform_fonts = platform_recommendations.get(platform, [])
        
        # Получить шрифты по категории
        category_fonts = popular_fonts.get(category, [])
        
        # Создать список рекомендаций
        for font_info in category_fonts:
            family = font_info['family']
            
            # Проверить соответствие критериям
            score = 0
            reasons = []
            
            if family in style_fonts:
                score += 2
                reasons.append(f"Perfect for {style} style")
            
            if family in platform_fonts:
                score += 2
                reasons.append(f"Optimized for {platform}")
            
            if score > 0:
                recommendations.append({
                    'family': family,
                    'score': score,
                    'reason': '; '.join(reasons),
                    'weights': font_info.get('weights', ['400']),
                    'description': font_info.get('description', ''),
                    'use_cases': self._get_use_cases(family, platform),
                    'category': category
                })
        
        # Сортировать по релевантности
        recommendations.sort(key=lambda x: x['score'], reverse=True)
        
        return recommendations[:10]  # Вернуть топ-10
    
    def _get_use_cases(self, font_family: str, platform: str) -> list:
        """Get use cases for a font family"""
        
        use_cases_map = {
            'Inter': ['titles', 'body_text', 'captions'],
            'Roboto': ['body_text', 'headings', 'buttons'],
            'Open Sans': ['body_text', 'paragraphs', 'descriptions'],
            'Montserrat': ['titles', 'headings', 'logos'],
            'Poppins': ['headings', 'titles', 'call_to_action'],
            'Oswald': ['titles', 'headings', 'emphasis'],
            'Playfair Display': ['titles', 'headings', 'luxury_brands'],
            'Merriweather': ['body_text', 'articles', 'long_form'],
            'Lora': ['body_text', 'quotes', 'articles'],
            'Bebas Neue': ['titles', 'logos', 'impact_text']
        }
        
        return use_cases_map.get(font_family, ['general_use'])

class FontCacheResource(Resource):
    """
    Resource for managing font cache
    """
    
    def delete(self):
        """
        Clear font cache
        
        Returns:
        {
            "success": true,
            "message": "Font cache cleared successfully"
        }
        """
        
        try:
            import os
            import shutil
            
            cache_dir = current_app.config.get('FONTS_CACHE_DIR', 'fonts/cache/')
            
            if os.path.exists(cache_dir):
                # Очистить кэш-директорию
                for filename in os.listdir(cache_dir):
                    file_path = os.path.join(cache_dir, filename)
                    try:
                        if os.path.isfile(file_path):
                            os.unlink(file_path)
                        elif os.path.isdir(file_path):
                            shutil.rmtree(file_path)
                    except Exception as e:
                        logger.warning(f"Failed to delete {file_path}: {e}")
                
                logger.info("Font cache cleared successfully")
                
                return success_response(
                    'Font cache cleared successfully',
                    {'cache_dir': cache_dir}
                )
            else:
                return success_response(
                    'Cache directory does not exist',
                    {'cache_dir': cache_dir}
                )
                
        except Exception as e:
            logger.error(f"Error clearing font cache: {str(e)}")
            return error_response(
                'Failed to clear font cache',
                str(e),
                500
            )
    
    def get(self):
        """
        Get font cache information
        
        Returns:
        {
            "success": true,
            "data": {
                "cache_size": "15.2 MB",
                "cached_fonts": 12,
                "cache_dir": "/app/fonts/cache/"
            }
        }
        """
        
        try:
            import os
            
            cache_dir = current_app.config.get('FONTS_CACHE_DIR', 'fonts/cache/')
            
            if not os.path.exists(cache_dir):
                return success_response(
                    'Cache directory does not exist',
                    {
                        'cache_size': '0 B',
                        'cached_fonts': 0,
                        'cache_dir': cache_dir
                    }
                )
            
            # Подсчитать размер кэша
            total_size = 0
            font_count = 0
            
            for filename in os.listdir(cache_dir):
                file_path = os.path.join(cache_dir, filename)
                if os.path.isfile(file_path) and filename.endswith('.ttf'):
                    total_size += os.path.getsize(file_path)
                    font_count += 1
            
            # Форматировать размер
            def format_size(size_bytes):
                if size_bytes < 1024:
                    return f"{size_bytes} B"
                elif size_bytes < 1024 * 1024:
                    return f"{size_bytes / 1024:.1f} KB"
                else:
                    return f"{size_bytes / (1024 * 1024):.1f} MB"
            
            response_data = {
                'cache_size': format_size(total_size),
                'cached_fonts': font_count,
                'cache_dir': cache_dir,
                'total_size_bytes': total_size
            }
            
            return success_response(
                'Font cache information retrieved successfully',
                response_data
            )
            
        except Exception as e:
            logger.error(f"Error getting font cache info: {str(e)}")
            return error_response(
                'Failed to get font cache information',
                str(e),
                500
            )
