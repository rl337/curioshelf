"""
Headless implementations of UI abstraction widgets

This module provides command-line implementations of all UI abstraction interfaces
that emit messages instead of rendering GUI components.
"""

from typing import Any, Optional, Callable, List
from pathlib import Path

from curioshelf.ui_abstraction import (
    UIWidget, UIButton, UITextInput, UIComboBox, UIListWidget, UICanvas,
    UIMessageBox, UIFileDialog, UIProgressBar, UIGroupBox, UITabWidget,
    UISplitter, UILayout
)


class HeadlessUIWidget(UIWidget):
    """Headless implementation of UIWidget"""
    
    def __init__(self, verbose: bool = True):
        super().__init__()
        self.verbose = verbose
    
    def _log(self, message: str):
        """Log a message if verbose mode is enabled"""
        if self.verbose:
            print(f"[HEADLESS] {message}")
    
    def set_enabled(self, enabled: bool):
        """Enable or disable the widget"""
        super().set_enabled(enabled)
        self._log(f"Widget {'enabled' if enabled else 'disabled'}")
    
    def set_visible(self, visible: bool):
        """Show or hide the widget"""
        super().set_visible(visible)
        self._log(f"Widget {'shown' if visible else 'hidden'}")


class HeadlessUIButton(UIButton):
    """Headless implementation of UIButton"""
    
    def __init__(self, text: str = "", verbose: bool = True):
        super().__init__(text)
        self.verbose = verbose
    
    def _log(self, message: str):
        """Log a message if verbose mode is enabled"""
        if self.verbose:
            print(f"[HEADLESS] {message}")
    
    def click(self):
        """Simulate a button click"""
        self._log(f"Button '{self._text}' clicked")
        super().click()
    
    def set_enabled(self, enabled: bool):
        """Enable or disable the button"""
        super().set_enabled(enabled)
        self._log(f"Button '{self._text}' {'enabled' if enabled else 'disabled'}")
    
    def set_visible(self, visible: bool):
        """Show or hide the button"""
        super().set_visible(visible)
        self._log(f"Button '{self._text}' {'shown' if visible else 'hidden'}")


class HeadlessUITextInput(UITextInput):
    """Headless implementation of UITextInput"""
    
    def __init__(self, placeholder: str = "", verbose: bool = True):
        super().__init__(placeholder)
        self.verbose = verbose
    
    def _log(self, message: str):
        """Log a message if verbose mode is enabled"""
        if self.verbose:
            print(f"[HEADLESS] {message}")
    
    def set_text(self, text: str):
        """Set text and emit signal"""
        old_text = self._text
        super().set_text(text)
        if old_text != text:
            self._log(f"Text input changed: '{old_text}' -> '{text}'")
    
    def set_enabled(self, enabled: bool):
        """Enable or disable the input"""
        super().set_enabled(enabled)
        self._log(f"Text input {'enabled' if enabled else 'disabled'}")
    
    def set_visible(self, visible: bool):
        """Show or hide the input"""
        super().set_visible(visible)
        self._log(f"Text input {'shown' if visible else 'hidden'}")


class HeadlessUIComboBox(UIComboBox):
    """Headless implementation of UIComboBox"""
    
    def __init__(self, verbose: bool = True):
        super().__init__()
        self.verbose = verbose
    
    def _log(self, message: str):
        """Log a message if verbose mode is enabled"""
        if self.verbose:
            print(f"[HEADLESS] {message}")
    
    def add_item(self, text: str, data: Any = None):
        """Add an item to the combo box"""
        super().add_item(text, data)
        self._log(f"Combo box item added: '{text}'")
    
    def clear(self):
        """Clear all items"""
        super().clear()
        self._log("Combo box cleared")
    
    def set_current_index(self, index: int):
        """Set the current selection"""
        old_index = self._current_index
        super().set_current_index(index)
        if old_index != index:
            text = self.current_text()
            self._log(f"Combo box selection changed to index {index}: '{text}'")
    
    def set_enabled(self, enabled: bool):
        """Enable or disable the combo box"""
        super().set_enabled(enabled)
        self._log(f"Combo box {'enabled' if enabled else 'disabled'}")
    
    def set_visible(self, visible: bool):
        """Show or hide the combo box"""
        super().set_visible(visible)
        self._log(f"Combo box {'shown' if visible else 'hidden'}")


