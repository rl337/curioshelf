"""
Tabbed main window for CurioShelf GUI
"""

from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
    QTabWidget, QMenuBar, QMenu, QStatusBar, QLabel,
    QFileDialog, QMessageBox, QToolBar, QSplitter
)
from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QPixmap, QAction
from pathlib import Path

from gui.sources_tab import SourcesTab
from gui.templates_tab import TemplatesTab
from gui.objects_tab import ObjectsTab
from curioshelf.models import AssetManager


class TabbedMainWindow(QMainWindow):
    """Main application window with tabbed interface"""
    
    def __init__(self):
        super().__init__()
        self.asset_manager = AssetManager()
        self.init_ui()
        self.setup_menus()
        self.setup_toolbar()
        self.setup_status_bar()
        
        # Load default templates
        self.load_default_templates()
    
    def init_ui(self):
        """Initialize the user interface"""
        self.setWindowTitle("CurioShelf - Visual Asset Manager")
        self.setGeometry(100, 100, 1400, 900)
        
        # Central widget with tab widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Main layout
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(5, 5, 5, 5)
        
        # Create tab widget
        self.tab_widget = QTabWidget()
        main_layout.addWidget(self.tab_widget)
        
        # Create tabs
        self.sources_tab = SourcesTab(self.asset_manager)
        self.templates_tab = TemplatesTab(self.asset_manager)
        self.objects_tab = ObjectsTab(self.asset_manager)
        
        # Add tabs
        self.tab_widget.addTab(self.sources_tab, "Sources")
        self.tab_widget.addTab(self.templates_tab, "Templates")
        self.tab_widget.addTab(self.objects_tab, "Objects")
        
        # Connect signals between tabs
        self.sources_tab.source_loaded.connect(self.objects_tab.on_source_loaded)
        self.templates_tab.template_created.connect(self.objects_tab.on_template_created)
        self.objects_tab.object_created.connect(self.sources_tab.on_object_created)
    
    def setup_menus(self):
        """Setup menu bar"""
        menubar = self.menuBar()
        
        # File menu
        file_menu = menubar.addMenu("&File")
        
        # New project
        new_action = QAction("&New Project", self)
        new_action.setShortcut("Ctrl+N")
        new_action.triggered.connect(self.new_project)
        file_menu.addAction(new_action)
        
        # Open project
        open_action = QAction("&Open Project", self)
        open_action.setShortcut("Ctrl+O")
        open_action.triggered.connect(self.open_project)
        file_menu.addAction(open_action)
        
        # Save project
        save_action = QAction("&Save Project", self)
        save_action.setShortcut("Ctrl+S")
        save_action.triggered.connect(self.save_project)
        file_menu.addAction(save_action)
        
        file_menu.addSeparator()
        
        # Export
        export_action = QAction("&Export Assets", self)
        export_action.setShortcut("Ctrl+E")
        export_action.triggered.connect(self.export_assets)
        file_menu.addAction(export_action)
        
        file_menu.addSeparator()
        
        # Exit
        exit_action = QAction("E&xit", self)
        exit_action.setShortcut("Ctrl+Q")
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)
        
        # View menu
        view_menu = menubar.addMenu("&View")
        
        # Tab shortcuts
        sources_action = QAction("&Sources Tab", self)
        sources_action.setShortcut("Ctrl+1")
        sources_action.triggered.connect(lambda: self.tab_widget.setCurrentIndex(0))
        view_menu.addAction(sources_action)
        
        templates_action = QAction("&Templates Tab", self)
        templates_action.setShortcut("Ctrl+2")
        templates_action.triggered.connect(lambda: self.tab_widget.setCurrentIndex(1))
        view_menu.addAction(templates_action)
        
        objects_action = QAction("&Objects Tab", self)
        objects_action.setShortcut("Ctrl+3")
        objects_action.triggered.connect(lambda: self.tab_widget.setCurrentIndex(2))
        view_menu.addAction(objects_action)
    
    def setup_toolbar(self):
        """Setup toolbar"""
        toolbar = QToolBar("Main Toolbar")
        self.addToolBar(toolbar)
        
        # Import source
        import_action = QAction("Import Source", self)
        import_action.triggered.connect(self.import_source)
        toolbar.addAction(import_action)
        
        toolbar.addSeparator()
        
        # Tab navigation
        sources_action = QAction("Sources", self)
        sources_action.triggered.connect(lambda: self.tab_widget.setCurrentIndex(0))
        toolbar.addAction(sources_action)
        
        templates_action = QAction("Templates", self)
        templates_action.triggered.connect(lambda: self.tab_widget.setCurrentIndex(1))
        toolbar.addAction(templates_action)
        
        objects_action = QAction("Objects", self)
        objects_action.triggered.connect(lambda: self.tab_widget.setCurrentIndex(2))
        toolbar.addAction(objects_action)
    
    def setup_status_bar(self):
        """Setup status bar"""
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        
        self.status_label = QLabel("Ready")
        self.status_bar.addWidget(self.status_label)
        
        # Tab indicator
        self.tab_label = QLabel("Sources")
        self.status_bar.addPermanentWidget(self.tab_label)
        
        # Connect tab change signal
        self.tab_widget.currentChanged.connect(self.on_tab_changed)
    
    def on_tab_changed(self, index):
        """Handle tab change"""
        tab_names = ["Sources", "Templates", "Objects"]
        if 0 <= index < len(tab_names):
            self.tab_label.setText(tab_names[index])
    
    def load_default_templates(self):
        """Load some default templates"""
        # Character template
        self.asset_manager.add_template(
            "character",
            "Basic character template",
            ["front", "back", "left", "right", "walk1", "walk2", "idle"]
        )
        
        # Tile template
        self.asset_manager.add_template(
            "tile",
            "Basic tile template",
            ["base", "variant1", "variant2"]
        )
        
        # UI element template
        self.asset_manager.add_template(
            "ui_element",
            "UI element template",
            ["normal", "hover", "pressed", "disabled"]
        )
        
        # Refresh templates tab
        self.templates_tab.refresh()
    
    def new_project(self):
        """Create a new project"""
        reply = QMessageBox.question(
            self, "New Project", 
            "This will clear all current data. Continue?",
            QMessageBox.Yes | QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            self.asset_manager = AssetManager()
            self.load_default_templates()
            
            # Refresh all tabs
            self.sources_tab.refresh()
            self.templates_tab.refresh()
            self.objects_tab.refresh()
            
            self.status_label.setText("New project created")
    
    def open_project(self):
        """Open an existing project"""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Open Project", "", "JSON Files (*.json)"
        )
        
        if file_path:
            try:
                self.asset_manager.load_metadata(file_path)
                
                # Refresh all tabs
                self.sources_tab.refresh()
                self.templates_tab.refresh()
                self.objects_tab.refresh()
                
                self.status_label.setText(f"Project loaded: {file_path}")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to load project: {str(e)}")
    
    def save_project(self):
        """Save the current project"""
        file_path, _ = QFileDialog.getSaveFileName(
            self, "Save Project", "", "JSON Files (*.json)"
        )
        
        if file_path:
            try:
                self.asset_manager.save_metadata(file_path)
                self.status_label.setText(f"Project saved: {file_path}")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to save project: {str(e)}")
    
    def import_source(self):
        """Import a source image"""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Import Source Image", "",
            "Image Files (*.png *.jpg *.jpeg *.svg *.bmp *.gif);;All Files (*)"
        )
        
        if file_path:
            try:
                # Load the image and get dimensions
                from PySide6.QtGui import QPixmap
                pixmap = QPixmap(file_path)
                
                if pixmap.isNull():
                    QMessageBox.warning(self, "Error", "Could not load the image file")
                    return
                
                # Add to asset manager
                source = self.asset_manager.add_source(
                    Path(file_path), pixmap.width(), pixmap.height()
                )
                
                # Switch to sources tab and load the source
                self.tab_widget.setCurrentIndex(0)
                self.sources_tab.load_source(source, file_path)
                
                self.status_label.setText(f"Source loaded: {file_path}")
                
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to load source: {str(e)}")
    
    def export_assets(self):
        """Export assets (stubbed for now)"""
        QMessageBox.information(
            self, "Export Assets", 
            "Export functionality will be implemented in the next phase."
        )
