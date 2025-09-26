"""
Tests for the sprite generator module
"""

import pytest
import tempfile
import os
from pathlib import Path

from curioshelf.sprite_generator import generate_sample_sprites
from curioshelf.sprite_generators.plugins.stick_figure import StickFigureSprite


class TestStickFigureSprite:
    """Test the StickFigureSprite class"""
    
    def test_sprite_initialization(self):
        """Test sprite initialization with different sizes"""
        sprite = StickFigureSprite(64, 64)
        assert sprite.width == 64
        assert sprite.height == 64
        assert sprite.center_x == 32
        assert sprite.center_y == 32
        
        sprite = StickFigureSprite(32, 48)
        assert sprite.width == 32
        assert sprite.height == 48
        assert sprite.center_x == 16
        assert sprite.center_y == 24
    
    def test_walk_cycle_generation(self):
        """Test walk cycle generation"""
        sprite = StickFigureSprite(64, 64)
        frames = sprite.generate_walk_cycle(5)
        
        assert len(frames) == 5
        for frame in frames:
            assert frame.startswith('<svg')
            assert frame.endswith('</svg>')
            assert 'width="64"' in frame
            assert 'height="64"' in frame
    
    def test_stopping_cycle_generation(self):
        """Test stopping cycle generation"""
        sprite = StickFigureSprite(64, 64)
        frames = sprite.generate_stopping_cycle(8)
        
        assert len(frames) == 8
        for frame in frames:
            assert frame.startswith('<svg')
            assert frame.endswith('</svg>')
    
    def test_speeding_up_cycle_generation(self):
        """Test speeding up cycle generation"""
        sprite = StickFigureSprite(64, 64)
        frames = sprite.generate_speeding_up_cycle(8)
        
        assert len(frames) == 8
        for frame in frames:
            assert frame.startswith('<svg')
            assert frame.endswith('</svg>')
    
    def test_jumping_cycle_generation(self):
        """Test jumping cycle generation"""
        sprite = StickFigureSprite(64, 64)
        frames = sprite.generate_jumping_cycle(12)
        
        assert len(frames) == 12
        for frame in frames:
            assert frame.startswith('<svg')
            assert frame.endswith('</svg>')
    
    def test_svg_structure(self):
        """Test that generated SVG has proper structure"""
        sprite = StickFigureSprite(32, 32)
        frames = sprite.generate_walk_cycle(1)
        
        svg_content = frames[0]
        
        # Check for essential SVG elements
        assert '<svg' in svg_content
        assert 'xmlns="http://www.w3.org/2000/svg"' in svg_content
        assert 'width="32"' in svg_content
        assert 'height="32"' in svg_content
        assert '</svg>' in svg_content
        
        # Check for stick figure elements
        assert 'circle' in svg_content  # Head
        assert 'line' in svg_content    # Body parts
        assert 'stroke="#000000"' in svg_content  # Black stroke


