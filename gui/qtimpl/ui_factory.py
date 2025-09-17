"""
Qt UI Factory for creating UI components

This factory creates Qt/PySide6 implementations of the UI abstraction layer.
"""

from typing import Any, Optional, Callable, Dict, List
from pathlib import Path

from PySide6.QtWidgets import (
    QWidget, QPushButton, QLineEdit, QTextEdit, QComboBox, QListWidget,
    QGraphicsView, QGraphicsScene, QMessageBox, QFileDialog, QProgressBar,
    QGroupBox, QTabWidget, QSplitter, QVBoxLayout, QHBoxLayout, QFormLayout,
    QApplication
)
from PySide6.QtCore import Qt, QRect, QTimer
from PySide6.QtGui import QPixmap, QFont, QPainter, QPen, QBrush, QScreen

from curioshelf.ui_abstraction import (
    UIWidget, UIButton, UITextInput, UIComboBox, UIListWidget, UICanvas,
    UIMessageBox, UIFileDialog, UIProgressBar, UIGroupBox, UITabWidget,
    UISplitter, UILayout
)
from curioshelf.ui_factory_interface import UIFactoryInterface
from gui.ui_interface import UIImplementationInterface, UIImplementationError
from .ui_widgets import (
    QtUIWidget, QtUIButton, QtUITextInput, QtUIComboBox, QtUIListWidget,
    QtUICanvas, QtUIMessageBox, QtUIFileDialog, QtUIProgressBar, QtUIGroupBox,
    QtUITabWidget, QtUISplitter, QtUILayout
)


