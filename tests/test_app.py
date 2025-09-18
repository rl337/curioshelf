#!/usr/bin/env python3
"""
Test script for CurioShelf
"""

import sys
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from curioshelf.models import AssetManager, Template, CurioObject, AssetSource, ObjectSlice


def test_models():
    """Test the core data models"""
    print("Testing core data models...")
    
    # Create asset manager
    manager = AssetManager()
    
    # Add a template
    template = manager.add_template(
        "test_character",
        "Test character template",
        ["front", "back", "left", "right"]
    )
    print(f"✓ Created template: {template.name}")
    
    # Add a source
    source = manager.add_source(
        Path("test_image.png"),
        800, 600
    )
    print(f"✓ Created source: {source.id}")
    
    # Add an object
    obj = manager.add_object("test_object", "test_character")
    print(f"✓ Created object: {obj.name}")
    
    # Add a slice
    slice_obj = ObjectSlice(
        name="front",
        source_id=source.id,
        x=100, y=100, width=64, height=64,
        layer="concept"
    )
    source.add_slice(slice_obj)
    obj.slices.append(slice_obj)
    print(f"✓ Created slice: {slice_obj.name}")
    
    # Test completeness
    completeness = manager.get_object_completeness(obj.id)
    print(f"✓ Object completeness: {completeness}")
    
    # Test metadata save/load
    test_file = Path("test_metadata.json")
    manager.save_metadata(test_file)
    print(f"✓ Saved metadata to: {test_file}")
    
    # Create new manager and load
    manager2 = AssetManager()
    manager2.load_metadata(test_file)
    print(f"✓ Loaded metadata: {len(manager2.objects)} objects, {len(manager2.templates)} templates")
    
    # Cleanup
    test_file.unlink()
    print("✓ Cleaned up test file")
    
    print("All model tests passed! ✓")


def test_gui_imports():
    """Test that GUI modules can be imported"""
    print("Testing GUI imports...")
    
    # Test that GUI modules can be imported without errors
    try:
        from curioshelf.ui.ui_factory import create_ui_factory, get_available_ui_backends
        print("✓ UI factory imported successfully")
        
        from curioshelf.ui.main_window_abstracted import MainWindowAbstracted
        print("✓ MainWindowAbstracted imported successfully")
        
        from curioshelf.ui.sources_tab_abstracted import SourcesTabAbstracted
        print("✓ SourcesTabAbstracted imported successfully")
        
        from curioshelf.ui.objects_tab_abstracted import ObjectsTabAbstracted
        print("✓ ObjectsTabAbstracted imported successfully")
        
        from curioshelf.ui.templates_tab_abstracted import TemplatesTabAbstracted
        print("✓ TemplatesTabAbstracted imported successfully")
        
        # Test that we can create a UI factory
        backends = get_available_ui_backends()
        print(f"✓ Available UI backends: {backends}")
        
        print("All GUI imports passed! ✓")
        
    except ImportError as e:
        print(f"✗ GUI import failed: {e}")
        assert False, f"GUI import failed: {e}"


if __name__ == "__main__":
    print("CurioShelf Test Suite")
    print("=" * 40)
    
    try:
        # Test models
        test_models()
        print()
        
        # Test GUI imports
        test_gui_imports()
        print()
        print("All tests passed! The application should work correctly.")
        print()
        print("To run the application:")
        print("  python main.py")
    except AssertionError as e:
        print(f"Test failed: {e}")
        print("Some tests failed. Please check the error messages above.")
        sys.exit(1)
