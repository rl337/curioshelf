"""
Directional layout system for UI widgets
Similar to Tkinter's pack geometry manager with north, south, east, west, center positions
"""

from typing import Optional, Dict, Any, List
from enum import Enum
from curioshelf.ui.abstraction import UIWidget, UILayout


class Direction(Enum):
    """Layout directions"""
    NORTH = "north"
    SOUTH = "south"
    EAST = "east"
    WEST = "west"
    CENTER = "center"


class DirectionalLayout(UILayout):
    """Directional layout that places widgets in specific directions"""
    
    def __init__(self, parent_widget: Optional[UIWidget] = None):
        super().__init__()
        self.parent_widget = parent_widget
        self.widgets: Dict[Direction, List[UIWidget]] = {
            Direction.NORTH: [],
            Direction.SOUTH: [],
            Direction.EAST: [],
            Direction.WEST: [],
            Direction.CENTER: []
        }
        self._qt_layout = None
        self._qt_widget = None
        
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
        
        # Ensure Qt layout is created
        self._ensure_qt_layout()
        
        # If we have a Qt layout, add the widget immediately
        if self._qt_layout and hasattr(widget, 'qt_widget'):
            self._add_widget_to_qt_layout(widget, direction, expand, fill, **kwargs)
    
    def _add_widget_to_qt_layout(self, widget: UIWidget, direction: Direction, 
                                expand: bool, fill: bool, **kwargs) -> None:
        """Add widget to the actual Qt layout"""
        if not hasattr(widget, 'qt_widget'):
            return
            
        qt_widget = widget.qt_widget
        
        # Set parent if we have one
        if self.parent_widget and hasattr(self.parent_widget, 'qt_widget'):
            qt_widget.setParent(self.parent_widget.qt_widget)
        
        # Add to the appropriate section of the layout
        if direction == Direction.NORTH:
            self._qt_layout.addWidget(qt_widget, 0, 1)  # Top row, middle column
        elif direction == Direction.SOUTH:
            self._qt_layout.addWidget(qt_widget, 2, 1)  # Bottom row, middle column
        elif direction == Direction.EAST:
            self._qt_layout.addWidget(qt_widget, 1, 2)  # Middle row, right column
        elif direction == Direction.WEST:
            self._qt_layout.addWidget(qt_widget, 1, 0)  # Middle row, left column
        elif direction == Direction.CENTER:
            self._qt_layout.addWidget(qt_widget, 1, 1)  # Center
    
    def set_parent_widget(self, parent_widget: UIWidget) -> None:
        """Set the parent widget for this layout"""
        self.parent_widget = parent_widget
        self._qt_widget = parent_widget.qt_widget if hasattr(parent_widget, 'qt_widget') else None
        
        # Create Qt layout if we have a parent
        if self._qt_widget:
            self._create_qt_layout()
            # Re-add all existing widgets
            self._re_add_all_widgets()
    
    def _ensure_qt_layout(self) -> None:
        """Ensure the Qt layout is created if we have a parent widget"""
        if self.parent_widget and hasattr(self.parent_widget, 'qt_widget') and not self._qt_layout:
            self._qt_widget = self.parent_widget.qt_widget
            self._create_qt_layout()
            self._re_add_all_widgets()
    
    def _create_qt_layout(self) -> None:
        """Create the Qt grid layout"""
        if not self._qt_widget:
            return
            
        from PySide6.QtWidgets import QGridLayout
        self._qt_layout = QGridLayout(self._qt_widget)
        
        # Set up the grid with 3x3 cells
        # [0,0] [0,1] [0,2]  <- North spans [0,1]
        # [1,0] [1,1] [1,2]  <- West [1,0], Center [1,1], East [1,2]
        # [2,0] [2,1] [2,2]  <- South spans [2,1]
        
        # Set column and row stretch
        self._qt_layout.setColumnStretch(0, 0)  # West column
        self._qt_layout.setColumnStretch(1, 1)  # Center column (expandable)
        self._qt_layout.setColumnStretch(2, 0)  # East column
        
        self._qt_layout.setRowStretch(0, 0)     # North row
        self._qt_layout.setRowStretch(1, 1)     # Center row (expandable)
        self._qt_layout.setRowStretch(2, 0)     # South row
    
    def _re_add_all_widgets(self) -> None:
        """Re-add all widgets to the Qt layout"""
        if not self._qt_layout:
            return
            
        for direction, widgets in self.widgets.items():
            for widget in widgets:
                if hasattr(widget, '_layout_expand'):
                    expand = widget._layout_expand
                    fill = widget._layout_fill
                    kwargs = widget._layout_kwargs
                else:
                    expand = False
                    fill = True
                    kwargs = {}
                    
                self._add_widget_to_qt_layout(widget, direction, expand, fill, **kwargs)
    
    def remove_widget(self, widget: UIWidget) -> None:
        """Remove a widget from the layout"""
        for direction, widgets in self.widgets.items():
            if widget in widgets:
                widgets.remove(widget)
                if self._qt_layout and hasattr(widget, 'qt_widget'):
                    self._qt_layout.removeWidget(widget.qt_widget)
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
        
        # If we have a Qt layout, add the widget immediately
        if self._qt_layout and hasattr(widget, 'qt_widget'):
            self._add_widget_to_qt_layout(widget, direction, expand, fill, **kwargs)
    
    def clear(self) -> None:
        """Clear all widgets from the layout"""
        for direction, widgets in self.widgets.items():
            for widget in widgets:
                if self._qt_layout and hasattr(widget, 'qt_widget'):
                    self._qt_layout.removeWidget(widget.qt_widget)
            widgets.clear()
    
    def get_widgets(self, direction: Direction) -> List[UIWidget]:
        """Get all widgets in a specific direction"""
        return self.widgets.get(direction, [])
    
    def has_widgets(self, direction: Direction) -> bool:
        """Check if there are widgets in a specific direction"""
        return len(self.widgets.get(direction, [])) > 0
