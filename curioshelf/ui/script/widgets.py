"""
Script UI Widget Implementations

This module provides script UI implementations of UI widgets that can be
manipulated and queried programmatically for scripting interfaces.
It approximates Qt's layout and sizing behavior for headless systems.
"""

from typing import List, Optional, Dict, Any, Callable, Tuple
from dataclasses import dataclass
from enum import Enum
from ..abstraction import (
    UIWidget, UIButton, UITextInput, UIComboBox, UIListWidget, UICanvas,
    UIMessageBox, UIFileDialog, UIProgressBar, UIGroupBox, UITabWidget,
    UISplitter, UILayout, UIMenuBar, UIMenu, UIMenuItem, UIStatusBar,
    UIListItem, UISignal
)


class ScriptUISignal:
    """Script UI signal implementation that mimics Qt-style signals"""
    
    def __init__(self, widget: 'ScriptUIWidget', signal_name: str):
        self._widget = widget
        self._signal_name = signal_name
    
    def connect(self, callback: Callable[..., None]) -> None:
        """Connect a callback to this signal"""
        self._widget.connect_signal(self._signal_name, callback)
    
    def disconnect(self, callback: Callable[..., None]) -> None:
        """Disconnect a callback from this signal"""
        if self._signal_name in self._widget._signals:
            if callback in self._widget._signals[self._signal_name]:
                self._widget._signals[self._signal_name].remove(callback)


class SizePolicy(Enum):
    """Size policy similar to Qt's QSizePolicy"""
    FIXED = "fixed"           # Widget size is fixed
    MINIMUM = "minimum"       # Widget size is minimum, can't be smaller
    MAXIMUM = "maximum"       # Widget size is maximum, can't be larger
    PREFERRED = "preferred"   # Widget prefers its size hint
    EXPANDING = "expanding"   # Widget wants to expand as much as possible
    MINIMUM_EXPANDING = "minimum_expanding"  # Minimum + expanding
    IGNORED = "ignored"       # Widget size is ignored


@dataclass
class SizeHint:
    """Size hint similar to Qt's QSizeHint"""
    width: int
    height: int
    min_width: int = 0
    min_height: int = 0
    max_width: int = 16777215  # Qt's default max
    max_height: int = 16777215


@dataclass
class Geometry:
    """Geometry information similar to Qt's QRect"""
    x: int = 0
    y: int = 0
    width: int = 0
    height: int = 0
    
    def __post_init__(self):
        self.width = max(0, self.width)
        self.height = max(0, self.height)
    
    @property
    def right(self) -> int:
        return self.x + self.width
    
    @property
    def bottom(self) -> int:
        return self.y + self.height
    
    def contains(self, x: int, y: int) -> bool:
        """Check if point is within geometry"""
        return (self.x <= x < self.right and 
                self.y <= y < self.bottom)
    
    def intersects(self, other: 'Geometry') -> bool:
        """Check if geometries intersect"""
        return not (self.right <= other.x or other.right <= self.x or
                   self.bottom <= other.y or other.bottom <= self.y)
    
    def union(self, other: 'Geometry') -> 'Geometry':
        """Return union of two geometries"""
        if self.width == 0 and self.height == 0:
            return other
        if other.width == 0 and other.height == 0:
            return self
        
        left = min(self.x, other.x)
        top = min(self.y, other.y)
        right = max(self.right, other.right)
        bottom = max(self.bottom, other.bottom)
        
        return Geometry(left, top, right - left, bottom - top)


