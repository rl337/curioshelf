"""
Tests for SVG validation and rasterization verification
"""

import pytest
import tempfile
import os
import xml.etree.ElementTree as ET
from pathlib import Path
from PIL import Image, ImageDraw
import io
import hashlib

from curioshelf.sprite_generator import generate_sample_sprites
from curioshelf.sprite_generators.plugins.stick_figure import StickFigureSprite


class TestSVGValidation:
    """Test SVG format validity and structure"""
    
    def test_svg_xml_validity(self):
        """Test that generated SVGs are valid XML"""
        sprite = StickFigureSprite(64, 64)
        frames = sprite.generate_walk_cycle(3)
        
        for i, frame in enumerate(frames):
            # Parse as XML to check validity
            try:
                root = ET.fromstring(frame)
                # Check that it's an SVG element (with or without namespace)
                assert root.tag in ['svg', '{http://www.w3.org/2000/svg}svg']
            except ET.ParseError as e:
                pytest.fail(f"Frame {i} is not valid XML: {e}")
    
    def test_svg_namespace(self):
        """Test that SVG has proper namespace declaration"""
        sprite = StickFigureSprite(64, 64)
        frames = sprite.generate_walk_cycle(1)
        
        svg_content = frames[0]
        assert 'xmlns="http://www.w3.org/2000/svg"' in svg_content
        assert 'xmlns:svg="http://www.w3.org/2000/svg"' not in svg_content  # Should not have duplicate
    
    def test_svg_dimensions(self):
        """Test that SVG has correct width and height attributes"""
        sprite = StickFigureSprite(32, 48)
        frames = sprite.generate_walk_cycle(1)
        
        svg_content = frames[0]
        assert 'width="32"' in svg_content
        assert 'height="48"' in svg_content
    
    def test_svg_structure_elements(self):
        """Test that SVG contains expected structural elements"""
        sprite = StickFigureSprite(64, 64)
        frames = sprite.generate_walk_cycle(1)
        
        svg_content = frames[0]
        
        # Should have background rect
        assert '<rect' in svg_content
        assert 'fill="transparent"' in svg_content
        
        # Should have stick figure elements
        assert '<circle' in svg_content  # Head
        assert '<line' in svg_content    # Body parts
        
        # Should have proper stroke attributes
        assert 'stroke="#000000"' in svg_content
        assert 'stroke-width=' in svg_content
    
    def test_svg_closing_tag(self):
        """Test that SVG is properly closed"""
        sprite = StickFigureSprite(64, 64)
        frames = sprite.generate_walk_cycle(1)
        
        svg_content = frames[0]
        assert svg_content.strip().endswith('</svg>')
    
    def test_all_animation_types_svg_validity(self):
        """Test that all animation types produce valid SVG"""
        sprite = StickFigureSprite(64, 64)
        
        animations = [
            sprite.generate_walk_cycle(3),
            sprite.generate_stopping_cycle(3),
            sprite.generate_speeding_up_cycle(3),
            sprite.generate_jumping_cycle(3)
        ]
        
        for anim_name, frames in zip(['walk', 'stopping', 'speeding_up', 'jumping'], animations):
            for i, frame in enumerate(frames):
                try:
                    root = ET.fromstring(frame)
                    assert root.tag in ['svg', '{http://www.w3.org/2000/svg}svg']
                except ET.ParseError as e:
                    pytest.fail(f"{anim_name} frame {i} is not valid XML: {e}")


