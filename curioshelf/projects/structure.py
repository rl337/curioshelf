"""
Project Structure Definition for CurioShelf

This module defines the concrete structure of a CurioShelf project,
including the curioshelf.json configuration file format and directory layout.
"""

from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Dict, List, Optional, Any
import json
import logging
from datetime import datetime


@dataclass
class ProjectMetadata:
    """Metadata for a CurioShelf project"""
    name: str
    description: str
    author: str
    version: str = "1.0.0"
    created: str = ""
    modified: str = ""
    
    def __post_init__(self):
        if not self.created:
            self.created = datetime.now().isoformat()
        if not self.modified:
            self.modified = self.created
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization"""
        return asdict(self)


@dataclass
class ProjectStructure:
    """Defines the structure of a CurioShelf project"""
    metadata: ProjectMetadata
    sources_dir: str = "sources"
    templates_dir: str = "templates"
    objects_dir: str = "objects"
    build_dir: str = "build"
    config_dir: str = "config"
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization"""
        return {
            "metadata": asdict(self.metadata),
            "directories": {
                "sources": self.sources_dir,
                "templates": self.templates_dir,
                "objects": self.objects_dir,
                "build": self.build_dir,
                "config": self.config_dir
            }
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ProjectStructure':
        """Create from dictionary (JSON deserialization)"""
        metadata = ProjectMetadata(**data["metadata"])
        directories = data.get("directories", {})
        
        return cls(
            metadata=metadata,
            sources_dir=directories.get("sources", "sources"),
            templates_dir=directories.get("templates", "templates"),
            objects_dir=directories.get("objects", "objects"),
            build_dir=directories.get("build", "build"),
            config_dir=directories.get("config", "config")
        )


class ProjectStructureManager:
    """Manages CurioShelf project structure and files"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
    
    def create_project(self, project_path: Path, metadata: ProjectMetadata) -> bool:
        """Create a new CurioShelf project"""
        try:
            # Create project directory
            project_path.mkdir(parents=True, exist_ok=True)
            
            # Create project structure
            structure = ProjectStructure(metadata=metadata)
            
            # Create curioshelf.json
            config_path = project_path / "curioshelf.json"
            with open(config_path, 'w') as f:
                json.dump(structure.to_dict(), f, indent=2)
            
            # Create directory structure
            for dir_name in [structure.sources_dir, structure.templates_dir, 
                           structure.objects_dir, structure.build_dir, structure.config_dir]:
                (project_path / dir_name).mkdir(exist_ok=True)
            
            # Create .gitignore for the project
            gitignore_path = project_path / ".gitignore"
            with open(gitignore_path, 'w') as f:
                f.write("# CurioShelf project\n")
                f.write("build/\n")
                f.write("*.tmp\n")
                f.write("*.log\n")
            
            self.logger.info(f"Created project at {project_path}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to create project at {project_path}: {e}")
            return False
    
    def load_project(self, project_path: Path) -> Optional[ProjectStructure]:
        """Load an existing CurioShelf project"""
        try:
            config_path = project_path / "curioshelf.json"
            if not config_path.exists():
                self.logger.error(f"No curioshelf.json found at {project_path}")
                return None
            
            with open(config_path, 'r') as f:
                data = json.load(f)
            
            structure = ProjectStructure.from_dict(data)
            self.logger.info(f"Loaded project from {project_path}")
            return structure
            
        except Exception as e:
            self.logger.error(f"Failed to load project from {project_path}: {e}")
            return None
    
    def is_project(self, path: Path) -> bool:
        """Check if a path is a valid CurioShelf project"""
        return (path.is_dir() and 
                (path / "curioshelf.json").exists())
    
    def save_project(self, project_path: Path, structure: ProjectStructure) -> bool:
        """Save project structure to curioshelf.json"""
        try:
            # Update modified timestamp
            structure.metadata.modified = datetime.now().isoformat()
            
            config_path = project_path / "curioshelf.json"
            with open(config_path, 'w') as f:
                json.dump(structure.to_dict(), f, indent=2)
            
            self.logger.info(f"Saved project to {project_path}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to save project to {project_path}: {e}")
            return False
    
    def get_project_info(self, project_path: Path) -> Optional[Dict[str, Any]]:
        """Get project information without loading the full structure"""
        try:
            config_path = project_path / "curioshelf.json"
            if not config_path.exists():
                return None
            
            with open(config_path, 'r') as f:
                data = json.load(f)
            
            return data.get("metadata", {})
            
        except Exception as e:
            self.logger.error(f"Failed to get project info from {project_path}: {e}")
            return None
