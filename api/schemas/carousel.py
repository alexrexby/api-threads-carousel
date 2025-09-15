"""
Carousel API Schemas
Data validation schemas using Marshmallow
"""

from marshmallow import Schema, fields, validate, validates, ValidationError, post_load
import re

class CarouselConfigSchema(Schema):
    """Schema for carousel configuration validation"""
    
    # Colors (hex format)
    background_color = fields.Str(
        validate=validate.Regexp(r'^#[0-9A-Fa-f]{6}$'),
        missing='#ffffff',
        error_messages={'invalid': 'Must be a valid hex color (e.g., #ffffff)'}
    )
    
    text_color = fields.Str(
        validate=validate.Regexp(r'^#[0-9A-Fa-f]{6}$'),
        missing='#000000',
        error_messages={'invalid': 'Must be a valid hex color (e.g., #000000)'}
    )
    
    # Font settings
    font_size = fields.Int(
        validate=validate.Range(min=8, max=200),
        missing=44,
        error_messages={'invalid': 'Font size must be between 8 and 200'}
    )
    
    title_font_size = fields.Int(
        validate=validate.Range(min=8, max=300),
        missing=56,
        error_messages={'invalid': 'Title font size must be between 8 and 300'}
    )
    
    # Layout settings
    padding = fields.Int(
        validate=validate.Range(min=0, max=500),
        missing=80,
        error_messages={'invalid': 'Padding must be between 0 and 500 pixels'}
    )
    
    corner_radius = fields.Int(
        validate=validate.Range(min=0, max=100),
        missing=0,
        error_messages={'invalid': 'Corner radius must be between 0 and 100 pixels'}
    )
    
    # Platform specification
    platform = fields.Str(
        validate=validate.OneOf([
            'instagram_post', 'instagram_story', 'linkedin', 
            'tiktok', 'twitter', 'facebook'
        ]),
        missing='instagram_post',
        error_messages={'invalid': 'Must be a supported platform'}
    )
    
    # UI elements
    add_page_numbers = fields.Bool(missing=False)
    add_logo_text = fields.Bool(missing=False)
    logo_text = fields.Str(
        validate=validate.Length(max=50),
        missing='',
        error_messages={'invalid': 'Logo text must be 50 characters or less'}
    )
    
    # Custom dimensions (optional, overrides platform defaults)
    custom_width = fields.Int(
        validate=validate.Range(min=100, max=4000),
        allow_none=True,
        error_messages={'invalid': 'Width must be between 100 and 4000 pixels'}
    )
    
    custom_height = fields.Int(
        validate=validate.Range(min=100, max=4000),
        allow_none=True,
        error_messages={'invalid': 'Height must be between 100 and 4000 pixels'}
    )
    
    # Advanced settings
    line_spacing = fields.Float(
        validate=validate.Range(min=0.5, max=3.0),
        missing=1.2,
        error_messages={'invalid': 'Line spacing must be between 0.5 and 3.0'}
    )
    
    text_align = fields.Str(
        validate=validate.OneOf(['left', 'center', 'right']),
        missing='left',
        error_messages={'invalid': 'Text alignment must be left, center, or right'}
    )
    
    @validates('logo_text')
    def validate_logo_text(self, value):
        """Validate logo text when add_logo_text is True"""
        if self.context.get('add_logo_text') and not value.strip():
            raise ValidationError('Logo text is required when add_logo_text is True')

class CarouselRequestSchema(Schema):
    """Schema for carousel generation request validation"""
    
    text = fields.Str(
        required=True,
        validate=validate.Length(min=1, max=10000),
        error_messages={
            'required': 'Text content is required',
            'invalid': 'Text must be between 1 and 10,000 characters'
        }
    )
    
    config = fields.Nested(
        CarouselConfigSchema,
        missing=dict,
        error_messages={'invalid': 'Invalid configuration format'}
    )
    
    @validates('text')
    def validate_text_content(self, value):
        """Validate text content structure"""
        if not value.strip():
            raise ValidationError('Text content cannot be empty')
        
        # Check for potential malicious content
        suspicious_patterns = [
            r'<script.*?>.*?</script>',
            r'javascript:',
            r'on\w+\s*=',
        ]
        
        for pattern in suspicious_patterns:
            if re.search(pattern, value, re.IGNORECASE):
                raise ValidationError('Text contains potentially unsafe content')
    
    @post_load
    def process_data(self, data, **kwargs):
        """Post-processing of validated data"""
        
        # Ensure text has proper slide separators
        text = data['text']
        if '========' not in text and len(text) > 500:
            # If text is long but has no separators, suggest adding them
            data['_warnings'] = ['Long text without slide separators detected']
        
        return data

class ConfigRequestSchema(Schema):
    """Schema for AI config generation request validation"""
    
    description = fields.Str(
        required=True,
        validate=validate.Length(min=5, max=500),
        error_messages={
            'required': 'Style description is required',
            'invalid': 'Description must be between 5 and 500 characters'
        }
    )
    
    platform = fields.Str(
        validate=validate.OneOf([
            'instagram_post', 'instagram_story', 'linkedin', 
            'tiktok', 'twitter', 'facebook'
        ]),
        missing='instagram_post',
        error_messages={'invalid': 'Must be a supported platform'}
    )
    
    additional_requirements = fields.Str(
        validate=validate.Length(max=200),
        missing='',
        error_messages={'invalid': 'Additional requirements must be 200 characters or less'}
    )
    
    brand_colors = fields.List(
        fields.Str(validate=validate.Regexp(r'^#[0-9A-Fa-f]{6}$')),
        missing=list,
        error_messages={'invalid': 'Brand colors must be valid hex colors'}
    )
    
    style_preferences = fields.Dict(
        keys=fields.Str(),
        values=fields.Raw(),
        missing=dict,
        error_messages={'invalid': 'Style preferences must be a valid dictionary'}
    )
    
    @validates('description')
    def validate_description(self, value):
        """Validate style description"""
        if not value.strip():
            raise ValidationError('Description cannot be empty')
        
        # Check for inappropriate content
        inappropriate_words = ['hack', 'exploit', 'malicious', 'virus']
        if any(word in value.lower() for word in inappropriate_words):
            raise ValidationError('Description contains inappropriate content')

class BatchCarouselRequestSchema(Schema):
    """Schema for batch carousel generation"""
    
    carousels = fields.List(
        fields.Nested(CarouselRequestSchema),
        required=True,
        validate=validate.Length(min=1, max=10),
        error_messages={
            'required': 'Carousel list is required',
            'invalid': 'Must provide 1-10 carousels for batch processing'
        }
    )
    
    batch_config = fields.Nested(
        CarouselConfigSchema,
        missing=dict,
        error_messages={'invalid': 'Invalid batch configuration'}
    )
    
    async_processing = fields.Bool(
        missing=True,
        error_messages={'invalid': 'Async processing flag must be boolean'}
    )

class CarouselResponseSchema(Schema):
    """Schema for carousel generation response"""
    
    success = fields.Bool(required=True)
    message = fields.Str(required=True)
    
    data = fields.Dict(
        keys=fields.Str(),
        values=fields.Raw()
    )
    
    errors = fields.List(
        fields.Str(),
        missing=list
    )
    
    warnings = fields.List(
        fields.Str(),
        missing=list
    )
    
    metadata = fields.Dict(
        keys=fields.Str(),
        values=fields.Raw(),
        missing=dict
    )