class TestSVGRasterization:
    """Test SVG rasterization and visual content verification"""
    
    def _rasterize_svg(self, svg_content: str, width: int, height: int) -> Image.Image:
        """Convert SVG to PIL Image for testing"""
        try:
            from PIL import Image, ImageDraw
            
            # Create a white background image
            img = Image.new('RGB', (width, height), 'white')
            draw = ImageDraw.Draw(img)
            
            # Parse SVG and draw basic elements
            root = ET.fromstring(svg_content)
            
            # Define namespace for SVG elements
            ns = {'svg': 'http://www.w3.org/2000/svg'}
            
            # Draw circles (head) - handle both namespaced and non-namespaced
            for circle in root.findall('.//circle') + root.findall('.//{http://www.w3.org/2000/svg}circle'):
                cx = float(circle.get('cx', 0))
                cy = float(circle.get('cy', 0))
                r = float(circle.get('r', 0))
                stroke_width = int(float(circle.get('stroke-width', 2)))
                draw.ellipse([cx-r, cy-r, cx+r, cy+r], outline='black', width=stroke_width)
            
            # Draw lines (body parts) - handle both namespaced and non-namespaced
            for line in root.findall('.//line') + root.findall('.//{http://www.w3.org/2000/svg}line'):
                x1 = float(line.get('x1', 0))
                y1 = float(line.get('y1', 0))
                x2 = float(line.get('x2', 0))
                y2 = float(line.get('y2', 0))
                stroke_width = int(float(line.get('stroke-width', 2)))
                draw.line([x1, y1, x2, y2], fill='black', width=stroke_width)
            
            return img
            
        except Exception as e:
            pytest.fail(f"Failed to rasterize SVG: {e}")
    
    def _image_hash(self, img: Image.Image) -> str:
        """Generate a hash for image comparison"""
        # Convert to grayscale and resize to standard size for comparison
        img_gray = img.convert('L').resize((32, 32))
        
        # Get pixel data as bytes
        pixel_data = img_gray.tobytes()
        
        # Generate hash
        return hashlib.md5(pixel_data).hexdigest()
    
    def test_svg_not_blank_when_rasterized(self):
        """Test that rasterized SVG is not blank/empty"""
        sprite = StickFigureSprite(64, 64)
        frames = sprite.generate_walk_cycle(1)
        
        svg_content = frames[0]
        img = self._rasterize_svg(svg_content, 64, 64)
        
        # Check that image is not completely white (blank)
        # Convert to grayscale and check if there are any non-white pixels
        img_gray = img.convert('L')
        pixels = list(img_gray.getdata())
        
        # Should have some non-white pixels (the stick figure)
        non_white_pixels = [p for p in pixels if p < 250]  # Allow for some anti-aliasing
        assert len(non_white_pixels) > 0, "Rasterized SVG appears to be blank"
    
    def test_walk_cycle_frames_are_different(self):
        """Test that walk cycle frames produce different images when rasterized"""
        sprite = StickFigureSprite(64, 64)
        frames = sprite.generate_walk_cycle(5)
        
        # Rasterize all frames
        images = []
        for frame in frames:
            img = self._rasterize_svg(frame, 64, 64)
            images.append(img)
        
        # Generate hashes for comparison
        hashes = [self._image_hash(img) for img in images]
        
        # All frames should be different
        assert len(set(hashes)) > 1, "Walk cycle frames are identical when rasterized"
        
        # At least the first and last frames should be different
        assert hashes[0] != hashes[-1], "First and last walk cycle frames are identical"
    
    def test_stopping_cycle_frames_are_different(self):
        """Test that stopping cycle frames produce different images"""
        sprite = StickFigureSprite(64, 64)
        frames = sprite.generate_stopping_cycle(5)
        
        images = [self._rasterize_svg(frame, 64, 64) for frame in frames]
        hashes = [self._image_hash(img) for img in images]
        
        # Should have some variation
        assert len(set(hashes)) > 1, "Stopping cycle frames are identical when rasterized"
    
    def test_speeding_up_cycle_frames_are_different(self):
        """Test that speeding up cycle frames produce different images"""
        sprite = StickFigureSprite(64, 64)
        frames = sprite.generate_speeding_up_cycle(5)
        
        images = [self._rasterize_svg(frame, 64, 64) for frame in frames]
        hashes = [self._image_hash(img) for img in images]
        
        # Should have some variation
        assert len(set(hashes)) > 1, "Speeding up cycle frames are identical when rasterized"
    
    def test_jumping_cycle_frames_are_different(self):
        """Test that jumping cycle frames produce different images"""
        sprite = StickFigureSprite(64, 64)
        frames = sprite.generate_jumping_cycle(5)
        
        images = [self._rasterize_svg(frame, 64, 64) for frame in frames]
        hashes = [self._image_hash(img) for img in images]
        
        # Should have some variation
        assert len(set(hashes)) > 1, "Jumping cycle frames are identical when rasterized"
    
    def test_different_animations_are_different(self):
        """Test that different animation types produce different images"""
        sprite = StickFigureSprite(64, 64)
        
        # Get first frame from each animation
        walk_frame = sprite.generate_walk_cycle(1)[0]
        stopping_frame = sprite.generate_stopping_cycle(1)[0]
        speeding_frame = sprite.generate_speeding_up_cycle(1)[0]
        jumping_frame = sprite.generate_jumping_cycle(1)[0]
        
        # Rasterize frames
        walk_img = self._rasterize_svg(walk_frame, 64, 64)
        stopping_img = self._rasterize_svg(stopping_frame, 64, 64)
        speeding_img = self._rasterize_svg(speeding_frame, 64, 64)
        jumping_img = self._rasterize_svg(jumping_frame, 64, 64)
        
        # Generate hashes
        hashes = [
            self._image_hash(walk_img),
            self._image_hash(stopping_img),
            self._image_hash(speeding_img),
            self._image_hash(jumping_img)
        ]
        
        # All animations should be different
        assert len(set(hashes)) > 1, "Different animation types produce identical images"
    
    def test_svg_scales_properly(self):
        """Test that SVG content scales with different sizes"""
        # Generate same animation at different sizes
        small_sprite = StickFigureSprite(32, 32)
        large_sprite = StickFigureSprite(128, 128)
        
        small_frames = small_sprite.generate_walk_cycle(1)
        large_frames = large_sprite.generate_walk_cycle(1)
        
        small_svg = small_frames[0]
        large_svg = large_frames[0]
        
        # Check dimensions
        assert 'width="32"' in small_svg
        assert 'height="32"' in small_svg
        assert 'width="128"' in large_svg
        assert 'height="128"' in large_svg
        
        # Both should be valid SVG
        ET.fromstring(small_svg)
        ET.fromstring(large_svg)


