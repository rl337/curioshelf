"""
Project opening view for the main window
"""

from typing import Optional, Callable, List
from pathlib import Path

from curioshelf.ui.abstraction import UIWidget, UILayout, UIButton, UILabel, UITextInput, UIGroupBox, UIListWidget
from curioshelf.ui.views.base_view import BaseView
from curioshelf.config import config
from curioshelf.projects.structure import ProjectStructureManager, ProjectMetadata


class ProjectOpenView(BaseView):
    """View for opening existing projects"""
    
    def __init__(self, ui_implementation, parent: Optional[UIWidget] = None,
                 on_open: Optional[Callable[[Path], None]] = None,
                 on_cancel: Optional[Callable[[], None]] = None):
        self.on_open = on_open
        self.on_cancel = on_cancel
        self.project_manager = ProjectStructureManager()
        super().__init__(ui_implementation, parent)
    
    def _setup_ui(self) -> None:
        """Set up the project opening UI using the same layout approach as project create view"""
        # Create main container
        self.widget = self.ui.create_widget("project_open_view")
        
        # Create directional layout (same as project create view)
        from curioshelf.ui.layouts.directional_layout import DirectionalLayout, Direction
        main_layout = DirectionalLayout(self.widget)
        self.widget.set_layout(main_layout)
        
        # Create title at the top
        title_label = self.ui.create_label("Open Existing Project")
        title_label.set_text("Open Existing Project")
        title_label.set_style("font-size: 18px; font-weight: bold; margin: 20px;")
        main_layout.add_widget(title_label, Direction.NORTH)
        
        # Create a stack widget for the main content (same as project create view)
        content_stack = self.ui.create_stack_widget(spacing=15)
        main_layout.add_widget(content_stack.widget, Direction.CENTER, expand=True)
        
        # Recent projects section
        recent_label = content_stack.add_label("Recent Projects:", style="font-weight: bold; margin-bottom: 5px;")
        
        # Recent projects list
        self.projects_list = self.ui.create_list_widget()
        self.projects_list.set_style("min-height: 200px; padding: 5px;")
        self.projects_list.item_selected.connect(self._on_project_selected)
        content_stack.add_widget(self.projects_list)
        
        # Recent projects buttons using row widget
        recent_btn_row = self.ui.create_row_widget(spacing=10)
        content_stack.add_widget(recent_btn_row.widget)
        
        self.open_btn = recent_btn_row.add_button("Open Selected Project", self._on_open_selected, "padding: 8px 16px;")
        self.open_btn.set_enabled(False)
        
        self.refresh_btn = recent_btn_row.add_button("Refresh", self._refresh_projects, "padding: 8px 16px;")
        
        # Browse section
        browse_label = content_stack.add_label("Or browse for a project directory:", style="font-weight: bold; margin-bottom: 5px;")
        
        # Project path input using row widget
        path_row = self.ui.create_row_widget(spacing=10)
        content_stack.add_widget(path_row.widget)
        
        path_label = path_row.add_label("Project Path:", style="padding: 5px;")
        
        self.project_path_input = path_row.add_text_input("Enter project directory path or click Browse...", expand=True, style="padding: 8px;")
        self.project_path_input.set_placeholder("Enter project directory path or click Browse...")
        
        self.browse_btn = path_row.add_button("Browse...", self._browse_for_project, "padding: 8px 16px;")
        
        # Open from path button
        self.open_from_path_btn = content_stack.add_button("Open from Path", self._open_from_path, "padding: 10px 20px; margin: 5px;")
        
        # Create button row at the bottom (same as project create view)
        button_row = self.ui.create_button_row_widget(spacing=10)
        main_layout.add_widget(button_row.widget, Direction.SOUTH)
        
        self.cancel_btn = button_row.add_secondary_button("Cancel", self._on_cancel)
        
        # Load recent projects
        self._refresh_projects()
    
    def get_title(self) -> str:
        """Get the title for this view"""
        return "Open Existing Project"
    
    def _refresh_projects(self) -> None:
        """Refresh the list of recent projects"""
        self.projects_list.clear()
        
        # Get recent projects from config
        recent_projects = config.get_recent_projects()
        
        if not recent_projects:
            # Add placeholder item
            placeholder = self.projects_list.create_item("No recent projects found")
            placeholder.set_data("", "")
            self.projects_list.add_item(placeholder)
        else:
            for project_info in recent_projects:
                project_path = project_info.get("path", "")
                project_name = project_info.get("name", Path(project_path).name)
                item = self.projects_list.create_item(f"{project_name} ({project_path})")
                item.set_data(project_path, project_name)
                self.projects_list.add_item(item)
    
    def _scan_for_projects(self, directory: Path) -> List[tuple]:
        """Scan directory for CurioShelf projects"""
        projects = []
        
        if not directory.exists():
            return projects
        
        try:
            for item in directory.iterdir():
                if item.is_dir():
                    config_file = item / "curioshelf.json"
                    if config_file.exists():
                        # Try to get project name from config
                        try:
                            project_name = item.name  # Default to directory name
                            projects.append((item, project_name))
                        except Exception:
                            # If we can't read the config, use directory name
                            projects.append((item, item.name))
        except Exception as e:
            print(f"Error scanning for projects: {e}")
        
        return projects
    
    def _on_project_selected(self, item) -> None:
        """Handle project selection in the list"""
        if item and item.get_data("path"):
            self.open_btn.set_enabled(True)
        else:
            self.open_btn.set_enabled(False)
    
    def _on_open_selected(self) -> None:
        """Handle open selected project button click"""
        selected_item = self.projects_list.get_selected_item()
        if not selected_item:
            return
        
        project_path_str = selected_item.get_data("path")
        project_name = selected_item.get_data("name")
        if not project_path_str:
            return
        
        try:
            project_path = Path(project_path_str)
            
            # Add to recent projects (this will move it to the top)
            if project_name:
                config.add_recent_project(project_path, project_name)
            
            if self.on_open:
                self.on_open(project_path)
        except Exception as e:
            # Show error message
            message_box = self.ui.create_message_box()
            message_box.show_error("Error", f"Invalid project path: {e}")
    
    def _browse_for_project(self) -> None:
        """Browse for an existing project directory"""
        # Start from the default project directory
        default_dir = str(config.get_default_project_directory())
        
        # Create file dialog
        file_dialog = self.ui.create_file_dialog()
        project_path = file_dialog.get_existing_directory("Open Project Directory", default_dir)
        
        if project_path:
            # Update the text input field
            self.project_path_input.set_text(project_path)
            # Automatically open the project after browsing
            self._open_from_path()
    
    def _open_from_path(self) -> None:
        """Open project from the path in the text input field"""
        project_path_str = self.project_path_input.get_text().strip()
        if not project_path_str:
            message_box = self.ui.create_message_box()
            message_box.show_error("Error", "Please enter a project path.")
            return
        
        try:
            project_path = Path(project_path_str)
            if not project_path.exists():
                message_box = self.ui.create_message_box()
                message_box.show_error("Error", "The specified path does not exist.")
                return
            
            # Check if this directory contains a curioshelf.json file
            config_file = project_path / "curioshelf.json"
            if not config_file.exists():
                message_box = self.ui.create_message_box()
                message_box.show_error("Error", "Selected directory does not contain a CurioShelf project (curioshelf.json not found).")
                return
            
            # Load the project
            structure = self.project_manager.load_project(project_path)
            if structure is None:
                message_box = self.ui.create_message_box()
                message_box.show_error("Error", "Failed to load project structure.")
                return
            
            # Add to recent projects
            project_name = structure.metadata.name if structure.metadata else project_path.name
            config.add_recent_project(project_path, project_name)
            
            # Open the project
            if self.on_open:
                self.on_open(project_path)
            
        except Exception as e:
            message_box = self.ui.create_message_box()
            message_box.show_error("Error", f"Failed to open project: {e}")
    
    def _on_cancel(self) -> None:
        """Handle cancel button click"""
        if self.on_cancel:
            self.on_cancel()
