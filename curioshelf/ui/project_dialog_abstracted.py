"""
Abstracted project dialog for creating and opening projects

This version uses the UI abstraction layer instead of direct PySide6 imports.
"""

from typing import Optional, Callable
from pathlib import Path

from curioshelf.projects import ProjectManager, ProjectInfo
from .abstraction import UIWidget


class ProjectDialogAbstracted(UIWidget):
    """Project dialog using UI abstraction layer"""
    
    def __init__(self, ui_factory):
        super().__init__()
        self.ui_factory = ui_factory
        self.project_manager = ProjectManager()
        
        # UI components
        self.dialog = None
        self.project_name_input = None
        self.project_path_input = None
        self.browse_btn = None
        self.create_btn = None
        self.open_btn = None
        self.cancel_btn = None
        self.existing_projects_list = None
        
        # Callbacks
        self.project_created: Optional[Callable[[Path, ProjectInfo], None]] = None
        self.project_loaded: Optional[Callable[[Path], None]] = None
        
        # Dialog mode (create or open)
        self.mode = "create"
        
        self.setup_ui()
        self.refresh()
    
    def set_mode(self, mode: str) -> None:
        """Set the dialog mode (create or open)"""
        self.mode = mode
        self._update_ui_for_mode()
    
    def _update_ui_for_mode(self) -> None:
        """Update UI elements based on the current mode"""
        if self.mode == "open":
            # Hide create project section, show open project section
            if hasattr(self, 'new_project_group'):
                self.new_project_group.set_visible(False)
            if hasattr(self, 'existing_projects_group'):
                self.existing_projects_group.set_visible(True)
        else:
            # Show create project section, hide open project section
            if hasattr(self, 'new_project_group'):
                self.new_project_group.set_visible(True)
            if hasattr(self, 'existing_projects_group'):
                self.existing_projects_group.set_visible(False)
    
    def setup_ui(self):
        """Setup the UI using abstraction layer"""
        # Create dialog
        self.dialog = self.ui_factory.create_widget()
        
        # Create main layout
        main_layout = self.ui_factory.create_layout("vertical")
        self.dialog.set_layout(main_layout)
        
        # Create new project section
        self.new_project_group = self.ui_factory.create_group_box("Create New Project")
        new_project_layout = self.ui_factory.create_layout("vertical")
        self.new_project_group.set_layout(new_project_layout)
        
        # Project name
        name_layout = self.ui_factory.create_layout("horizontal")
        name_layout.add_widget(self.ui_factory.create_text_input("Project Name:"))
        self.project_name_input = self.ui_factory.create_text_input("Enter project name...")
        name_layout.add_widget(self.project_name_input)
        new_project_layout.add_widget(name_layout)
        
        # Project path
        path_layout = self.ui_factory.create_layout("horizontal")
        path_layout.add_widget(self.ui_factory.create_text_input("Project Path:"))
        self.project_path_input = self.ui_factory.create_text_input("Select project directory...")
        path_layout.add_widget(self.project_path_input)
        
        self.browse_btn = self.ui_factory.create_button("Browse...")
        self.browse_btn.set_clicked_callback(self.browse_project_path)
        path_layout.add_widget(self.browse_btn)
        new_project_layout.add_widget(path_layout)
        
        # Create button
        self.create_btn = self.ui_factory.create_button("Create Project")
        self.create_btn.set_clicked_callback(self.create_project)
        new_project_layout.add_widget(self.create_btn)
        
        main_layout.add_widget(self.new_project_group)
        
        # Create open project section
        self.existing_projects_group = self.ui_factory.create_group_box("Open Existing Project")
        open_project_layout = self.ui_factory.create_layout("vertical")
        self.existing_projects_group.set_layout(open_project_layout)
        
        # Existing projects list
        self.existing_projects_list = self.ui_factory.create_list_widget()
        self.existing_projects_list.set_current_changed_callback(self.on_project_selected)
        open_project_layout.add_widget(self.existing_projects_list)
        
        # Open button
        self.open_btn = self.ui_factory.create_button("Open Project")
        self.open_btn.set_clicked_callback(self.open_project)
        self.open_btn.set_enabled(False)
        open_project_layout.add_widget(self.open_btn)
        
        main_layout.add_widget(self.existing_projects_group)
        
        # Create button row
        button_layout = self.ui_factory.create_layout("horizontal")
        self.cancel_btn = self.ui_factory.create_button("Cancel")
        self.cancel_btn.set_clicked_callback(self.cancel)
        button_layout.add_widget(self.cancel_btn)
        main_layout.add_widget(button_layout)
    
    def get_widget(self) -> UIWidget:
        """Get the main widget"""
        return self.dialog
    
    def refresh(self):
        """Refresh the dialog with current data"""
        self.refresh_existing_projects()
    
    def refresh_existing_projects(self):
        """Refresh the list of existing projects"""
        if not self.existing_projects_list:
            return
        
        self.existing_projects_list.clear()
        
        # Look for existing projects in common locations
        project_dirs = []
        
        # Check current directory
        current_dir = Path.cwd()
        for item in current_dir.iterdir():
            if item.is_dir() and (item / "project.json").exists():
                project_dirs.append(item)
        
        # Check parent directory
        parent_dir = current_dir.parent
        for item in parent_dir.iterdir():
            if item.is_dir() and (item / "project.json").exists():
                project_dirs.append(item)
        
        # Add projects to list
        for project_dir in project_dirs:
            try:
                project_info = self.project_manager.load_project_info(project_dir)
                display_text = f"{project_info.name} ({project_dir.name})"
                self.existing_projects_list.add_item(display_text, str(project_dir))
            except:
                # If we can't load project info, just show the directory name
                self.existing_projects_list.add_item(project_dir.name, str(project_dir))
    
    def on_project_selected(self, project_path: str):
        """Handle project selection"""
        if project_path:
            self.open_btn.set_enabled(True)
        else:
            self.open_btn.set_enabled(False)
    
    def browse_project_path(self):
        """Browse for project directory"""
        file_dialog = self.ui_factory.create_file_dialog()
        directory = file_dialog.get_existing_directory("Select Project Directory")
        
        if directory:
            self.project_path_input.set_text(directory)
    
    def create_project(self):
        """Create a new project"""
        project_name = self.project_name_input.text.strip()
        project_path = self.project_path_input.text.strip()
        
        if not project_name:
            msg_box = self.ui_factory.create_message_box()
            msg_box.show_warning("Error", "Please enter a project name")
            return
        
        if not project_path:
            msg_box = self.ui_factory.create_message_box()
            msg_box.show_warning("Error", "Please select a project directory")
            return
        
        try:
            project_dir = Path(project_path) / project_name
            project_info = self.project_manager.create_project(project_dir, project_name)
            
            if project_info:
                # Emit signal
                self.emit_signal("project_created", (project_dir, project_info))
                
                # Close dialog
                self.close()
            else:
                msg_box = self.ui_factory.create_message_box()
                msg_box.show_error("Error", "Failed to create project")
        
        except Exception as e:
            msg_box = self.ui_factory.create_message_box()
            msg_box.show_error("Error", f"Failed to create project: {str(e)}")
    
    def open_project(self):
        """Open an existing project"""
        project_path = self.existing_projects_list.current_data()
        
        if not project_path:
            msg_box = self.ui_factory.create_message_box()
            msg_box.show_warning("Error", "Please select a project to open")
            return
        
        try:
            project_dir = Path(project_path)
            
            # Emit signal
            self.emit_signal("project_loaded", project_dir)
            
            # Close dialog
            self.close()
        
        except Exception as e:
            msg_box = self.ui_factory.create_message_box()
            msg_box.show_error("Error", f"Failed to open project: {str(e)}")
    
    def cancel(self):
        """Cancel the dialog"""
        self.close()
    
    def close(self):
        """Close the dialog"""
        # In a real implementation, this would close the dialog window
        pass
    
    def exec(self):
        """Execute the dialog"""
        # Import here to avoid circular imports
        from .qtimpl.project_dialog import QtProjectDialog
        from PySide6.QtWidgets import QDialog
        from .dialog_auto_responder import get_auto_responder
        
        # Create and show the Qt dialog
        dialog = QtProjectDialog(mode=self.mode)
        
        # Connect signals
        dialog.project_created.connect(self._on_project_created)
        dialog.project_loaded.connect(self._on_project_loaded)
        
        # Setup auto-responder for scripted testing (only if test plugins are loaded)
        try:
            from test_support.test_plugin_loader import get_dialog_responder
            auto_responder = get_dialog_responder()
            if auto_responder and auto_responder.enabled:
                print(f"[PROJECT DIALOG] Auto-responder enabled, will auto-respond to dialog")
                # Use a timer to allow the dialog to be shown first
                from PySide6.QtCore import QTimer
                QTimer.singleShot(100, lambda: self._delayed_auto_respond(dialog, auto_responder))
        except ImportError:
            # Test plugins not available, run normally
            pass
        
        # Show the dialog
        result = dialog.exec()
        
        # If dialog was accepted, the signals will have been emitted
        # If dialog was rejected, emit a rejected event
        if result != QDialog.Accepted:
            from curioshelf.event_system import event_bus, UIEvent, EventType
            event = UIEvent(
                event_type=EventType.DIALOG_REJECTED,
                source="project_dialog",
                data={
                    "dialog_type": "project_dialog",
                    "mode": self.mode
                }
            )
            event_bus.emit(event)
    
    def _delayed_auto_respond(self, dialog, auto_responder):
        """Delayed auto-respond to allow dialog to be shown first"""
        try:
            auto_responder.auto_respond_to_dialog(dialog, "project_dialog", self.mode)
            print(f"[PROJECT DIALOG] Auto-responder completed successfully")
        except Exception as e:
            print(f"[PROJECT DIALOG] Auto-responder failed: {e}")
            # Close the dialog and re-raise the error
            dialog.reject()
            raise
    
    def _on_project_created(self, project_path: Path, project_info: ProjectInfo):
        """Handle project created signal"""
        from curioshelf.event_system import event_bus, UIEvent, EventType
        event = UIEvent(
            event_type=EventType.DIALOG_ACCEPTED,
            source="project_dialog",
            data={
                "dialog_type": "project_dialog",
                "mode": "create",
                "project_path": str(project_path),
                "project_info": project_info
            }
        )
        event_bus.emit(event)
    
    def _on_project_loaded(self, project_path: Path):
        """Handle project loaded signal"""
        from curioshelf.event_system import event_bus, UIEvent, EventType
        event = UIEvent(
            event_type=EventType.DIALOG_ACCEPTED,
            source="project_dialog",
            data={
                "dialog_type": "project_dialog",
                "mode": "open",
                "project_path": str(project_path)
            }
        )
        event_bus.emit(event)
    
    def connect_signal(self, signal_name: str, callback: Callable):
        """Connect a signal callback"""
        if signal_name == "project_created":
            self.project_created = callback
        elif signal_name == "project_loaded":
            self.project_loaded = callback