class TestGeneratedFilesSVGValidation:
    """Test SVG validation for files generated by generate_sample_sprites"""
    
    def test_generated_files_are_valid_svg(self):
        """Test that all generated files are valid SVG"""
        with tempfile.TemporaryDirectory() as temp_dir:
            generate_sample_sprites(output_dir=temp_dir, count=3, width=32, height=32)
            
            temp_path = Path(temp_dir)
            
            # Check all generated SVG files
            for svg_file in temp_path.rglob("*.svg"):
                with open(svg_file, 'r') as f:
                    svg_content = f.read()
                
                try:
                    root = ET.fromstring(svg_content)
                    assert root.tag in ['svg', '{http://www.w3.org/2000/svg}svg']
                except ET.ParseError as e:
                    pytest.fail(f"Generated file {svg_file} is not valid SVG: {e}")
    
    def test_generated_files_have_visual_content(self):
        """Test that generated files produce non-blank images when rasterized"""
        with tempfile.TemporaryDirectory() as temp_dir:
            generate_sample_sprites(output_dir=temp_dir, count=2, width=64, height=64)
            
            temp_path = Path(temp_dir)
            
            # Test a few files from each animation
            for anim_dir in ['walk', 'stopping', 'speeding_up', 'jumping']:
                anim_path = temp_path / anim_dir
                svg_files = list(anim_path.glob("*.svg"))
                
                for svg_file in svg_files[:2]:  # Test first 2 files
                    with open(svg_file, 'r') as f:
                        svg_content = f.read()
                    
                    # Rasterize and check for content
                    img = self._rasterize_svg(svg_content, 64, 64)
                    img_gray = img.convert('L')
                    pixels = list(img_gray.getdata())
                    
                    non_white_pixels = [p for p in pixels if p < 250]
                    assert len(non_white_pixels) > 0, f"Generated file {svg_file} appears blank when rasterized"
    
    def _rasterize_svg(self, svg_content: str, width: int, height: int) -> Image.Image:
        """Convert SVG to PIL Image for testing"""
        try:
            from PIL import Image, ImageDraw
            
            # Create a white background image
            img = Image.new('RGB', (width, height), 'white')
            draw = ImageDraw.Draw(img)
            
            # Parse SVG and draw basic elements
            root = ET.fromstring(svg_content)
            
            # Draw circles (head) - handle both namespaced and non-namespaced
            for circle in root.findall('.//circle') + root.findall('.//{http://www.w3.org/2000/svg}circle'):
                cx = float(circle.get('cx', 0))
                cy = float(circle.get('cy', 0))
                r = float(circle.get('r', 0))
                stroke_width = int(float(circle.get('stroke-width', 2)))
                draw.ellipse([cx-r, cy-r, cx+r, cy+r], outline='black', width=stroke_width)
            
            # Draw lines (body parts) - handle both namespaced and non-namespaced
            for line in root.findall('.//line') + root.findall('.//{http://www.w3.org/2000/svg}line'):
                x1 = float(line.get('x1', 0))
                y1 = float(line.get('y1', 0))
                x2 = float(line.get('x2', 0))
                y2 = float(line.get('y2', 0))
                stroke_width = int(float(line.get('stroke-width', 2)))
                draw.line([x1, y1, x2, y2], fill='black', width=stroke_width)
            
            return img
            
        except Exception as e:
            pytest.fail(f"Failed to rasterize SVG: {e}")
