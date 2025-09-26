"""
Robust SVG validation using svglib to actually parse and validate SVG content
"""

import pytest
import tempfile
import os
from pathlib import Path
from svglib.svglib import svg2rlg
from reportlab.graphics import renderPDF
from reportlab.graphics.shapes import Drawing
import xml.etree.ElementTree as ET

from curioshelf.sprite_generator import generate_sample_sprites
from curioshelf.sprite_generators.plugins.stick_figure import StickFigureSprite


class TestSVGRobustValidation:
    """Test SVG using svglib for proper SVG parsing and validation"""
    
    def _parse_svg_with_svglib(self, svg_content: str) -> Drawing:
        """Helper method to parse SVG content with svglib"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.svg', delete=False) as f:
            f.write(svg_content)
            temp_file = f.name
        
        try:
            drawing = svg2rlg(temp_file)
            return drawing
        finally:
            # Clean up temp file
            os.unlink(temp_file)
    
    def test_svg_parses_with_svglib(self):
        """Test that generated SVGs can be parsed by svglib"""
        sprite = StickFigureSprite(64, 64)
        frames = sprite.generate_walk_cycle(3)
        
        for i, frame in enumerate(frames):
            try:
                drawing = self._parse_svg_with_svglib(frame)
                assert drawing is not None
                assert isinstance(drawing, Drawing)
            except Exception as e:
                pytest.fail(f"Walk frame {i} failed to parse with svglib: {e}")
    
    def test_svg_has_visible_elements(self):
        """Test that parsed SVG has visible elements"""
        sprite = StickFigureSprite(64, 64)
        frames = sprite.generate_walk_cycle(1)
        
        frame = frames[0]
        drawing = self._parse_svg_with_svglib(frame)
        
        # Check that drawing has content
        assert drawing is not None
        assert hasattr(drawing, 'contents')
        assert len(drawing.contents) > 0, "SVG has no visible elements"
        
        # Check for specific element types
        element_types = [type(element).__name__ for element in drawing.contents]
        print(f"SVG element types: {element_types}")
        
        # Should have some drawing elements (may be wrapped in Group)
        def has_drawing_elements(contents):
            for element in contents:
                elem_type = type(element).__name__
                if 'Circle' in elem_type or 'Line' in elem_type or 'Rect' in elem_type:
                    return True
                # Check if it's a Group with drawing elements inside
                if elem_type == 'Group' and hasattr(element, 'contents'):
                    if has_drawing_elements(element.contents):
                        return True
            return False
        
        assert has_drawing_elements(drawing.contents), f"No drawing elements found: {element_types}"
    
    def test_svg_elements_have_valid_properties(self):
        """Test that SVG elements have valid properties"""
        sprite = StickFigureSprite(64, 64)
        frames = sprite.generate_walk_cycle(1)
        
        frame = frames[0]
        drawing = self._parse_svg_with_svglib(frame)
        
        for element in drawing.contents:
            # Check that elements have valid properties
            if hasattr(element, 'x') and hasattr(element, 'y'):
                # Position elements should have valid coordinates
                assert isinstance(element.x, (int, float)), f"Invalid x coordinate: {element.x}"
                assert isinstance(element.y, (int, float)), f"Invalid y coordinate: {element.y}"
            
            if hasattr(element, 'width') and hasattr(element, 'height'):
                # Size elements should have positive dimensions
                assert element.width > 0, f"Invalid width: {element.width}"
                assert element.height > 0, f"Invalid height: {element.height}"
            
            if hasattr(element, 'radius'):
                # Circle elements should have positive radius
                assert element.radius > 0, f"Invalid radius: {element.radius}"
    
    def test_all_animation_types_parse_with_svglib(self):
        """Test that all animation types can be parsed by svglib"""
        sprite = StickFigureSprite(64, 64)
        
        animations = [
            ('walk', sprite.generate_walk_cycle(2)),
            ('stopping', sprite.generate_stopping_cycle(2)),
            ('speeding_up', sprite.generate_speeding_up_cycle(2)),
            ('jumping', sprite.generate_jumping_cycle(2))
        ]
        
        for anim_name, frames in animations:
            for i, frame in enumerate(frames):
                try:
                    drawing = self._parse_svg_with_svglib(frame)
                    assert drawing is not None
                    assert len(drawing.contents) > 0, f"{anim_name} frame {i} has no content"
                except Exception as e:
                    pytest.fail(f"{anim_name} frame {i} failed to parse with svglib: {e}")
    
    def test_svg_can_be_rendered_to_pdf(self):
        """Test that SVG can be rendered to PDF (indicates valid SVG)"""
        sprite = StickFigureSprite(64, 64)
        frames = sprite.generate_walk_cycle(1)
        
        frame = frames[0]
        drawing = self._parse_svg_with_svglib(frame)
        
        # Try to render to PDF (this will fail if SVG is invalid)
        try:
            pdf_data = renderPDF.drawToString(drawing)
            assert len(pdf_data) > 0, "PDF rendering produced empty data"
        except Exception as e:
            pytest.fail(f"SVG failed to render to PDF: {e}")
    
    def test_svg_elements_are_within_bounds(self):
        """Test that all SVG elements are within the specified bounds"""
        sprite = StickFigureSprite(64, 64)
        frames = sprite.generate_walk_cycle(1)
        
        frame = frames[0]
        drawing = self._parse_svg_with_svglib(frame)
        
        # Check that all elements are within bounds
        for element in drawing.contents:
            if hasattr(element, 'x') and hasattr(element, 'y'):
                assert 0 <= element.x <= 64, f"Element x coordinate {element.x} out of bounds"
                assert 0 <= element.y <= 64, f"Element y coordinate {element.y} out of bounds"
            
            if hasattr(element, 'x1') and hasattr(element, 'y1'):
                assert 0 <= element.x1 <= 64, f"Element x1 coordinate {element.x1} out of bounds"
                assert 0 <= element.y1 <= 64, f"Element y1 coordinate {element.y1} out of bounds"
            
            if hasattr(element, 'x2') and hasattr(element, 'y2'):
                assert 0 <= element.x2 <= 64, f"Element x2 coordinate {element.x2} out of bounds"
                assert 0 <= element.y2 <= 64, f"Element y2 coordinate {element.y2} out of bounds"


class TestGeneratedFilesRobustValidation:
    """Test generated files using svglib validation"""
    
    def _parse_svg_with_svglib(self, svg_content: str) -> Drawing:
        """Helper method to parse SVG content with svglib"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.svg', delete=False) as f:
            f.write(svg_content)
            temp_file = f.name
        
        try:
            drawing = svg2rlg(temp_file)
            return drawing
        finally:
            # Clean up temp file
            os.unlink(temp_file)
    
    def test_generated_files_parse_with_svglib(self):
        """Test that all generated files can be parsed by svglib"""
        with tempfile.TemporaryDirectory() as temp_dir:
            generate_sample_sprites(output_dir=temp_dir, count=2, width=32, height=32)
            
            temp_path = Path(temp_dir)
            
            # Check all generated SVG files
            for svg_file in temp_path.rglob("*.svg"):
                with open(svg_file, 'r') as f:
                    svg_content = f.read()
                
                try:
                    drawing = self._parse_svg_with_svglib(svg_content)
                    assert drawing is not None
                    assert len(drawing.contents) > 0, f"File {svg_file} has no content"
                except Exception as e:
                    pytest.fail(f"Generated file {svg_file} failed to parse with svglib: {e}")
    
    def test_generated_files_have_valid_elements(self):
        """Test that generated files have valid SVG elements"""
        with tempfile.TemporaryDirectory() as temp_dir:
            generate_sample_sprites(output_dir=temp_dir, count=1, width=48, height=48)
            
            temp_path = Path(temp_dir)
            
            for svg_file in temp_path.rglob("*.svg"):
                with open(svg_file, 'r') as f:
                    svg_content = f.read()
                
                drawing = self._parse_svg_with_svglib(svg_content)
                
                # Check that we have the expected elements
                element_types = [type(element).__name__ for element in drawing.contents]
                
                # Should have some drawing elements (may be wrapped in Group)
                def has_drawing_elements(contents):
                    for element in contents:
                        elem_type = type(element).__name__
                        if 'Circle' in elem_type or 'Line' in elem_type or 'Rect' in elem_type:
                            return True
                        # Check if it's a Group with drawing elements inside
                        if elem_type == 'Group' and hasattr(element, 'contents'):
                            if has_drawing_elements(element.contents):
                                return True
                    return False
                
                assert has_drawing_elements(drawing.contents), f"File {svg_file} has no drawing elements: {element_types}"
    
    def test_generated_files_are_within_bounds(self):
        """Test that generated files have elements within specified bounds"""
        with tempfile.TemporaryDirectory() as temp_dir:
            generate_sample_sprites(output_dir=temp_dir, count=1, width=48, height=48)
            
            temp_path = Path(temp_dir)
            
            for svg_file in temp_path.rglob("*.svg"):
                with open(svg_file, 'r') as f:
                    svg_content = f.read()
                
                drawing = self._parse_svg_with_svglib(svg_content)
                
                # Check bounds for all elements
                for element in drawing.contents:
                    if hasattr(element, 'x') and hasattr(element, 'y'):
                        assert 0 <= element.x <= 48, f"Element x {element.x} out of bounds in {svg_file}"
                        assert 0 <= element.y <= 48, f"Element y {element.y} out of bounds in {svg_file}"
                    
                    if hasattr(element, 'x1') and hasattr(element, 'y1'):
                        assert 0 <= element.x1 <= 48, f"Element x1 {element.x1} out of bounds in {svg_file}"
                        assert 0 <= element.y1 <= 48, f"Element y1 {element.y1} out of bounds in {svg_file}"
                    
                    if hasattr(element, 'x2') and hasattr(element, 'y2'):
                        assert 0 <= element.x2 <= 48, f"Element x2 {element.x2} out of bounds in {svg_file}"
                        assert 0 <= element.y2 <= 48, f"Element y2 {element.y2} out of bounds in {svg_file}"