class HeadlessUIListWidget(UIListWidget):
    """Headless implementation of UIListWidget"""
    
    def __init__(self, verbose: bool = True):
        super().__init__()
        self.verbose = verbose
    
    def _log(self, message: str):
        """Log a message if verbose mode is enabled"""
        if self.verbose:
            print(f"[HEADLESS] {message}")
    
    def add_item(self, text: str, data: Any = None):
        """Add an item to the list"""
        super().add_item(text, data)
        self._log(f"List item added: '{text}'")
    
    def clear(self):
        """Clear all items"""
        super().clear()
        self._log("List cleared")
    
    def set_current_index(self, index: int):
        """Set the current selection"""
        old_index = self._current_index
        super().set_current_index(index)
        if old_index != index:
            text = self.current_text()
            self._log(f"List selection changed to index {index}: '{text}'")
    
    def set_enabled(self, enabled: bool):
        """Enable or disable the list"""
        super().set_enabled(enabled)
        self._log(f"List {'enabled' if enabled else 'disabled'}")
    
    def set_visible(self, visible: bool):
        """Show or hide the list"""
        super().set_visible(visible)
        self._log(f"List {'shown' if visible else 'hidden'}")


class HeadlessUICanvas(UICanvas):
    """Headless implementation of UICanvas"""
    
    def __init__(self, verbose: bool = True):
        super().__init__()
        self.verbose = verbose
    
    def _log(self, message: str):
        """Log a message if verbose mode is enabled"""
        if self.verbose:
            print(f"[HEADLESS] {message}")
    
    def set_pixmap(self, pixmap: Any):
        """Set the image to display"""
        super().set_pixmap(pixmap)
        if hasattr(pixmap, 'width') and hasattr(pixmap, 'height'):
            self._log(f"Canvas pixmap set: {pixmap.width}x{pixmap.height}")
        else:
            self._log(f"Canvas pixmap set: {pixmap}")
    
    def set_zoom(self, zoom_factor: float):
        """Set the zoom factor"""
        super().set_zoom(zoom_factor)
        self._log(f"Canvas zoom set to: {zoom_factor}")
    
    def set_selection_rect(self, rect: Any):
        """Set the selection rectangle"""
        super().set_selection_rect(rect)
        if rect:
            self._log(f"Canvas selection set: {rect}")
        else:
            self._log("Canvas selection cleared")
    
    def clear_selection(self):
        """Clear the current selection"""
        super().clear_selection()
        self._log("Canvas selection cleared")
    
    def set_enabled(self, enabled: bool):
        """Enable or disable the canvas"""
        super().set_enabled(enabled)
        self._log(f"Canvas {'enabled' if enabled else 'disabled'}")
    
    def set_visible(self, visible: bool):
        """Show or hide the canvas"""
        super().set_visible(visible)
        self._log(f"Canvas {'shown' if visible else 'hidden'}")


class HeadlessUIMessageBox(UIMessageBox):
    """Headless implementation of UIMessageBox"""
    
    def __init__(self, verbose: bool = True):
        self.verbose = verbose
    
    def _log(self, message: str):
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


class HeadlessUIFileDialog(UIFileDialog):
    """Headless implementation of UIFileDialog"""
    
    def __init__(self, verbose: bool = True):
        self.verbose = verbose
    
    def _log(self, message: str):
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


class HeadlessUIProgressBar(UIProgressBar):
    """Headless implementation of UIProgressBar"""
    
    def __init__(self, verbose: bool = True):
        super().__init__()
        self.verbose = verbose
    
    def _log(self, message: str):
        """Log a message if verbose mode is enabled"""
        if self.verbose:
            print(f"[HEADLESS] {message}")
    
    @property
    def value(self) -> int:
        return self._value
    
    @value.setter
    def value(self, value: int):
        old_value = self._value
        self._value = max(self._minimum, min(value, self._maximum))
        if old_value != self._value:
            self._log(f"Progress bar: {self._value}%")
    
    def set_enabled(self, enabled: bool):
        """Enable or disable the progress bar"""
        super().set_enabled(enabled)
        self._log(f"Progress bar {'enabled' if enabled else 'disabled'}")
    
    def set_visible(self, visible: bool):
        """Show or hide the progress bar"""
        super().set_visible(visible)
        self._log(f"Progress bar {'shown' if visible else 'hidden'}")


