"""
Event System for CurioShelf

This module provides a comprehensive event system that allows UI events to be
mapped to command handlers through a chain of command pattern. This enables
rigorous testing of UI interactions without triggering actual business logic.
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional, Callable, Type
from dataclasses import dataclass
from enum import Enum
import logging


class EventType(Enum):
    """Types of events that can be emitted"""
    MENU_ITEM_CLICKED = "menu_item_clicked"
    BUTTON_CLICKED = "button_clicked"
    TEXT_CHANGED = "text_changed"
    SELECTION_CHANGED = "selection_changed"
    PROJECT_LOADED = "project_loaded"
    PROJECT_SAVED = "project_saved"
    PROJECT_CLOSED = "project_closed"
    SOURCE_IMPORTED = "source_imported"
    OBJECT_CREATED = "object_created"
    TEMPLATE_CREATED = "template_created"
    UI_STATE_CHANGED = "ui_state_changed"
    STATUS_MESSAGE = "status_message"
    PROGRESS_UPDATE = "progress_update"
    ERROR_MESSAGE = "error_message"
    INFO_MESSAGE = "info_message"
    # New event types for event execution layer
    HOTKEY_PRESSED = "hotkey_pressed"
    DIALOG_ACCEPTED = "dialog_accepted"
    DIALOG_REJECTED = "dialog_rejected"
    SUCCESS = "success"
    ERROR = "error"


@dataclass
class UIEvent:
    """Represents a UI event with context"""
    event_type: EventType
    source: str  # Widget or component that emitted the event
    data: Dict[str, Any]  # Event-specific data
    timestamp: float = 0.0
    
    def __post_init__(self):
        import time
        if self.timestamp == 0.0:
            self.timestamp = time.time()


class Command(ABC):
    """Abstract base class for commands"""
    
    def __init__(self, context: Dict[str, Any] = None):
        self.context = context or {}
        self.executed = False
        self.result: Any = None
        self.error: Optional[Exception] = None
    
    @abstractmethod
    def execute(self) -> Any:
        """Execute the command"""
        pass
    
    @abstractmethod
    def can_execute(self) -> bool:
        """Check if the command can be executed"""
        pass
    
    def undo(self) -> Any:
        """Undo the command (optional)"""
        pass


class CommandHandler(ABC):
    """Abstract base class for command handlers"""
    
    @abstractmethod
    def can_handle(self, command: Command) -> bool:
        """Check if this handler can handle the given command"""
        pass
    
    @abstractmethod
    def handle(self, command: Command) -> Any:
        """Handle the command"""
        pass


class EventBus:
    """Central event bus for managing events and commands"""
    
    def __init__(self):
        self._event_handlers: Dict[EventType, List[Callable[[UIEvent], None]]] = {}
        self._command_handlers: List[CommandHandler] = []
        self._event_history: List[UIEvent] = []
        self._command_history: List[Command] = []
        self._logger = logging.getLogger(__name__)
    
    def subscribe(self, event_type: EventType, handler: Callable[[UIEvent], None]) -> None:
        """Subscribe to events of a specific type"""
        if event_type not in self._event_handlers:
            self._event_handlers[event_type] = []
        self._event_handlers[event_type].append(handler)
        self._logger.debug(f"Subscribed handler to {event_type}")
    
    def unsubscribe(self, event_type: EventType, handler: Callable[[UIEvent], None]) -> None:
        """Unsubscribe from events of a specific type"""
        if event_type in self._event_handlers:
            try:
                self._event_handlers[event_type].remove(handler)
                self._logger.debug(f"Unsubscribed handler from {eventType}")
            except ValueError:
                pass
    
    def emit(self, event: UIEvent) -> None:
        """Emit an event to all subscribers"""
        self._event_history.append(event)
        self._logger.debug(f"Emitting event: {event.event_type} from {event.source}")
        
        if event.event_type in self._event_handlers:
            for handler in self._event_handlers[event.event_type]:
                try:
                    handler(event)
                except Exception as e:
                    self._logger.error(f"Error in event handler: {e}")
    
    def register_command_handler(self, handler: CommandHandler) -> None:
        """Register a command handler"""
        self._command_handlers.append(handler)
        self._logger.debug(f"Registered command handler: {handler.__class__.__name__}")
    
    def execute_command(self, command: Command) -> Any:
        """Execute a command through the command chain"""
        self._command_history.append(command)
        self._logger.debug(f"Executing command: {command.__class__.__name__}")
        
        if not command.can_execute():
            raise ValueError(f"Command {command.__class__.__name__} cannot be executed")
        
        # Find a handler that can handle this command
        for handler in self._command_handlers:
            if handler.can_handle(command):
                try:
                    command.result = handler.handle(command)
                    command.executed = True
                    self._logger.debug(f"Command executed successfully by {handler.__class__.__name__}")
                    return command.result
                except Exception as e:
                    command.error = e
                    self._logger.error(f"Error executing command: {e}")
                    raise
        
        raise ValueError(f"No handler found for command {command.__class__.__name__}")
    
    def get_event_history(self, event_type: Optional[EventType] = None) -> List[UIEvent]:
        """Get event history, optionally filtered by type"""
        if event_type:
            return [e for e in self._event_history if e.event_type == event_type]
        return self._event_history.copy()
    
    def get_command_history(self) -> List[Command]:
        """Get command history"""
        return self._command_history.copy()
    
    def clear_history(self) -> None:
        """Clear event and command history"""
        self._event_history.clear()
        self._command_history.clear()
        self._logger.debug("Cleared event and command history")


# Global event bus instance
event_bus = EventBus()


# Specific command classes for common operations
class NewProjectCommand(Command):
    """Command for creating a new project"""
    
    def __init__(self, project_name: str = None, author: str = None, **kwargs):
        super().__init__(kwargs)
        self.project_name = project_name
        self.author = author
    
    def execute(self) -> Any:
        """Execute new project creation"""
        return {"action": "new_project", "project_name": self.project_name, "author": self.author}
    
    def can_execute(self) -> bool:
        """New project can always be created"""
        return True


class OpenProjectCommand(Command):
    """Command for opening an existing project"""
    
    def __init__(self, project_path: str = None, **kwargs):
        super().__init__(kwargs)
        self.project_path = project_path
    
    def execute(self) -> Any:
        """Execute project opening"""
        return {"action": "open_project", "project_path": self.project_path}
    
    def can_execute(self) -> bool:
        """Open project can always be executed"""
        return True


class SaveProjectCommand(Command):
    """Command for saving the current project"""
    
    def __init__(self, **kwargs):
        super().__init__(kwargs)
    
    def execute(self) -> Any:
        """Execute project saving"""
        return {"action": "save_project"}
    
    def can_execute(self) -> bool:
        """Save project requires a loaded project"""
        return self.context.get("project_loaded", False)


class CloseProjectCommand(Command):
    """Command for closing the current project"""
    
    def __init__(self, **kwargs):
        super().__init__(kwargs)
    
    def execute(self) -> Any:
        """Execute project closing"""
        return {"action": "close_project"}
    
    def can_execute(self) -> bool:
        """Close project requires a loaded project"""
        return self.context.get("project_loaded", False)


class ImportSourceCommand(Command):
    """Command for importing a source image"""
    
    def __init__(self, file_path: str = None, **kwargs):
        super().__init__(kwargs)
        self.file_path = file_path
    
    def execute(self) -> Any:
        """Execute source import"""
        return {"action": "import_source", "file_path": self.file_path}
    
    def can_execute(self) -> bool:
        """Import source requires a loaded project"""
        return self.context.get("project_loaded", False)


class CreateObjectCommand(Command):
    """Command for creating a new object"""
    
    def __init__(self, object_name: str = None, **kwargs):
        super().__init__(kwargs)
        self.object_name = object_name
    
    def execute(self) -> Any:
        """Execute object creation"""
        return {"action": "create_object", "object_name": self.object_name}
    
    def can_execute(self) -> bool:
        """Create object requires a loaded project"""
        return self.context.get("project_loaded", False)


class CreateTemplateCommand(Command):
    """Command for creating a new template"""
    
    def __init__(self, template_name: str = None, **kwargs):
        super().__init__(kwargs)
        self.template_name = template_name
    
    def execute(self) -> Any:
        """Execute template creation"""
        return {"action": "create_template", "template_name": self.template_name}
    
    def can_execute(self) -> bool:
        """Create template requires a loaded project"""
        return self.context.get("project_loaded", False)


class UpdateStatusCommand(Command):
    """Command for updating the status bar message"""
    
    def __init__(self, message: str, **kwargs):
        super().__init__(kwargs)
        self.message = message
    
    def execute(self) -> Any:
        """Execute status update"""
        return {"action": "update_status", "message": self.message}
    
    def can_execute(self) -> bool:
        """Status updates can always be executed"""
        return True


class UpdateProgressCommand(Command):
    """Command for updating progress information"""
    
    def __init__(self, progress: int, message: str = None, **kwargs):
        super().__init__(kwargs)
        self.progress = progress
        self.message = message
    
    def execute(self) -> Any:
        """Execute progress update"""
        return {"action": "update_progress", "progress": self.progress, "message": self.message}
    
    def can_execute(self) -> bool:
        """Progress updates can always be executed"""
        return True


class ShowErrorCommand(Command):
    """Command for showing error messages"""
    
    def __init__(self, error_message: str, **kwargs):
        super().__init__(kwargs)
        self.error_message = error_message
    
    def execute(self) -> Any:
        """Execute error display"""
        return {"action": "show_error", "message": self.error_message}
    
    def can_execute(self) -> bool:
        """Error messages can always be shown"""
        return True


class ShowInfoCommand(Command):
    """Command for showing info messages"""
    
    def __init__(self, info_message: str, **kwargs):
        super().__init__(kwargs)
        self.info_message = info_message
    
    def execute(self) -> Any:
        """Execute info display"""
        return {"action": "show_info", "message": self.info_message}
    
    def can_execute(self) -> bool:
        """Info messages can always be shown"""
        return True
