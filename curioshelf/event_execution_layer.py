"""
Event Execution Layer for CurioShelf

This module provides an event execution layer that sits between UI events
and the application interface. It handles complex command execution logic
and allows for multiple input methods (menus, hotkeys, etc.) to trigger
the same commands.
"""

from typing import Any, Dict, Optional, Callable, List
from pathlib import Path
import logging

from .event_system import UIEvent, EventType, EventBus, event_bus
from .application_interface import ApplicationInterface


class EventExecutor:
    """Executes UI events by mapping them to application interface calls"""
    
    def __init__(self, application: ApplicationInterface):
        self.app = application
        self.logger = logging.getLogger(__name__)
        
        # Register event handlers
        self._register_event_handlers()
    
    def _register_event_handlers(self) -> None:
        """Register event handlers for different event types"""
        event_bus.subscribe(EventType.MENU_ITEM_CLICKED, self._handle_menu_click)
        event_bus.subscribe(EventType.HOTKEY_PRESSED, self._handle_hotkey)
        event_bus.subscribe(EventType.BUTTON_CLICKED, self._handle_button_click)
        event_bus.subscribe(EventType.DIALOG_ACCEPTED, self._handle_dialog_accepted)
        event_bus.subscribe(EventType.DIALOG_REJECTED, self._handle_dialog_rejected)
    
    def _handle_menu_click(self, event: UIEvent) -> None:
        """Handle menu item click events"""
        menu_item = event.data.get('menu_item')
        if not menu_item:
            self.logger.warning("Menu click event missing menu_item data")
            return
        
        self.logger.info(f"Menu clicked: {menu_item}")
        self._execute_command(menu_item, event.data)
    
    def _handle_hotkey(self, event: UIEvent) -> None:
        """Handle hotkey press events"""
        hotkey = event.data.get('hotkey')
        if not hotkey:
            self.logger.warning("Hotkey event missing hotkey data")
            return
        
        self.logger.info(f"Hotkey pressed: {hotkey}")
        self._execute_command(hotkey, event.data)
    
    def _handle_button_click(self, event: UIEvent) -> None:
        """Handle button click events"""
        button_action = event.data.get('action')
        if not button_action:
            self.logger.warning("Button click event missing action data")
            return
        
        self.logger.info(f"Button clicked: {button_action}")
        self._execute_command(button_action, event.data)
    
    def _handle_dialog_accepted(self, event: UIEvent) -> None:
        """Handle dialog accepted events"""
        dialog_type = event.data.get('dialog_type')
        if not dialog_type:
            self.logger.warning("Dialog accepted event missing dialog_type data")
            return
        
        self.logger.info(f"Dialog accepted: {dialog_type}")
        self._execute_command(f"{dialog_type}_accepted", event.data)
    
    def _handle_dialog_rejected(self, event: UIEvent) -> None:
        """Handle dialog rejected events"""
        dialog_type = event.data.get('dialog_type')
        if not dialog_type:
            self.logger.warning("Dialog rejected event missing dialog_type data")
            return
        
        self.logger.info(f"Dialog rejected: {dialog_type}")
        # Usually no action needed for rejected dialogs
        self.logger.debug(f"No action for rejected {dialog_type} dialog")
    
    def _execute_command(self, command: str, data: Dict[str, Any]) -> None:
        """Execute a command based on the command string and data"""
        try:
            if command == "new_project":
                self._execute_new_project(data)
            elif command == "open_project":
                self._execute_open_project(data)
            elif command == "save_project":
                self._execute_save_project(data)
            elif command == "close_project":
                self._execute_close_project(data)
            elif command == "import_source":
                self._execute_import_source(data)
            elif command == "create_object":
                self._execute_create_object(data)
            elif command == "create_template":
                self._execute_create_template(data)
            elif command == "export_assets":
                self._execute_export_assets(data)
            elif command == "project_dialog_accepted":
                self._execute_project_dialog_accepted(data)
            elif command == "project_dialog_rejected":
                self._execute_project_dialog_rejected(data)
            else:
                self.logger.warning(f"Unknown command: {command}")
        except Exception as e:
            self.logger.error(f"Error executing command {command}: {e}")
            # Emit error event
            event_bus.emit(UIEvent(
                event_type=EventType.ERROR,
                source="event_executor",
                data={"error": str(e), "command": command}
            ))
    
    def _execute_new_project(self, data: Dict[str, Any]) -> None:
        """Execute new project creation"""
        # This will typically trigger a project dialog
        # The actual creation happens when the dialog is accepted
        self.logger.info("New project command - should show project dialog")
    
    def _execute_open_project(self, data: Dict[str, Any]) -> None:
        """Execute project opening"""
        # This will typically trigger a file dialog
        # The actual opening happens when a file is selected
        self.logger.info("Open project command - should show file dialog")
    
    def _execute_save_project(self, data: Dict[str, Any]) -> None:
        """Execute project saving"""
        try:
            if not self.app.is_project_loaded():
                self.logger.warning("Cannot save project - no project loaded")
                return
            
            success = self.app.save_project()
            if success:
                self.logger.info("Project saved successfully")
                # Emit success event
                event_bus.emit(UIEvent(
                    event_type=EventType.SUCCESS,
                    source="event_executor",
                    data={"action": "save_project", "message": "Project saved successfully"}
                ))
            else:
                self.logger.error("Failed to save project")
                # Emit error event
                event_bus.emit(UIEvent(
                    event_type=EventType.ERROR,
                    source="event_executor",
                    data={"action": "save_project", "error": "Failed to save project"}
                ))
        except Exception as e:
            self.logger.error(f"Error saving project: {e}")
            # Emit error event
            event_bus.emit(UIEvent(
                event_type=EventType.ERROR,
                source="event_executor",
                data={"action": "save_project", "error": str(e)}
            ))
    
    def _execute_close_project(self, data: Dict[str, Any]) -> None:
        """Execute project closing"""
        if not self.app.is_project_loaded():
            self.logger.warning("Cannot close project - no project loaded")
            return
        
        # Check if there are unsaved changes
        # For now, we'll just close without checking
        success = self.app.close_project()
        if success:
            self.logger.info("Project closed successfully")
            # Emit success event
            event_bus.emit(UIEvent(
                event_type=EventType.SUCCESS,
                source="event_executor",
                data={"action": "close_project", "message": "Project closed successfully"}
            ))
        else:
            self.logger.error("Failed to close project")
            # Emit error event
            event_bus.emit(UIEvent(
                event_type=EventType.ERROR,
                source="event_executor",
                data={"action": "close_project", "error": "Failed to close project"}
            ))
    
    def _execute_import_source(self, data: Dict[str, Any]) -> None:
        """Execute source import"""
        if not self.app.is_project_loaded():
            self.logger.warning("Cannot import source - no project loaded")
            return
        
        # This will typically trigger a file dialog
        # The actual import happens when a file is selected
        self.logger.info("Import source command - should show file dialog")
    
    def _execute_create_object(self, data: Dict[str, Any]) -> None:
        """Execute object creation"""
        if not self.app.is_project_loaded():
            self.logger.warning("Cannot create object - no project loaded")
            return
        
        object_name = data.get('object_name', 'New Object')
        template_name = data.get('template_name')
        
        success = self.app.create_object(object_name, template_name)
        if success:
            self.logger.info(f"Object '{object_name}' created successfully")
            # Emit success event
            event_bus.emit(UIEvent(
                event_type=EventType.SUCCESS,
                source="event_executor",
                data={"action": "create_object", "object_name": object_name}
            ))
        else:
            self.logger.error(f"Failed to create object '{object_name}'")
            # Emit error event
            event_bus.emit(UIEvent(
                event_type=EventType.ERROR,
                source="event_executor",
                data={"action": "create_object", "error": f"Failed to create object '{object_name}'"}
            ))
    
    def _execute_create_template(self, data: Dict[str, Any]) -> None:
        """Execute template creation"""
        if not self.app.is_project_loaded():
            self.logger.warning("Cannot create template - no project loaded")
            return
        
        template_name = data.get('template_name', 'New Template')
        
        success = self.app.create_template(template_name)
        if success:
            self.logger.info(f"Template '{template_name}' created successfully")
            # Emit success event
            event_bus.emit(UIEvent(
                event_type=EventType.SUCCESS,
                source="event_executor",
                data={"action": "create_template", "template_name": template_name}
            ))
        else:
            self.logger.error(f"Failed to create template '{template_name}'")
            # Emit error event
            event_bus.emit(UIEvent(
                event_type=EventType.ERROR,
                source="event_executor",
                data={"action": "create_template", "error": f"Failed to create template '{template_name}'"}
            ))
    
    def _execute_export_assets(self, data: Dict[str, Any]) -> None:
        """Execute asset export"""
        if not self.app.is_project_loaded():
            self.logger.warning("Cannot export assets - no project loaded")
            return
        
        output_path = data.get('output_path', Path('build'))
        if isinstance(output_path, str):
            output_path = Path(output_path)
        
        success = self.app.export_assets(output_path)
        if success:
            self.logger.info(f"Assets exported to {output_path}")
            # Emit success event
            event_bus.emit(UIEvent(
                event_type=EventType.SUCCESS,
                source="event_executor",
                data={"action": "export_assets", "output_path": str(output_path)}
            ))
        else:
            self.logger.error(f"Failed to export assets to {output_path}")
            # Emit error event
            event_bus.emit(UIEvent(
                event_type=EventType.ERROR,
                source="event_executor",
                data={"action": "export_assets", "error": f"Failed to export assets to {output_path}"}
            ))
    
    def _execute_project_dialog_accepted(self, data: Dict[str, Any]) -> None:
        """Execute project creation/opening when dialog is accepted"""
        project_path = data.get('project_path')
        project_info = data.get('project_info')
        
        if not project_path or not project_info:
            self.logger.error("Project dialog accepted but missing project_path or project_info")
            return
        
        # Determine if this is a new project or opening an existing one
        if data.get('is_new_project', True):
            # Create new project
            success = self.app.create_project(Path(project_path), project_info)
            action = "create_project"
        else:
            # Open existing project
            success = self.app.load_project(Path(project_path))
            action = "load_project"
        
        if success:
            self.logger.info(f"Project {action} successful: {project_path}")
            # Emit success event
            event_bus.emit(UIEvent(
                event_type=EventType.SUCCESS,
                source="event_executor",
                data={"action": action, "project_path": str(project_path)}
            ))
        else:
            self.logger.error(f"Project {action} failed: {project_path}")
            # Emit error event
            event_bus.emit(UIEvent(
                event_type=EventType.ERROR,
                source="event_executor",
                data={"action": action, "error": f"Project {action} failed"}
            ))
    
    def _execute_project_dialog_rejected(self, data: Dict[str, Any]) -> None:
        """Handle project dialog rejection"""
        self.logger.info("Project dialog rejected - no action taken")
    
    def execute_file_dialog_result(self, dialog_type: str, file_path: Optional[Path], data: Dict[str, Any] = None) -> None:
        """Execute a file dialog result"""
        if not file_path:
            self.logger.info(f"{dialog_type} dialog cancelled")
            return
        
        if data is None:
            data = {}
        
        if dialog_type == "open_project":
            success = self.app.load_project(file_path)
            action = "load_project"
        elif dialog_type == "import_source":
            success = self.app.import_source(file_path)
            action = "import_source"
        else:
            self.logger.warning(f"Unknown file dialog type: {dialog_type}")
            return
        
        if success:
            self.logger.info(f"{action} successful: {file_path}")
            # Emit success event
            event_bus.emit(UIEvent(
                event_type=EventType.SUCCESS,
                source="event_executor",
                data={"action": action, "file_path": str(file_path)}
            ))
        else:
            self.logger.error(f"{action} failed: {file_path}")
            # Emit error event
            event_bus.emit(UIEvent(
                event_type=EventType.ERROR,
                source="event_executor",
                data={"action": action, "error": f"{action} failed"}
            ))


class EventExecutionLayer:
    """Main event execution layer that coordinates between UI and application"""
    
    def __init__(self, application: ApplicationInterface):
        self.app = application
        self.executor = EventExecutor(application)
        self.logger = logging.getLogger(__name__)
    
    def start(self) -> None:
        """Start the event execution layer"""
        self.logger.info("Event execution layer started")
    
    def stop(self) -> None:
        """Stop the event execution layer"""
        self.logger.info("Event execution layer stopped")
    
    def get_application(self) -> ApplicationInterface:
        """Get the underlying application interface"""
        return self.app
