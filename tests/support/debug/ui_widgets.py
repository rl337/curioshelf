"""
Headless implementations of UI abstraction widgets

This module provides command-line implementations of all UI abstraction interfaces
that emit messages instead of rendering GUI components.
"""

from typing import Any, Optional, Callable, List
from pathlib import Path

from curioshelf.ui.abstraction import (
    UIWidget, UIButton, UITextInput, UIComboBox, UIListWidget, UICanvas,
    UIMessageBox, UIFileDialog, UIProgressBar, UIGroupBox, UITabWidget,
    UISplitter, UILayout, UIMenuBar, UIMenu, UIMenuItem, UIStatusBar
)
from .message_system import MessageLogger, MessageType


class DebugUIWidget(UIWidget):
    """Headless implementation of UIWidget"""
    
    def __init__(self, verbose: bool = True, message_logger: Optional[MessageLogger] = None) -> None:
        super().__init__()
        self.verbose = verbose
        self.message_logger = message_logger or MessageLogger(collect_messages=True, print_messages=verbose)
    
    def _log_ui_event(self, action: str, data: Optional[dict] = None) -> None:
        """Log a UI event"""
        self.message_logger.log_ui_event(self.__class__.__name__, action, data)
    
    def _log_state_change(self, action: str, data: Optional[dict] = None) -> None:
        """Log a state change"""
        self.message_logger.log_state_change(self.__class__.__name__, action, data)
    
    def set_enabled(self, enabled: bool) -> None:
        """Enable or disable the widget"""
        super().set_enabled(enabled)
        self._log_state_change(f"{'enabled' if enabled else 'disabled'}")
    
    def set_visible(self, visible: bool) -> None:
        """Show or hide the widget"""
        super().set_visible(visible)
        self._log_state_change(f"{'shown' if visible else 'hidden'}")
    
    def show(self) -> None:
        """Show the widget"""
        super().show()
        self._log_ui_event("shown")


class DebugUIButton(UIButton):
    """Headless implementation of UIButton"""
    
    def __init__(self, text: str = "", verbose: bool = True, message_logger: Optional[MessageLogger] = None) -> None:
        super().__init__(text)
        self.verbose = verbose
        self.message_logger = message_logger or MessageLogger(collect_messages=True, print_messages=verbose)
    
    def click(self) -> None:
        """Simulate a button click"""
        self.message_logger.log_user_action(self.__class__.__name__, "clicked", {"text": self._text})
        super().click()
    
    def set_enabled(self, enabled: bool) -> None:
        """Enable or disable the button"""
        super().set_enabled(enabled)
        self.message_logger.log_state_change(self.__class__.__name__, f"{'enabled' if enabled else 'disabled'}", {"text": self._text})
    
    def set_visible(self, visible: bool) -> None:
        """Show or hide the button"""
        super().set_visible(visible)
        self.message_logger.log_state_change(self.__class__.__name__, f"{'shown' if visible else 'hidden'}", {"text": self._text})


class DebugUITextInput(UITextInput):
    """Headless implementation of UITextInput"""
    
    def __init__(self, placeholder: str = "", verbose: bool = True, message_logger: Optional[MessageLogger] = None) -> None:
        super().__init__(placeholder)
        self.verbose = verbose
        self.message_logger = message_logger or MessageLogger(collect_messages=True, print_messages=verbose)
    
    def set_text(self, text: str) -> None:
        """Set text and emit signal"""
        old_text = self._text
        super().set_text(text)
        if old_text != text:
            self.message_logger.log_ui_event(self.__class__.__name__, "text_changed", {
                "old_text": old_text,
                "new_text": text,
                "placeholder": self._placeholder
            })
    
    def set_enabled(self, enabled: bool) -> None:
        """Enable or disable the input"""
        super().set_enabled(enabled)
        self.message_logger.log_state_change(self.__class__.__name__, f"{'enabled' if enabled else 'disabled'}", {
            "placeholder": self._placeholder
        })
    
    def set_visible(self, visible: bool) -> None:
        """Show or hide the input"""
        super().set_visible(visible)
        self.message_logger.log_state_change(self.__class__.__name__, f"{'shown' if visible else 'hidden'}", {
            "placeholder": self._placeholder
        })


