"""
Headless UI Factory for creating command-line UI components

This factory creates headless implementations of the UI abstraction layer
that emit messages instead of rendering GUI components.
"""

from typing import Any, Optional, Dict, List
from pathlib import Path

from ..abstraction import (
    UIWidget, UIButton, UITextInput, UIComboBox, UIListWidget, UICanvas,
    UIMessageBox, UIFileDialog, UIProgressBar, UIGroupBox, UITabWidget,
    UISplitter, UILayout, UIMenuBar, UIMenu, UIMenuItem, UIStatusBar
)
from ..factory_interface import UIFactoryInterface
from .ui_widgets import (
    HeadlessUIWidget, HeadlessUIButton, HeadlessUITextInput, HeadlessUIComboBox, 
    HeadlessUIListWidget, HeadlessUICanvas, HeadlessUIMessageBox, HeadlessUIFileDialog, 
    HeadlessUIProgressBar, HeadlessUIGroupBox, HeadlessUITabWidget, HeadlessUISplitter,
    HeadlessUILayout, HeadlessUIMenuBar, HeadlessUIMenu, HeadlessUIMenuItem, HeadlessUIStatusBar
)
from .message_system import MessageLogger, MessageType
from ..ui_interface import UIImplementationInterface, UIImplementationError


class HeadlessUIImplementation(UIImplementationInterface, UIFactoryInterface):
    """Headless implementation of the UI interface for testing"""
    
    def __init__(self, verbose: bool = True, collect_messages: bool = True) -> None:
        super().__init__(verbose)
        self._pixmap_counter = 0
        self._style = {}
        self._running = False
        self._message_logger = MessageLogger(
            collect_messages=collect_messages,
            print_messages=verbose
        )
        self._test_mode = False
        self._test_commands = []
        self._test_command_index = 0
    
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
    
    def enable_test_mode(self, commands: List[Dict[str, Any]]) -> None:
        """Enable test mode with a list of commands to execute"""
        self._test_mode = True
        self._test_commands = commands
        self._test_command_index = 0
        
        if self.verbose:
            print(f"[HEADLESS] Test mode enabled with {len(commands)} commands")
        
        # Execute commands immediately in headless mode
        self._execute_all_test_commands()
    
    def disable_test_mode(self) -> None:
        """Disable test mode and return to normal operation"""
        self._test_mode = False
        self._test_commands = []
        self._test_command_index = 0
        
        if self.verbose:
            print("[HEADLESS] Test mode disabled")
    
    def is_test_mode(self) -> bool:
        """Check if the UI implementation is currently in test mode"""
        return self._test_mode
    
    def _execute_all_test_commands(self) -> None:
        """Execute all test commands immediately (headless mode)"""
        for i, command in enumerate(self._test_commands):
            if self.verbose:
                print(f"[HEADLESS] Executing test command {i+1}/{len(self._test_commands)}: {command}")
            
            try:
                self._execute_test_command(command)
            except Exception as e:
                if self.verbose:
                    print(f"[HEADLESS] Test command {i+1} failed: {e}")
                break
        
        if self.verbose:
            print("[HEADLESS] Test execution completed")
        
        self.disable_test_mode()
    
    def _execute_test_command(self, command: Dict[str, Any]) -> None:
        """Execute a single test command"""
        cmd_type = command.get("command")
        
        if cmd_type == "wait":
            duration = command.get("duration", 0.1)
            # In headless mode, we can just log the wait
            if self.verbose:
                print(f"[HEADLESS] Waiting {duration}s")
            
        elif cmd_type == "create_widget":
            widget_type = command.get("widget_type")
            if widget_type == "button":
                text = command.get("text", "Test Button")
                self.create_button(text)
            elif widget_type == "text_input":
                placeholder = command.get("placeholder", "Test Input")
                self.create_text_input(placeholder)
            elif widget_type == "combo_box":
                self.create_combo_box()
            elif widget_type == "list_widget":
                self.create_list_widget()
            elif widget_type == "canvas":
                self.create_canvas()
            elif widget_type == "progress_bar":
                self.create_progress_bar()
            elif widget_type == "group_box":
                title = command.get("title", "Test Group")
                self.create_group_box(title)
            elif widget_type == "tab_widget":
                self.create_tab_widget()
            elif widget_type == "splitter":
                self.create_splitter()
            elif widget_type == "layout":
                layout_type = command.get("layout_type", "vertical")
                self.create_layout(layout_type)
                
        elif cmd_type == "assert":
            condition = command.get("condition")
            message = command.get("message", "Assertion failed")
            if not condition:
                raise AssertionError(message)
                
        elif cmd_type == "call_method":
            method_name = command.get("method")
            # This would be implemented by the test
            pass
    
    def _log(self, message: str):
        """Log a message if verbose mode is enabled"""
        if self.verbose:
            print(f"[HEADLESS] {message}")
    
    def create_widget(self, parent: Optional['UIWidget'] = None) -> 'HeadlessUIWidget':
        """Create a basic widget"""
        return HeadlessUIWidget(self.verbose, self._message_logger)
    
    def create_button(self, text: str = "", parent: Optional['UIWidget'] = None) -> 'HeadlessUIButton':
        """Create a button"""
        return HeadlessUIButton(text, self.verbose, self._message_logger)
    
    def create_text_input(self, placeholder: str = "", parent: Optional['UIWidget'] = None) -> 'HeadlessUITextInput':
        """Create a text input"""
        return HeadlessUITextInput(placeholder, self.verbose, self._message_logger)
    
    def create_combo_box(self, parent: Optional['UIWidget'] = None) -> 'HeadlessUIComboBox':
        """Create a combo box"""
        return HeadlessUIComboBox(self.verbose, self._message_logger)
    
    def create_list_widget(self, parent: Optional['UIWidget'] = None) -> 'HeadlessUIListWidget':
        """Create a list widget"""
        return HeadlessUIListWidget(self.verbose, self._message_logger)
    
    def create_canvas(self, parent: Optional['UIWidget'] = None) -> 'HeadlessUICanvas':
        """Create a canvas widget"""
        return HeadlessUICanvas(self.verbose, self._message_logger)
    
    def create_message_box(self, parent: Optional['UIWidget'] = None) -> 'HeadlessUIMessageBox':
        """Create a message box"""
        return HeadlessUIMessageBox(self.verbose, self._message_logger)
    
    def create_file_dialog(self, parent: Optional['UIWidget'] = None) -> 'HeadlessUIFileDialog':
        """Create a file dialog"""
        return HeadlessUIFileDialog(self.verbose, self._message_logger)
    
    def create_progress_bar(self, parent: Optional['UIWidget'] = None) -> 'HeadlessUIProgressBar':
        """Create a progress bar"""
        return HeadlessUIProgressBar(self.verbose, self._message_logger)
    
    def create_group_box(self, title: str = "") -> 'HeadlessUIGroupBox':
        """Create a group box"""
        return HeadlessUIGroupBox(title, self.verbose, self._message_logger)
    
    def create_tab_widget(self, parent: Optional['UIWidget'] = None) -> 'HeadlessUITabWidget':
        """Create a tab widget"""
        return HeadlessUITabWidget(self.verbose, self._message_logger)
    
    def create_splitter(self, orientation: str = "horizontal", parent: Optional['UIWidget'] = None) -> 'HeadlessUISplitter':
        """Create a splitter widget"""
        return HeadlessUISplitter(orientation, self.verbose, self._message_logger)
    
    def create_pixmap(self, width: int, height: int) -> 'HeadlessPixmap':
        """Create a pixmap for testing"""
        self._pixmap_counter += 1
        return HeadlessPixmap(width, height, self._pixmap_counter)
    
    def create_layout(self, orientation: str = "vertical", parent: Optional['UIWidget'] = None) -> 'HeadlessUILayout':
        """Create a layout"""
        return HeadlessUILayout(orientation, self.verbose, self._message_logger)
    
    def get_message_logger(self) -> MessageLogger:
        """Get the message logger for testing and debugging"""
        return self._message_logger
    
    def get_messages(self, component: Optional[str] = None, action: Optional[str] = None,
                    message_type: Optional[MessageType] = None):
        """Get messages from the logger"""
        return self._message_logger.get_messages(component, action, message_type)
    
    def clear_messages(self):
        """Clear all collected messages"""
        self._message_logger.clear_messages()
    
    def create_menu_bar(self, parent: Optional['UIWidget'] = None) -> 'UIMenuBar':
        """Create a menu bar widget"""
        return HeadlessUIMenuBar(self._message_logger)
    
    def create_menu(self, title: str, parent: Optional['UIMenuBar'] = None) -> 'UIMenu':
        """Create a menu widget"""
        menu = HeadlessUIMenu(self._message_logger)
        menu.set_title(title)
        return menu
    
    def create_menu_item(self, text: str, parent: Optional['UIMenu'] = None) -> 'UIMenuItem':
        """Create a menu item widget"""
        item = HeadlessUIMenuItem(self._message_logger)
        item.set_text(text)
        return item
    
    def create_status_bar(self, parent: Optional['UIWidget'] = None) -> 'UIStatusBar':
        """Create a status bar widget"""
        return HeadlessUIStatusBar(self._message_logger)
    
    def create_main_widget(self, parent: Optional['UIWidget'] = None) -> 'UIWidget':
        """Create a main widget (main window)"""
        return HeadlessUIWidget(self.verbose, self._message_logger)


# Backward compatibility alias
HeadlessUIFactory = HeadlessUIImplementation


# Register the implementation
from ..ui_interface import UIImplementationRegistry
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
