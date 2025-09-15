"""
Tests for Carousel Generator Service
Unit tests for carousel generation functionality
"""

import pytest
import json
from unittest.mock import patch, MagicMock
from api.services.carousel_generator import CarouselGeneratorService
from api import create_app

class TestCarouselGeneratorService:
    """Test cases for CarouselGeneratorService"""
    
    @pytest.fixture
    def app(self):
        """Create test Flask application"""
        app = create_app()
        app.config['TESTING'] = True
        app.config['MAX_SLIDES'] = 10
        app.config['SLIDE_SEPARATOR'] = '========'
        return app
    
    @pytest.fixture
    def service(self, app):
        """Create service instance"""
        with app.app_context():
            return CarouselGeneratorService()
    
    @pytest.fixture
    def sample_text(self):
        """Sample text for testing"""
        return """**Welcome to Our API**
This is the first slide content with some details.

========

**Features List**
- Easy to use
- Highly customizable  
- AI-powered design
- Multiple platforms

========

**Get Started**
Visit our documentation to begin using the API today!"""
    
    @pytest.fixture
    def sample_config(self):
        """Sample configuration for testing"""
        return {
            'background_color': '#ffffff',
            'text_color': '#000000',
            'font_size': 44,
            'title_font_size': 56,
            'padding': 80,
            'corner_radius': 0,
            'platform': 'instagram_post'
        }
    
    def test_parse_slides_basic(self, service, sample_text):
        """Test basic slide parsing"""
        config = {'slide_separator': '========'}
        slides = service._parse_slides(sample_text, config)
        
        assert len(slides) == 3
        assert "Welcome to Our API" in slides[0]
        assert "Features List" in slides[1]
        assert "Get Started" in slides[2]
    
    def test_parse_slides_no_separator(self, service):
        """Test parsing text without separators"""
        text = "This is a single slide without any separators."
        config = {'slide_separator': '========'}
        slides = service._parse_slides(text, config)
        
        assert len(slides) == 1
        assert slides[0] == text
    
    def test_parse_slides_auto_split(self, service):
        """Test automatic splitting of long text"""
        long_text = "This is a very long text. " * 100  # Create long text
        config = {'slide_separator': '========'}
        
        with patch.object(service, '_auto_split_text') as mock_split:
            mock_split.return_value = ['Part 1', 'Part 2']
            slides = service._parse_slides(long_text, config)
            mock_split.assert_called_once()
    
    def test_auto_split_text(self, service):
        """Test automatic text splitting functionality"""
        text = """First paragraph with some content.

Second paragraph with more content and details.

Third paragraph with additional information.

Fourth paragraph to complete the content."""
        
        slides = service._auto_split_text(text)
        assert len(slides) > 1
        assert all(len(slide) < 800 for slide in slides)
    
    def test_get_image_dimensions_custom(self, service):
        """Test getting custom image dimensions"""
        config = {
            'custom_width': 1200,
            'custom_height': 800
        }
        
        width, height = service._get_image_dimensions(config)
        assert width == 1200
        assert height == 800
    
    def test_get_image_dimensions_platform(self, service, app):
        """Test getting platform-specific dimensions"""
        with app.app_context():
            app.config['PLATFORM_SPECS'] = {
                'instagram_post': {'width': 1080, 'height': 1080},
                'instagram_story': {'width': 1080, 'height': 1920}
            }
            
            config = {'platform': 'instagram_story'}
            width, height = service._get_image_dimensions(config)
            assert width == 1080
            assert height == 1920
    
    def test_parse_slide_content_titles(self, service):
        """Test parsing slide content with titles"""
        text = """**Bold Title**
Regular content here
# Header Title
More content
ALL CAPS TITLE
Final content"""
        
        content = service._parse_slide_content(text)
        
        title_items = [item for item in content if item['type'] == 'title']
        text_items = [item for item in content if item['type'] == 'text']
        
        assert len(title_items) == 3
        assert len(text_items) == 3
        assert 'Bold Title' in [item['text'] for item in title_items]
        assert 'Header Title' in [item['text'] for item in title_items]
        assert 'ALL CAPS TITLE' in [item['text'] for item in title_items]
    
    @patch('api.services.carousel_generator.ImageFont')
    @patch('api.services.carousel_generator.Image')
    def test_create_slide_image(self, mock_image, mock_font, service, app, sample_config):
        """Test slide image creation"""
        with app.app_context():
            # Mock PIL objects
            mock_img = MagicMock()
            mock_draw = MagicMock()
            mock_image.new.return_value = mock_img
            mock_image.ImageDraw.Draw.return_value = mock_draw
            
            # Mock font
            mock_font_obj = MagicMock()
            mock_font.truetype.return_value = mock_font_obj
            mock_font_obj.getbbox.return_value = (0, 0, 100, 30)
            
            # Mock image save
            mock_byte_io = MagicMock()
            mock_byte_io.getvalue.return_value = b'fake_image_data'
            
            with patch('io.BytesIO', return_value=mock_byte_io):
                result = service._create_slide_image(
                    text="**Test Title**\nTest content",
                    config=sample_config,
                    width=1080,
                    height=1080,
                    slide_number=1,
                    total_slides=3
                )
            
            assert result == b'fake_image_data'
            mock_image.new.assert_called_once()
    
    def test_wrap_text(self, service):
        """Test text wrapping functionality"""
        # Mock font object
        mock_font = MagicMock()
        mock_font.getbbox.side_effect = lambda text: (0, 0, len(text) * 10, 20)
        
        text = "This is a long line that should be wrapped"
        max_width = 200  # Allows about 20 characters per line
        
        lines = service._wrap_text(text, mock_font, max_width)
        
        assert len(lines) > 1
        assert all(len(line) <= 20 for line in lines)
    
    def test_break_long_word(self, service):
        """Test breaking long words that don't fit"""
        mock_font = MagicMock()
        mock_font.getbbox.side_effect = lambda text: (0, 0, len(text) * 10, 20)
        
        word = "verylongwordthatdoesnotfit"
        max_width = 100  # Allows about 10 characters
        
        parts = service._break_long_word(word, mock_font, max_width)
        
        assert len(parts) > 1
        assert all(len(part) <= 10 for part in parts)
    
    @patch('api.services.carousel_generator.ImageFont')
    def test_get_font_fallback(self, mock_font, service):
        """Test font loading with fallback"""
        # Mock font loading failure
        mock_font.truetype.side_effect = Exception("Font not found")
        mock_font.load_default.return_value = MagicMock()
        
        font = service._get_font(24)
        
        mock_font.load_default.assert_called_once()
    
    def test_validate_slide_count(self, service, app):
        """Test slide count validation"""
        with app.app_context():
            # Create text with too many slides
            slides = ['Slide {}'.format(i) for i in range(15)]
            text = '\n========\n'.join(slides)
            config = sample_config = {
                'background_color': '#ffffff',
                'text_color': '#000000',
                'font_size': 44,
                'platform': 'instagram_post'
            }
            
            with pytest.raises(ValueError, match="Too many slides"):
                service.generate_carousel(text, config)

