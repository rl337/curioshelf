"""
Abstracted templates tab for managing templates

This version uses the UI abstraction layer instead of direct PySide6 imports.
"""

from typing import Optional, Callable
from pathlib import Path

from curioshelf.models import AssetManager, Template
from curioshelf.ui_abstraction import UIWidget


class TemplatesTabAbstracted:
    """Templates tab using UI abstraction layer"""
    
    def __init__(self, asset_manager: AssetManager, ui_factory):
        self.asset_manager = asset_manager
        self.ui_factory = ui_factory
        self.current_template: Optional[Template] = None
        
        # UI components
        self.widget = None
        self.templates_list = None
        self.template_name_label = None
        self.template_description_label = None
        self.views_list = None
        self.usage_label = None
        self.create_template_btn = None
        self.edit_template_btn = None
        self.delete_template_btn = None
        
        # Callbacks
        self.template_created: Optional[Callable[[Template], None]] = None
        self.template_updated: Optional[Callable[[Template], None]] = None
        self.template_deleted: Optional[Callable[[str], None]] = None
        
        self.setup_ui()
        self.refresh()
    
    def setup_ui(self):
        """Setup the UI using abstraction layer"""
        # Create main widget
        self.widget = self.ui_factory.create_widget()
        
        # Create main layout
        main_layout = self.ui_factory.create_layout("horizontal")
        self.widget.set_layout(main_layout)
        
        # Left panel - template list
        left_panel = self.ui_factory.create_widget()
        left_layout = self.ui_factory.create_layout("vertical")
        left_panel.set_layout(left_layout)
        
        # Template list
        templates_group = self.ui_factory.create_group_box("Templates")
        templates_layout = self.ui_factory.create_layout("vertical")
        templates_group.set_layout(templates_layout)
        
        self.templates_list = self.ui_factory.create_list_widget()
        self.templates_list.set_current_changed_callback(self.on_template_selected)
        templates_layout.add_widget(self.templates_list)
        
        # Template controls
        controls_layout = self.ui_factory.create_layout("horizontal")
        self.create_template_btn = self.ui_factory.create_button("Create Template")
        self.create_template_btn.set_clicked_callback(self.create_template)
        controls_layout.add_widget(self.create_template_btn)
        
        self.edit_template_btn = self.ui_factory.create_button("Edit")
        self.edit_template_btn.set_clicked_callback(self.edit_template)
        self.edit_template_btn.set_enabled(False)
        controls_layout.add_widget(self.edit_template_btn)
        
        self.delete_template_btn = self.ui_factory.create_button("Delete")
        self.delete_template_btn.set_clicked_callback(self.delete_template)
        self.delete_template_btn.set_enabled(False)
        controls_layout.add_widget(self.delete_template_btn)
        
        templates_layout.add_widget(controls_layout)
        left_layout.add_widget(templates_group)
        
        # Right panel - template details
        right_panel = self.ui_factory.create_widget()
        right_layout = self.ui_factory.create_layout("vertical")
        right_panel.set_layout(right_layout)
        
        # Template details
        details_group = self.ui_factory.create_group_box("Template Details")
        details_layout = self.ui_factory.create_layout("vertical")
        details_group.set_layout(details_layout)
        
        # Template name
        self.template_name_label = self.ui_factory.create_text_input()
        self.template_name_label.set_text("No template selected")
        details_layout.add_widget(self.template_name_label)
        
        # Template description
        self.template_description_label = self.ui_factory.create_text_input()
        self.template_description_label.set_text("")
        details_layout.add_widget(self.template_description_label)
        
        # Required views
        views_group = self.ui_factory.create_group_box("Required Views")
        views_layout = self.ui_factory.create_layout("vertical")
        views_group.set_layout(views_layout)
        
        self.views_list = self.ui_factory.create_list_widget()
        views_layout.add_widget(self.views_list)
        
        # Usage statistics
        usage_group = self.ui_factory.create_group_box("Usage")
        usage_layout = self.ui_factory.create_layout("vertical")
        usage_group.set_layout(usage_layout)
        
        self.usage_label = self.ui_factory.create_text_input()
        self.usage_label.set_text("No usage data")
        usage_layout.add_widget(self.usage_label)
        
        details_layout.add_widget(views_group)
        details_layout.add_widget(usage_group)
        right_layout.add_widget(details_group)
        
        # Add panels to main layout
        main_layout.add_widget(left_panel)
        main_layout.add_widget(right_panel)
    
    def get_widget(self) -> UIWidget:
        """Get the main widget"""
        return self.widget
    
    def refresh(self):
        """Refresh the template list"""
        if not self.templates_list:
            return
        
        self.templates_list.clear()
        for template in self.asset_manager.templates.values():
            self.templates_list.add_item(template.name, template.name)
    
    def on_template_selected(self, template_name: str):
        """Handle template selection"""
        if not template_name:
            return
        
        self.current_template = self.asset_manager.templates.get(template_name)
        
        if self.current_template:
            self.edit_template_btn.set_enabled(True)
            self.delete_template_btn.set_enabled(True)
            self.refresh_details()
        else:
            self.edit_template_btn.set_enabled(False)
            self.delete_template_btn.set_enabled(False)
    
    def refresh_details(self):
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
    
    def refresh_views(self):
        """Refresh the required views display"""
        if not self.views_list or not self.current_template:
            return
        
        self.views_list.clear()
        for view in self.current_template.required_views:
            self.views_list.add_item(view)
    
    def refresh_usage_stats(self):
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
    
    def create_template(self):
        """Create a new template"""
        # For testing, create a simple template
        template_name = f"test_template_{len(self.asset_manager.templates)}"
        description = "Test template"
        required_views = ["front", "back", "left", "right"]
        
        template = self.asset_manager.add_template(template_name, description, required_views)
        
        # Refresh and select the new template
        self.refresh()
        if self.templates_list:
            for i in range(len(self.templates_list._items)):
                if self.templates_list._items[i][1] == template.name:
                    self.templates_list.set_current_index(i)
                    break
        
        # Emit callback
        if self.template_created:
            self.template_created(template)
    
    def edit_template(self):
        """Edit the selected template"""
        if not self.current_template:
            return
        
        # For testing, just update the description
        self.current_template.description = f"Updated: {self.current_template.description}"
        
        self.refresh_details()
        
        # Emit callback
        if self.template_updated:
            self.template_updated(self.current_template)
    
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
            msg_box = self.ui_factory.create_message_box()
            msg_box.show_warning(
                "Cannot Delete Template",
                f"This template is being used by the following objects:\n{', '.join(using_objects)}\n\nPlease change their template first."
            )
            return
        
        # Confirm deletion
        msg_box = self.ui_factory.create_message_box()
        if not msg_box.show_question(
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
        if self.template_deleted:
            self.template_deleted(template_name)
    
    def connect_signal(self, signal_name: str, callback: Callable):
        """Connect a signal callback"""
        if signal_name == "template_created":
            self.template_created = callback
        elif signal_name == "template_updated":
            self.template_updated = callback
        elif signal_name == "template_deleted":
            self.template_deleted = callback
