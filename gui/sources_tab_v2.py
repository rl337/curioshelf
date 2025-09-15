"""
Sources tab for managing source images (simplified)

This version removes slice creation functionality, which has been moved
to the objects tab to establish 1:1 correspondence between views and slices.
"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
    QPushButton, QComboBox, QMessageBox, QSplitter,
    QFileDialog, QScrollArea, QGroupBox
)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QPainter, QPen, QBrush, QPixmap, QFont
from typing import Optional, Tuple
from pathlib import Path

from curioshelf.models import AssetSource
from curioshelf.business_logic_v2 import SourcesController


class SourcesTabV2(QWidget):
    """Simplified tab for managing source images only"""
    
    # Signals
    source_loaded = Signal(AssetSource)
    
    def __init__(self, asset_manager):
        super().__init__()
        self.asset_manager = asset_manager
        self.current_source = None
        
        # Create business logic controller
        from curioshelf.ui_mocks import MockUIFactory
        self.controller = SourcesController(asset_manager, MockUIFactory)
        
        self.init_ui()
        self.refresh()
    
    def init_ui(self):
        """Initialize the user interface"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(5, 5, 5, 5)
        
        # Top controls
        controls_layout = QHBoxLayout()
        
        # Import button
        self.import_btn = QPushButton("Import Source")
        self.import_btn.clicked.connect(self.import_source)
        controls_layout.addWidget(self.import_btn)
        
        # Source selection
        controls_layout.addWidget(QLabel("Source:"))
        self.source_combo = QComboBox()
        self.source_combo.currentTextChanged.connect(self.on_source_selected)
        controls_layout.addWidget(self.source_combo)
        
        controls_layout.addStretch()
        
        # Source count
        self.source_count_label = QLabel("0 sources")
        controls_layout.addWidget(self.source_count_label)
        
        layout.addLayout(controls_layout)
        
        # Main content area
        splitter = QSplitter(Qt.Horizontal)
        layout.addWidget(splitter)
        
        # Left panel - source list
        left_panel = QWidget()
        left_layout = QVBoxLayout(left_panel)
        left_layout.setContentsMargins(0, 0, 0, 0)
        
        # Sources group
        sources_group = QGroupBox("Sources")
        sources_layout = QVBoxLayout(sources_group)
        
        self.sources_list = QComboBox()
        self.sources_list.currentTextChanged.connect(self.on_source_selected)
        sources_layout.addWidget(self.sources_list)
        
        # Source actions
        source_actions = QHBoxLayout()
        
        self.delete_source_btn = QPushButton("Delete Source")
        self.delete_source_btn.clicked.connect(self.delete_source)
        self.delete_source_btn.setEnabled(False)
        source_actions.addWidget(self.delete_source_btn)
        
        source_actions.addStretch()
        
        sources_layout.addLayout(source_actions)
        left_layout.addWidget(sources_group)
        
        # Right panel - source preview
        right_panel = QWidget()
        right_layout = QVBoxLayout(right_panel)
        right_layout.setContentsMargins(0, 0, 0, 0)
        
        # Preview group
        preview_group = QGroupBox("Preview")
        preview_layout = QVBoxLayout(preview_group)
        
        # Canvas for image display
        self.canvas = SourceCanvas()
        self.canvas.setMinimumSize(400, 300)
        self.canvas.setStyleSheet("border: 1px solid #ccc; background-color: #f0f0f0;")
        
        # Scroll area for canvas
        scroll_area = QScrollArea()
        scroll_area.setWidget(self.canvas)
        scroll_area.setWidgetResizable(True)
        preview_layout.addWidget(scroll_area)
        
        # Source info
        self.source_info_label = QLabel("No source selected")
        self.source_info_label.setWordWrap(True)
        preview_layout.addWidget(self.source_info_label)
        
        right_layout.addWidget(preview_group)
        
        # Add panels to splitter
        splitter.addWidget(left_panel)
        splitter.addWidget(right_panel)
        
        # Set splitter proportions
        splitter.setSizes([200, 600])
    
    def refresh(self):
        """Refresh the UI with current data"""
        self.refresh_sources_list()
        self.update_source_count()
    
    def refresh_sources_list(self):
        """Refresh the sources list"""
        self.source_combo.clear()
        self.sources_list.clear()
        
        for source in self.asset_manager.sources.values():
            display_text = f"{source.file_path.name} ({source.width}x{source.height})"
            self.source_combo.addItem(display_text)
            self.sources_list.addItem(display_text)
    
    def update_source_count(self):
        """Update the source count label"""
        count = len(self.asset_manager.sources)
        self.source_count_label.setText(f"{count} source{'s' if count != 1 else ''}")
    
    def import_source(self):
        """Import a new source image"""
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
                
                # Add to asset manager
                source = self.asset_manager.add_source(
                    Path(file_path), pixmap.width(), pixmap.height()
                )
                
                # Load into canvas
                self.load_source(source, file_path)
                
                # Refresh UI
                self.refresh()
                self.source_combo.setCurrentText(f"{source.file_path.name} ({source.width}x{source.height})")
                
                # Emit signal
                self.source_loaded.emit(source)
                
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to load source: {str(e)}")
    
    def load_source(self, source: AssetSource, file_path: str):
        """Load a source image into the canvas"""
        self.current_source = source
        
        # Load image into canvas
        pixmap = QPixmap(file_path)
        if not pixmap.isNull():
            self.canvas.set_pixmap(pixmap)
            self.canvas.set_zoom(1.0)
        
        # Update info
        info_text = f"""
        <b>File:</b> {source.file_path.name}<br>
        <b>Path:</b> {source.file_path}<br>
        <b>Size:</b> {source.width} x {source.height}<br>
        <b>Type:</b> {source.file_type}<br>
        <b>Slices:</b> {len(source.slices)}
        """
        self.source_info_label.setText(info_text)
        
        # Enable delete button
        self.delete_source_btn.setEnabled(True)
    
    def on_source_selected(self, display_text: str):
        """Handle source selection"""
        if not display_text:
            return
        
        # Find the source by display text
        for source in self.asset_manager.sources.values():
            expected_text = f"{source.file_path.name} ({source.width}x{source.height})"
            if display_text == expected_text:
                self.load_source(source, str(source.file_path))
                break
    
    def delete_source(self):
        """Delete the selected source"""
        if not self.current_source:
            return
        
        # Check if source has slices
        if self.current_source.slices:
            reply = QMessageBox.question(
                self,
                "Delete Source",
                f"This source has {len(self.current_source.slices)} slice(s). Are you sure you want to delete it?",
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.No
            )
            if reply != QMessageBox.Yes:
                return
        
        # Remove from asset manager
        source_id = self.current_source.id
        if source_id in self.asset_manager.sources:
            del self.asset_manager.sources[source_id]
        
        # Clear current source and refresh
        self.current_source = None
        self.canvas.clear()
        self.source_info_label.setText("No source selected")
        self.delete_source_btn.setEnabled(False)
        self.refresh()


