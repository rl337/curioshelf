"""
Project creation view for the main window
"""

from typing import Optional, Callable
from pathlib import Path

from curioshelf.ui.abstraction import UIWidget, UILayout, UIButton, UILabel, UITextInput, UIGroupBox
from curioshelf.ui.layouts.directional_layout import DirectionalLayout, Direction
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
        """Set up the project creation UI using simple directional layout"""
        # Create main container
        self.widget = self.ui.create_widget("project_create_view")
        
        # Create directional layout
        main_layout = DirectionalLayout(self.widget)
        self.widget.set_layout(main_layout)
        
        # Create title at the top
        title_label = self.ui.create_label("Create New Project")
        title_label.set_text("Create New Project")
        title_label.set_style("font-size: 18px; font-weight: bold; margin: 20px;")
        main_layout.add_widget(title_label, Direction.NORTH)
        
        # Create a simple form using a stack widget
        form_stack = self.ui.create_stack_widget(spacing=15)
        main_layout.add_widget(form_stack.widget, Direction.CENTER, expand=True)
        
        # Add project name field
        name_label = form_stack.add_label("Project Name:", style="font-weight: bold; margin-bottom: 5px;")
        self.name_input = form_stack.add_text_input("Enter project name", style="padding: 8px; font-size: 14px;")
        self.name_input.text_changed.connect(self._on_name_changed)
        
        # Add project path field
        path_label = form_stack.add_label("Project Path:", style="font-weight: bold; margin-bottom: 5px;")
        
        # Create a row for path input and browse button
        path_row = self.ui.create_row_widget(spacing=10)
        form_stack.add_widget(path_row.widget)
        
        self.path_input = path_row.add_text_input("Select project directory", expand=True, style="padding: 8px; font-size: 14px;")
        # Set default project directory
        default_dir = config.get_default_project_directory()
        self.path_input.set_text(str(default_dir))
        
        self.browse_btn = path_row.add_button("Browse...", self._browse_directory, style="padding: 8px 16px; font-size: 14px;")
        
        # Create button row at the bottom
        button_row = self.ui.create_button_row_widget(spacing=10)
        main_layout.add_widget(button_row.widget, Direction.SOUTH)
        
        self.cancel_btn = button_row.add_secondary_button("Cancel", self._on_cancel)
        self.create_btn = button_row.add_primary_button("Create Project", self._on_create)
        
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
