#!/usr/bin/env python3
"""
Simple UI test to verify single window behavior
"""

import sys
from pathlib import Path

# Add the project root to the path
sys.path.insert(0, str(Path(__file__).parent))

from curioshelf.ui.ui_factory import create_ui_factory

def test_simple_ui():
    """Test simple UI creation"""
    print("=== Simple UI Test ===")
    
    # Create UI factory
    print("Creating UI factory...")
    ui_factory = create_ui_factory('qt', verbose=True)
    ui_impl = ui_factory.get_ui_implementation()
    
    # Create main window
    print("Creating main window...")
    main_window = ui_factory.create_main_window()
    
    # Get the Qt widget and show it
    qt_main_window = main_window.main_widget.qt_widget
    print(f"Main window type: {type(qt_main_window)}")
    print(f"Main window title: {qt_main_window.windowTitle()}")
    
    # Show the main window
    qt_main_window.show()
    
    print("Main window should now be visible!")
    print("Press Enter to continue...")
    input()

if __name__ == "__main__":
    test_simple_ui()
