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
        """Set up the project opening UI"""
        # Create main container
        self.widget = self.ui.create_widget("project_open_view")
        
        # Create main layout
        main_layout = self.ui.create_layout("vertical")
        self.widget.set_layout(main_layout)
        
        # Create title
        title_label = self.ui.create_label("Open Existing Project")
        title_label.set_text("Open Existing Project")
        title_label.set_style("font-size: 18px; font-weight: bold; margin-bottom: 20px;")
        main_layout.add_widget(title_label)
        
        # Create recent projects group
        recent_group = self.ui.create_group_box("Recent Projects")
        recent_group.set_title("Recent Projects")
        recent_layout = self.ui.create_layout("vertical")
        recent_group.set_layout(recent_layout)
        
        # Recent projects list
        self.projects_list = self.ui.create_list_widget()
        self.projects_list.set_style("width: 100%; height: 200px; margin-bottom: 15px;")
        self.projects_list.item_selected.connect(self._on_project_selected)
        recent_layout.add_widget(self.projects_list)
        
        # Recent projects buttons
        recent_btn_layout = self.ui.create_layout("horizontal")
        recent_btn_layout.set_style("justify-content: flex-start; gap: 10px;")
        
        self.open_btn = self.ui.create_button("Open Selected Project")
        self.open_btn.set_style("padding: 8px 16px; font-size: 14px;")
        self.open_btn.clicked.connect(self._on_open_selected)
        self.open_btn.set_enabled(False)
        recent_btn_layout.add_widget(self.open_btn)
        
        self.refresh_btn = self.ui.create_button("Refresh")
        self.refresh_btn.set_style("padding: 8px 16px; font-size: 14px;")
        self.refresh_btn.clicked.connect(self._refresh_projects)
        recent_btn_layout.add_widget(self.refresh_btn)
        
        recent_layout.add_widget(recent_btn_layout)
        main_layout.add_widget(recent_group)
        
        # Create browse group
        browse_group = self.ui.create_group_box("Browse for Project")
        browse_group.set_title("Browse for Project")
        browse_layout = self.ui.create_layout("vertical")
        browse_group.set_layout(browse_layout)
        
        browse_label = self.ui.create_label("Or browse for a project directory:")
        browse_label.set_text("Or browse for a project directory:")
        browse_label.set_style("margin-bottom: 10px;")
        browse_layout.add_widget(browse_label)
        
        self.browse_btn = self.ui.create_button("Browse for Project Directory...")
        self.browse_btn.set_style("padding: 10px 20px; font-size: 14px; width: 100%;")
        self.browse_btn.clicked.connect(self._browse_for_project)
        browse_layout.add_widget(self.browse_btn)
        
        main_layout.add_widget(browse_group)
        
        # Create button layout
        button_layout = self.ui.create_layout("horizontal")
        button_layout.set_style("justify-content: flex-end; margin-top: 20px; gap: 10px;")
        
        self.cancel_btn = self.ui.create_button("Cancel")
        self.cancel_btn.set_style("padding: 10px 20px; font-size: 14px;")
        self.cancel_btn.clicked.connect(self._on_cancel)
        button_layout.add_widget(self.cancel_btn)
        
        main_layout.add_widget(button_layout)
        
        # Load recent projects
        self._refresh_projects()
    
    def get_title(self) -> str:
        """Get the title for this view"""
        return "Open Existing Project"
    
    def _refresh_projects(self) -> None:
        """Refresh the list of recent projects"""
        self.projects_list.clear()
        
        # Get recent projects (for now, we'll scan the default directory)
        default_dir = config.get_default_project_directory()
        recent_projects = self._scan_for_projects(default_dir)
        
        if not recent_projects:
            # Add placeholder item
            placeholder = self.projects_list.create_item("No recent projects found")
            placeholder.set_data("", "")
            self.projects_list.add_item(placeholder)
        else:
            for project_path, project_name in recent_projects:
                item = self.projects_list.create_item(f"{project_name} ({project_path})")
                item.set_data(str(project_path), project_name)
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
        if not project_path_str:
            return
        
        try:
            project_path = Path(project_path_str)
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
            project_path = Path(project_path)
            # Check if this directory contains a curioshelf.json file
            config_file = project_path / "curioshelf.json"
            if not config_file.exists():
                # Show error message
                message_box = self.ui.create_message_box()
                message_box.show_error("Error", "Selected directory does not contain a CurioShelf project (curioshelf.json not found).")
                return
            
            try:
                # Load the project
                structure = self.project_manager.load_project(project_path)
                if structure is None:
                    # Show error message
                    message_box = self.ui.create_message_box()
                    message_box.show_error("Error", "Failed to load project structure.")
                    return
                
                # Open the project
                if self.on_open:
                    self.on_open(project_path)
                
            except Exception as e:
                # Show error message
                message_box = self.ui.create_message_box()
                message_box.show_error("Error", f"Failed to open project: {e}")
    
    def _on_cancel(self) -> None:
        """Handle cancel button click"""
        if self.on_cancel:
            self.on_cancel()