class ScriptUIWidget(UIWidget):
    """Base class for script UI widgets with programmatic control and Qt-like layout behavior"""
    
    def __init__(self) -> None:
        super().__init__()
        self._script_ui_id = f"script_widget_{id(self)}"
        self._properties: Dict[str, Any] = {}
        self._children: List['ScriptUIWidget'] = []
        self._parent: Optional['ScriptUIWidget'] = None
        self._verbose = False  # Add verbose flag
        
        # Layout and sizing properties (Qt-like)
        self._geometry = Geometry()
        self._size_hint = SizeHint(100, 30)  # Default size hint
        self._size_policy_horizontal = SizePolicy.PREFERRED
        self._size_policy_vertical = SizePolicy.PREFERRED
        self._minimum_size = SizeHint(0, 0)
        self._maximum_size = SizeHint(16777215, 16777215)
        self._margins = (0, 0, 0, 0)  # left, top, right, bottom
        self._spacing = 0
        self._stretch = 0  # Stretch factor for layouts
        
        # Layout management
        self._layout: Optional['ScriptUILayout'] = None
        self._needs_layout_update = True
    
    @property
    def verbose(self) -> bool:
        """Get verbose flag"""
        return self._verbose
    
    @verbose.setter
    def verbose(self, value: bool) -> None:
        """Set verbose flag"""
        self._verbose = value
    
    def get_script_ui_id(self) -> str:
        """Get the unique ID for this widget in script UI"""
        return self._script_ui_id
    
    def set_property(self, name: str, value: Any) -> None:
        """Set a property for programmatic access"""
        self._properties[name] = value
    
    def get_property(self, name: str, default: Any = None) -> Any:
        """Get a property for programmatic access"""
        return self._properties.get(name, default)
    
    def add_child(self, child: 'ScriptUIWidget') -> None:
        """Add a child widget"""
        if child not in self._children:
            self._children.append(child)
            child._parent = self
    
    def remove_child(self, child: 'ScriptUIWidget') -> None:
        """Remove a child widget"""
        if child in self._children:
            self._children.remove(child)
            child._parent = None
    
    def get_children(self) -> List['ScriptUIWidget']:
        """Get all child widgets"""
        return self._children.copy()
    
    def get_parent(self) -> Optional['ScriptUIWidget']:
        """Get the parent widget"""
        return self._parent
    
    def find_widget_by_id(self, widget_id: str) -> Optional['ScriptUIWidget']:
        """Find a widget by its script UI ID"""
        if self._script_ui_id == widget_id:
            return self
        
        for child in self._children:
            result = child.find_widget_by_id(widget_id)
            if result:
                return result
        
        return None
    
    def get_widget_tree(self) -> Dict[str, Any]:
        """Get a tree representation of the widget hierarchy"""
        return {
            "id": self._script_ui_id,
            "type": self.__class__.__name__,
            "properties": self._properties.copy(),
            "enabled": self.enabled,
            "visible": self.visible,
            "geometry": {
                "x": self._geometry.x,
                "y": self._geometry.y,
                "width": self._geometry.width,
                "height": self._geometry.height
            },
            "size_hint": {
                "width": self._size_hint.width,
                "height": self._size_hint.height
            },
            "children": [child.get_widget_tree() for child in self._children]
        }
    
    # Layout and sizing methods (Qt-like)
    
    def set_geometry(self, x: int, y: int, width: int, height: int) -> None:
        """Set the widget geometry"""
        self._geometry = Geometry(x, y, width, height)
        self.set_property("geometry", {
            "x": x, "y": y, "width": width, "height": height
        })
        self._needs_layout_update = True
        self._update_children_layout()
    
    def get_geometry(self) -> Tuple[int, int, int, int]:
        """Get the widget geometry as a tuple (x, y, width, height)"""
        return (self._geometry.x, self._geometry.y, self._geometry.width, self._geometry.height)
    
    def get_geometry_object(self) -> Geometry:
        """Get the widget geometry as a Geometry object"""
        return self._geometry
    
    def get_size(self) -> Tuple[int, int]:
        """Get the widget size as a tuple (width, height)"""
        return (self._geometry.width, self._geometry.height)
    
    def get_position(self) -> Tuple[int, int]:
        """Get the widget position as a tuple (x, y)"""
        return (self._geometry.x, self._geometry.y)
    
    def set_size_hint(self, width: int, height: int, 
                     min_width: int = 0, min_height: int = 0,
                     max_width: int = 16777215, max_height: int = 16777215) -> None:
        """Set the size hint for the widget"""
        self._size_hint = SizeHint(width, height, min_width, min_height, max_width, max_height)
        self.set_property("size_hint", {
            "width": width, "height": height,
            "min_width": min_width, "min_height": min_height,
            "max_width": max_width, "max_height": max_height
        })
        self._needs_layout_update = True
    
    def get_size_hint(self) -> SizeHint:
        """Get the size hint"""
        return self._size_hint
    
    def set_size_policy(self, horizontal: SizePolicy, vertical: SizePolicy) -> None:
        """Set the size policy for the widget"""
        self._size_policy_horizontal = horizontal
        self._size_policy_vertical = vertical
        self.set_property("size_policy", {
            "horizontal": horizontal.value,
            "vertical": vertical.value
        })
        self._needs_layout_update = True
    
    def get_size_policy(self) -> Tuple[SizePolicy, SizePolicy]:
        """Get the size policy"""
        return (self._size_policy_horizontal, self._size_policy_vertical)
    
    def set_minimum_size(self, width: int, height: int) -> None:
        """Set the minimum size"""
        self._minimum_size = SizeHint(width, height, width, height)
        self.set_property("minimum_size", {"width": width, "height": height})
        self._needs_layout_update = True
    
    def set_maximum_size(self, width: int, height: int) -> None:
        """Set the maximum size"""
        self._maximum_size = SizeHint(width, height, 0, 0, width, height)
        self.set_property("maximum_size", {"width": width, "height": height})
        self._needs_layout_update = True
    
    def set_margins(self, left: int, top: int, right: int, bottom: int) -> None:
        """Set the margins"""
        self._margins = (left, top, right, bottom)
        self.set_property("margins", {"left": left, "top": top, "right": right, "bottom": bottom})
        self._needs_layout_update = True
    
    def get_margins(self) -> Tuple[int, int, int, int]:
        """Get the margins"""
        return self._margins
    
    def set_stretch(self, stretch: int) -> None:
        """Set the stretch factor for layouts"""
        self._stretch = stretch
        self.set_property("stretch", stretch)
        self._needs_layout_update = True
    
    def get_stretch(self) -> int:
        """Get the stretch factor"""
        return self._stretch
    
    def size_hint(self) -> SizeHint:
        """Get the size hint (virtual method for subclasses to override)"""
        return self._size_hint
    
    def minimum_size_hint(self) -> SizeHint:
        """Get the minimum size hint"""
        return self._minimum_size
    
    def maximum_size_hint(self) -> SizeHint:
        """Get the maximum size hint"""
        return self._maximum_size
    
    def effective_size_hint(self) -> SizeHint:
        """Get the effective size hint considering size policy"""
        hint = self.size_hint()
        min_hint = self.minimum_size_hint()
        max_hint = self.maximum_size_hint()
        
        # Apply size policy constraints
        if self._size_policy_horizontal == SizePolicy.FIXED:
            width = hint.width
        elif self._size_policy_horizontal == SizePolicy.MINIMUM:
            width = min_hint.width
        elif self._size_policy_horizontal == SizePolicy.MAXIMUM:
            width = max_hint.width
        else:  # PREFERRED, EXPANDING, etc.
            width = hint.width
        
        if self._size_policy_vertical == SizePolicy.FIXED:
            height = hint.height
        elif self._size_policy_vertical == SizePolicy.MINIMUM:
            height = min_hint.height
        elif self._size_policy_vertical == SizePolicy.MAXIMUM:
            height = max_hint.height
        else:  # PREFERRED, EXPANDING, etc.
            height = hint.height
        
        # Clamp to min/max
        width = max(min_hint.width, min(width, max_hint.width))
        height = max(min_hint.height, min(height, max_hint.height))
        
        return SizeHint(width, height, min_hint.width, min_hint.height, max_hint.width, max_hint.height)
    
    def _update_children_layout(self) -> None:
        """Update layout for child widgets"""
        if self._layout:
            self._layout.update_layout()
        else:
            # Simple layout update for widgets without explicit layout
            for child in self._children:
                if hasattr(child, '_update_children_layout'):
                    child._update_children_layout()
    
    def resize(self, width: int, height: int) -> None:
        """Resize the widget"""
        self.set_geometry(self._geometry.x, self._geometry.y, width, height)
    
    def move(self, x: int, y: int) -> None:
        """Move the widget"""
        self.set_geometry(x, y, self._geometry.width, self._geometry.height)
    
    def adjust_size(self) -> None:
        """Adjust size to fit content"""
        hint = self.effective_size_hint()
        self.resize(hint.width, hint.height)
    
    def is_visible_to(self, other: 'ScriptUIWidget') -> bool:
        """Check if this widget is visible to another widget"""
        if not self.visible:
            return False
        
        # Check if this widget is in the parent chain of the other widget
        current = other
        while current:
            if current == self:
                return True
            current = current._parent
        
        return False
    
    def map_to_parent(self, x: int, y: int) -> Tuple[int, int]:
        """Map coordinates to parent widget"""
        return (x + self._geometry.x, y + self._geometry.y)
    
    def map_to_global(self, x: int, y: int) -> Tuple[int, int]:
        """Map coordinates to global coordinates"""
        gx, gy = x, y
        current = self
        while current:
            gx += current._geometry.x
            gy += current._geometry.y
            current = current._parent
        return (gx, gy)
    
    def map_from_parent(self, x: int, y: int) -> Tuple[int, int]:
        """Map coordinates from parent widget"""
        return (x - self._geometry.x, y - self._geometry.y)
    
    def map_from_global(self, x: int, y: int) -> Tuple[int, int]:
        """Map coordinates from global coordinates"""
        lx, ly = x, y
        current = self
        while current:
            lx -= current._geometry.x
            ly -= current._geometry.y
            current = current._parent
        return (lx, ly)
    
    def set_style(self, style: str) -> None:
        """Set CSS-like style for the widget (stub implementation)"""
        # Store style as a property for compatibility
        self.set_property("style", style)
        if self.verbose:
            print(f"[SCRIPT UI] Widget style set: {style}")


