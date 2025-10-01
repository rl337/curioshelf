"""
Project details view for displaying project information
"""

from typing import Optional, Callable
from pathlib import Path

from curioshelf.ui.abstraction import UIWidget
from curioshelf.ui.views.base_view import BaseView
from curioshelf.projects.structure import ProjectStructureManager, ProjectMetadata


class ProjectDetailsView(BaseView):
    """View for displaying project details and information"""
    
    def __init__(self, ui_implementation, parent: Optional[UIWidget] = None,
                 on_close_project: Optional[Callable[[], None]] = None,
                 on_continue_to_sources: Optional[Callable[[], None]] = None):
        self.on_close_project = on_close_project
        self.on_continue_to_sources = on_continue_to_sources
        self.project_manager = ProjectStructureManager()
        self.current_project_path = None
        super().__init__(ui_implementation, parent)
    
    def _setup_ui(self) -> None:
        """Set up the project details UI using the same layout approach as other views"""
        # Create main container
        self.widget = self.ui.create_widget("project_details_view")
        
        # Create directional layout (same as other views)
        from curioshelf.ui.layouts.directional_layout import DirectionalLayout, Direction
        main_layout = DirectionalLayout(self.widget)
        self.widget.set_layout(main_layout)
        
        # Create content stack
        content_stack = self.ui.create_stack_widget()
        main_layout.add_widget(content_stack.widget, Direction.CENTER)
        
        # Title
        title_label = content_stack.add_label("Project Details", style="font-size: 24px; font-weight: bold; margin: 20px;")
        
        # Project info section
        info_group = self.ui.create_group_box("Project Information")
        info_group.set_title("Project Information")
        content_stack.add_widget(info_group)
        
        # Project name
        self.name_label = content_stack.add_label("Name: Loading...", style="font-size: 16px; margin: 10px;")
        
        # Project path
        self.path_label = content_stack.add_label("Path: Loading...", style="font-size: 14px; margin: 10px; color: #666;")
        
        # Project description
        self.description_label = content_stack.add_label("Description: Loading...", style="font-size: 14px; margin: 10px;")
        
        # Project stats
        stats_group = self.ui.create_group_box("Project Statistics")
        stats_group.set_title("Project Statistics")
        content_stack.add_widget(stats_group)
        
        self.sources_count_label = content_stack.add_label("Sources: Loading...", style="font-size: 14px; margin: 10px;")
        self.objects_count_label = content_stack.add_label("Objects: Loading...", style="font-size: 14px; margin: 10px;")
        self.templates_count_label = content_stack.add_label("Templates: Loading...", style="font-size: 14px; margin: 10px;")
        
        # Action buttons
        action_group = self.ui.create_group_box("Actions")
        action_group.set_title("Actions")
        content_stack.add_widget(action_group)
        
        # Button row
        button_row = self.ui.create_button_row_widget(spacing=15)
        content_stack.add_widget(button_row)
        
        # Continue to sources button
        self.continue_btn = button_row.add_primary_button("Continue to Sources", self._on_continue_to_sources)
        
        # Close project button
        self.close_btn = button_row.add_secondary_button("Close Project", self._on_close_project)
    
    def get_title(self) -> str:
        """Get the title for this view"""
        return "Project Details"
    
    def load_project(self, project_path: Path) -> bool:
        """Load project details from the given path"""
        try:
            self.current_project_path = project_path
            
            # Load project structure
            structure = self.project_manager.load_project(project_path)
            if not structure or not structure.metadata:
                self._show_error("Failed to load project metadata")
                return False
            
            metadata = structure.metadata
            
            # Update project information
            self.name_label.set_text(f"Name: {metadata.name}")
            self.path_label.set_text(f"Path: {project_path}")
            self.description_label.set_text(f"Description: {metadata.description or 'No description available'}")
            
            # Update project statistics
            sources_count = len(structure.sources) if structure.sources else 0
            objects_count = len(structure.objects) if structure.objects else 0
            templates_count = len(structure.templates) if structure.templates else 0
            
            self.sources_count_label.set_text(f"Sources: {sources_count}")
            self.objects_count_label.set_text(f"Objects: {objects_count}")
            self.templates_count_label.set_text(f"Templates: {templates_count}")
            
            return True
            
        except Exception as e:
            print(f"Error loading project details: {e}")
            self._show_error(f"Error loading project: {str(e)}")
            return False
    
    def _show_error(self, message: str) -> None:
        """Show an error message"""
        self.name_label.set_text(f"Error: {message}")
        self.path_label.set_text("")
        self.description_label.set_text("")
        self.sources_count_label.set_text("")
        self.objects_count_label.set_text("")
        self.templates_count_label.set_text("")
    
    def _on_continue_to_sources(self) -> None:
        """Handle continue to sources button click"""
        if self.on_continue_to_sources:
            self.on_continue_to_sources()
    
    def _on_close_project(self) -> None:
        """Handle close project button click"""
        if self.on_close_project:
            self.on_close_project()
