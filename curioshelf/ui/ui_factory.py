"""
UI Factory for CurioShelf

This module provides a factory for creating UI implementations and main windows
based on the selected UI backend. It serves as the main entry point for UI
creation in the application.
"""

import sys
from pathlib import Path
from typing import Optional

from .ui_interface import create_ui_implementation, UIImplementationError

# Import implementations to register them
# Debug UI moved to tests/support/debug
from . import script

# Try to import Qt implementation (may fail if PySide6 not available)
try:
    from . import qtimpl
except ImportError:
    pass  # Qt implementation not available


class UIFactory:
    """Factory for creating UI components and main windows"""
    
    def __init__(self, ui_backend: str = "qt", verbose: bool = False):
        """
        Initialize the UI factory
        
        Args:
            ui_backend: UI backend to use ("qt", "debug", "script", etc.)
            verbose: Enable verbose logging
        """
        self.ui_backend = ui_backend
        self.verbose = verbose
        self._ui_implementation = None
        self._main_window = None
    
    def get_ui_implementation(self):
        """Get the UI implementation instance"""
        if self._ui_implementation is None:
            try:
                self._ui_implementation = create_ui_implementation(
                    self.ui_backend, verbose=self.verbose
                )
                self._ui_implementation.initialize()
            except Exception as e:
                if self.verbose:
                    print(f"Failed to create {self.ui_backend} UI implementation: {e}")
                
                # Fallback to debug if available
                if self.ui_backend != "debug":
                    try:
                        self._ui_implementation = create_ui_implementation(
                            "debug", verbose=self.verbose
                        )
                        self._ui_implementation.initialize()
                        if self.verbose:
                            print("Falling back to debug implementation")
                    except Exception as fallback_error:
                        raise UIImplementationError(
                            f"Failed to create any UI implementation. "
                            f"Original error: {e}, Fallback error: {fallback_error}"
                        )
                else:
                    raise UIImplementationError(f"Failed to create debug UI: {e}")
        
        return self._ui_implementation
    
    def create_main_window(self):
        """Create the main application window"""
        if self._main_window is None:
            from .main_window_abstracted import MainWindowAbstracted
            
            ui_impl = self.get_ui_implementation()
            self._main_window = MainWindowAbstracted(
                ui_impl, verbose=self.verbose
            )
        
        return self._main_window
    
    def cleanup(self):
        """Cleanup UI resources"""
        if self._main_window:
            self._main_window.cleanup()
            self._main_window = None
        
        if self._ui_implementation:
            self._ui_implementation.cleanup()
            self._ui_implementation = None


def create_ui_factory(ui_backend: str = "qt", verbose: bool = False) -> UIFactory:
    """
    Create a UI factory with the specified backend
    
    Args:
        ui_backend: UI backend to use ("qt", "debug", "script", etc.)
        verbose: Enable verbose logging
    
    Returns:
        UIFactory instance
    """
    return UIFactory(ui_backend, verbose)


def get_available_ui_backends() -> list:
    """Get list of available UI backends"""
    from .ui_interface import list_available_implementations
    return list_available_implementations()


def main():
    """Main entry point for testing the UI factory"""
    import argparse
    
    parser = argparse.ArgumentParser(description="CurioShelf UI Factory Test")
    parser.add_argument(
        "--ui", 
        choices=get_available_ui_backends(),
        default="qt",
        help="UI backend to use"
    )
    parser.add_argument(
        "--verbose", 
        action="store_true",
        help="Enable verbose logging"
    )
    
    args = parser.parse_args()
    
    print(f"Creating UI factory with backend: {args.ui}")
    
    try:
        factory = create_ui_factory(args.ui, args.verbose)
        main_window = factory.create_main_window()
        
        print("Main window created successfully!")
        print(f"UI Implementation: {factory.get_ui_implementation().__class__.__name__}")
        
        # Run the application
        if args.ui in ["debug", "script"]:
            print(f"{args.ui.title()} mode - no GUI will be shown")
        else:
            print("Starting GUI application...")
            factory.get_ui_implementation().run_event_loop()
        
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)
    finally:
        factory.cleanup()


if __name__ == "__main__":
    main()