class DebugUIComboBox(UIComboBox):
    """Headless implementation of UIComboBox"""
    
    def __init__(self, verbose: bool = True, message_logger: Optional[MessageLogger] = None) -> None:
        super().__init__()
        self.verbose = verbose
        self.message_logger = message_logger or MessageLogger(collect_messages=True, print_messages=verbose)
    
    def _log(self, message: str) -> None:
        """Log a message if verbose mode is enabled"""
        if self.verbose:
            print(f"[HEADLESS] {message}")
    
    def add_item(self, text: str, data: Any = None) -> None:
        """Add an item to the combo box"""
        super().add_item(text, data)
        self._log(f"Combo box item added: '{text}'")
        self.message_logger.log_ui_event(self.__class__.__name__, "item_added", {"text": text, "data": data})
    
    def clear(self) -> None:
        """Clear all items"""
        super().clear()
        self._log("Combo box cleared")
    
    def set_current_index(self, index: int) -> None:
        """Set the current selection"""
        old_index = self._current_index
        super().set_current_index(index)
        if old_index != index:
            text = self.current_text()
            self._log(f"Combo box selection changed to index {index}: '{text}'")
            self.message_logger.log_ui_event(self.__class__.__name__, "current_changed", {"index": index, "text": text})
    
    def set_enabled(self, enabled: bool) -> None:
        """Enable or disable the combo box"""
        super().set_enabled(enabled)
        self._log(f"Combo box {'enabled' if enabled else 'disabled'}")
        self.message_logger.log_state_change(self.__class__.__name__, "enabled" if enabled else "disabled")
    
    def set_visible(self, visible: bool) -> None:
        """Show or hide the combo box"""
        super().set_visible(visible)
        self._log(f"Combo box {'shown' if visible else 'hidden'}")


class DebugUIListWidget(UIListWidget):
    """Headless implementation of UIListWidget"""
    
    def __init__(self, verbose: bool = True, message_logger: Optional[MessageLogger] = None) -> None:
        super().__init__()
        self.verbose = verbose
        self.message_logger = message_logger or MessageLogger(collect_messages=True, print_messages=verbose)
    
    def _log(self, message: str) -> None:
        """Log a message if verbose mode is enabled"""
        if self.verbose:
            print(f"[HEADLESS] {message}")
    
    def add_item(self, text: str, data: Any = None) -> None:
        """Add an item to the list"""
        super().add_item(text, data)
        self._log(f"List item added: '{text}'")
        self.message_logger.log_ui_event(self.__class__.__name__, "item_added", {"text": text, "data": data})
    
    def clear(self) -> None:
        """Clear all items"""
        super().clear()
        self._log("List cleared")
    
    def set_current_index(self, index: int) -> None:
        """Set the current selection"""
        old_index = self._current_index
        super().set_current_index(index)
        if old_index != index:
            text = self.current_text()
            self._log(f"List selection changed to index {index}: '{text}'")
            self.message_logger.log_ui_event(self.__class__.__name__, "current_changed", {"index": index, "text": text})
    
    def set_enabled(self, enabled: bool) -> None:
        """Enable or disable the list"""
        super().set_enabled(enabled)
        self._log(f"List {'enabled' if enabled else 'disabled'}")
        self.message_logger.log_state_change(self.__class__.__name__, "enabled" if enabled else "disabled")
    
    def set_visible(self, visible: bool) -> None:
        """Show or hide the list"""
        super().set_visible(visible)
        self._log(f"List {'shown' if visible else 'hidden'}")


class DebugUICanvas(UICanvas):
    """Headless implementation of UICanvas"""
    
    def __init__(self, verbose: bool = True, message_logger: Optional[MessageLogger] = None) -> None:
        super().__init__()
        self.verbose = verbose
        self.message_logger = message_logger or MessageLogger(collect_messages=True, print_messages=verbose)
    
    def _log(self, message: str) -> None:
        """Log a message if verbose mode is enabled"""
        if self.verbose:
            print(f"[HEADLESS] {message}")
    
    def set_pixmap(self, pixmap: Any) -> None:
        """Set the image to display"""
        super().set_pixmap(pixmap)
        if hasattr(pixmap, 'width') and hasattr(pixmap, 'height'):
            self._log(f"Canvas pixmap set: {pixmap.width}x{pixmap.height}")
        else:
            self._log(f"Canvas pixmap set: {pixmap}")
    
    def set_zoom(self, zoom_factor: float) -> None:
        """Set the zoom factor"""
        super().set_zoom(zoom_factor)
        self._log(f"Canvas zoom set to: {zoom_factor}")
    
    def set_selection_rect(self, rect: Any) -> None:
        """Set the selection rectangle"""
        super().set_selection_rect(rect)
        if rect:
            self._log(f"Canvas selection set: {rect}")
        else:
            self._log("Canvas selection cleared")
    
    def clear_selection(self) -> None:
        """Clear the current selection"""
        super().clear_selection()
        self._log("Canvas selection cleared")
    
    def set_enabled(self, enabled: bool) -> None:
        """Enable or disable the canvas"""
        super().set_enabled(enabled)
        self._log(f"Canvas {'enabled' if enabled else 'disabled'}")
    
    def set_visible(self, visible: bool) -> None:
        """Show or hide the canvas"""
        super().set_visible(visible)
        self._log(f"Canvas {'shown' if visible else 'hidden'}")


