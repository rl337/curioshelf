"""
UI Abstraction Layer for CurioShelf

This module provides abstract interfaces for UI components, allowing for easy testing
and mocking without requiring the actual GUI framework to be running.
"""

from abc import ABC, abstractmethod
from typing import List, Optional, Dict, Any, Callable
from pathlib import Path
from dataclasses import dataclass

from ..models import AssetSource, ObjectSlice, CurioObject, Template


@dataclass
class UISignal:
    """Represents a UI signal/event"""
    name: str
    data: Any = None


class UIWidget(ABC):
    """Abstract base class for UI widgets"""
    
    def __init__(self) -> None:
        self._signals: Dict[str, List[Callable[..., None]]] = {}
        self._enabled = True
        self._visible = True
        self._layout: Optional['UILayout'] = None
        self._test_mode = False
        self._test_commands: List[Dict[str, Any]] = []
        self._test_command_index = 0
        self._state_callbacks: Dict[str, Callable[[], bool]] = {}
    
    def connect_signal(self, signal_name: str, callback: Callable[..., None]) -> None:
        """Connect a callback to a signal"""
        if signal_name not in self._signals:
            self._signals[signal_name] = []
        self._signals[signal_name].append(callback)
    
    def emit_signal(self, signal_name: str, data: Any = None) -> None:
        """Emit a signal to all connected callbacks"""
        if signal_name in self._signals:
            for callback in self._signals[signal_name]:
                callback(data)
    
    def set_enabled(self, enabled: bool) -> None:
        """Enable or disable the widget"""
        self._enabled = enabled
    
    def set_visible(self, visible: bool) -> None:
        """Show or hide the widget"""
        self._visible = visible
    
    def show(self) -> None:
        """Show the widget"""
        self.set_visible(True)
    
    def enable_test_mode(self, commands: List[Dict[str, Any]]) -> None:
        """Enable test mode with a list of commands to execute"""
        self._test_mode = True
        self._test_commands = commands
        self._test_command_index = 0
        self._start_test_execution()
    
    def disable_test_mode(self) -> None:
        """Disable test mode"""
        self._test_mode = False
        self._test_commands = []
        self._test_command_index = 0
    
    def _start_test_execution(self) -> None:
        """Start executing test commands (to be overridden by implementations)"""
        pass
    
    def _execute_test_command(self, command: Dict[str, Any]) -> None:
        """Execute a single test command (to be overridden by implementations)"""
        pass
    
    def _next_test_command(self) -> None:
        """Execute the next test command (to be overridden by implementations)"""
        pass
    
    @property
    def enabled(self) -> bool:
        return self._enabled
    
    @property
    def visible(self) -> bool:
        return self._visible
    
    def set_layout(self, layout: 'UILayout') -> None:
        """Set the layout for the widget"""
        self._layout = layout
    
    def set_state_callback(self, state_name: str, callback: Callable[[], bool]) -> None:
        """Set a callback that returns the state for a given state name"""
        self._state_callbacks[state_name] = callback
    
    def get_state_callback(self, state_name: str) -> Optional[Callable[[], bool]]:
        """Get the callback for a given state name"""
        return self._state_callbacks.get(state_name)
    
    def has_state_callback(self, state_name: str) -> bool:
        """Check if a state callback exists for the given state name"""
        return state_name in self._state_callbacks
    
    def update_state(self, state_name: str) -> None:
        """Update the widget state based on the callback for the given state name"""
        if state_name in self._state_callbacks:
            callback = self._state_callbacks[state_name]
            new_state = callback()
            if state_name == "enabled":
                self.set_enabled(new_state)
            elif state_name == "visible":
                self.set_visible(new_state)
    
    def update_all_states(self) -> None:
        """Update all widget states based on their callbacks"""
        for state_name in self._state_callbacks:
            self.update_state(state_name)


class UIButton(UIWidget):
    """Abstract button interface"""
    
    def __init__(self, text: str = "") -> None:
        super().__init__()
        self._text = text
        self._clicked_callback: Optional[Callable[[], None]] = None
    
    @property
    def text(self) -> str:
        return self._text
    
    @text.setter
    def text(self, value: str) -> None:
        self._text = value
    
    def set_clicked_callback(self, callback: Callable[[], None]) -> None:
        """Set the callback for button clicks"""
        self._clicked_callback = callback
    
    def click(self) -> None:
        """Simulate a button click"""
        if self._clicked_callback:
            self._clicked_callback()
        self.emit_signal("clicked")
    
    def set_enabled_callback(self, callback: Callable[[], bool]) -> None:
        """Set a callback that determines if the button should be enabled"""
        self.set_state_callback("enabled", callback)
    
    def set_visible_callback(self, callback: Callable[[], bool]) -> None:
        """Set a callback that determines if the button should be visible"""
        self.set_state_callback("visible", callback)


