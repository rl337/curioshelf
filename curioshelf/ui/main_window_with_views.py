"""
Main window with view-based UI instead of modal dialogs
"""

from typing import Optional, Dict, Any
from pathlib import Path

from curioshelf.application_interface import ApplicationInterface
from curioshelf.event_system import event_bus, UIEvent, EventType
from curioshelf.event_execution_layer import EventExecutionLayer
from curioshelf.status_bar_handler import StatusBarEventHandler
from curioshelf.ui.ui_interface import UIImplementationInterface
from curioshelf.ui.abstraction import UIWidget, UILayout, UIMenuBar, UIMenu, UIMenuItem, UIStatusBar
from curioshelf.ui.views.view_container import ViewContainer
from curioshelf.ui.views.sources_list_view import SourcesListView
from curioshelf.ui.views.project_create_view import ProjectCreateView
from curioshelf.ui.views.project_open_view import ProjectOpenView
from curioshelf.ui.views.project_details_view import ProjectDetailsView
from tests.mock_application import MockCurioShelfApplication


class MainWindowWithViews:
    """Main application window using view-based UI instead of modal dialogs"""
    
    def __init__(self, ui_implementation, application: Optional[ApplicationInterface] = None, use_mock: bool = False, verbose: bool = False):
        # Use provided application or create default
        if application:
            self.app = application
        elif use_mock:
            self.app = MockCurioShelfApplication()
        else:
            from curioshelf.application import CurioShelfApplication
            self.app = CurioShelfApplication(ui_implementation)
        
        # Use provided UI implementation
        self.ui = ui_implementation
        
        # UI components
        self.main_widget = None
        self.menu_bar = None
        self.status_bar = None
        self.view_container = None
        
        # Status bar event handler
        self.status_handler = StatusBarEventHandler()
        
        # Event execution layer
        self.event_layer = EventExecutionLayer(self.app)
        self.event_layer.start()
        
        # Register event handlers
        self._register_event_handlers()
        
        # Menu and toolbar actions
        self.actions: Dict[str, Any] = {}
        
        # Setup UI
        self.setup_ui()
    
    def _register_event_handlers(self) -> None:
        """Register event handlers for dialog events"""
        event_bus.subscribe(EventType.SHOW_DIALOG, self._handle_show_dialog)
        event_bus.subscribe(EventType.UI_STATE_CHANGED, self._handle_ui_state_changed)
    
    def _handle_show_dialog(self, event: UIEvent) -> None:
        """Handle show dialog events - now shows views instead of dialogs"""
        print(f"[DEBUG] Received SHOW_DIALOG event: {event.data}")
        dialog_type = event.data.get('dialog_type')
        mode = event.data.get('mode')
        
        print(f"[DEBUG] Dialog type: {dialog_type}, mode: {mode}")
        
        if dialog_type == 'project_dialog':
            print(f"[DEBUG] Showing project view in {mode} mode")
            if mode == 'create':
                self.show_project_create_view()
            elif mode == 'open':
                self.show_project_open_view()
        elif dialog_type == 'file_dialog':
            print(f"[DEBUG] Showing file dialog for {mode}")
            self._show_file_dialog(event.data)
        else:
            print(f"[DEBUG] Unknown dialog type: {dialog_type}")
    
    def _show_file_dialog(self, data: Dict[str, Any]) -> None:
        """Show file dialog based on event data"""
        mode = data.get('mode')
        title = data.get('title', 'Select File')
        file_filter = data.get('filter', 'All Files (*)')
        
        print(f"[DEBUG] Showing file dialog: {title}")
        
        file_dialog = self.ui.create_file_dialog()
        
        # Set default directory based on mode
        if mode == 'import_source':
            # For import source, start from the default project directory
            from curioshelf.config import config
            default_dir = str(config.get_default_project_directory())
            file_path = file_dialog.get_open_file_name(title, file_filter, default_dir)
        else:
            file_path = file_dialog.get_open_file_name(title, file_filter)
        
        if file_path:
            print(f"[DEBUG] File selected: {file_path}")
            # Execute the file dialog result through the existing event execution layer
            self.event_layer.execute_file_dialog_result(mode, Path(file_path))
        else:
            print(f"[DEBUG] File dialog cancelled")
    
    def _handle_ui_state_changed(self, event: UIEvent) -> None:
        """Handle UI state change events"""
        print(f"[DEBUG] Received UI_STATE_CHANGED event: {event.data}")
        
        # Prevent recursive updates
        if hasattr(self, '_updating_menu_state') and self._updating_menu_state:
            print(f"[DEBUG] Already updating menu state, skipping to prevent recursion")
            return
        
        self._updating_menu_state = True
        try:
            self._update_menu_state()
            print(f"[DEBUG] Menu state updated")
        finally:
            self._updating_menu_state = False
    
    def setup_ui(self):
        """Setup the user interface using view system"""
        # Create main widget
        self.main_widget = self.ui.create_main_widget()
        
        # Create view container
        self.view_container = ViewContainer(self.ui)
        
        # Create views
        self._create_views()
        
        # Create menu bar
        self.create_menu_bar()
        
        # Create status bar
        self.create_status_bar()
        
        # Set up the main layout
        self._setup_main_layout()
        
        # Make the main widget visible
        self.main_widget.set_visible(True)
    
    def _create_views(self):
        """Create all views"""
        # Create sources list view
        self.sources_view = SourcesListView(
            self.ui,
            on_import_source=self._on_import_source
        )
        self.view_container.register_view("sources", self.sources_view)
        
        # Create project create view
        self.project_create_view = ProjectCreateView(
            self.ui,
            on_create=self._on_project_created,
            on_cancel=self._on_project_cancel
        )
        self.view_container.register_view("project_create", self.project_create_view)
        
        # Create project open view for initial display (no cancel button)
        self.project_open_view = ProjectOpenView(
            self.ui,
            on_open=self._on_project_opened,
            on_cancel=self._on_project_cancel,
            show_cancel_button=False
        )
        self.view_container.register_view("project_open", self.project_open_view)
        
        # Create project open view for menu/hotkey invocation (with cancel button)
        self.project_open_dialog_view = ProjectOpenView(
            self.ui,
            on_open=self._on_project_opened,
            on_cancel=self._on_project_cancel,
            show_cancel_button=True
        )
        self.view_container.register_view("project_open_dialog", self.project_open_dialog_view)
        
        # Create project details view
        self.project_details_view = ProjectDetailsView(
            self.ui,
            on_close_project=self._on_close_project,
            on_continue_to_sources=self._on_continue_to_sources
        )
        self.view_container.register_view("project_details", self.project_details_view)
        
        # Set the appropriate default view based on project state
        self._set_initial_view()
    
    def _set_initial_view(self):
        """Set the initial view based on whether a project is loaded"""
        if self.app.is_project_loaded():
            # If a project is loaded, show the sources view
            self.view_container.set_default_view(self.sources_view)
            # Refresh the sources view with current project data
            self._refresh_sources_view()
        else:
            # If no project is loaded, show the project open view
            self.view_container.set_default_view(self.project_open_view)
            # Refresh the recent projects list
            self.project_open_view._refresh_projects()
    
    def _setup_main_layout(self):
        """Set up the main layout with menu bar and status bar"""
        # Create main layout
        main_layout = self.ui.create_layout("vertical")
        self.main_widget.set_layout(main_layout)
        
        # Add menu bar at the top
        if self.menu_bar:
            main_layout.add_widget(self.menu_bar)
        
        # Add view container (this will contain all the views)
        main_layout.add_widget(self.view_container.get_widget())
        
        # Add status bar at the bottom
        if self.status_bar:
            main_layout.add_widget(self.status_bar)
    
    def create_menu_bar(self):
        """Create the menu bar"""
        self.menu_bar = self.ui.create_menu_bar()
        
        # Project menu
        project_menu = self.ui.create_menu("Project")
        
        # New Project
        new_project_action = self.ui.create_menu_item("New Project")
        new_project_action.set_text("New Project")
        new_project_action.clicked.connect(self._on_new_project)
        new_project_action.set_enabled_callback(lambda: True)  # Always enabled
        project_menu.add_item(new_project_action)
        self.actions["new_project"] = new_project_action
        
        # Open Project
        open_project_action = self.ui.create_menu_item("Open Project")
        open_project_action.set_text("Open Project")
        open_project_action.clicked.connect(self._on_open_project)
        open_project_action.set_enabled_callback(lambda: True)  # Always enabled
        project_menu.add_item(open_project_action)
        self.actions["open_project"] = open_project_action
        
        # Separator
        project_menu.add_separator()
        
        # Save Project
        save_project_action = self.ui.create_menu_item("Save Project")
        save_project_action.set_text("Save Project")
        save_project_action.clicked.connect(self._on_save_project)
        save_project_action.set_enabled_callback(lambda: self.app.is_project_loaded())
        project_menu.add_item(save_project_action)
        self.actions["save_project"] = save_project_action
        
        # Close Project
        close_project_action = self.ui.create_menu_item("Close Project")
        close_project_action.set_text("Close Project")
        close_project_action.clicked.connect(self._on_close_project)
        close_project_action.set_enabled_callback(lambda: self.app.is_project_loaded())
        project_menu.add_item(close_project_action)
        self.actions["close_project"] = close_project_action
        
        self.menu_bar.add_menu(project_menu)
        
        # Sources menu
        sources_menu = self.ui.create_menu("Sources")
        
        # Import Source
        import_source_action = self.ui.create_menu_item("Import Source")
        import_source_action.set_text("Import Source")
        import_source_action.clicked.connect(self._on_import_source)
        import_source_action.set_enabled_callback(lambda: self.app.is_project_loaded())
        sources_menu.add_item(import_source_action)
        self.actions["import_source"] = import_source_action
        
        self.menu_bar.add_menu(sources_menu)
        
        # Update menu state
        self._update_menu_state()
    
    def create_status_bar(self):
        """Create the status bar"""
        self.status_bar = self.ui.create_status_bar()
        
        # Status label
        self.status_label = self.ui.create_label("Ready")
        self.status_label.set_text("Ready - No project loaded")
        self.status_bar.add_widget(self.status_label)
        
        # Project status label
        self.project_status_label = self.ui.create_label("")
        self.status_bar.add_widget(self.project_status_label)
    
    def _update_menu_state(self):
        """Update the enabled/disabled state of all menu items based on application state"""
        # Update all menu items that have state callbacks
        for action_name, action in self.actions.items():
            if hasattr(action, 'update_all_states'):
                action.update_all_states()
            
            # Explicitly update the enabled state if the callback exists
            if hasattr(action, 'update_state') and action.has_state_callback('enabled'):
                action.update_state('enabled')
    
    def _on_new_project(self):
        """Handle new project menu click"""
        print("New Project menu clicked - showing project create view")
        self.show_project_create_view()
    
    def _on_open_project(self):
        """Handle open project menu click"""
        print("Open Project menu clicked - showing project open view")
        self.show_project_open_view()
    
    def _on_save_project(self):
        """Handle save project menu click"""
        print("Save Project menu clicked")
        if self.app.is_project_loaded():
            success = self.app.save_project()
            if success:
                print("Project saved successfully")
            else:
                print("Failed to save project")
        else:
            print("No project loaded to save")
    
    def _on_close_project(self):
        """Handle close project menu click"""
        print("Close Project menu clicked")
        if self.app.is_project_loaded():
            success = self.app.close_project()
            if success:
                print("Project closed successfully")
                # Update menu state to reflect project unloaded
                self._update_menu_state()
                # Return to project open view
                self.view_container.hide_current_view()
                self.view_container.set_default_view(self.project_open_view)
                self.project_open_view._refresh_projects()
            else:
                print("Failed to close project")
        else:
            print("No project loaded to close")
    
    def _on_import_source(self):
        """Handle import source menu click"""
        print("Import Source menu clicked")
        if self.app.is_project_loaded():
            # Show file dialog for source import
            self._show_file_dialog({
                'mode': 'import_source',
                'title': 'Import Source Image',
                'filter': 'Image Files (*.png *.jpg *.jpeg *.svg *.bmp *.gif);;All Files (*)'
            })
        else:
            print("Cannot import source - no project loaded")
    
    def show_project_create_view(self):
        """Show the project creation view"""
        self.view_container.show_view_by_name("project_create")
        self.project_create_view.reset()
    
    def show_project_open_view(self):
        """Show the project opening view"""
        self.view_container.show_view_by_name("project_open_dialog")
        # Refresh the projects list
        self.project_open_dialog_view._refresh_projects()
    
    def _on_project_created(self, project_name: str, project_path: Path):
        """Handle project creation"""
        print(f"Creating project: {project_name} at {project_path}")
        
        # Create project info
        from curioshelf.projects import ProjectInfo
        project_info = ProjectInfo(
            name=project_name,
            description=f"Project created by user",
            author="User"
        )
        
        # Create the project through the application
        success = self.app.create_project(project_path, project_info)
        
        if success:
            print("Project created successfully")
            
            # Add to recent projects
            try:
                from curioshelf.config import config
                config.add_recent_project(project_path, project_name)
            except Exception as e:
                print(f"Warning: Could not add project to recent projects: {e}")
            
            # Update menu state to reflect project loaded
            self._update_menu_state()
            # Return to sources view
            self.view_container.hide_current_view()
            # Add any existing sources to the sources view
            self._refresh_sources_view()
        else:
            print("Failed to create project")
            # Show error message
            message_box = self.ui.create_message_box()
            message_box.show_error("Error", "Failed to create project. Please check the project path and try again.")
    
    def _on_project_opened(self, project_path: Path):
        """Handle project opening"""
        print(f"Opening project at {project_path}")
        
        # Load the project through the application
        success = self.app.load_project(project_path)
        
        if success:
            print("Project opened successfully")

            # Add to recent projects
            try:
                from curioshelf.config import config
                from curioshelf.projects.structure import ProjectStructureManager
                project_manager = ProjectStructureManager()
                structure = project_manager.load_project(project_path)
                project_name = structure.metadata.name if structure and structure.metadata else project_path.name
                config.add_recent_project(project_path, project_name)
            except Exception as e:
                print(f"Warning: Could not add project to recent projects: {e}")

            # Update menu state to reflect project loaded
            self._update_menu_state()
            
            # Show project details view
            self.view_container.hide_current_view()
            self.project_details_view.load_project(project_path)
            self.view_container.show_view_by_name("project_details")
        else:
            print("Failed to open project")
            # Show error message
            message_box = self.ui.create_message_box()
            message_box.show_error("Error", "Failed to open project. Please check the project path and try again.")
    
    def _on_project_cancel(self):
        """Handle project dialog cancellation"""
        print("Project dialog cancelled - returning to sources view")
        self.view_container.hide_current_view()
    
    def _on_continue_to_sources(self):
        """Handle continue to sources button click"""
        print("Continuing to sources view")
        self.view_container.show_view_by_name("sources")
        self._refresh_sources_view()
    
    def _refresh_sources_view(self):
        """Refresh the sources view with current project sources"""
        if hasattr(self.app, 'get_sources'):
            sources = self.app.get_sources()
            self.sources_view.clear_sources()
            for source in sources:
                self.sources_view.add_source(Path(source))
    
    def get_main_widget(self):
        """Get the main widget for display"""
        return self.main_widget
    
    def cleanup(self):
        """Clean up resources"""
        if self.view_container:
            # View container doesn't need cleanup, but views might
            for view in self.view_container.views.values():
                if hasattr(view, 'cleanup'):
                    view.cleanup()
        if self.event_layer:
            self.event_layer.stop()
        if self.status_handler:
            self.status_handler.cleanup()
