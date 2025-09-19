"""
Projects Submodule

This module contains all project-related functionality for CurioShelf,
including project structure definition, management, and operations.
"""

from .structure import ProjectMetadata, ProjectStructure, ProjectStructureManager
from .manager import ProjectManager, ProjectInfo

__all__ = [
    'ProjectMetadata',
    'ProjectStructure', 
    'ProjectStructureManager',
    'ProjectManager',
    'ProjectInfo'
]