class UITextInput(UIWidget):
    """Abstract text input interface"""
    
    def __init__(self, placeholder: str = "") -> None:
        super().__init__()
        self._text = ""
        self._placeholder = placeholder
    
    @property
    def text(self) -> str:
        return self._text
    
    @text.setter
    def text(self, value: str) -> None:
        self._text = value
    
    @property
    def placeholder(self) -> str:
        return self._placeholder
    
    @placeholder.setter
    def placeholder(self, value: str) -> None:
        self._placeholder = value
    
    def set_text_changed_callback(self, callback: Callable[[str], None]) -> None:
        """Set callback for text changes"""
        self.connect_signal("text_changed", callback)
    
    def set_text(self, text: str) -> None:
        """Set text and emit signal"""
        old_text = self._text
        self._text = text
        if old_text != text:
            self.emit_signal("text_changed", text)


class UIComboBox(UIWidget):
    """Abstract combo box interface"""
    
    def __init__(self) -> None:
        super().__init__()
        self._items: List[tuple[str, Any]] = []  # (text, data) pairs
        self._current_index = -1
    
    def add_item(self, text: str, data: Any = None) -> None:
        """Add an item to the combo box"""
        self._items.append((text, data))
    
    def clear(self) -> None:
        """Clear all items"""
        self._items.clear()
        self._current_index = -1
    
    def set_current_index(self, index: int) -> None:
        """Set the current selection"""
        if 0 <= index < len(self._items):
            self._current_index = index
            self.emit_signal("current_changed", self.current_data())
    
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
    
    def set_current_changed_callback(self, callback: Callable[[Any], None]) -> None:
        """Set callback for selection changes"""
        self.connect_signal("current_changed", callback)


class UIListWidget(UIWidget):
    """Abstract list widget interface"""
    
    def __init__(self) -> None:
        super().__init__()
        self._items: List[tuple[str, Any]] = []  # (text, data) pairs
        self._current_index = -1
    
    def add_item(self, text: str, data: Any = None) -> None:
        """Add an item to the list"""
        self._items.append((text, data))
    
    def clear(self) -> None:
        """Clear all items"""
        self._items.clear()
        self._current_index = -1
    
    def set_current_index(self, index: int) -> None:
        """Set the current selection"""
        if 0 <= index < len(self._items):
            self._current_index = index
            self.emit_signal("current_changed", self.current_data())
    
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
    
    def set_current_changed_callback(self, callback: Callable[[Any], None]) -> None:
        """Set callback for selection changes"""
        self.connect_signal("current_changed", callback)


class UICanvas(UIWidget):
    """Abstract canvas interface for image display and selection"""
    
    def __init__(self) -> None:
        super().__init__()
        self._pixmap = None
        self._zoom_factor = 1.0
        self._selection_rect = None
    
    def set_pixmap(self, pixmap: Any) -> None:
        """Set the image to display"""
        self._pixmap = pixmap
        self.emit_signal("pixmap_changed")
    
    def set_zoom(self, zoom_factor: float) -> None:
        """Set the zoom factor"""
        self._zoom_factor = zoom_factor
        self.emit_signal("zoom_changed")
    
    @property
    def zoom_factor(self) -> float:
        return self._zoom_factor
    
    @property
    def selection_rect(self) -> Optional[Any]:
        return self._selection_rect
    
    def set_selection_rect(self, rect: Any) -> None:
        """Set the selection rectangle"""
        self._selection_rect = rect
        self.emit_signal("selection_changed", rect)
    
    def clear_selection(self) -> None:
        """Clear the current selection"""
        self._selection_rect = None
        self.emit_signal("selection_changed", None)
    
    def set_selection_changed_callback(self, callback: Callable[[Any], None]) -> None:
        """Set callback for selection changes"""
        self.connect_signal("selection_changed", callback)


class UIDialog(ABC):
    """Abstract dialog interface"""
    
    @abstractmethod
    def exec(self) -> int:
        """Execute the dialog and return the result code"""
        pass
    
    @abstractmethod
    def get_data(self) -> Any:
        """Get the dialog data"""
        pass


class UIMessageBox(ABC):
    """Abstract message box interface"""
    
    @abstractmethod
    def show_info(self, title: str, message: str) -> None:
        """Show an info message"""
        pass
    
    @abstractmethod
    def show_warning(self, title: str, message: str) -> None:
        """Show a warning message"""
        pass
    
    @abstractmethod
    def show_error(self, title: str, message: str) -> None:
        """Show an error message"""
        pass
    
    @abstractmethod
    def show_question(self, title: str, message: str) -> bool:
        """Show a question dialog and return True if Yes was clicked"""
        pass


class UIFileDialog(ABC):
    """Abstract file dialog interface"""
    
    @abstractmethod
    def get_open_file_name(self, title: str, filter: str = "") -> Optional[str]:
        """Get a file name for opening"""
        pass
    
    @abstractmethod
    def get_save_file_name(self, title: str, filter: str = "") -> Optional[str]:
        """Get a file name for saving"""
        pass


