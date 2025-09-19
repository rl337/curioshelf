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
from .ui_state_manager import UIStateManager


class ApplicationInterface(ABC):
    """Abstract interface for the main application object"""
    
    # Project Management
    @abstractmethod
    def create_project(self, project_path: Path, project_info: ProjectInfo) -> bool:
        """Create a new project"""
        pass
    
    @abstractmethod
    def load_project(self, project_path: Path) -> bool:
        """Load an existing project"""
        pass
    
    @abstractmethod
    def save_project(self) -> bool:
        """Save the current project"""
        pass
    
    @abstractmethod
    def close_project(self) -> bool:
        """Close the current project"""
        pass
    
    @abstractmethod
    def get_project_status(self) -> Dict[str, Any]:
        """Get current project status"""
        pass
    
    # Asset Management
    @abstractmethod
    def import_source(self, file_path: Path) -> bool:
        """Import a source image"""
        pass
    
    @abstractmethod
    def create_object(self, object_name: str, source_id: str = None) -> bool:
        """Create a new object"""
        pass
    
    @abstractmethod
    def create_template(self, template_name: str, object_id: str = None) -> bool:
        """Create a new template"""
        pass
    
    @abstractmethod
    def export_assets(self, output_path: Path) -> bool:
        """Export assets to output path"""
        pass
    
    # State Queries
    @abstractmethod
    def is_project_loaded(self) -> bool:
        """Check if a project is currently loaded"""
        pass
    
    @abstractmethod
    def has_sources(self) -> bool:
        """Check if project has any sources"""
        pass
    
    @abstractmethod
    def has_objects(self) -> bool:
        """Check if project has any objects"""
        pass
    
    @abstractmethod
    def has_templates(self) -> bool:
        """Check if project has any templates"""
        pass
    
    @abstractmethod
    def get_asset_counts(self) -> Dict[str, int]:
        """Get counts of different asset types"""
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
