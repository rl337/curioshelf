"""
Project creation view for the main window
"""

from typing import Optional, Callable
from pathlib import Path

from curioshelf.ui.abstraction import UIWidget, UILayout, UIButton, UILabel, UITextInput, UIGroupBox
from curioshelf.ui.views.base_view import BaseView
from curioshelf.config import config


class ProjectCreateView(BaseView):
    """View for creating new projects"""
    
    def __init__(self, ui_implementation, parent: Optional[UIWidget] = None, 
                 on_create: Optional[Callable[[str, Path], None]] = None,
                 on_cancel: Optional[Callable[[], None]] = None):
        self.on_create = on_create
        self.on_cancel = on_cancel
        super().__init__(ui_implementation, parent)
    
    def _setup_ui(self) -> None:
        """Set up the project creation UI"""
        # Create main container
        self.widget = self.ui.create_widget("project_create_view")
        
        # Create main layout
        main_layout = self.ui.create_layout("vertical")
        self.widget.set_layout(main_layout)
        
        # Create title
        title_label = self.ui.create_label("Create New Project")
        title_label.set_text("Create New Project")
        title_label.set_style("font-size: 18px; font-weight: bold; margin-bottom: 20px;")
        main_layout.add_widget(title_label)
        
        # Create form group
        form_group = self.ui.create_group_box("Project Details")
        form_group.set_title("Project Details")
        form_layout = self.ui.create_layout("vertical")
        form_group.set_layout(form_layout)
        
        # Project name input
        name_label = self.ui.create_label("Project Name:")
        name_label.set_text("Project Name:")
        name_label.set_style("font-weight: bold; margin-bottom: 5px;")
        form_layout.add_widget(name_label)
        
        self.name_input = self.ui.create_line_edit()
        self.name_input.set_placeholder("Enter project name")
        self.name_input.set_style("width: 100%; padding: 8px; margin-bottom: 15px; font-size: 14px;")
        self.name_input.text_changed.connect(self._on_name_changed)
        form_layout.add_widget(self.name_input)
        
        # Project path input
        path_label = self.ui.create_label("Project Path:")
        path_label.set_text("Project Path:")
        path_label.set_style("font-weight: bold; margin-bottom: 5px;")
        form_layout.add_widget(path_label)
        
        path_layout = self.ui.create_layout("horizontal")
        
        self.path_input = self.ui.create_line_edit()
        self.path_input.set_placeholder("Select project directory")
        self.path_input.set_style("flex: 1; padding: 8px; margin-right: 10px; font-size: 14px;")
        # Set default project directory
        default_dir = config.get_default_project_directory()
        self.path_input.set_text(str(default_dir))
        path_layout.add_widget(self.path_input)
        
        self.browse_btn = self.ui.create_button("Browse...")
        self.browse_btn.set_style("padding: 8px 16px; font-size: 14px;")
        self.browse_btn.clicked.connect(self._browse_directory)
        path_layout.add_widget(self.browse_btn)
        
        form_layout.add_widget(path_layout)
        main_layout.add_widget(form_group)
        
        # Create button layout
        button_layout = self.ui.create_layout("horizontal")
        button_layout.set_style("justify-content: flex-end; margin-top: 20px; gap: 10px;")
        
        self.cancel_btn = self.ui.create_button("Cancel")
        self.cancel_btn.set_style("padding: 10px 20px; font-size: 14px;")
        self.cancel_btn.clicked.connect(self._on_cancel)
        button_layout.add_widget(self.cancel_btn)
        
        self.create_btn = self.ui.create_button("Create Project")
        self.create_btn.set_style("padding: 10px 20px; font-size: 14px; background-color: #007acc; color: white;")
        self.create_btn.clicked.connect(self._on_create)
        button_layout.add_widget(self.create_btn)
        
        main_layout.add_widget(button_layout)
        
        # Set up auto-completion timer
        self.auto_complete_timer = None
        if hasattr(self.ui, 'create_timer'):
            self.auto_complete_timer = self.ui.create_timer()
            self.auto_complete_timer.set_single_shot(True)
            self.auto_complete_timer.timeout.connect(self._update_project_path)
    
    def get_title(self) -> str:
        """Get the title for this view"""
        return "Create New Project"
    
    def _on_name_changed(self, text: str) -> None:
        """Handle project name text changes for auto-completion"""
        if config.get("auto_complete_project_path", True) and self.auto_complete_timer:
            # Restart the timer to debounce rapid changes
            self.auto_complete_timer.stop()
            self.auto_complete_timer.start(300)  # 300ms delay
    
    def _update_project_path(self) -> None:
        """Update the project path based on the project name"""
        project_name = self.name_input.get_text().strip()
        if project_name:
            suggested_path = config.get_project_path_for_name(project_name)
            self.path_input.set_text(str(suggested_path))
    
    def _browse_directory(self) -> None:
        """Browse for project directory"""
        # Start from the current path or default directory
        current_path = self.path_input.get_text().strip()
        if not current_path:
            current_path = str(config.get_default_project_directory())
        
        # Create file dialog
        file_dialog = self.ui.create_file_dialog()
        directory = file_dialog.get_existing_directory("Select Project Directory", current_path)
        
        if directory:
            self.path_input.set_text(directory)
    
    def _on_create(self) -> None:
        """Handle create project button click"""
        project_name = self.name_input.get_text().strip()
        project_path_str = self.path_input.get_text().strip()
        
        if not project_name:
            # Show error message
            message_box = self.ui.create_message_box()
            message_box.show_error("Error", "Please enter a project name.")
            return
        
        if not project_path_str:
            # Show error message
            message_box = self.ui.create_message_box()
            message_box.show_error("Error", "Please select a project directory.")
            return
        
        try:
            project_path = Path(project_path_str)
            if self.on_create:
                self.on_create(project_name, project_path)
        except Exception as e:
            # Show error message
            message_box = self.ui.create_message_box()
            message_box.show_error("Error", f"Invalid project path: {e}")
    
    def _on_cancel(self) -> None:
        """Handle cancel button click"""
        if self.on_cancel:
            self.on_cancel()
    
    def reset(self) -> None:
        """Reset the form to default values"""
        self.name_input.set_text("")
        default_dir = config.get_default_project_directory()
        self.path_input.set_text(str(default_dir))
