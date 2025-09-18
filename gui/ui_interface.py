"""
UI Implementation Interface for CurioShelf

This module defines the interface that all UI implementations must implement.
It serves as a contract for creating new UI framework implementations and
ensures consistency across different UI backends.

The interface is designed to be:
- Framework agnostic
- Well documented with clear expectations
- Extensible for future UI components
- Testable and mockable
"""

from abc import ABC, abstractmethod
from typing import Any, Optional, List, Dict, Callable
from pathlib import Path

from curioshelf.ui_abstraction import (
    UIWidget, UIButton, UITextInput, UIComboBox, UIListWidget, UICanvas,
    UIMessageBox, UIFileDialog, UIProgressBar, UIGroupBox, UITabWidget,
    UISplitter, UILayout, UIMenuBar, UIMenu, UIMenuItem, UIStatusBar
)


class UIImplementationInterface(ABC):
    """
    Abstract interface for UI implementations
    
    This interface defines the contract that all UI implementations must follow.
    It provides a factory pattern for creating UI components and ensures
    consistent behavior across different UI frameworks.
    
    Implementations should:
    1. Create concrete instances of all UI abstraction classes
    2. Handle framework-specific initialization and cleanup
    3. Provide proper signal/event handling
    4. Support both enabled/disabled and visible/hidden states
    5. Emit appropriate signals for user interactions
    
    Example implementations:
    - QtUIImplementation (PySide6/Qt)
    - HeadlessUIImplementation (Command-line testing)
    - WebUIImplementation (Future web-based UI)
    - MobileUIImplementation (Future mobile UI)
    """
    
    def __init__(self, verbose: bool = False):
        """
        Initialize the UI implementation
        
        Args:
            verbose: Whether to enable verbose logging/debugging output
        """
        self.verbose = verbose
        self._initialized = False
    
    @abstractmethod
    def initialize(self) -> bool:
        """
        Initialize the UI implementation
        
        This method should perform any necessary setup for the UI framework,
        such as creating the main application object, setting up event loops,
        or initializing graphics contexts.
        
        Returns:
            bool: True if initialization was successful, False otherwise
            
        Raises:
            UIImplementationError: If initialization fails due to framework issues
        """
        pass
    
    @abstractmethod
    def cleanup(self) -> bool:
        """
        Cleanup the UI implementation
        
        This method should perform any necessary cleanup for the UI framework,
        such as closing windows, cleaning up resources, or shutting down
        the main application object.
        
        Returns:
            bool: True if cleanup was successful, False otherwise
        """
        pass
    
    @abstractmethod
    def is_initialized(self) -> bool:
        """
        Check if the UI implementation is properly initialized
        
        Returns:
            bool: True if initialized and ready to use, False otherwise
        """
        pass
    
    # Widget Factory Methods
    
    @abstractmethod
    def create_widget(self, parent: Optional[UIWidget] = None) -> UIWidget:
        """
        Create a basic widget container
        
        Args:
            parent: Optional parent widget for proper hierarchy
            
        Returns:
            UIWidget: A basic widget that can contain other widgets
        """
        pass
    
    @abstractmethod
    def create_button(self, text: str = "", parent: Optional[UIWidget] = None) -> UIButton:
        """
        Create a clickable button widget
        
        Args:
            text: The text to display on the button
            parent: Optional parent widget for proper hierarchy
            
        Returns:
            UIButton: A button widget that emits clicked signals
        """
        pass
    
    @abstractmethod
    def create_text_input(self, placeholder: str = "", parent: Optional[UIWidget] = None) -> UITextInput:
        """
        Create a text input widget
        
        Args:
            placeholder: Placeholder text to show when empty
            parent: Optional parent widget for proper hierarchy
            
        Returns:
            UITextInput: A text input widget that emits text_changed signals
        """
        pass
    
    @abstractmethod
    def create_combo_box(self, parent: Optional[UIWidget] = None) -> UIComboBox:
        """
        Create a dropdown combo box widget
        
        Returns:
            UIComboBox: A combo box widget that emits current_changed signals
        """
        pass
    
    @abstractmethod
    def create_list_widget(self, parent: Optional[UIWidget] = None) -> UIListWidget:
        """
        Create a list selection widget
        
        Returns:
            UIListWidget: A list widget that emits current_changed signals
        """
        pass
    
    @abstractmethod
    def create_canvas(self) -> UICanvas:
        """
        Create a canvas widget for image display and selection
        
        Returns:
            UICanvas: A canvas widget that supports:
                - Image display (set_pixmap)
                - Zoom control (set_zoom)
                - Selection rectangles (set_selection_rect)
                - Selection change signals
        """
        pass
    
    @abstractmethod
    def create_message_box(self) -> UIMessageBox:
        """
        Create a message box for user notifications
        
        Returns:
            UIMessageBox: A message box that supports:
                - Info messages (show_info)
                - Warning messages (show_warning)
                - Error messages (show_error)
                - Question dialogs (show_question)
        """
        pass
    
    @abstractmethod
    def create_file_dialog(self) -> UIFileDialog:
        """
        Create a file dialog for file selection
        
        Returns:
            UIFileDialog: A file dialog that supports:
                - Open file selection (get_open_file_name)
                - Save file selection (get_save_file_name)
                - File type filtering
        """
        pass
    
    @abstractmethod
    def create_progress_bar(self, parent: Optional[UIWidget] = None) -> UIProgressBar:
        """
        Create a progress bar widget
        
        Returns:
            UIProgressBar: A progress bar widget that supports:
                - Value setting (0-100)
                - Min/max range configuration
                - Visual progress indication
        """
        pass
    
    @abstractmethod
    def create_group_box(self, title: str = "") -> UIGroupBox:
        """
        Create a group box widget for organizing related controls
        
        Args:
            title: The title text for the group box
            
        Returns:
            UIGroupBox: A group box widget that can contain other widgets
        """
        pass
    
    @abstractmethod
    def create_tab_widget(self, parent: Optional[UIWidget] = None) -> UITabWidget:
        """
        Create a tabbed widget container
        
        Returns:
            UITabWidget: A tab widget that supports:
                - Adding tabs (add_tab)
                - Tab switching (set_current_index)
                - Tab change signals
        """
        pass
    
    @abstractmethod
    def create_splitter(self, orientation: str = "horizontal") -> UISplitter:
        """
        Create a splitter widget for resizable panels
        
        Args:
            orientation: "horizontal" or "vertical" splitter orientation
            
        Returns:
            UISplitter: A splitter widget that supports:
                - Adding widgets (add_widget)
                - Size control (set_sizes)
                - Resizable panels
        """
        pass
    
    @abstractmethod
    def create_layout(self, orientation: str = "vertical", parent: Optional[UIWidget] = None) -> UILayout:
        """
        Create a layout manager for organizing widgets
        
        Args:
            orientation: "vertical", "horizontal", or "form" layout orientation
            parent: Optional parent widget for proper hierarchy
            
        Returns:
            UILayout: A layout that supports:
                - Adding widgets (add_widget)
                - Removing widgets (remove_widget)
                - Automatic widget arrangement
        """
        pass
    
    # Menu and Status Bar Support
    
    @abstractmethod
    def create_menu_bar(self, parent: Optional[UIWidget] = None) -> 'UIMenuBar':
        """
        Create a menu bar widget
        
        Args:
            parent: Optional parent widget for proper hierarchy
            
        Returns:
            UIMenuBar: A menu bar widget that can contain menus
        """
        pass
    
    @abstractmethod
    def create_menu(self, title: str, parent: Optional['UIMenuBar'] = None) -> 'UIMenu':
        """
        Create a menu widget
        
        Args:
            title: Menu title text
            parent: Optional parent menu bar
            
        Returns:
            UIMenu: A menu widget that can contain menu items
        """
        pass
    
    @abstractmethod
    def create_menu_item(self, text: str, parent: Optional['UIMenu'] = None) -> 'UIMenuItem':
        """
        Create a menu item widget
        
        Args:
            text: Menu item text
            parent: Optional parent menu
            
        Returns:
            UIMenuItem: A menu item widget that can be clicked
        """
        pass
    
    @abstractmethod
    def create_status_bar(self, parent: Optional[UIWidget] = None) -> 'UIStatusBar':
        """
        Create a status bar widget
        
        Args:
            parent: Optional parent widget for proper hierarchy
            
        Returns:
            UIStatusBar: A status bar widget for displaying status information
        """
        pass
    
    # Utility Methods
    
    @abstractmethod
    def create_pixmap(self, width: int, height: int) -> Any:
        """
        Create a pixmap/image object for canvas display
        
        Args:
            width: Width of the pixmap in pixels
            height: Height of the pixmap in pixels
            
        Returns:
            Any: A pixmap object suitable for use with create_canvas()
                The exact type depends on the implementation.
        """
        pass
    
    @abstractmethod
    def run_event_loop(self) -> int:
        """
        Run the main event loop for the UI framework
        
        This method should start the main event loop and block until
        the application is ready to exit.
        
        Returns:
            int: Exit code (0 for success, non-zero for error)
        """
        pass
    
    @abstractmethod
    def quit_event_loop(self) -> None:
        """
        Quit the main event loop
        
        This method should signal the event loop to exit gracefully.
        """
        pass
    
    # State Management
    
    @abstractmethod
    def set_global_style(self, style: Dict[str, Any]) -> None:
        """
        Set global styling for the UI implementation
        
        Args:
            style: Dictionary containing style properties
                Common properties:
                - "theme": "light" or "dark"
                - "font_family": Font family name
                - "font_size": Base font size
                - "colors": Dictionary of color values
        """
        pass
    
    @abstractmethod
    def get_screen_size(self) -> tuple[int, int]:
        """
        Get the primary screen size
        
        Returns:
            tuple[int, int]: (width, height) of the primary screen in pixels
        """
        pass
    
    @abstractmethod
    def get_dpi_scale(self) -> float:
        """
        Get the DPI scaling factor for high-DPI displays
        
        Returns:
            float: DPI scaling factor (1.0 for normal DPI, >1.0 for high DPI)
        """
        pass
    
    # Error Handling
    
    @abstractmethod
    def handle_error(self, error: Exception, context: str = "") -> None:
        """
        Handle errors in the UI implementation
        
        Args:
            error: The exception that occurred
            context: Additional context about where the error occurred
        """
        pass
    
    @abstractmethod
    def enable_test_mode(self, commands: List[Dict[str, Any]]) -> None:
        """
        Enable test mode with a list of commands to execute
        
        This method allows the UI implementation to enter test mode where
        it can execute a series of commands for testing purposes. The
        implementation should handle the commands appropriately for its
        framework (e.g., using timers for Qt, immediate execution for headless).
        
        Args:
            commands: List of test commands to execute
        """
        pass
    
    @abstractmethod
    def disable_test_mode(self) -> None:
        """
        Disable test mode and return to normal operation
        """
        pass
    
    @abstractmethod
    def is_test_mode(self) -> bool:
        """
        Check if the UI implementation is currently in test mode
        
        Returns:
            True if in test mode, False otherwise
        """
        pass