class HeadlessUIGroupBox(UIGroupBox):
    """Headless implementation of UIGroupBox"""
    
    def __init__(self, title: str = "", verbose: bool = True):
        super().__init__(title)
        self.verbose = verbose
    
    def _log(self, message: str):
        """Log a message if verbose mode is enabled"""
        if self.verbose:
            print(f"[HEADLESS] {message}")
    
    def set_enabled(self, enabled: bool):
        """Enable or disable the group box"""
        super().set_enabled(enabled)
        self._log(f"Group box '{self._title}' {'enabled' if enabled else 'disabled'}")
    
    def set_visible(self, visible: bool):
        """Show or hide the group box"""
        super().set_visible(visible)
        self._log(f"Group box '{self._title}' {'shown' if visible else 'hidden'}")


class HeadlessUITabWidget(UITabWidget):
    """Headless implementation of UITabWidget"""
    
    def __init__(self, verbose: bool = True):
        super().__init__()
        self.verbose = verbose
    
    def _log(self, message: str):
        """Log a message if verbose mode is enabled"""
        if self.verbose:
            print(f"[HEADLESS] {message}")
    
    def add_tab(self, widget: UIWidget, title: str):
        """Add a tab"""
        super().add_tab(widget, title)
        self._log(f"Tab added: '{title}'")
    
    def set_current_index(self, index: int):
        """Set the current tab"""
        old_index = self._current_index
        super().set_current_index(index)
        if old_index != index and 0 <= index < len(self._tabs):
            title = self._tabs[index][1]
            self._log(f"Tab changed to index {index}: '{title}'")
    
    def set_enabled(self, enabled: bool):
        """Enable or disable the tab widget"""
        super().set_enabled(enabled)
        self._log(f"Tab widget {'enabled' if enabled else 'disabled'}")
    
    def set_visible(self, visible: bool):
        """Show or hide the tab widget"""
        super().set_visible(visible)
        self._log(f"Tab widget {'shown' if visible else 'hidden'}")


class HeadlessUISplitter(UISplitter):
    """Headless implementation of UISplitter"""
    
    def __init__(self, orientation: str = "horizontal", verbose: bool = True):
        super().__init__(orientation)
        self.verbose = verbose
    
    def _log(self, message: str):
        """Log a message if verbose mode is enabled"""
        if self.verbose:
            print(f"[HEADLESS] {message}")
    
    def add_widget(self, widget: UIWidget):
        """Add a widget to the splitter"""
        super().add_widget(widget)
        self._log(f"Widget added to {self._orientation} splitter")
    
    def set_sizes(self, sizes: List[int]):
        """Set the sizes of the widgets"""
        super().set_sizes(sizes)
        self._log(f"Splitter sizes set: {sizes}")
    
    def set_enabled(self, enabled: bool):
        """Enable or disable the splitter"""
        super().set_enabled(enabled)
        self._log(f"Splitter {'enabled' if enabled else 'disabled'}")
    
    def set_visible(self, visible: bool):
        """Show or hide the splitter"""
        super().set_visible(visible)
        self._log(f"Splitter {'shown' if visible else 'hidden'}")


class HeadlessUILayout(UILayout):
    """Headless implementation of UILayout"""
    
    def __init__(self, orientation: str = "vertical", verbose: bool = True):
        self._orientation = orientation
        self.verbose = verbose
    
    def _log(self, message: str):
        """Log a message if verbose mode is enabled"""
        if self.verbose:
            print(f"[HEADLESS] {message}")
    
    def add_widget(self, widget: UIWidget, *args, **kwargs):
        """Add a widget to the layout"""
        self._log(f"Widget added to {self._orientation} layout")
    
    def remove_widget(self, widget: UIWidget):
        """Remove a widget from the layout"""
        self._log(f"Widget removed from {self._orientation} layout")
