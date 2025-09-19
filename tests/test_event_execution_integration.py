"""
Comprehensive Integration Tests for Event Execution Layer

This module tests the complete flow from UI events through the event execution layer
to the application interface implementations, using real project structures.
"""

import pytest
import tempfile
from pathlib import Path
from unittest.mock import Mock, patch
import json

from curioshelf.event_execution_layer import EventExecutionLayer, EventExecutor
from curioshelf.event_system import UIEvent, EventType, event_bus
from curioshelf.projects import ProjectMetadata, ProjectStructure, ProjectStructureManager
from curioshelf.app_impl.application_impl import CurioShelfApplicationImpl
from curioshelf.ui.ui_factory import create_ui_factory


class TestEventExecutionIntegration:
    """Test complete event execution flow with real project operations"""
    
    def test_project_creation_flow(self, temp_project_dir):
        """Test complete project creation flow from UI event to file system"""
        # Create UI factory and application
        ui_factory = create_ui_factory("headless", verbose=False)
        app = CurioShelfApplicationImpl(ui_factory)
        event_layer = EventExecutionLayer(app)
        
        # Create project metadata
        metadata = ProjectMetadata(
            name="Test Project",
            description="A test project for integration testing",
            author="Test User"
        )
        
        # Emit project dialog accepted event
        event = UIEvent(
            event_type=EventType.DIALOG_ACCEPTED,
            source="project_dialog",
            data={
                "dialog_type": "project_dialog",
                "is_new_project": True,
                "project_path": str(temp_project_dir),
                "project_info": metadata
            }
        )
        
        # Emit the event
        event_bus.emit(event)
        
        # Verify project was created
        assert (temp_project_dir / "curioshelf.json").exists()
        
        # Load and verify project structure
        project_manager = ProjectStructureManager()
        structure = project_manager.load_project(temp_project_dir)
        assert structure is not None
        assert structure.metadata.name == "Test Project"
        assert structure.metadata.author == "Test User"
        
        # Verify directory structure was created
        assert (temp_project_dir / "sources").exists()
        assert (temp_project_dir / "templates").exists()
        assert (temp_project_dir / "objects").exists()
        assert (temp_project_dir / "build").exists()
        assert (temp_project_dir / "config").exists()
        assert (temp_project_dir / ".gitignore").exists()
    
    def test_project_loading_flow(self, temp_project_with_files):
        """Test project loading flow from UI event"""
        # Create UI factory and application
        ui_factory = create_ui_factory("headless", verbose=False)
        app = CurioShelfApplicationImpl(ui_factory)
        event_layer = EventExecutionLayer(app)
        
        # Emit project dialog accepted event for loading
        event = UIEvent(
            event_type=EventType.DIALOG_ACCEPTED,
            source="project_dialog",
            data={
                "dialog_type": "project_dialog",
                "is_new_project": False,
                "project_path": str(temp_project_with_files)
            }
        )
        
        # Emit the event
        event_bus.emit(event)
        
        # Verify project was loaded
        assert app.is_project_loaded()
        project_info = app.get_project_info()
        assert project_info is not None
        assert project_info.name == "Test Project"
    
    def test_save_project_flow(self, temp_project_with_files):
        """Test project saving flow from UI event"""
        # Create UI factory and application
        ui_factory = create_ui_factory("headless", verbose=False)
        app = CurioShelfApplicationImpl(ui_factory)
        event_layer = EventExecutionLayer(app)
        
        # Load project first
        app.load_project(temp_project_with_files)
        assert app.is_project_loaded()
        
        # Emit save project event
        event = UIEvent(
            event_type=EventType.MENU_ITEM_CLICKED,
            source="main_window",
            data={"menu_item": "save_project"}
        )
        
        # Emit the event
        event_bus.emit(event)
        
        # Verify project was saved (check modified timestamp)
        project_manager = ProjectStructureManager()
        structure = project_manager.load_project(temp_project_with_files)
        assert structure is not None
        # The modified timestamp should be recent
        assert structure.metadata.modified > structure.metadata.created
    
    def test_close_project_flow(self, temp_project_with_files):
        """Test project closing flow from UI event"""
        # Create UI factory and application
        ui_factory = create_ui_factory("headless", verbose=False)
        app = CurioShelfApplicationImpl(ui_factory)
        event_layer = EventExecutionLayer(app)
        
        # Load project first
        app.load_project(temp_project_with_files)
        assert app.is_project_loaded()
        
        # Emit close project event
        event = UIEvent(
            event_type=EventType.MENU_ITEM_CLICKED,
            source="main_window",
            data={"menu_item": "close_project"}
        )
        
        # Emit the event
        event_bus.emit(event)
        
        # Verify project was closed
        assert not app.is_project_loaded()
    
    def test_create_object_flow(self, temp_project_with_files):
        """Test object creation flow from UI event"""
        # Create UI factory and application
        ui_factory = create_ui_factory("headless", verbose=False)
        app = CurioShelfApplicationImpl(ui_factory)
        event_layer = EventExecutionLayer(app)
        
        # Load project first
        app.load_project(temp_project_with_files)
        assert app.is_project_loaded()
        
        # Emit create object event
        event = UIEvent(
            event_type=EventType.MENU_ITEM_CLICKED,
            source="main_window",
            data={
                "menu_item": "create_object",
                "object_name": "Test Object"
            }
        )
        
        # Emit the event
        event_bus.emit(event)
        
        # Verify object was created
        objects = app.get_objects()
        assert len(objects) > 0
        # Check that the object has the expected name
        object_names = [obj.name for obj in objects]
        assert "Test Object" in object_names
    
    def test_create_template_flow(self, temp_project_with_files):
        """Test template creation flow from UI event"""
        # Create UI factory and application
        ui_factory = create_ui_factory("headless", verbose=False)
        app = CurioShelfApplicationImpl(ui_factory)
        event_layer = EventExecutionLayer(app)
        
        # Load project first
        app.load_project(temp_project_with_files)
        assert app.is_project_loaded()
        
        # Emit create template event
        event = UIEvent(
            event_type=EventType.MENU_ITEM_CLICKED,
            source="main_window",
            data={
                "menu_item": "create_template",
                "template_name": "Test Template"
            }
        )
        
        # Emit the event
        event_bus.emit(event)
        
        # Verify template was created
        templates = app.get_templates()
        assert len(templates) > 0
        # Check that the template has the expected name
        template_names = [template.name for template in templates]
        assert "Test Template" in template_names
    
    def test_import_source_flow(self, temp_project_with_files, sample_image_path):
        """Test source import flow from UI event"""
        # Create UI factory and application
        ui_factory = create_ui_factory("headless", verbose=False)
        app = CurioShelfApplicationImpl(ui_factory)
        event_layer = EventExecutionLayer(app)
        
        # Load project first
        app.load_project(temp_project_with_files)
        assert app.is_project_loaded()
        
        # Emit import source event
        event = UIEvent(
            event_type=EventType.MENU_ITEM_CLICKED,
            source="main_window",
            data={
                "menu_item": "import_source",
                "file_path": str(sample_image_path)
            }
        )
        
        # Emit the event
        event_bus.emit(event)
        
        # Verify source was imported
        sources = app.get_sources()
        assert len(sources) > 0
        # Check that the source file path is correct (should be relative to project)
        source_paths = [str(source.file_path) for source in sources]
        assert any('sample.png' in path for path in source_paths)
    
    def test_error_handling_flow(self, temp_project_dir):
        """Test error handling in event execution flow"""
        # Create UI factory and application
        ui_factory = create_ui_factory("headless", verbose=False)
        app = CurioShelfApplicationImpl(ui_factory)
        event_layer = EventExecutionLayer(app)
        
        # Try to save project without loading one first
        event = UIEvent(
            event_type=EventType.MENU_ITEM_CLICKED,
            source="main_window",
            data={"menu_item": "save_project"}
        )
        
        # Emit the event
        event_bus.emit(event)
        
        # Verify no project is loaded (error case)
        assert not app.is_project_loaded()
    
    def test_hotkey_flow(self, temp_project_with_files):
        """Test hotkey event flow"""
        # Create UI factory and application
        ui_factory = create_ui_factory("headless", verbose=False)
        app = CurioShelfApplicationImpl(ui_factory)
        event_layer = EventExecutionLayer(app)
        
        # Load project first
        app.load_project(temp_project_with_files)
        assert app.is_project_loaded()
        
        # Emit hotkey event
        event = UIEvent(
            event_type=EventType.HOTKEY_PRESSED,
            source="main_window",
            data={"hotkey": "save_project"}
        )
        
        # Emit the event
        event_bus.emit(event)
        
        # Verify project was saved (check modified timestamp)
        project_manager = ProjectStructureManager()
        structure = project_manager.load_project(temp_project_with_files)
        assert structure is not None
        assert structure.metadata.modified > structure.metadata.created
    
    def test_multiple_events_flow(self, temp_project_dir):
        """Test multiple events in sequence"""
        # Create UI factory and application
        ui_factory = create_ui_factory("headless", verbose=False)
        app = CurioShelfApplicationImpl(ui_factory)
        event_layer = EventExecutionLayer(app)
        
        # Create project metadata
        metadata = ProjectMetadata(
            name="Multi Event Test Project",
            description="Testing multiple events",
            author="Test User"
        )
        
        # 1. Create project
        create_event = UIEvent(
            event_type=EventType.DIALOG_ACCEPTED,
            source="project_dialog",
            data={
                "dialog_type": "project_dialog",
                "is_new_project": True,
                "project_path": str(temp_project_dir),
                "project_info": metadata
            }
        )
        event_bus.emit(create_event)
        
        # 2. Create object
        object_event = UIEvent(
            event_type=EventType.MENU_ITEM_CLICKED,
            source="main_window",
            data={
                "menu_item": "create_object",
                "object_name": "Multi Event Object"
            }
        )
        event_bus.emit(object_event)
        
        # 3. Create template
        template_event = UIEvent(
            event_type=EventType.MENU_ITEM_CLICKED,
            source="main_window",
            data={
                "menu_item": "create_template",
                "template_name": "Multi Event Template"
            }
        )
        event_bus.emit(template_event)
        
        # 4. Save project
        save_event = UIEvent(
            event_type=EventType.MENU_ITEM_CLICKED,
            source="main_window",
            data={"menu_item": "save_project"}
        )
        event_bus.emit(save_event)
        
        # Verify all operations completed
        assert app.is_project_loaded()
        assert len(app.get_objects()) > 0
        assert len(app.get_templates()) > 0
        
        # Verify project structure
        project_manager = ProjectStructureManager()
        structure = project_manager.load_project(temp_project_dir)
        assert structure is not None
        assert structure.metadata.name == "Multi Event Test Project"


