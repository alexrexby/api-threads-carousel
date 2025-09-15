"""
AI Configuration Generator Service
Service for generating carousel configurations using OpenAI
"""

import logging
import json
import re
from typing import Dict, Any, Optional
from flask import current_app
import openai

logger = logging.getLogger(__name__)

class AIConfigGeneratorService:
    """
    Service for generating carousel design configurations using AI
    """
    
    def __init__(self):
        self.client = None
        self._initialize_openai()
    
    def _initialize_openai(self):
        """Initialize OpenAI client with API key"""
        
        api_key = current_app.config.get('OPENAI_API_KEY')
        if api_key:
            try:
                self.client = openai.OpenAI(api_key=api_key)
                logger.info("OpenAI client initialized successfully")
            except Exception as e:
                logger.error(f"Failed to initialize OpenAI client: {e}")
                self.client = None
        else:
            logger.warning("OpenAI API key not configured")
    
    def generate_config(
        self,
        description: str,
        platform: str = 'instagram_post',
        additional_requirements: str = '',
        brand_colors: Optional[list] = None
    ) -> Dict[str, Any]:
        """
        Generate carousel configuration based on description
        
        Args:
            description: Style description from user
            platform: Target social media platform
            additional_requirements: Additional styling requirements
            brand_colors: Optional list of brand colors
            
        Returns:
            Dictionary with generated config and explanation
        """
        
        if not self.client:
            raise Exception("OpenAI client not available")
        
        try:
            # Get platform specifications
            platform_specs = current_app.config.get('PLATFORM_SPECS', {}).get(platform, {})
            
            # Prepare the prompt
            prompt = self._build_prompt(
                description=description,
                platform=platform,
                platform_specs=platform_specs,
                additional_requirements=additional_requirements,
                brand_colors=brand_colors
            )
            
            # Call OpenAI API
            response = self.client.chat.completions.create(
                model=current_app.config.get('OPENAI_MODEL', 'gpt-3.5-turbo'),
                messages=[
                    {
                        "role": "system",
                        "content": self._get_system_prompt()
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                max_tokens=current_app.config.get('OPENAI_MAX_TOKENS', 1000),
                temperature=0.7,
                response_format={"type": "json_object"}
            )
            
            # Parse response
            response_content = response.choices[0].message.content
            result = json.loads(response_content)
            
            # Validate and sanitize the generated config
            config = self._validate_and_sanitize_config(result.get('config', {}), platform_specs)
            
            return {
                'config': config,
                'explanation': result.get('explanation', 'AI-generated configuration'),
                'platform': platform,
                'prompt_used': description
            }
            
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse AI response as JSON: {e}")
            return self._get_fallback_config(description, platform)
            
        except Exception as e:
            logger.error(f"Error generating AI config: {e}")
            return self._get_fallback_config(description, platform)
    
    def _get_system_prompt(self) -> str:
        """Get the system prompt for AI configuration generation"""
        
        return """You are an expert graphic designer specializing in social media carousel design. 
        Your task is to generate optimal design configurations based on user descriptions.
        
        You must respond with valid JSON containing:
        1. "config" - the design configuration object
        2. "explanation" - brief explanation of design choices
        
        Design principles to follow:
        - Ensure good contrast between text and background colors
        - Choose font sizes appropriate for the platform and readability
        - Consider modern design trends and user preferences
        - Ensure accessibility with sufficient color contrast
        - Adapt to platform-specific requirements
        
        Available configuration options:
        - background_color: hex color (e.g., "#ffffff")
        - text_color: hex color (e.g., "#000000") 
        - font_size: integer 8-200
        - title_font_size: integer 8-300
        - padding: integer 0-500 (pixels)
        - corner_radius: integer 0-100 (pixels)
        - line_spacing: float 0.5-3.0
        - text_align: "left", "center", or "right"
        - add_page_numbers: boolean
        - add_logo_text: boolean
        - logo_text: string (if add_logo_text is true)
        
        Respond only with valid JSON."""
    
    def _build_prompt(
        self,
        description: str,
        platform: str,
        platform_specs: Dict[str, Any],
        additional_requirements: str,
        brand_colors: Optional[list]
    ) -> str:
        """Build the user prompt for AI generation"""
        
        prompt_parts = [
            f"Generate a carousel design configuration for {platform}.",
            f"Platform dimensions: {platform_specs.get('width', 1080)}x{platform_specs.get('height', 1080)} pixels.",
            f"Style description: {description}",
        ]
        
        if additional_requirements:
            prompt_parts.append(f"Additional requirements: {additional_requirements}")
        
        if brand_colors:
            colors_str = ", ".join(brand_colors)
            prompt_parts.append(f"Consider these brand colors: {colors_str}")
        
        # Add platform-specific guidance
        platform_guidance = {
            'instagram_post': 'Design for Instagram feed posts - clean, modern, eye-catching',
            'instagram_story': 'Design for Instagram stories - vertical format, bold and engaging',
            'linkedin': 'Design for LinkedIn - professional, business-oriented, readable',
            'tiktok': 'Design for TikTok - vibrant, youthful, attention-grabbing',
            'twitter': 'Design for Twitter - concise, clear, informative',
            'facebook': 'Design for Facebook - engaging, social, accessible'
        }
        
        if platform in platform_guidance:
            prompt_parts.append(platform_guidance[platform])
        
        prompt_parts.append("Generate the configuration as JSON with 'config' and 'explanation' fields.")
        
        return " ".join(prompt_parts)
    
    def _validate_and_sanitize_config(self, config: Dict[str, Any], platform_specs: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate and sanitize the AI-generated configuration
        
        Args:
            config: Raw configuration from AI
            platform_specs: Platform specifications
            
        Returns:
            Validated and sanitized configuration
        """
        
        # Start with default config
        base_config = current_app.config['DEFAULT_CONFIG'].copy()
        
        # Validate and apply each setting
        validated_config = {}
        
        # Color validation
        if 'background_color' in config:
            bg_color = self._validate_hex_color(config['background_color'])
            if bg_color:
                validated_config['background_color'] = bg_color
        
        if 'text_color' in config:
            text_color = self._validate_hex_color(config['text_color'])
            if text_color:
                validated_config['text_color'] = text_color
        
        # Font size validation
        if 'font_size' in config:
            font_size = self._validate_integer(config['font_size'], 8, 200)
            if font_size:
                validated_config['font_size'] = font_size
        
        if 'title_font_size' in config:
            title_size = self._validate_integer(config['title_font_size'], 8, 300)
            if title_size:
                validated_config['title_font_size'] = title_size
        
        # Layout validation
        if 'padding' in config:
            padding = self._validate_integer(config['padding'], 0, 500)
            if padding is not None:
                validated_config['padding'] = padding
        
        if 'corner_radius' in config:
            radius = self._validate_integer(config['corner_radius'], 0, 100)
            if radius is not None:
                validated_config['corner_radius'] = radius
        
        if 'line_spacing' in config:
            spacing = self._validate_float(config['line_spacing'], 0.5, 3.0)
            if spacing:
                validated_config['line_spacing'] = spacing
        
        # Text alignment validation
        if 'text_align' in config:
            align = config['text_align']
            if align in ['left', 'center', 'right']:
                validated_config['text_align'] = align
        
        # Boolean settings
        for bool_setting in ['add_page_numbers', 'add_logo_text']:
            if bool_setting in config:
                if isinstance(config[bool_setting], bool):
                    validated_config[bool_setting] = config[bool_setting]
        
        # Logo text
        if 'logo_text' in config and isinstance(config['logo_text'], str):
            validated_config['logo_text'] = config['logo_text'][:50]  # Limit length
        
        # Ensure contrast between text and background
        if 'background_color' in validated_config and 'text_color' in validated_config:
            if not self._has_sufficient_contrast(
                validated_config['background_color'], 
                validated_config['text_color']
            ):
                # Adjust text color for better contrast
                if validated_config['background_color'].lower() in ['#ffffff', '#fff']:
                    validated_config['text_color'] = '#000000'
                else:
                    validated_config['text_color'] = '#ffffff'
        
        # Merge with base config
        final_config = {**base_config, **validated_config}
        
        return final_config
    
    def _validate_hex_color(self, color: str) -> Optional[str]:
        """
        Validate hex color format
        
        Args:
            color: Color string to validate
            
        Returns:
            Valid hex color or None
        """
        
        if not isinstance(color, str):
            return None
        
        # Remove whitespace and ensure # prefix
        color = color.strip()
        if not color.startswith('#'):
            color = '#' + color
        
        # Validate hex format
        if re.match(r'^#[0-9A-Fa-f]{6}, color):
            return color.upper()
        
        return None
    
    def _validate_integer(self, value: Any, min_val: int, max_val: int) -> Optional[int]:
        """
        Validate integer within range
        
        Args:
            value: Value to validate
            min_val: Minimum allowed value
            max_val: Maximum allowed value
            
        Returns:
            Valid integer or None
        """
        
        try:
            int_val = int(value)
            if min_val <= int_val <= max_val:
                return int_val
        except (ValueError, TypeError):
            pass
        
        return None
    
    def _validate_float(self, value: Any, min_val: float, max_val: float) -> Optional[float]:
        """
        Validate float within range
        
        Args:
            value: Value to validate
            min_val: Minimum allowed value
            max_val: Maximum allowed value
            
        Returns:
            Valid float or None
        """
        
        try:
            float_val = float(value)
            if min_val <= float_val <= max_val:
                return float_val
        except (ValueError, TypeError):
            pass
        
        return None
    
    def _has_sufficient_contrast(self, bg_color: str, text_color: str) -> bool:
        """
        Check if colors have sufficient contrast for accessibility
        
        Args:
            bg_color: Background color hex
            text_color: Text color hex
            
        Returns:
            True if contrast is sufficient
        """
        
        try:
            # Convert hex to RGB
            bg_rgb = tuple(int(bg_color[i:i+2], 16) for i in (1, 3, 5))
            text_rgb = tuple(int(text_color[i:i+2], 16) for i in (1, 3, 5))
            
            # Calculate relative luminance
            def luminance(rgb):
                r, g, b = [x/255.0 for x in rgb]
                r = r/12.92 if r <= 0.03928 else ((r+0.055)/1.055)**2.4
                g = g/12.92 if g <= 0.03928 else ((g+0.055)/1.055)**2.4
                b = b/12.92 if b <= 0.03928 else ((b+0.055)/1.055)**2.4
                return 0.2126*r + 0.7152*g + 0.0722*b
            
            l1 = luminance(bg_rgb)
            l2 = luminance(text_rgb)
            
            # Calculate contrast ratio
            contrast = (max(l1, l2) + 0.05) / (min(l1, l2) + 0.05)
            
            # WCAG AA standard requires 4.5:1 for normal text
            return contrast >= 4.5
            
        except Exception:
            # If calculation fails, assume insufficient contrast
            return False
    
    def _get_fallback_config(self, description: str, platform: str) -> Dict[str, Any]:
        """
        Generate fallback configuration when AI fails
        
        Args:
            description: Original description
            platform: Target platform
            
        Returns:
            Fallback configuration
        """
        
        logger.info("Generating fallback configuration")
        
        # Analyze description for keywords and generate simple config
        description_lower = description.lower()
        
        # Start with default config
        config = current_app.config['DEFAULT_CONFIG'].copy()
        
        # Apply platform specs
        platform_specs = current_app.config.get('PLATFORM_SPECS', {}).get(platform, {})
        if platform_specs:
            config['platform'] = platform
        
        # Simple keyword-based styling
        if any(word in description_lower for word in ['dark', 'black', 'night']):
            config['background_color'] = '#1a1a1a'
            config['text_color'] = '#ffffff'
        elif any(word in description_lower for word in ['light', 'white', 'clean']):
            config['background_color'] = '#ffffff'
            config['text_color'] = '#333333'
        elif any(word in description_lower for word in ['blue', 'corporate', 'business']):
            config['background_color'] = '#1e3d59'
            config['text_color'] = '#ffffff'
        elif any(word in description_lower for word in ['red', 'urgent', 'important']):
            config['background_color'] = '#dc3545'
            config['text_color'] = '#ffffff'
        elif any(word in description_lower for word in ['green', 'nature', 'eco']):
            config['background_color'] = '#28a745'
            config['text_color'] = '#ffffff'
        
        # Adjust font sizes based on platform
        if platform == 'instagram_story':
            config['font_size'] = 48
            config['title_font_size'] = 64
        elif platform == 'tiktok':
            config['font_size'] = 46
            config['title_font_size'] = 60
        
        # Add some style based on description
        if any(word in description_lower for word in ['modern', 'minimal']):
            config['corner_radius'] = 20
            config['padding'] = 100
        elif any(word in description_lower for word in ['classic', 'traditional']):
            config['corner_radius'] = 0
            config['padding'] = 80
        
        return {
            'config': config,
            'explanation': f'Fallback configuration based on keywords from: {description}',
            'platform': platform,
            'note': 'This is a fallback configuration as AI generation was not available'
        }
    
    def generate_style_suggestions(self, industry: str, target_audience: str) -> Dict[str, Any]:
        """
        Generate style suggestions based on industry and target audience
        
        Args:
            industry: Business industry
            target_audience: Target audience description
            
        Returns:
            Style suggestions and configurations
        """
        
        if not self.client:
            return self._get_fallback_suggestions(industry, target_audience)
        
        try:
            prompt = f"""
            Generate 3 different carousel design style suggestions for:
            Industry: {industry}
            Target Audience: {target_audience}
            
            For each style, provide:
            1. Style name
            2. Description
            3. Configuration object
            4. Use case recommendations
            
            Consider industry best practices and audience preferences.
            """
            
            response = self.client.chat.completions.create(
                model=current_app.config.get('OPENAI_MODEL', 'gpt-3.5-turbo'),
                messages=[
                    {
                        "role": "system",
                        "content": "You are a design consultant. Provide 3 design suggestions as JSON with an array of style objects."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                max_tokens=current_app.config.get('OPENAI_MAX_TOKENS', 1500),
                temperature=0.8,
                response_format={"type": "json_object"}
            )
            
            result = json.loads(response.choices[0].message.content)
            
            # Validate each style configuration
            styles = result.get('styles', [])
            validated_styles = []
            
            for style in styles:
                if 'config' in style:
                    validated_config = self._validate_and_sanitize_config(style['config'], {})
                    style['config'] = validated_config
                validated_styles.append(style)
            
            return {
                'success': True,
                'styles': validated_styles,
                'industry': industry,
                'target_audience': target_audience
            }
            
        except Exception as e:
            logger.error(f"Error generating style suggestions: {e}")
            return self._get_fallback_suggestions(industry, target_audience)
    
    def _get_fallback_suggestions(self, industry: str, target_audience: str) -> Dict[str, Any]:
        """Generate fallback style suggestions"""
        
        base_config = current_app.config['DEFAULT_CONFIG'].copy()
        
        styles = [
            {
                'name': 'Professional',
                'description': 'Clean, corporate design suitable for business content',
                'config': {
                    **base_config,
                    'background_color': '#f8f9fa',
                    'text_color': '#343a40',
                    'corner_radius': 15,
                    'padding': 90
                },
                'use_case': 'Business presentations, corporate announcements'
            },
            {
                'name': 'Modern Bold',
                'description': 'Eye-catching design with vibrant colors',
                'config': {
                    **base_config,
                    'background_color': '#6c5ce7',
                    'text_color': '#ffffff',
                    'corner_radius': 25,
                    'padding': 80,
                    'font_size': 46
                },
                'use_case': 'Marketing campaigns, social media engagement'
            },
            {
                'name': 'Minimalist',
                'description': 'Simple, elegant design focusing on content',
                'config': {
                    **base_config,
                    'background_color': '#ffffff',
                    'text_color': '#2d3436',
                    'corner_radius': 0,
                    'padding': 100,
                    'text_align': 'center'
                },
                'use_case': 'Educational content, thought leadership'
            }
        ]
        
        return {
            'success': True,
            'styles': styles,
            'industry': industry,
            'target_audience': target_audience,
            'note': 'Fallback suggestions as AI generation was not available'
        }