class ScriptUIButton(ScriptUIWidget, UIButton):
    """Script UI implementation of a button with Qt-like sizing"""
    
    def __init__(self, text: str = "") -> None:
        super().__init__()
        self._text = text
        self._clicked_callback: Optional[Callable[[], None]] = None
        self.set_property("text", text)
        
        # Set appropriate size hint for button
        text_width = len(text) * 8 + 20  # Approximate character width + padding
        self.set_size_hint(text_width, 30)  # Standard button height
        self.set_minimum_size(50, 25)  # Minimum button size
        self.set_size_policy(SizePolicy.PREFERRED, SizePolicy.FIXED)
    
    def click(self) -> None:
        """Simulate a button click programmatically"""
        if self.verbose:
            print(f"[SCRIPT UI] Button '{self._text}' clicked")
        
        if self._clicked_callback:
            self._clicked_callback()
        self.emit_signal("clicked")
    
    def set_text(self, text: str) -> None:
        """Set button text"""
        self._text = text
        self.set_property("text", text)
        # Update size hint based on new text
        text_width = len(text) * 8 + 20
        self.set_size_hint(text_width, 30)
    
    def get_text(self) -> str:
        """Get button text"""
        return self._text
    
    def size_hint(self) -> SizeHint:
        """Override size hint to be based on text content"""
        text_width = len(self._text) * 8 + 20
        return SizeHint(text_width, 30, 50, 25)
    
    @property
    def clicked(self) -> ScriptUISignal:
        """Get the clicked signal for Qt-style connections"""
        return ScriptUISignal(self, "clicked")


class ScriptUITextInput(ScriptUIWidget, UITextInput):
    """Script UI implementation of a text input with Qt-like sizing"""
    
    def __init__(self, placeholder: str = "") -> None:
        super().__init__()
        self._text = ""
        self._placeholder = placeholder
        self.set_property("placeholder", placeholder)
        
        # Set appropriate size hint for text input
        self.set_size_hint(150, 25)  # Standard text input size
        self.set_minimum_size(50, 20)
        self.set_size_policy(SizePolicy.EXPANDING, SizePolicy.FIXED)
    
    def set_text(self, text: str) -> None:
        """Set text and emit signal"""
        old_text = self._text
        self._text = text
        self.set_property("text", text)
        if old_text != text:
            self.emit_signal("text_changed", text)
    
    def get_text(self) -> str:
        """Get the current text"""
        return self._text
    
    def get_placeholder(self) -> str:
        """Get placeholder text"""
        return self._placeholder
    
    def set_placeholder(self, placeholder: str) -> None:
        """Set placeholder text"""
        self._placeholder = placeholder
        self.set_property("placeholder", placeholder)
    
    def clear(self) -> None:
        """Clear the text input"""
        self.set_text("")
    
    @property
    def text_changed(self) -> ScriptUISignal:
        """Get the text_changed signal for Qt-style connections"""
        return ScriptUISignal(self, "text_changed")


