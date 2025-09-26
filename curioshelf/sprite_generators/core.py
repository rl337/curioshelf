"""
Core sprite generator classes and interfaces.
"""

from abc import ABC, abstractmethod
from typing import List, Dict, Any, Tuple
from dataclasses import dataclass
from pathlib import Path
import json


@dataclass
class SpriteMetadata:
    """Metadata for a single sprite within a sprite sheet."""
    id: str
    plugin_name: str
    animation: str
    frame: int
    x: int
    y: int
    width: int
    height: int
    properties: Dict[str, Any]


@dataclass
class PluginSpriteData:
    """Data returned by a plugin for its sprites."""
    svg_content: str
    width: int
    height: int
    sprites: List[SpriteMetadata]
    plugin_name: str
    properties: Dict[str, Any]


class SpritePlugin(ABC):
    """Base class for sprite generation plugins."""
    
    def __init__(self, name: str):
        self.name = name
    
    @abstractmethod
    def generate_sprites(self, 
                        frames_per_animation: int = 10,
                        sprite_width: int = 64, 
                        sprite_height: int = 64,
                        **kwargs) -> PluginSpriteData:
        """
        Generate sprites for this plugin.
        
        Args:
            frames_per_animation: Number of frames per animation
            sprite_width: Width of each sprite
            sprite_height: Height of each sprite
            **kwargs: Additional plugin-specific parameters
            
        Returns:
            PluginSpriteData containing SVG content and sprite metadata
        """
        pass
    
    @abstractmethod
    def get_animation_types(self) -> List[str]:
        """Get list of animation types this plugin supports."""
        pass
    
    @abstractmethod
    def get_color_variations(self) -> List[str]:
        """Get list of color variations this plugin supports."""
        pass


