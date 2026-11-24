"""Content generator for InstaNote - creates infographic images"""

from PIL import Image, ImageDraw, ImageFont
import random
from typing import Dict, List, Tuple
from pathlib import Path
import os

# Try to find fonts
def find_font(size: int, bold: bool = False) -> ImageFont.FreeTypeFont:
    """Find available font or use default"""
    # Prioritize Windows fonts
    fonts = [
        'C:\\Windows\\Fonts\\arial.ttf',
        'C:\\Windows\\Fonts\\arialbd.ttf',
        'C:\\Windows\\Fonts\\calibri.ttf',
        'C:\\Windows\\Fonts\\consola.ttf',
        'C:\\Windows\\Fonts\\tahoma.ttf',
    ]
    
    for font_path in fonts:
        if os.path.exists(font_path):
            return ImageFont.truetype(font_path, size)
    
    # Fallback to default
    return ImageFont.load_default()


class InfographicGenerator:
    """Generates handwritten-style infographic images"""
    
    def __init__(self, width: int = 1080, height: int = 1350):
        self.width = width
        self.height = height
        self.colors = {
            'background': (255, 250, 240),
            'paper': (248, 245, 235),
            'accent': (70, 130, 180),
            'text': (40, 40, 40),
            'header': (50, 50, 50),
            'highlight': (255, 100, 100),
            'green': (60, 179, 113),
            'blue': (65, 105, 225),
            'gold': (255, 215, 0),
            'marker': (255, 165, 0),
            'shadow': (0, 0, 0, 100)
        }
    
    def create_image(self, vehicle_specs: Dict) -> Image.Image:
        """Create infographic image for vehicle"""
        img = Image.new('RGB', (self.width, self.height), self.colors['background'])
        draw = ImageDraw.Draw(img)
        
        # Draw notebook paper effect
        self._draw_notebook_paper(img, draw)
        
        # Draw header
        self._draw_header(img, draw, vehicle_specs)
        
        # Draw vehicle illustration placeholder
        self._draw_vehicle_placeholder(img, draw, vehicle_specs)
        
        # Draw specifications sections
        self._draw_specs_sections(img, draw, vehicle_specs)
        
        # Draw footer
        self._draw_footer(img, draw)
        
        return img
    
    def _draw_notebook_paper(self, img: Image.Image, draw: ImageDraw.Draw):
        """Draw notebook paper texture"""
        # Light paper texture
        for x in range(0, self.width, 10):
            draw.line([(x, 0), (x, self.height)], fill=(245, 240, 230), width=1)
        
        # Margin lines
        for y in range(100, self.height - 100, 20):
            draw.line([(50, y), (self.width - 50, y)], fill=(240, 235, 225), width=1)
    
    def _draw_header(self, img: Image.Image, draw: ImageDraw.Draw, specs: Dict):
        """Draw header with vehicle name"""
        name = specs.get('name', 'Vehicle')
        manufacturer = specs.get('manufacturer', '')
        
        # Handwritten title
        title_font = find_font(48, bold=True)
        draw.text((self.width//2, 80), name, fill=self.colors['header'], 
                  font=title_font, anchor='mt')
        
        # Manufacturer subtitle
        sub_font = find_font(28)
        draw.text((self.width//2, 130), f"by {manufacturer}", fill=self.colors['text'],
                  font=sub_font, anchor='mt')
        
        # Decorative line
        draw.line([(self.width//2 - 200, 160), (self.width//2 + 200, 160)], 
                  fill=self.colors['accent'], width=3)
    
    def _draw_vehicle_placeholder(self, img: Image.Image, draw: ImageDraw.Draw, specs: Dict):
        """Draw vehicle illustration placeholder"""
        # Draw a simple vehicle silhouette
        center_x = self.width // 2
        y_start = 200
        
        # Car body
        car_width = 300
        car_height = 120
        draw.ellipse([center_x - car_width//2, y_start, 
                      center_x + car_width//2, y_start + car_height],
                     fill=self.colors['accent'], outline=self.colors['text'], width=2)
        
        # Wheels
        wheel_radius = 30
        for offset in [-80, 80]:
            draw.ellipse([center_x + offset - wheel_radius, y_start + car_height - 20,
                          center_x + offset + wheel_radius, y_start + car_height],
                         fill=self.colors['paper'], outline=self.colors['text'], width=2)
            draw.ellipse([center_x + offset - wheel_radius + 5, y_start + car_height - 15,
                          center_x + offset + wheel_radius - 5, y_start + car_height - 5],
                         fill=self.colors['text'])
        
        # Window
        draw.rectangle([center_x - 80, y_start + 30, center_x + 80, y_start + 80],
                       fill=(200, 220, 240), outline=self.colors['text'])
    
    def _draw_specs_sections(self, img: Image.Image, draw: ImageDraw.Draw, specs: Dict):
        """Draw specifications sections"""
        sections = [
            ('Engine Specs', [
                ('Engine', specs.get('engine', 'N/A')),
                ('Horsepower', specs.get('horsepower', 'N/A')),
                ('Torque', specs.get('torque', 'N/A')),
                ('Transmission', specs.get('transmission', 'N/A'))
            ]),
            ('Dimensions', [
                ('Length', specs.get('dimensions', {}).get('length', 'N/A')),
                ('Width', specs.get('dimensions', {}).get('width', 'N/A')),
                ('Height', specs.get('dimensions', {}).get('height', 'N/A')),
                ('Weight', specs.get('weight', 'N/A'))
            ]),
            ('Performance', [
                ('Top Speed', specs.get('top_speed', 'N/A')),
                ('Mileage/Range', specs.get('mileage', specs.get('range', 'N/A'))),
                ('Fuel Tank', specs.get('fuel_tank', 'N/A')),
                ('Battery', specs.get('battery', 'N/A'))
            ]),
            ('Features', [
                ('Features', ', '.join(specs.get('features', [])[:5]))
            ])
        ]
        
        y_offset = 350
        section_height = 180
        
        for section_name, items in sections:
            # Section background
            draw.rectangle([(40, y_offset), (self.width - 40, y_offset + section_height)],
                          fill=self.colors['paper'], outline=self.colors['accent'], width=2)
            
            # Section title
            title_font = find_font(24, bold=True)
            draw.text((50, y_offset + 15), section_name, fill=self.colors['header'],
                      font=title_font)
            
            # Items
            item_font = find_font(18)
            for i, (label, value) in enumerate(items):
                y = y_offset + 50 + i * 35
                draw.text((60, y), f"{label}:", fill=self.colors['text'], font=item_font)
                draw.text((200, y), value, fill=self.colors['text'], font=item_font)
            
            # Arrow pointer
            draw.polygon([(self.width - 80, y_offset + 30),
                          (self.width - 60, y_offset + 30),
                          (self.width - 70, y_offset + 50)],
                         fill=self.colors['marker'])
            
            y_offset += section_height + 40
    
    def _draw_footer(self, img: Image.Image, draw: ImageDraw.Draw):
        """Draw footer with price and colors"""
        footer_y = self.height - 150
        
        # Price box
        price_box = ImageDraw.Draw(img)
        price_box.rectangle([(50, footer_y), (300, footer_y + 60)],
                           fill=self.colors['highlight'], outline=self.colors['text'])
        
        price_font = find_font(22, bold=True)
        draw.text((175, footer_y + 20), "Price: $99,999", fill='white',
                  font=price_font, anchor='mt')
        
        # Color swatches
        draw.text((350, footer_y + 15), "Colors:", fill=self.colors['header'],
                  font=find_font(18, bold=True))
        
        color_positions = [400, 480, 560, 640, 720]
        colors = [(255, 0, 0), (0, 0, 255), (0, 255, 0), (255, 255, 0), (128, 0, 128)]
        
        for i, (x, color) in enumerate(zip(color_positions, colors)):
            draw.ellipse([x, footer_y + 30, x + 30, footer_y + 50], fill=color)
        
        # Logo
        logo_font = find_font(20)
        draw.text((self.width - 200, footer_y + 25), "InstaNote", 
                  fill=self.colors['accent'], font=logo_font)
    
    def generate_multiple_slides(self, vehicle_specs: Dict) -> List[Image.Image]:
        """Generate multiple slides for extensive information"""
        slides = []
        
        # Slide 1: Overview
        slide1 = self.create_image(vehicle_specs)
        slides.append(slide1)
        
        # Slide 2: Detailed specs
        slide2 = self._create_detail_slide(vehicle_specs)
        slides.append(slide2)
        
        return slides
    
    def _create_detail_slide(self, specs: Dict) -> Image.Image:
        """Create detailed specifications slide"""
        img = Image.new('RGB', (self.width, self.height), self.colors['background'])
        draw = ImageDraw.Draw(img)
        
        # Title
        title_font = find_font(36, bold=True)
        draw.text((self.width//2, 60), "Technical Specifications", 
                  fill=self.colors['header'], font=title_font, anchor='mt')
        
        # Detailed specs table
        table_font = find_font(16)
        y_offset = 150
        
        detailed_specs = [
            ('Engine Capacity', specs.get('engine', 'N/A')),
            ('Horsepower', specs.get('horsepower', 'N/A')),
            ('Torque', specs.get('torque', 'N/A')),
            ('Compression Ratio', 'N/A'),
            ('Bore x Stroke', 'N/A'),
            ('Cooling', 'Liquid'),
            ('Fuel System', 'EFI'),
            ('Transmission', specs.get('transmission', 'N/A')),
            ('Gear Ratios', 'N/A'),
            ('Final Drive', 'Chain'),
            ('Suspension Front', specs.get('suspension', 'N/A').split(',')[0] if specs.get('suspension') else 'N/A'),
            ('Suspension Rear', 'N/A'),
            ('Brakes Front', specs.get('brakes', 'N/A').split(',')[0] if specs.get('brakes') else 'N/A'),
            ('Brakes Rear', 'N/A'),
            ('ABS', 'Yes'),
            ('Wheelbase', 'N/A'),
            ('Seat Height', 'N/A'),
            ('Ground Clearance', 'N/A'),
            ('Weight', specs.get('weight', 'N/A')),
            ('Fuel Capacity', 'N/A'),
        ]
        
        for i, (label, value) in enumerate(detailed_specs):
            y = y_offset + i * 30
            draw.text((60, y), f"{label}:", fill=self.colors['text'], font=table_font)
            draw.text((250, y), value, fill=self.colors['text'], font=table_font)
        
        return img


def generate_infographic(vehicle_specs: Dict, output_path: Path = None) -> Path:
    """Generate infographic image for vehicle"""
    generator = InfographicGenerator()
    img = generator.create_image(vehicle_specs)
    
    if output_path is None:
        output_path = Path(__file__).parent.parent / "output" / f"{vehicle_specs.get('name', 'vehicle').replace(' ', '_')}.png"
    
    output_path.parent.mkdir(parents=True, exist_ok=True)
    img.save(output_path, quality=95)
    
    return output_path


def generate_multiple_infographics(vehicle_specs: Dict) -> List[Path]:
    """Generate multiple infographic slides"""
    generator = InfographicGenerator()
    slides = generator.generate_multiple_slides(vehicle_specs)
    
    paths = []
    for i, slide in enumerate(slides):
        output_path = Path(__file__).parent.parent / "output" / f"{vehicle_specs.get('name', 'vehicle').replace(' ', '_')}_slide{i+1}.png"
        output_path.parent.mkdir(parents=True, exist_ok=True)
        slide.save(output_path, quality=95)
        paths.append(output_path)
    
    return paths


def get_content_generator():
    """Get a content generator instance"""
    return InfographicGenerator()