class ScriptUIComboBox(ScriptUIWidget, UIComboBox):
    """Script UI implementation of a combo box"""
    
    def __init__(self) -> None:
        super().__init__()
        self._items: List[tuple[str, Any]] = []
        self._current_index = -1
    
    def add_item(self, text_or_item, data: Any = None) -> None:
        """Add an item to the combo box"""
        if isinstance(text_or_item, str):
            self._items.append((text_or_item, data))
        else:
            item = text_or_item
            self._items.append((item.get_text(), item.get_data()))
        
        self.set_property("items", [item[0] for item in self._items])
    
    def clear(self) -> None:
        """Clear all items"""
        self._items.clear()
        self._current_index = -1
        self.set_property("items", [])
    
    def set_current_index(self, index: int) -> None:
        """Set the current selection"""
        if 0 <= index < len(self._items):
            self._current_index = index
            self.set_property("current_index", index)
            self.set_property("current_text", self._items[index][0])
            self.emit_signal("current_index_changed", index)
    
    def get_current_index(self) -> int:
        """Get the current selection index"""
        return self._current_index
    
    def get_current_text(self) -> str:
        """Get the current selection text"""
        if 0 <= self._current_index < len(self._items):
            return self._items[self._current_index][0]
        return ""
    
    def get_item_count(self) -> int:
        """Get the number of items"""
        return len(self._items)


class ScriptUIListWidget(ScriptUIWidget, UIListWidget):
    """Script UI implementation of a list widget"""
    
    def __init__(self) -> None:
        super().__init__()
        self._items: List[Tuple[str, Any]] = []  # List of (text, data) tuples
        self._current_index = -1
    
    def add_item(self, item: UIListItem) -> None:
        """Add an item to the list"""
        # Extract text and data from UIListItem using proper methods
        text = item.get_text()
        data = item.get_data()
        self._items.append((text, data))
        self.set_property("item_count", len(self._items))
    
    def clear(self) -> None:
        """Clear all items"""
        self._items.clear()
        self._current_index = -1
        self.set_property("item_count", 0)
    
    def set_current_index(self, index: int) -> None:
        """Set the current selection"""
        if 0 <= index < len(self._items):
            self._current_index = index
            self.set_property("current_index", index)
            self.emit_signal("current_index_changed", index)
            self.emit_signal("item_selected", index)
    
    def get_current_index(self) -> int:
        """Get the current selection index"""
        return self._current_index
    
    def get_item_count(self) -> int:
        """Get the number of items"""
        return len(self._items)
    
    def get_item(self, index: int) -> Optional[UIListItem]:
        """Get an item by index"""
        if 0 <= index < len(self._items):
            # Return a mock UIListItem for compatibility
            from tests.ui_mocks import MockUIListItem
            text, data = self._items[index]
            item = MockUIListItem(text)
            if data is not None:
                item.set_data(data)
            return item
        return None
    
    def current_text(self) -> str:
        """Get the text of the currently selected item"""
        if 0 <= self._current_index < len(self._items):
            return self._items[self._current_index][0]
        return ""
    
    def current_data(self) -> Any:
        """Get the data of the currently selected item"""
        if 0 <= self._current_index < len(self._items):
            return self._items[self._current_index][1]
        return None
    
    @property
    def item_selected(self) -> ScriptUISignal:
        """Get the item_selected signal for Qt-style connections"""
        return ScriptUISignal(self, "item_selected")


class ScriptUICanvas(ScriptUIWidget, UICanvas):
    """Script UI implementation of a canvas"""
    
    def __init__(self) -> None:
        super().__init__()
        self._draw_commands: List[Dict[str, Any]] = []
    
    def draw_rect(self, x: int, y: int, width: int, height: int, color: str = "black") -> None:
        """Draw a rectangle"""
        command = {
            "type": "rect",
            "x": x, "y": y, "width": width, "height": height, "color": color
        }
        self._draw_commands.append(command)
        self.set_property("draw_commands", self._draw_commands.copy())
    
    def draw_circle(self, x: int, y: int, radius: int, color: str = "black") -> None:
        """Draw a circle"""
        command = {
            "type": "circle",
            "x": x, "y": y, "radius": radius, "color": color
        }
        self._draw_commands.append(command)
        self.set_property("draw_commands", self._draw_commands.copy())
    
    def clear(self) -> None:
        """Clear the canvas"""
        self._draw_commands.clear()
        self.set_property("draw_commands", [])
    
    def get_draw_commands(self) -> List[Dict[str, Any]]:
        """Get all draw commands"""
        return self._draw_commands.copy()


class ScriptUIMessageBox(ScriptUIWidget, UIMessageBox):
    """Script UI implementation of a message box"""
    
    def __init__(self) -> None:
        super().__init__()
        self._title = ""
        self._text = ""
        self._buttons: List[str] = []
        self._result: Optional[str] = None
    
    def set_title(self, title: str) -> None:
        """Set the message box title"""
        self._title = title
        self.set_property("title", title)
    
    def set_text(self, text: str) -> None:
        """Set the message box text"""
        self._text = text
        self.set_property("text", text)
    
    def set_buttons(self, buttons: List[str]) -> None:
        """Set the message box buttons"""
        self._buttons = buttons
        self.set_property("buttons", buttons)
    
    def show(self) -> str:
        """Show the message box and return the result"""
        if self.verbose:
            print(f"[SCRIPT UI] Message Box: {self._title}")
            print(f"[SCRIPT UI] Text: {self._text}")
            print(f"[SCRIPT UI] Buttons: {self._buttons}")
        
        # For script UI, we can simulate different behaviors
        # In a real implementation, this might interact with the script runtime
        self._result = self._buttons[0] if self._buttons else "OK"
        self.set_property("result", self._result)
        return self._result
    
    def get_result(self) -> Optional[str]:
        """Get the message box result"""
        return self._result


