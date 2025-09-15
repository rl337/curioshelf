"""
Abstracted sources tab for managing source images

This version uses the UI abstraction layer instead of direct PySide6 imports.
"""

from typing import Optional, Callable
from pathlib import Path

from curioshelf.models import AssetManager, AssetSource
from curioshelf.ui_abstraction import UIWidget


class SourcesTabAbstracted:
    """Sources tab using UI abstraction layer"""
    
    def __init__(self, asset_manager: AssetManager, ui_factory):
        self.asset_manager = asset_manager
        self.ui_factory = ui_factory
        self.current_source: Optional[AssetSource] = None
        
        # UI components
        self.widget = None
        self.source_combo = None
        self.canvas = None
        self.import_btn = None
        
        # Callbacks
        self.source_loaded: Optional[Callable[[AssetSource], None]] = None
        
        self.setup_ui()
        self.refresh()
    
    def setup_ui(self):
        """Setup the UI using abstraction layer"""
        # Create main widget
        self.widget = self.ui_factory.create_widget()
        
        # Create layout
        layout = self.ui_factory.create_layout("vertical")
        self.widget.set_layout(layout)
        
        # Create controls
        controls_group = self.ui_factory.create_group_box("Source Controls")
        controls_layout = self.ui_factory.create_layout("horizontal")
        controls_group.set_layout(controls_layout)
        
        # Import button
        self.import_btn = self.ui_factory.create_button("Import Source")
        self.import_btn.set_clicked_callback(self.import_source)
        controls_layout.add_widget(self.import_btn)
        
        # Source selection
        self.source_combo = self.ui_factory.create_combo_box()
        self.source_combo.set_current_changed_callback(self.on_source_selected)
        controls_layout.add_widget(self.source_combo)
        
        layout.add_widget(controls_group)
        
        # Create canvas
        self.canvas = self.ui_factory.create_canvas()
        layout.add_widget(self.canvas)
    
    def get_widget(self) -> UIWidget:
        """Get the main widget"""
        return self.widget
    
    def refresh(self):
        """Refresh the UI with current data"""
        self.refresh_source_combo()
    
    def refresh_source_combo(self):
        """Refresh the source combo box"""
        if not self.source_combo:
            return
        
        self.source_combo.clear()
        for source in self.asset_manager.sources.values():
            display_text = f"{source.file_path.name} ({source.width}x{source.height})"
            self.source_combo.add_item(display_text, source.id)
    
    def import_source(self):
        """Import a new source image"""
        file_dialog = self.ui_factory.create_file_dialog()
        file_path = file_dialog.get_open_file_name(
            "Import Source Image",
            "Image Files (*.png *.jpg *.jpeg *.svg *.bmp *.gif);;All Files (*)"
        )
        
        if file_path:
            try:
                # Create a mock pixmap for testing
                pixmap = self.ui_factory.create_pixmap(800, 600)
                
                # Add to asset manager
                source = self.asset_manager.add_source(
                    Path(file_path), pixmap.width, pixmap.height
                )
                
                # Load into canvas
                self.load_source(source, file_path)
                
                # Emit callback
                if self.source_loaded:
                    self.source_loaded(source)
                
            except Exception as e:
                msg_box = self.ui_factory.create_message_box()
                msg_box.show_error("Error", f"Failed to load source: {str(e)}")
    
    def load_source(self, source: AssetSource, file_path: str):
        """Load a source image into the canvas"""
        self.current_source = source
        if self.canvas:
            pixmap = self.ui_factory.create_pixmap(source.width, source.height)
            self.canvas.set_pixmap(pixmap)
            self.canvas.set_zoom(1.0)
    
    def on_source_selected(self, source_id: str):
        """Handle source selection"""
        if not source_id:
            return
        
        source = self.asset_manager.sources.get(source_id)
        if source:
            self.load_source(source, str(source.file_path))
    
    def connect_signal(self, signal_name: str, callback: Callable):
        """Connect a signal callback"""
        if signal_name == "source_loaded":
            self.source_loaded = callback
