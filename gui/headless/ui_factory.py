"""
Headless UI Factory for creating command-line UI components

This factory creates headless implementations of the UI abstraction layer
that emit messages instead of rendering GUI components.
"""

from typing import Any, Optional, Dict, List
from pathlib import Path

from curioshelf.ui_abstraction import (
    UIWidget, UIButton, UITextInput, UIComboBox, UIListWidget, UICanvas,
    UIMessageBox, UIFileDialog, UIProgressBar, UIGroupBox, UITabWidget,
    UISplitter, UILayout
)
from .ui_widgets import (
    HeadlessUIWidget, HeadlessUIButton, HeadlessUITextInput, HeadlessUIComboBox, 
    HeadlessUIListWidget, HeadlessUICanvas, HeadlessUIMessageBox, HeadlessUIFileDialog, 
    HeadlessUIProgressBar, HeadlessUIGroupBox, HeadlessUITabWidget, HeadlessUISplitter,
    HeadlessUILayout
)
from gui.ui_interface import UIImplementationInterface, UIImplementationError


class HeadlessUIImplementation(UIImplementationInterface):
    """Headless implementation of the UI interface for testing"""
    
    def __init__(self, verbose: bool = True):
        super().__init__(verbose)
        self._pixmap_counter = 0
        self._style = {}
        self._running = False
    
    def initialize(self) -> bool:
        """Initialize the headless UI implementation"""
        self._initialized = True
        if self.verbose:
            print("[HEADLESS] UI implementation initialized")
        return True
    
    def cleanup(self) -> bool:
        """Cleanup the headless UI implementation"""
        self._initialized = False
        self._running = False
        if self.verbose:
            print("[HEADLESS] UI implementation cleaned up")
        return True
    
    def is_initialized(self) -> bool:
        """Check if headless is initialized"""
        return self._initialized
    
    def run_event_loop(self) -> int:
        """Run the headless event loop (just wait)"""
        if not self.is_initialized():
            self.initialize()
        
        self._running = True
        if self.verbose:
            print("[HEADLESS] Event loop started (headless mode)")
        
        # In headless mode, we just return immediately
        return 0
    
    def quit_event_loop(self) -> None:
        """Quit the headless event loop"""
        self._running = False
        if self.verbose:
            print("[HEADLESS] Event loop quit")
    
    def set_global_style(self, style: Dict[str, Any]) -> None:
        """Set global headless styling (just store it)"""
        self._style = style
        if self.verbose:
            print(f"[HEADLESS] Style set: {style}")
    
    def get_screen_size(self) -> tuple[int, int]:
        """Get mock screen size"""
        return (1920, 1080)  # Default screen size
    
    def get_dpi_scale(self) -> float:
        """Get mock DPI scale"""
        return 1.0
    
    def handle_error(self, error: Exception, context: str = "") -> None:
        """Handle headless errors"""
        error_msg = f"Headless UI Error: {str(error)}"
        if self.verbose:
            print(f"[HEADLESS ERROR] {error_msg} (Context: {context})")
        raise UIImplementationError(error_msg, "headless", context)
    
    def _log(self, message: str):
        """Log a message if verbose mode is enabled"""
        if self.verbose:
            print(f"[HEADLESS] {message}")
    
    def create_widget(self) -> 'HeadlessUIWidget':
        """Create a basic widget"""
        return HeadlessUIWidget()
    
    def create_button(self, text: str = "") -> 'HeadlessUIButton':
        """Create a button"""
        return HeadlessUIButton(text, self.verbose)
    
    def create_text_input(self, placeholder: str = "") -> 'HeadlessUITextInput':
        """Create a text input"""
        return HeadlessUITextInput(placeholder, self.verbose)
    
    def create_combo_box(self) -> 'HeadlessUIComboBox':
        """Create a combo box"""
        return HeadlessUIComboBox(self.verbose)
    
    def create_list_widget(self) -> 'HeadlessUIListWidget':
        """Create a list widget"""
        return HeadlessUIListWidget(self.verbose)
    
    def create_canvas(self) -> 'HeadlessUICanvas':
        """Create a canvas widget"""
        return HeadlessUICanvas(self.verbose)
    
    def create_message_box(self) -> 'HeadlessUIMessageBox':
        """Create a message box"""
        return HeadlessUIMessageBox(self.verbose)
    
    def create_file_dialog(self) -> 'HeadlessUIFileDialog':
        """Create a file dialog"""
        return HeadlessUIFileDialog(self.verbose)
    
    def create_progress_bar(self) -> 'HeadlessUIProgressBar':
        """Create a progress bar"""
        return HeadlessUIProgressBar(self.verbose)
    
    def create_group_box(self, title: str = "") -> 'HeadlessUIGroupBox':
        """Create a group box"""
        return HeadlessUIGroupBox(title, self.verbose)
    
    def create_tab_widget(self) -> 'HeadlessUITabWidget':
        """Create a tab widget"""
        return HeadlessUITabWidget(self.verbose)
    
    def create_splitter(self, orientation: str = "horizontal") -> 'HeadlessUISplitter':
        """Create a splitter widget"""
        return HeadlessUISplitter(orientation, self.verbose)
    
    def create_pixmap(self, width: int, height: int) -> 'HeadlessPixmap':
        """Create a pixmap for testing"""
        self._pixmap_counter += 1
        return HeadlessPixmap(width, height, self._pixmap_counter)
    
    def create_layout(self, orientation: str = "vertical") -> 'HeadlessUILayout':
        """Create a layout"""
        return HeadlessUILayout(orientation, self.verbose)


# Backward compatibility alias
HeadlessUIFactory = HeadlessUIImplementation


# Register the implementation
from gui.ui_interface import UIImplementationRegistry
UIImplementationRegistry.register("headless", HeadlessUIImplementation)


class HeadlessPixmap:
    """Headless implementation of a pixmap"""
    
    def __init__(self, width: int, height: int, counter: int):
        self.width = width
        self.height = height
        self.counter = counter
    
    def isNull(self) -> bool:
        """Check if pixmap is null"""
        return False
    
    def __str__(self) -> str:
        return f"HeadlessPixmap({self.width}x{self.height}, #{self.counter})"
