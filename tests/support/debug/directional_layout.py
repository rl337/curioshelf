"""
Headless implementation of DirectionalLayout that matches Qt behavior exactly
"""

from typing import Optional, Dict, Any, List
from enum import Enum
from curioshelf.ui.abstraction import UIWidget, UILayout
from .message_system import MessageLogger


class Direction(Enum):
    """Layout directions"""
    NORTH = "north"
    SOUTH = "south"
    EAST = "east"
    WEST = "west"
    CENTER = "center"


class DebugDirectionalLayout(UILayout):
    """Headless directional layout that matches Qt behavior exactly"""
    
    def __init__(self, parent_widget: Optional[UIWidget] = None, 
                 message_logger: Optional[MessageLogger] = None):
        super().__init__()
        self.parent_widget = parent_widget
        self.message_logger = message_logger or MessageLogger(collect_messages=True, print_messages=True)
        self.widgets: Dict[Direction, List[UIWidget]] = {
            Direction.NORTH: [],
            Direction.SOUTH: [],
            Direction.EAST: [],
            Direction.WEST: [],
            Direction.CENTER: []
        }
        self._layout_created = False
        
        # Log layout creation
        self.message_logger.log_ui_event("DebugDirectionalLayout", "layout_created", {
            "parent_widget": id(parent_widget) if parent_widget else None
        })
    
    def add_widget(self, widget: UIWidget, direction: Direction = Direction.CENTER, 
                   expand: bool = False, fill: bool = True, **kwargs) -> None:
        """Add a widget to the layout in a specific direction"""
        if direction not in self.widgets:
            direction = Direction.CENTER
            
        self.widgets[direction].append(widget)
        
        # Store layout properties for the widget
        widget._layout_direction = direction
        widget._layout_expand = expand
        widget._layout_fill = fill
        widget._layout_kwargs = kwargs
        
        # Log widget addition
        self.message_logger.log_ui_event("DebugDirectionalLayout", "widget_added", {
            "widget_type": widget.__class__.__name__,
            "direction": direction.value,
            "expand": expand,
            "fill": fill,
            "widget_id": id(widget)
        })
    
    def set_parent_widget(self, parent_widget: UIWidget) -> None:
        """Set the parent widget for this layout"""
        self.parent_widget = parent_widget
        self._layout_created = True
        
        # Log parent widget setting
        self.message_logger.log_ui_event("DebugDirectionalLayout", "parent_widget_set", {
            "parent_widget_id": id(parent_widget),
            "parent_widget_type": parent_widget.__class__.__name__
        })
    
    def _ensure_layout_created(self) -> None:
        """Ensure the layout is created if we have a parent widget"""
        if self.parent_widget and not self._layout_created:
            self.set_parent_widget(self.parent_widget)
    
    def remove_widget(self, widget: UIWidget) -> None:
        """Remove a widget from the layout"""
        for direction, widgets in self.widgets.items():
            if widget in widgets:
                widgets.remove(widget)
                self.message_logger.log_ui_event("DebugDirectionalLayout", "widget_removed", {
                    "widget_type": widget.__class__.__name__,
                    "direction": direction.value,
                    "widget_id": id(widget)
                })
                break
    
    def insert_widget(self, index: int, widget: UIWidget, *args: Any, **kwargs: Any) -> None:
        """Insert a widget at a specific index in the layout"""
        # For directional layout, we'll add to center by default
        direction = kwargs.get('direction', Direction.CENTER)
        expand = kwargs.get('expand', False)
        fill = kwargs.get('fill', True)
        
        # Remove direction from kwargs to avoid passing it to add_widget
        if 'direction' in kwargs:
            del kwargs['direction']
        if 'expand' in kwargs:
            del kwargs['expand']
        if 'fill' in kwargs:
            del kwargs['fill']
        
        if direction not in self.widgets:
            direction = Direction.CENTER
            
        # Insert at the specified index
        self.widgets[direction].insert(index, widget)
        
        # Store layout properties for the widget
        widget._layout_direction = direction
        widget._layout_expand = expand
        widget._layout_fill = fill
        widget._layout_kwargs = kwargs
        
        # Log widget insertion
        self.message_logger.log_ui_event("DebugDirectionalLayout", "widget_inserted", {
            "widget_type": widget.__class__.__name__,
            "direction": direction.value,
            "index": index,
            "expand": expand,
            "fill": fill,
            "widget_id": id(widget)
        })
    
    def clear(self) -> None:
        """Clear all widgets from the layout"""
        for direction, widgets in self.widgets.items():
            for widget in widgets:
                self.message_logger.log_ui_event("DebugDirectionalLayout", "widget_removed", {
                    "widget_type": widget.__class__.__name__,
                    "direction": direction.value,
                    "widget_id": id(widget)
                })
            widgets.clear()
        
        self.message_logger.log_ui_event("DebugDirectionalLayout", "layout_cleared", {})
    
    def get_widgets(self, direction: Direction) -> List[UIWidget]:
        """Get all widgets in a specific direction"""
        return self.widgets.get(direction, [])
    
    def has_widgets(self, direction: Direction) -> bool:
        """Check if there are widgets in a specific direction"""
        return len(self.widgets.get(direction, [])) > 0
    
    def get_all_widgets(self) -> List[UIWidget]:
        """Get all widgets in all directions"""
        all_widgets = []
        for widgets in self.widgets.values():
            all_widgets.extend(widgets)
        return all_widgets
    
    def get_widget_count(self) -> int:
        """Get total number of widgets in the layout"""
        return sum(len(widgets) for widgets in self.widgets.values())
    
    def get_direction_widget_count(self, direction: Direction) -> int:
        """Get number of widgets in a specific direction"""
        return len(self.widgets.get(direction, []))
