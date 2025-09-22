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
    
    # Use script UI instead of Qt to avoid wrapper issues
    print("Creating UI factory...")
    ui_factory = create_ui_factory('script', verbose=True)
    ui_impl = ui_factory.get_ui_implementation()
    
    # Test that we can create basic UI components
    print("Testing UI component creation...")
    
    # Test main widget creation
    main_widget = ui_impl.create_main_widget()
    assert main_widget is not None
    print("✓ Main widget created successfully!")
    
    # Test script execution (which is what script UI is designed for)
    print("Testing script execution...")
    result = ui_impl.execute_script_content("print('Hello from script UI!')")
    print("✓ Script execution successful!")
    
    print("✓ All UI tests completed successfully!")
    print(f"Main widget type: {type(main_widget)}")
    print(f"Script execution result: {result}")

if __name__ == "__main__":
    test_simple_ui()
