"""
Validation Utilities
Common validation functions and decorators for API endpoints
"""

import functools
import logging
from typing import Any, Dict, Optional
from flask import request, current_app
from marshmallow import ValidationError

logger = logging.getLogger(__name__)

def validate_request_data(schema, location='json'):
    """
    Validate request data using Marshmallow schema
    
    Args:
        schema: Marshmallow schema instance
        location: Where to get data from ('json', 'form', 'args')
        
    Returns:
        Validated data dictionary
        
    Raises:
        ValidationError: If validation fails
    """
    
    # Get request data based on location
    if location == 'json':
        raw_data = request.get_json()
        if raw_data is None:
            raise ValidationError('Request must contain valid JSON')
    elif location == 'form':
        raw_data = request.form.to_dict()
    elif location == 'args':
        raw_data = request.args.to_dict()
    else:
        raise ValueError(f"Unsupported data location: {location}")
    
    # Validate using schema
    try:
        validated_data = schema.load(raw_data)
        logger.debug(f"Request data validated successfully")
        return validated_data
    except ValidationError as e:
        logger.warning(f"Validation failed: {e.messages}")
        raise

def validate_content_length(max_length: Optional[int] = None):
    """
    Decorator to validate request content length
    
    Args:
        max_length: Maximum allowed content length in bytes
    """
    
    if max_length is None:
        max_length = current_app.config.get('MAX_CONTENT_LENGTH', 16 * 1024 * 1024)
    
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            content_length = request.content_length
            if content_length and content_length > max_length:
                raise ValidationError(f'Request too large. Maximum size: {max_length} bytes')
            return func(*args, **kwargs)
        return wrapper
    return decorator

def validate_rate_limit(requests_per_minute: int = 60):
    """
    Basic rate limiting decorator
    Note: In production, use Redis or similar for distributed rate limiting
    
    Args:
        requests_per_minute: Maximum requests per minute per IP
    """
    
    # Simple in-memory rate limiting (not suitable for production)
    request_counts = {}
    
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            client_ip = request.remote_addr
            current_time = int(time.time() / 60)  # Current minute
            
            # Clean old entries
            request_counts[client_ip] = {
                k: v for k, v in request_counts.get(client_ip, {}).items()
                if k >= current_time - 1
            }
            
            # Count requests in current minute
            current_requests = request_counts.get(client_ip, {}).get(current_time, 0)
            
            if current_requests >= requests_per_minute:
                raise ValidationError('Rate limit exceeded')
            
            # Increment counter
            if client_ip not in request_counts:
                request_counts[client_ip] = {}
            request_counts[client_ip][current_time] = current_requests + 1
            
            return func(*args, **kwargs)
        return wrapper
    return decorator

def validate_api_key(required: bool = False):
    """
    Decorator to validate API key from headers
    
    Args:
        required: Whether API key is required
    """
    
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            api_key = request.headers.get('X-API-Key') or request.headers.get('Authorization')
            
            if required and not api_key:
                raise ValidationError('API key required')
            
            if api_key:
                # Remove "Bearer " prefix if present
                if api_key.startswith('Bearer '):
                    api_key = api_key[7:]
                
                # Validate API key (implement your validation logic)
                if not _is_valid_api_key(api_key):
                    raise ValidationError('Invalid API key')
            
            # Add API key to request context for logging
            request.api_key = api_key
            
            return func(*args, **kwargs)
        return wrapper
    return decorator

def validate_text_content(text: str, max_length: int = 10000) -> Dict[str, Any]:
    """
    Validate and analyze text content
    
    Args:
        text: Text content to validate
        max_length: Maximum allowed text length
        
    Returns:
        Dictionary with validation results and statistics
    """
    
    if not isinstance(text, str):
        raise ValidationError('Text must be a string')
    
    if len(text) == 0:
        raise ValidationError('Text cannot be empty')
    
    if len(text) > max_length:
        raise ValidationError(f'Text too long. Maximum length: {max_length} characters')
    
    # Analyze text content
    analysis = {
        'length': len(text),
        'word_count': len(text.split()),
        'line_count': len(text.splitlines()),
        'has_separators': '========' in text,
        'estimated_slides': text.count('========') + 1 if '========' in text else 1,
        'warnings': []
    }
    
    # Check for potential issues
    if analysis['estimated_slides'] > current_app.config.get('MAX_SLIDES', 20):
        analysis['warnings'].append(f"Too many slides ({analysis['estimated_slides']}). Maximum: {current_app.config.get('MAX_SLIDES', 20)}")
    
    if analysis['length'] > 5000 and not analysis['has_separators']:
        analysis['warnings'].append('Long text without slide separators may result in poor formatting')
    
    if analysis['word_count'] < 5:
        analysis['warnings'].append('Very short text may not fill slides effectively')
    
    return analysis

