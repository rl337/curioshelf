"""
Tests for project creation and opening functionality
"""

import pytest
import tempfile
from pathlib import Path
from unittest.mock import Mock, patch

from curioshelf.app_impl.application_impl import CurioShelfApplicationImpl
from curioshelf.mock_application import MockCurioShelfApplication
from curioshelf.projects import ProjectMetadata, ProjectStructureManager
from curioshelf.event_execution_layer import EventExecutor
from curioshelf.event_system import UIEvent, EventType, event_bus


class TestProjectCreation:
    """Test project creation functionality"""
    
    def test_create_project_with_metadata(self):
        """Test creating a project with ProjectMetadata"""
        app = CurioShelfApplicationImpl()
        
        with tempfile.TemporaryDirectory() as temp_dir:
            project_path = Path(temp_dir) / "test_project"
            
            metadata = ProjectMetadata(
                name="Test Project",
                description="A test project",
                author="Test User",
                version="1.0.0"
            )
            
            # Create project
            success = app.create_project(project_path, metadata)
            
            assert success, "Project creation should succeed"
            assert app.is_project_loaded(), "Project should be loaded after creation"
            assert project_path.exists(), "Project directory should exist"
            assert (project_path / "curioshelf.json").exists(), "Project config file should exist"
            
            # Verify project structure
            assert (project_path / "sources").exists(), "Sources directory should exist"
            assert (project_path / "templates").exists(), "Templates directory should exist"
            assert (project_path / "objects").exists(), "Objects directory should exist"
            assert (project_path / "build").exists(), "Build directory should exist"
            assert (project_path / "config").exists(), "Config directory should exist"
    
    def test_create_project_with_legacy_info(self):
        """Test creating a project with legacy ProjectInfo"""
        from curioshelf.projects import ProjectInfo
        
        app = CurioShelfApplicationImpl()
        
        with tempfile.TemporaryDirectory() as temp_dir:
            project_path = Path(temp_dir) / "test_project"
            
            project_info = ProjectInfo(
                name="Test Project",
                description="A test project",
                author="Test User",
                version="1.0.0"
            )
            
            # Create project
            success = app.create_project(project_path, project_info)
            
            assert success, "Project creation should succeed"
            assert app.is_project_loaded(), "Project should be loaded after creation"
            assert project_path.exists(), "Project directory should exist"
    
    def test_create_project_failure(self):
        """Test project creation failure handling"""
        app = CurioShelfApplicationImpl()
        
        # Try to create project in invalid location
        invalid_path = Path("/invalid/path/that/does/not/exist")
        
        metadata = ProjectMetadata(
            name="Test Project",
            description="A test project",
            author="Test User"
        )
        
        # This should fail
        success = app.create_project(invalid_path, metadata)
        
        assert not success, "Project creation should fail with invalid path"
        assert not app.is_project_loaded(), "Project should not be loaded after failed creation"
    
    def test_project_metadata_serialization(self):
        """Test that project metadata can be serialized to JSON"""
        metadata = ProjectMetadata(
            name="Test Project",
            description="A test project",
            author="Test User",
            version="1.0.0"
        )
        
        # Convert to dict
        metadata_dict = metadata.to_dict()
        
        assert metadata_dict["name"] == "Test Project"
        assert metadata_dict["description"] == "A test project"
        assert metadata_dict["author"] == "Test User"
        assert metadata_dict["version"] == "1.0.0"
        assert "created" in metadata_dict
        assert "modified" in metadata_dict


class TestProjectOpening:
    """Test project opening functionality"""
    
    def test_open_existing_project(self):
        """Test opening an existing project"""
        app = CurioShelfApplicationImpl()
        
        with tempfile.TemporaryDirectory() as temp_dir:
            project_path = Path(temp_dir) / "test_project"
            
            # Create a project first
            metadata = ProjectMetadata(
                name="Test Project",
                description="A test project",
                author="Test User"
            )
            
            create_success = app.create_project(project_path, metadata)
            assert create_success, "Project creation should succeed"
            
            # Close the project
            app.close_project()
            assert not app.is_project_loaded(), "Project should be closed"
            
            # Open the project
            open_success = app.load_project(project_path)
            assert open_success, "Project opening should succeed"
            assert app.is_project_loaded(), "Project should be loaded after opening"
    
    def test_open_nonexistent_project(self):
        """Test opening a project that doesn't exist"""
        app = CurioShelfApplicationImpl()
        
        with tempfile.TemporaryDirectory() as temp_dir:
            nonexistent_path = Path(temp_dir) / "nonexistent_project"
            
            # Try to open non-existent project
            success = app.load_project(nonexistent_path)
            
            assert not success, "Opening non-existent project should fail"
            assert not app.is_project_loaded(), "Project should not be loaded"
    
    def test_open_invalid_project(self):
        """Test opening a directory that's not a valid project"""
        app = CurioShelfApplicationImpl()
        
        with tempfile.TemporaryDirectory() as temp_dir:
            invalid_project_path = Path(temp_dir) / "not_a_project"
            invalid_project_path.mkdir()
            
            # Try to open invalid project
            success = app.load_project(invalid_project_path)
            
            assert not success, "Opening invalid project should fail"
            assert not app.is_project_loaded(), "Project should not be loaded"


