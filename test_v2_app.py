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
        from gui.main_window_abstracted import MainWindowAbstracted
        from gui.sources_tab_abstracted import SourcesTabAbstracted
        from gui.objects_tab_abstracted import ObjectsTabAbstracted
        from gui.templates_tab_abstracted import TemplatesTabAbstracted
        from curioshelf.business_logic_v2 import SourcesController, TemplatesController, ObjectsController
        from curioshelf.ui_mocks import MockUIFactory
        from gui.ui_factory import create_ui_factory
        print("✅ All V2 imports successful")
    except Exception as e:
        print(f"❌ Import error: {e}")
        assert False, f"Import error: {e}"

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
    except Exception as e:
        print(f"❌ Business logic error: {e}")
        assert False, f"Business logic error: {e}"

def test_application():
    """Test that the application can be created"""
    try:
        from gui.ui_factory import create_ui_factory
        
        # Create UI factory
        factory = create_ui_factory("headless", verbose=False)
        
        # Create main window
        window = factory.create_main_window()
        
        # Check that window was created
        assert window is not None
        assert hasattr(window, 'asset_manager')
        assert hasattr(window, 'tab_widget')
        
        print("✅ Application creation successful")
    except Exception as e:
        print(f"❌ Application error: {e}")
        assert False, f"Application error: {e}"

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
        try:
            test_func()
            passed += 1
        except AssertionError as e:
            print(f"❌ {test_name} failed: {e}")
        except Exception as e:
            print(f"❌ {test_name} failed with unexpected error: {e}")
    
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

