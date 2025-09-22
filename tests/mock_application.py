"""
Mock Application Implementation for Testing

This module provides a mock implementation of the application interface
for testing UI interactions without triggering actual business logic.
"""

from typing import Any, Dict, List, Optional, Callable
from pathlib import Path
import logging

from curioshelf.application_interface import ApplicationInterface
from curioshelf.models import AssetSource, Template, CurioObject
from curioshelf.projects import ProjectInfo
from curioshelf.event_system import event_bus, UIEvent, EventType
from curioshelf.status_bar_handler import (
    emit_project_status, emit_asset_status, emit_info_message, 
    emit_error_message, emit_progress_update
)


class MockCurioShelfApplication(ApplicationInterface):
    """Mock application object for testing UI interactions"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        
        # Mock state
        self._project_loaded = False
        self._project_info: Optional[ProjectInfo] = None
        self._sources: List[AssetSource] = []
        self._objects: List[CurioObject] = []
        self._templates: List[Template] = []
        
        # Event handlers
        self.event_handlers: Dict[str, Callable] = {}
        
        # Operation tracking
        self.operations_performed: List[Dict[str, Any]] = []
        
        # Setup initial state
        self._update_application_state()
    
    # Project Management
    def create_project(self, project_path: Path, project_info) -> bool:
        """Mock project creation"""
        # Handle both ProjectInfo objects and dictionaries
        if isinstance(project_info, dict):
            project_name = project_info.get('name', 'Unknown Project')
        else:
            project_name = project_info.name
        
        self.logger.info(f"MOCK: Creating project: {project_name}")
        
        self._project_loaded = True
        self._project_info = project_info
        self._sources = []
        self._objects = []
        self._templates = []
        
        self.operations_performed.append({
            "operation": "create_project",
            "project_name": project_name,
            "project_path": str(project_path)
        })
        
        # Emit mock events
        emit_info_message(f"Mock: Project '{project_name}' created successfully", "mock_application")
        emit_project_status(project_name, "mock_application")
        
        return True
    
    def load_project(self, project_path: Path) -> bool:
        """Mock project loading"""
        self.logger.info(f"MOCK: Loading project from: {project_path}")
        
        self._project_loaded = True
        self._project_info = ProjectInfo(
            name="Mock Project",
            author="Mock Author",
            description="A mock project for testing"
        )
        
        # Add some mock data
        self._sources = [
            AssetSource(id="source1", file_path=Path("mock1.png"), file_type="png", width=800, height=600, slices=[]),
            AssetSource(id="source2", file_path=Path("mock2.jpg"), file_type="jpg", width=800, height=600, slices=[])
        ]
        self._objects = [
            CurioObject(id="object1", name="Mock Object 1", template_name=None, sources={}, slices=[]),
            CurioObject(id="object2", name="Mock Object 2", template_name=None, sources={}, slices=[])
        ]
        self._templates = [
            Template(name="Mock Template 1", description="Mock template 1", required_views=["front", "back"]),
            Template(name="Mock Template 2", description="Mock template 2", required_views=["front", "back"])
        ]
        
        self.operations_performed.append({
            "operation": "load_project",
            "project_path": str(project_path)
        })
        
        # Emit mock events
        emit_info_message(f"Mock: Project loaded from {project_path}", "mock_application")
        emit_project_status(self._project_info.name, "mock_application")
        
        return True
    
    def save_project(self) -> bool:
        """Mock project saving"""
        if not self._project_loaded:
            self.logger.warning("MOCK: Cannot save project: no project loaded")
            return False
        
        self.logger.info("MOCK: Saving project")
        
        self.operations_performed.append({
            "operation": "save_project"
        })
        
        # Emit mock events
        emit_info_message("Mock: Project saved successfully", "mock_application")
        
        return True
    
    def close_project(self) -> bool:
        """Mock project closing"""
        if not self._project_loaded:
            self.logger.warning("MOCK: Cannot close project: no project loaded")
            return True
        
        self.logger.info("MOCK: Closing project")
        
        self._project_loaded = False
        self._project_info = None
        self._sources = []
        self._objects = []
        self._templates = []
        
        self.operations_performed.append({
            "operation": "close_project"
        })
        
        # Emit mock events
        emit_info_message("Mock: Project closed", "mock_application")
        emit_project_status(None, "mock_application")
        
        return True
    
    def import_source(self, file_path: Path) -> bool:
        """Mock source import"""
        if not self._project_loaded:
            self.logger.warning("MOCK: Cannot import source: no project loaded")
            return False
        
        self.logger.info(f"MOCK: Importing source: {file_path}")
        
        # Add to mock sources
        self._sources.append(str(file_path))
        
        self.operations_performed.append({
            "operation": "import_source",
            "file_path": str(file_path)
        })
        
        return True
    
    def add_source(self, file_path: Path) -> bool:
        """Mock source add (alias for import_source)"""
        return self.import_source(file_path)
    
    def create_object(self, object_name: str, source_id: str = None) -> bool:
        """Mock object creation"""
        if not self._project_loaded:
            self.logger.warning("MOCK: Cannot create object: no project loaded")
            return False
        
        self.logger.info(f"MOCK: Creating object: {object_name}")
        
        # Add to mock objects
        self._objects.append(object_name)
        
        self.operations_performed.append({
            "operation": "create_object",
            "object_name": object_name
        })
        
        return True
    
    def create_template(self, template_name: str, object_id: str = None) -> bool:
        """Mock template creation"""
        if not self._project_loaded:
            self.logger.warning("MOCK: Cannot create template: no project loaded")
            return False
        
        self.logger.info(f"MOCK: Creating template: {template_name}")
        
        # Add to mock templates
        self._templates.append(template_name)
        
        self.operations_performed.append({
            "operation": "create_template",
            "template_name": template_name
        })
        
        return True
    
    def add_source(self, source_name: str) -> None:
        """Mock adding a source (for testing)"""
        self._sources.append(source_name)
    
    def add_object(self, object_name: str) -> None:
        """Mock adding an object (for testing)"""
        self._objects.append(object_name)
    
    def add_template(self, template_name: str) -> None:
        """Mock adding a template (for testing)"""
        self._templates.append(template_name)
    
    def get_project_status(self) -> Dict[str, Any]:
        """Get mock project status"""
        project_name = None
        if self._project_info:
            if isinstance(self._project_info, dict):
                project_name = self._project_info.get('name')
            else:
                project_name = self._project_info.name
        
        return {
            "loaded": self._project_loaded,
            "name": project_name,
            "path": None
        }
    
    # Asset Management
    def import_source(self, file_path: Path) -> bool:
        """Mock source import"""
        if not self._project_loaded:
            self.logger.warning("MOCK: Cannot import source: no project loaded")
            return False
        
        self.logger.info(f"MOCK: Importing source: {file_path}")
        
        source = AssetSource(
            id=file_path.stem,
            file_path=file_path,
            file_type=file_path.suffix[1:],  # Remove the dot
            width=800,  # Mock width
            height=600,  # Mock height
            slices=[]
        )
        self._sources.append(source)
        
        self.operations_performed.append({
            "operation": "import_source",
            "file_path": str(file_path)
        })
        
        # Emit mock events
        emit_info_message(f"Mock: Source '{source.id}' imported", "mock_application")
        
        return True
    
    def add_object(self, object_name: str, source_id: str = None) -> bool:
        """Mock object add (alias for create_object)"""
        return self.create_object(object_name, source_id)
    
    def create_object(self, object_name: str, source_id: str = None) -> bool:
        """Mock object creation"""
        if not self._project_loaded:
            self.logger.warning("MOCK: Cannot create object: no project loaded")
            return False
        
        self.logger.info(f"MOCK: Creating object: {object_name}")
        
        obj = CurioObject(
            id=object_name.lower().replace(' ', '_'),
            name=object_name,
            template_name=None,
            sources={},
            slices=[]
        )
        self._objects.append(obj)
        
        self.operations_performed.append({
            "operation": "create_object",
            "object_name": object_name,
            "source_id": source_id
        })
        
        # Emit mock events
        emit_info_message(f"Mock: Object '{object_name}' created", "mock_application")
        
        return True
    
    def add_template(self, template_name: str, object_id: str = None) -> bool:
        """Mock template add (alias for create_template)"""
        return self.create_template(template_name, object_id)
    
    def create_template(self, template_name: str, object_id: str = None) -> bool:
        """Mock template creation"""
        if not self._project_loaded:
            self.logger.warning("MOCK: Cannot create template: no project loaded")
            return False
        
        self.logger.info(f"MOCK: Creating template: {template_name}")
        
        template = Template(
            name=template_name,
            description=f"Mock template: {template_name}",
            required_views=["front", "back"]
        )
        self._templates.append(template)
        
        self.operations_performed.append({
            "operation": "create_template",
            "template_name": template_name,
            "object_id": object_id
        })
        
        # Emit mock events
        emit_info_message(f"Mock: Template '{template_name}' created", "mock_application")
        
        return True
    
    def export_assets(self, output_path: Path) -> bool:
        """Mock asset export"""
        if not self._project_loaded:
            self.logger.warning("MOCK: Cannot export assets: no project loaded")
            return False
        
        if not self._sources:
            self.logger.warning("MOCK: Cannot export assets: no sources available")
            return False
        
        self.logger.info(f"MOCK: Exporting assets to: {output_path}")
        
        self.operations_performed.append({
            "operation": "export_assets",
            "output_path": str(output_path)
        })
        
        # Emit mock events
        emit_info_message(f"Mock: Assets exported to {output_path}", "mock_application")
        
        return True
    
    # State Queries
    def is_project_loaded(self) -> bool:
        """Check if a project is currently loaded"""
        return self._project_loaded
    
    def has_sources(self) -> bool:
        """Check if project has any sources"""
        return len(self._sources) > 0
    
    def has_objects(self) -> bool:
        """Check if project has any objects"""
        return len(self._objects) > 0
    
    def has_templates(self) -> bool:
        """Check if project has any templates"""
        return len(self._templates) > 0
    
    def get_asset_counts(self) -> Dict[str, int]:
        """Get counts of different asset types"""
        return {
            "sources": len(self._sources),
            "objects": len(self._objects),
            "templates": len(self._templates),
            "slices": 0  # Mock doesn't track slices
        }
    
    # Detailed State Methods for UI Ghosting
    def valid_project(self) -> bool:
        """True if we have a valid, editable project loaded"""
        return self.is_project_loaded()
    
    def can_create_project(self) -> bool:
        """True if we can create a new project (no project loaded or current project is closed)"""
        return not self.is_project_loaded()
    
    def can_open_project(self) -> bool:
        """True if we can open a project (no project loaded or current project is closed)"""
        return not self.is_project_loaded()
    
    def can_save_project(self) -> bool:
        """True if we can save the current project (valid project loaded with changes)"""
        return self.valid_project()
    
    def can_close_project(self) -> bool:
        """True if we can close the current project (valid project loaded)"""
        return self.valid_project()
    
    def can_import_source(self) -> bool:
        """True if we can import a source (valid project loaded)"""
        return self.valid_project()
    
    def can_create_object(self) -> bool:
        """True if we can create an object (valid project loaded and has sources)"""
        return self.valid_project() and self.has_sources()
    
    def can_create_template(self) -> bool:
        """True if we can create a template (valid project loaded and has objects)"""
        return self.valid_project() and self.has_objects()
    
    def can_export_assets(self) -> bool:
        """True if we can export assets (valid project loaded and has assets)"""
        return self.valid_project() and (self.has_sources() or self.has_objects() or self.has_templates())
    
    def can_edit_sources(self) -> bool:
        """True if we can edit sources (valid project loaded and has sources)"""
        return self.valid_project() and self.has_sources()
    
    def can_edit_objects(self) -> bool:
        """True if we can edit objects (valid project loaded and has objects)"""
        return self.valid_project() and self.has_objects()
    
    def can_edit_templates(self) -> bool:
        """True if we can edit templates (valid project loaded and has templates)"""
        return self.valid_project() and self.has_templates()
    
    # UI State Management
    def get_ui_state(self) -> Dict[str, bool]:
        """Get current UI state (what should be enabled/disabled)"""
        return {
            # Project operations
            "new_project": self.can_create_project(),
            "open_project": self.can_open_project(),
            "save_project": self.can_save_project(),
            "close_project": self.can_close_project(),
            
            # Asset operations
            "import_source": self.can_import_source(),
            "create_object": self.can_create_object(),
            "create_template": self.can_create_template(),
            "export_assets": self.can_export_assets(),
            
            # Edit operations
            "edit_sources": self.can_edit_sources(),
            "edit_objects": self.can_edit_objects(),
            "edit_templates": self.can_edit_templates(),
            
            # Tab visibility (for main window tabs)
            "sources_tab_enabled": self.can_import_source(),
            "objects_tab_enabled": self.can_create_object(),
            "templates_tab_enabled": self.can_create_template(),
            
            # Legacy compatibility
            "has_project": self.valid_project(),
            "has_sources": self.has_sources(),
            "has_objects": self.has_objects(),
            "has_templates": self.has_templates(),
        }
    
    def update_ui_state(self) -> None:
        """Update UI state based on current application state"""
        # Emit status events
        if self.is_project_loaded():
            project_info = self.get_project_info()
            if project_info:
                emit_project_status(project_info.name, "mock_application")
            else:
                emit_project_status("Mock Project", "mock_application")
        else:
            emit_project_status(None, "mock_application")
        
        # Emit asset status
        counts = self.get_asset_counts()
        emit_asset_status(
            counts["sources"], 
            counts["templates"], 
            counts["objects"], 
            counts["slices"], 
            "mock_application"
        )
    
    # Event Handling
    def set_event_handlers(self, handlers: Dict[str, Callable]) -> None:
        """Set event handlers for UI events"""
        self.event_handlers.update(handlers)
    
    def emit_event(self, event_type: str, data: Dict[str, Any]) -> None:
        """Emit an event to the event system"""
        event = UIEvent(
            event_type=EventType(event_type) if hasattr(EventType, event_type.upper()) else EventType.UI_STATE_CHANGED,
            source="mock_application",
            data=data
        )
        event_bus.emit(event)
    
    # Data Access
    def get_sources(self) -> List[AssetSource]:
        """Get all sources"""
        return self._sources.copy()
    
    def get_objects(self) -> List[CurioObject]:
        """Get all objects"""
        return self._objects.copy()
    
    def get_templates(self) -> List[Template]:
        """Get all templates"""
        return self._templates.copy()
    
    def get_project_info(self) -> Optional[ProjectInfo]:
        """Get current project information"""
        return self._project_info
    
    # Testing Utilities
    def get_operations_performed(self) -> List[Dict[str, Any]]:
        """Get list of operations performed (for testing)"""
        return self.operations_performed.copy()
    
    def clear_operations(self) -> None:
        """Clear operations list (for testing)"""
        self.operations_performed.clear()
    
    def reset_state(self) -> None:
        """Reset to initial state (for testing)"""
        self._project_loaded = False
        self._project_info = None
        self._sources = []
        self._objects = []
        self._templates = []
        self.operations_performed.clear()
        self._update_application_state()
    
    def _update_application_state(self) -> None:
        """Update internal application state"""
        # This method is called for consistency with the real application
        # In the mock, we don't need to do anything special
        pass
