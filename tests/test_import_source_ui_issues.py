"""
Tests for import source UI issues

This module tests the specific UI issues with import source functionality:
1. File dialog method availability
2. Import source through main window
3. File dialog result execution
"""

import pytest
import tempfile
from pathlib import Path
from unittest.mock import Mock, patch

from curioshelf.ui.ui_factory import create_ui_factory
from curioshelf.app_impl.application_impl import CurioShelfApplicationImpl
from curioshelf.ui.main_window_with_views import MainWindowWithViews
from curioshelf.config import config


class TestImportSourceUIIssues:
    """Test import source UI issues"""
    
    def test_file_dialog_methods_exist(self):
        """Test that file dialog has all required methods"""
        # Create UI factory
        ui_factory = create_ui_factory("script", verbose=False)
        ui_impl = ui_factory.get_ui_implementation()
        ui_impl.initialize()
        
        # Create file dialog
        file_dialog = ui_impl.create_file_dialog()
        
        # Test if the required methods exist
        required_methods = ['get_open_file_name', 'get_save_file_name', 'get_existing_directory']
        missing_methods = []
        
        for method_name in required_methods:
            if not hasattr(file_dialog, method_name):
                missing_methods.append(method_name)
        
        assert not missing_methods, f"Missing methods: {missing_methods}"
    
    def test_file_dialog_methods_callable(self):
        """Test that file dialog methods are callable"""
        # Create UI factory
        ui_factory = create_ui_factory("script", verbose=False)
        ui_impl = ui_factory.get_ui_implementation()
        ui_impl.initialize()
        
        # Create file dialog
        file_dialog = ui_impl.create_file_dialog()
        
        # Test get_open_file_name
        result = file_dialog.get_open_file_name(
            "Import Source Image",
            "Image Files (*.png *.jpg *.jpeg *.svg *.bmp *.gif);;All Files (*)",
            str(Path.home())
        )
        # Should not raise an exception, result can be None for script UI
        assert result is None or isinstance(result, str)
        
        # Test get_save_file_name
        result = file_dialog.get_save_file_name(
            "Save File",
            "All Files (*)"
        )
        assert result is None or isinstance(result, str)
        
        # Test get_existing_directory
        result = file_dialog.get_existing_directory(
            "Select Directory",
            str(Path.home())
        )
        assert result is None or isinstance(result, str)
    
    def test_import_source_with_project(self):
        """Test import source functionality with a loaded project"""
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
            assert app.is_project_loaded(), "Project should be loaded"
            
            # Test import source method exists and is callable
            assert hasattr(main_window, '_on_import_source'), "Main window should have _on_import_source method"
            
            # Test that import source can be called without error
            try:
                main_window._on_import_source()
            except Exception as e:
                pytest.fail(f"Import source should not raise exception: {e}")
    
    def test_import_source_with_mock_file(self):
        """Test import source with a mock file"""
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
            
            # Create a mock image file
            mock_image_path = Path(temp_dir) / "test_image.png"
            mock_image_path.write_bytes(b"fake png data")
            
            # Mock the file dialog to return our test file
            original_create_file_dialog = ui_impl.create_file_dialog
            
            def mock_create_file_dialog():
                dialog = original_create_file_dialog()
                # Override the get_open_file_name method to return our test file
                def mock_get_open_file_name(title, filter_str="", directory=""):
                    return str(mock_image_path)
                dialog.get_open_file_name = mock_get_open_file_name
                return dialog
            
            ui_impl.create_file_dialog = mock_create_file_dialog
            
            try:
                # Test import source
                main_window._on_import_source()
                
                # Check if the source was added to the asset manager
                assert app.asset_manager is not None, "Asset manager should exist"
                assert len(app.asset_manager.sources) > 0, "Source should be added to asset manager"
                
            finally:
                ui_impl.create_file_dialog = original_create_file_dialog
    
    def test_event_execution_layer_file_dialog_method(self):
        """Test that EventExecutionLayer has execute_file_dialog_result method"""
        from curioshelf.event_execution_layer import EventExecutionLayer
        from curioshelf.app_impl.application_impl import CurioShelfApplicationImpl
        
        # Create application
        app = CurioShelfApplicationImpl()
        
        # Create event execution layer
        event_layer = EventExecutionLayer(app)
        
        # Test that the method exists
        assert hasattr(event_layer, 'execute_file_dialog_result'), "EventExecutionLayer should have execute_file_dialog_result method"
        
        # Test that the method is callable
        try:
            event_layer.execute_file_dialog_result("import_source", None)
        except Exception as e:
            pytest.fail(f"execute_file_dialog_result should not raise exception: {e}")
    
    def test_import_source_integration(self):
        """Test complete import source integration"""
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
            
            # Create a mock image file
            mock_image_path = Path(temp_dir) / "test_image.png"
            mock_image_path.write_bytes(b"fake png data")
            
            # Mock the file dialog to return our test file
            original_create_file_dialog = ui_impl.create_file_dialog
            
            def mock_create_file_dialog():
                dialog = original_create_file_dialog()
                # Override the get_open_file_name method to return our test file
                def mock_get_open_file_name(title, filter_str="", directory=""):
                    return str(mock_image_path)
                dialog.get_open_file_name = mock_get_open_file_name
                return dialog
            
            ui_impl.create_file_dialog = mock_create_file_dialog
            
            try:
                # Test import source
                main_window._on_import_source()
                
                # Verify the source was imported
                assert app.asset_manager is not None, "Asset manager should exist"
                assert len(app.asset_manager.sources) > 0, "Source should be added to asset manager"
                
                # Get the imported source
                sources = list(app.asset_manager.sources.values())
                assert len(sources) == 1, "Should have exactly one source"
                
                source = sources[0]
                # The source file path should be relative to the project (sources/test_image.png)
                # because the application copies the file to the project's sources directory
                expected_relative_path = Path("sources") / mock_image_path.name
                assert source.file_path == expected_relative_path, f"Source file path should be {expected_relative_path}, got {source.file_path}"
                
            finally:
                ui_impl.create_file_dialog = original_create_file_dialog


# Mark tests that require script UI
pytestmark = pytest.mark.script
