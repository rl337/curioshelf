"""
Test all UI implementations to ensure consistency across backends
"""

import pytest
import tempfile
from pathlib import Path
from typing import List, Tuple

from curioshelf.ui.ui_factory import create_ui_factory
from curioshelf.ui.main_window_with_views import MainWindowWithViews
from curioshelf.app_impl.application_impl import CurioShelfApplicationImpl


def get_available_ui_implementations() -> List[str]:
    """Get list of available UI implementations"""
    available = []
    
    # Always test script UI
    available.append("script")
    
    # Test Qt UI if available
    try:
        import PySide6
        available.append("qt")
    except ImportError:
        print("Qt UI not available - PySide6 not installed")
    
    return available


@pytest.fixture(params=get_available_ui_implementations())
def ui_implementation(request):
    """Fixture that provides all available UI implementations"""
    ui_type = request.param
    ui_factory = create_ui_factory(ui_type, verbose=False)
    ui_impl = ui_factory.get_ui_implementation()
    ui_impl.initialize()
    yield ui_impl, ui_type
    # Cleanup if needed
    if hasattr(ui_impl, 'cleanup'):
        ui_impl.cleanup()


class TestAllUIImplementations:
    """Test all UI implementations for consistency"""
    
    def test_ui_initialization(self, ui_implementation):
        """Test that UI implementations can be initialized"""
        ui_impl, ui_type = ui_implementation
        assert ui_impl is not None
        assert hasattr(ui_impl, 'create_widget')
        assert hasattr(ui_impl, 'create_button')
        assert hasattr(ui_impl, 'create_label')
        assert hasattr(ui_impl, 'create_list_widget')
    
    def test_main_window_creation(self, ui_implementation):
        """Test that main window can be created with all UI implementations"""
        ui_impl, ui_type = ui_implementation
        app = CurioShelfApplicationImpl(create_ui_factory(ui_type, verbose=False))
        main_window = MainWindowWithViews(ui_impl, app)
        
        assert main_window is not None
        assert hasattr(main_window, 'project_open_view')
        assert hasattr(main_window, 'project_create_view')
        assert hasattr(main_window, 'sources_view')
    
    def test_project_open_view_creation(self, ui_implementation):
        """Test that project open view can be created with all UI implementations"""
        ui_impl, ui_type = ui_implementation
        app = CurioShelfApplicationImpl(create_ui_factory(ui_type, verbose=False))
        main_window = MainWindowWithViews(ui_impl, app)
        
        project_open_view = main_window.project_open_view
        assert project_open_view is not None
        assert hasattr(project_open_view, 'projects_list')
        assert hasattr(project_open_view, 'open_btn')
        assert hasattr(project_open_view, 'refresh_btn')
        assert hasattr(project_open_view, 'browse_btn')
    
    def test_project_selection_signal_emission(self, ui_implementation):
        """Test that project selection signals work correctly in all UI implementations"""
        ui_impl, ui_type = ui_implementation
        app = CurioShelfApplicationImpl(create_ui_factory(ui_type, verbose=False))
        main_window = MainWindowWithViews(ui_impl, app)
        
        project_open_view = main_window.project_open_view
        
        # Create a test project directory
        with tempfile.TemporaryDirectory() as temp_dir:
            project_path = Path(temp_dir) / "test_project"
            project_path.mkdir()
            (project_path / "curioshelf.json").write_text('{"name": "Test Project"}')
            
            # Add project to recent projects
            from curioshelf.config import config
            config.add_recent_project(project_path, "Test Project")
            
            # Refresh the projects list
            project_open_view._refresh_projects()
            
            # Get the projects list widget
            projects_list = project_open_view.projects_list
            
            # Test that we have items
            assert projects_list.get_item_count() > 0, f"Should have recent projects in {ui_type} UI"
            
            # Test signal emission by connecting to it
            received_item = None
            
            def on_item_selected(item):
                nonlocal received_item
                received_item = item
            
            # Connect to the signal
            projects_list.item_selected.connect(on_item_selected)
            
            # Simulate selection by setting current index
            projects_list.set_current_index(0)
            
            # Check that we received the item object, not an integer
            assert received_item is not None, f"Should have received an item in {ui_type} UI"
            assert hasattr(received_item, 'get_data'), f"Item should have get_data method in {ui_type} UI"
            assert received_item.get_data("path") is not None, f"Item should have path data in {ui_type} UI"
            assert received_item.get_data("name") is not None, f"Item should have name data in {ui_type} UI"
    
    def test_project_selection_button_state(self, ui_implementation):
        """Test that project selection enables/disables buttons correctly in all UI implementations"""
        ui_impl, ui_type = ui_implementation
        app = CurioShelfApplicationImpl(create_ui_factory(ui_type, verbose=False))
        main_window = MainWindowWithViews(ui_impl, app)
        
        project_open_view = main_window.project_open_view
        
        # Create a test project directory
        with tempfile.TemporaryDirectory() as temp_dir:
            project_path = Path(temp_dir) / "test_project"
            project_path.mkdir()
            (project_path / "curioshelf.json").write_text('{"name": "Test Project"}')
            
            # Add project to recent projects
            from curioshelf.config import config
            config.add_recent_project(project_path, "Test Project")
            
            # Refresh the projects list
            project_open_view._refresh_projects()
            
            # Test that the open button is initially disabled
            assert not project_open_view.open_btn.is_enabled(), f"Open button should be disabled initially in {ui_type} UI"
            
            # Simulate selecting a project
            projects_list = project_open_view.projects_list
            projects_list.set_current_index(0)
            
            # Test that the open button is now enabled
            assert project_open_view.open_btn.is_enabled(), f"Open button should be enabled after selection in {ui_type} UI"
    
    def test_project_create_view_creation(self, ui_implementation):
        """Test that project create view can be created with all UI implementations"""
        ui_impl, ui_type = ui_implementation
        app = CurioShelfApplicationImpl(create_ui_factory(ui_type, verbose=False))
        main_window = MainWindowWithViews(ui_impl, app)
        
        project_create_view = main_window.project_create_view
        assert project_create_view is not None
        assert hasattr(project_create_view, 'name_input')
        assert hasattr(project_create_view, 'path_input')
        assert hasattr(project_create_view, 'create_btn')
        assert hasattr(project_create_view, 'cancel_btn')
    
    def test_sources_view_creation(self, ui_implementation):
        """Test that sources view can be created with all UI implementations"""
        ui_impl, ui_type = ui_implementation
        app = CurioShelfApplicationImpl(create_ui_factory(ui_type, verbose=False))
        main_window = MainWindowWithViews(ui_impl, app)
        
        sources_view = main_window.sources_view
        assert sources_view is not None
        assert hasattr(sources_view, 'sources_list')
        assert hasattr(sources_view, 'import_btn')
        assert hasattr(sources_view, 'remove_btn')
    
    def test_project_details_view_creation(self, ui_implementation):
        """Test that project details view can be created with all UI implementations"""
        ui_impl, ui_type = ui_implementation
        app = CurioShelfApplicationImpl(create_ui_factory(ui_type, verbose=False))
        main_window = MainWindowWithViews(ui_impl, app)
        
        project_details_view = main_window.project_details_view
        assert project_details_view is not None
        assert hasattr(project_details_view, 'name_label')
        assert hasattr(project_details_view, 'path_label')
        assert hasattr(project_details_view, 'continue_btn')
        assert hasattr(project_details_view, 'close_btn')


def test_ui_implementation_availability():
    """Test that we can detect available UI implementations"""
    available = get_available_ui_implementations()
    assert len(available) > 0, "Should have at least one UI implementation available"
    assert "script" in available, "Script UI should always be available"
    
    # Print available implementations for debugging
    print(f"Available UI implementations: {available}")


if __name__ == "__main__":
    # Run tests for all available UI implementations
    available = get_available_ui_implementations()
    print(f"Testing UI implementations: {available}")
    
    # Run pytest with the available implementations
    pytest.main([__file__, "-v", f"--tb=short"])
