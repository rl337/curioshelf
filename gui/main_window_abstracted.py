"""
Abstracted main window for CurioShelf

This version uses the UI abstraction layer instead of direct PySide6 imports.
It can work with any UI implementation (Qt, headless, web, etc.).
"""

from typing import Optional, Dict, Any
from pathlib import Path

from curioshelf.models import AssetManager
from curioshelf.project_manager import ProjectManager, ProjectInfo
from curioshelf.ui_state_manager import UIStateManager
from gui.project_dialog_abstracted import ProjectDialogAbstracted


class MainWindowAbstracted:
    """Main application window using UI abstraction layer"""
    
    def __init__(self, ui_implementation, verbose: bool = False):
        # Initialize managers
        self.project_manager = ProjectManager()
        self.ui_state_manager = UIStateManager()
        self.asset_manager: Optional[AssetManager] = None
        
        # Use provided UI implementation
        self.ui = ui_implementation
        
        # UI components (will be created by setup_ui)
        self.main_widget = None
        self.tab_widget = None
        self.sources_tab = None
        self.templates_tab = None
        self.objects_tab = None
        self.status_label = None
        self.progress_label = None
        self.project_status_label = None
        
        # Menu and toolbar actions
        self.actions: Dict[str, Any] = {}
        
        # Setup UI
        self.setup_ui()
        self.setup_ui_state_management()
        
        # Don't show project dialog immediately - let the user choose
        # self.show_project_dialog()
    
    def setup_ui(self):
        """Setup the user interface using abstraction layer"""
        # Create main widget
        self.main_widget = self.ui.create_widget()
        
        # Create main layout
        main_layout = self.ui.create_layout("vertical")
        self.main_widget.set_layout(main_layout)
        
        # Create menu bar
        self.create_menu_bar()
        
        # Create toolbar
        self.create_toolbar()
        
        # Create tab widget
        self.tab_widget = self.ui.create_tab_widget()
        main_layout.add_widget(self.tab_widget)
        
        # Create tabs (will be initialized when project is loaded)
        self.sources_tab = None
        self.templates_tab = None
        self.objects_tab = None
        
        # Add placeholder tabs with some content
        placeholder1 = self.ui.create_widget()
        placeholder1_label = self.ui.create_text_input()
        placeholder1_label.set_text("Sources tab - Load a project to see sources")
        placeholder1_label.set_enabled(False)  # Make it read-only
        
        placeholder2 = self.ui.create_widget()
        placeholder2_label = self.ui.create_text_input()
        placeholder2_label.set_text("Templates tab - Load a project to see templates")
        placeholder2_label.set_enabled(False)  # Make it read-only
        
        placeholder3 = self.ui.create_widget()
        placeholder3_label = self.ui.create_text_input()
        placeholder3_label.set_text("Objects tab - Load a project to see objects")
        placeholder3_label.set_enabled(False)  # Make it read-only
        
        # Create layouts for placeholder tabs
        placeholder1_layout = self.ui.create_layout("vertical")
        placeholder1.set_layout(placeholder1_layout)
        placeholder1_layout.add_widget(placeholder1_label)
        
        placeholder2_layout = self.ui.create_layout("vertical")
        placeholder2.set_layout(placeholder2_layout)
        placeholder2_layout.add_widget(placeholder2_label)
        
        placeholder3_layout = self.ui.create_layout("vertical")
        placeholder3.set_layout(placeholder3_layout)
        placeholder3_layout.add_widget(placeholder3_label)
        
        self.tab_widget.add_tab(placeholder1, "Sources")
        self.tab_widget.add_tab(placeholder2, "Templates")
        self.tab_widget.add_tab(placeholder3, "Objects")
        
        # Create status bar
        self.create_status_bar()
        
        # Add status bar to main layout
        status_layout = self.ui.create_layout("horizontal")
        status_layout.add_widget(self.status_label)
        status_layout.add_widget(self.progress_label)
        status_layout.add_widget(self.project_status_label)
        main_layout.add_widget(status_layout)
        
        # Set up refresh timer
        self.setup_refresh_timer()
        
        # Ensure all widgets are visible
        self.show_all_widgets()
    
    def show_all_widgets(self):
        """Show all widgets in the main window"""
        # Show main widget
        if hasattr(self.main_widget, 'show'):
            self.main_widget.show()
        
        # Show tab widget
        if hasattr(self.tab_widget, 'show'):
            self.tab_widget.show()
        
        # Show status bar widgets
        if self.status_label and hasattr(self.status_label, 'show'):
            self.status_label.show()
        if self.progress_label and hasattr(self.progress_label, 'show'):
            self.progress_label.show()
        if self.project_status_label and hasattr(self.project_status_label, 'show'):
            self.project_status_label.show()
    
    def create_menu_bar(self):
        """Create the menu bar using abstraction layer"""
        # Note: In a real implementation, this would create actual menu widgets
        # For now, we'll store menu actions for state management
        self.actions = {
            "new_project": self.ui.create_button("New Project"),
            "open_project": self.ui.create_button("Open Project"),
            "save_project": self.ui.create_button("Save Project"),
            "close_project": self.ui.create_button("Close Project"),
            "import_source": self.ui.create_button("Import Source"),
            "export_assets": self.ui.create_button("Export Assets"),
            "create_object": self.ui.create_button("Create Object"),
            "create_template": self.ui.create_button("Create Template"),
        }
        
        # Connect actions
        self.actions["new_project"].set_clicked_callback(self.new_project)
        self.actions["open_project"].set_clicked_callback(self.open_project)
        self.actions["save_project"].set_clicked_callback(self.save_project)
        self.actions["close_project"].set_clicked_callback(self.close_project)
        self.actions["import_source"].set_clicked_callback(self.import_source)
        self.actions["export_assets"].set_clicked_callback(self.export_assets)
        self.actions["create_object"].set_clicked_callback(self.create_object)
        self.actions["create_template"].set_clicked_callback(self.create_template)
    
    def create_toolbar(self):
        """Create the toolbar using abstraction layer"""
        # Toolbar actions are the same as menu actions
        # In a real implementation, this would create a toolbar widget
        pass
    
    def create_status_bar(self):
        """Create the status bar using abstraction layer"""
        # Create status labels
        self.status_label = self.ui.create_text_input()
        self.status_label.set_text("Ready")
        
        self.progress_label = self.ui.create_text_input()
        self.progress_label.set_text("No project loaded")
        
        self.project_status_label = self.ui.create_text_input()
        self.project_status_label.set_text("No Project")
    
    def setup_refresh_timer(self):
        """Setup refresh timer for status updates"""
        # In a real implementation, this would use the UI framework's timer
        # For now, we'll just set a flag
        self._refresh_enabled = True
    
    def setup_ui_state_management(self):
        """Setup UI state management"""
        # Connect state manager signals
        self.ui_state_manager.connect_signal("project_state_changed", self.on_project_state_changed)
        self.ui_state_manager.connect_signal("source_state_changed", self.on_source_state_changed)
        self.ui_state_manager.connect_signal("object_state_changed", self.on_object_state_changed)
        self.ui_state_manager.connect_signal("template_state_changed", self.on_template_state_changed)
        
        # Register UI elements for state management
        self.register_ui_elements()
    
    def register_ui_elements(self):
        """Register UI elements with the state manager"""
        # Register menu actions
        self.ui_state_manager.register_element(
            "save_project", self.actions["save_project"], ["project_required"]
        )
        self.ui_state_manager.register_element(
            "close_project", self.actions["close_project"], ["project_required"]
        )
        self.ui_state_manager.register_element(
            "import_source", self.actions["import_source"], ["project_required"]
        )
        self.ui_state_manager.register_element(
            "create_object", self.actions["create_object"], ["project_required"]
        )
        self.ui_state_manager.register_element(
            "create_template", self.actions["create_template"], ["project_required"]
        )
        self.ui_state_manager.register_element(
            "export_assets", self.actions["export_assets"], ["project_required"]
        )
        
        # Always enabled actions
        self.ui_state_manager.register_element(
            "new_project", self.actions["new_project"], ["always_enabled"]
        )
        self.ui_state_manager.register_element(
            "open_project", self.actions["open_project"], ["always_enabled"]
        )
    
    def show_project_dialog(self):
        """Show the project management dialog"""
        dialog = ProjectDialogAbstracted(self.ui)
        dialog.connect_signal("project_created", self.on_project_created)
        dialog.connect_signal("project_loaded", self.on_project_loaded)
        dialog.exec()
    
    def on_project_created(self, project_path: Path, project_info: ProjectInfo):
        """Handle project creation"""
        self.load_project(project_path)
    
    def on_project_loaded(self, project_path: Path):
        """Handle project loading"""
        self.load_project(project_path)
    
    def load_project(self, project_path: Path):
        """Load a project"""
        if self.project_manager.load_project(project_path):
            self.asset_manager = self.project_manager.asset_manager
            self.initialize_tabs()
            self.update_ui_states()
            self.update_project_status()
            self.status_label.set_text(f"Project loaded: {project_path.name}")
        else:
            self.show_error("Failed to load project")
    
    def initialize_tabs(self):
        """Initialize tabs with the loaded project's asset manager"""
        if not self.asset_manager:
            return
        
        # Remove existing tabs
        # Note: In a real implementation, this would remove tabs from the tab widget
        
        # Create new tabs using abstraction layer
        from gui.sources_tab_abstracted import SourcesTabAbstracted
        from gui.templates_tab_abstracted import TemplatesTabAbstracted
        from gui.objects_tab_abstracted import ObjectsTabAbstracted
        
        self.sources_tab = SourcesTabAbstracted(self.asset_manager, self.ui)
        self.templates_tab = TemplatesTabAbstracted(self.asset_manager, self.ui)
        self.objects_tab = ObjectsTabAbstracted(self.asset_manager, self.ui)
        
        # Add tabs to widget
        self.tab_widget.add_tab(self.sources_tab.get_widget(), "Sources")
        self.tab_widget.add_tab(self.templates_tab.get_widget(), "Templates")
        self.tab_widget.add_tab(self.objects_tab.get_widget(), "Objects")
        
        # Connect signals
        self.sources_tab.source_loaded.connect(self.on_source_loaded)
        self.objects_tab.slice_created.connect(self.on_slice_created)
        self.objects_tab.object_created.connect(self.on_object_created)
        self.objects_tab.object_updated.connect(self.on_object_updated)
        self.objects_tab.object_deleted.connect(self.on_object_deleted)
        
        # Load default templates if none exist
        if not self.asset_manager.templates:
            self.load_default_templates()
    
    def load_default_templates(self):
        """Load default templates"""
        try:
            # Load example templates
            self.asset_manager.load_templates("metadata/example_templates.json")
        except:
            # Create some basic templates if file doesn't exist
            self.asset_manager.add_template(
                "character",
                "Basic character template",
                ["front", "back", "left", "right", "walk1", "walk2", "idle"]
            )
            
            self.asset_manager.add_template(
                "tile",
                "Basic tile template",
                ["base", "variant1", "variant2"]
            )
            
            self.asset_manager.add_template(
                "ui_element",
                "UI element template",
                ["normal", "hover", "pressed", "disabled"]
            )
        
        # Refresh templates tab
        if self.templates_tab:
            self.templates_tab.refresh()
    
    def update_ui_states(self):
        """Update UI element states based on current project state"""
        if not self.asset_manager:
            self.ui_state_manager.update_all_states(False, False, False, False)
            return
        
        has_sources = len(self.asset_manager.sources) > 0
        has_objects = len(self.asset_manager.objects) > 0
        has_templates = len(self.asset_manager.templates) > 0
        
        self.ui_state_manager.update_all_states(True, has_sources, has_objects, has_templates)
    
    def update_project_status(self):
        """Update the project status display"""
        status = self.project_manager.get_project_status()
        if status["loaded"]:
            self.project_status_label.set_text(f"Project: {status['name']}")
        else:
            self.project_status_label.set_text("No Project")
    
    def refresh_status(self):
        """Refresh the status bar with current statistics"""
        if not self.asset_manager:
            self.progress_label.set_text("No project loaded")
            return
        
        source_count = len(self.asset_manager.sources)
        template_count = len(self.asset_manager.templates)
        object_count = len(self.asset_manager.objects)
        
        # Count total slices
        total_slices = sum(len(source.slices) for source in self.asset_manager.sources.values())
        
        status_text = f"Sources: {source_count} | Templates: {template_count} | Objects: {object_count} | Slices: {total_slices}"
        self.progress_label.set_text(status_text)
    
    # Project management methods
    def new_project(self):
        """Create a new project"""
        self.show_project_dialog()
    
    def open_project(self):
        """Open an existing project"""
        self.show_project_dialog()
    
    def save_project(self):
        """Save the current project"""
        if self.project_manager.save_project():
            self.status_label.set_text("Project saved")
        else:
            self.show_error("Failed to save project")
    
    def close_project(self):
        """Close the current project"""
        if self.project_manager.close_project():
            self.asset_manager = None
            self.initialize_tabs()
            self.update_ui_states()
            self.update_project_status()
            self.status_label.set_text("Project closed")
        else:
            self.show_error("Failed to close project")
    
    def import_source(self):
        """Import a new source image"""
        if not self.asset_manager:
            self.show_warning("Please create or load a project first")
            return
        
        file_dialog = self.ui.create_file_dialog()
        file_path = file_dialog.get_open_file_name(
            "Import Source Image",
            "Image Files (*.png *.jpg *.jpeg *.svg *.bmp *.gif);;All Files (*)"
        )
        
        if file_path:
            try:
                # Load image to get dimensions
                pixmap = self.ui.create_pixmap(800, 600)  # Mock pixmap
                
                # Add source file to project
                project_relative_path = self.project_manager.add_source_file(Path(file_path))
                if not project_relative_path:
                    self.show_error("Failed to add source file to project")
                    return
                
                # Add to asset manager
                source = self.asset_manager.add_source(
                    project_relative_path, pixmap.width, pixmap.height
                )
                
                # Switch to sources tab and load the source
                self.tab_widget.set_current_index(0)
                self.sources_tab.load_source(source, str(project_relative_path))
                
                # Update UI states
                self.update_ui_states()
                
                self.status_label.set_text(f"Imported: {source.file_path.name}")
                
            except Exception as e:
                self.show_error(f"Failed to load source: {str(e)}")
    
    def create_object(self):
        """Create a new object"""
        if not self.asset_manager:
            self.show_warning("Please create or load a project first")
            return
        
        # Switch to objects tab and trigger creation
        self.tab_widget.set_current_index(2)
        self.objects_tab.create_object()
        self.update_ui_states()
    
    def create_template(self):
        """Create a new template"""
        if not self.asset_manager:
            self.show_warning("Please create or load a project first")
            return
        
        # Switch to templates tab and trigger creation
        self.tab_widget.set_current_index(1)
        self.templates_tab.create_template()
        self.update_ui_states()
    
    def export_assets(self):
        """Export assets to build directory"""
        if not self.asset_manager:
            self.show_warning("Please create or load a project first")
            return
        
        try:
            # Use project's build directory
            if self.project_manager.current_project_path:
                build_dir = self.project_manager.current_project_path / "build"
            else:
                build_dir = Path("build")
            
            build_dir.mkdir(exist_ok=True)
            
            # Export metadata
            metadata_file = build_dir / "metadata.json"
            self.asset_manager.save_metadata(str(metadata_file))
            
            self.show_info(f"Assets exported to {build_dir}")
            self.status_label.set_text(f"Exported to {build_dir}")
            
        except Exception as e:
            self.show_error(f"Failed to export assets: {str(e)}")
    
    # Signal handlers
    def on_project_state_changed(self, has_project: bool):
        """Handle project state changes"""
        self.update_project_status()
    
    def on_source_state_changed(self, has_sources: bool):
        """Handle source state changes"""
        pass
    
    def on_object_state_changed(self, has_objects: bool):
        """Handle object state changes"""
        pass
    
    def on_template_state_changed(self, has_templates: bool):
        """Handle template state changes"""
        pass
    
    def on_source_loaded(self, source):
        """Handle source loaded signal"""
        self.status_label.set_text(f"Source loaded: {source.file_path.name}")
    
    def on_slice_created(self, slice_obj):
        """Handle slice created signal"""
        self.status_label.set_text(f"Slice created: {slice_obj.name}")
    
    def on_object_created(self, obj):
        """Handle object created signal"""
        self.status_label.set_text(f"Object created: {obj.name}")
    
    def on_object_updated(self, obj):
        """Handle object updated signal"""
        self.status_label.set_text(f"Object updated: {obj.name}")
    
    def on_object_deleted(self, object_id):
        """Handle object deleted signal"""
        self.status_label.set_text("Object deleted")
    
    # Utility methods
    def show_info(self, message: str):
        """Show info message - log to console and update status"""
        print(f"[INFO] {message}")
        if self.status_label:
            self.status_label.set_text(f"Info: {message}")
    
    def show_warning(self, message: str):
        """Show warning message - log to console and update status"""
        print(f"[WARNING] {message}")
        if self.status_label:
            self.status_label.set_text(f"Warning: {message}")
    
    def show_error(self, message: str):
        """Show error message - log to console and update status"""
        print(f"[ERROR] {message}")
        if self.status_label:
            self.status_label.set_text(f"Error: {message}")
    
    def run(self):
        """Run the application"""
        return self.ui.run_event_loop()
    
    def cleanup(self):
        """Cleanup the application"""
        if self.project_manager.is_project_loaded:
            self.project_manager.save_project()
        self.ui.cleanup()
