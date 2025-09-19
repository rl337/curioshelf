"""
Project management system for CurioShelf

Handles project creation, loading, saving, and state management.
A project is a collection of source files, templates, objects, and metadata
organized in a directory structure or zip file.
"""

import json
import zipfile
import shutil
from pathlib import Path
from typing import Optional, Dict, Any, List
from dataclasses import dataclass, field
from datetime import datetime

from ..models import AssetManager
from ..status_bar_handler import emit_project_status, emit_info_message, emit_error_message


@dataclass
class ProjectInfo:
    """Metadata about a project"""
    name: str
    description: str = ""
    version: str = "1.0.0"
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    modified_at: str = field(default_factory=lambda: datetime.now().isoformat())
    author: str = ""
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "description": self.description,
            "version": self.version,
            "created_at": self.created_at,
            "modified_at": self.modified_at,
            "author": self.author
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ProjectInfo':
        return cls(
            name=data["name"],
            description=data.get("description", ""),
            version=data.get("version", "1.0.0"),
            created_at=data.get("created_at", datetime.now().isoformat()),
            modified_at=data.get("modified_at", datetime.now().isoformat()),
            author=data.get("author", "")
        )


class ProjectManager:
    """Manages project lifecycle and file operations"""
    
    def __init__(self):
        self.current_project_path: Optional[Path] = None
        self.project_info: Optional[ProjectInfo] = None
        self.asset_manager: Optional[AssetManager] = None
        self.is_project_loaded = False
        
        # Project structure
        self.sources_dir = "sources"
        self.templates_dir = "templates"
        self.objects_dir = "objects"
        self.build_dir = "build"
        self.metadata_file = "project.json"
        self.assets_file = "assets.json"
    
    def create_project(self, project_path: Path, project_info: ProjectInfo) -> bool:
        """Create a new project at the specified path"""
        try:
            # Create project directory
            project_path.mkdir(parents=True, exist_ok=True)
            
            # Create subdirectories
            (project_path / self.sources_dir).mkdir(exist_ok=True)
            (project_path / self.templates_dir).mkdir(exist_ok=True)
            (project_path / self.objects_dir).mkdir(exist_ok=True)
            (project_path / self.build_dir).mkdir(exist_ok=True)
            
            # Save project info
            project_info.modified_at = datetime.now().isoformat()
            with open(project_path / self.metadata_file, 'w') as f:
                json.dump(project_info.to_dict(), f, indent=2)
            
            # Initialize empty assets
            empty_assets = {
                "sources": {},
                "objects": {},
                "templates": {}
            }
            with open(project_path / self.assets_file, 'w') as f:
                json.dump(empty_assets, f, indent=2)
            
            # Set as current project
            self.current_project_path = project_path
            self.project_info = project_info
            self.asset_manager = AssetManager()
            self.is_project_loaded = True
            
            # Emit status events
            emit_info_message(f"Project '{project_info.name}' created successfully", "project_manager")
            emit_project_status(project_info.name, "project_manager")
            
            return True
            
        except Exception as e:
            error_msg = f"Error creating project: {e}"
            print(error_msg)
            emit_error_message(error_msg, "project_manager")
            return False
    
    def load_project(self, project_path: Path) -> bool:
        """Load an existing project"""
        try:
            # Check if project exists
            if not project_path.exists() or not project_path.is_dir():
                return False
            
            # Load project info
            project_info_file = project_path / self.metadata_file
            if not project_info_file.exists():
                return False
            
            with open(project_info_file, 'r') as f:
                project_data = json.load(f)
            self.project_info = ProjectInfo.from_dict(project_data)
            
            # Load assets
            assets_file = project_path / self.assets_file
            if assets_file.exists():
                self.asset_manager = AssetManager()
                self.asset_manager.load_metadata(str(assets_file))
            else:
                self.asset_manager = AssetManager()
            
            # Set as current project
            self.current_project_path = project_path
            self.is_project_loaded = True
            
            # Emit status events
            emit_info_message(f"Project '{self.project_info.name}' loaded successfully", "project_manager")
            emit_project_status(self.project_info.name, "project_manager")
            
            return True
            
        except Exception as e:
            error_msg = f"Error loading project: {e}"
            print(error_msg)
            emit_error_message(error_msg, "project_manager")
            return False
    
    def save_project(self) -> bool:
        """Save the current project"""
        if not self.is_project_loaded or not self.current_project_path or not self.asset_manager:
            return False
        
        try:
            # Update project info
            if self.project_info:
                self.project_info.modified_at = datetime.now().isoformat()
                
                # Save project info
                with open(self.current_project_path / self.metadata_file, 'w') as f:
                    json.dump(self.project_info.to_dict(), f, indent=2)
            
            # Save assets
            with open(self.current_project_path / self.assets_file, 'w') as f:
                self.asset_manager.save_metadata(str(self.current_project_path / self.assets_file))
            
            # Emit status events
            emit_info_message(f"Project '{self.project_info.name}' saved successfully", "project_manager")
            
            return True
            
        except Exception as e:
            error_msg = f"Error saving project: {e}"
            print(error_msg)
            emit_error_message(error_msg, "project_manager")
            return False
    
    def close_project(self) -> bool:
        """Close the current project"""
        if not self.is_project_loaded:
            return True
        
        try:
            # Save before closing
            self.save_project()
            
            # Clear project state
            self.current_project_path = None
            self.project_info = None
            self.asset_manager = None
            self.is_project_loaded = False
            
            # Emit status events
            emit_info_message("Project closed", "project_manager")
            emit_project_status(None, "project_manager")
            
            return True
            
        except Exception as e:
            error_msg = f"Error closing project: {e}"
            print(error_msg)
            emit_error_message(error_msg, "project_manager")
            return False
    
    def add_source_file(self, source_path: Path) -> Optional[Path]:
        """Add a source file to the project and return the project-relative path"""
        if not self.is_project_loaded or not self.current_project_path:
            return None
        
        try:
            # Copy file to project sources directory
            project_sources_dir = self.current_project_path / self.sources_dir
            destination = project_sources_dir / source_path.name
            
            # Handle duplicate names
            counter = 1
            original_destination = destination
            while destination.exists():
                stem = original_destination.stem
                suffix = original_destination.suffix
                destination = project_sources_dir / f"{stem}_{counter}{suffix}"
                counter += 1
            
            shutil.copy2(source_path, destination)
            
            # Return relative path from project root
            return destination.relative_to(self.current_project_path)
            
        except Exception as e:
            print(f"Error adding source file: {e}")
            return None
    
    def get_project_relative_path(self, file_path: Path) -> Path:
        """Convert absolute path to project-relative path"""
        if not self.is_project_loaded or not self.current_project_path:
            return file_path
        
        try:
            return file_path.relative_to(self.current_project_path)
        except ValueError:
            # Path is not within project directory
            return file_path
    
    def get_absolute_path(self, relative_path: Path) -> Path:
        """Convert project-relative path to absolute path"""
        if not self.is_project_loaded or not self.current_project_path:
            return relative_path
        
        return self.current_project_path / relative_path
    
    def export_project(self, export_path: Path, include_sources: bool = True) -> bool:
        """Export project as a zip file"""
        if not self.is_project_loaded or not self.current_project_path:
            return False
        
        try:
            with zipfile.ZipFile(export_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
                # Add project metadata
                zipf.write(
                    self.current_project_path / self.metadata_file,
                    self.metadata_file
                )
                zipf.write(
                    self.current_project_path / self.assets_file,
                    self.assets_file
                )
                
                # Add source files if requested
                if include_sources:
                    sources_dir = self.current_project_path / self.sources_dir
                    for source_file in sources_dir.rglob('*'):
                        if source_file.is_file():
                            arcname = source_file.relative_to(self.current_project_path)
                            zipf.write(source_file, arcname)
            
            return True
            
        except Exception as e:
            print(f"Error exporting project: {e}")
            return False
    
    def import_project(self, zip_path: Path, extract_to: Path) -> bool:
        """Import a project from a zip file"""
        try:
            # Create extraction directory
            extract_to.mkdir(parents=True, exist_ok=True)
            
            with zipfile.ZipFile(zip_path, 'r') as zipf:
                zipf.extractall(extract_to)
            
            # Load the extracted project
            return self.load_project(extract_to)
            
        except Exception as e:
            print(f"Error importing project: {e}")
            return False
    
    def get_project_status(self) -> Dict[str, Any]:
        """Get current project status information"""
        if not self.is_project_loaded:
            return {
                "loaded": False,
                "name": "No Project",
                "path": None,
                "sources_count": 0,
                "objects_count": 0,
                "templates_count": 0
            }
        
        sources_count = len(self.asset_manager.sources) if self.asset_manager else 0
        objects_count = len(self.asset_manager.objects) if self.asset_manager else 0
        templates_count = len(self.asset_manager.templates) if self.asset_manager else 0
        
        return {
            "loaded": True,
            "name": self.project_info.name if self.project_info else "Unknown",
            "path": str(self.current_project_path) if self.current_project_path else None,
            "sources_count": sources_count,
            "objects_count": objects_count,
            "templates_count": templates_count
        }
