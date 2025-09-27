"""
Abstracted project dialog for creating and opening projects

This version uses the UI abstraction layer instead of direct PySide6 imports.

DEPRECATED: This module is deprecated and should not be used in new code.
Use the view system (ProjectCreateView/ProjectOpenView) instead.
"""

from typing import Optional, Callable
from pathlib import Path
import time

from curioshelf.projects import ProjectManager, ProjectInfo
from curioshelf.config import config
from .abstraction import UIWidget


class ProjectDialogAbstracted(UIWidget):
    """Project dialog using UI abstraction layer - DEPRECATED: Use view system instead"""
    
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
        
        # Auto-completion timer (simple implementation using time)
        self.auto_complete_timer = None
        self.auto_complete_timer_start = None
        
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
        # Connect text change callback for auto-completion
        self.project_name_input.set_text_changed_callback(self._on_project_name_changed)
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
                from curioshelf.ui.abstraction import UIListItem
                project_item = UIListItem(display_text)
                project_item.set_data(str(project_dir))
                self.existing_projects_list.add_item(project_item)
            except:
                # If we can't load project info, just show the directory name
                fallback_item = UIListItem(project_dir.name)
                fallback_item.set_data(str(project_dir))
                self.existing_projects_list.add_item(fallback_item)
    
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
    
    def _on_project_name_changed(self, text: str) -> None:
        """Handle project name text changes for auto-completion"""
        if config.get("auto_complete_project_path", True):
            # Simple timer implementation using time
            self.auto_complete_timer_start = time.time()
            # Schedule update after 300ms delay
            self._schedule_project_path_update()
    
    def _schedule_project_path_update(self) -> None:
        """Schedule project path update with debouncing"""
        if self.auto_complete_timer_start is None:
            return
        
        # Check if enough time has passed since last change
        if time.time() - self.auto_complete_timer_start >= 0.3:  # 300ms delay
            self._update_project_path()
        else:
            # Schedule another check
            import threading
            def delayed_check():
                time.sleep(0.1)  # Check every 100ms
                self._schedule_project_path_update()
            threading.Thread(target=delayed_check, daemon=True).start()
    
    def _update_project_path(self) -> None:
        """Update the project path based on the project name"""
        project_name = self.project_name_input.get_text().strip()
        if project_name:
            suggested_path = config.get_project_path_for_name(project_name)
            self.project_path_input.set_text(str(suggested_path))
    
    def cancel(self):
        """Cancel the dialog"""
        self.close()
    
    def close(self):
        """Close the dialog"""
        # In a real implementation, this would close the dialog window
        pass
    
    def exec(self):
        """Execute the dialog - DEPRECATED: Use view system instead"""
        # This method is deprecated and should not be used in the new UI system
        # The new UI system uses views instead of modal dialogs
        raise DeprecationWarning(
            "ProjectDialogAbstracted.exec() is deprecated. "
            "Use the view system (ProjectCreateView/ProjectOpenView) instead."
        )
    
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