class ScriptUIFileDialog(ScriptUIWidget, UIFileDialog):
    """Script UI implementation of a file dialog"""
    
    def __init__(self) -> None:
        super().__init__()
        self._title = ""
        self._filter = ""
        self._mode = "open"
        self._result: Optional[str] = None
    
    def set_title(self, title: str) -> None:
        """Set the dialog title"""
        self._title = title
        self.set_property("title", title)
    
    def set_filter(self, filter_str: str) -> None:
        """Set the file filter"""
        self._filter = filter_str
        self.set_property("filter", filter_str)
    
    def set_mode(self, mode: str) -> None:
        """Set the dialog mode (open/save)"""
        self._mode = mode
        self.set_property("mode", mode)
    
    def show(self) -> Optional[str]:
        """Show the file dialog and return the selected file"""
        if self.verbose:
            print(f"[SCRIPT UI] File Dialog: {self._title}")
            print(f"[SCRIPT UI] Filter: {self._filter}")
            print(f"[SCRIPT UI] Mode: {self._mode}")
        
        # For script UI, we can simulate different behaviors
        # In a real implementation, this might interact with the script runtime
        self._result = None  # Simulate no file selected
        self.set_property("result", self._result)
        return self._result
    
    def get_result(self) -> Optional[str]:
        """Get the selected file"""
        return self._result


class ScriptUIProgressBar(ScriptUIWidget, UIProgressBar):
    """Script UI implementation of a progress bar"""
    
    def __init__(self) -> None:
        super().__init__()
        self._value = 0
        self._minimum = 0
        self._maximum = 100
    
    def set_value(self, value: int) -> None:
        """Set the progress value"""
        self._value = max(self._minimum, min(self._maximum, value))
        self.set_property("value", self._value)
        self.emit_signal("value_changed", self._value)
    
    def set_range(self, minimum: int, maximum: int) -> None:
        """Set the progress range"""
        self._minimum = minimum
        self._maximum = maximum
        self.set_property("minimum", minimum)
        self.set_property("maximum", maximum)
    
    def get_value(self) -> int:
        """Get the current value"""
        return self._value
    
    def get_percentage(self) -> float:
        """Get the progress as a percentage"""
        if self._maximum > self._minimum:
            return (self._value - self._minimum) / (self._maximum - self._minimum) * 100
        return 0.0


class ScriptUIGroupBox(ScriptUIWidget, UIGroupBox):
    """Script UI implementation of a group box"""
    
    def __init__(self, title: str = "") -> None:
        super().__init__()
        self._title = title
        self.set_property("title", title)
    
    def set_title(self, title: str) -> None:
        """Set the group box title"""
        self._title = title
        self.set_property("title", title)
    
    def get_title(self) -> str:
        """Get the group box title"""
        return self._title


class ScriptUITabWidget(ScriptUIWidget, UITabWidget):
    """Script UI implementation of a tab widget"""
    
    def __init__(self) -> None:
        super().__init__()
        self._tabs: List[tuple[str, UIWidget]] = []
        self._current_index = -1
    
    def add_tab(self, title: str, widget: UIWidget) -> None:
        """Add a tab"""
        self._tabs.append((title, widget))
        self.set_property("tab_count", len(self._tabs))
        if self._current_index == -1:
            self._current_index = 0
    
    def set_current_index(self, index: int) -> None:
        """Set the current tab"""
        if 0 <= index < len(self._tabs):
            self._current_index = index
            self.set_property("current_index", index)
            self.emit_signal("current_index_changed", index)
    
    def get_current_index(self) -> int:
        """Get the current tab index"""
        return self._current_index
    
    def get_tab_count(self) -> int:
        """Get the number of tabs"""
        return len(self._tabs)


class ScriptUISplitter(ScriptUIWidget, UISplitter):
    """Script UI implementation of a splitter"""
    
    def __init__(self, orientation: str = "horizontal") -> None:
        super().__init__()
        self._orientation = orientation
        self.set_property("orientation", orientation)
    
    def set_orientation(self, orientation: str) -> None:
        """Set the splitter orientation"""
        self._orientation = orientation
        self.set_property("orientation", orientation)
    
    def get_orientation(self) -> str:
        """Get the splitter orientation"""
        return self._orientation


