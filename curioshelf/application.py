"""
Main Application Implementation for CurioShelf

This module provides the main application object that aggregates all controllers
and provides a clean interface for UI interactions.
"""

from .application_interface import ApplicationInterface
from .app_impl.application_impl import CurioShelfApplicationImpl


class CurioShelfApplication(CurioShelfApplicationImpl):
    """Main application object that aggregates all controllers"""
    
    def __init__(self, ui_factory=None):
        super().__init__(ui_factory)