class SourceCanvas(QWidget):
    """Canvas for displaying source images"""
    
    def __init__(self):
        super().__init__()
        self.pixmap = None
        self.zoom_factor = 1.0
    
    def set_pixmap(self, pixmap: QPixmap):
        """Set the image to display"""
        self.pixmap = pixmap
        self.update()
    
    def set_zoom(self, zoom_factor: float):
        """Set the zoom factor"""
        self.zoom_factor = zoom_factor
        self.update()
    
    def clear(self):
        """Clear the canvas"""
        self.pixmap = None
        self.update()
    
    def paintEvent(self, event):
        """Paint the canvas"""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        # Fill background
        painter.fillRect(self.rect(), QBrush(Qt.white))
        
        if self.pixmap and not self.pixmap.isNull():
            # Calculate scaled size
            scaled_size = self.pixmap.size() * self.zoom_factor
            
            # Center the image
            x = (self.width() - scaled_size.width()) // 2
            y = (self.height() - scaled_size.height()) // 2
            
            # Draw the image
            painter.drawPixmap(x, y, self.pixmap.scaled(scaled_size, Qt.KeepAspectRatio, Qt.SmoothTransformation))
            
            # Draw border
            painter.setPen(QPen(Qt.black, 1))
            painter.drawRect(x, y, scaled_size.width(), scaled_size.height())
    
    def sizeHint(self):
        """Return the preferred size"""
        if self.pixmap and not self.pixmap.isNull():
            return self.pixmap.size() * self.zoom_factor
        return super().sizeHint()
