"""
Canvas widget for displaying and selecting regions from source images
"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
    QPushButton, QLineEdit, QComboBox, QSpinBox,
    QGroupBox, QMessageBox
)
from PySide6.QtCore import Qt, Signal, QRect
from PySide6.QtGui import QPainter, QPen, QBrush, QPixmap, QFont
from typing import Optional, Tuple
from pathlib import Path

from curioshelf.models import AssetSource, ObjectSlice


class CanvasWidget(QWidget):
    """Widget for displaying source images and selecting rectangular regions"""
    
    # Signals
    slice_created = Signal(ObjectSlice)
    
    def __init__(self, asset_manager):
        super().__init__()
        self.asset_manager = asset_manager
        self.current_source = None
        self.current_pixmap = None
        self.zoom_factor = 1.0
        self.selection_start = None
        self.selection_end = None
        self.is_selecting = False
        
        self.init_ui()
    
    def init_ui(self):
        """Initialize the user interface"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(5, 5, 5, 5)
        
        # Controls panel
        controls_layout = QHBoxLayout()
        
        # Slice name input
        controls_layout.addWidget(QLabel("Slice Name:"))
        self.slice_name_input = QLineEdit()
        self.slice_name_input.setPlaceholderText("Enter slice name...")
        controls_layout.addWidget(self.slice_name_input)
        
        # Layer selection
        controls_layout.addWidget(QLabel("Layer:"))
        self.layer_combo = QComboBox()
        self.layer_combo.addItems(["concept", "working", "production"])
        controls_layout.addWidget(self.layer_combo)
        
        # Create slice button
        self.create_slice_btn = QPushButton("Create Slice")
        self.create_slice_btn.clicked.connect(self.create_slice)
        self.create_slice_btn.setEnabled(False)
        controls_layout.addWidget(self.create_slice_btn)
        
        # Clear selection button
        self.clear_selection_btn = QPushButton("Clear Selection")
        self.clear_selection_btn.clicked.connect(self.clear_selection)
        controls_layout.addWidget(self.clear_selection_btn)
        
        controls_layout.addStretch()
        
        # Zoom controls
        controls_layout.addWidget(QLabel("Zoom:"))
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
        
        # Canvas area
        self.canvas = CanvasArea(self)
        self.canvas.selection_changed.connect(self.on_selection_changed)
        layout.addWidget(self.canvas)
        
        # Instructions
        instructions = QLabel(
            "Click and drag to select a rectangular region, then enter a name and click 'Create Slice'"
        )
        instructions.setStyleSheet("color: gray; font-style: italic;")
        layout.addWidget(instructions)
    
    def load_source(self, source: AssetSource, file_path: str):
        """Load a source image into the canvas"""
        self.current_source = source
        self.current_pixmap = QPixmap(file_path)
        
        if self.current_pixmap.isNull():
            QMessageBox.warning(self, "Error", "Could not load the image file")
            return
        
        self.canvas.set_pixmap(self.current_pixmap)
        self.zoom_fit()
        self.clear_selection()
    
    def clear(self):
        """Clear the canvas"""
        self.current_source = None
        self.current_pixmap = None
        self.canvas.clear()
        self.clear_selection()
    
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
        
        # Emit signal
        self.slice_created.emit(slice_obj)
        
        # Clear selection and reset UI
        self.clear_selection()
        self.slice_name_input.clear()
        
        QMessageBox.information(self, "Success", f"Slice '{slice_name}' created successfully!")
    
    def clear_selection(self):
        """Clear the current selection"""
        self.canvas.clear_selection()
        self.create_slice_btn.setEnabled(False)
    
    def zoom_in(self):
        """Zoom in"""
        self.zoom_factor *= 1.2
        self.update_zoom()
    
    def zoom_out(self):
        """Zoom out"""
        self.zoom_factor /= 1.2
        self.update_zoom()
    
    def zoom_fit(self):
        """Fit image to canvas"""
        if not self.current_pixmap:
            return
        
        canvas_size = self.canvas.size()
        pixmap_size = self.current_pixmap.size()
        
        scale_x = canvas_size.width() / pixmap_size.width()
        scale_y = canvas_size.height() / pixmap_size.height()
        
        self.zoom_factor = min(scale_x, scale_y) * 0.9  # Leave some margin
        self.update_zoom()
    
    def update_zoom(self):
        """Update zoom display and canvas"""
        self.zoom_label.setText(f"{int(self.zoom_factor * 100)}%")
        self.canvas.set_zoom(self.zoom_factor)
        self.canvas.update()


class CanvasArea(QWidget):
    """The actual canvas area for drawing and selection"""
    
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
    
    def clear(self):
        """Clear the pixmap"""
        self.pixmap = None
        self.selection_rect = None
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