class SpriteGenerator:
    """Main sprite generator that coordinates plugins and creates sprite sheets."""
    
    def __init__(self):
        self.plugins: List[SpritePlugin] = []
    
    def register_plugin(self, plugin: SpritePlugin) -> None:
        """Register a sprite generation plugin."""
        self.plugins.append(plugin)
    
    def generate_sprite_sheet(self, 
                             output_dir: str = "samples",
                             frames_per_animation: int = 10,
                             sprite_width: int = 64,
                             sprite_height: int = 64,
                             **kwargs) -> None:
        """
        Generate a comprehensive sprite sheet using all registered plugins.
        
        Args:
            output_dir: Directory to save the sprite sheet
            frames_per_animation: Number of frames per animation
            sprite_width: Width of each sprite
            sprite_height: Height of each sprite
            **kwargs: Additional parameters passed to plugins
        """
        if not self.plugins:
            raise ValueError("No plugins registered. Use register_plugin() to add plugins.")
        
        # Create output directory
        output_path = Path(output_dir)
        output_path.mkdir(exist_ok=True)
        
        # Generate sprites from all plugins
        plugin_data = []
        total_width = 0
        total_height = 0
        
        print(f"Generating sprite sheet with {len(self.plugins)} plugins...")
        
        for plugin in self.plugins:
            print(f"  Processing plugin: {plugin.name}")
            data = plugin.generate_sprites(
                frames_per_animation=frames_per_animation,
                sprite_width=sprite_width,
                sprite_height=sprite_height,
                **kwargs
            )
            plugin_data.append(data)
            
            # Calculate layout dimensions
            total_width = max(total_width, data.width)
            total_height += data.height
        
        print(f"Sprite sheet dimensions: {total_width}x{total_height} pixels")
        
        # Create the main sprite sheet SVG
        svg_content = self._create_sprite_sheet_svg(plugin_data, total_width, total_height)
        
        # Create comprehensive metadata
        metadata = self._create_sprite_sheet_metadata(
            plugin_data, total_width, total_height, 
            sprite_width, sprite_height, frames_per_animation
        )
        
        # Save files
        self._save_sprite_sheet(output_path, svg_content, metadata)
        
        print(f"Sprite sheet generated successfully!")
        print(f"Total sprites: {len(metadata['sprites'])}")
        print(f"File size: {(output_path / 'sprite_sheet.svg').stat().st_size / 1024:.1f} KB")
    
    def _create_sprite_sheet_svg(self, plugin_data: List[PluginSpriteData], 
                                total_width: int, total_height: int) -> str:
        """Create the main sprite sheet SVG by combining plugin SVGs."""
        svg_content = f'''<svg width="{total_width}" height="{total_height}" xmlns="http://www.w3.org/2000/svg">
<rect width="{total_width}" height="{total_height}" fill="white"/>
'''
        
        current_y = 0
        for data in plugin_data:
            # Add a group for this plugin's sprites
            svg_content += f'<g id="plugin_{data.plugin_name}" transform="translate(0, {current_y})">\n'
            
            # Add a box around the plugin's area
            svg_content += f'<rect x="0" y="0" width="{data.width}" height="{data.height}" fill="none" stroke="black" stroke-width="2" stroke-dasharray="5,5"/>\n'
            
            # Add a label for the plugin
            label_y = 20
            svg_content += f'<text x="10" y="{label_y}" font-family="Arial, sans-serif" font-size="16" font-weight="bold" fill="black">{data.plugin_name.replace("_", " ").title()}</text>\n'
            
            # Add the plugin's sprite content (offset down to make room for label)
            label_offset = 30
            svg_content += f'<g transform="translate(0, {label_offset})">\n'
            svg_content += data.svg_content
            svg_content += '</g>\n'
            
            svg_content += '</g>\n'
            current_y += data.height
        
        svg_content += '</svg>'
        return svg_content
    
    def _create_sprite_sheet_metadata(self, plugin_data: List[PluginSpriteData],
                                    total_width: int, total_height: int,
                                    sprite_width: int, sprite_height: int,
                                    frames_per_animation: int) -> Dict[str, Any]:
        """Create comprehensive metadata for the sprite sheet."""
        metadata = {
            "sprite_sheet": {
                "width": total_width,
                "height": total_height,
                "sprite_width": sprite_width,
                "sprite_height": sprite_height,
                "plugins": len(plugin_data)
            },
            "frames_per_animation": frames_per_animation,
            "plugins": [],
            "sprites": []
        }
        
        current_y = 0
        for data in plugin_data:
            # Add plugin info
            plugin_info = {
                "name": data.plugin_name,
                "width": data.width,
                "height": data.height,
                "y_offset": current_y,
                "sprite_count": len(data.sprites),
                "properties": data.properties
            }
            metadata["plugins"].append(plugin_info)
            
            # Add sprite info with adjusted coordinates
            for sprite in data.sprites:
                adjusted_sprite = {
                    "id": sprite.id,
                    "plugin_name": sprite.plugin_name,
                    "animation": sprite.animation,
                    "frame": sprite.frame,
                    "x": sprite.x,
                    "y": sprite.y + current_y,  # Adjust Y coordinate
                    "width": sprite.width,
                    "height": sprite.height,
                    "properties": sprite.properties
                }
                metadata["sprites"].append(adjusted_sprite)
            
            current_y += data.height
        
        return metadata
    
    def _save_sprite_sheet(self, output_path: Path, svg_content: str, metadata: Dict[str, Any]) -> None:
        """Save the sprite sheet and metadata files."""
        # Save SVG
        svg_path = output_path / "sprite_sheet.svg"
        with open(svg_path, 'w') as f:
            f.write(svg_content)
        
        # Save metadata
        metadata_path = output_path / "sprite_metadata.json"
        with open(metadata_path, 'w') as f:
            json.dump(metadata, f, indent=2)
        
        # Create README
        readme_path = output_path / "README.md"
        with open(readme_path, 'w') as f:
            f.write(self._generate_readme(metadata))
    
    def _generate_readme(self, metadata: Dict[str, Any]) -> str:
        """Generate a README file for the sprite sheet."""
        plugins_info = []
        for plugin in metadata["plugins"]:
            plugins_info.append(f"- **{plugin['name']}**: {plugin['sprite_count']} sprites ({plugin['width']}x{plugin['height']})")
        
        return f"""# Sprite Sheet

This directory contains a comprehensive sprite sheet generated by CurioShelf for testing purposes.

## Sprite Sheet Specifications

- **File**: sprite_sheet.svg
- **Size**: {metadata['sprite_sheet']['width']}x{metadata['sprite_sheet']['height']} pixels
- **Sprite Size**: {metadata['sprite_sheet']['sprite_width']}x{metadata['sprite_sheet']['sprite_height']} pixels each
- **Format**: SVG (Scalable Vector Graphics)

## Plugins Used

{chr(10).join(plugins_info)}

## Metadata

- **File**: sprite_metadata.json
- **Format**: JSON
- **Contains**: Sprite locations, plugin info, and properties

## Usage

This sprite sheet can be imported into CurioShelf projects for testing the asset management features. Each plugin's sprites are laid out vertically, with the metadata file providing exact coordinates for each sprite.

Generated by CurioShelf Sprite Generator
"""
