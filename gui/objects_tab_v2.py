"""
Objects tab for managing objects and creating slices for views

This version includes slice creation functionality moved from the sources tab,
establishing 1:1 correspondence between object views and source slices.
"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
    QPushButton, QLineEdit, QComboBox, QListWidget,
    QListWidgetItem, QGroupBox, QMessageBox, QDialog,
    QDialogButtonBox, QFormLayout, QSplitter, QScrollArea,
    QFrame, QGridLayout, QProgressBar
)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QFont, QPalette, QColor, QPainter, QPen, QBrush, QPixmap
from typing import Optional

from curioshelf.models import CurioObject, Template, AssetSource, ObjectSlice
from curioshelf.business_logic_v2 import ObjectsController


class ObjectsTabV2(QWidget):
    """Tab for managing objects and creating slices for their views"""
    
    # Signals
    object_created = Signal(CurioObject)
    object_updated = Signal(CurioObject)
    object_deleted = Signal(str)  # object id
    slice_created = Signal(ObjectSlice)
    
    def __init__(self, asset_manager):
        super().__init__()
        self.asset_manager = asset_manager
        self.current_object = None
        self.current_source = None
        
        # Create business logic controller
        from curioshelf.ui_mocks import MockUIFactory
        self.controller = ObjectsController(asset_manager, MockUIFactory)
        
        self.init_ui()
        self.refresh()
    
    def init_ui(self):
        """Initialize the user interface"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(5, 5, 5, 5)
        
        # Top controls
        controls_layout = QHBoxLayout()
        
        # Create object button
        self.create_object_btn = QPushButton("Create Object")
        self.create_object_btn.clicked.connect(self.create_object)
        controls_layout.addWidget(self.create_object_btn)
        
        # Object search
        controls_layout.addWidget(QLabel("Search:"))
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Search objects...")
        self.search_input.textChanged.connect(self.on_search_changed)
        controls_layout.addWidget(self.search_input)
        
        controls_layout.addStretch()
        
        # Object count
        self.object_count_label = QLabel("0 objects")
        controls_layout.addWidget(self.object_count_label)
        
        layout.addLayout(controls_layout)
        
        # Main content area
        splitter = QSplitter(Qt.Horizontal)
        layout.addWidget(splitter)
        
        # Left panel - object list
        left_panel = QWidget()
        left_layout = QVBoxLayout(left_panel)
        left_layout.setContentsMargins(0, 0, 0, 0)
        
        # Objects group
        objects_group = QGroupBox("Objects")
        objects_layout = QVBoxLayout(objects_group)
        
        self.objects_list = QListWidget()
        self.objects_list.itemClicked.connect(self.on_object_selected)
        objects_layout.addWidget(self.objects_list)
        
        # Object actions
        object_actions = QHBoxLayout()
        
        self.edit_object_btn = QPushButton("Edit")
        self.edit_object_btn.clicked.connect(self.edit_object)
        self.edit_object_btn.setEnabled(False)
        object_actions.addWidget(self.edit_object_btn)
        
        self.delete_object_btn = QPushButton("Delete")
        self.delete_object_btn.clicked.connect(self.delete_object)
        self.delete_object_btn.setEnabled(False)
        object_actions.addWidget(self.delete_object_btn)
        
        object_actions.addStretch()
        
        objects_layout.addLayout(object_actions)
        left_layout.addWidget(objects_group)
        
        # Right panel - object details and slice creation
        right_panel = QWidget()
        right_layout = QVBoxLayout(right_panel)
        right_layout.setContentsMargins(0, 0, 0, 0)
        
        # Object details group
        details_group = QGroupBox("Object Details")
        details_layout = QVBoxLayout(details_group)
        
        self.object_name_label = QLabel("No object selected")
        self.object_name_label.setFont(QFont("Arial", 12, QFont.Bold))
        details_layout.addWidget(self.object_name_label)
        
        self.object_template_label = QLabel("")
        details_layout.addWidget(self.object_template_label)
        
        # Template compliance
        compliance_group = QGroupBox("Template Compliance")
        compliance_layout = QVBoxLayout(compliance_group)
        
        self.compliance_progress = QProgressBar()
        self.compliance_progress.setVisible(False)
        compliance_layout.addWidget(self.compliance_progress)
        
        self.compliance_scroll = QScrollArea()
        self.compliance_scroll.setMaximumHeight(150)
        self.compliance_scroll.setWidgetResizable(True)
        compliance_layout.addWidget(self.compliance_scroll)
        
        self.compliance_widget = QWidget()
        self.compliance_layout = QVBoxLayout(self.compliance_widget)
        self.compliance_scroll.setWidget(self.compliance_widget)
        
        details_layout.addWidget(compliance_group)
        
        # Slice creation group
        slice_group = QGroupBox("Create Slices for Views")
        slice_layout = QVBoxLayout(slice_group)
        
        # Source selection for slice creation
        source_layout = QHBoxLayout()
        source_layout.addWidget(QLabel("Source:"))
        self.source_combo = QComboBox()
        self.source_combo.currentTextChanged.connect(self.on_source_selected)
        source_layout.addWidget(self.source_combo)
        
        # Layer selection
        source_layout.addWidget(QLabel("Layer:"))
        self.layer_combo = QComboBox()
        self.layer_combo.addItems(["concept", "working", "production"])
        source_layout.addWidget(self.layer_combo)
        
        slice_layout.addLayout(source_layout)
        
        # Canvas for slice creation
        self.canvas = SliceCanvas()
        self.canvas.setMinimumSize(400, 300)
        self.canvas.setStyleSheet("border: 1px solid #ccc; background-color: #f0f0f0;")
        self.canvas.selection_changed.connect(self.on_selection_changed)
        
        # Scroll area for canvas
        canvas_scroll = QScrollArea()
        canvas_scroll.setWidget(self.canvas)
        canvas_scroll.setWidgetResizable(True)
        slice_layout.addWidget(canvas_scroll)
        
        # Views list and slice creation controls
        views_layout = QHBoxLayout()
        
        # Views list
        views_group = QGroupBox("Required Views")
        views_group_layout = QVBoxLayout(views_group)
        
        self.views_list = QListWidget()
        self.views_list.itemClicked.connect(self.on_view_selected)
        views_group_layout.addWidget(self.views_list)
        
        views_layout.addWidget(views_group)
        
        # Slice creation controls
        slice_controls_group = QGroupBox("Slice Creation")
        slice_controls_layout = QVBoxLayout(slice_controls_group)
        
        # Selection info
        self.selection_info_label = QLabel("No selection")
        slice_controls_layout.addWidget(self.selection_info_label)
        
        # Slice creation buttons
        slice_buttons_layout = QHBoxLayout()
        
        self.create_slice_btn = QPushButton("Create Slice for Selected View")
        self.create_slice_btn.clicked.connect(self.create_slice)
        self.create_slice_btn.setEnabled(False)
        slice_buttons_layout.addWidget(self.create_slice_btn)
        
        self.clear_selection_btn = QPushButton("Clear Selection")
        self.clear_selection_btn.clicked.connect(self.clear_selection)
        slice_buttons_layout.addWidget(self.clear_selection_btn)
        
        slice_controls_layout.addLayout(slice_buttons_layout)
        
        views_layout.addWidget(slice_controls_group)
        
        slice_layout.addLayout(views_layout)
        
        details_layout.addWidget(slice_group)
        
        right_layout.addWidget(details_group)
        
        # Add panels to splitter
        splitter.addWidget(left_panel)
        splitter.addWidget(right_panel)
        
        # Set splitter proportions
        splitter.setSizes([300, 700])
    
    def refresh(self):
        """Refresh the UI with current data"""
        self.refresh_objects_list()
        self.refresh_sources_combo()
        self.update_object_count()
        if self.current_object:
            self.refresh_object_details()
    
    def refresh_objects_list(self):
        """Refresh the objects list"""
        self.objects_list.clear()
        
        search_text = self.search_input.text().lower()
        
        for obj in self.asset_manager.objects.values():
            if not search_text or search_text in obj.name.lower():
                item = QListWidgetItem(obj.name)
                item.setData(Qt.UserRole, obj.id)
                self.objects_list.addItem(item)
    
    def refresh_sources_combo(self):
        """Refresh the sources combo box"""
        self.source_combo.clear()
        for source in self.asset_manager.sources.values():
            display_text = f"{source.file_path.name} ({source.width}x{source.height})"
            self.source_combo.addItem(display_text)
    
    def update_object_count(self):
        """Update the object count label"""
        count = len(self.asset_manager.objects)
        self.object_count_label.setText(f"{count} object{'s' if count != 1 else ''}")
    
    def on_search_changed(self):
        """Handle search text changes"""
        self.refresh_objects_list()
    
    def on_object_selected(self, item: QListWidgetItem):
        """Handle object selection"""
        object_id = item.data(Qt.UserRole)
        self.current_object = self.asset_manager.objects.get(object_id)
        
        if self.current_object:
            self.edit_object_btn.setEnabled(True)
            self.delete_object_btn.setEnabled(True)
            self.refresh_object_details()
        else:
            self.edit_object_btn.setEnabled(False)
            self.delete_object_btn.setEnabled(False)
    
    def refresh_object_details(self):
        """Refresh the object details display"""
        if not self.current_object:
            self.object_name_label.setText("No object selected")
            self.object_template_label.setText("")
            self.compliance_progress.setVisible(False)
            self.views_list.clear()
            return
        
        self.object_name_label.setText(self.current_object.name)
        
        if self.current_object.template_name:
            template = self.asset_manager.templates.get(self.current_object.template_name)
            if template:
                self.object_template_label.setText(f"Template: {template.name}")
            else:
                self.object_template_label.setText("Template: Unknown")
        else:
            self.object_template_label.setText("No template assigned")
        
        # Refresh compliance and views
        self.refresh_compliance()
        self.refresh_views()
    
    def refresh_compliance(self):
        """Refresh the template compliance display"""
        if not self.current_object or not self.current_object.template_name:
            self.compliance_progress.setVisible(False)
            return
        
        template = self.asset_manager.templates.get(self.current_object.template_name)
        if not template:
            self.compliance_progress.setVisible(False)
            return
        
        # Get completeness status
        completeness = self.asset_manager.get_object_completeness(self.current_object.id)
        
        # Calculate progress
        total_views = len(template.required_views)
        completed_views = sum(1 for is_complete in completeness.values() if is_complete)
        progress = int((completed_views / total_views) * 100) if total_views > 0 else 0
        
        self.compliance_progress.setValue(progress)
        self.compliance_progress.setVisible(True)
        
        # Clear existing compliance widgets
        for i in reversed(range(self.compliance_layout.count())):
            child = self.compliance_layout.itemAt(i).widget()
            if child:
                child.setParent(None)
        
        # Add compliance widgets for each view
        for view_name in template.required_views:
            is_complete = completeness.get(view_name, False)
            
            view_item = QFrame()
            view_item.setFrameStyle(QFrame.Box)
            view_item.setStyleSheet("QFrame { background-color: #f0f0f0; margin: 2px; }")
            
            view_layout = QHBoxLayout(view_item)
            view_layout.setContentsMargins(8, 4, 8, 4)
            
            # View name
            view_label = QLabel(view_name)
            view_label.setFont(QFont("Arial", 10, QFont.Bold))
            view_layout.addWidget(view_label)
            
            # Status
            status_label = QLabel("✓ Complete" if is_complete else "✗ Missing")
            status_label.setStyleSheet("color: green;" if is_complete else "color: red;")
            view_layout.addWidget(status_label)
            
            view_layout.addStretch()
            
            self.compliance_layout.addWidget(view_item)
        
        self.compliance_layout.addStretch()
    
    def refresh_views(self):
        """Refresh the views list for the current object"""
        self.views_list.clear()
        
        if not self.current_object:
            return
        
        # Get template for this object
        template = None
        if self.current_object.template_name:
            template = self.asset_manager.templates.get(self.current_object.template_name)
        
        if not template:
            self.views_list.addItem("No template assigned")
            return
        
        # Group slices by view name
        slices_by_view = {}
        for slice_obj in self.current_object.slices:
            view_name = slice_obj.name  # In the new model, slice name = view name
            if view_name not in slices_by_view:
                slices_by_view[view_name] = []
            slices_by_view[view_name].append(slice_obj)
        
        # Add views from template
        for view_name in template.required_views:
            if view_name in slices_by_view:
                # View has slices
                slice_count = len(slices_by_view[view_name])
                status = f"✓ {slice_count} slice(s)"
                item = QListWidgetItem(f"{view_name}: {status}")
                item.setData(Qt.UserRole, view_name)
                self.views_list.addItem(item)
            else:
                # View is missing
                item = QListWidgetItem(f"{view_name}: ✗ Missing")
                item.setData(Qt.UserRole, view_name)
                self.views_list.addItem(item)
    
    def on_source_selected(self, display_text: str):
        """Handle source selection for slice creation"""
        if not display_text:
            return
        
        # Find the source by display text
        for source in self.asset_manager.sources.values():
            expected_text = f"{source.file_path.name} ({source.width}x{source.height})"
            if display_text == expected_text:
                self.current_source = source
                self.load_source(source)
                break
    
    def load_source(self, source: AssetSource):
        """Load a source image into the canvas"""
        # For now, create a mock pixmap
        # In a real implementation, this would load the actual image
        pixmap = QPixmap(source.width, source.height)
        pixmap.fill(Qt.lightGray)
        
        self.canvas.set_pixmap(pixmap)
        self.canvas.set_zoom(1.0)
    
    def on_view_selected(self, item: QListWidgetItem):
        """Handle view selection"""
        view_name = item.data(Qt.UserRole)
        if view_name:
            self.selection_info_label.setText(f"Selected view: {view_name}")
    
    def on_selection_changed(self, rect):
        """Handle selection changes from the canvas"""
        if rect and hasattr(rect, 'isValid') and rect.isValid():
            self.create_slice_btn.setEnabled(True)
            self.selection_info_label.setText(f"Selection: {rect.width}x{rect.height} at ({rect.x}, {rect.y})")
        else:
            self.create_slice_btn.setEnabled(False)
            self.selection_info_label.setText("No selection")
    
    def create_slice(self):
        """Create a slice for the selected view"""
        if not self.current_object or not self.current_source:
            QMessageBox.warning(self, "Error", "Please select an object and source")
            return
        
        # Get the selected view
        current_item = self.views_list.currentItem()
        if not current_item:
            QMessageBox.warning(self, "Error", "Please select a view to create a slice for")
            return
        
        view_name = current_item.data(Qt.UserRole)
        if not view_name:
            QMessageBox.warning(self, "Error", "Invalid view selection")
            return
        
        # Get the selection from canvas
        selection = self.canvas.get_selection()
        if not selection or not hasattr(selection, 'isValid') or not selection.isValid():
            QMessageBox.warning(self, "Error", "Please make a selection on the canvas")
            return
        
        # Create the slice
        slice_obj = ObjectSlice(
            name=view_name,  # Slice name = view name for 1:1 correspondence
            source_id=self.current_source.id,
            x=selection.x,
            y=selection.y,
            width=selection.width,
            height=selection.height,
            layer=self.layer_combo.currentText()
        )
        
        # Add to source
        self.current_source.add_slice(slice_obj)
        
        # Add to object
        self.current_object.slices.append(slice_obj)
        
        # Emit signal
        self.slice_created.emit(slice_obj)
        
        # Clear selection and refresh
        self.clear_selection()
        self.refresh_object_details()
        
        QMessageBox.information(self, "Success", f"Slice for view '{view_name}' created successfully!")
    
    def clear_selection(self):
        """Clear the canvas selection"""
        self.canvas.clear_selection()
        self.create_slice_btn.setEnabled(False)
        self.selection_info_label.setText("No selection")
    
    def create_object(self):
        """Create a new object"""
        dialog = ObjectDialog(self.asset_manager)
        if dialog.exec() == QDialog.Accepted:
            name, template_name = dialog.get_object_data()
            
            if name:
                obj = self.asset_manager.add_object(name, template_name)
                
                # Refresh and select the new object
                self.refresh()
                for i in range(self.objects_list.count()):
                    item = self.objects_list.item(i)
                    if item.data(Qt.UserRole) == obj.id:
                        self.objects_list.setCurrentItem(item)
                        break
                
                self.object_created.emit(obj)
    
    def edit_object(self):
        """Edit the selected object"""
        if not self.current_object:
            return
        
        dialog = ObjectDialog(self.asset_manager, self.current_object.name, self.current_object.template_name)
        if dialog.exec() == QDialog.Accepted:
            name, template_name = dialog.get_object_data()
            
            if name:
                self.current_object.name = name
                self.current_object.template_name = template_name
                
                self.refresh_object_details()
                self.object_updated.emit(self.current_object)
    
    def delete_object(self):
        """Delete the selected object"""
        if not self.current_object:
            return
        
        reply = QMessageBox.question(
            self,
            "Delete Object",
            f"Are you sure you want to delete '{self.current_object.name}'?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            object_id = self.current_object.id
            
            # Remove from asset manager
            if object_id in self.asset_manager.objects:
                del self.asset_manager.objects[object_id]
            
            # Clear current object and refresh
            self.current_object = None
            self.refresh()
            self.refresh_object_details()
            
            self.object_deleted.emit(object_id)


class SliceCanvas(QWidget):
    """Canvas for slice creation with selection"""
    
    selection_changed = Signal(object)
    
    def __init__(self):
        super().__init__()
        self.pixmap = None
        self.zoom_factor = 1.0
        self.selection_rect = None
        self.drawing = False
        self.start_point = None
    
    def set_pixmap(self, pixmap: QPixmap):
        """Set the image to display"""
        self.pixmap = pixmap
        self.update()
    
    def set_zoom(self, zoom_factor: float):
        """Set the zoom factor"""
        self.zoom_factor = zoom_factor
        self.update()
    
    def get_selection(self):
        """Get the current selection"""
        return self.selection_rect
    
    def clear_selection(self):
        """Clear the current selection"""
        self.selection_rect = None
        self.update()
        self.selection_changed.emit(None)
    
    def mousePressEvent(self, event):
        """Handle mouse press for selection"""
        if event.button() == Qt.LeftButton:
            self.drawing = True
            self.start_point = event.pos()
            self.selection_rect = None
            self.update()
    
    def mouseMoveEvent(self, event):
        """Handle mouse move for selection"""
        if self.drawing and self.start_point:
            self.selection_rect = self.start_point.x(), self.start_point.y(), event.pos().x() - self.start_point.x(), event.pos().y() - self.start_point.y()
            self.update()
    
    def mouseReleaseEvent(self, event):
        """Handle mouse release for selection"""
        if event.button() == Qt.LeftButton and self.drawing:
            self.drawing = False
            if self.selection_rect:
                # Convert to a simple rect object for compatibility
                class SimpleRect:
                    def __init__(self, x, y, w, h):
                        self.x = x
                        self.y = y
                        self.width = w
                        self.height = h
                    
                    def isValid(self):
                        return self.width > 0 and self.height > 0
                
                rect = SimpleRect(*self.selection_rect)
                self.selection_changed.emit(rect)
    
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
        
        # Draw selection rectangle
        if self.selection_rect:
            x, y, w, h = self.selection_rect
            painter.setPen(QPen(Qt.red, 2, Qt.DashLine))
            painter.setBrush(QBrush(Qt.red, Qt.DiagCrossPattern))
            painter.drawRect(x, y, w, h)
    
    def sizeHint(self):
        """Return the preferred size"""
        if self.pixmap and not self.pixmap.isNull():
            return self.pixmap.size() * self.zoom_factor
        return super().sizeHint()


class ObjectDialog(QDialog):
    """Dialog for creating/editing objects"""
    
    def __init__(self, asset_manager, name="", template_name=""):
        super().__init__()
        self.asset_manager = asset_manager
        self.setWindowTitle("Object")
        self.setModal(True)
        self.resize(300, 150)
        
        layout = QVBoxLayout(self)
        
        # Form layout
        form_layout = QFormLayout()
        
        self.name_input = QLineEdit(name)
        self.name_input.setPlaceholderText("Enter object name...")
        form_layout.addRow("Name:", self.name_input)
        
        self.template_combo = QComboBox()
        self.template_combo.addItem("No Template", "")
        for template in self.asset_manager.templates.values():
            self.template_combo.addItem(template.name, template.name)
        
        # Select current template
        if template_name:
            for i in range(self.template_combo.count()):
                if self.template_combo.itemData(i) == template_name:
                    self.template_combo.setCurrentIndex(i)
                    break
        
        form_layout.addRow("Template:", self.template_combo)
        
        layout.addLayout(form_layout)
        
        # Buttons
        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)
    
    def get_object_data(self):
        """Get the object data from the dialog"""
        name = self.name_input.text().strip()
        template_name = self.template_combo.currentData()
        return name, template_name
