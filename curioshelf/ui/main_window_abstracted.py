"""
Abstracted main window for CurioShelf

This version uses the UI abstraction layer instead of direct PySide6 imports.
It can work with any UI implementation (Qt, headless, web, etc.).
"""

from typing import Optional, Dict, Any
from pathlib import Path

from curioshelf.application_interface import ApplicationInterface
from curioshelf.application import CurioShelfApplication
from curioshelf.mock_application import MockCurioShelfApplication
from curioshelf.app_impl.application_impl import CurioShelfApplicationImpl
from curioshelf.projects import ProjectInfo
from curioshelf.event_system import (
    event_bus, UIEvent, EventType, NewProjectCommand, OpenProjectCommand,
    SaveProjectCommand, CloseProjectCommand, ImportSourceCommand,
    CreateObjectCommand, CreateTemplateCommand
)
from curioshelf.event_execution_layer import EventExecutionLayer
from curioshelf.status_bar_handler import StatusBarEventHandler
from .project_dialog_abstracted import ProjectDialogAbstracted


class MainWindowAbstracted:
    """Main application window using UI abstraction layer"""
    
    def __init__(self, ui_implementation, application: Optional[ApplicationInterface] = None, use_mock: bool = False, verbose: bool = False):
        # Use provided application or create default
        if application:
            self.app = application
        elif use_mock:
            self.app = MockCurioShelfApplication()
        else:
            self.app = CurioShelfApplication(ui_implementation)
        
        # Use provided UI implementation
        self.ui = ui_implementation
        
        # UI components (will be created by setup_ui)
        self.main_widget = None
        self.tab_widget = None
        self.sources_tab = None
        self.templates_tab = None
        self.objects_tab = None
        self.menu_bar = None
        self.status_bar = None
        
        # Legacy attributes for backward compatibility with tests
        self.status_label = None
        self.progress_label = None
        self.project_status_label = None
        
        # Status bar event handler
        self.status_handler = StatusBarEventHandler()
        
        # Event execution layer
        self.event_layer = EventExecutionLayer(self.app)
        self.event_layer.start()
        
        # Menu and toolbar actions
        self.actions: Dict[str, Any] = {}
        
        # Setup UI
        self.setup_ui()
        # Don't show project dialog immediately - let the user choose
        # self.show_project_dialog()
    
    def setup_ui(self):
        """Setup the user interface using abstraction layer"""
        # Create main widget
        self.main_widget = self.ui.create_main_widget()
        
        # Create menu bar
        self.create_menu_bar()
        
        # Create status bar
        self.create_status_bar()
        
        # Set menu bar and status bar on main widget
        if hasattr(self.main_widget, 'set_menu_bar'):
            self.main_widget.set_menu_bar(self.menu_bar)
        if hasattr(self.main_widget, 'set_status_bar'):
            self.main_widget.set_status_bar(self.status_bar)
        
        # Create main layout
        main_layout = self.ui.create_layout("vertical", parent=self.main_widget)
        self.main_widget.set_layout(main_layout)
        
        # Create tab widget
        self.tab_widget = self.ui.create_tab_widget(parent=self.main_widget)
        main_layout.add_widget(self.tab_widget)
        
        # Create tabs (will be initialized when project is loaded)
        self.sources_tab = None
        self.templates_tab = None
        self.objects_tab = None
        
        # Add placeholder tabs with some content
        placeholder1 = self.ui.create_widget(parent=self.main_widget)
        placeholder1_label = self.ui.create_text_input(parent=placeholder1)
        placeholder1_label.set_text("Sources tab - Load a project to see sources")
        placeholder1_label.set_enabled(False)  # Make it read-only
        
        placeholder2 = self.ui.create_widget(parent=self.main_widget)
        placeholder2_label = self.ui.create_text_input(parent=placeholder2)
        placeholder2_label.set_text("Templates tab - Load a project to see templates")
        placeholder2_label.set_enabled(False)  # Make it read-only
        
        placeholder3 = self.ui.create_widget(parent=self.main_widget)
        placeholder3_label = self.ui.create_text_input(parent=placeholder3)
        placeholder3_label.set_text("Objects tab - Load a project to see objects")
        placeholder3_label.set_enabled(False)  # Make it read-only
        
        # Create layouts for placeholder tabs
        placeholder1_layout = self.ui.create_layout("vertical", parent=placeholder1)
        placeholder1.set_layout(placeholder1_layout)
        placeholder1_layout.add_widget(placeholder1_label)
        
        placeholder2_layout = self.ui.create_layout("vertical", parent=placeholder2)
        placeholder2.set_layout(placeholder2_layout)
        placeholder2_layout.add_widget(placeholder2_label)
        
        placeholder3_layout = self.ui.create_layout("vertical", parent=placeholder3)
        placeholder3.set_layout(placeholder3_layout)
        placeholder3_layout.add_widget(placeholder3_label)
        
        self.tab_widget.add_tab(placeholder1, "Sources")
        self.tab_widget.add_tab(placeholder2, "Templates")
        self.tab_widget.add_tab(placeholder3, "Objects")
        
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
        
        # Show menu bar
        if self.menu_bar and hasattr(self.menu_bar, 'show'):
            self.menu_bar.show()
        
        # Show status bar
        if self.status_bar and hasattr(self.status_bar, 'show'):
            self.status_bar.show()
    
    def create_menu_bar(self):
        """Create the menu bar using abstraction layer"""
        # Create menu bar
        self.menu_bar = self.ui.create_menu_bar(parent=self.main_widget)
        
        # Create Project menu
        project_menu = self.ui.create_menu("Project", parent=self.menu_bar)
        
        # Create menu items
        new_project_item = self.ui.create_menu_item("New Project", parent=project_menu)
        new_project_item.set_clicked_callback(lambda: self._handle_menu_click("New Project", NewProjectCommand()))
        project_menu.add_item(new_project_item)
        
        open_project_item = self.ui.create_menu_item("Open Project", parent=project_menu)
        open_project_item.set_clicked_callback(lambda: self._handle_menu_click("Open Project", OpenProjectCommand()))
        project_menu.add_item(open_project_item)
        
        save_project_item = self.ui.create_menu_item("Save Project", parent=project_menu)
        save_project_item.set_clicked_callback(lambda: self._handle_menu_click("Save Project", SaveProjectCommand()))
        project_menu.add_item(save_project_item)
        
        close_project_item = self.ui.create_menu_item("Close Project", parent=project_menu)
        close_project_item.set_clicked_callback(lambda: self._handle_menu_click("Close Project", CloseProjectCommand()))
        project_menu.add_item(close_project_item)
        
        # Add Project menu to menu bar
        self.menu_bar.add_menu(project_menu)
        
        # Create Sources menu
        sources_menu = self.ui.create_menu("Sources", parent=self.menu_bar)
        
        import_source_item = self.ui.create_menu_item("Import Source", parent=sources_menu)
        import_source_item.set_clicked_callback(lambda: self._handle_menu_click("Import Source", ImportSourceCommand()))
        sources_menu.add_item(import_source_item)
        
        export_assets_item = self.ui.create_menu_item("Export Assets", parent=sources_menu)
        export_assets_item.set_clicked_callback(lambda: self._handle_menu_click("Export Assets", self.export_assets))
        sources_menu.add_item(export_assets_item)
        
        # Add Sources menu to menu bar
        self.menu_bar.add_menu(sources_menu)
        
        # Create Objects menu
        objects_menu = self.ui.create_menu("Objects", parent=self.menu_bar)
        
        create_object_item = self.ui.create_menu_item("Create Object", parent=objects_menu)
        create_object_item.set_clicked_callback(lambda: self._handle_menu_click("Create Object", CreateObjectCommand()))
        objects_menu.add_item(create_object_item)
        
        # Add Objects menu to menu bar
        self.menu_bar.add_menu(objects_menu)
        
        # Create Templates menu
        templates_menu = self.ui.create_menu("Templates", parent=self.menu_bar)
        
        create_template_item = self.ui.create_menu_item("Create Template", parent=templates_menu)
        create_template_item.set_clicked_callback(lambda: self._handle_menu_click("Create Template", CreateTemplateCommand()))
        templates_menu.add_item(create_template_item)
        
        # Add Templates menu to menu bar
        self.menu_bar.add_menu(templates_menu)
        
        # Store menu items for state management
        self.actions = {
            "new_project": new_project_item,
            "open_project": open_project_item,
            "save_project": save_project_item,
            "close_project": close_project_item,
            "import_source": import_source_item,
            "export_assets": export_assets_item,
            "create_object": create_object_item,
            "create_template": create_template_item,
        }
        
        # Set initial menu state (no project loaded)
        self._update_menu_state()
    
    def _handle_menu_click(self, menu_name: str, command) -> None:
        """Handle menu item click by emitting events to the event execution layer"""
        try:
            # Map menu names to command strings
            command_map = {
                "New Project": "new_project",
                "Open Project": "open_project", 
                "Save Project": "save_project",
                "Close Project": "close_project",
                "Import Source": "import_source",
                "Create Object": "create_object",
                "Create Template": "create_template",
                "Export Assets": "export_assets"
            }
            
            command_string = command_map.get(menu_name)
            if command_string:
                # Emit menu click event
                event = UIEvent(
                    event_type=EventType.MENU_ITEM_CLICKED,
                    source="main_window",
                    data={
                        "menu_item": command_string,
                        "menu_name": menu_name
                    }
                )
                event_bus.emit(event)
            else:
                print(f"Unknown menu action: {menu_name}")
            
        except Exception as e:
            print(f"Menu action '{menu_name}' failed: {e}")
    
    def _update_menu_state(self) -> None:
        """Update menu item enabled/disabled state based on application state"""
        # Update application state first
        self.app.update_ui_state()
        
        # Get UI state from application
        ui_state = self.app.get_ui_state()
        
        # Update menu items based on application state
        for action_name, enabled in ui_state.items():
            if action_name in self.actions:
                self.actions[action_name].set_enabled(enabled)
    
    def create_toolbar(self):
        """Create the toolbar using abstraction layer"""
        # Toolbar actions are the same as menu actions
        # In a real implementation, this would create a toolbar widget
        pass
    
    def create_status_bar(self):
        """Create the status bar using abstraction layer"""
        # Create status bar
        self.status_bar = self.ui.create_status_bar(parent=self.main_widget)
        self.status_bar.set_message("Ready - No project loaded")
        
        # Connect status bar to event handler
        self.status_handler.set_status_bar(self.status_bar)
    
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
        if self.app.load_project(project_path):
            self.initialize_tabs()
            self.update_ui_states()
            self.update_project_status()
            if self.status_bar:
                self.status_bar.set_message(f"Project loaded: {project_path.name}")
        else:
            self.show_error("Failed to load project")
    
    def initialize_tabs(self):
        """Initialize tabs with the loaded project's asset manager"""
        if not self.app.is_project_loaded():
            return
        
        # Remove existing tabs
        # Note: In a real implementation, this would remove tabs from the tab widget
        
        # Create new tabs using abstraction layer
        from .sources_tab_abstracted import SourcesTabAbstracted
        from .templates_tab_abstracted import TemplatesTabAbstracted
        from .objects_tab_abstracted import ObjectsTabAbstracted
        
        # Create tabs with application layer
        self.sources_tab = SourcesTabAbstracted(self.app, self.ui)
        self.templates_tab = TemplatesTabAbstracted(self.app, self.ui)
        self.objects_tab = ObjectsTabAbstracted(self.app, self.ui)
        
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
        if not self.app.has_templates():
            self.load_default_templates()
    
    def load_default_templates(self):
        """Load default templates"""
        try:
            # Try to load example templates from file
            # For now, just create basic templates using application layer
            self.app.create_template(
                "character",
                "Basic character template",
                ["front", "back", "left", "right", "walk1", "walk2", "idle"]
            )
            
            self.app.create_template(
                "tile",
                "Basic tile template",
                ["base", "variant1", "variant2"]
            )
            
            self.app.create_template(
                "ui_element",
                "UI element template",
                ["normal", "hover", "pressed", "disabled"]
            )
        except Exception as e:
            print(f"Warning: Could not load default templates: {e}")
        
        # Refresh templates tab
        if self.templates_tab:
            self.templates_tab.refresh()
    
    def update_ui_states(self):
        """Update UI element states based on current project state"""
        self.app.update_ui_state()
        self._update_menu_state()
    
    def update_project_status(self):
        """Update the project status display"""
        status = self.app.get_project_status()
        if status["loaded"]:
            emit_project_status(status['name'], "project_manager")
        else:
            emit_project_status(None, "project_manager")
    
    def refresh_status(self):
        """Refresh the status bar with current statistics"""
        if not self.app.is_project_loaded():
            emit_project_status(None, "asset_manager")
            return
        
        asset_counts = self.app.get_asset_counts()
        source_count = asset_counts.get('sources', 0)
        template_count = asset_counts.get('templates', 0)
        object_count = asset_counts.get('objects', 0)
        
        # Count total slices
        sources = self.app.get_sources()
        total_slices = sum(len(source.slices) for source in sources)
        
        emit_asset_status(source_count, template_count, object_count, total_slices, "asset_manager")
    
    # Project management methods
    def new_project(self):
        """Create a new project"""
        self.show_project_dialog()
    
    def open_project(self):
        """Open an existing project"""
        self.show_project_dialog()
    
    def save_project(self):
        """Save the current project"""
        if self.app.save_project():
            self.app.update_ui_state()
        else:
            self.show_error("Failed to save project")
    
    def close_project(self):
        """Close the current project"""
        if self.app.close_project():
            self.app.update_ui_state()
        else:
            self.show_error("Failed to close project")
    
    def import_source(self):
        """Import a new source image"""
        if not self.app.is_project_loaded():
            self.show_warning("Please create or load a project first")
            return
        
        file_dialog = self.ui.create_file_dialog()
        file_path = file_dialog.get_open_file_name(
            "Import Source Image",
            "Image Files (*.png *.jpg *.jpeg *.svg *.bmp *.gif);;All Files (*)"
        )
        
        if file_path:
            try:
                # Use application layer to import source
                success = self.app.import_source(Path(file_path))
                if success:
                    self.show_info(f"Imported: {Path(file_path).name}")
                    if self.status_bar:
                        self.status_bar.set_message(f"Imported: {Path(file_path).name}")
                else:
                    self.show_error("Failed to import source")
                
                # Switch to sources tab
                if self.tab_widget:
                    self.tab_widget.set_current_index(0)
                
                # Update UI states
                self.update_ui_states()
                
            except Exception as e:
                self.show_error(f"Failed to load source: {str(e)}")
    
    def create_object(self):
        """Create a new object"""
        if not self.app.is_project_loaded():
            self.show_warning("Please create or load a project first")
            return
        
        # Use the application layer to create object
        self.app.create_object("New Object")
        self.update_ui_states()
    
    def create_template(self):
        """Create a new template"""
        if not self.app.is_project_loaded():
            self.show_warning("Please create or load a project first")
            return
        
        # Use the application layer to create template
        self.app.create_template("New Template")
        self.update_ui_states()
    
    def export_assets(self):
        """Export assets to build directory"""
        if not self.app.is_project_loaded():
            self.show_warning("Please create or load a project first")
            return
        
        try:
            # Use project's build directory
            project_info = self.app.get_project_info()
            if project_info and hasattr(project_info, 'path'):
                build_dir = project_info.path / "build"
            else:
                build_dir = Path("build")
            
            build_dir.mkdir(exist_ok=True)
            
            # Use application layer to export
            self.app.export_assets(build_dir)
            
            self.show_info(f"Assets exported to {build_dir}")
            if self.status_bar:
                self.status_bar.set_message(f"Exported to {build_dir}")
            
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
        if self.app.is_project_loaded():
            self.app.save_project()
        self.ui.cleanup()