class ScriptUILayout(ScriptUIWidget, UILayout):
    """Script UI implementation of a layout with Qt-like behavior"""
    
    def __init__(self, orientation: str = "vertical") -> None:
        super().__init__()
        self._orientation = orientation
        self._widgets: List[UIWidget] = []
        self._spacing = 6  # Default spacing between widgets
        self._margins = (0, 0, 0, 0)  # left, top, right, bottom
        self.set_property("orientation", orientation)
        
        # Layout-specific size policy
        self.set_size_policy(SizePolicy.EXPANDING, SizePolicy.EXPANDING)
    
    def add_widget(self, widget: UIWidget, expand: bool = False, **kwargs) -> None:
        """Add a widget to the layout"""
        self._widgets.append(widget)
        self.set_property("widget_count", len(self._widgets))
        if isinstance(widget, ScriptUIWidget):
            self.add_child(widget)
            # Set stretch factor based on expand parameter
            if expand:
                widget.set_stretch(1)
        self._needs_layout_update = True
    
    def remove_widget(self, widget: UIWidget) -> None:
        """Remove a widget from the layout"""
        if widget in self._widgets:
            self._widgets.remove(widget)
            self.set_property("widget_count", len(self._widgets))
            if isinstance(widget, ScriptUIWidget):
                self.remove_child(widget)
            self._needs_layout_update = True
    
    def insert_widget(self, index: int, widget: UIWidget, *args: Any, **kwargs: Any) -> None:
        """Insert a widget at a specific index in the layout"""
        if 0 <= index <= len(self._widgets):
            self._widgets.insert(index, widget)
            self.set_property("widget_count", len(self._widgets))
            if isinstance(widget, ScriptUIWidget):
                self.add_child(widget)
            self._needs_layout_update = True
    
    def get_widgets(self) -> List[UIWidget]:
        """Get all widgets in the layout"""
        return self._widgets.copy()
    
    def set_orientation(self, orientation: str) -> None:
        """Set the layout orientation"""
        self._orientation = orientation
        self.set_property("orientation", orientation)
        self._needs_layout_update = True
    
    def get_orientation(self) -> str:
        """Get the layout orientation"""
        return self._orientation
    
    def set_spacing(self, spacing: int) -> None:
        """Set spacing between widgets"""
        self._spacing = spacing
        self.set_property("spacing", spacing)
        self._needs_layout_update = True
    
    def get_spacing(self) -> int:
        """Get spacing between widgets"""
        return self._spacing
    
    def set_margins(self, left: int, top: int, right: int, bottom: int) -> None:
        """Set layout margins"""
        self._margins = (left, top, right, bottom)
        self.set_property("margins", {"left": left, "top": top, "right": right, "bottom": bottom})
        self._needs_layout_update = True
    
    def get_margins(self) -> Tuple[int, int, int, int]:
        """Get layout margins"""
        return self._margins
    
    def size_hint(self) -> SizeHint:
        """Calculate size hint for the layout"""
        if not self._widgets:
            return SizeHint(0, 0)
        
        total_width = 0
        total_height = 0
        
        if self._orientation == "vertical":
            # Vertical layout: width is max of all widgets, height is sum + spacing
            for i, widget in enumerate(self._widgets):
                if isinstance(widget, ScriptUIWidget):
                    hint = widget.effective_size_hint()
                    total_width = max(total_width, hint.width)
                    total_height += hint.height
                    if i > 0:  # Add spacing between widgets
                        total_height += self._spacing
        else:  # horizontal
            # Horizontal layout: height is max of all widgets, width is sum + spacing
            for i, widget in enumerate(self._widgets):
                if isinstance(widget, ScriptUIWidget):
                    hint = widget.effective_size_hint()
                    total_height = max(total_height, hint.height)
                    total_width += hint.width
                    if i > 0:  # Add spacing between widgets
                        total_width += self._spacing
        
        # Add margins
        total_width += self._margins[0] + self._margins[2]  # left + right
        total_height += self._margins[1] + self._margins[3]  # top + bottom
        
        return SizeHint(total_width, total_height)
    
    def minimum_size_hint(self) -> SizeHint:
        """Calculate minimum size hint for the layout"""
        if not self._widgets:
            return SizeHint(0, 0)
        
        total_width = 0
        total_height = 0
        
        if self._orientation == "vertical":
            for i, widget in enumerate(self._widgets):
                if isinstance(widget, ScriptUIWidget):
                    hint = widget.minimum_size_hint()
                    total_width = max(total_width, hint.width)
                    total_height += hint.height
                    if i > 0:
                        total_height += self._spacing
        else:  # horizontal
            for i, widget in enumerate(self._widgets):
                if isinstance(widget, ScriptUIWidget):
                    hint = widget.minimum_size_hint()
                    total_height = max(total_height, hint.height)
                    total_width += hint.width
                    if i > 0:
                        total_width += self._spacing
        
        # Add margins
        total_width += self._margins[0] + self._margins[2]
        total_height += self._margins[1] + self._margins[3]
        
        return SizeHint(total_width, total_height)
    
    def update_layout(self) -> None:
        """Update the layout of child widgets"""
        if not self._widgets or not self._needs_layout_update:
            return
        
        self._needs_layout_update = False
        
        # Get available space (parent geometry minus margins)
        available_width = self._geometry.width - self._margins[0] - self._margins[2]
        available_height = self._geometry.height - self._margins[1] - self._margins[3]
        
        if available_width <= 0 or available_height <= 0:
            return
        
        # Calculate widget positions and sizes
        if self._orientation == "vertical":
            self._layout_vertical(available_width, available_height)
        else:  # horizontal
            self._layout_horizontal(available_width, available_height)
    
    def _layout_vertical(self, available_width: int, available_height: int) -> None:
        """Layout widgets vertically"""
        if not self._widgets:
            return
        
        # Calculate total preferred height
        total_preferred_height = 0
        expanding_widgets = []
        
        for widget in self._widgets:
            if isinstance(widget, ScriptUIWidget):
                hint = widget.effective_size_hint()
                total_preferred_height += hint.height
                if widget.get_size_policy()[1] == SizePolicy.EXPANDING:
                    expanding_widgets.append(widget)
        
        # Add spacing
        total_preferred_height += (len(self._widgets) - 1) * self._spacing
        
        # Calculate extra height to distribute
        extra_height = max(0, available_height - total_preferred_height)
        
        # Distribute extra height among expanding widgets
        extra_per_widget = 0
        if expanding_widgets and extra_height > 0:
            extra_per_widget = extra_height // len(expanding_widgets)
        
        # Position widgets
        current_y = self._geometry.y + self._margins[1]
        
        for i, widget in enumerate(self._widgets):
            if isinstance(widget, ScriptUIWidget):
                hint = widget.effective_size_hint()
                
                # Calculate widget height
                widget_height = hint.height
                if widget in expanding_widgets:
                    widget_height += extra_per_widget
                
                # Calculate widget width
                widget_width = min(available_width, hint.width)
                if widget.get_size_policy()[0] == SizePolicy.EXPANDING:
                    widget_width = available_width
                
                # Center horizontally
                widget_x = self._geometry.x + self._margins[0] + (available_width - widget_width) // 2
                
                # Set widget geometry
                widget.set_geometry(widget_x, current_y, widget_width, widget_height)
                
                current_y += widget_height + self._spacing
    
    def _layout_horizontal(self, available_width: int, available_height: int) -> None:
        """Layout widgets horizontally"""
        if not self._widgets:
            return
        
        # Calculate total preferred width
        total_preferred_width = 0
        expanding_widgets = []
        
        for widget in self._widgets:
            if isinstance(widget, ScriptUIWidget):
                hint = widget.effective_size_hint()
                total_preferred_width += hint.width
                if widget.get_size_policy()[0] == SizePolicy.EXPANDING:
                    expanding_widgets.append(widget)
        
        # Add spacing
        total_preferred_width += (len(self._widgets) - 1) * self._spacing
        
        # Calculate extra width to distribute
        extra_width = max(0, available_width - total_preferred_width)
        
        # Distribute extra width among expanding widgets
        extra_per_widget = 0
        if expanding_widgets and extra_width > 0:
            extra_per_widget = extra_width // len(expanding_widgets)
        
        # Position widgets
        current_x = self._geometry.x + self._margins[0]
        
        for i, widget in enumerate(self._widgets):
            if isinstance(widget, ScriptUIWidget):
                hint = widget.effective_size_hint()
                
                # Calculate widget width
                widget_width = hint.width
                if widget in expanding_widgets:
                    widget_width += extra_per_widget
                
                # Calculate widget height
                widget_height = min(available_height, hint.height)
                if widget.get_size_policy()[1] == SizePolicy.EXPANDING:
                    widget_height = available_height
                
                # Center vertically
                widget_y = self._geometry.y + self._margins[1] + (available_height - widget_height) // 2
                
                # Set widget geometry
                widget.set_geometry(current_x, widget_y, widget_width, widget_height)
                
                current_x += widget_width + self._spacing


