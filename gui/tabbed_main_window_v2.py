"""
Main application window with V2 tabbed interface

This version uses the new V2 architecture with simplified sources tab
and enhanced objects tab that includes slice creation.
Now includes project management and UI state management.
"""

from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
    QTabWidget, QMenuBar, QMenu, QStatusBar, QLabel,
    QFileDialog, QMessageBox, QToolBar, QSplitter
)
from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QPixmap, QAction
from pathlib import Path

from gui.sources_tab_v2 import SourcesTabV2
from gui.templates_tab import TemplatesTab
from gui.objects_tab_v2 import ObjectsTabV2
from gui.project_dialog import ProjectDialog
from curioshelf.models import AssetManager
from curioshelf.project_manager import ProjectManager, ProjectInfo
from curioshelf.ui_state_manager import UIStateManager


class TabbedMainWindowV2(QMainWindow):
    """Main application window with V2 tabbed interface"""
    
    def __init__(self):
        super().__init__()
        # Initialize managers
        self.project_manager = ProjectManager()
        self.ui_state_manager = UIStateManager()
        self.asset_manager = None  # Will be set when project is loaded
        
        self.init_ui()
        self.setup_ui_state_management()
        
        # Show project dialog on startup
        self.show_project_dialog()
    
    def init_ui(self):
        """Initialize the user interface"""
        self.setWindowTitle("CurioShelf V2 - Visual Asset Manager")
        self.setGeometry(100, 100, 1400, 900)
        
        # Create central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Create main layout
        layout = QVBoxLayout(central_widget)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # Create tab widget
        self.tab_widget = QTabWidget()
        layout.addWidget(self.tab_widget)
        
        # Create tabs (will be initialized when project is loaded)
        self.sources_tab = None
        self.templates_tab = None
        self.objects_tab = None
        
        # Add placeholder tabs (will be replaced when project is loaded)
        self.tab_widget.addTab(QLabel("No Project Loaded"), "Sources")
        self.tab_widget.addTab(QLabel("No Project Loaded"), "Templates")
        self.tab_widget.addTab(QLabel("No Project Loaded"), "Objects")
        
        # Create menu bar
        self.create_menu_bar()
        
        # Create toolbar
        self.create_toolbar()
        
        # Create status bar
        self.create_status_bar()
        
        # Register UI elements now that menu and toolbar are created
        self.register_ui_elements()
        
        # Set up refresh timer
        self.refresh_timer = QTimer()
        self.refresh_timer.timeout.connect(self.refresh_status)
        self.refresh_timer.start(1000)  # Refresh every second
    
    def setup_ui_state_management(self):
        """Setup UI state management"""
        # Connect state manager signals
        self.ui_state_manager.connect_signal("project_state_changed", self.on_project_state_changed)
        self.ui_state_manager.connect_signal("source_state_changed", self.on_source_state_changed)
        self.ui_state_manager.connect_signal("object_state_changed", self.on_object_state_changed)
        self.ui_state_manager.connect_signal("template_state_changed", self.on_template_state_changed)
        
        # UI elements will be registered after menu and toolbar creation
    
    def register_ui_elements(self):
        """Register UI elements with the state manager"""
        # Register menu actions
        self.ui_state_manager.register_element(
            "save_project", self.save_project_action, ["project_required"]
        )
        self.ui_state_manager.register_element(
            "close_project", self.close_project_action, ["project_required"]
        )
        self.ui_state_manager.register_element(
            "import_source", self.import_source_action, ["project_required"]
        )
        self.ui_state_manager.register_element(
            "create_object", self.create_object_action, ["project_required"]
        )
        self.ui_state_manager.register_element(
            "create_template", self.create_template_action, ["project_required"]
        )
        self.ui_state_manager.register_element(
            "export_assets", self.export_action, ["project_required"]
        )
        
        # Always enabled actions
        self.ui_state_manager.register_element(
            "new_project", self.new_project_action, ["always_enabled"]
        )
        self.ui_state_manager.register_element(
            "open_project", self.open_project_action, ["always_enabled"]
        )
    
    def create_menu_bar(self):
        """Create the menu bar"""
        menubar = self.menuBar()
        
        # File menu
        file_menu = menubar.addMenu("File")
        
        # Project actions
        self.new_project_action = QAction("New Project", self)
        self.new_project_action.setShortcut("Ctrl+N")
        self.new_project_action.triggered.connect(self.new_project)
        file_menu.addAction(self.new_project_action)
        
        self.open_project_action = QAction("Open Project", self)
        self.open_project_action.setShortcut("Ctrl+O")
        self.open_project_action.triggered.connect(self.open_project)
        file_menu.addAction(self.open_project_action)
        
        self.save_project_action = QAction("Save Project", self)
        self.save_project_action.setShortcut("Ctrl+S")
        self.save_project_action.triggered.connect(self.save_project)
        file_menu.addAction(self.save_project_action)
        
        self.close_project_action = QAction("Close Project", self)
        self.close_project_action.triggered.connect(self.close_project)
        file_menu.addAction(self.close_project_action)
        
        file_menu.addSeparator()
        
        # Import source action
        self.import_source_action = QAction("Import Source", self)
        self.import_source_action.setShortcut("Ctrl+I")
        self.import_source_action.triggered.connect(self.import_source)
        file_menu.addAction(self.import_source_action)
        
        file_menu.addSeparator()
        
        # Export action
        self.export_action = QAction("Export Assets", self)
        self.export_action.setShortcut("Ctrl+E")
        self.export_action.triggered.connect(self.export_assets)
        file_menu.addAction(self.export_action)
        
        file_menu.addSeparator()
        
        # Exit action
        exit_action = QAction("Exit", self)
        exit_action.setShortcut("Ctrl+Q")
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)
        
        # Edit menu
        edit_menu = menubar.addMenu("Edit")
        
        # Create object action
        self.create_object_action = QAction("Create Object", self)
        self.create_object_action.setShortcut("Ctrl+Shift+N")
        self.create_object_action.triggered.connect(self.create_object)
        edit_menu.addAction(self.create_object_action)
        
        # Create template action
        self.create_template_action = QAction("Create Template", self)
        self.create_template_action.setShortcut("Ctrl+T")
        self.create_template_action.triggered.connect(self.create_template)
        edit_menu.addAction(self.create_template_action)
        
        # View menu
        view_menu = menubar.addMenu("View")
        
        # Switch to sources tab
        sources_action = QAction("Sources", self)
        sources_action.setShortcut("Ctrl+1")
        sources_action.triggered.connect(lambda: self.tab_widget.setCurrentIndex(0))
        view_menu.addAction(sources_action)
        
        # Switch to templates tab
        templates_action = QAction("Templates", self)
        templates_action.setShortcut("Ctrl+2")
        templates_action.triggered.connect(lambda: self.tab_widget.setCurrentIndex(1))
        view_menu.addAction(templates_action)
        
        # Switch to objects tab
        objects_action = QAction("Objects", self)
        objects_action.setShortcut("Ctrl+3")
        objects_action.triggered.connect(lambda: self.tab_widget.setCurrentIndex(2))
        view_menu.addAction(objects_action)
        
        # Help menu
        help_menu = menubar.addMenu("Help")
        
        # About action
        about_action = QAction("About", self)
        about_action.triggered.connect(self.show_about)
        help_menu.addAction(about_action)
    
    def create_toolbar(self):
        """Create the toolbar"""
        toolbar = QToolBar("Main Toolbar")
        self.addToolBar(toolbar)
        
        # Project buttons
        toolbar.addAction(self.new_project_action)
        toolbar.addAction(self.open_project_action)
        toolbar.addAction(self.save_project_action)
        toolbar.addSeparator()
        
        # Import source button
        toolbar.addAction(self.import_source_action)
        toolbar.addSeparator()
        
        # Create object button
        toolbar.addAction(self.create_object_action)
        
        # Create template button
        toolbar.addAction(self.create_template_action)
        
        toolbar.addSeparator()
        
        # Export button
        toolbar.addAction(self.export_action)
    
    def create_status_bar(self):
        """Create the status bar"""
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        
        # Status label
        self.status_label = QLabel("Ready")
        self.status_bar.addWidget(self.status_label)
        
        # Progress bar
        self.progress_bar = QLabel("")
        self.status_bar.addPermanentWidget(self.progress_bar)
        
        # Project status label
        self.project_status_label = QLabel("No Project")
        self.status_bar.addPermanentWidget(self.project_status_label)
    
    def show_project_dialog(self):
        """Show the project management dialog"""
        dialog = ProjectDialog(self)
        dialog.project_created.connect(self.on_project_created)
        dialog.project_loaded.connect(self.on_project_loaded)
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
            self.status_label.setText(f"Project loaded: {project_path.name}")
        else:
            QMessageBox.critical(self, "Error", "Failed to load project")
    
    def initialize_tabs(self):
        """Initialize tabs with the loaded project's asset manager"""
        if not self.asset_manager:
            return
        
        # Remove existing tabs
        for i in range(self.tab_widget.count()):
            self.tab_widget.removeTab(0)
        
        # Create new tabs
        self.sources_tab = SourcesTabV2(self.asset_manager)
        self.templates_tab = TemplatesTab(self.asset_manager)
        self.objects_tab = ObjectsTabV2(self.asset_manager)
        
        # Add tabs to widget
        self.tab_widget.addTab(self.sources_tab, "Sources")
        self.tab_widget.addTab(self.templates_tab, "Templates")
        self.tab_widget.addTab(self.objects_tab, "Objects")
        
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
    
    def refresh_status(self):
        """Refresh the status bar with current statistics"""
        if not self.asset_manager:
            self.progress_bar.setText("No project loaded")
            return
        
        source_count = len(self.asset_manager.sources)
        template_count = len(self.asset_manager.templates)
        object_count = len(self.asset_manager.objects)
        
        # Count total slices
        total_slices = sum(len(source.slices) for source in self.asset_manager.sources.values())
        
        status_text = f"Sources: {source_count} | Templates: {template_count} | Objects: {object_count} | Slices: {total_slices}"
        self.progress_bar.setText(status_text)
    
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
            self.project_status_label.setText(f"Project: {status['name']}")
        else:
            self.project_status_label.setText("No Project")
    
    def new_project(self):
        """Create a new project"""
        self.show_project_dialog()
    
    def open_project(self):
        """Open an existing project"""
        self.show_project_dialog()
    
    def save_project(self):
        """Save the current project"""
        if self.project_manager.save_project():
            self.status_label.setText("Project saved")
        else:
            QMessageBox.critical(self, "Error", "Failed to save project")
    
    def close_project(self):
        """Close the current project"""
        if self.project_manager.close_project():
            self.asset_manager = None
            self.initialize_tabs()
            self.update_ui_states()
            self.update_project_status()
            self.status_label.setText("Project closed")
        else:
            QMessageBox.critical(self, "Error", "Failed to close project")
    
    def import_source(self):
        """Import a new source image"""
        if not self.asset_manager:
            QMessageBox.warning(self, "No Project", "Please create or load a project first")
            return
        
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Import Source Image",
            "",
            "Image Files (*.png *.jpg *.jpeg *.svg *.bmp *.gif);;All Files (*)"
        )
        
        if file_path:
            try:
                # Load image to get dimensions
                pixmap = QPixmap(file_path)
                if pixmap.isNull():
                    QMessageBox.warning(self, "Error", "Could not load the image file")
                    return
                
                # Add source file to project
                project_relative_path = self.project_manager.add_source_file(Path(file_path))
                if not project_relative_path:
                    QMessageBox.critical(self, "Error", "Failed to add source file to project")
                    return
                
                # Add to asset manager
                source = self.asset_manager.add_source(
                    project_relative_path, pixmap.width(), pixmap.height()
                )
                
                # Switch to sources tab and load the source
                self.tab_widget.setCurrentIndex(0)
                self.sources_tab.load_source(source, str(project_relative_path))
                
                # Update UI states
                self.update_ui_states()
                
                self.status_label.setText(f"Imported: {source.file_path.name}")
                
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to load source: {str(e)}")
    
    def create_object(self):
        """Create a new object"""
        if not self.asset_manager:
            QMessageBox.warning(self, "No Project", "Please create or load a project first")
            return
        
        # Switch to objects tab and trigger creation
        self.tab_widget.setCurrentIndex(2)
        self.objects_tab.create_object()
        self.update_ui_states()
    
    def create_template(self):
        """Create a new template"""
        if not self.asset_manager:
            QMessageBox.warning(self, "No Project", "Please create or load a project first")
            return
        
        # Switch to templates tab and trigger creation
        self.tab_widget.setCurrentIndex(1)
        # Note: TemplatesTab doesn't have a create_template method yet
        # This would need to be implemented
        self.update_ui_states()
    
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
    
    def export_assets(self):
        """Export assets to build directory"""
        if not self.asset_manager:
            QMessageBox.warning(self, "No Project", "Please create or load a project first")
            return
        
        try:
            # Use project's build directory
            if self.project_manager.current_project_path:
                build_dir = self.project_manager.current_project_path / "build"
            else:
                build_dir = Path("build")
            
            build_dir.mkdir(exist_ok=True)
            
            # Export sources
            sources_dir = build_dir / "sources"
            sources_dir.mkdir(exist_ok=True)
            
            for source in self.asset_manager.sources.values():
                # In a real implementation, this would copy/convert the source files
                pass
            
            # Export slices
            slices_dir = build_dir / "slices"
            slices_dir.mkdir(exist_ok=True)
            
            for source in self.asset_manager.sources.values():
                for slice_obj in source.slices:
                    # In a real implementation, this would extract and save slices
                    pass
            
            # Export metadata
            metadata_file = build_dir / "metadata.json"
            self.asset_manager.save_metadata(str(metadata_file))
            
            QMessageBox.information(self, "Export Complete", f"Assets exported to {build_dir}")
            self.status_label.setText(f"Exported to {build_dir}")
            
        except Exception as e:
            QMessageBox.critical(self, "Export Error", f"Failed to export assets: {str(e)}")
    
    def show_about(self):
        """Show about dialog"""
        QMessageBox.about(
            self,
            "About CurioShelf V2",
            """
            <h3>CurioShelf V2</h3>
            <p>Visual Asset Manager for 2D Games</p>
            <p>Version 2.0</p>
            <p>Built with PySide6</p>
            <p><b>New in V2:</b></p>
            <ul>
            <li>1:1 correspondence between views and slices</li>
            <li>Simplified sources tab</li>
            <li>Enhanced objects tab with slice creation</li>
            <li>Improved template compliance tracking</li>
            </ul>
            """
        )
    
    def on_source_loaded(self, source):
        """Handle source loaded signal"""
        self.status_label.setText(f"Source loaded: {source.file_path.name}")
    
    def on_slice_created(self, slice_obj):
        """Handle slice created signal"""
        self.status_label.setText(f"Slice created: {slice_obj.name}")
    
    def on_object_created(self, obj):
        """Handle object created signal"""
        self.status_label.setText(f"Object created: {obj.name}")
    
    def on_object_updated(self, obj):
        """Handle object updated signal"""
        self.status_label.setText(f"Object updated: {obj.name}")
    
    def on_object_deleted(self, object_id):
        """Handle object deleted signal"""
        self.status_label.setText("Object deleted")
    
    def closeEvent(self, event):
        """Handle application close"""
        # Save project before closing
        if self.project_manager.is_project_loaded:
            if self.project_manager.save_project():
                self.status_label.setText("Project saved before closing")
            else:
                reply = QMessageBox.question(
                    self, "Save Error", 
                    "Failed to save project. Close anyway?",
                    QMessageBox.Yes | QMessageBox.No
                )
                if reply == QMessageBox.No:
                    event.ignore()
                    return
        
        event.accept()