class TestProjectStructureManager:
    """Test the ProjectStructureManager directly"""
    
    def test_create_project_structure(self):
        """Test creating project structure"""
        manager = ProjectStructureManager()
        
        with tempfile.TemporaryDirectory() as temp_dir:
            project_path = Path(temp_dir) / "test_project"
            
            metadata = ProjectMetadata(
                name="Test Project",
                description="A test project",
                author="Test User"
            )
            
            # Create project
            success = manager.create_project(project_path, metadata)
            
            assert success, "Project creation should succeed"
            assert project_path.exists(), "Project directory should exist"
            assert (project_path / "curioshelf.json").exists(), "Config file should exist"
            
            # Verify all directories exist
            for dir_name in ["sources", "templates", "objects", "build", "config"]:
                assert (project_path / dir_name).exists(), f"{dir_name} directory should exist"
    
    def test_load_project_structure(self):
        """Test loading project structure"""
        manager = ProjectStructureManager()
        
        with tempfile.TemporaryDirectory() as temp_dir:
            project_path = Path(temp_dir) / "test_project"
            
            # Create a project
            metadata = ProjectMetadata(
                name="Test Project",
                description="A test project",
                author="Test User"
            )
            
            create_success = manager.create_project(project_path, metadata)
            assert create_success, "Project creation should succeed"
            
            # Load the project
            structure = manager.load_project(project_path)
            
            assert structure is not None, "Project structure should be loaded"
            assert structure.metadata.name == "Test Project"
            assert structure.metadata.description == "A test project"
            assert structure.metadata.author == "Test User"
    
    def test_is_project(self):
        """Test project detection"""
        manager = ProjectStructureManager()
        
        with tempfile.TemporaryDirectory() as temp_dir:
            project_path = Path(temp_dir) / "test_project"
            
            # Initially not a project
            assert not manager.is_project(project_path), "Should not be a project initially"
            
            # Create a project
            metadata = ProjectMetadata(
                name="Test Project",
                description="A test project",
                author="Test User"
            )
            
            manager.create_project(project_path, metadata)
            
            # Now should be a project
            assert manager.is_project(project_path), "Should be a project after creation"


