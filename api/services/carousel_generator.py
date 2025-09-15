"""
Carousel Generator Service
Core service for generating carousel images using Pillow with Google Fonts support
"""

import logging
import io
import re
import textwrap
import os
import requests
from typing import List, Dict, Any, Tuple, Optional
from PIL import Image, ImageDraw, ImageFont, ImageColor
from flask import current_app
import numpy as np

logger = logging.getLogger(__name__)

class CarouselGeneratorService:
    """
    Service class for generating carousel images from text and configuration
    """
    
    def __init__(self):
        self.fonts_cache = {}  # Кэш для загруженных шрифтов
        self.google_fonts_api_key = current_app.config.get('GOOGLE_FONTS_API_KEY')
        self.fonts_dir = os.path.join(os.getcwd(), 'fonts')
        self._ensure_fonts_directory()
        
    def _ensure_fonts_directory(self):
        """Создать директорию для шрифтов если её нет"""
        if not os.path.exists(self.fonts_dir):
            os.makedirs(self.fonts_dir)
            logger.info(f"Created fonts directory: {self.fonts_dir}")
    
    def generate_carousel(self, text: str, config: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate carousel images from text content
        
        Args:
            text: Text content with slide separators
            config: Configuration dictionary for styling
            
        Returns:
            Dictionary containing generated slides and metadata
        """
        
        try:
            # Parse text into slides
            slides_text = self._parse_slides(text, config)
            
            if not slides_text:
                raise ValueError("No valid slides found in text")
            
            # Validate slide count
            if len(slides_text) > current_app.config.get('MAX_SLIDES', 20):
                raise ValueError(f"Too many slides. Maximum is {current_app.config.get('MAX_SLIDES', 20)}")
            
            # Get image dimensions based on platform
            width, height = self._get_image_dimensions(config)
            
            # Подготовить шрифты
            self._prepare_fonts(config)
            
            # Generate images for each slide
            slides_data = []
            
            for i, slide_text in enumerate(slides_text):
                logger.debug(f"Generating slide {i + 1}/{len(slides_text)}")
                
                # Create slide image
                image_bytes = self._create_slide_image(
                    text=slide_text,
                    config=config,
                    width=width,
                    height=height,
                    slide_number=i + 1,
                    total_slides=len(slides_text)
                )
                
                slides_data.append({
                    'text': slide_text,
                    'image_bytes': image_bytes,
                    'width': width,
                    'height': height,
                    'slide_number': i + 1
                })
            
            result = {
                'total_slides': len(slides_text),
                'slides': slides_data,
                'config_used': config,
                'dimensions': {'width': width, 'height': height}
            }
            
            logger.info(f"Successfully generated {len(slides_text)} carousel slides")
            return result
            
        except Exception as e:
            logger.error(f"Error generating carousel: {str(e)}")
            raise
    
    def _prepare_fonts(self, config: Dict[str, Any]):
        """
        Подготовить шрифты для использования (загрузить Google Fonts если нужно)
        
        Args:
            config: Configuration dictionary
        """
        
        font_family = config.get('font_family', 'Inter')
        font_weight = config.get('font_weight', '400')
        
        # Проверить, есть ли шрифт в кэше
        font_key = f"{font_family}-{font_weight}"
        
        if font_key not in self.fonts_cache:
            font_path = self._get_google_font(font_family, font_weight)
            if font_path:
                self.fonts_cache[font_key] = font_path
                logger.info(f"Loaded Google Font: {font_family} {font_weight}")
            else:
                # Fallback к системному шрифту
                self.fonts_cache[font_key] = self._get_fallback_font_path()
                logger.warning(f"Using fallback font for {font_family}")
    
    def _get_google_font(self, family: str, weight: str = '400') -> Optional[str]:
        """
        Загрузить Google Font и вернуть путь к файлу
        
        Args:
            family: Название семейства шрифта (например, 'Inter', 'Roboto')
            weight: Вес шрифта ('300', '400', '500', '600', '700')
            
        Returns:
            Путь к файлу шрифта или None если загрузка не удалась
        """
        
        try:
            # Проверить, есть ли уже загруженный шрифт
            font_filename = f"{family.replace(' ', '')}-{weight}.ttf"
            font_path = os.path.join(self.fonts_dir, font_filename)
            
            if os.path.exists(font_path):
                return font_path
            
            # Получить URL для загрузки шрифта
            download_url = self._get_font_download_url(family, weight)
            
            if download_url:
                # Загрузить шрифт
                response = requests.get(download_url, timeout=30)
                response.raise_for_status()
                
                # Сохранить в файл
                with open(font_path, 'wb') as f:
                    f.write(response.content)
                
                logger.info(f"Downloaded Google Font: {family} {weight}")
                return font_path
            
        except Exception as e:
            logger.error(f"Failed to download Google Font {family} {weight}: {e}")
        
        return None
    
    def _get_font_download_url(self, family: str, weight: str) -> Optional[str]:
        """
        Получить URL для загрузки Google Font
        
        Args:
            family: Название семейства шрифта
            weight: Вес шрифта
            
        Returns:
            URL для загрузки или None
        """
        
        try:
            # Использовать Google Fonts API для получения URL
            if self.google_fonts_api_key:
                api_url = f"https://www.googleapis.com/webfonts/v1/webfonts"
                params = {'key': self.google_fonts_api_key, 'family': family}
                
                response = requests.get(api_url, params=params, timeout=10)
                response.raise_for_status()
                
                data = response.json()
                if 'items' in data and len(data['items']) > 0:
                    font_data = data['items'][0]
                    if 'files' in font_data and weight in font_data['files']:
                        return font_data['files'][weight]
            
            # Fallback: использовать прямые ссылки Google Fonts CSS API
            css_url = f"https://fonts.googleapis.com/css2?family={family.replace(' ', '+')}:wght@{weight}&display=swap"
            
            response = requests.get(css_url, timeout=10)
            response.raise_for_status()
            
            # Парсить CSS для получения URL .ttf файла
            css_content = response.text
            
            # Найти URL в CSS (упрощенный парсинг)
            import re
            url_match = re.search(r'url\((https://[^)]+\.ttf)\)', css_content)
            if url_match:
                return url_match.group(1)
                
        except Exception as e:
            logger.error(f"Failed to get font download URL for {family}: {e}")
        
        return None
    
    def _parse_slides(self, text: str, config: Dict[str, Any]) -> List[str]:
        """
        Parse text into individual slides using separators
        
        Args:
            text: Raw text content
            config: Configuration dictionary
            
        Returns:
            List of slide text content
        """
        
        separator = config.get('slide_separator', current_app.config.get('SLIDE_SEPARATOR', '========'))
        
        # Split by separator and clean up
        slides = [slide.strip() for slide in text.split(separator)]
        
        # Remove empty slides
        slides = [slide for slide in slides if slide]
        
        # If no separators found and text is long, try to auto-split
        if len(slides) == 1 and len(text) > 1000:
            slides = self._auto_split_text(text)
        
        return slides
    
    def _auto_split_text(self, text: str) -> List[str]:
        """
        Automatically split long text into slides
        
        Args:
            text: Long text content
            
        Returns:
            List of slide texts
        """
        
        # Split by paragraphs first
        paragraphs = [p.strip() for p in text.split('\n\n') if p.strip()]
        
        slides = []
        current_slide = ""
        max_chars_per_slide = 800
        
        for paragraph in paragraphs:
            if len(current_slide + paragraph) < max_chars_per_slide:
                current_slide += "\n\n" + paragraph if current_slide else paragraph
            else:
                if current_slide:
                    slides.append(current_slide.strip())
                current_slide = paragraph
        
        if current_slide:
            slides.append(current_slide.strip())
        
        return slides
    
    def _get_image_dimensions(self, config: Dict[str, Any]) -> Tuple[int, int]:
        """
        Get image dimensions based on platform or custom settings
        
        Args:
            config: Configuration dictionary
            
        Returns:
            Tuple of (width, height)
        """
        
        # Check for custom dimensions first
        if config.get('custom_width') and config.get('custom_height'):
            return config['custom_width'], config['custom_height']
        
        # Get platform specifications
        platform = config.get('platform', 'instagram_post')
        platform_specs = current_app.config.get('PLATFORM_SPECS', {})
        
        if platform in platform_specs:
            specs = platform_specs[platform]
            return specs['width'], specs['height']
        
        # Fallback to default
        return (
            current_app.config.get('DEFAULT_IMAGE_WIDTH', 1080),
            current_app.config.get('DEFAULT_IMAGE_HEIGHT', 1080)
        )
    
    def _create_slide_image(
        self, 
        text: str, 
        config: Dict[str, Any], 
        width: int, 
        height: int,
        slide_number: int,
        total_slides: int
    ) -> bytes:
        """
        Create a single slide image
        
        Args:
            text: Text content for the slide
            config: Styling configuration
            width: Image width
            height: Image height
            slide_number: Current slide number
            total_slides: Total number of slides
            
        Returns:
            Image bytes (PNG format)
        """
        
        # Create image with background color
        bg_color = config.get('background_color', '#ffffff')
        image = Image.new('RGB', (width, height), ImageColor.getrgb(bg_color))
        draw = ImageDraw.Draw(image)
        
        # Apply corner radius if specified
        corner_radius = config.get('corner_radius', 0)
        if corner_radius > 0:
            image = self._apply_corner_radius(image, corner_radius)
            draw = ImageDraw.Draw(image)
        
        # Get fonts
        font_size = config.get('font_size', 44)
        title_font_size = config.get('title_font_size', 56)
        
        regular_font = self._get_font(font_size, config)
        title_font = self._get_font(title_font_size, config)
        
        # Parse text content (titles vs regular text)
        parsed_content = self._parse_slide_content(text)
        
        # Calculate layout
        padding = config.get('padding', 80)
        content_width = width - (2 * padding)
        content_height = height - (2 * padding)
        
        # Render content
        y_position = padding
        text_color = ImageColor.getrgb(config.get('text_color', '#000000'))
        line_spacing = config.get('line_spacing', 1.2)
        text_align = config.get('text_align', 'left')
        
        for content_item in parsed_content:
            if content_item['type'] == 'title':
                y_position = self._draw_text_block(
                    draw=draw,
                    text=content_item['text'],
                    font=title_font,
                    color=text_color,
                    x=padding,
                    y=y_position,
                    max_width=content_width,
                    line_spacing=line_spacing,
                    align=text_align
                )
                y_position += 30  # Extra spacing after titles
                
            elif content_item['type'] == 'text':
                y_position = self._draw_text_block(
                    draw=draw,
                    text=content_item['text'],
                    font=regular_font,
                    color=text_color,
                    x=padding,
                    y=y_position,
                    max_width=content_width,
                    line_spacing=line_spacing,
                    align=text_align
                )
                y_position += 20  # Normal spacing
        
        # Add page numbers if enabled
        if config.get('add_page_numbers', False):
            self._add_page_numbers(
                draw=draw,
                slide_number=slide_number,
                total_slides=total_slides,
                width=width,
                height=height,
                font=regular_font,
                color=text_color
            )
        
        # Add logo text if enabled
        if config.get('add_logo_text', False) and config.get('logo_text'):
            self._add_logo_text(
                draw=draw,
                logo_text=config['logo_text'],
                width=width,
                height=height,
                font=regular_font,
                color=text_color
            )
        
        # Convert to bytes
        img_byte_arr = io.BytesIO()
        image.save(img_byte_arr, format='PNG', quality=95, optimize=True)
        img_byte_arr = img_byte_arr.getvalue()
        
        return img_byte_arr
    
    def _parse_slide_content(self, text: str) -> List[Dict[str, str]]:
        """
        Parse slide text into structured content (titles, text, etc.)
        
        Args:
            text: Raw slide text
            
        Returns:
            List of content items with type and text
        """
        
        content_items = []
        lines = text.split('\n')
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            # Check if line is a title (marked with ** or #)
            if line.startswith('**') and line.endswith('**'):
                # Bold markdown style title
                title_text = line[2:-2].strip()
                content_items.append({'type': 'title', 'text': title_text})
                
            elif line.startswith('#'):
                # Markdown header style title
                title_text = line.lstrip('#').strip()
                content_items.append({'type': 'title', 'text': title_text})
                
            elif line.isupper() and len(line) < 50:
                # All caps short text as title
                content_items.append({'type': 'title', 'text': line})
                
            else:
                # Regular text
                content_items.append({'type': 'text', 'text': line})
        
        return content_items
    
    def _draw_text_block(
        self,
        draw: ImageDraw.Draw,
        text: str,
        font: ImageFont.FreeTypeFont,
        color: Tuple[int, int, int],
        x: int,
        y: int,
        max_width: int,
        line_spacing: float = 1.2,
        align: str = 'left'
    ) -> int:
        """
        Draw a block of text with proper wrapping and alignment
        
        Args:
            draw: ImageDraw object
            text: Text to draw
            font: Font to use
            color: Text color
            x: X position
            y: Y position
            max_width: Maximum width for text wrapping
            line_spacing: Line spacing multiplier
            align: Text alignment (left, center, right)
            
        Returns:
            Y position after drawing (for next element)
        """
        
        # Wrap text to fit width
        wrapped_lines = self._wrap_text(text, font, max_width)
        
        current_y = y
        
        for line in wrapped_lines:
            # Calculate line width for alignment
            line_bbox = draw.textbbox((0, 0), line, font=font)
            line_width = line_bbox[2] - line_bbox[0]
            line_height = line_bbox[3] - line_bbox[1]
            
            # Calculate x position based on alignment
            if align == 'center':
                line_x = x + (max_width - line_width) // 2
            elif align == 'right':
                line_x = x + max_width - line_width
            else:  # left
                line_x = x
            
            # Draw the line
            draw.text((line_x, current_y), line, font=font, fill=color)
            
            # Move to next line
            current_y += int(line_height * line_spacing)
        
        return current_y
    
    def _wrap_text(self, text: str, font: ImageFont.FreeTypeFont, max_width: int) -> List[str]:
        """
        Wrap text to fit within specified width
        
        Args:
            text: Text to wrap
            font: Font being used
            max_width: Maximum width in pixels
            
        Returns:
            List of wrapped text lines
        """
        
        words = text.split()
        lines = []
        current_line = ""
        
        for word in words:
            # Test adding this word to current line
            test_line = f"{current_line} {word}".strip()
            
            # Get text width
            bbox = font.getbbox(test_line)
            text_width = bbox[2] - bbox[0]
            
            if text_width <= max_width:
                current_line = test_line
            else:
                # Current line is full, start new line
                if current_line:
                    lines.append(current_line)
                current_line = word
                
                # Check if single word is too long
                word_bbox = font.getbbox(word)
                word_width = word_bbox[2] - word_bbox[0]
                
                if word_width > max_width:
                    # Word is too long, need to break it
                    lines.extend(self._break_long_word(word, font, max_width))
                    current_line = ""
        
        if current_line:
            lines.append(current_line)
        
        return lines
    
    def _break_long_word(self, word: str, font: ImageFont.FreeTypeFont, max_width: int) -> List[str]:
        """
        Break a long word that doesn't fit on one line
        
        Args:
            word: Word to break
            font: Font being used
            max_width: Maximum width in pixels
            
        Returns:
            List of word parts
        """
        
        parts = []
        current_part = ""
        
        for char in word:
            test_part = current_part + char
            bbox = font.getbbox(test_part)
            width = bbox[2] - bbox[0]
            
            if width <= max_width:
                current_part = test_part
            else:
                if current_part:
                    parts.append(current_part)
                current_part = char
        
        if current_part:
            parts.append(current_part)
        
        return parts
    
    def _add_page_numbers(
        self,
        draw: ImageDraw.Draw,
        slide_number: int,
        total_slides: int,
        width: int,
        height: int,
        font: ImageFont.FreeTypeFont,
        color: Tuple[int, int, int]
    ):
        """Add page numbers to the slide"""
        
        page_text = f"{slide_number}/{total_slides}"
        
        # Get text dimensions
        bbox = draw.textbbox((0, 0), page_text, font=font)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]
        
        # Position at bottom right
        x = width - text_width - 20
        y = height - text_height - 20
        
        draw.text((x, y), page_text, font=font, fill=color)
    
    def _add_logo_text(
        self,
        draw: ImageDraw.Draw,
        logo_text: str,
        width: int,
        height: int,
        font: ImageFont.FreeTypeFont,
        color: Tuple[int, int, int]
    ):
        """Add logo text to the slide"""
        
        # Get text dimensions
        bbox = draw.textbbox((0, 0), logo_text, font=font)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]
        
        # Position at bottom left
        x = 20
        y = height - text_height - 20
        
        draw.text((x, y), logo_text, font=font, fill=color)
    
    def _apply_corner_radius(self, image: Image.Image, radius: int) -> Image.Image:
        """
        Apply corner radius to image
        
        Args:
            image: PIL Image
            radius: Corner radius in pixels
            
        Returns:
            Image with rounded corners
        """
        
        # Create a mask with rounded corners
        mask = Image.new('L', image.size, 0)
        mask_draw = ImageDraw.Draw(mask)
        
        # Draw rounded rectangle on mask
        mask_draw.rounded_rectangle(
            [(0, 0), image.size],
            radius=radius,
            fill=255
        )
        
        # Apply mask to image
        image.putalpha(mask)
        
        return image
    
    def _get_font(self, size: int, config: Dict[str, Any]) -> ImageFont.FreeTypeFont:
        """
        Get font object with specified size using Google Fonts
        
        Args:
            size: Font size in pixels
            config: Configuration dictionary containing font settings
            
        Returns:
            PIL Font object
        """
        
        font_family = config.get('font_family', 'Inter')
        font_weight = config.get('font_weight', '400')
        font_key = f"{font_family}-{font_weight}"
        
        # Получить путь к шрифту из кэша
        font_path = self.fonts_cache.get(font_key)
        
        if font_path and os.path.exists(font_path):
            try:
                return ImageFont.truetype(font_path, size)
            except Exception as e:
                logger.warning(f"Failed to load cached font {font_path}: {e}")
        
        # Fallback к системному шрифту
        fallback_path = self._get_fallback_font_path()
        if fallback_path:
            try:
                return ImageFont.truetype(fallback_path, size)
            except Exception:
                pass
        
        # Последний fallback - шрифт по умолчанию PIL
        logger.warning("Using PIL default font")
        return ImageFont.load_default()
    
    def _get_fallback_font_path(self) -> str:
        """Get path to fallback system font file"""
        
        # Try common system font paths
        font_paths = [
            # Ubuntu/Debian
            '/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',
            '/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf',
            # CentOS/RHEL
            '/usr/share/fonts/liberation/LiberationSans-Regular.ttf',
            # macOS
            '/System/Library/Fonts/Arial.ttf',
            '/System/Library/Fonts/Helvetica.ttc',
            # Windows
            'C:/Windows/Fonts/arial.ttf',
            'C:/Windows/Fonts/calibri.ttf',
            # Local fonts directory
            'fonts/DejaVuSans.ttf',
            'fonts/arial.ttf'
        ]
        
        for path in font_paths:
            if os.path.exists(path):
                try:
                    ImageFont.truetype(path, 20)  # Test load
                    return path
                except Exception:
                    continue
        
        logger.warning("No suitable fallback font found")
        return ""
    
    def get_available_google_fonts(self) -> List[Dict[str, Any]]:
        """
        Получить список доступных Google Fonts
        
        Returns:
            Список шрифтов с их характеристиками
        """
        
        if not self.google_fonts_api_key:
            return self._get_popular_fonts_list()
        
        try:
            api_url = "https://www.googleapis.com/webfonts/v1/webfonts"
            params = {'key': self.google_fonts_api_key, 'sort': 'popularity'}
            
            response = requests.get(api_url, params=params, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            fonts_list = []
            
            for font in data.get('items', [])[:50]:  # Ограничить до 50 популярных
                fonts_list.append({
                    'family': font['family'],
                    'category': font.get('category', 'sans-serif'),
                    'variants': font.get('variants', ['400']),
                    'subsets': font.get('subsets', ['latin'])
                })
            
            return fonts_list
            
        except Exception as e:
            logger.error(f"Failed to fetch Google Fonts list: {e}")
            return self._get_popular_fonts_list()
    
    def _get_popular_fonts_list(self) -> List[Dict[str, Any]]:
        """Возвращает список популярных шрифтов без API"""
        
        return [
            {'family': 'Inter', 'category': 'sans-serif', 'variants': ['300', '400', '500', '600', '700']},
            {'family': 'Roboto', 'category': 'sans-serif', 'variants': ['300', '400', '500', '700']},
            {'family': 'Open Sans', 'category': 'sans-serif', 'variants': ['300', '400', '600', '700']},
            {'family': 'Lato', 'category': 'sans-serif', 'variants': ['300', '400', '700']},
            {'family': 'Montserrat', 'category': 'sans-serif', 'variants': ['300', '400', '500', '600', '700']},
            {'family': 'Poppins', 'category': 'sans-serif', 'variants': ['300', '400', '500', '600', '700']},
            {'family': 'Source Sans Pro', 'category': 'sans-serif', 'variants': ['300', '400', '600', '700']},
            {'family': 'Nunito', 'category': 'sans-serif', 'variants': ['300', '400', '600', '700']},
            {'family': 'PT Sans', 'category': 'sans-serif', 'variants': ['400', '700']},
            {'family': 'Raleway', 'category': 'sans-serif', 'variants': ['300', '400', '500', '600', '700']},
            {'family': 'Playfair Display', 'category': 'serif', 'variants': ['400', '700']},
            {'family': 'Merriweather', 'category': 'serif', 'variants': ['300', '400', '700']},
            {'family': 'Lora', 'category': 'serif', 'variants': ['400', '700']},
            {'family': 'Crimson Text', 'category': 'serif', 'variants': ['400', '600', '700']},
        ]