class TestProjectStructure:
    """Test the project structure definition and management"""
    
    def test_project_metadata_creation(self):
        """Test creating project metadata"""
        metadata = ProjectMetadata(
            name="Test Project",
            description="A test project",
            author="Test User"
        )
        
        assert metadata.name == "Test Project"
        assert metadata.description == "A test project"
        assert metadata.author == "Test User"
        assert metadata.version == "1.0.0"
        assert metadata.created != ""
        assert metadata.modified == metadata.created
    
    def test_project_structure_creation(self):
        """Test creating project structure"""
        metadata = ProjectMetadata(
            name="Test Project",
            description="A test project",
            author="Test User"
        )
        
        structure = ProjectStructure(metadata=metadata)
        
        assert structure.metadata == metadata
        assert structure.sources_dir == "sources"
        assert structure.templates_dir == "templates"
        assert structure.objects_dir == "objects"
        assert structure.build_dir == "build"
        assert structure.config_dir == "config"
    
    def test_project_structure_serialization(self):
        """Test serializing and deserializing project structure"""
        metadata = ProjectMetadata(
            name="Test Project",
            description="A test project",
            author="Test User"
        )
        
        structure = ProjectStructure(metadata=metadata)
        
        # Serialize to dict
        data = structure.to_dict()
        assert "metadata" in data
        assert "directories" in data
        assert data["metadata"]["name"] == "Test Project"
        
        # Deserialize from dict
        restored = ProjectStructure.from_dict(data)
        assert restored.metadata.name == structure.metadata.name
        assert restored.sources_dir == structure.sources_dir
    
    def test_project_manager_creation(self, temp_project_dir):
        """Test project creation with ProjectStructureManager"""
        project_manager = ProjectStructureManager()
        
        metadata = ProjectMetadata(
            name="Manager Test Project",
            description="Testing project manager",
            author="Test User"
        )
        
        # Create project
        success = project_manager.create_project(temp_project_dir, metadata)
        assert success
        
        # Verify project structure
        assert (temp_project_dir / "curioshelf.json").exists()
        assert (temp_project_dir / "sources").exists()
        assert (temp_project_dir / "templates").exists()
        assert (temp_project_dir / "objects").exists()
        assert (temp_project_dir / "build").exists()
        assert (temp_project_dir / "config").exists()
        assert (temp_project_dir / ".gitignore").exists()
        
        # Verify project can be loaded
        structure = project_manager.load_project(temp_project_dir)
        assert structure is not None
        assert structure.metadata.name == "Manager Test Project"
    
    def test_project_manager_loading(self, temp_project_with_files):
        """Test project loading with ProjectStructureManager"""
        project_manager = ProjectStructureManager()
        
        # Load project
        structure = project_manager.load_project(temp_project_with_files)
        assert structure is not None
        assert structure.metadata.name == "Test Project"
        
        # Verify is_project check
        assert project_manager.is_project(temp_project_with_files)
        assert not project_manager.is_project(temp_project_with_files.parent)
    
    def test_project_manager_saving(self, temp_project_with_files):
        """Test project saving with ProjectStructureManager"""
        project_manager = ProjectStructureManager()
        
        # Load project
        structure = project_manager.load_project(temp_project_with_files)
        assert structure is not None
        
        # Modify metadata
        structure.metadata.description = "Modified description"
        
        # Save project
        success = project_manager.save_project(temp_project_with_files, structure)
        assert success
        
        # Reload and verify changes
        reloaded = project_manager.load_project(temp_project_with_files)
        assert reloaded is not None
        assert reloaded.metadata.description == "Modified description"
        assert reloaded.metadata.modified > reloaded.metadata.created