class UIProgressBar(UIWidget):
    """Abstract progress bar interface"""
    
    def __init__(self) -> None:
        super().__init__()
        self._value = 0
        self._minimum = 0
        self._maximum = 100
    
    @property
    def value(self) -> int:
        return self._value
    
    @value.setter
    def value(self, value: int) -> None:
        self._value = max(self._minimum, min(value, self._maximum))
    
    @property
    def minimum(self) -> int:
        return self._minimum
    
    @minimum.setter
    def minimum(self, value: int) -> None:
        self._minimum = value
    
    @property
    def maximum(self) -> int:
        return self._maximum
    
    @maximum.setter
    def maximum(self, value: int) -> None:
        self._maximum = value


class UILayout(ABC):
    """Abstract layout interface"""
    
    @abstractmethod
    def add_widget(self, widget: UIWidget, *args: Any, **kwargs: Any) -> None:
        """Add a widget to the layout"""
        pass
    
    @abstractmethod
    def remove_widget(self, widget: UIWidget) -> None:
        """Remove a widget from the layout"""
        pass


class UIGroupBox(UIWidget):
    """Abstract group box interface"""
    
    def __init__(self, title: str = "") -> None:
        super().__init__()
        self._title = title
        self._layout: Optional[UILayout] = None
    
    @property
    def title(self) -> str:
        return self._title
    
    @title.setter
    def title(self, value: str) -> None:
        self._title = value
    
    def set_layout(self, layout: UILayout) -> None:
        """Set the layout for the group box"""
        self._layout = layout


class UITabWidget(UIWidget):
    """Abstract tab widget interface"""
    
    def __init__(self) -> None:
        super().__init__()
        self._tabs: List[tuple] = []  # (widget, title) pairs
        self._current_index = 0
    
    def add_tab(self, widget: UIWidget, title: str) -> None:
        """Add a tab"""
        self._tabs.append((widget, title))
    
    def set_current_index(self, index: int) -> None:
        """Set the current tab"""
        if 0 <= index < len(self._tabs):
            self._current_index = index
            self.emit_signal("current_changed", index)
    
    def current_index(self) -> int:
        """Get the current tab index"""
        return self._current_index
    
    def set_current_changed_callback(self, callback: Callable[[int], None]) -> None:
        """Set callback for tab changes"""
        self.connect_signal("current_changed", callback)


class UISplitter(UIWidget):
    """Abstract splitter interface"""
    
    def __init__(self, orientation: str = "horizontal") -> None:
        super().__init__()
        self._orientation = orientation
        self._widgets: List[UIWidget] = []
        self._sizes: List[int] = []
    
    def add_widget(self, widget: UIWidget) -> None:
        """Add a widget to the splitter"""
        self._widgets.append(widget)
        self._sizes.append(100)  # Default size
    
    def set_sizes(self, sizes: List[int]) -> None:
        """Set the sizes of the widgets"""
        if len(sizes) == len(self._widgets):
            self._sizes = sizes.copy()
    
    def get_sizes(self) -> List[int]:
        """Get the current sizes"""
        return self._sizes.copy()


class UIMenuBar(UIWidget):
    """Abstract base class for menu bars"""
    
    def __init__(self) -> None:
        super().__init__()
        self._menus: List['UIMenu'] = []
    
    def add_menu(self, menu: 'UIMenu') -> None:
        """Add a menu to the menu bar"""
        self._menus.append(menu)
    
    def get_menus(self) -> List['UIMenu']:
        """Get all menus in the menu bar"""
        return self._menus.copy()


class UIMenu(UIWidget):
    """Abstract base class for menus"""
    
    def __init__(self, title: str) -> None:
        super().__init__()
        self._title = title
        self._items: List['UIMenuItem'] = []
    
    @property
    def title(self) -> str:
        """Get the menu title"""
        return self._title
    
    def add_item(self, item: 'UIMenuItem') -> None:
        """Add a menu item to the menu"""
        self._items.append(item)
    
    def get_items(self) -> List['UIMenuItem']:
        """Get all menu items in the menu"""
        return self._items.copy()


class UIMenuItem(UIWidget):
    """Abstract base class for menu items"""
    
    def __init__(self, text: str) -> None:
        super().__init__()
        self._text = text
        self._clicked_callback: Optional[Callable[[], None]] = None
    
    @property
    def text(self) -> str:
        """Get the menu item text"""
        return self._text
    
    @text.setter
    def text(self, value: str) -> None:
        """Set the menu item text"""
        self._text = value
    
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
    
    def set_enabled_callback(self, callback: Callable[[], bool]) -> None:
        """Set a callback that determines if the menu item should be enabled"""
        self.set_state_callback("enabled", callback)
    
    def set_visible_callback(self, callback: Callable[[], bool]) -> None:
        """Set a callback that determines if the menu item should be visible"""
        self.set_state_callback("visible", callback)


class UIStatusBar(UIWidget):
    """Abstract base class for status bars"""
    
    def __init__(self) -> None:
        super().__init__()
        self._message = ""
    
    def set_message(self, message: str) -> None:
        """Set the status bar message"""
        self._message = message
        self.emit_signal("message_changed", message)
    
    def get_message(self) -> str:
        """Get the current status bar message"""
        return self._message
