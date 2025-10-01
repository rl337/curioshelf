"""
Test project selection functionality with Qt UI implementation
"""

import pytest
from pathlib import Path
import tempfile
import os

from curioshelf.ui.ui_factory import create_ui_factory
from curioshelf.ui.main_window_with_views import MainWindowWithViews
from curioshelf.app_impl.application_impl import CurioShelfApplicationImpl


class TestQtProjectSelection:
    """Test project selection with Qt UI implementation"""
    
    def test_qt_project_selection_signal_emission(self):
        """Test that Qt UI correctly emits item_selected signal with item object"""
        # Create Qt UI factory
        ui_factory = create_ui_factory("qt", verbose=False)
        ui_impl = ui_factory.get_ui_implementation()
        ui_impl.initialize()
        
        # Create application
        app = CurioShelfApplicationImpl(ui_factory)
        
        # Create main window
        main_window = MainWindowWithViews(ui_impl, app)
        
        # Get the project open view
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
            assert projects_list.get_item_count() > 0, "Should have recent projects"
            
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
            assert received_item is not None, "Should have received an item"
            assert hasattr(received_item, 'get_data'), "Item should have get_data method"
            assert received_item.get_data("path") is not None, "Item should have path data"
            assert received_item.get_data("name") is not None, "Item should have name data"
    
    def test_qt_project_selection_integration(self):
        """Test full project selection integration with Qt UI"""
        # Create Qt UI factory
        ui_factory = create_ui_factory("qt", verbose=False)
        ui_impl = ui_factory.get_ui_implementation()
        ui_impl.initialize()
        
        # Create application
        app = CurioShelfApplicationImpl(ui_factory)
        
        # Create main window
        main_window = MainWindowWithViews(ui_impl, app)
        
        # Get the project open view
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
            assert not project_open_view.open_btn.is_enabled(), "Open button should be disabled initially"
            
            # Simulate selecting a project
            projects_list = project_open_view.projects_list
            projects_list.set_current_index(0)
            
            # Test that the open button is now enabled
            assert project_open_view.open_btn.is_enabled(), "Open button should be enabled after selection"
