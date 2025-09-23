"""
Debug UI Factory for creating command-line UI components

This factory creates debug implementations of the UI abstraction layer
that emit messages instead of rendering GUI components. Used for development
and debugging purposes.
"""

from typing import Any, Optional, Dict, List
from pathlib import Path

from curioshelf.ui.abstraction import (
    UIWidget, UIButton, UITextInput, UIComboBox, UIListWidget, UICanvas,
    UIMessageBox, UIFileDialog, UIProgressBar, UIGroupBox, UITabWidget,
    UISplitter, UILayout, UIMenuBar, UIMenu, UIMenuItem, UIStatusBar
)
from curioshelf.ui.factory_interface import UIFactoryInterface
from .ui_widgets import (
    DebugUIWidget, DebugUIButton, DebugUILabel, DebugUITextInput, DebugUIComboBox, 
    DebugUIListWidget, DebugUICanvas, DebugUIMessageBox, DebugUIFileDialog, 
    DebugUIProgressBar, DebugUIGroupBox, DebugUITabWidget, DebugUISplitter,
    DebugUILayout, DebugUIMenuBar, DebugUIMenu, DebugUIMenuItem, DebugUIStatusBar
)
from .message_system import MessageLogger, MessageType
from curioshelf.ui.ui_interface import UIImplementationInterface, UIImplementationError


class DebugUIImplementation(UIImplementationInterface, UIFactoryInterface):
    """Debug implementation of the UI interface for development and testing"""
    
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
            print("[DEBUG] UI implementation initialized")
        return True
    
    def cleanup(self) -> bool:
        """Cleanup the headless UI implementation"""
        self._initialized = False
        self._running = False
        if self.verbose:
            print("[DEBUG] UI implementation cleaned up")
        return True
    
    def get_ui_implementation(self) -> 'UIImplementationInterface':
        """Get the UI implementation instance"""
        return self
    
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
    
    def create_widget(self, parent: Optional['UIWidget'] = None) -> 'DebugUIWidget':
        """Create a basic widget"""
        return DebugUIWidget(self.verbose, self._message_logger)
    
    def create_button(self, text: str = "", parent: Optional['UIWidget'] = None) -> 'DebugUIButton':
        """Create a button"""
        return DebugUIButton(text, self.verbose, self._message_logger)
    
    def create_text_input(self, placeholder: str = "", parent: Optional['UIWidget'] = None) -> 'DebugUITextInput':
        """Create a text input"""
        return DebugUITextInput(placeholder, self.verbose, self._message_logger)
    
    def create_line_edit(self, parent: Optional['UIWidget'] = None) -> 'DebugUITextInput':
        """Create a line edit widget (alias for create_text_input)"""
        return DebugUITextInput("", self.verbose, self._message_logger)
    
    def create_label(self, text: str = "", parent: Optional['UIWidget'] = None) -> 'DebugUILabel':
        """Create a label widget"""
        from .ui_widgets import DebugUILabel
        return DebugUILabel(text, self.verbose, self._message_logger)
    
    def create_combo_box(self, parent: Optional['UIWidget'] = None) -> 'DebugUIComboBox':
        """Create a combo box"""
        return DebugUIComboBox(self.verbose, self._message_logger)
    
    def create_list_widget(self, parent: Optional['UIWidget'] = None) -> 'DebugUIListWidget':
        """Create a list widget"""
        return DebugUIListWidget(self.verbose, self._message_logger)
    
    def create_canvas(self, parent: Optional['UIWidget'] = None) -> 'DebugUICanvas':
        """Create a canvas widget"""
        return DebugUICanvas(self.verbose, self._message_logger)
    
    def create_message_box(self, parent: Optional['UIWidget'] = None) -> 'DebugUIMessageBox':
        """Create a message box"""
        return DebugUIMessageBox(self.verbose, self._message_logger)
    
    def create_file_dialog(self, parent: Optional['UIWidget'] = None) -> 'DebugUIFileDialog':
        """Create a file dialog"""
        return DebugUIFileDialog(self.verbose, self._message_logger)
    
    def create_progress_bar(self, parent: Optional['UIWidget'] = None) -> 'DebugUIProgressBar':
        """Create a progress bar"""
        return DebugUIProgressBar(self.verbose, self._message_logger)
    
    def create_group_box(self, title: str = "") -> 'DebugUIGroupBox':
        """Create a group box"""
        return DebugUIGroupBox(title, self.verbose, self._message_logger)
    
    def create_tab_widget(self, parent: Optional['UIWidget'] = None) -> 'DebugUITabWidget':
        """Create a tab widget"""
        return DebugUITabWidget(self.verbose, self._message_logger)
    
    def create_splitter(self, orientation: str = "horizontal", parent: Optional['UIWidget'] = None) -> 'DebugUISplitter':
        """Create a splitter widget"""
        return DebugUISplitter(orientation, self.verbose, self._message_logger)
    
    def create_pixmap(self, width: int, height: int) -> 'HeadlessPixmap':
        """Create a pixmap for testing"""
        self._pixmap_counter += 1
        return HeadlessPixmap(width, height, self._pixmap_counter)
    
    def create_layout(self, orientation: str = "vertical", parent: Optional['UIWidget'] = None) -> 'DebugUILayout':
        """Create a layout"""
        return DebugUILayout(orientation, self.verbose, self._message_logger)
    
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
        return DebugUIMenuBar(self._message_logger)
    
    def create_menu(self, title: str, parent: Optional['UIMenuBar'] = None) -> 'UIMenu':
        """Create a menu widget"""
        menu = DebugUIMenu(self._message_logger)
        menu.set_title(title)
        return menu
    
    def create_menu_item(self, text: str, parent: Optional['UIMenu'] = None) -> 'UIMenuItem':
        """Create a menu item widget"""
        item = DebugUIMenuItem(self._message_logger)
        item.set_text(text)
        return item
    
    def create_status_bar(self, parent: Optional['UIWidget'] = None) -> 'UIStatusBar':
        """Create a status bar widget"""
        return DebugUIStatusBar(self._message_logger)
    
    def create_main_widget(self, parent: Optional['UIWidget'] = None) -> 'UIWidget':
        """Create a main widget (main window)"""
        return DebugUIWidget(self.verbose, self._message_logger)


# Backward compatibility alias
DebugUIFactory = DebugUIImplementation


# Register the implementation
from curioshelf.ui.ui_interface import UIImplementationRegistry
UIImplementationRegistry.register("debug", DebugUIImplementation)


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
