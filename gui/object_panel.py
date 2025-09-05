"""
Object management panel
"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
    QPushButton, QLineEdit, QComboBox, QListWidget,
    QListWidgetItem, QGroupBox, QMessageBox, QDialog,
    QDialogButtonBox, QFormLayout
)
from PySide6.QtCore import Qt, Signal
from typing import Optional

from curioshelf.models import CurioObject, Template


class ObjectPanel(QWidget):
    """Panel for managing objects and their slices"""
    
    # Signals
    object_selected = Signal(CurioObject)
    slice_selected = Signal(str)  # slice name
    
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
        
        # Objects group
        objects_group = QGroupBox("Objects")
        objects_layout = QVBoxLayout(objects_group)
        
        # Object controls
        object_controls = QHBoxLayout()
        
        self.object_name_input = QLineEdit()
        self.object_name_input.setPlaceholderText("Object name...")
        object_controls.addWidget(self.object_name_input)
        
        self.template_combo = QComboBox()
        self.template_combo.addItem("No Template", None)
        object_controls.addWidget(self.template_combo)
        
        self.create_object_btn = QPushButton("Create")
        self.create_object_btn.clicked.connect(self.create_object)
        object_controls.addWidget(self.create_object_btn)
        
        objects_layout.addLayout(object_controls)
        
        # Objects list
        self.objects_list = QListWidget()
        self.objects_list.itemClicked.connect(self.on_object_selected)
        objects_layout.addWidget(self.objects_list)
        
        # Object actions
        object_actions = QHBoxLayout()
        
        self.delete_object_btn = QPushButton("Delete")
        self.delete_object_btn.clicked.connect(self.delete_object)
        self.delete_object_btn.setEnabled(False)
        object_actions.addWidget(self.delete_object_btn)
        
        object_actions.addStretch()
        
        objects_layout.addLayout(object_actions)
        
        layout.addWidget(objects_group)
        
        # Slices group
        slices_group = QGroupBox("Slices")
        slices_layout = QVBoxLayout(slices_group)
        
        # Slices list
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
        
        layout.addWidget(slices_group)
        
        # Template compliance group
        compliance_group = QGroupBox("Template Compliance")
        compliance_layout = QVBoxLayout(compliance_group)
        
        self.compliance_list = QListWidget()
        compliance_layout.addWidget(self.compliance_list)
        
        layout.addWidget(compliance_group)
        
        # Refresh templates
        self.refresh_templates()
    
    def refresh(self):
        """Refresh the object list"""
        self.objects_list.clear()
        
        for obj in self.asset_manager.objects.values():
            item = QListWidgetItem(obj.name)
            item.setData(Qt.UserRole, obj.id)
            self.objects_list.addItem(item)
    
    def refresh_templates(self):
        """Refresh the template combo box"""
        self.template_combo.clear()
        self.template_combo.addItem("No Template", None)
        
        for template in self.asset_manager.templates.values():
            self.template_combo.addItem(template.name, template.name)
    
    def create_object(self):
        """Create a new object"""
        name = self.object_name_input.text().strip()
        if not name:
            QMessageBox.warning(self, "Error", "Please enter an object name")
            return
        
        template_name = self.template_combo.currentData()
        
        # Check if object name already exists
        for obj in self.asset_manager.objects.values():
            if obj.name.lower() == name.lower():
                QMessageBox.warning(self, "Error", "An object with this name already exists")
                return
        
        # Create the object
        obj = self.asset_manager.add_object(name, template_name)
        
        # Clear input and refresh
        self.object_name_input.clear()
        self.refresh()
        
        # Select the new object
        for i in range(self.objects_list.count()):
            item = self.objects_list.item(i)
            if item.data(Qt.UserRole) == obj.id:
                self.objects_list.setCurrentItem(item)
                self.on_object_selected(item)
                break
    
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
            # Remove from asset manager
            if self.current_object.id in self.asset_manager.objects:
                del self.asset_manager.objects[self.current_object.id]
            
            # Clear current object and refresh
            self.current_object = None
            self.refresh()
            self.refresh_slices()
            self.refresh_compliance()
            
            self.delete_object_btn.setEnabled(False)
    
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
    
    def on_object_selected(self, item):
        """Handle object selection"""
        object_id = item.data(Qt.UserRole)
        self.current_object = self.asset_manager.objects.get(object_id)
        
        if self.current_object:
            self.delete_object_btn.setEnabled(True)
            self.object_selected.emit(self.current_object)
            self.refresh_slices()
            self.refresh_compliance()
        else:
            self.delete_object_btn.setEnabled(False)
    
    def on_slice_selected(self, item):
        """Handle slice selection"""
        if item:
            slice_name = item.text()
            self.slice_selected.emit(slice_name)
            self.delete_slice_btn.setEnabled(True)
        else:
            self.delete_slice_btn.setEnabled(False)
    
    def refresh_slices(self):
        """Refresh the slices list for the current object"""
        self.slices_list.clear()
        
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
    
    def refresh_compliance(self):
        """Refresh the template compliance list"""
        self.compliance_list.clear()
        
        if not self.current_object or not self.current_object.template_name:
            return
        
        template = self.asset_manager.templates.get(self.current_object.template_name)
        if not template:
            return
        
        # Get completeness status
        completeness = self.asset_manager.get_object_completeness(self.current_object.id)
        
        for view in template.required_views:
            is_complete = completeness.get(view, False)
            
            item = QListWidgetItem(f"{'✓' if is_complete else '✗'} {view}")
            if is_complete:
                item.setBackground(Qt.green)
            else:
                item.setBackground(Qt.red)
            
            self.compliance_list.addItem(item)
    
    def add_slice_to_object(self, slice_obj):
        """Add a slice to the current object"""
        if not self.current_object:
            # If no object is selected, show a message
            from PySide6.QtWidgets import QMessageBox
            QMessageBox.information(
                self, "No Object Selected", 
                "Please select an object first before creating slices."
            )
            return
        
        # Add to object's slices list
        self.current_object.slices.append(slice_obj)
        
        # Refresh displays
        self.refresh_slices()
        self.refresh_compliance()
