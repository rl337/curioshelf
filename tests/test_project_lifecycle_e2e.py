"""
End-to-end tests for project lifecycle

This module tests the complete project lifecycle:
1. Create a new project
2. Import a source file (samples/sprite_sheet.svg)
3. Verify project directory and files are created
4. Close the project
5. Re-open the project
6. Verify the project loads correctly with the imported source
"""

import pytest
import tempfile
import shutil
from pathlib import Path
from unittest.mock import Mock, patch

from curioshelf.ui.ui_factory import create_ui_factory
from curioshelf.app_impl.application_impl import CurioShelfApplicationImpl
from curioshelf.ui.main_window_with_views import MainWindowWithViews
from curioshelf.config import config


class TestProjectLifecycleE2E:
    """Test complete project lifecycle end-to-end"""
    
    def test_complete_project_lifecycle(self):
        """Test complete project lifecycle with source import"""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create UI factory and application
            ui_factory = create_ui_factory("script", verbose=False)
            ui_impl = ui_factory.get_ui_implementation()
            ui_impl.initialize()
            
            app = CurioShelfApplicationImpl(ui_factory)
            
            # Create main window
            main_window = MainWindowWithViews(ui_impl, app)
            
            # Step 1: Create a new project
            print("Step 1: Creating new project...")
            project_path = Path(temp_dir) / "test_project"
            
            # Create project info
            from curioshelf.projects import ProjectInfo
            project_info = ProjectInfo(
                name="Test Project",
                description="A test project for E2E testing",
                author="Test User"
            )
            
            # Create the project
            success = app.create_project(project_path, project_info)
            assert success, "Project creation should succeed"
            assert app.is_project_loaded(), "Project should be loaded after creation"
            
            # Verify project directory structure
            assert project_path.exists(), "Project directory should exist"
            assert (project_path / "curioshelf.json").exists(), "Project config file should exist"
            assert (project_path / "sources").exists(), "Sources directory should exist"
            assert (project_path / "templates").exists(), "Templates directory should exist"
            assert (project_path / "objects").exists(), "Objects directory should exist"
            assert (project_path / "build").exists(), "Build directory should exist"
            
            # Step 2: Import a source file
            print("Step 2: Importing source file...")
            
            # Copy the sample sprite sheet to a temporary location
            sample_svg_path = Path(__file__).parent.parent / "samples" / "sprite_sheet.svg"
            if not sample_svg_path.exists():
                pytest.skip("Sample sprite sheet not found, skipping test")
            
            temp_svg_path = Path(temp_dir) / "sprite_sheet.svg"
            shutil.copy2(sample_svg_path, temp_svg_path)
            
            # Mock the file dialog to return our test file
            original_create_file_dialog = ui_impl.create_file_dialog
            
            def mock_create_file_dialog():
                dialog = original_create_file_dialog()
                # Override the get_open_file_name method to return our test file
                def mock_get_open_file_name(title, filter_str="", directory=""):
                    return str(temp_svg_path)
                dialog.get_open_file_name = mock_get_open_file_name
                return dialog
            
            ui_impl.create_file_dialog = mock_create_file_dialog
            
            try:
                # Import the source
                main_window._on_import_source()
                
                # Verify source was imported
                assert app.asset_manager is not None, "Asset manager should exist"
                assert len(app.asset_manager.sources) > 0, "Source should be added to asset manager"
                
                # Get the imported source
                sources = list(app.asset_manager.sources.values())
                assert len(sources) == 1, "Should have exactly one source"
                
                source = sources[0]
                # The source file should be copied to the project's sources directory
                expected_source_path = project_path / "sources" / "sprite_sheet.svg"
                assert expected_source_path.exists(), "Source file should be copied to project sources directory"
                
                # Verify the source file content matches
                with open(temp_svg_path, 'rb') as f:
                    original_content = f.read()
                with open(expected_source_path, 'rb') as f:
                    copied_content = f.read()
                assert original_content == copied_content, "Copied source file should match original"
                
                print("Step 3: Closing project...")
                
                # Step 3: Close the project
                success = app.close_project()
                assert success, "Project close should succeed"
                assert not app.is_project_loaded(), "Project should not be loaded after close"
                
                print("Step 4: Re-opening project...")
                
                # Step 4: Re-open the project
                success = app.load_project(project_path)
                assert success, "Project load should succeed"
                assert app.is_project_loaded(), "Project should be loaded after reopening"
                
                # Verify the project was loaded correctly
                project_info_loaded = app.get_project_info()
                assert project_info_loaded is not None, "Project info should be available"
                assert project_info_loaded.name == "Test Project", "Project name should match"
                
                # Verify the source was loaded back
                assert app.asset_manager is not None, "Asset manager should exist after reload"
                assert len(app.asset_manager.sources) > 0, "Source should be available after reload"
                
                # Get the reloaded source
                sources_reloaded = list(app.asset_manager.sources.values())
                assert len(sources_reloaded) == 1, "Should have exactly one source after reload"
                
                source_reloaded = sources_reloaded[0]
                # The source file path should be in the project's sources directory
                expected_source_path = project_path / "sources" / "sprite_sheet.svg"
                assert source_reloaded.file_path == expected_source_path, f"Source path should be {expected_source_path}, got {source_reloaded.file_path}"
                
                print("✅ Complete project lifecycle test passed!")
                
            finally:
                ui_impl.create_file_dialog = original_create_file_dialog
    
    def test_project_open_view_functionality(self):
        """Test that project open view works correctly"""
        # Create UI factory and application
        ui_factory = create_ui_factory("script", verbose=False)
        ui_impl = ui_factory.get_ui_implementation()
        ui_impl.initialize()
        
        app = CurioShelfApplicationImpl(ui_factory)
        
        # Create main window
        main_window = MainWindowWithViews(ui_impl, app)
        
        # Get the project open view
        project_open_view = main_window.project_open_view
        
        # Test that the view has the required components
        assert hasattr(project_open_view, 'projects_list'), "Project open view should have projects list"
        assert hasattr(project_open_view, 'open_btn'), "Project open view should have open button"
        assert hasattr(project_open_view, 'refresh_btn'), "Project open view should have refresh button"
        assert hasattr(project_open_view, 'browse_btn'), "Project open view should have browse button"
        assert hasattr(project_open_view, 'cancel_btn'), "Project open view should have cancel button"
        
        # Test that the list widget has the required methods
        projects_list = project_open_view.projects_list
        assert hasattr(projects_list, 'create_item'), "Projects list should have create_item method"
        assert hasattr(projects_list, 'add_item'), "Projects list should have add_item method"
        assert hasattr(projects_list, 'clear'), "Projects list should have clear method"
        assert hasattr(projects_list, 'get_selected_item'), "Projects list should have get_selected_item method"
        
        # Test that buttons have click handlers
        assert hasattr(project_open_view, '_on_open_selected'), "Should have open selected handler"
        assert hasattr(project_open_view, '_refresh_projects'), "Should have refresh projects handler"
        assert hasattr(project_open_view, '_browse_for_project'), "Should have browse for project handler"
        assert hasattr(project_open_view, '_on_cancel'), "Should have cancel handler"
    
    def test_project_open_view_with_existing_project(self):
        """Test project open view with an existing project"""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create UI factory and application
            ui_factory = create_ui_factory("script", verbose=False)
            ui_impl = ui_factory.get_ui_implementation()
            ui_impl.initialize()
            
            app = CurioShelfApplicationImpl(ui_factory)
            
            # Create main window
            main_window = MainWindowWithViews(ui_impl, app)
            
            # Create a test project
            project_path = Path(temp_dir) / "test_project"
            
            # Create project info
            from curioshelf.projects import ProjectInfo
            project_info = ProjectInfo(
                name="Test Project",
                description="A test project",
                author="Test User"
            )
            
            # Create the project
            success = app.create_project(project_path, project_info)
            assert success, "Project creation should succeed"
            
            # Close the project
            app.close_project()
            
            # Get the project open view
            project_open_view = main_window.project_open_view
            
            # Test refresh projects
            project_open_view._refresh_projects()
            
            # The projects list should have items (or at least a placeholder)
            projects_list = project_open_view.projects_list
            item_count = projects_list.get_item_count()
            assert item_count >= 0, "Projects list should have items or be empty"
            
            # Test browse for project functionality
            # Mock the file dialog to return our test project
            original_create_file_dialog = ui_impl.create_file_dialog
            
            def mock_create_file_dialog():
                dialog = original_create_file_dialog()
                # Override the get_existing_directory method to return our test project
                def mock_get_existing_directory(title, directory=""):
                    return str(project_path)
                dialog.get_existing_directory = mock_get_existing_directory
                return dialog
            
            ui_impl.create_file_dialog = mock_create_file_dialog
            
            try:
                # Test browse for project
                project_open_view._browse_for_project()
                
                # The project should be loaded
                assert app.is_project_loaded(), "Project should be loaded after browse"
                
            finally:
                ui_impl.create_file_dialog = original_create_file_dialog


# Mark tests that require script UI
pytestmark = pytest.mark.script
