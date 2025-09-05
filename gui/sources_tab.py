"""
Sources tab for managing source images and creating slices
"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
    QPushButton, QLineEdit, QComboBox, QListWidget,
    QListWidgetItem, QGroupBox, QMessageBox, QSplitter,
    QFileDialog, QScrollArea
)
from PySide6.QtCore import Qt, Signal, QRect
from PySide6.QtGui import QPainter, QPen, QBrush, QPixmap, QFont
from typing import Optional, Tuple
from pathlib import Path

from curioshelf.models import AssetSource, ObjectSlice


class SourcesTab(QWidget):
    """Tab for managing source images and creating slices"""
    
    # Signals
    source_loaded = Signal(AssetSource)
    slice_created = Signal(ObjectSlice)
    
    def __init__(self, asset_manager):
        super().__init__()
        self.asset_manager = asset_manager
        self.current_source = None
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
        
        # Zoom controls
        self.zoom_out_btn = QPushButton("-")
        self.zoom_out_btn.clicked.connect(self.zoom_out)
        controls_layout.addWidget(self.zoom_out_btn)
        
        self.zoom_label = QLabel("100%")
        self.zoom_label.setMinimumWidth(50)
        controls_layout.addWidget(self.zoom_label)
        
        self.zoom_in_btn = QPushButton("+")
        self.zoom_in_btn.clicked.connect(self.zoom_in)
        controls_layout.addWidget(self.zoom_in_btn)
        
        self.zoom_fit_btn = QPushButton("Fit")
        self.zoom_fit_btn.clicked.connect(self.zoom_fit)
        controls_layout.addWidget(self.zoom_fit_btn)
        
        layout.addLayout(controls_layout)
        
        # Main content with splitter
        splitter = QSplitter(Qt.Horizontal)
        layout.addWidget(splitter)
        
        # Left panel for slice creation
        left_panel = QWidget()
        left_layout = QVBoxLayout(left_panel)
        
        # Slice creation group
        slice_group = QGroupBox("Create Slice")
        slice_layout = QVBoxLayout(slice_group)
        
        # Slice name input
        slice_layout.addWidget(QLabel("Slice Name:"))
        self.slice_name_input = QLineEdit()
        self.slice_name_input.setPlaceholderText("Enter slice name...")
        slice_layout.addWidget(self.slice_name_input)
        
        # Layer selection
        slice_layout.addWidget(QLabel("Layer:"))
        self.layer_combo = QComboBox()
        self.layer_combo.addItems(["concept", "working", "production"])
        slice_layout.addWidget(self.layer_combo)
        
        # Object selection
        slice_layout.addWidget(QLabel("Object:"))
        self.object_combo = QComboBox()
        self.object_combo.addItem("No Object", None)
        slice_layout.addWidget(self.object_combo)
        
        # Create slice button
        self.create_slice_btn = QPushButton("Create Slice")
        self.create_slice_btn.clicked.connect(self.create_slice)
        self.create_slice_btn.setEnabled(False)
        slice_layout.addWidget(self.create_slice_btn)
        
        # Clear selection button
        self.clear_selection_btn = QPushButton("Clear Selection")
        self.clear_selection_btn.clicked.connect(self.clear_selection)
        slice_layout.addWidget(self.clear_selection_btn)
        
        left_layout.addWidget(slice_group)
        
        # Slices list
        slices_group = QGroupBox("Slices")
        slices_layout = QVBoxLayout(slices_group)
        
        self.slices_list = QListWidget()
        self.slices_list.itemClicked.connect(self.on_slice_selected)
        slices_layout.addWidget(self.slices_list)
        
        # Slice actions
        slice_actions = QHBoxLayout()
        
        self.delete_slice_btn = QPushButton("Delete Slice")
        self.delete_slice_btn.clicked.connect(self.delete_slice)
        self.delete_slice_btn.setEnabled(False)
        slice_actions.addWidget(self.delete_slice_btn)
        
        slice_actions.addStretch()
        
        slices_layout.addLayout(slice_actions)
        
        left_layout.addWidget(slices_group)
        
        # Canvas area (right panel)
        self.canvas = SourceCanvas(self)
        self.canvas.selection_changed.connect(self.on_selection_changed)
        
        # Add panels to splitter
        splitter.addWidget(left_panel)
        splitter.addWidget(self.canvas)
        
        # Set splitter proportions
        splitter.setSizes([300, 1100])
    
    def refresh(self):
        """Refresh the source list and object list"""
        # Refresh source combo
        self.source_combo.clear()
        for source in self.asset_manager.sources.values():
            self.source_combo.addItem(f"{source.file_path.name} ({source.width}x{source.height})", source.id)
        
        # Refresh object combo
        self.object_combo.clear()
        self.object_combo.addItem("No Object", None)
        for obj in self.asset_manager.objects.values():
            self.object_combo.addItem(obj.name, obj.id)
    
    def import_source(self):
        """Import a new source image"""
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
                
                # Refresh and select the new source
                self.refresh()
                self.source_combo.setCurrentText(f"{source.file_path.name} ({source.width}x{source.height})")
                self.load_source(source, file_path)
                
                # Emit signal
                self.source_loaded.emit(source)
                
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to load source: {str(e)}")
    
    def load_source(self, source: AssetSource, file_path: str):
        """Load a source image into the canvas"""
        self.current_source = source
        self.canvas.set_pixmap(QPixmap(file_path))
        self.canvas.set_zoom(1.0)
        self.refresh_slices()
    
    def on_source_selected(self, text):
        """Handle source selection"""
        if not text:
            return
        
        source_id = self.source_combo.currentData()
        if source_id:
            source = self.asset_manager.sources.get(source_id)
            if source:
                self.load_source(source, str(source.file_path))
    
    def on_selection_changed(self, selection_rect: Optional[QRect]):
        """Handle selection changes from the canvas"""
        if selection_rect and selection_rect.isValid():
            self.create_slice_btn.setEnabled(True)
            # Update slice name input with suggested name
            if not self.slice_name_input.text():
                self.slice_name_input.setText("slice")
        else:
            self.create_slice_btn.setEnabled(False)
    
    def create_slice(self):
        """Create a slice from the current selection"""
        if not self.current_source or not self.canvas.selection_rect:
            return
        
        slice_name = self.slice_name_input.text().strip()
        if not slice_name:
            QMessageBox.warning(self, "Error", "Please enter a slice name")
            return
        
        # Convert selection coordinates from canvas space to source space
        selection = self.canvas.selection_rect
        source_rect = self.canvas.canvas_to_source_rect(selection)
        
        if not source_rect.isValid():
            QMessageBox.warning(self, "Error", "Invalid selection")
            return
        
        # Create the slice
        slice_obj = ObjectSlice(
            name=slice_name,
            source_id=self.current_source.id,
            x=source_rect.x(),
            y=source_rect.y(),
            width=source_rect.width(),
            height=source_rect.height(),
            layer=self.layer_combo.currentText()
        )
        
        # Add to source
        self.current_source.add_slice(slice_obj)
        
        # Add to object if selected
        object_id = self.object_combo.currentData()
        if object_id:
            obj = self.asset_manager.objects.get(object_id)
            if obj:
                obj.slices.append(slice_obj)
        
        # Emit signal
        self.slice_created.emit(slice_obj)
        
        # Clear selection and reset UI
        self.clear_selection()
        self.slice_name_input.clear()
        self.refresh_slices()
        
        QMessageBox.information(self, "Success", f"Slice '{slice_name}' created successfully!")
    
    def clear_selection(self):
        """Clear the current selection"""
        self.canvas.clear_selection()
        self.create_slice_btn.setEnabled(False)
    
    def on_slice_selected(self, item):
        """Handle slice selection"""
        if item:
            self.delete_slice_btn.setEnabled(True)
        else:
            self.delete_slice_btn.setEnabled(False)
    
    def delete_slice(self):
        """Delete the selected slice"""
        current_item = self.slices_list.currentItem()
        if not current_item or not self.current_source:
            return
        
        slice_name = current_item.text()
        
        reply = QMessageBox.question(
            self, "Delete Slice",
            f"Are you sure you want to delete slice '{slice_name}'?",
            QMessageBox.Yes | QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            # Remove from source
            self.current_source.remove_slice(slice_name)
            
            # Remove from any objects
            for obj in self.asset_manager.objects.values():
                obj.slices = [s for s in obj.slices if s.name != slice_name]
            
            self.refresh_slices()
    
    def refresh_slices(self):
        """Refresh the slices list for the current source"""
        self.slices_list.clear()
        
        if not self.current_source:
            return
        
        # Group slices by layer
        slices_by_layer = {}
        for slice_obj in self.current_source.slices:
            layer = slice_obj.layer
            if layer not in slices_by_layer:
                slices_by_layer[layer] = []
            slices_by_layer[layer].append(slice_obj)
        
        # Add slices to list
        for layer in sorted(slices_by_layer.keys()):
            # Add layer header
            layer_item = QListWidgetItem(f"--- {layer.upper()} ---")
            layer_item.setFlags(Qt.NoItemFlags)  # Not selectable
            layer_item.setBackground(Qt.lightGray)
            self.slices_list.addItem(layer_item)
            
            # Add slices for this layer
            for slice_obj in sorted(slices_by_layer[layer], key=lambda s: s.name):
                item = QListWidgetItem(f"  {slice_obj.name}")
                item.setData(Qt.UserRole, slice_obj)
                self.slices_list.addItem(item)
    
    def zoom_in(self):
        """Zoom in"""
        self.canvas.zoom_in()
        self.zoom_label.setText(f"{int(self.canvas.zoom_factor * 100)}%")
    
    def zoom_out(self):
        """Zoom out"""
        self.canvas.zoom_out()
        self.zoom_label.setText(f"{int(self.canvas.zoom_factor * 100)}%")
    
    def zoom_fit(self):
        """Fit image to canvas"""
        self.canvas.zoom_fit()
        self.zoom_label.setText(f"{int(self.canvas.zoom_factor * 100)}%")
    
    def on_object_created(self, obj):
        """Handle object creation from other tabs"""
        self.refresh()


class SourceCanvas(QWidget):
    """Canvas for displaying source images and selecting rectangular regions"""
    
    selection_changed = Signal(object)  # QRect or None
    
    def __init__(self, parent):
        super().__init__(parent)
        self.pixmap = None
        self.zoom_factor = 1.0
        self.selection_rect = None
        self.is_dragging = False
        self.drag_start = None
        
        self.setMinimumSize(400, 300)
        self.setMouseTracking(True)
    
    def set_pixmap(self, pixmap: QPixmap):
        """Set the pixmap to display"""
        self.pixmap = pixmap
        self.update()
    
    def set_zoom(self, zoom_factor: float):
        """Set the zoom factor"""
        self.zoom_factor = zoom_factor
        self.update()
    
    def clear_selection(self):
        """Clear the current selection"""
        self.selection_rect = None
        self.selection_changed.emit(None)
        self.update()
    
    def zoom_in(self):
        """Zoom in"""
        self.zoom_factor *= 1.2
        self.update()
    
    def zoom_out(self):
        """Zoom out"""
        self.zoom_factor /= 1.2
        self.update()
    
    def zoom_fit(self):
        """Fit image to canvas"""
        if not self.pixmap:
            return
        
        canvas_size = self.size()
        pixmap_size = self.pixmap.size()
        
        scale_x = canvas_size.width() / pixmap_size.width()
        scale_y = canvas_size.height() / pixmap_size.height()
        
        self.zoom_factor = min(scale_x, scale_y) * 0.9  # Leave some margin
        self.update()
    
    def canvas_to_source_rect(self, canvas_rect: QRect) -> QRect:
        """Convert canvas coordinates to source image coordinates"""
        if not self.pixmap:
            return QRect()
        
        # Calculate the displayed pixmap rectangle
        pixmap_size = self.pixmap.size()
        canvas_size = self.size()
        
        # Center the pixmap
        scaled_width = int(pixmap_size.width() * self.zoom_factor)
        scaled_height = int(pixmap_size.height() * self.zoom_factor)
        
        x_offset = (canvas_size.width() - scaled_width) // 2
        y_offset = (canvas_size.height() - scaled_height) // 2
        
        # Convert canvas coordinates to source coordinates
        source_x = int((canvas_rect.x() - x_offset) / self.zoom_factor)
        source_y = int((canvas_rect.y() - y_offset) / self.zoom_factor)
        source_width = int(canvas_rect.width() / self.zoom_factor)
        source_height = int(canvas_rect.height() / self.zoom_factor)
        
        return QRect(source_x, source_y, source_width, source_height)
    
    def paintEvent(self, event):
        """Paint the canvas"""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        # Fill background
        painter.fillRect(self.rect(), Qt.lightGray)
        
        if not self.pixmap:
            # Draw placeholder text
            painter.setPen(Qt.darkGray)
            painter.setFont(QFont("Arial", 16))
            painter.drawText(self.rect(), Qt.AlignCenter, "No image loaded")
            return
        
        # Draw the pixmap centered and scaled
        pixmap_size = self.pixmap.size()
        canvas_size = self.size()
        
        scaled_width = int(pixmap_size.width() * self.zoom_factor)
        scaled_height = int(pixmap_size.height() * self.zoom_factor)
        
        x_offset = (canvas_size.width() - scaled_width) // 2
        y_offset = (canvas_size.height() - scaled_height) // 2
        
        scaled_rect = QRect(x_offset, y_offset, scaled_width, scaled_height)
        painter.drawPixmap(scaled_rect, self.pixmap)
        
        # Draw selection rectangle
        if self.selection_rect and self.selection_rect.isValid():
            painter.setPen(QPen(Qt.red, 2, Qt.SolidLine))
            painter.setBrush(QBrush(Qt.red, Qt.NoBrush))
            painter.drawRect(self.selection_rect)
    
    def mousePressEvent(self, event):
        """Handle mouse press events"""
        if event.button() == Qt.LeftButton:
            self.is_dragging = True
            self.drag_start = event.pos()
            self.selection_rect = QRect()
    
    def mouseMoveEvent(self, event):
        """Handle mouse move events"""
        if self.is_dragging and self.drag_start:
            # Update selection rectangle
            self.selection_rect = QRect(
                min(self.drag_start.x(), event.x()),
                min(self.drag_start.y(), event.y()),
                abs(event.x() - self.drag_start.x()),
                abs(event.y() - self.drag_start.y())
            )
            self.update()
    
    def mouseReleaseEvent(self, event):
        """Handle mouse release events"""
        if event.button() == Qt.LeftButton and self.is_dragging:
            self.is_dragging = False
            
            if self.selection_rect and self.selection_rect.width() > 5 and self.selection_rect.height() > 5:
                self.selection_changed.emit(self.selection_rect)
            else:
                self.clear_selection()