class TestSVGInkscapeCompatibility:
    """Test SVG compatibility with Inkscape-like tools"""
    
    def test_svg_has_proper_viewbox(self):
        """Test that SVG has proper viewBox for Inkscape compatibility"""
        sprite = StickFigureSprite(64, 64)
        frames = sprite.generate_walk_cycle(1)
        
        frame = frames[0]
        
        # Parse as XML to check for viewBox
        root = ET.fromstring(frame)
        
        # Check for viewBox attribute
        viewbox = root.get('viewBox')
        if viewbox:
            # If viewBox exists, it should be valid
            parts = viewbox.split()
            assert len(parts) == 4, f"Invalid viewBox format: {viewbox}"
            assert all(part.replace('.', '').replace('-', '').isdigit() for part in parts), f"Invalid viewBox values: {viewbox}"
        else:
            # If no viewBox, width and height should be present
            width = root.get('width')
            height = root.get('height')
            assert width is not None, "No viewBox and no width attribute"
            assert height is not None, "No viewBox and no height attribute"
    
    def test_svg_has_proper_namespace_declaration(self):
        """Test that SVG has proper namespace declaration for Inkscape"""
        sprite = StickFigureSprite(64, 64)
        frames = sprite.generate_walk_cycle(1)
        
        frame = frames[0]
        
        # Check for proper namespace declaration
        assert 'xmlns="http://www.w3.org/2000/svg"' in frame, "Missing SVG namespace declaration"
        
        # Parse and verify namespace
        root = ET.fromstring(frame)
        assert root.tag in ['svg', '{http://www.w3.org/2000/svg}svg'], f"Invalid root tag: {root.tag}"
    
    def test_svg_has_no_invalid_attributes(self):
        """Test that SVG doesn't have attributes that could crash Inkscape"""
        sprite = StickFigureSprite(64, 64)
        frames = sprite.generate_walk_cycle(1)
        
        frame = frames[0]
        root = ET.fromstring(frame)
        
        # Check for potentially problematic attributes
        def check_element_attributes(element):
            for attr_name, attr_value in element.attrib.items():
                # Check for NaN or infinite values
                if attr_value in ['NaN', 'Infinity', '-Infinity']:
                    pytest.fail(f"Invalid attribute value '{attr_value}' in {attr_name}")
                
                # Check for empty or None values where they shouldn't be
                if attr_name in ['cx', 'cy', 'r', 'x1', 'y1', 'x2', 'y2'] and not attr_value:
                    pytest.fail(f"Empty value for required attribute {attr_name}")
            
            # Recursively check child elements
            for child in element:
                check_element_attributes(child)
        
        check_element_attributes(root)
    
    def test_svg_has_valid_stroke_properties(self):
        """Test that SVG has valid stroke properties"""
        sprite = StickFigureSprite(64, 64)
        frames = sprite.generate_walk_cycle(1)
        
        frame = frames[0]
        root = ET.fromstring(frame)
        
        # Check stroke properties
        for element in root.iter():
            if 'stroke' in element.attrib:
                stroke_color = element.attrib['stroke']
                assert stroke_color in ['#000000', 'black', 'none'], f"Invalid stroke color: {stroke_color}"
            
            if 'stroke-width' in element.attrib:
                stroke_width = element.attrib['stroke-width']
                try:
                    width_val = float(stroke_width)
                    assert width_val > 0, f"Invalid stroke width: {stroke_width}"
                except ValueError:
                    pytest.fail(f"Invalid stroke width format: {stroke_width}")
            
            if 'fill' in element.attrib:
                fill_color = element.attrib['fill']
                assert fill_color in ['none', 'transparent', '#000000', 'black'], f"Invalid fill color: {fill_color}"