class QtUIImplementation(UIImplementationInterface, UIFactoryInterface):
    """Qt/PySide6 implementation of the UI interface"""
    
    def __init__(self, verbose: bool = False):
        super().__init__(verbose)
        self._pixmap_counter = 0
        self._app = None
        self._style = {}
        self._test_mode = False
        self._test_commands = []
        self._test_command_index = 0
    
    def initialize(self) -> bool:
        """Initialize the Qt UI implementation"""
        try:
            # Always create QApplication - it's needed for widget creation
            if not QApplication.instance():
                if self.verbose:
                    print("[QT] Creating new QApplication instance...")
                self._app = QApplication([])
                self._app.setApplicationName("CurioShelf")
                self._app.setApplicationVersion("2.0.0")
                self._app.setOrganizationName("CurioShelf")
                if self.verbose:
                    print("[QT] QApplication created successfully")
            else:
                if self.verbose:
                    print("[QT] Using existing QApplication instance")
                self._app = QApplication.instance()
            
            self._initialized = True
            if self.verbose:
                print("[QT] UI implementation initialized")
            return True
        except Exception as e:
            self.handle_error(e, "Qt initialization")
            return False
    
    def cleanup(self) -> bool:
        """Cleanup the Qt UI implementation"""
        try:
            if self._app and self._app != QApplication.instance():
                self._app.quit()
            self._initialized = False
            if self.verbose:
                print("[QT] UI implementation cleaned up")
            return True
        except Exception as e:
            self.handle_error(e, "Qt cleanup")
            return False
    
    def is_initialized(self) -> bool:
        """Check if Qt is initialized"""
        return self._initialized and QApplication.instance() is not None
    
    def run_event_loop(self) -> int:
        """Run the Qt event loop"""
        if not self.is_initialized():
            self.initialize()
        
        if self._app:
            if self.verbose:
                print("[QT] Starting Qt event loop...")
            result = self._app.exec()
            if self.verbose:
                print(f"[QT] Qt event loop exited with code: {result}")
            return result
        else:
            if self.verbose:
                print("[QT] No Qt application instance available")
            return 1
    
    def quit_event_loop(self) -> None:
        """Quit the Qt event loop"""
        if self._app:
            self._app.quit()
    
    def set_global_style(self, style: Dict[str, Any]) -> None:
        """Set global Qt styling"""
        self._style = style
        
        # Apply theme
        if "theme" in style:
            if style["theme"] == "dark":
                self._app.setStyleSheet("""
                    QWidget {
                        background-color: #2b2b2b;
                        color: #ffffff;
                    }
                    QPushButton {
                        background-color: #404040;
                        border: 1px solid #606060;
                        padding: 5px;
                    }
                    QPushButton:hover {
                        background-color: #505050;
                    }
                """)
        
        # Apply font
        if "font_family" in style or "font_size" in style:
            font = QFont()
            if "font_family" in style:
                font.setFamily(style["font_family"])
            if "font_size" in style:
                font.setPointSize(style["font_size"])
            self._app.setFont(font)
    
    def get_screen_size(self) -> tuple[int, int]:
        """Get primary screen size"""
        if QApplication.instance():
            screen = QApplication.primaryScreen()
            if screen:
                size = screen.size()
                return (size.width(), size.height())
        return (1920, 1080)  # Default fallback
    
    def get_dpi_scale(self) -> float:
        """Get DPI scaling factor"""
        if QApplication.instance():
            screen = QApplication.primaryScreen()
            if screen:
                return screen.devicePixelRatio()
        return 1.0
    
    def handle_error(self, error: Exception, context: str = "") -> None:
        """Handle Qt errors"""
        error_msg = f"Qt UI Error: {str(error)}"
        if self.verbose:
            print(f"[QT ERROR] {error_msg} (Context: {context})")
        raise UIImplementationError(error_msg, "qt", context)
    
    def enable_test_mode(self, commands: List[Dict[str, Any]]) -> None:
        """Enable test mode with a list of commands to execute"""
        self._test_mode = True
        self._test_commands = commands
        self._test_command_index = 0
        
        if self.verbose:
            print(f"[QT] Test mode enabled with {len(commands)} commands")
        
        # Execute commands immediately in test mode (like headless implementation)
        # This avoids event loop issues in test environments
        self._execute_all_test_commands()
    
    def _execute_all_test_commands(self) -> None:
        """Execute all test commands immediately (like headless implementation)"""
        for i, command in enumerate(self._test_commands):
            if self.verbose:
                print(f"[QT] Executing test command {i+1}/{len(self._test_commands)}: {command}")
            try:
                self._execute_test_command(command)
            except Exception as e:
                if self.verbose:
                    print(f"[QT] Test command {i+1} failed: {e}")
                break
        
        if self.verbose:
            print("[QT] Test execution completed")
        self.disable_test_mode()
    
    def disable_test_mode(self) -> None:
        """Disable test mode and return to normal operation"""
        self._test_mode = False
        self._test_commands = []
        self._test_command_index = 0
        
        
        if self.verbose:
            print("[QT] Test mode disabled")
    
    def is_test_mode(self) -> bool:
        """Check if the UI implementation is currently in test mode"""
        return self._test_mode
    
    
    def _execute_test_command(self, command: Dict[str, Any]) -> None:
        """Execute a single test command"""
        cmd_type = command.get("command")
        
        if cmd_type == "wait":
            duration = command.get("duration", 0.1)
            # In test mode, we can simulate wait with a simple sleep
            import time
            time.sleep(duration)
            
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
    
    def create_widget(self) -> 'QtUIWidget':
        """Create a basic widget"""
        return QtUIWidget()
    
    def create_button(self, text: str = "") -> 'QtUIButton':
        """Create a button"""
        return QtUIButton(text)
    
    def create_text_input(self, placeholder: str = "") -> 'QtUITextInput':
        """Create a text input"""
        return QtUITextInput(placeholder)
    
    def create_combo_box(self) -> 'QtUIComboBox':
        """Create a combo box"""
        return QtUIComboBox()
    
    def create_list_widget(self) -> 'QtUIListWidget':
        """Create a list widget"""
        return QtUIListWidget()
    
    def create_canvas(self) -> 'QtUICanvas':
        """Create a canvas widget"""
        return QtUICanvas()
    
    def create_message_box(self) -> 'QtUIMessageBox':
        """Create a message box"""
        msg_box = QtUIMessageBox()
        # Pass test mode flag to message box
        msg_box._test_mode = self._test_mode
        return msg_box
    
    def create_file_dialog(self) -> 'QtUIFileDialog':
        """Create a file dialog"""
        return QtUIFileDialog()
    
    def create_progress_bar(self) -> 'QtUIProgressBar':
        """Create a progress bar"""
        return QtUIProgressBar()
    
    def create_group_box(self, title: str = "") -> 'QtUIGroupBox':
        """Create a group box"""
        return QtUIGroupBox(title)
    
    def create_tab_widget(self) -> 'QtUITabWidget':
        """Create a tab widget"""
        return QtUITabWidget()
    
    def create_splitter(self, orientation: str = "horizontal") -> 'QtUISplitter':
        """Create a splitter widget"""
        return QtUISplitter(orientation)
    
    def create_pixmap(self, width: int, height: int) -> QPixmap:
        """Create a pixmap for testing"""
        self._pixmap_counter += 1
        pixmap = QPixmap(width, height)
        pixmap.fill(Qt.white)
        
        # Draw a simple pattern for testing
        painter = QPainter(pixmap)
        painter.setPen(QPen(Qt.blue, 2))
        painter.setBrush(QBrush(Qt.lightBlue))
        painter.drawRect(10, 10, width - 20, height - 20)
        painter.drawText(20, 30, f"Test Image {self._pixmap_counter}")
        painter.end()
        
        return pixmap
    
    def create_layout(self, orientation: str = "vertical") -> 'QtUILayout':
        """Create a layout"""
        return QtUILayout(orientation)


# Backward compatibility alias
QtUIFactory = QtUIImplementation


# Register the implementation
from gui.ui_interface import UIImplementationRegistry
UIImplementationRegistry.register("qt", QtUIImplementation)
