"""
Status Bar Event Handler for CurioShelf

This module provides event handlers for status bar updates, allowing the UI
to be updated through the event system for better testability.
"""

from typing import Any, Optional
import logging

from .event_system import (
    event_bus, UIEvent, EventType, UpdateStatusCommand, UpdateProgressCommand,
    ShowErrorCommand, ShowInfoCommand
)


class StatusBarEventHandler:
    """Event handler for status bar updates"""
    
    def __init__(self, status_bar=None):
        self.status_bar = status_bar
        self.logger = logging.getLogger(__name__)
        self._setup_event_handlers()
    
    def set_status_bar(self, status_bar) -> None:
        """Set the status bar widget to update"""
        self.status_bar = status_bar
    
    def _setup_event_handlers(self) -> None:
        """Setup event handlers for status bar updates"""
        event_bus.subscribe(EventType.STATUS_MESSAGE, self._handle_status_message)
        event_bus.subscribe(EventType.PROGRESS_UPDATE, self._handle_progress_update)
        event_bus.subscribe(EventType.ERROR_MESSAGE, self._handle_error_message)
        event_bus.subscribe(EventType.INFO_MESSAGE, self._handle_info_message)
    
    def _handle_status_message(self, event: UIEvent) -> None:
        """Handle status message events"""
        message = event.data.get("message", "Ready")
        self.logger.info(f"Status message: {message}")
        
        if self.status_bar and hasattr(self.status_bar, 'set_message'):
            self.status_bar.set_message(message)
    
    def _handle_progress_update(self, event: UIEvent) -> None:
        """Handle progress update events"""
        progress = event.data.get("progress", 0)
        message = event.data.get("message", f"Progress: {progress}%")
        self.logger.info(f"Progress update: {progress}% - {message}")
        
        if self.status_bar and hasattr(self.status_bar, 'set_message'):
            self.status_bar.set_message(message)
    
    def _handle_error_message(self, event: UIEvent) -> None:
        """Handle error message events"""
        error_message = event.data.get("message", "An error occurred")
        self.logger.error(f"Error message: {error_message}")
        
        if self.status_bar and hasattr(self.status_bar, 'set_message'):
            self.status_bar.set_message(f"Error: {error_message}")
    
    def _handle_info_message(self, event: UIEvent) -> None:
        """Handle info message events"""
        info_message = event.data.get("message", "Information")
        self.logger.info(f"Info message: {info_message}")
        
        if self.status_bar and hasattr(self.status_bar, 'set_message'):
            self.status_bar.set_message(f"Info: {info_message}")
    
    def cleanup(self) -> None:
        """Clean up the status bar event handler"""
        # Unsubscribe from events
        event_bus.unsubscribe(EventType.STATUS_MESSAGE, self._handle_status_message)
        event_bus.unsubscribe(EventType.PROGRESS_UPDATE, self._handle_progress_update)
        event_bus.unsubscribe(EventType.ERROR_MESSAGE, self._handle_error_message)
        event_bus.unsubscribe(EventType.INFO_MESSAGE, self._handle_info_message)


def emit_status_message(message: str, source: str = "system") -> None:
    """Emit a status message event"""
    event = UIEvent(
        event_type=EventType.STATUS_MESSAGE,
        source=source,
        data={"message": message}
    )
    event_bus.emit(event)


def emit_progress_update(progress: int, message: str = None, source: str = "system") -> None:
    """Emit a progress update event"""
    event = UIEvent(
        event_type=EventType.PROGRESS_UPDATE,
        source=source,
        data={"progress": progress, "message": message or f"Progress: {progress}%"}
    )
    event_bus.emit(event)


def emit_error_message(error_message: str, source: str = "system") -> None:
    """Emit an error message event"""
    event = UIEvent(
        event_type=EventType.ERROR_MESSAGE,
        source=source,
        data={"message": error_message}
    )
    event_bus.emit(event)


def emit_info_message(info_message: str, source: str = "system") -> None:
    """Emit an info message event"""
    event = UIEvent(
        event_type=EventType.INFO_MESSAGE,
        source=source,
        data={"message": info_message}
    )
    event_bus.emit(event)


def emit_project_status(project_name: str = None, source: str = "project_manager") -> None:
    """Emit project status update"""
    if project_name:
        message = f"Ready - Project: {project_name}"
    else:
        message = "Ready - No project loaded"
    
    emit_status_message(message, source)


def emit_asset_status(sources: int = 0, templates: int = 0, objects: int = 0, slices: int = 0, source: str = "asset_manager") -> None:
    """Emit asset status update"""
    message = f"Ready - Sources: {sources} | Templates: {templates} | Objects: {objects} | Slices: {slices}"
    emit_status_message(message, source)