def validate_color_scheme(config: Dict[str, Any]) -> Dict[str, Any]:
    """
    Validate color scheme for accessibility and design quality
    
    Args:
        config: Configuration dictionary with colors
        
    Returns:
        Dictionary with validation results and suggestions
    """
    
    results = {
        'valid': True,
        'warnings': [],
        'suggestions': []
    }
    
    bg_color = config.get('background_color', '#ffffff')
    text_color = config.get('text_color', '#000000')
    
    # Check contrast ratio
    contrast_ratio = _calculate_contrast_ratio(bg_color, text_color)
    
    if contrast_ratio < 4.5:
        results['valid'] = False
        results['warnings'].append(f'Poor contrast ratio: {contrast_ratio:.2f}. Minimum: 4.5')
        
        # Suggest better colors
        if _is_light_color(bg_color):
            results['suggestions'].append('Consider using darker text color for better readability')
        else:
            results['suggestions'].append('Consider using lighter text color for better readability')
    
    # Check for common color issues
    if bg_color.lower() == text_color.lower():
        results['valid'] = False
        results['warnings'].append('Background and text colors are identical')
    
    # Check for accessibility-friendly colors
    if bg_color.lower() in ['#ff0000', '#00ff00']:  # Pure red or green
        results['warnings'].append('Avoid pure red or green backgrounds for colorblind accessibility')
    
    return results

def validate_platform_compatibility(config: Dict[str, Any], platform: str) -> Dict[str, Any]:
    """
    Validate configuration compatibility with target platform
    
    Args:
        config: Configuration dictionary
        platform: Target platform name
        
    Returns:
        Dictionary with compatibility results
    """
    
    results = {
        'compatible': True,
        'warnings': [],
        'optimizations': []
    }
    
    platform_specs = current_app.config.get('PLATFORM_SPECS', {}).get(platform, {})
    
    if not platform_specs:
        results['warnings'].append(f'Unknown platform: {platform}')
        return results
    
    # Check font sizes for platform
    font_size = config.get('font_size', 44)
    
    if platform == 'instagram_story':
        if font_size < 40:
            results['optimizations'].append('Consider larger font size for Instagram Stories (40+ recommended)')
    elif platform == 'linkedin':
        if font_size > 50:
            results['optimizations'].append('Consider smaller font size for LinkedIn (50 or less recommended)')
    
    # Check aspect ratio considerations
    aspect_ratio = platform_specs.get('aspect_ratio', '1:1')
    
    if aspect_ratio == '9:16' and config.get('text_align') == 'center':
        results['optimizations'].append('Center alignment works well for vertical formats')
    elif aspect_ratio == '1:1' and config.get('padding', 80) > 100:
        results['optimizations'].append('Consider reducing padding for square format to maximize content space')
    
    return results

def _is_valid_api_key(api_key: str) -> bool:
    """
    Validate API key format and authenticity
    
    Args:
        api_key: API key to validate
        
    Returns:
        True if valid, False otherwise
    """
    
    # Implement your API key validation logic here
    # This is a placeholder implementation
    
    if not api_key or len(api_key) < 10:
        return False
    
    # Check against configured valid keys
    valid_keys = current_app.config.get('VALID_API_KEYS', [])
    if valid_keys and api_key not in valid_keys:
        return False
    
    return True

def _calculate_contrast_ratio(color1: str, color2: str) -> float:
    """
    Calculate WCAG contrast ratio between two colors
    
    Args:
        color1: First color (hex)
        color2: Second color (hex)
        
    Returns:
        Contrast ratio as float
    """
    
    try:
        # Convert hex to RGB
        rgb1 = tuple(int(color1[i:i+2], 16) for i in (1, 3, 5))
        rgb2 = tuple(int(color2[i:i+2], 16) for i in (1, 3, 5))
        
        # Calculate relative luminance
        def luminance(rgb):
            r, g, b = [x/255.0 for x in rgb]
            r = r/12.92 if r <= 0.03928 else ((r+0.055)/1.055)**2.4
            g = g/12.92 if g <= 0.03928 else ((g+0.055)/1.055)**2.4
            b = b/12.92 if b <= 0.03928 else ((b+0.055)/1.055)**2.4
            return 0.2126*r + 0.7152*g + 0.0722*b
        
        l1 = luminance(rgb1)
        l2 = luminance(rgb2)
        
        # Calculate contrast ratio
        contrast = (max(l1, l2) + 0.05) / (min(l1, l2) + 0.05)
        return contrast
        
    except Exception:
        return 1.0  # Return minimal contrast if calculation fails

def _is_light_color(color: str) -> bool:
    """
    Determine if a color is light or dark
    
    Args:
        color: Hex color string
        
    Returns:
        True if light color, False if dark
    """
    
    try:
        # Convert hex to RGB
        rgb = tuple(int(color[i:i+2], 16) for i in (1, 3, 5))
        
        # Calculate perceived brightness
        brightness = (rgb[0] * 0.299 + rgb[1] * 0.587 + rgb[2] * 0.114)
        
        return brightness > 127
        
    except Exception:
        return True  # Default to light if calculation fails
