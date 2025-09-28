#!/usr/bin/env python3
"""
Test suite for UI layout patterns to ensure all components follow the correct patterns
"""

import sys
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from curioshelf.ui.ui_factory import create_ui_factory
from curioshelf.ui.views.project_create_view import ProjectCreateView
from curioshelf.ui.views.project_open_view import ProjectOpenView
from curioshelf.ui.views.sources_list_view import SourcesListView


def test_project_create_view_layout():
    """Test project create view layout patterns"""
    print("Testing Project Create View Layout...")
    
    try:
        factory = create_ui_factory("script", verbose=False)
        ui_impl = factory.get_ui_implementation()
        ui_impl.initialize()
        
        def on_create(name, path):
            print(f"Project created: {name} at {path}")
        
        def on_cancel():
            print("Project creation cancelled")
        
        view = ProjectCreateView(ui_impl, on_create=on_create, on_cancel=on_cancel)
        
        # Verify all components exist
        assert view.widget is not None
        assert hasattr(view, 'name_input')
        assert hasattr(view, 'path_input')
        assert hasattr(view, 'browse_btn')
        assert hasattr(view, 'create_btn')
        assert hasattr(view, 'cancel_btn')
        
        # Test functionality
        view.name_input.set_text("Test Project")
        assert view.name_input.get_text() == "Test Project"
        
        print("✓ Project Create View layout test passed")
        return True
        
    except Exception as e:
        print(f"✗ Project Create View layout test failed: {e}")
        return False


def test_project_open_view_layout():
    """Test project open view layout patterns"""
    print("Testing Project Open View Layout...")
    
    try:
        factory = create_ui_factory("script", verbose=False)
        ui_impl = factory.get_ui_implementation()
        ui_impl.initialize()
        
        def on_open(project_path):
            print(f"Project opened: {project_path}")
        
        def on_cancel():
            print("Project opening cancelled")
        
        view = ProjectOpenView(ui_impl, on_open=on_open, on_cancel=on_cancel)
        
        # Verify all components exist
        assert view.widget is not None
        assert hasattr(view, 'project_path_input')
        assert hasattr(view, 'browse_btn')
        assert hasattr(view, 'open_from_path_btn')
        assert hasattr(view, 'projects_list')
        assert hasattr(view, 'open_btn')
        assert hasattr(view, 'refresh_btn')
        assert hasattr(view, 'cancel_btn')
        
        # Test functionality
        view.project_path_input.set_text("/test/path")
        assert view.project_path_input.get_text() == "/test/path"
        
        print("✓ Project Open View layout test passed")
        return True
        
    except Exception as e:
        print(f"✗ Project Open View layout test failed: {e}")
        return False


def test_sources_list_view_layout():
    """Test sources list view layout patterns"""
    print("Testing Sources List View Layout...")
    
    try:
        factory = create_ui_factory("script", verbose=False)
        ui_impl = factory.get_ui_implementation()
        ui_impl.initialize()
        
        def on_import_source():
            print("Import source clicked")
        
        view = SourcesListView(ui_impl, on_import_source=on_import_source)
        
        # Verify all components exist
        assert view.widget is not None
        assert hasattr(view, 'sources_list')
        assert hasattr(view, 'import_btn')
        assert hasattr(view, 'remove_btn')
        assert hasattr(view, 'empty_label')
        
        # Test functionality
        assert not view.remove_btn.is_enabled()  # Should be disabled initially
        assert view.empty_label.is_visible()  # Should be visible initially
        
        print("✓ Sources List View layout test passed")
        return True
        
    except Exception as e:
        print(f"✗ Sources List View layout test failed: {e}")
        return False


def test_layout_patterns():
    """Test all UI layout patterns"""
    print("=" * 60)
    print("UI LAYOUT PATTERNS TEST SUITE")
    print("=" * 60)
    
    tests = [
        test_project_create_view_layout,
        test_project_open_view_layout,
        test_sources_list_view_layout,
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        if test():
            passed += 1
        print()
    
    print("=" * 60)
    print(f"RESULTS: {passed}/{total} tests passed")
    print("=" * 60)
    
    if passed == total:
        print("🎉 All UI layout pattern tests passed!")
        return True
    else:
        print("❌ Some UI layout pattern tests failed!")
        return False


if __name__ == "__main__":
    success = test_layout_patterns()
    sys.exit(0 if success else 1)
