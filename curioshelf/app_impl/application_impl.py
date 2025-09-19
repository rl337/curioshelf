"""
Application Implementation

This module provides the main application implementation that aggregates
all controllers and implements the ApplicationInterface.
"""

from typing import Any, Dict, List, Optional, Callable
from pathlib import Path
import logging

from ..application_interface import ApplicationInterface
from ..models import AssetManager, AssetSource, Template, CurioObject
from ..project_manager import ProjectManager, ProjectInfo
from ..ui_state_manager import UIStateManager
from ..event_system import event_bus, UIEvent, EventType
from ..status_bar_handler import (
    emit_project_status, emit_asset_status, emit_info_message, 
    emit_error_message, emit_progress_update
)
from .controllers import SourcesController, TemplatesController, ObjectsController


class CurioShelfApplicationImpl(ApplicationInterface):
    """Main application implementation that aggregates all controllers"""
    
    def __init__(self, ui_factory=None):
        self.logger = logging.getLogger(__name__)
        
        # Initialize managers
        self.project_manager = ProjectManager()
        self.asset_manager: Optional[AssetManager] = None
        self.ui_state_manager = UIStateManager()
        
        # UI factory for creating controllers
        self.ui_factory = ui_factory
        
        # Controllers
        self.sources_controller: Optional[SourcesController] = None
        self.templates_controller: Optional[TemplatesController] = None
        self.objects_controller: Optional[ObjectsController] = None
        
        # Event handlers
        self.event_handlers: Dict[str, Callable] = {}
        
        # State tracking
        self._project_loaded = False
        self._sources_count = 0
        self._objects_count = 0
        self._templates_count = 0
        
        # Setup initial state
        self._update_application_state()
    
    def initialize_controllers(self, ui_factory) -> None:
        """Initialize all controllers with the UI factory"""
        self.ui_factory = ui_factory
        
        if self.asset_manager:
            self.sources_controller = SourcesController(self.asset_manager, ui_factory)
            self.templates_controller = TemplatesController(self.asset_manager, ui_factory)
            self.objects_controller = ObjectsController(self.asset_manager, ui_factory)
            
            # Setup controller UI
            self.sources_controller.setup_ui(ui_factory)
            self.templates_controller.setup_ui(ui_factory)
            self.objects_controller.setup_ui(ui_factory)
    
    # Project Management
    def create_project(self, project_path: Path, project_info: ProjectInfo) -> bool:
        """Create a new project"""
        self.logger.info(f"Creating project: {project_info.name}")
        
        success = self.project_manager.create_project(project_path, project_info)
        if success:
            self.asset_manager = self.project_manager.asset_manager
            self._update_application_state()
            
            # Initialize controllers if UI factory is available
            if self.ui_factory:
                self.initialize_controllers(self.ui_factory)
            
            self.emit_event("project_created", {"project_name": project_info.name})
        
        return success
    
    def load_project(self, project_path: Path) -> bool:
        """Load an existing project"""
        self.logger.info(f"Loading project from: {project_path}")
        
        success = self.project_manager.load_project(project_path)
        if success:
            self.asset_manager = self.project_manager.asset_manager
            self._update_application_state()
            
            # Initialize controllers if UI factory is available
            if self.ui_factory:
                self.initialize_controllers(self.ui_factory)
            
            self.emit_event("project_loaded", {"project_path": str(project_path)})
        
        return success
    
    def save_project(self) -> bool:
        """Save the current project"""
        if not self.is_project_loaded():
            self.logger.warning("Cannot save project: no project loaded")
            return False
        
        self.logger.info("Saving project")
        success = self.project_manager.save_project()
        
        if success:
            self.emit_event("project_saved", {})
        
        return success
    
    def close_project(self) -> bool:
        """Close the current project"""
        if not self.is_project_loaded():
            self.logger.warning("Cannot close project: no project loaded")
            return True  # Already closed
        
        self.logger.info("Closing project")
        success = self.project_manager.close_project()
        
        if success:
            self.asset_manager = None
            self.sources_controller = None
            self.templates_controller = None
            self.objects_controller = None
            self._update_application_state()
            self.emit_event("project_closed", {})
        
        return success
    
    def get_project_status(self) -> Dict[str, Any]:
        """Get current project status"""
        return self.project_manager.get_project_status()
    
    # Asset Management
    def import_source(self, file_path: Path) -> bool:
        """Import a source image"""
        if not self.is_project_loaded():
            self.logger.warning("Cannot import source: no project loaded")
            return False
        
        self.logger.info(f"Importing source: {file_path}")
        
        # Add source to project
        project_path = self.project_manager.add_source_file(file_path)
        if project_path:
            # Create AssetSource object
            source = AssetSource(
                id=file_path.stem,
                file_path=project_path,
                file_type=file_path.suffix[1:],  # Remove the dot
                width=800,  # Mock width
                height=600,  # Mock height
                slices=[]
            )
            
            if self.asset_manager:
                self.asset_manager.add_source(source)
                self._update_application_state()
                self.emit_event("source_imported", {"source_id": source.id})
                return True
        
        return False
    
    def create_object(self, object_name: str, source_id: str = None) -> bool:
        """Create a new object"""
        if not self.is_project_loaded():
            self.logger.warning("Cannot create object: no project loaded")
            return False
        
        self.logger.info(f"Creating object: {object_name}")
        
        if self.asset_manager:
            # Create object
            obj = CurioObject(
                id=object_name.lower().replace(' ', '_'),
                name=object_name,
                template_name=None,
                sources={},
                slices=[]
            )
            
            self.asset_manager.add_object(obj)
            self._update_application_state()
            self.emit_event("object_created", {"object_id": obj.id})
            return True
        
        return False
    
    def create_template(self, template_name: str, object_id: str = None) -> bool:
        """Create a new template"""
        if not self.is_project_loaded():
            self.logger.warning("Cannot create template: no project loaded")
            return False
        
        self.logger.info(f"Creating template: {template_name}")
        
        if self.asset_manager:
            # Create template
            self.asset_manager.add_template(
                name=template_name,
                description=f"Template: {template_name}",
                required_views=["front", "back"]
            )
            self._update_application_state()
            self.emit_event("template_created", {"template_name": template_name})
            return True
        
        return False
    
    def export_assets(self, output_path: Path) -> bool:
        """Export assets to output path"""
        if not self.is_project_loaded():
            self.logger.warning("Cannot export assets: no project loaded")
            return False
        
        if not self.has_sources():
            self.logger.warning("Cannot export assets: no sources available")
            return False
        
        self.logger.info(f"Exporting assets to: {output_path}")
        
        # TODO: Implement actual export logic
        self.emit_event("assets_exported", {"output_path": str(output_path)})
        return True
    
    # State Queries
    def is_project_loaded(self) -> bool:
        """Check if a project is currently loaded"""
        return self.project_manager.get_project_status()["loaded"]
    
    def has_sources(self) -> bool:
        """Check if project has any sources"""
        return self.asset_manager is not None and len(self.asset_manager.sources) > 0
    
    def has_objects(self) -> bool:
        """Check if project has any objects"""
        return self.asset_manager is not None and len(self.asset_manager.objects) > 0
    
    def has_templates(self) -> bool:
        """Check if project has any templates"""
        return self.asset_manager is not None and len(self.asset_manager.templates) > 0
    
    def get_asset_counts(self) -> Dict[str, int]:
        """Get counts of different asset types"""
        if not self.asset_manager:
            return {"sources": 0, "objects": 0, "templates": 0, "slices": 0}
        
        sources_count = len(self.asset_manager.sources)
        objects_count = len(self.asset_manager.objects)
        templates_count = len(self.asset_manager.templates)
        slices_count = sum(len(source.slices) for source in self.asset_manager.sources.values())
        
        return {
            "sources": sources_count,
            "objects": objects_count,
            "templates": templates_count,
            "slices": slices_count
        }
    
    # UI State Management
    def get_ui_state(self) -> Dict[str, bool]:
        """Get current UI state (what should be enabled/disabled)"""
        return {
            "new_project": True,  # Always enabled
            "open_project": True,  # Always enabled
            "save_project": self.is_project_loaded(),
            "close_project": self.is_project_loaded(),
            "import_source": self.is_project_loaded(),
            "create_object": self.is_project_loaded(),
            "create_template": self.is_project_loaded(),
            "export_assets": self.is_project_loaded() and self.has_sources(),
        }
    
    def update_ui_state(self) -> None:
        """Update UI state based on current application state"""
        self._update_application_state()
        
        # Update UI state manager
        self.ui_state_manager.update_all_states(
            self.is_project_loaded(),
            self.has_sources(),
            self.has_objects(),
            self.has_templates()
        )
        
        # Emit status events
        if self.is_project_loaded():
            project_info = self.get_project_info()
            if project_info:
                emit_project_status(project_info.name, "application")
            else:
                emit_project_status("Unknown Project", "application")
        else:
            emit_project_status(None, "application")
        
        # Emit asset status
        counts = self.get_asset_counts()
        emit_asset_status(
            counts["sources"], 
            counts["templates"], 
            counts["objects"], 
            counts["slices"], 
            "application"
        )
    
    # Event Handling
    def set_event_handlers(self, handlers: Dict[str, Callable]) -> None:
        """Set event handlers for UI events"""
        self.event_handlers.update(handlers)
    
    def emit_event(self, event_type: str, data: Dict[str, Any]) -> None:
        """Emit an event to the event system"""
        event = UIEvent(
            event_type=EventType(event_type) if hasattr(EventType, event_type.upper()) else EventType.UI_STATE_CHANGED,
            source="application",
            data=data
        )
        event_bus.emit(event)
    
    # Data Access
    def get_sources(self) -> List[AssetSource]:
        """Get all sources"""
        if not self.asset_manager:
            return []
        return list(self.asset_manager.sources.values())
    
    def get_objects(self) -> List[CurioObject]:
        """Get all objects"""
        if not self.asset_manager:
            return []
        return list(self.asset_manager.objects.values())
    
    def get_templates(self) -> List[Template]:
        """Get all templates"""
        if not self.asset_manager:
            return []
        return list(self.asset_manager.templates.values())
    
    def get_project_info(self) -> Optional[ProjectInfo]:
        """Get current project information"""
        return self.project_manager.project_info
    
    # Controller Access
    def get_sources_controller(self) -> Optional[SourcesController]:
        """Get the sources controller"""
        return self.sources_controller
    
    def get_templates_controller(self) -> Optional[TemplatesController]:
        """Get the templates controller"""
        return self.templates_controller
    
    def get_objects_controller(self) -> Optional[ObjectsController]:
        """Get the objects controller"""
        return self.objects_controller
    
    # Private Methods
    def _update_application_state(self) -> None:
        """Update internal application state"""
        self._project_loaded = self.is_project_loaded()
        
        if self.asset_manager:
            self._sources_count = len(self.asset_manager.sources)
            self._objects_count = len(self.asset_manager.objects)
            self._templates_count = len(self.asset_manager.templates)
        else:
            self._sources_count = 0
            self._objects_count = 0
            self._templates_count = 0