class TestEventExecution:
    """Test event execution for project operations"""
    
    def test_new_project_event(self):
        """Test new project event execution"""
        app = MockCurioShelfApplication()
        executor = EventExecutor(app)
        
        # Capture events
        events = []
        def capture_event(event):
            events.append(event)
        
        event_bus.subscribe(EventType.SUCCESS, capture_event)
        event_bus.subscribe(EventType.ERROR, capture_event)
        
        # Execute new project command
        executor._execute_new_project({})
        
        # Should have emitted a success event
        success_events = [e for e in events if e.event_type == EventType.SUCCESS]
        assert len(success_events) > 0, "Should emit success event"
        
        # Project should be created
        assert app.is_project_loaded(), "Project should be loaded after creation"
    
    def test_open_project_event(self):
        """Test open project event execution"""
        app = MockCurioShelfApplication()
        executor = EventExecutor(app)
        
        # Capture events
        events = []
        def capture_event(event):
            events.append(event)
        
        event_bus.subscribe(EventType.SUCCESS, capture_event)
        event_bus.subscribe(EventType.ERROR, capture_event)
        
        # Execute open project command
        executor._execute_open_project({})
        
        # Should have emitted a success event
        success_events = [e for e in events if e.event_type == EventType.SUCCESS]
        assert len(success_events) > 0, "Should emit success event"
        
        # Project should be loaded
        assert app.is_project_loaded(), "Project should be loaded after opening"
    
    def test_save_project_event(self):
        """Test save project event execution"""
        app = MockCurioShelfApplication()
        executor = EventExecutor(app)
        
        # Create a project first
        from curioshelf.projects import ProjectInfo
        project_info = ProjectInfo(name="Test", author="User", description="Test")
        app.create_project(Path("/tmp/test"), project_info)
        
        # Capture events
        events = []
        def capture_event(event):
            events.append(event)
        
        event_bus.subscribe(EventType.SUCCESS, capture_event)
        event_bus.subscribe(EventType.ERROR, capture_event)
        
        # Execute save project command
        executor._execute_save_project({})
        
        # Should have emitted a success event
        success_events = [e for e in events if e.event_type == EventType.SUCCESS]
        assert len(success_events) > 0, "Should emit success event"
    
    def test_close_project_event(self):
        """Test close project event execution"""
        app = MockCurioShelfApplication()
        executor = EventExecutor(app)
        
        # Create a project first
        from curioshelf.projects import ProjectInfo
        project_info = ProjectInfo(name="Test", author="User", description="Test")
        app.create_project(Path("/tmp/test"), project_info)
        
        assert app.is_project_loaded(), "Project should be loaded initially"
        
        # Capture events
        events = []
        def capture_event(event):
            events.append(event)
        
        event_bus.subscribe(EventType.SUCCESS, capture_event)
        event_bus.subscribe(EventType.ERROR, capture_event)
        
        # Execute close project command
        executor._execute_close_project({})
        
        # Should have emitted a success event
        success_events = [e for e in events if e.event_type == EventType.SUCCESS]
        assert len(success_events) > 0, "Should emit success event"
        
        # Project should be closed
        assert not app.is_project_loaded(), "Project should be closed after close command"


class TestProjectIntegration:
    """Integration tests for project functionality"""
    
    def test_full_project_lifecycle(self):
        """Test complete project lifecycle: create, use, save, close, reopen"""
        app = CurioShelfApplicationImpl()
        
        with tempfile.TemporaryDirectory() as temp_dir:
            project_path = Path(temp_dir) / "lifecycle_test"
            
            # 1. Create project
            metadata = ProjectMetadata(
                name="Lifecycle Test",
                description="Testing full project lifecycle",
                author="Test User"
            )
            
            create_success = app.create_project(project_path, metadata)
            assert create_success, "Project creation should succeed"
            assert app.is_project_loaded(), "Project should be loaded"
            
            # 2. Add some content (sources, objects, templates)
            # Import a source
            source_path = project_path / "sources" / "test_image.png"
            source_path.touch()  # Create empty file
            app.import_source(source_path)
            
            # Create an object
            app.create_object("test_object")
            
            # Create a template
            app.create_template("test_template")
            
            # 3. Save project
            save_success = app.save_project()
            assert save_success, "Project save should succeed"
            
            # 4. Close project
            close_success = app.close_project()
            assert close_success, "Project close should succeed"
            assert not app.is_project_loaded(), "Project should be closed"
            
            # 5. Reopen project
            open_success = app.load_project(project_path)
            assert open_success, "Project reopen should succeed"
            assert app.is_project_loaded(), "Project should be loaded again"
            
            # 6. Verify content is still there
            assert app.has_sources(), "Sources should still be there"
            assert app.has_objects(), "Objects should still be there"
            assert app.has_templates(), "Templates should still be there"
    
    def test_project_state_consistency(self):
        """Test that project state is consistent across operations"""
        app = CurioShelfApplicationImpl()
        
        with tempfile.TemporaryDirectory() as temp_dir:
            project_path = Path(temp_dir) / "state_test"
            
            # Create project
            metadata = ProjectMetadata(
                name="State Test",
                description="Testing state consistency",
                author="Test User"
            )
            
            app.create_project(project_path, metadata)
            
            # Test state methods
            assert app.valid_project(), "Project should be valid"
            assert app.can_save_project(), "Should be able to save project"
            assert app.can_close_project(), "Should be able to close project"
            assert app.can_import_source(), "Should be able to import sources"
            assert not app.can_create_object(), "Should not be able to create objects without sources"
            assert not app.can_create_template(), "Should not be able to create templates without objects"
            
            # Add a source
            source_path = project_path / "sources" / "test.png"
            source_path.touch()
            app.import_source(source_path)
            
            # Now should be able to create objects
            assert app.can_create_object(), "Should be able to create objects with sources"
            
            # Create an object
            app.create_object("test_object")
            
            # Now should be able to create templates
            assert app.can_create_template(), "Should be able to create templates with objects"
