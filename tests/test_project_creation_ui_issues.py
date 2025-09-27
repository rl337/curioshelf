"""
Tests for project creation UI issues

This module tests the specific UI issues with project creation:
1. Auto-append of project name to project path
2. Project creation callback parameter handling
"""

import pytest
import tempfile
from pathlib import Path
from unittest.mock import Mock, patch

from curioshelf.ui.ui_factory import create_ui_factory
from curioshelf.app_impl.application_impl import CurioShelfApplicationImpl
from curioshelf.ui.main_window_with_views import MainWindowWithViews
from curioshelf.ui.views.project_create_view import ProjectCreateView
from curioshelf.config import config


class TestProjectCreationUIIssues:
    """Test project creation UI issues"""
    
    def test_project_name_auto_append(self):
        """Test that project name auto-append to path works"""
        # Create UI factory
        ui_factory = create_ui_factory("script", verbose=False)
        ui_impl = ui_factory.get_ui_implementation()
        ui_impl.initialize()
        
        # Create project create view
        project_view = ProjectCreateView(ui_impl)
        
        # Set project name
        project_view.name_input.set_text("Test Project")
        
        # Trigger the name change event
        project_view._on_name_changed("Test Project")
        
        # Wait for timer to trigger (simulate it)
        if project_view.auto_complete_timer:
            project_view.auto_complete_timer.stop()
            project_view._update_project_path()
        
        # Check if path was updated
        current_path = project_view.path_input.get_text()
        expected_path = str(config.get_project_path_for_name("Test Project"))
        
        assert current_path == expected_path, f"Expected path '{expected_path}', got '{current_path}'"
    
    def test_project_creation_callback_parameters(self):
        """Test that project creation callback receives correct parameters"""
        # Create UI factory and application
        ui_factory = create_ui_factory("script", verbose=False)
        ui_impl = ui_factory.get_ui_implementation()
        ui_impl.initialize()
        
        app = CurioShelfApplicationImpl(ui_factory)
        
        # Create main window
        main_window = MainWindowWithViews(ui_impl, app)
        
        # Get the project create view
        project_view = main_window.project_create_view
        
        # Set up test data
        project_view.name_input.set_text("Test Project")
        project_view.path_input.set_text("/tmp/test_project")
        
        # Mock the app.create_project method to capture parameters
        call_args = []
        original_create_project = app.create_project
        
        def mock_create_project(project_path, project_info):
            call_args.append((project_path, project_info))
            # Return success to avoid error handling
            return True
        
        app.create_project = mock_create_project
        
        try:
            # Trigger the create button
            project_view._on_create()
            
            # Verify callback was called with correct parameters
            assert len(call_args) == 1, "create_project should be called exactly once"
            path, info = call_args[0]
            assert isinstance(path, Path), f"Expected Path object, got {type(path)}"
            assert str(path) == "/tmp/test_project", f"Expected path '/tmp/test_project', got '{path}'"
            assert info.name == "Test Project", f"Expected name 'Test Project', got '{info.name}'"
            
        finally:
            app.create_project = original_create_project
    
    def test_project_creation_actual_creation(self):
        """Test actual project creation through the UI"""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create UI factory and application
            ui_factory = create_ui_factory("script", verbose=False)
            ui_impl = ui_factory.get_ui_implementation()
            ui_impl.initialize()
            
            app = CurioShelfApplicationImpl(ui_factory)
            
            # Create main window
            main_window = MainWindowWithViews(ui_impl, app)
            
            # Get the project create view
            project_view = main_window.project_create_view
            
            # Set up test data
            project_view.name_input.set_text("Test Project")
            project_view.path_input.set_text(str(Path(temp_dir) / "test_project"))
            
            # Trigger the create button
            project_view._on_create()
            
            # Check if project was created
            project_path = Path(temp_dir) / "test_project"
            assert project_path.exists(), "Project directory should be created"
            assert (project_path / "curioshelf.json").exists(), "Project config file should be created"
    
    def test_project_creation_with_auto_append_integration(self):
        """Test project creation with auto-append integration"""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create UI factory and application
            ui_factory = create_ui_factory("script", verbose=False)
            ui_impl = ui_factory.get_ui_implementation()
            ui_impl.initialize()
            
            app = CurioShelfApplicationImpl(ui_factory)
            
            # Create main window
            main_window = MainWindowWithViews(ui_impl, app)
            
            # Get the project create view
            project_view = main_window.project_create_view
            
            # Set project name (should trigger auto-append)
            project_view.name_input.set_text("Auto Test Project")
            
            # Trigger the name change event
            project_view._on_name_changed("Auto Test Project")
            
            # Wait for timer to trigger (simulate it)
            if project_view.auto_complete_timer:
                project_view.auto_complete_timer.stop()
                project_view._update_project_path()
            
            # Verify auto-append worked
            current_path = project_view.path_input.get_text()
            expected_path = str(config.get_project_path_for_name("Auto Test Project"))
            assert current_path == expected_path, f"Auto-append failed. Expected '{expected_path}', got '{current_path}'"
            
            # Now test creation with the auto-appended path
            # Override the path to use our temp directory
            project_view.path_input.set_text(str(Path(temp_dir) / "auto_test_project"))
            
            # Trigger the create button
            project_view._on_create()
            
            # Check if project was created
            project_path = Path(temp_dir) / "auto_test_project"
            assert project_path.exists(), "Project directory should be created"
            assert (project_path / "curioshelf.json").exists(), "Project config file should be created"


# Mark tests that require script UI
pytestmark = pytest.mark.script