class TestCarouselAPI:
    """Test cases for Carousel API endpoints"""
    
    @pytest.fixture
    def app(self):
        """Create test Flask application"""
        app = create_app()
        app.config['TESTING'] = True
        return app
    
    @pytest.fixture
    def client(self, app):
        """Create test client"""
        return app.test_client()
    
    def test_generate_carousel_endpoint(self, client):
        """Test carousel generation endpoint"""
        data = {
            'text': '**Test Title**\nTest content\n\n========\n\n**Second Slide**\nMore content',
            'config': {
                'background_color': '#ffffff',
                'text_color': '#000000',
                'font_size': 44,
                'platform': 'instagram_post'
            }
        }
        
        with patch('api.services.carousel_generator.CarouselGeneratorService.generate_carousel') as mock_generate:
            mock_generate.return_value = {
                'total_slides': 2,
                'slides': [
                    {
                        'text': 'Slide 1',
                        'image_bytes': b'fake_image_1',
                        'width': 1080,
                        'height': 1080,
                        'slide_number': 1
                    },
                    {
                        'text': 'Slide 2',
                        'image_bytes': b'fake_image_2',
                        'width': 1080,
                        'height': 1080,
                        'slide_number': 2
                    }
                ]
            }
            
            response = client.post(
                '/api/v1/generate-carousel',
                data=json.dumps(data),
                content_type='application/json'
            )
            
            assert response.status_code == 200
            result = json.loads(response.data)
            assert result['success'] is True
            assert result['data']['total_slides'] == 2
    
    def test_generate_carousel_validation_error(self, client):
        """Test carousel generation with validation error"""
        data = {
            'text': '',  # Empty text should cause validation error
            'config': {}
        }
        
        response = client.post(
            '/api/v1/generate-carousel',
            data=json.dumps(data),
            content_type='application/json'
        )
        
        assert response.status_code == 400
        result = json.loads(response.data)
        assert result['success'] is False
    
    def test_generate_carousel_no_json(self, client):
        """Test carousel generation without JSON data"""
        response = client.post('/api/v1/generate-carousel')
        
        assert response.status_code == 400
        result = json.loads(response.data)
        assert result['success'] is False
    
    def test_health_endpoint(self, client):
        """Test health check endpoint"""
        response = client.get('/api/v1/health')
        
        assert response.status_code == 200
        result = json.loads(response.data)
        assert result['success'] is True
        assert result['data']['status'] == 'healthy'
    
    def test_status_endpoint(self, client):
        """Test detailed status endpoint"""
        response = client.get('/api/v1/status')
        
        assert response.status_code == 200
        result = json.loads(response.data)
        assert result['success'] is True
        assert 'service' in result['data']
        assert 'system' in result['data']
    
    @patch('api.services.ai_config_generator.openai.OpenAI')
    def test_generate_config_endpoint(self, mock_openai, client, app):
        """Test AI config generation endpoint"""
        with app.app_context():
            app.config['OPENAI_API_KEY'] = 'test_key'
            
            # Mock OpenAI response
            mock_client = MagicMock()
            mock_openai.return_value = mock_client
            mock_response = MagicMock()
            mock_response.choices[0].message.content = json.dumps({
                'config': {
                    'background_color': '#1e3d59',
                    'text_color': '#ffffff',
                    'font_size': 48
                },
                'explanation': 'Corporate style configuration'
            })
            mock_client.chat.completions.create.return_value = mock_response
            
            data = {
                'description': 'Corporate blue style',
                'platform': 'linkedin'
            }
            
            response = client.post(
                '/api/v1/generate-config',
                data=json.dumps(data),
                content_type='application/json'
            )
            
            assert response.status_code == 200
            result = json.loads(response.data)
            assert result['success'] is True
            assert 'config' in result['data']
    
    def test_generate_config_no_openai_key(self, client, app):
        """Test config generation without OpenAI key"""
        with app.app_context():
            app.config['OPENAI_API_KEY'] = None
            
            data = {
                'description': 'Modern style',
                'platform': 'instagram_post'
            }
            
            response = client.post(
                '/api/v1/generate-config',
                data=json.dumps(data),
                content_type='application/json'
            )
            
            assert response.status_code == 503
            result = json.loads(response.data)
            assert result['success'] is False

if __name__ == '__main__':
    pytest.main([__file__])
