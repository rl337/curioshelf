"""
Test Command Handlers for CurioShelf

This module provides test implementations of command handlers that can be used
for testing UI interactions without triggering actual business logic.
"""

from typing import Any, Dict, List
import logging

from curioshelf.event_system import Command, CommandHandler, EventBus, UIEvent, EventType


class MockCommandHandler(CommandHandler):
    """Test implementation of command handler that logs commands instead of executing them"""
    
    def __init__(self):
        self.executed_commands: List[Command] = []
        self.logger = logging.getLogger(__name__)
    
    def can_handle(self, command: Command) -> bool:
        """Test handler can handle any command"""
        return True
    
    def handle(self, command: Command) -> Any:
        """Handle command by logging it"""
        self.executed_commands.append(command)
        self.logger.info(f"TEST: Executed command {command.__class__.__name__}")
        
        # Return mock result based on command type
        if hasattr(command, 'execute'):
            return command.execute()
        return {"status": "test_executed", "command": command.__class__.__name__}
    
    def get_executed_commands(self) -> List[Command]:
        """Get list of executed commands"""
        return self.executed_commands.copy()
    
    def clear_executed_commands(self) -> None:
        """Clear executed commands list"""
        self.executed_commands.clear()


class MockBusinessLogicHandler(CommandHandler):
    """Mock business logic handler that simulates business operations"""
    
    def __init__(self):
        self.project_loaded = False
        self.current_project = None
        self.sources = []
        self.objects = []
        self.templates = []
        self.logger = logging.getLogger(__name__)
    
    def can_handle(self, command: Command) -> bool:
        """Handle all business logic commands"""
        return True
    
    def handle(self, command: Command) -> Any:
        """Handle command with mock business logic"""
        command_name = command.__class__.__name__
        self.logger.info(f"MOCK: Handling {command_name}")
        
        if command_name == "NewProjectCommand":
            return self._handle_new_project(command)
        elif command_name == "OpenProjectCommand":
            return self._handle_open_project(command)
        elif command_name == "SaveProjectCommand":
            return self._handle_save_project(command)
        elif command_name == "CloseProjectCommand":
            return self._handle_close_project(command)
        elif command_name == "ImportSourceCommand":
            return self._handle_import_source(command)
        elif command_name == "CreateObjectCommand":
            return self._handle_create_object(command)
        elif command_name == "CreateTemplateCommand":
            return self._handle_create_template(command)
        else:
            return {"status": "unknown_command", "command": command_name}
    
    def _handle_new_project(self, command) -> Dict[str, Any]:
        """Handle new project creation"""
        project_name = getattr(command, 'project_name', 'Test Project')
        self.current_project = project_name
        self.project_loaded = True
        self.sources = []
        self.objects = []
        self.templates = []
        return {
            "status": "success",
            "action": "new_project",
            "project_name": project_name,
            "message": f"Created new project: {project_name}"
        }
    
    def _handle_open_project(self, command) -> Dict[str, Any]:
        """Handle project opening"""
        project_path = getattr(command, 'project_path', '/test/project')
        self.current_project = f"Project from {project_path}"
        self.project_loaded = True
        self.sources = ["test_source1.png", "test_source2.jpg"]
        self.objects = ["test_object1", "test_object2"]
        self.templates = ["test_template1", "test_template2"]
        return {
            "status": "success",
            "action": "open_project",
            "project_path": project_path,
            "message": f"Opened project from {project_path}"
        }
    
    def _handle_save_project(self, command) -> Dict[str, Any]:
        """Handle project saving"""
        if not self.project_loaded:
            return {
                "status": "error",
                "action": "save_project",
                "message": "No project loaded to save"
            }
        return {
            "status": "success",
            "action": "save_project",
            "message": f"Saved project: {self.current_project}"
        }
    
    def _handle_close_project(self, command) -> Dict[str, Any]:
        """Handle project closing"""
        if not self.project_loaded:
            return {
                "status": "error",
                "action": "close_project",
                "message": "No project loaded to close"
            }
        old_project = self.current_project
        self.current_project = None
        self.project_loaded = False
        self.sources = []
        self.objects = []
        self.templates = []
        return {
            "status": "success",
            "action": "close_project",
            "message": f"Closed project: {old_project}"
        }
    
    def _handle_import_source(self, command) -> Dict[str, Any]:
        """Handle source import"""
        if not self.project_loaded:
            return {
                "status": "error",
                "action": "import_source",
                "message": "No project loaded"
            }
        file_path = getattr(command, 'file_path', 'test_source.png')
        self.sources.append(file_path)
        return {
            "status": "success",
            "action": "import_source",
            "file_path": file_path,
            "message": f"Imported source: {file_path}"
        }
    
    def _handle_create_object(self, command) -> Dict[str, Any]:
        """Handle object creation"""
        if not self.project_loaded:
            return {
                "status": "error",
                "action": "create_object",
                "message": "No project loaded"
            }
        object_name = getattr(command, 'object_name', 'New Object')
        self.objects.append(object_name)
        return {
            "status": "success",
            "action": "create_object",
            "object_name": object_name,
            "message": f"Created object: {object_name}"
        }
    
    def _handle_create_template(self, command) -> Dict[str, Any]:
        """Handle template creation"""
        if not self.project_loaded:
            return {
                "status": "error",
                "action": "create_template",
                "message": "No project loaded"
            }
        template_name = getattr(command, 'template_name', 'New Template')
        self.templates.append(template_name)
        return {
            "status": "success",
            "action": "create_template",
            "template_name": template_name,
            "message": f"Created template: {template_name}"
        }
    
    def get_state(self) -> Dict[str, Any]:
        """Get current mock state"""
        return {
            "project_loaded": self.project_loaded,
            "current_project": self.current_project,
            "sources": self.sources.copy(),
            "objects": self.objects.copy(),
            "templates": self.templates.copy()
        }


class EventLogger:
    """Utility class for logging events during testing"""
    
    def __init__(self):
        self.events: List[UIEvent] = []
        self.logger = logging.getLogger(__name__)
    
    def log_event(self, event: UIEvent) -> None:
        """Log an event"""
        self.events.append(event)
        self.logger.info(f"EVENT: {event.event_type} from {event.source} with data {event.data}")
    
    def get_events(self, event_type: EventType = None) -> List[UIEvent]:
        """Get logged events, optionally filtered by type"""
        if event_type:
            return [e for e in self.events if e.event_type == event_type]
        return self.events.copy()
    
    def clear_events(self) -> None:
        """Clear logged events"""
        self.events.clear()
