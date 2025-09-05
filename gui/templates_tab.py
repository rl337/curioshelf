"""
Templates tab for managing templates with visual representation
"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
    QPushButton, QLineEdit, QListWidget, QListWidgetItem,
    QGroupBox, QMessageBox, QDialog, QDialogButtonBox,
    QFormLayout, QTextEdit, QListWidget as QListWidget2,
    QScrollArea, QFrame, QGridLayout, QSizePolicy, QSplitter
)
from PySide6.QtCore import Qt, Signal, QSize
from PySide6.QtGui import QFont, QPalette, QColor
from typing import List

from curioshelf.models import Template


class TemplatesTab(QWidget):
    """Tab for managing templates with visual representation"""
    
    # Signals
    template_created = Signal(Template)
    template_updated = Signal(Template)
    template_deleted = Signal(str)  # template name
    
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
        
        # Top controls
        controls_layout = QHBoxLayout()
        
        # Create template button
        self.create_template_btn = QPushButton("Create Template")
        self.create_template_btn.clicked.connect(self.create_template)
        controls_layout.addWidget(self.create_template_btn)
        
        # Template search
        controls_layout.addWidget(QLabel("Search:"))
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Search templates...")
        self.search_input.textChanged.connect(self.filter_templates)
        controls_layout.addWidget(self.search_input)
        
        controls_layout.addStretch()
        
        # Template count
        self.template_count_label = QLabel("0 templates")
        controls_layout.addWidget(self.template_count_label)
        
        layout.addLayout(controls_layout)
        
        # Main content with splitter
        splitter = QSplitter(Qt.Horizontal)
        layout.addWidget(splitter)
        
        # Left panel - template list
        left_panel = QWidget()
        left_layout = QVBoxLayout(left_panel)
        left_layout.setContentsMargins(0, 0, 0, 0)
        
        # Templates list
        templates_group = QGroupBox("Templates")
        templates_layout = QVBoxLayout(templates_group)
        
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
        
        left_layout.addWidget(templates_group)
        
        # Right panel - template details
        right_panel = QWidget()
        right_layout = QVBoxLayout(right_panel)
        right_layout.setContentsMargins(0, 0, 0, 0)
        
        # Template details
        details_group = QGroupBox("Template Details")
        details_layout = QVBoxLayout(details_group)
        
        self.template_name_label = QLabel("No template selected")
        self.template_name_label.setStyleSheet("font-weight: bold; font-size: 16px;")
        details_layout.addWidget(self.template_name_label)
        
        self.template_description_label = QLabel("")
        self.template_description_label.setWordWrap(True)
        details_layout.addWidget(self.template_description_label)
        
        # Required views visualization
        views_group = QGroupBox("Required Views")
        views_layout = QVBoxLayout(views_group)
        
        self.views_scroll = QScrollArea()
        self.views_scroll.setWidgetResizable(True)
        self.views_scroll.setMaximumHeight(300)
        views_layout.addWidget(self.views_scroll)
        
        self.views_widget = QWidget()
        self.views_layout = QVBoxLayout(self.views_widget)
        self.views_scroll.setWidget(self.views_widget)
        
        details_layout.addWidget(views_group)
        
        # Usage statistics
        stats_group = QGroupBox("Usage Statistics")
        stats_layout = QVBoxLayout(stats_group)
        
        self.usage_label = QLabel("No usage data")
        stats_layout.addWidget(self.usage_label)
        
        details_layout.addWidget(stats_group)
        
        right_layout.addWidget(details_group)
        
        # Add panels to splitter
        splitter.addWidget(left_panel)
        splitter.addWidget(right_panel)
        
        # Set splitter proportions
        splitter.setSizes([400, 1000])
    
    def refresh(self):
        """Refresh the template list"""
        self.templates_list.clear()
        
        for template in self.asset_manager.templates.values():
            item = QListWidgetItem(template.name)
            item.setData(Qt.UserRole, template.name)
            self.templates_list.addItem(item)
        
        self.update_template_count()
    
    def update_template_count(self):
        """Update the template count label"""
        count = len(self.asset_manager.templates)
        self.template_count_label.setText(f"{count} template{'s' if count != 1 else ''}")
    
    def filter_templates(self, text):
        """Filter templates based on search text"""
        for i in range(self.templates_list.count()):
            item = self.templates_list.item(i)
            template_name = item.text()
            if text.lower() in template_name.lower():
                item.setHidden(False)
            else:
                item.setHidden(True)
    
    def create_template(self):
        """Create a new template"""
        dialog = TemplateEditDialog("", "", [], self)
        if dialog.exec() == QDialog.Accepted:
            template_name, description, required_views = dialog.get_template_data()
            
            # Create the template
            template = self.asset_manager.add_template(template_name, description, required_views)
            
            # Refresh and select the new template
            self.refresh()
            for i in range(self.templates_list.count()):
                item = self.templates_list.item(i)
                if item.data(Qt.UserRole) == template.name:
                    self.templates_list.setCurrentItem(item)
                    self.on_template_selected(item)
                    break
            
            # Emit signal
            self.template_created.emit(template)
    
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
            old_name = self.current_template.name
            self.current_template.name = template_name
            self.current_template.description = description
            self.current_template.required_views = required_views
            
            # Update in asset manager if name changed
            if template_name != old_name:
                del self.asset_manager.templates[old_name]
                self.asset_manager.templates[template_name] = self.current_template
            
            self.refresh()
            self.refresh_details()
            
            # Emit signal
            self.template_updated.emit(self.current_template)
    
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
            template_name = self.current_template.name
            
            # Remove from asset manager
            if template_name in self.asset_manager.templates:
                del self.asset_manager.templates[template_name]
            
            # Clear current template and refresh
            self.current_template = None
            self.refresh()
            self.refresh_details()
            
            # Emit signal
            self.template_deleted.emit(template_name)
    
    def on_template_selected(self, item):
        """Handle template selection"""
        template_name = item.data(Qt.UserRole)
        self.current_template = self.asset_manager.templates.get(template_name)
        
        if self.current_template:
            self.edit_template_btn.setEnabled(True)
            self.delete_template_btn.setEnabled(True)
            self.refresh_details()
        else:
            self.edit_template_btn.setEnabled(False)
            self.delete_template_btn.setEnabled(False)
    
    def refresh_details(self):
        """Refresh the template details display"""
        if not self.current_template:
            self.template_name_label.setText("No template selected")
            self.template_description_label.setText("")
            self.clear_views()
            self.usage_label.setText("No usage data")
            return
        
        self.template_name_label.setText(self.current_template.name)
        self.template_description_label.setText(self.current_template.description)
        
        # Refresh views visualization
        self.refresh_views()
        
        # Refresh usage statistics
        self.refresh_usage_stats()
    
    def clear_views(self):
        """Clear the views widget"""
        while self.views_layout.count():
            child = self.views_layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()
    
    def refresh_views(self):
        """Refresh the required views visualization"""
        self.clear_views()
        
        if not self.current_template:
            return
        
        # Create a grid layout for views
        grid_layout = QGridLayout()
        
        # Add view items
        for i, view in enumerate(self.current_template.required_views):
            # Create view item widget
            view_item = QFrame()
            view_item.setFrameStyle(QFrame.Box)
            view_item.setStyleSheet("""
                QFrame {
                    background-color: #e8f4f8;
                    border: 2px solid #4a90e2;
                    border-radius: 8px;
                    padding: 8px;
                }
            """)
            
            view_layout = QVBoxLayout(view_item)
            view_layout.setContentsMargins(8, 8, 8, 8)
            
            # View name
            view_label = QLabel(view)
            view_label.setStyleSheet("font-weight: bold; font-size: 14px;")
            view_label.setAlignment(Qt.AlignCenter)
            view_layout.addWidget(view_label)
            
            # View status (placeholder for now)
            status_label = QLabel("Required")
            status_label.setStyleSheet("color: #666; font-size: 12px;")
            status_label.setAlignment(Qt.AlignCenter)
            view_layout.addWidget(status_label)
            
            # Add to grid (3 columns)
            row = i // 3
            col = i % 3
            grid_layout.addWidget(view_item, row, col)
        
        # Add grid to views layout
        self.views_layout.addLayout(grid_layout)
        self.views_layout.addStretch()
    
    def refresh_usage_stats(self):
        """Refresh usage statistics"""
        if not self.current_template:
            return
        
        # Count objects using this template
        using_objects = []
        for obj in self.asset_manager.objects.values():
            if obj.template_name == self.current_template.name:
                using_objects.append(obj.name)
        
        if using_objects:
            self.usage_label.setText(f"Used by {len(using_objects)} object(s):\n{', '.join(using_objects)}")
        else:
            self.usage_label.setText("Not currently used by any objects")


class TemplateEditDialog(QDialog):
    """Dialog for editing template details"""
    
    def __init__(self, name: str, description: str, required_views: List[str], parent=None):
        super().__init__(parent)
        self.setWindowTitle("Edit Template")
        self.setModal(True)
        self.resize(500, 400)
        
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
