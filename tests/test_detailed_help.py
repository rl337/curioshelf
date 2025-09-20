#!/usr/bin/env python3
"""
Test script to demonstrate the detailed help system with improved docstrings.
This script creates a mock application that uses the interface decorators.
"""

import sys
from pathlib import Path

# Add the project root to the path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from curioshelf.ui.script.reflection import CommandReflector
from curioshelf.application_interface import ApplicationInterface
from abc import abstractmethod
from typing import Any, Dict, List, Optional
from pathlib import Path


class ConcreteTestApplication(ApplicationInterface):
    """Test application that implements the interface with decorators"""
    
    def __init__(self):
        self._project_loaded = False
        self._project_info = None
        self._sources = []
        self._objects = []
        self._templates = []
    
    # Project Management
    def create_project(self, project_path: Path, project_info) -> bool:
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
        self._project_loaded = True
        self._project_info = project_info
        return True
    
    def load_project(self, project_path: Path) -> bool:
        """Load an existing project from the specified path.
        
        Args:
            project_path (Path): The file system path to the project directory containing curioshelf.json
        
        Returns:
            bool: True if the project was loaded successfully, False otherwise
            
        Example:
            success = load_project("/path/to/existing/project")
        """
        self._project_loaded = True
        return True
    
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
        return self._project_loaded
    
    def close_project(self) -> bool:
        """Close the currently loaded project and clear the workspace.
        
        Returns:
            bool: True if the project was closed successfully, False otherwise
            
        Note:
            This clears all project data from memory. Use save_project() first if needed.
            
        Example:
            success = close_project()
        """
        self._project_loaded = False
        self._project_info = None
        return True
    
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
        return {
            "loaded": self._project_loaded,
            "name": self._project_info.get("name") if self._project_info else None,
            "path": None,
            "sources_count": len(self._sources),
            "objects_count": len(self._objects),
            "templates_count": len(self._templates)
        }
    
    # Asset Management
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
        if not self._project_loaded:
            return False
        self._sources.append(str(file_path))
        return True
    
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
        if not self._project_loaded:
            return False
        self._objects.append(object_name)
        return True
    
    def create_template(self, template_name: str, object_id: str = None) -> bool:
        """Create a new template with the specified name, optionally from an object.
        
        Args:
            template_name (str): The name for the new template
            object_id (str, optional): ID of the object to create the template from. If None, creates an empty template.
        
        Returns:
            bool: True if the template was created successfully, False otherwise
            
        Note:
            Requires a valid project to be loaded. Use get_objects() to see available objects.
            
        Example:
            # Create empty template
            success = create_template("my_template")
            
            # Create template from object
            success = create_template("my_template", "object_123")
        """
        if not self._project_loaded:
            return False
        self._templates.append(template_name)
        return True
    
    def export_assets(self, output_path: Path) -> bool:
        """Export all project assets to the specified output path.
        
        Args:
            output_path (Path): The directory path where assets should be exported
        
        Returns:
            bool: True if assets were exported successfully, False otherwise
            
        Example:
            success = export_assets("/path/to/export/directory")
        """
        return self._project_loaded
    
    def get_sources(self) -> List[str]:
        """Get a list of all source assets in the current project.
        
        Returns:
            List[str]: List of source asset names/IDs
            
        Example:
            sources = get_sources()
            print(f"Found {len(sources)} sources")
        """
        return self._sources.copy()
    
    def get_objects(self) -> List[str]:
        """Get a list of all objects in the current project.
        
        Returns:
            List[str]: List of object names/IDs
            
        Example:
            objects = get_objects()
            print(f"Found {len(objects)} objects")
        """
        return self._objects.copy()
    
    def get_templates(self) -> List[str]:
        """Get a list of all templates in the current project.
        
        Returns:
            List[str]: List of template names/IDs
            
        Example:
            templates = get_templates()
            print(f"Found {len(templates)} templates")
        """
        return self._templates.copy()
    
    # State Queries
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
        return self._project_loaded
    
    def has_sources(self) -> bool:
        """Check if the current project has any source assets.
        
        Returns:
            bool: True if the project has source assets, False otherwise
            
        Example:
            if has_sources():
                print("Project has sources")
        """
        return len(self._sources) > 0
    
    def has_objects(self) -> bool:
        """Check if the current project has any objects.
        
        Returns:
            bool: True if the project has objects, False otherwise
            
        Example:
            if has_objects():
                print("Project has objects")
        """
        return len(self._objects) > 0
    
    def has_templates(self) -> bool:
        """Check if the current project has any templates.
        
        Returns:
            bool: True if the project has templates, False otherwise
            
        Example:
            if has_templates():
                print("Project has templates")
        """
        return len(self._templates) > 0
    
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
        return {
            "sources": len(self._sources),
            "objects": len(self._objects),
            "templates": len(self._templates),
            "slices": 0
        }
    
    # Hidden methods (not discoverable)
    def valid_project(self) -> bool:
        """True if we have a valid, editable project loaded"""
        return self._project_loaded
    
    def can_create_project(self) -> bool:
        """True if we can create a new project (no project loaded or current project is closed)"""
        return not self._project_loaded
    
    def can_open_project(self) -> bool:
        """True if we can open a project (no project loaded or current project is closed)"""
        return not self._project_loaded
    
    def can_save_project(self) -> bool:
        """True if we can save the current project (valid project loaded with changes)"""
        return self._project_loaded
    
    def can_close_project(self) -> bool:
        """True if we can close the current project (valid project loaded)"""
        return self._project_loaded
    
    def can_import_source(self) -> bool:
        """True if we can import a source (valid project loaded)"""
        return self._project_loaded
    
    def can_create_object(self) -> bool:
        """True if we can create an object (valid project loaded and has sources)"""
        return self._project_loaded and len(self._sources) > 0
    
    def can_create_template(self) -> bool:
        """True if we can create a template (valid project loaded and has objects)"""
        return self._project_loaded and len(self._objects) > 0
    
    def can_export_assets(self) -> bool:
        """True if we can export assets (valid project loaded and has assets)"""
        return self._project_loaded and (len(self._sources) > 0 or len(self._objects) > 0 or len(self._templates) > 0)
    
    def can_edit_sources(self) -> bool:
        """True if we can edit sources (valid project loaded and has sources)"""
        return self._project_loaded and len(self._sources) > 0
    
    def can_edit_objects(self) -> bool:
        """True if we can edit objects (valid project loaded and has objects)"""
        return self._project_loaded and len(self._objects) > 0
    
    def can_edit_templates(self) -> bool:
        """True if we can edit templates (valid project loaded and has templates)"""
        return self._project_loaded and len(self._templates) > 0
    
    def get_project_info(self) -> Dict[str, Any]:
        """Get current project information"""
        return self._project_info or {}
    
    def get_ui_state(self) -> Dict[str, Any]:
        """Get current UI state (what should be enabled/disabled)"""
        return {
            "can_create_project": self.can_create_project(),
            "can_open_project": self.can_open_project(),
            "can_save_project": self.can_save_project(),
            "can_close_project": self.can_close_project(),
            "can_import_source": self.can_import_source(),
            "can_create_object": self.can_create_object(),
            "can_create_template": self.can_create_template(),
            "can_export_assets": self.can_export_assets()
        }
    
    def emit_event(self, event_type: str, data: Any = None) -> None:
        """Emit an event to the event system"""
        pass
    
    def set_event_handlers(self, handlers: Dict[str, callable]) -> None:
        """Set event handlers for UI events"""
        pass
    
    def update_ui_state(self) -> None:
        """Update UI state based on current application state"""
        pass


def main():
    """Test the detailed help system"""
    print("=== CurioShelf Detailed Help System Test ===")
    print()
    
    # Create test application
    app = ConcreteTestApplication()
    
    # Create command reflector
    reflector = CommandReflector()
    reflector.reflect_interface(app)
    
    # Show help for all commands
    print("Available Commands:")
    print("=" * 50)
    help_text = reflector.get_command_help()
    print(help_text)
    
    # Show detailed help for specific commands
    print("\nDetailed Help for Specific Commands:")
    print("=" * 50)
    
    commands_to_show = ["create_project", "get_project_status", "import_source", "create_object", "is_project_loaded", "get_asset_counts"]
    
    for cmd_name in commands_to_show:
        print(f"\n--- Help for '{cmd_name}' ---")
        detailed_help = reflector.get_command_help(cmd_name)
        print(detailed_help)
    
    print("\n=== Test Complete ===")


if __name__ == "__main__":
    main()
