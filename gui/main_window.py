"""
Main window for CurioShelf GUI
"""

from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
    QSplitter, QMenuBar, QMenu, QStatusBar, QLabel,
    QFileDialog, QMessageBox, QToolBar
)
from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QPixmap, QAction

from gui.canvas_widget import CanvasWidget
from gui.object_panel import ObjectPanel
from gui.template_panel import TemplatePanel
from curioshelf.models import AssetManager


class MainWindow(QMainWindow):
    """Main application window"""
    
    def __init__(self):
        super().__init__()
        self.asset_manager = AssetManager()
        self.current_source = None
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
        
        # Central widget with splitter
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Main layout
        main_layout = QHBoxLayout(central_widget)
        main_layout.setContentsMargins(5, 5, 5, 5)
        
        # Create splitter for resizable panels
        splitter = QSplitter(Qt.Horizontal)
        main_layout.addWidget(splitter)
        
        # Left panel for objects and templates
        left_panel = QWidget()
        left_layout = QVBoxLayout(left_panel)
        left_layout.setContentsMargins(0, 0, 0, 0)
        
        # Object panel
        self.object_panel = ObjectPanel(self.asset_manager)
        left_layout.addWidget(self.object_panel)
        
        # Template panel
        self.template_panel = TemplatePanel(self.asset_manager)
        left_layout.addWidget(self.template_panel)
        
        # Canvas widget (center)
        self.canvas_widget = CanvasWidget(self.asset_manager)
        
        # Add panels to splitter
        splitter.addWidget(left_panel)
        splitter.addWidget(self.canvas_widget)
        
        # Set splitter proportions (left panel: 300px, canvas: rest)
        splitter.setSizes([300, 1100])
    
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
        
        # Import source
        import_action = QAction("&Import Source", self)
        import_action.setShortcut("Ctrl+I")
        import_action.triggered.connect(self.import_source)
        file_menu.addAction(import_action)
        
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
        
        # Edit menu
        edit_menu = menubar.addMenu("&Edit")
        
        # Undo/Redo (placeholder)
        undo_action = QAction("&Undo", self)
        undo_action.setShortcut("Ctrl+Z")
        undo_action.setEnabled(False)
        edit_menu.addAction(undo_action)
        
        redo_action = QAction("&Redo", self)
        redo_action.setShortcut("Ctrl+Y")
        redo_action.setEnabled(False)
        edit_menu.addAction(redo_action)
        
        # View menu
        view_menu = menubar.addMenu("&View")
        
        # Zoom controls
        zoom_in_action = QAction("Zoom &In", self)
        zoom_in_action.setShortcut("Ctrl+=")
        zoom_in_action.triggered.connect(self.canvas_widget.zoom_in)
        view_menu.addAction(zoom_in_action)
        
        zoom_out_action = QAction("Zoom &Out", self)
        zoom_out_action.setShortcut("Ctrl+-")
        zoom_out_action.triggered.connect(self.canvas_widget.zoom_out)
        view_menu.addAction(zoom_out_action)
        
        zoom_fit_action = QAction("&Fit to Window", self)
        zoom_fit_action.setShortcut("Ctrl+0")
        zoom_fit_action.triggered.connect(self.canvas_widget.zoom_fit)
        view_menu.addAction(zoom_fit_action)
    
    def setup_toolbar(self):
        """Setup toolbar"""
        toolbar = QToolBar("Main Toolbar")
        self.addToolBar(toolbar)
        
        # Import source
        import_action = QAction("Import Source", self)
        import_action.triggered.connect(self.import_source)
        toolbar.addAction(import_action)
        
        toolbar.addSeparator()
        
        # Zoom controls
        zoom_in_action = QAction("Zoom In", self)
        zoom_in_action.triggered.connect(self.canvas_widget.zoom_in)
        toolbar.addAction(zoom_in_action)
        
        zoom_out_action = QAction("Zoom Out", self)
        zoom_out_action.triggered.connect(self.canvas_widget.zoom_out)
        toolbar.addAction(zoom_out_action)
        
        zoom_fit_action = QAction("Fit", self)
        zoom_fit_action.triggered.connect(self.canvas_widget.zoom_fit)
        toolbar.addAction(zoom_fit_action)
    
    def setup_status_bar(self):
        """Setup status bar"""
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        
        self.status_label = QLabel("Ready")
        self.status_bar.addWidget(self.status_label)
        
        # Zoom level indicator
        self.zoom_label = QLabel("100%")
        self.status_bar.addPermanentWidget(self.zoom_label)
    
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
            self.canvas_widget.clear()
            self.object_panel.refresh()
            self.template_panel.refresh()
            self.status_label.setText("New project created")
    
    def open_project(self):
        """Open an existing project"""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Open Project", "", "JSON Files (*.json)"
        )
        
        if file_path:
            try:
                self.asset_manager.load_metadata(file_path)
                self.object_panel.refresh()
                self.template_panel.refresh()
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
                    file_path, pixmap.width(), pixmap.height()
                )
                
                # Load into canvas
                self.canvas_widget.load_source(source, file_path)
                self.current_source = source
                
                # Connect slice creation to object panel
                self.canvas_widget.slice_created.connect(self.object_panel.add_slice_to_object)
                
                self.status_label.setText(f"Source loaded: {file_path}")
                
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to load source: {str(e)}")
    
    def export_assets(self):
        """Export assets (stubbed for now)"""
        QMessageBox.information(
            self, "Export Assets", 
            "Export functionality will be implemented in the next phase."
        )
