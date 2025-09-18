#!/usr/bin/env python3
"""
UI Layout Debugging Script

This script uses the scripted UI testing system to debug layout and window issues.
"""

import sys
import json
from pathlib import Path

# Add the project root to the path
sys.path.insert(0, str(Path(__file__).parent))

from gui.ui_factory import create_ui_factory
from gui.main_window_abstracted import MainWindowAbstracted

def create_debug_script():
    """Create a debugging script to investigate UI layout issues"""
    return [
        {
            "command": "wait",
            "duration": 0.5,
            "description": "Initial wait for UI to initialize"
        },
        {
            "command": "debug_info",
            "info_type": "windows",
            "description": "List all windows"
        },
        {
            "command": "debug_info",
            "info_type": "widgets",
            "description": "List all widgets in main window"
        },
        {
            "command": "debug_info",
            "info_type": "parenting",
            "description": "Check widget parenting"
        },
        {
            "command": "wait",
            "duration": 1.0,
            "description": "Wait to observe UI state"
        }
    ]

def debug_ui():
    """Debug the UI using scripted commands"""
    print("=== UI Layout Debugging ===")
    
    # Create UI factory
    print("Creating UI factory...")
    ui_factory = create_ui_factory('qt', verbose=True)
    ui_impl = ui_factory.get_ui_implementation()
    
    # Create main window
    print("Creating main window...")
    main_window = ui_factory.create_main_window()
    
    # Enable test mode with debug commands
    debug_commands = create_debug_script()
    print(f"Enabling test mode with {len(debug_commands)} debug commands...")
    ui_impl.enable_test_mode(debug_commands)
    
    print("Debug session completed!")

if __name__ == "__main__":
    debug_ui()
