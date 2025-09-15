"""
Health Check and Status API Endpoints
Monitoring and system status endpoints
"""

import logging
import os
import sys
import psutil
from datetime import datetime
from flask import current_app
from flask_restful import Resource

from ..utils.responses import success_response, error_response

logger = logging.getLogger(__name__)

class HealthResource(Resource):
    """
    Basic health check endpoint
    """
    
    def get(self):
        """
        Simple health check
        
        Returns:
        {
            "success": true,
            "data": {
                "status": "healthy",
                "timestamp": "2025-01-15T10:30:00Z",
                "version": "1.0.0"
            }
        }
        """
        
        try:
            response_data = {
                'status': 'healthy',
                'timestamp': datetime.utcnow().isoformat() + 'Z',
                'version': '1.0.0',
                'service': 'carousel-api'
            }
            
            return success_response('Service is healthy', response_data)
            
        except Exception as e:
            logger.error(f"Health check failed: {str(e)}")
            return error_response(
                'Health check failed',
                str(e),
                500
            )

class StatusResource(Resource):
    """
    Detailed system status endpoint
    """
    
    def get(self):
        """
        Detailed system status and metrics
        
        Returns comprehensive system information including:
        - System resources (CPU, memory, disk)
        - Service configuration
        - Dependencies status
        - Performance metrics
        """
        
        try:
            # Basic service info
            status_data = {
                'service': {
                    'name': 'API Threads Carousel Generator',
                    'version': '1.0.0',
                    'status': 'healthy',
                    'timestamp': datetime.utcnow().isoformat() + 'Z',
                    'uptime': self._get_uptime()
                },
                'system': self._get_system_info(),
                'configuration': self._get_config_status(),
                'dependencies': self._check_dependencies(),
                'metrics': self._get_metrics()
            }
            
            # Determine overall health
            overall_status = 'healthy'
            if not status_data['dependencies']['all_available']:
                overall_status = 'degraded'
            
            status_data['service']['status'] = overall_status
            
            return success_response(
                f'System status: {overall_status}',
                status_data
            )
            
        except Exception as e:
            logger.error(f"Status check failed: {str(e)}")
            return error_response(
                'Status check failed',
                str(e),
                500
            )
    
    def _get_uptime(self):
        """Get system uptime information"""
        try:
            boot_time = psutil.boot_time()
            uptime_seconds = datetime.now().timestamp() - boot_time
            
            return {
                'seconds': int(uptime_seconds),
                'human_readable': self._seconds_to_human_readable(uptime_seconds)
            }
        except Exception:
            return {'error': 'Unable to determine uptime'}
    
    def _get_system_info(self):
        """Get system resource information"""
        try:
            # CPU information
            cpu_percent = psutil.cpu_percent(interval=1)
            cpu_count = psutil.cpu_count()
            
            # Memory information
            memory = psutil.virtual_memory()
            
            # Disk information
            disk = psutil.disk_usage('/')
            
            return {
                'cpu': {
                    'usage_percent': cpu_percent,
                    'core_count': cpu_count,
                    'load_average': list(os.getloadavg()) if hasattr(os, 'getloadavg') else None
                },
                'memory': {
                    'total_gb': round(memory.total / (1024**3), 2),
                    'available_gb': round(memory.available / (1024**3), 2),
                    'used_gb': round(memory.used / (1024**3), 2),
                    'usage_percent': memory.percent
                },
                'disk': {
                    'total_gb': round(disk.total / (1024**3), 2),
                    'free_gb': round(disk.free / (1024**3), 2),
                    'used_gb': round(disk.used / (1024**3), 2),
                    'usage_percent': round((disk.used / disk.total) * 100, 2)
                },
                'python_version': sys.version
            }
        except Exception as e:
            return {'error': f'Unable to get system info: {str(e)}'}
    
    def _get_config_status(self):
        """Get configuration status"""
        try:
            config_status = {
                'debug_mode': current_app.debug,
                'environment': os.getenv('FLASK_ENV', 'development'),
                'api_version': current_app.config.get('API_VERSION', '1.0'),
                'max_slides': current_app.config.get('MAX_SLIDES', 20),
                'default_image_size': {
                    'width': current_app.config.get('DEFAULT_IMAGE_WIDTH', 1080),
                    'height': current_app.config.get('DEFAULT_IMAGE_HEIGHT', 1080)
                },
                'supported_platforms': list(current_app.config.get('PLATFORM_SPECS', {}).keys()),
                'features': {
                    'ai_config_generation': bool(current_app.config.get('OPENAI_API_KEY')),
                    'caching': current_app.config.get('CACHE_TYPE', 'simple') != 'null',
                    'rate_limiting': bool(current_app.config.get('RATE_LIMIT_PER_MINUTE'))
                }
            }
            
            return config_status
            
        except Exception as e:
            return {'error': f'Unable to get config status: {str(e)}'}
    
    def _check_dependencies(self):
        """Check status of external dependencies"""
        dependencies = {
            'pillow': self._check_pillow(),
            'openai': self._check_openai(),
            'numpy': self._check_numpy()
        }
        
        # Check if all dependencies are available
        all_available = all(dep.get('available', False) for dep in dependencies.values())
        
        return {
            'all_available': all_available,
            'details': dependencies
        }
    
    def _check_pillow(self):
        """Check Pillow (PIL) availability and version"""
        try:
            from PIL import Image, ImageDraw, ImageFont
            import PIL
            
            return {
                'available': True,
                'version': PIL.__version__,
                'features': {
                    'image_creation': True,
                    'text_rendering': True,
                    'font_support': True
                }
            }
        except ImportError as e:
            return {
                'available': False,
                'error': str(e)
            }
    
    def _check_openai(self):
        """Check OpenAI client availability"""
        try:
            import openai
            api_key_configured = bool(current_app.config.get('OPENAI_API_KEY'))
            
            return {
                'available': True,
                'version': openai.__version__,
                'api_key_configured': api_key_configured,
                'model': current_app.config.get('OPENAI_MODEL', 'gpt-3.5-turbo')
            }
        except ImportError as e:
            return {
                'available': False,
                'error': str(e)
            }
    
    def _check_numpy(self):
        """Check NumPy availability"""
        try:
            import numpy as np
            
            return {
                'available': True,
                'version': np.__version__
            }
        except ImportError as e:
            return {
                'available': False,
                'error': str(e)
            }
    
    def _get_metrics(self):
        """Get basic performance metrics"""
        try:
            # This is a placeholder for actual metrics
            # In production, you might integrate with Prometheus or similar
            
            return {
                'requests_total': 0,  # Placeholder
                'requests_per_minute': 0,  # Placeholder
                'average_response_time_ms': 0,  # Placeholder
                'error_rate_percent': 0,  # Placeholder
                'active_connections': 0  # Placeholder
            }
        except Exception:
            return {'error': 'Metrics not available'}
    
    def _seconds_to_human_readable(self, seconds):
        """Convert seconds to human readable format"""
        intervals = [
            ('days', 86400),
            ('hours', 3600),
            ('minutes', 60),
            ('seconds', 1)
        ]
        
        result = []
        for name, count in intervals:
            value = int(seconds // count)
            if value:
                result.append(f"{value} {name}")
                seconds -= value * count
        
        return ', '.join(result) if result else '0 seconds'
