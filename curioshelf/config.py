"""
Configuration management for CurioShelf
"""

import os
import platform
import json
from pathlib import Path
from typing import Optional, List, Dict, Any


class CurioShelfConfig:
    """Configuration management for CurioShelf"""
    
    def __init__(self):
        self._config = {}
        self._config_file_path = self._get_config_file_path()
        self._load_defaults()
        self._load_from_file()
    
    def _load_defaults(self):
        """Load default configuration values"""
        # Get the appropriate default directory based on OS
        default_project_dir = self._get_default_project_directory()
        
        self._config = {
            "default_project_directory": str(default_project_dir),
            "auto_complete_project_path": True,
            "remember_recent_projects": True,
            "max_recent_projects": 10,
            "recent_projects": [],
        }
    
    def _get_default_project_directory(self) -> Path:
        """Get the default project directory based on the operating system"""
        system = platform.system().lower()
        
        if system == "windows":
            # Windows: Use Documents folder
            documents = os.path.expanduser("~/Documents")
            return Path(documents) / "CurioShelf Projects"
        elif system == "darwin":
            # macOS: Use Documents folder
            documents = os.path.expanduser("~/Documents")
            return Path(documents) / "CurioShelf Projects"
        else:
            # Linux/Unix: Use home directory
            home = os.path.expanduser("~")
            return Path(home) / "CurioShelf Projects"
    
    def get(self, key: str, default=None):
        """Get a configuration value"""
        return self._config.get(key, default)
    
    def set(self, key: str, value):
        """Set a configuration value"""
        self._config[key] = value
    
    def get_default_project_directory(self) -> Path:
        """Get the default project directory"""
        return Path(self._config["default_project_directory"])
    
    def get_project_path_for_name(self, project_name: str) -> Path:
        """Get the suggested project path for a given project name"""
        if not project_name.strip():
            return self.get_default_project_directory()
        
        # Clean the project name (remove invalid characters)
        clean_name = self._clean_project_name(project_name)
        return self.get_default_project_directory() / clean_name
    
    def _clean_project_name(self, name: str) -> str:
        """Clean a project name to be filesystem-safe"""
        # Remove or replace invalid characters
        invalid_chars = '<>:"/\\|?*'
        for char in invalid_chars:
            name = name.replace(char, '_')
        
        # Remove leading/trailing whitespace and dots
        name = name.strip(' .')
        
        # Ensure it's not empty
        if not name:
            name = "Untitled Project"
        
        return name
    
    def _get_config_file_path(self) -> Path:
        """Get the path to the .curioshelf config file"""
        # Look for .curioshelf in current directory first
        current_dir = Path.cwd()
        config_file = current_dir / ".curioshelf"
        if config_file.exists():
            return config_file
        
        # Fall back to home directory
        home_dir = Path.home()
        return home_dir / ".curioshelf"
    
    def _load_from_file(self) -> None:
        """Load configuration from .curioshelf file if it exists"""
        self._config_file_existed = self._config_file_path.exists()
        if not self._config_file_existed:
            return
        
        try:
            with open(self._config_file_path, 'r') as f:
                file_config = json.load(f)
            
            # Merge file config with defaults, preserving defaults for missing keys
            for key, value in file_config.items():
                if key in self._config:
                    self._config[key] = value
        except Exception as e:
            print(f"Warning: Could not load config from {self._config_file_path}: {e}")
    
    def save_to_file(self) -> None:
        """Save configuration to .curioshelf file (only if it previously existed)"""
        # Check if the config file existed when we loaded it
        if not hasattr(self, '_config_file_existed') or not self._config_file_existed:
            return  # Only write back if it previously existed
        
        try:
            with open(self._config_file_path, 'w') as f:
                json.dump(self._config, f, indent=2)
        except Exception as e:
            print(f"Warning: Could not save config to {self._config_file_path}: {e}")
    
    def add_recent_project(self, project_path: Path, project_name: str) -> None:
        """Add a project to the recent projects list"""
        if not self.get("remember_recent_projects", True):
            return
        
        recent_projects = self._config.get("recent_projects", [])
        max_recent = self._config.get("max_recent_projects", 10)
        
        # Remove if already exists
        recent_projects = [p for p in recent_projects if p.get("path") != str(project_path)]
        
        # Add to beginning
        recent_projects.insert(0, {
            "path": str(project_path),
            "name": project_name,
            "last_opened": str(Path(project_path).stat().st_mtime) if project_path.exists() else "0"
        })
        
        # Trim to max length
        recent_projects = recent_projects[:max_recent]
        
        self._config["recent_projects"] = recent_projects
        self.save_to_file()
    
    def get_recent_projects(self) -> List[Dict[str, Any]]:
        """Get the list of recent projects"""
        recent_projects = self._config.get("recent_projects", [])
        
        # Filter out projects that no longer exist
        valid_projects = []
        for project in recent_projects:
            project_path = Path(project.get("path", ""))
            if project_path.exists() and (project_path / "curioshelf.json").exists():
                valid_projects.append(project)
        
        # Update the config if we filtered out any projects
        if len(valid_projects) != len(recent_projects):
            self._config["recent_projects"] = valid_projects
            self.save_to_file()
        
        return valid_projects


# Global configuration instance
config = CurioShelfConfig()