class UIImplementationError(Exception):
    """Exception raised by UI implementations when errors occur"""
    
    def __init__(self, message: str, implementation: str = "", context: str = ""):
        super().__init__(message)
        self.implementation = implementation
        self.context = context
    
    def __str__(self) -> str:
        base_msg = super().__str__()
        if self.implementation:
            base_msg = f"[{self.implementation}] {base_msg}"
        if self.context:
            base_msg = f"{base_msg} (Context: {self.context})"
        return base_msg


# Implementation Registry

class UIImplementationRegistry:
    """
    Registry for managing UI implementations
    
    This class provides a centralized way to register and retrieve
    UI implementations, making it easy to switch between different
    UI backends or add new ones.
    """
    
    _implementations: Dict[str, type] = {}
    
    @classmethod
    def register(cls, name: str, implementation_class: type) -> None:
        """
        Register a UI implementation
        
        Args:
            name: Unique name for the implementation
            implementation_class: Class that implements UIImplementationInterface
        """
        if not issubclass(implementation_class, UIImplementationInterface):
            raise ValueError(f"Implementation class must inherit from UIImplementationInterface")
        cls._implementations[name] = implementation_class
    
    @classmethod
    def get(cls, name: str) -> type:
        """
        Get a registered UI implementation
        
        Args:
            name: Name of the implementation to retrieve
            
        Returns:
            type: The implementation class
            
        Raises:
            KeyError: If the implementation is not registered
        """
        if name not in cls._implementations:
            available = ", ".join(cls._implementations.keys())
            raise KeyError(f"UI implementation '{name}' not found. Available: {available}")
        return cls._implementations[name]
    
    @classmethod
    def list_implementations(cls) -> List[str]:
        """
        List all registered implementations
        
        Returns:
            List[str]: List of registered implementation names
        """
        return list(cls._implementations.keys())
    
    @classmethod
    def create(cls, name: str, **kwargs: Any) -> UIImplementationInterface:
        """
        Create an instance of a registered implementation
        
        Args:
            name: Name of the implementation to create
            **kwargs: Additional arguments to pass to the implementation constructor
            
        Returns:
            UIImplementationInterface: Instance of the requested implementation
        """
        implementation_class = cls.get(name)
        return implementation_class(**kwargs)  # type: ignore[no-any-return]


# Convenience Functions

def create_ui_implementation(name: str, **kwargs: Any) -> UIImplementationInterface:
    """
    Create a UI implementation by name
    
    This is a convenience function that uses the registry to create
    UI implementations without needing to import specific classes.
    
    Args:
        name: Name of the implementation ("qt", "headless", etc.)
        **kwargs: Additional arguments for the implementation
        
    Returns:
        UIImplementationInterface: The created implementation instance
        
    Example:
        # Create Qt implementation
        ui = create_ui_implementation("qt", verbose=True)
        
        # Create headless implementation for testing
        ui = create_ui_implementation("headless", verbose=True)
    """
    return UIImplementationRegistry.create(name, **kwargs)


def list_available_implementations() -> List[str]:
    """
    List all available UI implementations
    
    Returns:
        List[str]: List of available implementation names
    """
    return UIImplementationRegistry.list_implementations()
