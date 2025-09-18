"""
Sources Controller

Business logic controller for sources management.
"""

from typing import List, Optional, Dict, Any, Callable
from pathlib import Path

from ...models import AssetManager, AssetSource, ObjectSlice, CurioObject, Template
from ...ui_abstraction import (
    UIWidget, UIButton, UITextInput, UIComboBox, UIListWidget, UICanvas,
    UIMessageBox, UIFileDialog, UIProgressBar, UIGroupBox, UITabWidget
)
from ...ui_factory_interface import UIFactoryInterface, UIComponentManager


class SourcesController:
    """Business logic controller for sources management (simplified)"""
    
    def __init__(self, asset_manager: AssetManager, ui_factory: UIFactoryInterface) -> None:
        self.asset_manager = asset_manager
        self.ui_factory = ui_factory
        self.ui_manager = UIComponentManager(ui_factory)
        
        # UI components
        self.import_btn: Optional[UIButton] = None
        self.source_combo: Optional[UIComboBox] = None
        self.canvas: Optional[UICanvas] = None
        
        # State
        self.current_source: Optional[AssetSource] = None
        self.message_box: Optional[UIMessageBox] = None
        self.file_dialog: Optional[UIFileDialog] = None
        
        # Callbacks
        self.on_source_loaded: Optional[Callable[[AssetSource], None]] = None
    
    def setup_ui(self, ui_factory: UIFactoryInterface) -> None:
        """Setup UI components using the factory"""
        self.ui_factory = ui_factory
        self.ui_manager = UIComponentManager(ui_factory)
        
        # Create UI components
        self.import_btn = ui_factory.create_button("Import Source")
        self.source_combo = ui_factory.create_combo_box()
        self.canvas = ui_factory.create_canvas()
        self.message_box = ui_factory.create_message_box()
        self.file_dialog = ui_factory.create_file_dialog()
        
        # Setup connections
        self.import_btn.set_clicked_callback(self.import_source)
        self.source_combo.set_current_changed_callback(self.on_source_selected)
        
        # Initial refresh
        self.refresh()
    
    def refresh(self) -> None:
        """Refresh the UI with current data"""
        self.refresh_source_combo()
    
    def refresh_source_combo(self) -> None:
        """Refresh the source combo box"""
        if not self.source_combo:
            return
        
        self.source_combo.clear()
        for source in self.asset_manager.sources.values():
            display_text = f"{source.file_path.name} ({source.width}x{source.height})"
            self.source_combo.add_item(display_text, source.id)
    
    def import_source(self) -> None:
        """Import a new source image"""
        if not self.file_dialog:
            return
        
        file_path = self.file_dialog.get_open_file_name(
            "Import Source Image",
            "Image Files (*.png *.jpg *.jpeg *.svg *.bmp *.gif);;All Files (*)"
        )
        
        if file_path:
            try:
                # Create a mock pixmap for testing
                pixmap = self.ui_factory.create_pixmap(800, 600)
                
                if pixmap.isNull():
                    if self.message_box:
                        self.message_box.show_warning("Error", "Could not load the image file")
                    return
                
                # Add to asset manager
                source = self.asset_manager.add_source(
                    Path(file_path), pixmap.width, pixmap.height
                )
                
                # Load into canvas
                self.load_source(source, file_path)
                
                # Emit callback
                if self.on_source_loaded:
                    self.on_source_loaded(source)
                
            except Exception as e:
                if self.message_box:
                    self.message_box.show_error("Error", f"Failed to load source: {str(e)}")
    
    def load_source(self, source: AssetSource, file_path: str) -> None:
        """Load a source image into the canvas"""
        self.current_source = source
        if self.canvas:
            pixmap = self.ui_factory.create_pixmap(source.width, source.height)
            self.canvas.set_pixmap(pixmap)
            self.canvas.set_zoom(1.0)
    
    def on_source_selected(self, source_id: str) -> None:
        """Handle source selection"""
        if not source_id:
            return
        
        source = self.asset_manager.sources.get(source_id)
        if source:
            self.load_source(source, str(source.file_path))
