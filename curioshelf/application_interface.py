"""
Application Interface for CurioShelf

This module defines the interface for the main application object that aggregates
all controllers and provides a clean interface for UI interactions.
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional, Callable
from pathlib import Path

from .models import AssetManager, AssetSource, Template, CurioObject
from .projects import ProjectManager, ProjectInfo
from .ui.state_manager import UIStateManager
from .ui.script.reflection import script_discoverable, script_hidden


class ApplicationInterface(ABC):
    """Abstract interface for the main application object"""
    
    # Project Management
    @abstractmethod
    @script_discoverable("project", "Create a new project with the specified path and info")
    def create_project(self, project_path: Path, project_info: ProjectInfo) -> bool:
        """Create a new project with the specified path and project information.
        
        Args:
            project_path (Path): The file system path where the project should be created
            project_info (ProjectInfo): Dictionary containing project metadata including:
                - name (str): The display name of the project
                - author (str): The author/creator of the project
                - description (str): Optional description of the project
        
        Returns:
            bool: True if the project was created successfully, False otherwise
            
        Example:
            project_info = {"name": "My Project", "author": "John Doe", "description": "A test project"}
            success = create_project("/path/to/project", project_info)
        """
        pass
    
    @abstractmethod
    @script_discoverable("project", "Load an existing project from the specified path")
    def load_project(self, project_path: Path) -> bool:
        """Load an existing project from the specified path.
        
        Args:
            project_path (Path): The file system path to the project directory containing curioshelf.json
        
        Returns:
            bool: True if the project was loaded successfully, False otherwise
            
        Example:
            success = load_project("/path/to/existing/project")
        """
        pass
    
    @abstractmethod
    @script_discoverable("project", "Save the currently loaded project")
    def save_project(self) -> bool:
        """Save the currently loaded project to disk.
        
        Returns:
            bool: True if the project was saved successfully, False otherwise
            
        Note:
            Requires a valid project to be loaded. Use is_project_loaded() to check.
            
        Example:
            if is_project_loaded():
                success = save_project()
        """
        pass
    
    @abstractmethod
    @script_discoverable("project", "Close the currently loaded project")
    def close_project(self) -> bool:
        """Close the currently loaded project and clear the workspace.
        
        Returns:
            bool: True if the project was closed successfully, False otherwise
            
        Note:
            This clears all project data from memory. Use save_project() first if needed.
            
        Example:
            success = close_project()
        """
        pass
    
    @abstractmethod
    @script_discoverable("project", "Get detailed status information about the current project")
    def get_project_status(self) -> Dict[str, Any]:
        """Get detailed status information about the current project.
        
        Returns:
            Dict[str, Any]: Dictionary containing project status information:
                - loaded (bool): Whether a project is currently loaded
                - name (str): The name of the loaded project, or None if none loaded
                - path (str): The file system path to the project, or None if none loaded
                - sources_count (int): Number of source assets in the project
                - objects_count (int): Number of objects in the project
                - templates_count (int): Number of templates in the project
                
        Example:
            status = get_project_status()
            print(f"Project: {status['name']}, Sources: {status['sources_count']}")
        """
        pass
    
    # Asset Management
    @abstractmethod
    @script_discoverable("assets", "Import a source image file into the current project")
    def import_source(self, file_path: Path) -> bool:
        """Import a source image file into the current project.
        
        Args:
            file_path (Path): The file system path to the image file to import
        
        Returns:
            bool: True if the source was imported successfully, False otherwise
            
        Note:
            Requires a valid project to be loaded. Supported formats: JPG, PNG, TIFF, etc.
            
        Example:
            success = import_source("/path/to/image.jpg")
        """
        pass
    
    @abstractmethod
    @script_discoverable("assets", "Create a new object, optionally from a source")
    def create_object(self, object_name: str, source_id: str = None) -> bool:
        """Create a new object with the specified name, optionally from a source.
        
        Args:
            object_name (str): The name for the new object
            source_id (str, optional): ID of the source to create the object from. If None, creates an empty object.
        
        Returns:
            bool: True if the object was created successfully, False otherwise
            
        Note:
            Requires a valid project to be loaded. Use get_sources() to see available sources.
            
        Example:
            # Create empty object
            success = create_object("my_object")
            
            # Create object from source
            success = create_object("my_object", "source_123")
        """
        pass
    
    @abstractmethod
    @script_discoverable("assets", "Create a new template, optionally from an object")
    def create_template(self, template_name: str, object_id: str = None) -> bool:
        """Create a new template with the specified name, optionally from an object"""
        pass
    
    @abstractmethod
    def export_assets(self, output_path: Path) -> bool:
        """Export assets to output path"""
        pass
    
    # State Queries
    @abstractmethod
    @script_discoverable("state", "Check if a project is currently loaded")
    def is_project_loaded(self) -> bool:
        """Check if a project is currently loaded.
        
        Returns:
            bool: True if a project is currently loaded and accessible, False otherwise
            
        Example:
            if is_project_loaded():
                print("Project is loaded")
            else:
                print("No project loaded")
        """
        pass
    
    @abstractmethod
    @script_discoverable("state", "Check if the current project has any source assets")
    def has_sources(self) -> bool:
        """Check if the current project has any source assets"""
        pass
    
    @abstractmethod
    @script_discoverable("state", "Check if the current project has any objects")
    def has_objects(self) -> bool:
        """Check if the current project has any objects"""
        pass
    
    @abstractmethod
    @script_discoverable("state", "Check if the current project has any templates")
    def has_templates(self) -> bool:
        """Check if the current project has any templates"""
        pass
    
    @abstractmethod
    @script_discoverable("state", "Get counts of different asset types in the current project")
    def get_asset_counts(self) -> Dict[str, int]:
        """Get counts of different asset types in the current project.
        
        Returns:
            Dict[str, int]: Dictionary containing asset counts:
                - sources (int): Number of source assets
                - objects (int): Number of objects
                - templates (int): Number of templates
                - slices (int): Number of object slices
                
        Example:
            counts = get_asset_counts()
            print(f"Sources: {counts['sources']}, Objects: {counts['objects']}")
        """
        pass
    
    # Detailed State Methods for UI Ghosting
    @abstractmethod
    @script_hidden
    def valid_project(self) -> bool:
        """True if we have a valid, editable project loaded"""
        pass
    
    @abstractmethod
    @script_hidden
    def can_create_project(self) -> bool:
        """True if we can create a new project (no project loaded or current project is closed)"""
        pass
    
    @abstractmethod
    @script_hidden
    def can_open_project(self) -> bool:
        """True if we can open a project (no project loaded or current project is closed)"""
        pass
    
    @abstractmethod
    @script_hidden
    def can_save_project(self) -> bool:
        """True if we can save the current project (valid project loaded with changes)"""
        pass
    
    @abstractmethod
    @script_hidden
    def can_close_project(self) -> bool:
        """True if we can close the current project (valid project loaded)"""
        pass
    
    @abstractmethod
    def can_import_source(self) -> bool:
        """True if we can import a source (valid project loaded)"""
        pass
    
    @abstractmethod
    def can_create_object(self) -> bool:
        """True if we can create an object (valid project loaded and has sources)"""
        pass
    
    @abstractmethod
    def can_create_template(self) -> bool:
        """True if we can create a template (valid project loaded and has objects)"""
        pass
    
    @abstractmethod
    def can_export_assets(self) -> bool:
        """True if we can export assets (valid project loaded and has assets)"""
        pass
    
    @abstractmethod
    def can_edit_sources(self) -> bool:
        """True if we can edit sources (valid project loaded and has sources)"""
        pass
    
    @abstractmethod
    def can_edit_objects(self) -> bool:
        """True if we can edit objects (valid project loaded and has objects)"""
        pass
    
    @abstractmethod
    def can_edit_templates(self) -> bool:
        """True if we can edit templates (valid project loaded and has templates)"""
        pass
    
    # UI State Management
    @abstractmethod
    def get_ui_state(self) -> Dict[str, bool]:
        """Get current UI state (what should be enabled/disabled)"""
        pass
    
    @abstractmethod
    def update_ui_state(self) -> None:
        """Update UI state based on current application state"""
        pass
    
    # Event Handling
    @abstractmethod
    def set_event_handlers(self, handlers: Dict[str, Callable]) -> None:
        """Set event handlers for UI events"""
        pass
    
    @abstractmethod
    def emit_event(self, event_type: str, data: Dict[str, Any]) -> None:
        """Emit an event to the event system"""
        pass
    
    # Data Access
    @abstractmethod
    def get_sources(self) -> List[AssetSource]:
        """Get all sources"""
        pass
    
    @abstractmethod
    def get_objects(self) -> List[CurioObject]:
        """Get all objects"""
        pass
    
    @abstractmethod
    def get_templates(self) -> List[Template]:
        """Get all templates"""
        pass
    
    @abstractmethod
    def get_project_info(self) -> Optional[ProjectInfo]:
        """Get current project information"""
        pass
