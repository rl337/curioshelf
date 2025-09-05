"""
Template management panel
"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
    QPushButton, QLineEdit, QListWidget, QListWidgetItem,
    QGroupBox, QMessageBox, QDialog, QDialogButtonBox,
    QFormLayout, QTextEdit, QListWidget as QListWidget2
)
from PySide6.QtCore import Qt, Signal
from typing import List

from curioshelf.models import Template


class TemplatePanel(QWidget):
    """Panel for managing templates"""
    
    # Signals
    template_selected = Signal(Template)
    
    def __init__(self, asset_manager):
        super().__init__()
        self.asset_manager = asset_manager
        self.current_template = None
        self.init_ui()
        self.refresh()
    
    def init_ui(self):
        """Initialize the user interface"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(5, 5, 5, 5)
        
        # Templates group
        templates_group = QGroupBox("Templates")
        templates_layout = QVBoxLayout(templates_group)
        
        # Template controls
        template_controls = QHBoxLayout()
        
        self.template_name_input = QLineEdit()
        self.template_name_input.setPlaceholderText("Template name...")
        template_controls.addWidget(self.template_name_input)
        
        self.create_template_btn = QPushButton("Create")
        self.create_template_btn.clicked.connect(self.create_template)
        template_controls.addWidget(self.create_template_btn)
        
        templates_layout.addLayout(template_controls)
        
        # Templates list
        self.templates_list = QListWidget()
        self.templates_list.itemClicked.connect(self.on_template_selected)
        templates_layout.addWidget(self.templates_list)
        
        # Template actions
        template_actions = QHBoxLayout()
        
        self.edit_template_btn = QPushButton("Edit")
        self.edit_template_btn.clicked.connect(self.edit_template)
        self.edit_template_btn.setEnabled(False)
        template_actions.addWidget(self.edit_template_btn)
        
        self.delete_template_btn = QPushButton("Delete")
        self.delete_template_btn.clicked.connect(self.delete_template)
        self.delete_template_btn.setEnabled(False)
        template_actions.addWidget(self.delete_template_btn)
        
        template_actions.addStretch()
        
        templates_layout.addLayout(template_actions)
        
        layout.addWidget(templates_group)
        
        # Template details group
        details_group = QGroupBox("Template Details")
        details_layout = QVBoxLayout(details_group)
        
        self.template_name_label = QLabel("No template selected")
        self.template_name_label.setStyleSheet("font-weight: bold;")
        details_layout.addWidget(self.template_name_label)
        
        self.template_description_label = QLabel("")
        details_layout.addWidget(self.template_description_label)
        
        self.required_views_label = QLabel("Required Views:")
        details_layout.addWidget(self.required_views_label)
        
        self.views_list = QListWidget()
        details_layout.addWidget(self.views_list)
        
        layout.addWidget(details_group)
    
    def refresh(self):
        """Refresh the template list"""
        self.templates_list.clear()
        
        for template in self.asset_manager.templates.values():
            item = QListWidgetItem(template.name)
            item.setData(Qt.UserRole, template.name)
            self.templates_list.addItem(item)
    
    def create_template(self):
        """Create a new template"""
        name = self.template_name_input.text().strip()
        if not name:
            QMessageBox.warning(self, "Error", "Please enter a template name")
            return
        
        # Check if template name already exists
        if name in self.asset_manager.templates:
            QMessageBox.warning(self, "Error", "A template with this name already exists")
            return
        
        # Open edit dialog
        dialog = TemplateEditDialog(name, "", [], self)
        if dialog.exec() == QDialog.Accepted:
            template_name, description, required_views = dialog.get_template_data()
            
            # Create the template
            template = self.asset_manager.add_template(template_name, description, required_views)
            
            # Clear input and refresh
            self.template_name_input.clear()
            self.refresh()
            
            # Select the new template
            for i in range(self.templates_list.count()):
                item = self.templates_list.item(i)
                if item.data(Qt.UserRole) == template.name:
                    self.templates_list.setCurrentItem(item)
                    self.on_template_selected(item)
                    break
    
    def edit_template(self):
        """Edit the selected template"""
        if not self.current_template:
            return
        
        dialog = TemplateEditDialog(
            self.current_template.name,
            self.current_template.description,
            self.current_template.required_views,
            self
        )
        
        if dialog.exec() == QDialog.Accepted:
            template_name, description, required_views = dialog.get_template_data()
            
            # Update the template
            self.current_template.name = template_name
            self.current_template.description = description
            self.current_template.required_views = required_views
            
            # Update in asset manager
            if template_name != self.current_template.name:
                # Name changed, need to update the key
                del self.asset_manager.templates[self.current_template.name]
                self.asset_manager.templates[template_name] = self.current_template
            
            self.refresh()
            self.refresh_details()
    
    def delete_template(self):
        """Delete the selected template"""
        if not self.current_template:
            return
        
        # Check if any objects are using this template
        using_objects = []
        for obj in self.asset_manager.objects.values():
            if obj.template_name == self.current_template.name:
                using_objects.append(obj.name)
        
        if using_objects:
            QMessageBox.warning(
                self, "Cannot Delete Template",
                f"This template is being used by the following objects:\n{', '.join(using_objects)}\n\nPlease change their template first."
            )
            return
        
        reply = QMessageBox.question(
            self, "Delete Template",
            f"Are you sure you want to delete template '{self.current_template.name}'?",
            QMessageBox.Yes | QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            # Remove from asset manager
            if self.current_template.name in self.asset_manager.templates:
                del self.asset_manager.templates[self.current_template.name]
            
            # Clear current template and refresh
            self.current_template = None
            self.refresh()
            self.refresh_details()
            
            self.edit_template_btn.setEnabled(False)
            self.delete_template_btn.setEnabled(False)
    
    def on_template_selected(self, item):
        """Handle template selection"""
        template_name = item.data(Qt.UserRole)
        self.current_template = self.asset_manager.templates.get(template_name)
        
        if self.current_template:
            self.edit_template_btn.setEnabled(True)
            self.delete_template_btn.setEnabled(True)
            self.template_selected.emit(self.current_template)
            self.refresh_details()
        else:
            self.edit_template_btn.setEnabled(False)
            self.delete_template_btn.setEnabled(False)
    
    def refresh_details(self):
        """Refresh the template details display"""
        if not self.current_template:
            self.template_name_label.setText("No template selected")
            self.template_description_label.setText("")
            self.views_list.clear()
            return
        
        self.template_name_label.setText(self.current_template.name)
        self.template_description_label.setText(self.current_template.description)
        
        # Refresh views list
        self.views_list.clear()
        for view in self.current_template.required_views:
            item = QListWidgetItem(view)
            self.views_list.addItem(item)


class TemplateEditDialog(QDialog):
    """Dialog for editing template details"""
    
    def __init__(self, name: str, description: str, required_views: List[str], parent=None):
        super().__init__(parent)
        self.setWindowTitle("Edit Template")
        self.setModal(True)
        self.resize(400, 300)
        
        layout = QVBoxLayout(self)
        
        # Form layout
        form_layout = QFormLayout()
        
        self.name_input = QLineEdit(name)
        form_layout.addRow("Name:", self.name_input)
        
        self.description_input = QTextEdit(description)
        self.description_input.setMaximumHeight(80)
        form_layout.addRow("Description:", self.description_input)
        
        layout.addLayout(form_layout)
        
        # Required views
        views_label = QLabel("Required Views:")
        layout.addWidget(views_label)
        
        views_layout = QHBoxLayout()
        
        self.views_list = QListWidget2()
        self.views_list.addItems(required_views)
        views_layout.addWidget(self.views_list)
        
        views_controls = QVBoxLayout()
        
        self.add_view_btn = QPushButton("Add")
        self.add_view_btn.clicked.connect(self.add_view)
        views_controls.addWidget(self.add_view_btn)
        
        self.remove_view_btn = QPushButton("Remove")
        self.remove_view_btn.clicked.connect(self.remove_view)
        views_controls.addWidget(self.remove_view_btn)
        
        views_controls.addStretch()
        views_layout.addLayout(views_controls)
        
        layout.addLayout(views_layout)
        
        # Dialog buttons
        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)
    
    def add_view(self):
        """Add a new required view"""
        from PySide6.QtWidgets import QInputDialog
        view_name, ok = QInputDialog.getText(self, "Add View", "Enter view name:")
        if ok and view_name.strip():
            view_name = view_name.strip()
            
            # Check if already exists
            for i in range(self.views_list.count()):
                if self.views_list.item(i).text() == view_name:
                    QMessageBox.warning(self, "Error", "This view already exists")
                    return
            
            self.views_list.addItem(view_name)
    
    def remove_view(self):
        """Remove the selected view"""
        current_item = self.views_list.currentItem()
        if current_item:
            self.views_list.takeItem(self.views_list.row(current_item))
    
    def get_template_data(self):
        """Get the template data from the dialog"""
        name = self.name_input.text().strip()
        description = self.description_input.toPlainText().strip()
        required_views = [self.views_list.item(i).text() for i in range(self.views_list.count())]
        
        return name, description, required_views