class TestGenerateSampleSprites:
    """Test the generate_sample_sprites function"""
    
    def test_generate_samples_default(self):
        """Test generating samples with default parameters"""
        with tempfile.TemporaryDirectory() as temp_dir:
            generate_sample_sprites(output_dir=temp_dir, count=3, width=32, height=32)
            
            # Check that directories were created
            temp_path = Path(temp_dir)
            assert (temp_path / "walk").exists()
            assert (temp_path / "stopping").exists()
            assert (temp_path / "speeding_up").exists()
            assert (temp_path / "jumping").exists()
            assert (temp_path / "README.md").exists()
            
            # Check that files were created
            for anim_dir in ["walk", "stopping", "speeding_up", "jumping"]:
                anim_path = temp_path / anim_dir
                svg_files = list(anim_path.glob("*.svg"))
                assert len(svg_files) == 3
                
                # Check file naming
                for i in range(3):
                    expected_file = anim_path / f"{anim_dir}_{i:03d}.svg"
                    assert expected_file.exists()
    
    def test_generate_samples_custom_params(self):
        """Test generating samples with custom parameters"""
        with tempfile.TemporaryDirectory() as temp_dir:
            generate_sample_sprites(
                output_dir=temp_dir, 
                count=5, 
                width=64, 
                height=48
            )
            
            # Check README content
            readme_path = Path(temp_dir) / "README.md"
            with open(readme_path, 'r') as f:
                readme_content = f.read()
            
            assert "64x48 pixels" in readme_content
            assert "5 frames" in readme_content
    
    def test_generate_samples_existing_directory(self):
        """Test generating samples in existing directory"""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create some existing files
            existing_file = Path(temp_dir) / "existing.txt"
            existing_file.write_text("test")
            
            # Generate samples
            generate_sample_sprites(output_dir=temp_dir, count=2, width=16, height=16)
            
            # Check that existing file is still there
            assert existing_file.exists()
            
            # Check that new directories were created
            assert (Path(temp_dir) / "walk").exists()
            assert (Path(temp_dir) / "README.md").exists()
    
    def test_svg_file_content(self):
        """Test that generated SVG files have valid content"""
        with tempfile.TemporaryDirectory() as temp_dir:
            generate_sample_sprites(output_dir=temp_dir, count=1, width=32, height=32)
            
            # Check one SVG file
            svg_file = Path(temp_dir) / "walk" / "walk_000.svg"
            with open(svg_file, 'r') as f:
                content = f.read()
            
            # Basic SVG validation
            assert content.startswith('<svg')
            assert content.endswith('</svg>')
            assert 'width="32"' in content
            assert 'height="32"' in content
            assert 'circle' in content  # Head
            assert 'line' in content    # Body parts
    
    def test_color_parameter(self):
        """Test that color parameter works correctly"""
        # Test with different colors
        colors_to_test = ['cyan', 'magenta', 'red', 'green', 'blue']
        expected_hex = {
            'cyan': '#00FFFF',
            'magenta': '#FF00FF', 
            'red': '#FF0000',
            'green': '#00FF00',
            'blue': '#0000FF'
        }
        
        for color_name in colors_to_test:
            sprite = StickFigureSprite(32, 32, color_name)
            assert sprite.stroke_color == expected_hex[color_name], f"Color {color_name} should map to {expected_hex[color_name]}"
    
    def test_hex_color_parameter(self):
        """Test that hex color parameter works correctly"""
        hex_color = '#FF5733'
        sprite = StickFigureSprite(32, 32, hex_color)
        assert sprite.stroke_color == hex_color, f"Hex color {hex_color} should be preserved"
    
    def test_invalid_color_fallback(self):
        """Test that invalid colors fallback to black"""
        sprite = StickFigureSprite(32, 32, 'invalidcolor')
        assert sprite.stroke_color == '#000000', "Invalid color should fallback to black"
    
    def test_case_insensitive_colors(self):
        """Test that color names are case insensitive"""
        sprite1 = StickFigureSprite(32, 32, 'CYAN')
        sprite2 = StickFigureSprite(32, 32, 'cyan')
        sprite3 = StickFigureSprite(32, 32, 'Cyan')
        
        assert sprite1.stroke_color == sprite2.stroke_color == sprite3.stroke_color == '#00FFFF'
    
    def test_generate_samples_with_color(self):
        """Test generating samples with custom color"""
        with tempfile.TemporaryDirectory() as temp_dir:
            generate_sample_sprites(output_dir=temp_dir, count=1, width=32, height=32, color='magenta')
            
            # Check that the color is applied in the generated files
            svg_file = Path(temp_dir) / "walk" / "walk_000.svg"
            with open(svg_file, 'r') as f:
                content = f.read()
            
            # Should contain magenta color
            assert '#FF00FF' in content, "Generated SVG should contain magenta color"
            assert 'stroke="#FF00FF"' in content, "Stroke should be magenta"