class DebugUIMessageBox(UIMessageBox):
    """Headless implementation of UIMessageBox"""
    
    def __init__(self, verbose: bool = True, message_logger: Optional[MessageLogger] = None) -> None:
        self.verbose = verbose
        self.message_logger = message_logger or MessageLogger(collect_messages=True, print_messages=verbose)
    
    def _log(self, message: str) -> None:
        """Log a message if verbose mode is enabled"""
        if self.verbose:
            print(f"[HEADLESS] {message}")
    
    def show_info(self, title: str, message: str) -> None:
        """Show an info message"""
        self._log(f"INFO: {title} - {message}")
    
    def show_warning(self, title: str, message: str) -> None:
        """Show a warning message"""
        self._log(f"WARNING: {title} - {message}")
    
    def show_error(self, title: str, message: str) -> None:
        """Show an error message"""
        self._log(f"ERROR: {title} - {message}")
    
    def show_question(self, title: str, message: str) -> bool:
        """Show a question dialog and return True if Yes was clicked"""
        self._log(f"QUESTION: {title} - {message}")
        # For testing, always return True
        return True


class DebugUIFileDialog(UIFileDialog):
    """Headless implementation of UIFileDialog"""
    
    def __init__(self, verbose: bool = True, message_logger: Optional[MessageLogger] = None) -> None:
        self.verbose = verbose
        self.message_logger = message_logger or MessageLogger(collect_messages=True, print_messages=verbose)
    
    def _log(self, message: str) -> None:
        """Log a message if verbose mode is enabled"""
        if self.verbose:
            print(f"[HEADLESS] {message}")
    
    def get_open_file_name(self, title: str, filter: str = "") -> Optional[str]:
        """Get a file name for opening"""
        self._log(f"FILE DIALOG OPEN: {title} (filter: {filter})")
        # For testing, return a mock file path
        return "/mock/path/to/file.png"
    
    def get_save_file_name(self, title: str, filter: str = "") -> Optional[str]:
        """Get a file name for saving"""
        self._log(f"FILE DIALOG SAVE: {title} (filter: {filter})")
        # For testing, return a mock file path
        return "/mock/path/to/save/file.json"


class DebugUIProgressBar(UIProgressBar):
    """Headless implementation of UIProgressBar"""
    
    def __init__(self, verbose: bool = True, message_logger: Optional[MessageLogger] = None) -> None:
        super().__init__()
        self.verbose = verbose
        self.message_logger = message_logger or MessageLogger(collect_messages=True, print_messages=verbose)
    
    def _log(self, message: str) -> None:
        """Log a message if verbose mode is enabled"""
        if self.verbose:
            print(f"[HEADLESS] {message}")
    
    @property
    def value(self) -> int:
        return self._value
    
    @value.setter
    def value(self, value: int) -> None:
        old_value = self._value
        self._value = max(self._minimum, min(value, self._maximum))
        if old_value != self._value:
            self._log(f"Progress bar: {self._value}%")
            self.message_logger.log_ui_event(self.__class__.__name__, "value_changed", {"value": self._value})
    
    def set_enabled(self, enabled: bool) -> None:
        """Enable or disable the progress bar"""
        super().set_enabled(enabled)
        self._log(f"Progress bar {'enabled' if enabled else 'disabled'}")
        self.message_logger.log_state_change(self.__class__.__name__, "enabled" if enabled else "disabled")
    
    def set_visible(self, visible: bool) -> None:
        """Show or hide the progress bar"""
        super().set_visible(visible)
        self._log(f"Progress bar {'shown' if visible else 'hidden'}")
    
    def set_value(self, value: int) -> None:
        """Set the progress bar value"""
        self.value = value


