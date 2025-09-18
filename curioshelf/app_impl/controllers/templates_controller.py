"""
Templates Controller

Business logic controller for templates management.
"""

from typing import List, Optional, Dict, Any, Callable
from pathlib import Path

from ...models import AssetManager, AssetSource, ObjectSlice, CurioObject, Template
from ...ui_abstraction import (
    UIWidget, UIButton, UITextInput, UIComboBox, UIListWidget, UICanvas,
    UIMessageBox, UIFileDialog, UIProgressBar, UIGroupBox, UITabWidget
)
from ...ui_factory_interface import UIFactoryInterface, UIComponentManager


class TemplatesController:
    """Business logic controller for templates management"""
    
    def __init__(self, asset_manager: AssetManager, ui_factory: UIFactoryInterface) -> None:
        self.asset_manager = asset_manager
        self.ui_factory = ui_factory
        self.ui_manager = UIComponentManager(ui_factory)
        
        # UI components
        self.templates_list: Optional[UIListWidget] = None
        self.template_name_label: Optional[UITextInput] = None
        self.template_description_label: Optional[UITextInput] = None
        self.views_widget: Optional[UIListWidget] = None
        self.usage_label: Optional[UITextInput] = None
        self.create_template_btn: Optional[UIButton] = None
        self.edit_template_btn: Optional[UIButton] = None
        self.delete_template_btn: Optional[UIButton] = None
        
        # State
        self.current_template: Optional[Template] = None
        self.message_box: Optional[UIMessageBox] = None
        
        # Callbacks
        self.on_template_created: Optional[Callable[[Template], None]] = None
        self.on_template_updated: Optional[Callable[[Template], None]] = None
        self.on_template_deleted: Optional[Callable[[str], None]] = None
    
    def setup_ui(self, ui_factory: UIFactoryInterface) -> None:
        """Setup UI components using the factory"""
        self.ui_factory = ui_factory
        self.ui_manager = UIComponentManager(ui_factory)
        
        # Create UI components
        self.templates_list = ui_factory.create_list_widget()
        self.template_name_label = ui_factory.create_text_input()
        self.template_description_label = ui_factory.create_text_input()
        self.views_widget = ui_factory.create_list_widget()
        self.usage_label = ui_factory.create_text_input()
        self.create_template_btn = ui_factory.create_button("Create Template")
        self.edit_template_btn = ui_factory.create_button("Edit")
        self.delete_template_btn = ui_factory.create_button("Delete")
        self.message_box = ui_factory.create_message_box()
        
        # Setup connections
        self.templates_list.set_current_changed_callback(self.on_template_selected)
        self.create_template_btn.set_clicked_callback(self.create_template)
        self.edit_template_btn.set_clicked_callback(self.edit_template)
        self.delete_template_btn.set_clicked_callback(self.delete_template)
        
        # Initial refresh
        self.refresh()
    
    def refresh(self) -> None:
        """Refresh the template list"""
        if not self.templates_list:
            return
        
        self.templates_list.clear()
        for template in self.asset_manager.templates.values():
            self.templates_list.add_item(template.name, template.name)
    
    def on_template_selected(self, template_name: str) -> None:
        """Handle template selection"""
        if not template_name:
            return
        
        self.current_template = self.asset_manager.templates.get(template_name)
        
        if self.current_template:
            if self.edit_template_btn:
                self.edit_template_btn.set_enabled(True)
            if self.delete_template_btn:
                self.delete_template_btn.set_enabled(True)
            self.refresh_details()
        else:
            if self.edit_template_btn:
                self.edit_template_btn.set_enabled(False)
            if self.delete_template_btn:
                self.delete_template_btn.set_enabled(False)
    
    def refresh_details(self) -> None:
        """Refresh the template details display"""
        if not self.current_template:
            if self.template_name_label:
                self.template_name_label.set_text("No template selected")
            if self.template_description_label:
                self.template_description_label.set_text("")
            if self.usage_label:
                self.usage_label.set_text("No usage data")
            return
        
        if self.template_name_label:
            self.template_name_label.set_text(self.current_template.name)
        if self.template_description_label:
            self.template_description_label.set_text(self.current_template.description)
        
        # Refresh views
        self.refresh_views()
        
        # Refresh usage statistics
        self.refresh_usage_stats()
    
    def refresh_views(self) -> None:
        """Refresh the required views display"""
        if not self.views_widget or not self.current_template:
            return
        
        # Clear existing views
        if hasattr(self.views_widget, 'clear'):
            self.views_widget.clear()
        
        # Add views (simplified for testing)
        for view in self.current_template.required_views:
            if hasattr(self.views_widget, 'add_item'):
                self.views_widget.add_item(view)
    
    def refresh_usage_stats(self) -> None:
        """Refresh usage statistics"""
        if not self.usage_label or not self.current_template:
            return
        
        # Count objects using this template
        using_objects = []
        for obj in self.asset_manager.objects.values():
            if obj.template_name == self.current_template.name:
                using_objects.append(obj.name)
        
        if using_objects:
            usage_text = f"Used by {len(using_objects)} object(s): {', '.join(using_objects)}"
        else:
            usage_text = "Not currently used by any objects"
        
        self.usage_label.set_text(usage_text)
    
    def create_template(self) -> None:
        """Create a new template"""
        # For testing, create a simple template
        template_name = f"test_template_{len(self.asset_manager.templates)}"
        description = "Test template"
        required_views = ["front", "back", "left", "right"]
        
        template = self.asset_manager.add_template(template_name, description, required_views)
        
        # Refresh and select the new template
        self.refresh()
        if self.templates_list:
            for i in range(self.templates_list._items.__len__()):
                if self.templates_list._items[i][1] == template.name:
                    self.templates_list.set_current_index(i)
                    break
        
        # Emit callback
        if self.on_template_created:
            self.on_template_created(template)
    
    def edit_template(self) -> None:
        """Edit the selected template"""
        if not self.current_template:
            return
        
        # For testing, just update the description
        self.current_template.description = f"Updated: {self.current_template.description}"
        
        self.refresh_details()
        
        # Emit callback
        if self.on_template_updated:
            self.on_template_updated(self.current_template)
    
    def delete_template(self) -> None:
        """Delete the selected template"""
        if not self.current_template:
            return
        
        # Check if any objects are using this template
        using_objects = []
        for obj in self.asset_manager.objects.values():
            if obj.template_name == self.current_template.name:
                using_objects.append(obj.name)
        
        if using_objects:
            if self.message_box:
                self.message_box.show_warning(
                    "Cannot Delete Template",
                    f"This template is being used by the following objects:\n{', '.join(using_objects)}\n\nPlease change their template first."
                )
            return
        
        # Confirm deletion
        if self.message_box and not self.message_box.show_question(
            "Delete Template",
            f"Are you sure you want to delete template '{self.current_template.name}'?"
        ):
            return
        
        template_name = self.current_template.name
        
        # Remove from asset manager
        if template_name in self.asset_manager.templates:
            del self.asset_manager.templates[template_name]
        
        # Clear current template and refresh
        self.current_template = None
        self.refresh()
        self.refresh_details()
        
        # Emit callback
        if self.on_template_deleted:
            self.on_template_deleted(template_name)
