"""
Stick figure sprite generation plugin.
"""

import math
from typing import List, Dict, Any
from ..core import SpritePlugin, PluginSpriteData, SpriteMetadata


class StickFigureSprite:
    """Generates SVG sprites of a classic stick figure with various animations"""
    
    # Web-safe color mapping
    WEB_SAFE_COLORS = {
        'black': '#000000',
        'white': '#FFFFFF',
        'red': '#FF0000',
        'green': '#00FF00',
        'blue': '#0000FF',
        'cyan': '#00FFFF',
        'magenta': '#FF00FF',
        'yellow': '#FFFF00',
        'orange': '#FFA500',
        'purple': '#800080',
        'pink': '#FFC0CB',
        'brown': '#A52A2A',
        'gray': '#808080',
        'grey': '#808080',
        'lime': '#00FF00',
        'navy': '#000080',
        'olive': '#808000',
        'teal': '#008080',
        'maroon': '#800000',
        'silver': '#C0C0C0',
        'aqua': '#00FFFF',
        'fuchsia': '#FF00FF',
        'lime': '#00FF00',
        'darkred': '#8B0000',
        'darkgreen': '#006400',
        'darkblue': '#00008B',
        'darkcyan': '#008B8B',
        'darkmagenta': '#8B008B',
        'darkyellow': '#B8860B',
        'darkorange': '#FF8C00',
        'darkpurple': '#800080',
        'darkpink': '#FF1493',
        'darkbrown': '#8B4513',
        'darkgray': '#A9A9A9',
        'darkgrey': '#A9A9A9',
        'lightred': '#FFA0A0',
        'lightgreen': '#90EE90',
        'lightblue': '#ADD8E6',
        'lightcyan': '#E0FFFF',
        'lightmagenta': '#FFB6C1',
        'lightyellow': '#FFFFE0',
        'lightorange': '#FFE4B5',
        'lightpurple': '#DDA0DD',
        'lightpink': '#FFB6C1',
        'lightbrown': '#D2B48C',
        'lightgray': '#D3D3D3',
        'lightgrey': '#D3D3D3'
    }
    
    def __init__(self, width: int = 64, height: int = 64, color: str = "black"):
        self.width = width
        self.height = height
        self.center_x = width // 2
        self.center_y = height // 2
        
        # Stick figure proportions (relative to sprite size)
        self.head_radius = min(width, height) * 0.12
        self.torso_length = min(width, height) * 0.3
        self.arm_length = min(width, height) * 0.25
        self.leg_length = min(width, height) * 0.35
        
        # Animation parameters
        self.stroke_width = max(1, min(width, height) // 32)
        self.stroke_color = self._get_color_hex(color)
    
    def _get_color_hex(self, color_name: str) -> str:
        """Convert color name to hex value, with fallback to black"""
        color_lower = color_name.lower().strip()
        if color_lower in self.WEB_SAFE_COLORS:
            return self.WEB_SAFE_COLORS[color_lower]
        elif color_name.startswith('#'):
            # Already a hex color
            return color_name
        else:
            # Unknown color, fallback to black
            print(f"Warning: Unknown color '{color_name}', using black")
            return "#000000"
    
    def generate_walk_cycle(self, frame_count: int = 10) -> List[str]:
        """Generate a walk cycle animation"""
        frames = []
        
        for i in range(frame_count):
            # Calculate animation progress (0.0 to 1.0), but don't include the end point to avoid identical first/last frames
            progress = i / frame_count
            
            # Head bobbing (subtle vertical movement)
            head_bob = math.sin(progress * 2 * math.pi) * 2
            
            # Arm swing (opposite to leg movement)
            arm_swing = math.sin(progress * 2 * math.pi) * 45
            
            # Leg movement (more pronounced)
            leg_swing = math.sin(progress * 2 * math.pi) * 30
            
            # Generate the frame
            frame = self._draw_stick_figure_svg(
                head_y=self.center_y - self.torso_length - self.head_radius + head_bob,
                body_y_offset=0,
                left_arm_angle=arm_swing,
                right_arm_angle=-arm_swing,
                left_thigh_angle=90 + leg_swing,  # Start from vertical (90 degrees)
                left_shin_angle=leg_swing * 0.7,
                right_thigh_angle=90 - leg_swing,  # Start from vertical (90 degrees)
                right_shin_angle=-leg_swing * 0.7
            )
            frames.append(frame)
        
        return frames
    
    def generate_stopping_cycle(self, frame_count: int = 10) -> List[str]:
        """Generate a coming to stop animation"""
        frames = []
        
        for i in range(frame_count):
            # Calculate animation progress (0.0 to 1.0), but don't include the end point to avoid identical first/last frames
            progress = i / frame_count
            
            # Gradually reduce movement
            movement_factor = 1.0 - progress
            
            # Head lean forward (increasing)
            head_lean = progress * 15
            
            # Arm movement (decreasing)
            arm_swing = math.sin(progress * 4 * math.pi) * 20 * movement_factor
            
            # Leg movement (decreasing)
            leg_swing = math.sin(progress * 4 * math.pi) * 15 * movement_factor
            
            # Generate the frame
            frame = self._draw_stick_figure_svg(
                head_y=self.center_y - self.torso_length - self.head_radius - head_lean,
                body_y_offset=0,
                left_arm_angle=arm_swing,
                right_arm_angle=-arm_swing,
                left_thigh_angle=90 + leg_swing,
                left_shin_angle=leg_swing * 0.5,
                right_thigh_angle=90 - leg_swing,
                right_shin_angle=-leg_swing * 0.5
            )
            frames.append(frame)
        
        return frames
    
    def generate_speeding_up_cycle(self, frame_count: int = 10) -> List[str]:
        """Generate a speeding up animation"""
        frames = []
        
        for i in range(frame_count):
            # Calculate animation progress (0.0 to 1.0), but don't include the end point to avoid identical first/last frames
            progress = i / frame_count
            
            # Increasing movement intensity
            movement_factor = progress * 1.5
            
            # Head lean back (increasing)
            head_lean = progress * 10
            
            # Arm movement (increasing)
            arm_swing = math.sin(progress * 6 * math.pi) * 25 * movement_factor
            
            # Leg movement (increasing)
            leg_swing = math.sin(progress * 6 * math.pi) * 30 * movement_factor
            
            # Generate the frame
            frame = self._draw_stick_figure_svg(
                head_y=self.center_y - self.torso_length - self.head_radius + head_lean,
                body_y_offset=0,
                left_arm_angle=arm_swing,
                right_arm_angle=-arm_swing,
                left_thigh_angle=90 + leg_swing,
                left_shin_angle=leg_swing * 0.8,
                right_thigh_angle=90 - leg_swing,
                right_shin_angle=-leg_swing * 0.8
            )
            frames.append(frame)
        
        return frames
    
    def generate_jumping_cycle(self, frame_count: int = 10) -> List[str]:
        """Generate a jumping animation"""
        frames = []
        
        for i in range(frame_count):
            # Calculate animation progress (0.0 to 1.0), but don't include the end point to avoid identical first/last frames
            progress = i / frame_count
            
            # Jump height (parabolic)
            jump_height = math.sin(progress * math.pi) * 20
            
            # Arm position (up during jump)
            arm_angle = 45 if progress < 0.3 or progress > 0.7 else -20
            
            # Leg position (bent during takeoff and landing)
            leg_angle = 0
            if progress < 0.2:  # Takeoff
                leg_angle = -30 * (0.2 - progress) / 0.2
            elif progress > 0.8:  # Landing
                leg_angle = -30 * (progress - 0.8) / 0.2
            
            # Generate the frame
            frame = self._draw_stick_figure_svg(
                head_y=self.center_y - self.torso_length - self.head_radius - jump_height,
                body_y_offset=0,
                left_arm_angle=arm_angle,
                right_arm_angle=arm_angle,
                left_thigh_angle=90 + leg_angle,
                left_shin_angle=leg_angle * 0.5,
                right_thigh_angle=90 + leg_angle,
                right_shin_angle=leg_angle * 0.5
            )
            frames.append(frame)
        
        return frames
    
    def _draw_stick_figure(self, head_y: float, body_y_offset: float,
                          left_arm_angle: float, right_arm_angle: float,
                          left_thigh_angle: float, left_shin_angle: float,
                          right_thigh_angle: float, right_shin_angle: float,
                          stroke_width: int = None) -> str:
        """Draw a stick figure with the given parameters"""
        if stroke_width is None:
            stroke_width = self.stroke_width
        
        # Head
        head = f'<circle cx="{self.center_x:.1f}" cy="{head_y:.1f}" r="{self.head_radius:.1f}" fill="none" stroke="{self.stroke_color}" stroke-width="{stroke_width}"/>\n'
        
        # Body
        body_y = head_y + self.head_radius + self.torso_length + body_y_offset
        body = f'<line x1="{self.center_x:.1f}" y1="{head_y + self.head_radius:.1f}" x2="{self.center_x:.1f}" y2="{body_y:.1f}" stroke="{self.stroke_color}" stroke-width="{stroke_width}"/>\n'
        
        # Arms
        arms = self._draw_arms(body_y, left_arm_angle, right_arm_angle, stroke_width)
        
        # Legs
        legs = self._draw_legs(body_y, left_thigh_angle, left_shin_angle, right_thigh_angle, right_shin_angle, stroke_width)
        
        return head + body + arms + legs
    
    def _draw_stick_figure_svg(self, head_y: float, body_y_offset: float,
                              left_arm_angle: float, right_arm_angle: float,
                              left_thigh_angle: float, left_shin_angle: float,
                              right_thigh_angle: float, right_shin_angle: float,
                              stroke_width: int = None) -> str:
        """Draw a complete SVG stick figure with the given parameters"""
        content = self._draw_stick_figure(head_y, body_y_offset, left_arm_angle, right_arm_angle,
                                        left_thigh_angle, left_shin_angle, right_thigh_angle, right_shin_angle, stroke_width)
        
        # Add background rectangle
        background = f'<rect width="{self.width}" height="{self.height}" fill="transparent"/>\n'
        
        return f'<svg width="{self.width}" height="{self.height}" xmlns="http://www.w3.org/2000/svg">\n{background}{content}</svg>'
    
    def _draw_arms(self, body_y: float, left_arm_angle: float, right_arm_angle: float, stroke_width: int) -> str:
        """Draw the arms of the stick figure"""
        # Convert angles to radians
        left_rad = math.radians(left_arm_angle)
        right_rad = math.radians(right_arm_angle)
        
        # Calculate arm endpoints
        left_arm_x = self.center_x + math.cos(left_rad) * self.arm_length
        left_arm_y = body_y + math.sin(left_rad) * self.arm_length
        
        right_arm_x = self.center_x + math.cos(right_rad) * self.arm_length
        right_arm_y = body_y + math.sin(right_rad) * self.arm_length
        
        left_arm = f'<line x1="{self.center_x:.1f}" y1="{body_y:.1f}" x2="{left_arm_x:.1f}" y2="{left_arm_y:.1f}" stroke="{self.stroke_color}" stroke-width="{stroke_width}"/>\n'
        right_arm = f'<line x1="{self.center_x:.1f}" y1="{body_y:.1f}" x2="{right_arm_x:.1f}" y2="{right_arm_y:.1f}" stroke="{self.stroke_color}" stroke-width="{stroke_width}"/>\n'
        
        return left_arm + right_arm
    
    def _draw_legs(self, body_y: float, left_thigh_angle: float, left_shin_angle: float,
                   right_thigh_angle: float, right_shin_angle: float, stroke_width: int) -> str:
        """Draw the legs of the stick figure"""
        # Convert angles to radians
        left_thigh_rad = math.radians(left_thigh_angle)
        left_shin_rad = math.radians(left_shin_angle)
        right_thigh_rad = math.radians(right_thigh_angle)
        right_shin_rad = math.radians(right_shin_angle)
        
        # Calculate thigh endpoints (thighs go down from body bottom)
        left_thigh_x = self.center_x + math.cos(left_thigh_rad) * self.leg_length
        left_thigh_y = body_y + math.sin(left_thigh_rad) * self.leg_length
        
        right_thigh_x = self.center_x + math.cos(right_thigh_rad) * self.leg_length
        right_thigh_y = body_y + math.sin(right_thigh_rad) * self.leg_length
        
        # Calculate shin endpoints (shins go from thigh end)
        left_shin_x = left_thigh_x + math.cos(left_shin_rad) * self.leg_length * 0.8
        left_shin_y = left_thigh_y + math.sin(left_shin_rad) * self.leg_length * 0.8
        
        right_shin_x = right_thigh_x + math.cos(right_shin_rad) * self.leg_length * 0.8
        right_shin_y = right_thigh_y + math.sin(right_shin_rad) * self.leg_length * 0.8
        
        # Draw thigh segments (from body bottom to thigh end)
        left_thigh = f'<line x1="{self.center_x:.1f}" y1="{body_y:.1f}" x2="{left_thigh_x:.1f}" y2="{left_thigh_y:.1f}" stroke="{self.stroke_color}" stroke-width="{stroke_width}"/>\n'
        right_thigh = f'<line x1="{self.center_x:.1f}" y1="{body_y:.1f}" x2="{right_thigh_x:.1f}" y2="{right_thigh_y:.1f}" stroke="{self.stroke_color}" stroke-width="{stroke_width}"/>\n'
        
        # Draw shin segments (from thigh end to shin end)
        left_shin = f'<line x1="{left_thigh_x:.1f}" y1="{left_thigh_y:.1f}" x2="{left_shin_x:.1f}" y2="{left_shin_y:.1f}" stroke="{self.stroke_color}" stroke-width="{stroke_width}"/>\n'
        right_shin = f'<line x1="{right_thigh_x:.1f}" y1="{right_thigh_y:.1f}" x2="{right_shin_x:.1f}" y2="{right_shin_y:.1f}" stroke="{self.stroke_color}" stroke-width="{stroke_width}"/>\n'
        
        return left_thigh + right_thigh + left_shin + right_shin


class StickFigurePlugin(SpritePlugin):
    """Plugin for generating stick figure sprites with various animations and colors."""
    
    def __init__(self):
        super().__init__("stick_figure")
        self.primary_colors = ['red', 'green', 'blue']
        self.secondary_colors = ['cyan', 'magenta', 'yellow']
        self.animations = {
            "walk": "Walk Cycle",
            "stopping": "Coming to Stop", 
            "speeding_up": "Speeding Up",
            "jumping": "Jumping"
        }
    
    def get_animation_types(self) -> List[str]:
        """Get list of animation types this plugin supports."""
        return list(self.animations.keys())
    
    def get_color_variations(self) -> List[str]:
        """Get list of color variations this plugin supports."""
        return self.primary_colors + self.secondary_colors
    
    def generate_sprites(self, 
                        frames_per_animation: int = 10,
                        sprite_width: int = 64, 
                        sprite_height: int = 64,
                        **kwargs) -> PluginSpriteData:
        """Generate stick figure sprites with all color and animation combinations."""
        
        all_colors = self.primary_colors + self.secondary_colors
        
        # Calculate layout dimensions - new rectangular layout with proper margins
        # Each color gets its own section with 2 animations per row
        animations_per_row = 2
        rows_per_color = (len(self.animations) + animations_per_row - 1) // animations_per_row  # Ceiling division
        # Use the provided frames_per_animation parameter
        
        # Calculate margins and spacing
        label_height = 30  # Space for animation labels (increased)
        margin_bottom = 20  # Space between color sections (increased)
        margin_right = 20   # Space between animations in a row (increased)
        padding_top = 10    # Space above stick figures
        padding_bottom = 10 # Space below stick figures
        
        # Calculate dimensions for each animation type
        # Stick figures need extra space because they extend beyond their base sprite area
        animation_heights = {
            "walk": sprite_height + label_height + padding_top + padding_bottom,
            "stopping": sprite_height + label_height + padding_top + padding_bottom,
            "speeding_up": sprite_height + label_height + padding_top + padding_bottom,
            "jumping": int(sprite_height * 1.5) + label_height + padding_top + padding_bottom  # Jumping needs more height
        }
        
        # Calculate the maximum height needed for any animation
        max_animation_height = max(animation_heights.values())
        
        plugin_width = animations_per_row * frames_per_animation * sprite_width + (animations_per_row - 1) * margin_right
        plugin_height = len(all_colors) * rows_per_color * max_animation_height + (len(all_colors) - 1) * margin_bottom + 30  # Add space for main label
        
        print(f"    Generating {plugin_width}x{plugin_height} sprite grid")
        print(f"    Colors: {all_colors}")
        print(f"    Animations: {list(self.animations.keys())}")
        print(f"    Frames per animation: {frames_per_animation}")
        
        # Start building the plugin's SVG
        svg_content = f'''<rect width="{plugin_width}" height="{plugin_height}" fill="transparent"/>
'''
        
        sprites = []
        
        # Generate sprites for each color and animation combination
        for color_idx, color in enumerate(all_colors):
            # Calculate the base Y position for this color (with proper spacing)
            color_base_y = color_idx * (rows_per_color * max_animation_height + margin_bottom) + 30
            
            # Group animations into rows of 2
            animation_list = list(self.animations.items())
            for row_idx in range(rows_per_color):
                row_base_y = color_base_y + row_idx * max_animation_height
                
                # Get the animations for this row (up to 2)
                start_anim = row_idx * animations_per_row
                end_anim = min(start_anim + animations_per_row, len(animation_list))
                row_animations = animation_list[start_anim:end_anim]
                
                for anim_col_idx, (anim_name, anim_desc) in enumerate(row_animations):
                    # Create sprite generator for this color
                    generator = StickFigureSprite(sprite_width, sprite_height, color)
                    
                    # Generate frames based on animation type
                    if anim_name == "walk":
                        frames = generator.generate_walk_cycle(frames_per_animation)
                    elif anim_name == "stopping":
                        frames = generator.generate_stopping_cycle(frames_per_animation)
                    elif anim_name == "speeding_up":
                        frames = generator.generate_speeding_up_cycle(frames_per_animation)
                    elif anim_name == "jumping":
                        frames = generator.generate_jumping_cycle(frames_per_animation)
                    else:
                        continue
                    
                    # Calculate the base X position for this animation (with proper spacing)
                    anim_base_x = anim_col_idx * (frames_per_animation * sprite_width + margin_right)
                    
                    # Get the height for this specific animation
                    anim_height = animation_heights[anim_name]
                    
                    # Add a box around this animation
                    box_width = frames_per_animation * sprite_width
                    box_height = anim_height
                    svg_content += f'<rect x="{anim_base_x}" y="{row_base_y}" width="{box_width}" height="{box_height}" fill="none" stroke="black" stroke-width="1" stroke-dasharray="3,3"/>\n'
                    
                    # Add animation label (positioned well above the animation)
                    label_x = anim_base_x + 5
                    label_y = row_base_y + 20  # Positioned well above the content
                    svg_content += f'<text x="{label_x}" y="{label_y}" font-family="Arial, sans-serif" font-size="12" font-weight="bold" fill="black">{anim_desc}</text>\n'
                    
                    # Add each frame to the plugin's SVG
                    for frame_idx, frame in enumerate(frames):
                        # Calculate position in the animation row (below the label with padding)
                        x = anim_base_x + frame_idx * sprite_width
                        y = row_base_y + label_height + padding_top  # Start below the label with padding
                        
                        # Extract the content from the frame (remove the outer SVG tags)
                        svg_start = frame.find('>') + 1
                        svg_end = frame.rfind('</svg>')
                        frame_content = frame[svg_start:svg_end].strip()
                        
                        # Add a group with transform for this sprite
                        svg_content += f'<g transform="translate({x}, {y})">\n'
                        svg_content += frame_content
                        svg_content += '</g>\n'
                        
                        # Add metadata for this sprite
                        sprite_info = SpriteMetadata(
                            id=f"{color}_{anim_name}_{frame_idx:03d}",
                            plugin_name=self.name,
                            animation=anim_name,
                            frame=frame_idx,
                            x=x,
                            y=y,
                            width=sprite_width,
                            height=sprite_height,
                            properties={
                                "color": color,
                                "color_hex": generator.stroke_color,
                                "is_primary": color in self.primary_colors,
                                "is_secondary": color in self.secondary_colors,
                                "animation_description": self.animations[anim_name]
                            }
                        )
                        sprites.append(sprite_info)
        
        return PluginSpriteData(
            svg_content=svg_content,
            width=plugin_width,
            height=plugin_height,
            sprites=sprites,
            plugin_name=self.name,
            properties={
                "total_colors": len(all_colors),
                "total_animations": len(self.animations),
                "primary_colors": self.primary_colors,
                "secondary_colors": self.secondary_colors,
                "animation_descriptions": self.animations
            }
        )