class DebugUIGroupBox(UIGroupBox):
    """Headless implementation of UIGroupBox"""
    
    def __init__(self, title: str = "", verbose: bool = True, message_logger: Optional[MessageLogger] = None) -> None:
        super().__init__(title)
        self.verbose = verbose
        self.message_logger = message_logger or MessageLogger(collect_messages=True, print_messages=verbose)
    
    def _log(self, message: str) -> None:
        """Log a message if verbose mode is enabled"""
        if self.verbose:
            print(f"[HEADLESS] {message}")
    
    def set_enabled(self, enabled: bool) -> None:
        """Enable or disable the group box"""
        super().set_enabled(enabled)
        self._log(f"Group box '{self._title}' {'enabled' if enabled else 'disabled'}")
    
    def set_visible(self, visible: bool) -> None:
        """Show or hide the group box"""
        super().set_visible(visible)
        self._log(f"Group box '{self._title}' {'shown' if visible else 'hidden'}")


class DebugUITabWidget(UITabWidget):
    """Headless implementation of UITabWidget"""
    
    def __init__(self, verbose: bool = True, message_logger: Optional[MessageLogger] = None) -> None:
        super().__init__()
        self.verbose = verbose
        self.message_logger = message_logger or MessageLogger(collect_messages=True, print_messages=verbose)
    
    def _log(self, message: str) -> None:
        """Log a message if verbose mode is enabled"""
        if self.verbose:
            print(f"[HEADLESS] {message}")
    
    def add_tab(self, widget: UIWidget, title: str) -> None:
        """Add a tab"""
        super().add_tab(widget, title)
        self._log(f"Tab added: '{title}'")
    
    def set_current_index(self, index: int) -> None:
        """Set the current tab"""
        old_index = self._current_index
        super().set_current_index(index)
        if old_index != index and 0 <= index < len(self._tabs):
            title = self._tabs[index][1]
            self._log(f"Tab changed to index {index}: '{title}'")
    
    def set_enabled(self, enabled: bool) -> None:
        """Enable or disable the tab widget"""
        super().set_enabled(enabled)
        self._log(f"Tab widget {'enabled' if enabled else 'disabled'}")
    
    def set_visible(self, visible: bool) -> None:
        """Show or hide the tab widget"""
        super().set_visible(visible)
        self._log(f"Tab widget {'shown' if visible else 'hidden'}")


class DebugUISplitter(UISplitter):
    """Headless implementation of UISplitter"""
    
    def __init__(self, orientation: str = "horizontal", verbose: bool = True, message_logger: Optional[MessageLogger] = None) -> None:
        super().__init__(orientation)
        self.verbose = verbose
        self.message_logger = message_logger or MessageLogger(collect_messages=True, print_messages=verbose)
    
    def _log(self, message: str) -> None:
        """Log a message if verbose mode is enabled"""
        if self.verbose:
            print(f"[HEADLESS] {message}")
    
    def add_widget(self, widget: UIWidget) -> None:
        """Add a widget to the splitter"""
        super().add_widget(widget)
        self._log(f"Widget added to {self._orientation} splitter")
    
    def set_sizes(self, sizes: List[int]) -> None:
        """Set the sizes of the widgets"""
        super().set_sizes(sizes)
        self._log(f"Splitter sizes set: {sizes}")
    
    def set_enabled(self, enabled: bool) -> None:
        """Enable or disable the splitter"""
        super().set_enabled(enabled)
        self._log(f"Splitter {'enabled' if enabled else 'disabled'}")
    
    def set_visible(self, visible: bool) -> None:
        """Show or hide the splitter"""
        super().set_visible(visible)
        self._log(f"Splitter {'shown' if visible else 'hidden'}")


class DebugUILayout(UILayout):
    """Headless implementation of UILayout"""
    
    def __init__(self, orientation: str = "vertical", verbose: bool = True, message_logger: Optional[MessageLogger] = None) -> None:
        self._orientation = orientation
        self.verbose = verbose
        self.message_logger = message_logger or MessageLogger(collect_messages=True, print_messages=verbose)
        self._widgets: List[UIWidget] = []
    
    def _log_ui_event(self, action: str, data: Optional[dict] = None) -> None:
        """Log a UI event"""
        self.message_logger.log_ui_event(self.__class__.__name__, action, data)
    
    def add_widget(self, widget: UIWidget, *args: Any, **kwargs: Any) -> None:
        """Add a widget to the layout"""
        self._widgets.append(widget)
        self._log_ui_event("widget_added", {
            "orientation": self._orientation,
            "widget_type": widget.__class__.__name__
        })
    
    def remove_widget(self, widget: UIWidget) -> None:
        """Remove a widget from the layout"""
        if widget in self._widgets:
            self._widgets.remove(widget)
        self._log_ui_event("widget_removed", {
            "orientation": self._orientation,
            "widget_type": widget.__class__.__name__
        })


