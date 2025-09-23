"""
Configuration management for CurioShelf
"""

import os
import platform
from pathlib import Path
from typing import Optional


class CurioShelfConfig:
    """Configuration management for CurioShelf"""
    
    def __init__(self):
        self._config = {}
        self._load_defaults()
    
    def _load_defaults(self):
        """Load default configuration values"""
        # Get the appropriate default directory based on OS
        default_project_dir = self._get_default_project_directory()
        
        self._config = {
            "default_project_directory": str(default_project_dir),
            "auto_complete_project_path": True,
            "remember_recent_projects": True,
            "max_recent_projects": 10,
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


# Global configuration instance
config = CurioShelfConfig()