class ScriptUIMenuItem(ScriptUIWidget, UIMenuItem):
    """Script UI implementation of a menu item"""
    
    def __init__(self, text: str = "") -> None:
        # Call UIMenuItem.__init__ first, then UIWidget.__init__ to avoid double inheritance
        UIMenuItem.__init__(self, text)
        UIWidget.__init__(self)
        
        # Initialize ScriptUIWidget-specific properties
        self._script_ui_id = f"script_widget_{id(self)}"
        self._properties: Dict[str, Any] = {}
        self._children: List['ScriptUIWidget'] = []
        self._parent: Optional['ScriptUIWidget'] = None
        self._verbose = False
        
        # Layout and sizing properties (Qt-like)
        self._geometry = Geometry()
        self._size_hint = SizeHint(100, 30)  # Default size hint
        self._size_policy_horizontal = SizePolicy.PREFERRED
        self._size_policy_vertical = SizePolicy.PREFERRED
        self._minimum_size = SizeHint(0, 0)
        self._maximum_size = SizeHint(16777215, 16777215)
        self._margins = (0, 0, 0, 0)  # left, top, right, bottom
        self._spacing = 0
        self._stretch = 0  # Stretch factor for layouts
        
        # Layout management
        self._layout: Optional['ScriptUILayout'] = None
        self._needs_layout_update = True
        
        self._text = text
        self._clicked_callback: Optional[Callable[[], None]] = None
        self.set_property("text", text)
    
    @property
    def text(self) -> str:
        """Get the menu item text"""
        return self._text
    
    @text.setter
    def text(self, value: str) -> None:
        """Set the menu item text"""
        self._text = value
        self.set_property("text", value)
    
    def set_text(self, text: str) -> None:
        """Set the menu item text"""
        self.text = text
    
    def set_clicked_callback(self, callback: Callable[[], None]) -> None:
        """Set the callback for when the menu item is clicked"""
        self._clicked_callback = callback
    
    def _on_clicked(self) -> None:
        """Handle menu item click"""
        # Only execute callback if the item is enabled
        if not self.enabled:
            return
        
        if self._clicked_callback:
            self._clicked_callback()
        self.emit_signal("clicked")
    
    @property
    def clicked(self) -> ScriptUISignal:
        """Get the clicked signal for Qt-style connections"""
        return ScriptUISignal(self, "clicked")