class DebugUIMenuBar(UIWidget):
    """Headless implementation of UIMenuBar"""
    
    def __init__(self, message_logger: Optional[MessageLogger] = None) -> None:
        super().__init__()
        self.message_logger = message_logger or MessageLogger(collect_messages=True, print_messages=True)
        self._menus = []
    
    def add_menu(self, menu: 'UIMenu') -> None:
        """Add a menu to the menu bar"""
        self._menus.append(menu)
        self.message_logger.log_ui_event("DebugUIMenuBar", "menu_added", {
            "menu_name": getattr(menu, 'name', 'Unknown')
        })
    
    def show(self) -> None:
        """Show the menu bar"""
        super().show()
        self.message_logger.log_ui_event("DebugUIMenuBar", "shown")


class DebugUIMenu(UIWidget):
    """Headless implementation of UIMenu"""
    
    def __init__(self, message_logger: Optional[MessageLogger] = None) -> None:
        super().__init__()
        self.message_logger = message_logger or MessageLogger(collect_messages=True, print_messages=True)
        self.name = ""
        self._items = []
    
    def set_title(self, title: str) -> None:
        """Set the menu title"""
        self.name = title
        self.message_logger.log_ui_event("DebugUIMenu", "title_set", {"title": title})
    
    def add_item(self, item: 'UIMenuItem') -> None:
        """Add an item to the menu"""
        self._items.append(item)
        self.message_logger.log_ui_event("DebugUIMenu", "item_added", {
            "item_text": getattr(item, 'text', 'Unknown')
        })
    
    def show(self) -> None:
        """Show the menu"""
        super().show()
        self.message_logger.log_ui_event("DebugUIMenu", "shown", {"name": self.name})


class DebugUIMenuItem(UIMenuItem):
    """Headless implementation of UIMenuItem"""
    
    def __init__(self, text: str = "", parent: Optional[Any] = None, message_logger: Optional[MessageLogger] = None) -> None:
        super().__init__(text)
        self.message_logger = message_logger or MessageLogger(collect_messages=True, print_messages=True)
        self._clicked_callback: Optional[Callable] = None
    
    def set_text(self, text: str) -> None:
        """Set the menu item text"""
        self.text = text
        self.message_logger.log_ui_event("DebugUIMenuItem", "text_set", {"text": text})
    
    def set_clicked_callback(self, callback: Callable) -> None:
        """Set the clicked callback"""
        super().set_clicked_callback(callback)
        self.message_logger.log_ui_event("DebugUIMenuItem", "callback_set", {"text": self.text})
    
    def set_enabled(self, enabled: bool) -> None:
        """Enable or disable the menu item"""
        super().set_enabled(enabled)
        self.message_logger.log_state_change("DebugUIMenuItem", f"{'enabled' if enabled else 'disabled'}", {
            "text": self.text
        })
    
    def show(self) -> None:
        """Show the menu item"""
        super().show()
        self.message_logger.log_ui_event("DebugUIMenuItem", "shown", {"text": self.text})
    
    def update_state(self, state_name: str) -> None:
        """Update the menu item state based on the callback for the given state name"""
        super().update_state(state_name)
        # Log the state change in headless mode
        if state_name == "enabled":
            self.message_logger.log_state_change("DebugUIMenuItem", f"enabled_{self.enabled}", {
                "text": self.text,
                "enabled": self.enabled
            })
        elif state_name == "visible":
            self.message_logger.log_state_change("DebugUIMenuItem", f"visible_{self.visible}", {
                "text": self.text,
                "visible": self.visible
            })


class DebugUIStatusBar(UIWidget):
    """Headless implementation of UIStatusBar"""
    
    def __init__(self, message_logger: Optional[MessageLogger] = None) -> None:
        super().__init__()
        self.message_logger = message_logger or MessageLogger(collect_messages=True, print_messages=True)
        self._message = ""
    
    def set_message(self, message: str) -> None:
        """Set the status bar message"""
        self._message = message
        self.message_logger.log_ui_event("DebugUIStatusBar", "message_set", {"message": message})
    
    def get_message(self) -> str:
        """Get the current status bar message"""
        return self._message
    
    def show(self) -> None:
        """Show the status bar"""
        super().show()
        self.message_logger.log_ui_event("DebugUIStatusBar", "shown", {"message": self._message})
