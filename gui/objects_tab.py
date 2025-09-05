"""
Objects tab for managing objects and their slices
"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
    QPushButton, QLineEdit, QComboBox, QListWidget,
    QListWidgetItem, QGroupBox, QMessageBox, QDialog,
    QDialogButtonBox, QFormLayout, QSplitter, QScrollArea,
    QFrame, QGridLayout, QProgressBar
)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QFont, QPalette, QColor
from typing import Optional

from curioshelf.models import CurioObject, Template, AssetSource


class ObjectsTab(QWidget):
    """Tab for managing objects and their slices"""
    
    # Signals
    object_created = Signal(CurioObject)
    object_updated = Signal(CurioObject)
    object_deleted = Signal(str)  # object id
    
    def __init__(self, asset_manager):
        super().__init__()
        self.asset_manager = asset_manager
        self.current_object = None
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
        self.search_input.textChanged.connect(self.filter_objects)
        controls_layout.addWidget(self.search_input)
        
        controls_layout.addStretch()
        
        # Object count
        self.object_count_label = QLabel("0 objects")
        controls_layout.addWidget(self.object_count_label)
        
        layout.addLayout(controls_layout)
        
        # Main content with splitter
        splitter = QSplitter(Qt.Horizontal)
        layout.addWidget(splitter)
        
        # Left panel - object list
        left_panel = QWidget()
        left_layout = QVBoxLayout(left_panel)
        left_layout.setContentsMargins(0, 0, 0, 0)
        
        # Objects list
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
        
        # Right panel - object details
        right_panel = QWidget()
        right_layout = QVBoxLayout(right_panel)
        right_layout.setContentsMargins(0, 0, 0, 0)
        
        # Object details
        details_group = QGroupBox("Object Details")
        details_layout = QVBoxLayout(details_group)
        
        self.object_name_label = QLabel("No object selected")
        self.object_name_label.setStyleSheet("font-weight: bold; font-size: 16px;")
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
        self.compliance_scroll.setWidgetResizable(True)
        self.compliance_scroll.setMaximumHeight(200)
        compliance_layout.addWidget(self.compliance_scroll)
        
        self.compliance_widget = QWidget()
        self.compliance_layout = QVBoxLayout(self.compliance_widget)
        self.compliance_scroll.setWidget(self.compliance_widget)
        
        details_layout.addWidget(compliance_group)
        
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
        
        details_layout.addWidget(slices_group)
        
        right_layout.addWidget(details_group)
        
        # Add panels to splitter
        splitter.addWidget(left_panel)
        splitter.addWidget(right_panel)
        
        # Set splitter proportions
        splitter.setSizes([400, 1000])
    
    def refresh(self):
        """Refresh the object list"""
        self.objects_list.clear()
        
        for obj in self.asset_manager.objects.values():
            item = QListWidgetItem(obj.name)
            item.setData(Qt.UserRole, obj.id)
            self.objects_list.addItem(item)
        
        self.update_object_count()
    
    def update_object_count(self):
        """Update the object count label"""
        count = len(self.asset_manager.objects)
        self.object_count_label.setText(f"{count} object{'s' if count != 1 else ''}")
    
    def filter_objects(self, text):
        """Filter objects based on search text"""
        for i in range(self.objects_list.count()):
            item = self.objects_list.item(i)
            object_name = item.text()
            if text.lower() in object_name.lower():
                item.setHidden(False)
            else:
                item.setHidden(True)
    
    def create_object(self):
        """Create a new object"""
        dialog = ObjectEditDialog("", None, self.asset_manager, self)
        if dialog.exec() == QDialog.Accepted:
            name, template_name = dialog.get_object_data()
            
            # Create the object
            obj = self.asset_manager.add_object(name, template_name)
            
            # Refresh and select the new object
            self.refresh()
            for i in range(self.objects_list.count()):
                item = self.objects_list.item(i)
                if item.data(Qt.UserRole) == obj.id:
                    self.objects_list.setCurrentItem(item)
                    self.on_object_selected(item)
                    break
            
            # Emit signal
            self.object_created.emit(obj)
    
    def edit_object(self):
        """Edit the selected object"""
        if not self.current_object:
            return
        
        dialog = ObjectEditDialog(
            self.current_object.name,
            self.current_object.template_name,
            self.asset_manager,
            self
        )
        
        if dialog.exec() == QDialog.Accepted:
            name, template_name = dialog.get_object_data()
            
            # Update the object
            self.current_object.name = name
            self.current_object.template_name = template_name
            
            self.refresh()
            self.refresh_details()
            
            # Emit signal
            self.object_updated.emit(self.current_object)
    
    def delete_object(self):
        """Delete the selected object"""
        if not self.current_object:
            return
        
        reply = QMessageBox.question(
            self, "Delete Object",
            f"Are you sure you want to delete '{self.current_object.name}'?",
            QMessageBox.Yes | QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            object_id = self.current_object.id
            
            # Remove from asset manager
            if object_id in self.asset_manager.objects:
                del self.asset_manager.objects[object_id]
            
            # Clear current object and refresh
            self.current_object = None
            self.refresh()
            self.refresh_details()
            
            # Emit signal
            self.object_deleted.emit(object_id)
    
    def on_object_selected(self, item):
        """Handle object selection"""
        object_id = item.data(Qt.UserRole)
        self.current_object = self.asset_manager.objects.get(object_id)
        
        if self.current_object:
            self.edit_object_btn.setEnabled(True)
            self.delete_object_btn.setEnabled(True)
            self.refresh_details()
        else:
            self.edit_object_btn.setEnabled(False)
            self.delete_object_btn.setEnabled(False)
    
    def on_slice_selected(self, item):
        """Handle slice selection"""
        if item:
            self.delete_slice_btn.setEnabled(True)
        else:
            self.delete_slice_btn.setEnabled(False)
    
    def delete_slice(self):
        """Delete the selected slice"""
        if not self.current_object:
            return
        
        current_item = self.slices_list.currentItem()
        if not current_item:
            return
        
        slice_name = current_item.text()
        
        reply = QMessageBox.question(
            self, "Delete Slice",
            f"Are you sure you want to delete slice '{slice_name}'?",
            QMessageBox.Yes | QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            # Find and remove the slice
            for source in self.current_object.sources.values():
                if source.remove_slice(slice_name):
                    break
            
            # Remove from object's slices list
            self.current_object.slices = [
                s for s in self.current_object.slices if s.name != slice_name
            ]
            
            self.refresh_slices()
            self.refresh_compliance()
    
    def refresh_details(self):
        """Refresh the object details display"""
        if not self.current_object:
            self.object_name_label.setText("No object selected")
            self.object_template_label.setText("")
            self.clear_compliance()
            self.clear_slices()
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
        
        # Refresh compliance and slices
        self.refresh_compliance()
        self.refresh_slices()
    
    def clear_compliance(self):
        """Clear the compliance widget"""
        while self.compliance_layout.count():
            child = self.compliance_layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()
    
    def refresh_compliance(self):
        """Refresh the template compliance display"""
        self.clear_compliance()
        
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
        
        # Create compliance items
        for view in template.required_views:
            is_complete = completeness.get(view, False)
            
            # Create view item widget
            view_item = QFrame()
            view_item.setFrameStyle(QFrame.Box)
            
            if is_complete:
                view_item.setStyleSheet("""
                    QFrame {
                        background-color: #d4edda;
                        border: 2px solid #28a745;
                        border-radius: 4px;
                        padding: 4px;
                    }
                """)
                status_text = "✓ Complete"
            else:
                view_item.setStyleSheet("""
                    QFrame {
                        background-color: #f8d7da;
                        border: 2px solid #dc3545;
                        border-radius: 4px;
                        padding: 4px;
                    }
                """)
                status_text = "✗ Missing"
            
            view_layout = QHBoxLayout(view_item)
            view_layout.setContentsMargins(8, 4, 8, 4)
            
            # View name
            view_label = QLabel(view)
            view_label.setStyleSheet("font-weight: bold;")
            view_layout.addWidget(view_label)
            
            # Status
            status_label = QLabel(status_text)
            status_label.setStyleSheet("color: #666;")
            view_layout.addWidget(status_label)
            
            view_layout.addStretch()
            
            self.compliance_layout.addWidget(view_item)
        
        self.compliance_layout.addStretch()
    
    def clear_slices(self):
        """Clear the slices list"""
        self.slices_list.clear()
    
    def refresh_slices(self):
        """Refresh the slices list for the current object"""
        self.clear_slices()
        
        if not self.current_object:
            return
        
        # Group slices by layer
        slices_by_layer = {}
        for slice_obj in self.current_object.slices:
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
    
    def on_source_loaded(self, source: AssetSource):
        """Handle source loaded from other tabs"""
        self.refresh()
    
    def on_template_created(self, template: Template):
        """Handle template created from other tabs"""
        self.refresh()


class ObjectEditDialog(QDialog):
    """Dialog for editing object details"""
    
    def __init__(self, name: str, template_name: Optional[str], asset_manager, parent=None):
        super().__init__(parent)
        self.asset_manager = asset_manager
        self.setWindowTitle("Edit Object")
        self.setModal(True)
        self.resize(400, 200)
        
        layout = QVBoxLayout(self)
        
        # Form layout
        form_layout = QFormLayout()
        
        self.name_input = QLineEdit(name)
        form_layout.addRow("Name:", self.name_input)
        
        # Template selection
        self.template_combo = QComboBox()
        self.template_combo.addItem("No Template", None)
        for template in self.asset_manager.templates.values():
            self.template_combo.addItem(template.name, template.name)
        
        # Set current template
        if template_name:
            for i in range(self.template_combo.count()):
                if self.template_combo.itemData(i) == template_name:
                    self.template_combo.setCurrentIndex(i)
                    break
        
        form_layout.addRow("Template:", self.template_combo)
        
        layout.addLayout(form_layout)
        
        # Dialog buttons
        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)
    
    def get_object_data(self):
        """Get the object data from the dialog"""
        name = self.name_input.text().strip()
        template_name = self.template_combo.currentData()
        return name, template_name
