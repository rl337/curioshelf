#!/usr/bin/env python3
"""
Test script for CurioShelf V2 application

This script tests the V2 application to ensure it runs correctly
with the new architecture.
"""

import sys
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from PySide6.QtWidgets import QApplication, QMessageBox
from PySide6.QtCore import Qt

def test_imports():
    """Test that all V2 components can be imported"""
    try:
        from gui.tabbed_main_window_v2 import TabbedMainWindowV2
        from gui.sources_tab_v2 import SourcesTabV2
        from gui.objects_tab_v2 import ObjectsTabV2
        from curioshelf.business_logic_v2 import SourcesController, TemplatesController, ObjectsController
        from curioshelf.ui_mocks import MockUIFactory
        print("✅ All V2 imports successful")
        return True
    except Exception as e:
        print(f"❌ Import error: {e}")
        return False

def test_business_logic():
    """Test that business logic controllers work"""
    try:
        from curioshelf.models import AssetManager
        from curioshelf.business_logic_v2 import SourcesController, TemplatesController, ObjectsController
        from curioshelf.ui_mocks import MockUIFactory
        
        # Create asset manager
        asset_manager = AssetManager()
        
        # Create controllers
        sources_controller = SourcesController(asset_manager, MockUIFactory)
        templates_controller = TemplatesController(asset_manager, MockUIFactory)
        objects_controller = ObjectsController(asset_manager, MockUIFactory)
        
        # Setup UI
        sources_controller.setup_ui(MockUIFactory)
        templates_controller.setup_ui(MockUIFactory)
        objects_controller.setup_ui(MockUIFactory)
        
        print("✅ Business logic controllers work correctly")
        return True
    except Exception as e:
        print(f"❌ Business logic error: {e}")
        return False

def test_application():
    """Test that the application can be created"""
    try:
        from gui.tabbed_main_window_v2 import TabbedMainWindowV2
        
        # Create QApplication
        app = QApplication(sys.argv)
        
        # Create main window
        window = TabbedMainWindowV2()
        
        # Check that window was created
        assert window is not None
        assert window.asset_manager is not None
        assert window.tab_widget is not None
        assert window.tab_widget.count() == 3  # Sources, Templates, Objects
        
        print("✅ Application creation successful")
        return True
    except Exception as e:
        print(f"❌ Application error: {e}")
        return False

def main():
    """Run all tests"""
    print("🧪 Testing CurioShelf V2 Application")
    print("=" * 50)
    
    tests = [
        ("Import Test", test_imports),
        ("Business Logic Test", test_business_logic),
        ("Application Test", test_application),
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n🔍 Running {test_name}...")
        if test_func():
            passed += 1
        else:
            print(f"❌ {test_name} failed")
    
    print("\n" + "=" * 50)
    print(f"📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("✅ All tests passed! V2 application is ready.")
        return 0
    else:
        print("❌ Some tests failed. Check the errors above.")
        return 1

if __name__ == "__main__":
    sys.exit(main())

