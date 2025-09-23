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
from ..projects import ProjectManager, ProjectInfo, ProjectStructureManager, ProjectMetadata
from ..ui.state_manager import UIStateManager
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
        self.project_structure_manager = ProjectStructureManager()
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
        self.current_project_path: Optional[Path] = None
        self._templates_count = 0
        
        # Setup initial state
        self._update_application_state()
    
    def initialize_controllers(self, ui_implementation) -> None:
        """Initialize all controllers with the UI implementation"""
        if self.asset_manager:
            self.sources_controller = SourcesController(self.asset_manager, ui_implementation)
            self.templates_controller = TemplatesController(self.asset_manager, ui_implementation)
            self.objects_controller = ObjectsController(self.asset_manager, ui_implementation)
            
            # Setup controller UI
            self.sources_controller.setup_ui(ui_implementation)
            self.templates_controller.setup_ui(ui_implementation)
            self.objects_controller.setup_ui(ui_implementation)
    
    # Project Management
    def create_project(self, project_path: Path, project_info) -> bool:
        """Create a new project"""
        self.logger.info(f"Creating project: {project_info.name}")
        
        # Convert ProjectMetadata to ProjectInfo if needed
        if hasattr(project_info, 'to_dict'):
            # It's a ProjectMetadata object, convert to ProjectInfo
            legacy_project_info = ProjectInfo(
                name=project_info.name,
                description=project_info.description,
                author=project_info.author,
                version=project_info.version
            )
        else:
            # Assume it's already a ProjectInfo
            legacy_project_info = project_info
        
        # Create project structure
        if hasattr(project_info, 'to_dict'):
            # Use the new project structure
            success = self.project_structure_manager.create_project(project_path, project_info)
        else:
            # Use the legacy project structure
            success = self.project_manager.create_project(project_path, project_info)
        
        if success:
            # Set up the legacy project manager for compatibility
            if hasattr(project_info, 'to_dict'):
                # We created with new structure, now set up legacy
                self.project_manager.current_project_path = project_path
                self.project_manager.project_info = legacy_project_info
                self.project_manager.asset_manager = AssetManager()
                self.project_manager.is_project_loaded = True
                self.asset_manager = self.project_manager.asset_manager
                self.current_project_path = project_path
            else:
                # We created with legacy structure
                self.asset_manager = self.project_manager.asset_manager
            
            self._update_application_state()
            self.update_ui_state()
            
            # Initialize controllers if UI factory is available
            if self.ui_factory:
                ui_impl = self.ui_factory.get_ui_implementation()
                self.initialize_controllers(ui_impl)
            
            self.emit_event("project_created", {"project_name": legacy_project_info.name})
            return True
        
        return False
    
    def load_project(self, project_path: Path) -> bool:
        """Load an existing project"""
        self.logger.info(f"Loading project from: {project_path}")
        
        # Try to load as new project structure first
        if self.project_structure_manager.is_project(project_path):
            structure = self.project_structure_manager.load_project(project_path)
            if structure:
                # Convert to legacy format for compatibility
                legacy_project_info = ProjectInfo(
                    name=structure.metadata.name,
                    description=structure.metadata.description,
                    author=structure.metadata.author,
                    version=structure.metadata.version
                )
                
                # Set up legacy project manager
                self.project_manager.current_project_path = project_path
                self.project_manager.project_info = legacy_project_info
                self.project_manager.asset_manager = AssetManager()
                self.project_manager.is_project_loaded = True
                self.asset_manager = self.project_manager.asset_manager
                
                # Set application's current project path
                self.current_project_path = project_path
                
                # Load existing assets from the project
                self._load_project_assets(project_path)
                
                self._update_application_state()
                self.update_ui_state()
                
                # Initialize controllers if UI factory is available
                if self.ui_factory:
                    ui_impl = self.ui_factory.get_ui_implementation()
                    self.initialize_controllers(ui_impl)
                
                self.emit_event("project_loaded", {"project_path": str(project_path)})
                return True
        
        # Try to load as legacy project structure
        success = self.project_manager.load_project(project_path)
        if success:
            self.asset_manager = self.project_manager.asset_manager
            self._update_application_state()
            
            # Initialize controllers if UI factory is available
            if self.ui_factory:
                ui_impl = self.ui_factory.get_ui_implementation()
                self.initialize_controllers(ui_impl)
            
            self.emit_event("project_loaded", {"project_path": str(project_path)})
            return True
        
        self.logger.error(f"Failed to load project from: {project_path}")
        return False
    
    def _load_project_assets(self, project_path: Path) -> None:
        """Load existing assets from a project directory"""
        if not self.asset_manager:
            return
        
        # Load sources from the sources directory
        sources_dir = project_path / "sources"
        if sources_dir.exists():
            for source_file in sources_dir.iterdir():
                if source_file.is_file() and source_file.suffix.lower() in ['.png', '.jpg', '.jpeg', '.gif', '.bmp']:
                    try:
                        # Add source to asset manager
                        source = self.asset_manager.add_source(source_file, 800, 600)  # Mock dimensions
                        self.logger.info(f"Loaded source: {source_file.name}")
                    except Exception as e:
                        self.logger.warning(f"Failed to load source {source_file.name}: {e}")
        
        # Load objects from the objects directory
        objects_dir = project_path / "objects"
        if objects_dir.exists():
            for object_file in objects_dir.iterdir():
                if object_file.is_file() and object_file.suffix == '.json':
                    try:
                        # For now, just create a basic object
                        object_name = object_file.stem
                        obj = self.asset_manager.add_object(object_name)
                        self.logger.info(f"Loaded object: {object_name}")
                    except Exception as e:
                        self.logger.warning(f"Failed to load object {object_file.name}: {e}")
        
        # Load templates from the templates directory
        templates_dir = project_path / "templates"
        if templates_dir.exists():
            for template_file in templates_dir.iterdir():
                if template_file.is_file() and template_file.suffix == '.json':
                    try:
                        # For now, just create a basic template
                        template_name = template_file.stem
                        template = self.asset_manager.add_template(
                            name=template_name,
                            description=f"Template: {template_name}",
                            required_views=["front", "back"]
                        )
                        self.logger.info(f"Loaded template: {template_name}")
                    except Exception as e:
                        self.logger.warning(f"Failed to load template {template_file.name}: {e}")
    
    def _save_project_assets(self, project_path: Path) -> None:
        """Save current assets to project directory"""
        if not self.asset_manager:
            return
        
        # Ensure project directory exists
        project_path.mkdir(parents=True, exist_ok=True)
        
        # Save sources
        sources_dir = project_path / "sources"
        sources_dir.mkdir(exist_ok=True)
        
        for source in self.asset_manager.get_sources():
            # Copy source file to project directory if it's not already there
            source_path = Path(source.file_path)
            if not source_path.is_absolute() or str(source_path).startswith(str(project_path)):
                continue  # Already in project directory
            
            dest_path = sources_dir / source_path.name
            if not dest_path.exists():
                try:
                    import shutil
                    shutil.copy2(source_path, dest_path)
                    self.logger.info(f"Saved source: {dest_path.name}")
                except Exception as e:
                    self.logger.warning(f"Failed to save source {source_path.name}: {e}")
        
        # Save objects
        objects_dir = project_path / "objects"
        objects_dir.mkdir(exist_ok=True)
        
        for obj in self.asset_manager.get_objects():
            object_file = objects_dir / f"{obj.name}.json"
            try:
                import json
                with open(object_file, 'w') as f:
                    json.dump({
                        "name": obj.name,
                        "slices": [{"name": slice.name, "source_id": slice.source_id} for slice in obj.slices]
                    }, f, indent=2)
                self.logger.info(f"Saved object: {obj.name}")
            except Exception as e:
                self.logger.warning(f"Failed to save object {obj.name}: {e}")
        
        # Save templates
        templates_dir = project_path / "templates"
        templates_dir.mkdir(exist_ok=True)
        
        for template in self.asset_manager.get_templates():
            template_file = templates_dir / f"{template.name}.json"
            try:
                import json
                with open(template_file, 'w') as f:
                    json.dump({
                        "name": template.name,
                        "description": template.description,
                        "required_views": template.required_views
                    }, f, indent=2)
                self.logger.info(f"Saved template: {template.name}")
            except Exception as e:
                self.logger.warning(f"Failed to save template {template.name}: {e}")
    
    def save_project(self) -> bool:
        """Save the current project"""
        if not self.is_project_loaded():
            self.logger.warning("Cannot save project: no project loaded")
            return False
        
        self.logger.info("Saving project")
        
        # Save assets to project directory
        if self.project_manager.current_project_path and self.asset_manager:
            self._save_project_assets(self.project_manager.current_project_path)
        
        # Save legacy project structure
        legacy_success = self.project_manager.save_project()
        
        # Also save new project structure if it exists
        if self.project_manager.current_project_path:
            # Check if this is a new project structure
            if self.project_structure_manager.is_project(self.project_manager.current_project_path):
                # Load the current structure and save it (this will update the modified timestamp)
                structure = self.project_structure_manager.load_project(self.project_manager.current_project_path)
                if structure:
                    new_success = self.project_structure_manager.save_project(self.project_manager.current_project_path, structure)
                    if not new_success:
                        self.logger.warning("Failed to save new project structure")
        
        if legacy_success:
            self.emit_event("project_saved", {})
        
        return legacy_success
    
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
            self.current_project_path = None
            self._update_application_state()
            self.update_ui_state()  # Add this line to update UI state
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
            # Add source to asset manager
            if self.asset_manager:
                source = self.asset_manager.add_source(project_path, 800, 600)  # Mock dimensions
                self._update_application_state()
                self.emit_event("source_imported", {"source_id": source.id})
                return True
        
        return False
    
    def add_source(self, file_path: Path) -> bool:
        """Add a source image file to the current project (alias for import_source)"""
        return self.import_source(file_path)
    
    def add_object(self, object_name: str, source_id: str = None) -> bool:
        """Add a new object to the current project (alias for create_object)"""
        return self.create_object(object_name, source_id)
    
    def create_object(self, object_name: str, source_id: str = None) -> bool:
        """Create a new object"""
        if not self.is_project_loaded():
            self.logger.warning("Cannot create object: no project loaded")
            return False
        
        self.logger.info(f"Creating object: {object_name}")
        
        if self.asset_manager:
            # Create object
            obj = self.asset_manager.add_object(object_name)
            self._update_application_state()
            self.emit_event("object_created", {"object_id": obj.id})
            return True
        
        return False
    
    def add_template(self, template_name: str, object_id: str = None) -> bool:
        """Add a new template to the current project (alias for create_template)"""
        return self.create_template(template_name, object_id)
    
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
    
    # Detailed State Methods for UI Ghosting
    def valid_project(self) -> bool:
        """True if we have a valid, editable project loaded"""
        return (self.is_project_loaded() and 
                self.project_manager is not None and 
                self.asset_manager is not None)
    
    def can_create_project(self) -> bool:
        """True if we can create a new project (no project loaded or current project is closed)"""
        return not self.is_project_loaded()
    
    def can_open_project(self) -> bool:
        """True if we can open a project (no project loaded or current project is closed)"""
        return not self.is_project_loaded()
    
    def can_save_project(self) -> bool:
        """True if we can save the current project (valid project loaded with changes)"""
        # For now, always allow saving if we have a valid project
        # TODO: Add dirty state tracking to only enable when there are changes
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
        
        # Emit UI state changed event
        self.emit_event("ui_state_changed", {
            "project_loaded": self.is_project_loaded(),
            "has_sources": self.has_sources(),
            "has_objects": self.has_objects(),
            "has_templates": self.has_templates(),
        })
    
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
