"""
Tests for the plugin-based sprite generator system.
"""

import pytest
import tempfile
import json
from pathlib import Path

from curioshelf.sprite_generators import SpriteGenerator, SpritePlugin, SpriteMetadata, PluginSpriteData
from curioshelf.sprite_generators.plugins.stick_figure import StickFigurePlugin


class TestSpriteGeneratorCore:
    """Test the core sprite generator functionality"""
    
    def test_sprite_generator_initialization(self):
        """Test that sprite generator initializes correctly"""
        generator = SpriteGenerator()
        assert generator.plugins == []
    
    def test_register_plugin(self):
        """Test plugin registration"""
        generator = SpriteGenerator()
        plugin = StickFigurePlugin()
        
        generator.register_plugin(plugin)
        assert len(generator.plugins) == 1
        assert generator.plugins[0] == plugin
    
    def test_generate_sprite_sheet_no_plugins(self):
        """Test that generating without plugins raises an error"""
        generator = SpriteGenerator()
        
        with pytest.raises(ValueError, match="No plugins registered"):
            generator.generate_sprite_sheet()
    
    def test_generate_sprite_sheet_with_plugin(self):
        """Test sprite sheet generation with a plugin"""
        with tempfile.TemporaryDirectory() as temp_dir:
            generator = SpriteGenerator()
            generator.register_plugin(StickFigurePlugin())
            
            generator.generate_sprite_sheet(
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
            generator = SpriteGenerator()
            generator.register_plugin(StickFigurePlugin())
            
            generator.generate_sprite_sheet(
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
            assert "frames_per_animation" in metadata
            assert "plugins" in metadata
            assert "sprites" in metadata
            
            # Check sprite sheet info
            sheet_info = metadata["sprite_sheet"]
            assert "width" in sheet_info
            assert "height" in sheet_info
            assert "sprite_width" in sheet_info
            assert "sprite_height" in sheet_info
            assert "plugins" in sheet_info
            
            # Check plugin info
            assert len(metadata["plugins"]) == 1
            plugin_info = metadata["plugins"][0]
            assert "name" in plugin_info
            assert "width" in plugin_info
            assert "height" in plugin_info
            assert "y_offset" in plugin_info
            assert "sprite_count" in plugin_info
            assert "properties" in plugin_info
    
    def test_sprite_coordinate_adjustment(self):
        """Test that sprite coordinates are properly adjusted for the final layout"""
        with tempfile.TemporaryDirectory() as temp_dir:
            generator = SpriteGenerator()
            generator.register_plugin(StickFigurePlugin())
            
            generator.generate_sprite_sheet(
                output_dir=temp_dir,
                frames_per_animation=2,
                sprite_width=32,
                sprite_height=32
            )
            
            with open(Path(temp_dir) / "sprite_metadata.json", 'r') as f:
                metadata = json.load(f)
            
            # Check that sprites have proper coordinates
            for sprite in metadata["sprites"]:
                assert "x" in sprite
                assert "y" in sprite
                assert "width" in sprite
                assert "height" in sprite
                assert sprite["x"] >= 0
                assert sprite["y"] >= 0
                assert sprite["width"] > 0
                assert sprite["height"] > 0


class TestStickFigurePlugin:
    """Test the stick figure plugin"""
    
    def test_plugin_initialization(self):
        """Test plugin initialization"""
        plugin = StickFigurePlugin()
        assert plugin.name == "stick_figure"
        assert len(plugin.get_animation_types()) == 4
        assert len(plugin.get_color_variations()) == 6
    
    def test_plugin_animation_types(self):
        """Test that plugin returns correct animation types"""
        plugin = StickFigurePlugin()
        animations = plugin.get_animation_types()
        
        expected_animations = ["walk", "stopping", "speeding_up", "jumping"]
        assert set(animations) == set(expected_animations)
    
    def test_plugin_color_variations(self):
        """Test that plugin returns correct color variations"""
        plugin = StickFigurePlugin()
        colors = plugin.get_color_variations()
        
        expected_colors = ["red", "green", "blue", "cyan", "magenta", "yellow"]
        assert set(colors) == set(expected_colors)
    
    def test_plugin_generate_sprites(self):
        """Test sprite generation from plugin"""
        plugin = StickFigurePlugin()
        
        data = plugin.generate_sprites(
            frames_per_animation=2,
            sprite_width=32,
            sprite_height=32
        )
        
        # Check return type
        assert isinstance(data, PluginSpriteData)
        assert data.plugin_name == "stick_figure"
        assert data.width > 0
        assert data.height > 0
        assert len(data.sprites) > 0
        
        # Check SVG content
        assert data.svg_content.startswith('<rect')
        assert 'transform="translate(' in data.svg_content
    
    def test_plugin_sprite_metadata(self):
        """Test that plugin generates correct sprite metadata"""
        plugin = StickFigurePlugin()
        
        data = plugin.generate_sprites(
            frames_per_animation=2,
            sprite_width=32,
            sprite_height=32
        )
        
        # Check sprite metadata
        for sprite in data.sprites:
            assert isinstance(sprite, SpriteMetadata)
            assert sprite.plugin_name == "stick_figure"
            assert sprite.animation in plugin.get_animation_types()
            assert sprite.properties["color"] in plugin.get_color_variations()
            assert "is_primary" in sprite.properties
            assert "is_secondary" in sprite.properties
            assert "color_hex" in sprite.properties
    
    def test_plugin_sprite_coordinates(self):
        """Test that plugin generates correct sprite coordinates"""
        plugin = StickFigurePlugin()
        
        data = plugin.generate_sprites(
            frames_per_animation=2,
            sprite_width=32,
            sprite_height=32
        )
        
        # Check that all sprites are within the plugin's bounds
        for sprite in data.sprites:
            assert 0 <= sprite.x < data.width
            assert 0 <= sprite.y < data.height
            assert sprite.width == 32
            assert sprite.height == 32
    
    def test_plugin_sprite_distribution(self):
        """Test that sprites are distributed correctly across colors and animations"""
        plugin = StickFigurePlugin()
        
        data = plugin.generate_sprites(
            frames_per_animation=2,
            sprite_width=32,
            sprite_height=32
        )
        
        # Count sprites by color and animation
        color_counts = {}
        anim_counts = {}
        
        for sprite in data.sprites:
            color = sprite.properties["color"]
            anim = sprite.animation
            
            color_counts[color] = color_counts.get(color, 0) + 1
            anim_counts[anim] = anim_counts.get(anim, 0) + 1
        
        # Each color should have the same number of sprites
        expected_per_color = len(plugin.get_animation_types()) * 2  # 2 frames per animation
        for color, count in color_counts.items():
            assert count == expected_per_color, f"Color {color} should have {expected_per_color} sprites, got {count}"
        
        # Each animation should have the same number of sprites
        expected_per_animation = len(plugin.get_color_variations()) * 2  # 2 frames per animation
        for anim, count in anim_counts.items():
            assert count == expected_per_animation, f"Animation {anim} should have {expected_per_animation} sprites, got {count}"


class TestSpriteGeneratorIntegration:
    """Test integration between core generator and plugins"""
    
    def test_multiple_plugins_layout(self):
        """Test that multiple plugins are laid out correctly"""
        # Create a simple test plugin
        class TestPlugin(SpritePlugin):
            def __init__(self, name, height):
                super().__init__(name)
                self.height = height
            
            def generate_sprites(self, **kwargs):
                return PluginSpriteData(
                    svg_content=f'<rect width="100" height="{self.height}" fill="red"/>',
                    width=100,
                    height=self.height,
                    sprites=[
                        SpriteMetadata(
                            id=f"{self.name}_sprite",
                            plugin_name=self.name,
                            animation="test",
                            frame=0,
                            x=0, y=0,
                            width=100, height=self.height,
                            properties={}
                        )
                    ],
                    plugin_name=self.name,
                    properties={}
                )
            
            def get_animation_types(self):
                return ["test"]
            
            def get_color_variations(self):
                return ["red"]
        
        with tempfile.TemporaryDirectory() as temp_dir:
            generator = SpriteGenerator()
            generator.register_plugin(TestPlugin("plugin1", 50))
            generator.register_plugin(TestPlugin("plugin2", 75))
            
            generator.generate_sprite_sheet(output_dir=temp_dir)
            
            with open(Path(temp_dir) / "sprite_metadata.json", 'r') as f:
                metadata = json.load(f)
            
            # Check that we have 2 plugins
            assert len(metadata["plugins"]) == 2
            
            # Check that sprites are properly positioned
            plugin1_sprites = [s for s in metadata["sprites"] if s["plugin_name"] == "plugin1"]
            plugin2_sprites = [s for s in metadata["sprites"] if s["plugin_name"] == "plugin2"]
            
            assert len(plugin1_sprites) == 1
            assert len(plugin2_sprites) == 1
            
            # Plugin2 sprites should be below plugin1 sprites
            assert plugin2_sprites[0]["y"] > plugin1_sprites[0]["y"]
    
    def test_sprite_rectangle_validation(self):
        """Test that sprite rectangles are computed correctly and match generated sprites"""
        with tempfile.TemporaryDirectory() as temp_dir:
            generator = SpriteGenerator()
            generator.register_plugin(StickFigurePlugin())
            
            generator.generate_sprite_sheet(
                output_dir=temp_dir,
                frames_per_animation=2,
                sprite_width=32,
                sprite_height=32
            )
            
            with open(Path(temp_dir) / "sprite_metadata.json", 'r') as f:
                metadata = json.load(f)
            
            # Check that all sprites are within the sprite sheet bounds
            sheet_width = metadata["sprite_sheet"]["width"]
            sheet_height = metadata["sprite_sheet"]["height"]
            
            for sprite in metadata["sprites"]:
                # Check that sprite is within bounds
                assert 0 <= sprite["x"] < sheet_width
                assert 0 <= sprite["y"] < sheet_height
                assert sprite["x"] + sprite["width"] <= sheet_width
                assert sprite["y"] + sprite["height"] <= sheet_height
                
                # Check that sprite has valid dimensions
                assert sprite["width"] > 0
                assert sprite["height"] > 0
    
    def test_no_sprite_overlaps(self):
        """Test that sprites don't overlap in the final layout"""
        with tempfile.TemporaryDirectory() as temp_dir:
            generator = SpriteGenerator()
            generator.register_plugin(StickFigurePlugin())
            
            generator.generate_sprite_sheet(
                output_dir=temp_dir,
                frames_per_animation=2,
                sprite_width=32,
                sprite_height=32
            )
            
            with open(Path(temp_dir) / "sprite_metadata.json", 'r') as f:
                metadata = json.load(f)
            
            # Check for overlaps
            sprites = metadata["sprites"]
            for i, sprite1 in enumerate(sprites):
                for j, sprite2 in enumerate(sprites[i+1:], i+1):
                    # Check if rectangles overlap
                    x1, y1, w1, h1 = sprite1["x"], sprite1["y"], sprite1["width"], sprite1["height"]
                    x2, y2, w2, h2 = sprite2["x"], sprite2["y"], sprite2["width"], sprite2["height"]
                    
                    # Rectangles don't overlap if one is completely to the left, right, above, or below the other
                    no_overlap = (x1 + w1 <= x2 or x2 + w2 <= x1 or 
                                y1 + h1 <= y2 or y2 + h2 <= y1)
                    
                    assert no_overlap, f"Sprites {sprite1['id']} and {sprite2['id']} overlap"