class TestSpriteSheetGeneration:
    """Test sprite sheet generation functionality"""
    
    def test_generate_sprite_sheet_basic(self):
        """Test basic sprite sheet generation"""
        with tempfile.TemporaryDirectory() as temp_dir:
            from curioshelf.sprite_generator import generate_sprite_sheet
            
            generate_sprite_sheet(
                output_dir=temp_dir, 
                frames_per_animation=2, 
                sprite_width=32, 
                sprite_height=32
            )
            
            # Check that files were created
            assert (Path(temp_dir) / "sprite_sheet.svg").exists()
            assert (Path(temp_dir) / "sprite_metadata.json").exists()
            assert (Path(temp_dir) / "README.md").exists()
    
    def test_sprite_sheet_metadata_structure(self):
        """Test that sprite sheet metadata has correct structure"""
        with tempfile.TemporaryDirectory() as temp_dir:
            from curioshelf.sprite_generator import generate_sprite_sheet
            import json
            
            generate_sprite_sheet(
                output_dir=temp_dir, 
                frames_per_animation=2, 
                sprite_width=32, 
                sprite_height=32
            )
            
            # Load and check metadata
            with open(Path(temp_dir) / "sprite_metadata.json", 'r') as f:
                metadata = json.load(f)
            
            # Check top-level structure
            assert "sprite_sheet" in metadata
            assert "colors" in metadata
            assert "animations" in metadata
            assert "frames_per_animation" in metadata
            assert "sprites" in metadata
            
            # Check sprite sheet info
            sheet_info = metadata["sprite_sheet"]
            assert "width" in sheet_info
            assert "height" in sheet_info
            assert "sprite_width" in sheet_info
            assert "sprite_height" in sheet_info
            assert "columns" in sheet_info
            assert "rows" in sheet_info
            
            # Check that we have the expected number of sprites
            expected_sprites = len(metadata["colors"]) * len(metadata["animations"]) * metadata["frames_per_animation"]
            assert len(metadata["sprites"]) == expected_sprites
    
    def test_sprite_sheet_sprite_properties(self):
        """Test that individual sprites have correct properties"""
        with tempfile.TemporaryDirectory() as temp_dir:
            from curioshelf.sprite_generator import generate_sprite_sheet
            import json
            
            generate_sprite_sheet(
                output_dir=temp_dir, 
                frames_per_animation=2, 
                sprite_width=32, 
                sprite_height=32
            )
            
            with open(Path(temp_dir) / "sprite_metadata.json", 'r') as f:
                metadata = json.load(f)
            
            # Check a few sprites
            for sprite in metadata["sprites"][:5]:  # Check first 5 sprites
                assert "id" in sprite
                assert "color" in sprite
                assert "animation" in sprite
                assert "frame" in sprite
                assert "x" in sprite
                assert "y" in sprite
                assert "width" in sprite
                assert "height" in sprite
                assert "is_primary" in sprite
                assert "is_secondary" in sprite
                
                # Check that coordinates are valid
                assert sprite["x"] >= 0
                assert sprite["y"] >= 0
                assert sprite["width"] > 0
                assert sprite["height"] > 0
    
    def test_sprite_sheet_color_distribution(self):
        """Test that colors are distributed correctly"""
        with tempfile.TemporaryDirectory() as temp_dir:
            from curioshelf.sprite_generator import generate_sprite_sheet
            import json
            
            generate_sprite_sheet(
                output_dir=temp_dir, 
                frames_per_animation=2, 
                sprite_width=32, 
                sprite_height=32
            )
            
            with open(Path(temp_dir) / "sprite_metadata.json", 'r') as f:
                metadata = json.load(f)
            
            # Count sprites per color
            color_counts = {}
            for sprite in metadata["sprites"]:
                color = sprite["color"]
                color_counts[color] = color_counts.get(color, 0) + 1
            
            # Each color should have the same number of sprites
            expected_per_color = len(metadata["animations"]) * metadata["frames_per_animation"]
            for color, count in color_counts.items():
                assert count == expected_per_color, f"Color {color} should have {expected_per_color} sprites, got {count}"
    
    def test_sprite_sheet_animation_distribution(self):
        """Test that animations are distributed correctly"""
        with tempfile.TemporaryDirectory() as temp_dir:
            from curioshelf.sprite_generator import generate_sprite_sheet
            import json
            
            generate_sprite_sheet(
                output_dir=temp_dir, 
                frames_per_animation=2, 
                sprite_width=32, 
                sprite_height=32
            )
            
            with open(Path(temp_dir) / "sprite_metadata.json", 'r') as f:
                metadata = json.load(f)
            
            # Count sprites per animation
            anim_counts = {}
            for sprite in metadata["sprites"]:
                anim = sprite["animation"]
                anim_counts[anim] = anim_counts.get(anim, 0) + 1
            
            # Each animation should have the same number of sprites
            expected_per_animation = len(metadata["colors"]) * metadata["frames_per_animation"]
            for anim, count in anim_counts.items():
                assert count == expected_per_animation, f"Animation {anim} should have {expected_per_animation} sprites, got {count}"
    
    def test_sprite_sheet_svg_structure(self):
        """Test that the generated SVG has correct structure"""
        with tempfile.TemporaryDirectory() as temp_dir:
            from curioshelf.sprite_generator import generate_sprite_sheet
            
            generate_sprite_sheet(
                output_dir=temp_dir, 
                frames_per_animation=2, 
                sprite_width=32, 
                sprite_height=32
            )
            
            # Check SVG file
            svg_file = Path(temp_dir) / "sprite_sheet.svg"
            with open(svg_file, 'r') as f:
                content = f.read()
            
            # Basic SVG validation
            assert content.startswith('<svg')
            assert content.endswith('</svg>')
            assert 'xmlns="http://www.w3.org/2000/svg"' in content
            
            # Should contain groups for each sprite
            assert '<g transform="translate(' in content
            
            # Should contain stick figure elements
            assert 'circle' in content  # Head
            assert 'line' in content    # Body parts
    
    def test_sprite_sheet_primary_secondary_colors(self):
        """Test that primary and secondary color flags are set correctly"""
        with tempfile.TemporaryDirectory() as temp_dir:
            from curioshelf.sprite_generator import generate_sprite_sheet
            import json
            
            generate_sprite_sheet(
                output_dir=temp_dir, 
                frames_per_animation=1, 
                sprite_width=32, 
                sprite_height=32
            )
            
            with open(Path(temp_dir) / "sprite_metadata.json", 'r') as f:
                metadata = json.load(f)
            
            # Check primary colors
            primary_colors = ['red', 'green', 'blue']
            for sprite in metadata["sprites"]:
                if sprite["color"] in primary_colors:
                    assert sprite["is_primary"] == True
                    assert sprite["is_secondary"] == False
                else:
                    assert sprite["is_primary"] == False
                    assert sprite["is_secondary"] == True