class ScriptUIMenu(ScriptUIWidget, UIMenu):
    """Script UI implementation of a menu"""
    
    def __init__(self, title: str = "") -> None:
        # Call UIMenu.__init__ first, then UIWidget.__init__ to avoid double inheritance
        UIMenu.__init__(self, title)
        UIWidget.__init__(self)
        
        # Initialize ScriptUIWidget-specific properties
        self._script_ui_id = f"script_widget_{id(self)}"
        self._properties: Dict[str, Any] = {}
        self._children: List['ScriptUIWidget'] = []
        self._parent: Optional['ScriptUIWidget'] = None
        self._verbose = False
        
        # Layout and sizing properties (Qt-like)
        self._geometry = Geometry()
        self._size_hint = SizeHint(100, 30)  # Default size hint
        self._size_policy_horizontal = SizePolicy.PREFERRED
        self._size_policy_vertical = SizePolicy.PREFERRED
        self._minimum_size = SizeHint(0, 0)
        self._maximum_size = SizeHint(16777215, 16777215)
        self._margins = (0, 0, 0, 0)  # left, top, right, bottom
        self._spacing = 0
        self._stretch = 0  # Stretch factor for layouts
        
        # Layout management
        self._layout: Optional['ScriptUILayout'] = None
        self._needs_layout_update = True
        
        self._title = title
        self._items: List[UIMenuItem] = []
        self.set_property("title", title)
    
    @property
    def title(self) -> str:
        """Get the menu title"""
        return self._title
    
    @title.setter
    def title(self, value: str) -> None:
        """Set the menu title"""
        self._title = value
        self.set_property("title", value)
    
    def add_item(self, item: UIMenuItem) -> None:
        """Add a menu item to the menu"""
        self._items.append(item)
        self.set_property("item_count", len(self._items))
    
    def remove_item(self, item: UIMenuItem) -> None:
        """Remove a menu item from the menu"""
        if item in self._items:
            self._items.remove(item)
            self.set_property("item_count", len(self._items))
    
    def get_items(self) -> List[UIMenuItem]:
        """Get all menu items"""
        return self._items.copy()
    
    def clear(self) -> None:
        """Clear all menu items"""
        self._items.clear()
        self.set_property("item_count", 0)
    
    def add_separator(self) -> None:
        """Add a separator to the menu (stub implementation)"""
        # For script UI, we can just add a placeholder item
        separator_item = ScriptUIMenuItem("---")
        self._items.append(separator_item)
        self.set_property("item_count", len(self._items))


class ScriptUIMenuBar(ScriptUIWidget, UIMenuBar):
    """Script UI implementation of a menu bar"""
    
    def __init__(self) -> None:
        # Call UIMenuBar.__init__ first, then UIWidget.__init__ to avoid double inheritance
        UIMenuBar.__init__(self)
        UIWidget.__init__(self)
        
        # Initialize ScriptUIWidget-specific properties
        self._script_ui_id = f"script_widget_{id(self)}"
        self._properties: Dict[str, Any] = {}
        self._children: List['ScriptUIWidget'] = []
        self._parent: Optional['ScriptUIWidget'] = None
        self._verbose = False
        
        # Layout and sizing properties (Qt-like)
        self._geometry = Geometry()
        self._size_hint = SizeHint(100, 30)  # Default size hint
        self._size_policy_horizontal = SizePolicy.EXPANDING
        self._size_policy_vertical = SizePolicy.FIXED
        self._minimum_size = SizeHint(0, 0)
        self._maximum_size = SizeHint(16777215, 16777215)
        self._margins = (0, 0, 0, 0)  # left, top, right, bottom
        self._spacing = 0
        self._stretch = 0  # Stretch factor for layouts
        
        # Layout management
        self._layout: Optional['ScriptUILayout'] = None
        self._needs_layout_update = True
        
        self._menus: List[UIMenu] = []
    
    def add_menu(self, menu: UIMenu) -> None:
        """Add a menu to the menu bar"""
        self._menus.append(menu)
        self.set_property("menu_count", len(self._menus))
    
    def remove_menu(self, menu: UIMenu) -> None:
        """Remove a menu from the menu bar"""
        if menu in self._menus:
            self._menus.remove(menu)
            self.set_property("menu_count", len(self._menus))
    
    def get_menus(self) -> List[UIMenu]:
        """Get all menus"""
        return self._menus.copy()
    
    def clear(self) -> None:
        """Clear all menus"""
        self._menus.clear()
        self.set_property("menu_count", 0)


class ScriptUIStatusBar(ScriptUIWidget, UIStatusBar):
    """Script UI implementation of a status bar"""
    
    def __init__(self) -> None:
        # Call UIStatusBar.__init__ first, then UIWidget.__init__ to avoid double inheritance
        UIStatusBar.__init__(self)
        UIWidget.__init__(self)
        
        # Initialize ScriptUIWidget-specific properties
        self._script_ui_id = f"script_widget_{id(self)}"
        self._properties: Dict[str, Any] = {}
        self._children: List['ScriptUIWidget'] = []
        self._parent: Optional['ScriptUIWidget'] = None
        self._verbose = False
        
        # Layout and sizing properties (Qt-like)
        self._geometry = Geometry()
        self._size_hint = SizeHint(100, 25)  # Default status bar size
        self._size_policy_horizontal = SizePolicy.EXPANDING
        self._size_policy_vertical = SizePolicy.FIXED
        self._minimum_size = SizeHint(0, 0)
        self._maximum_size = SizeHint(16777215, 16777215)
        self._margins = (0, 0, 0, 0)  # left, top, right, bottom
        self._spacing = 0
        self._stretch = 0  # Stretch factor for layouts
        
        # Layout management
        self._layout: Optional['ScriptUILayout'] = None
        self._needs_layout_update = True
        
        self._widgets: List[UIWidget] = []
    
    def add_widget(self, widget: UIWidget) -> None:
        """Add a widget to the status bar"""
        self._widgets.append(widget)
        self.set_property("widget_count", len(self._widgets))
        if isinstance(widget, ScriptUIWidget):
            self.add_child(widget)
    
    def remove_widget(self, widget: UIWidget) -> None:
        """Remove a widget from the status bar"""
        if widget in self._widgets:
            self._widgets.remove(widget)
            self.set_property("widget_count", len(self._widgets))
            if isinstance(widget, ScriptUIWidget):
                self.remove_child(widget)
    
    def get_widgets(self) -> List[UIWidget]:
        """Get all widgets in the status bar"""
        return self._widgets.copy()
    
    def clear(self) -> None:
        """Clear all widgets from the status bar"""
        self._widgets.clear()
        self.set_property("widget_count", 0)
