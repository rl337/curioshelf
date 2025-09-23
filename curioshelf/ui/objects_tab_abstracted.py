"""
Abstracted objects tab for managing objects and their slices

This version uses the UI abstraction layer instead of direct PySide6 imports.
"""

from typing import Optional, Callable, Any
from pathlib import Path

from curioshelf.models import AssetManager, CurioObject, ObjectSlice, Template
from .abstraction import UIWidget


class ObjectsTabAbstracted:
    """Objects tab using UI abstraction layer"""
    
    def __init__(self, asset_manager: AssetManager, ui_factory):
        self.asset_manager = asset_manager
        self.ui_factory = ui_factory
        self.current_object: Optional[CurioObject] = None
        self.current_source: Optional[Any] = None
        
        # UI components
        self.widget = None
        self.objects_list = None
        self.object_name_label = None
        self.object_template_label = None
        self.compliance_progress = None
        self.views_list = None
        self.create_object_btn = None
        self.edit_object_btn = None
        self.delete_object_btn = None
        
        # Slice creation UI components
        self.source_combo = None
        self.canvas = None
        self.layer_combo = None
        self.create_slice_btn = None
        self.clear_selection_btn = None
        
        # Callbacks
        self.object_created: Optional[Callable[[CurioObject], None]] = None
        self.object_updated: Optional[Callable[[CurioObject], None]] = None
        self.object_deleted: Optional[Callable[[str], None]] = None
        self.slice_created: Optional[Callable[[ObjectSlice], None]] = None
        
        self.setup_ui()
        self.refresh()
    
    def setup_ui(self):
        """Setup the UI using abstraction layer"""
        # Create main widget
        self.widget = self.ui_factory.create_widget()
        
        # Create main layout
        main_layout = self.ui_factory.create_layout("horizontal")
        self.widget.set_layout(main_layout)
        
        # Left panel - object list and details
        left_panel = self.ui_factory.create_widget()
        left_layout = self.ui_factory.create_layout("vertical")
        left_panel.set_layout(left_layout)
        
        # Object list
        objects_group = self.ui_factory.create_group_box("Objects")
        objects_layout = self.ui_factory.create_layout("vertical")
        objects_group.set_layout(objects_layout)
        
        self.objects_list = self.ui_factory.create_list_widget()
        self.objects_list.set_current_changed_callback(self.on_object_selected)
        objects_layout.add_widget(self.objects_list)
        
        # Object controls
        controls_layout = self.ui_factory.create_layout("horizontal")
        self.create_object_btn = self.ui_factory.create_button("Create Object")
        self.create_object_btn.set_clicked_callback(self.create_object)
        controls_layout.add_widget(self.create_object_btn)
        
        self.edit_object_btn = self.ui_factory.create_button("Edit")
        self.edit_object_btn.set_clicked_callback(self.edit_object)
        self.edit_object_btn.set_enabled(False)
        controls_layout.add_widget(self.edit_object_btn)
        
        self.delete_object_btn = self.ui_factory.create_button("Delete")
        self.delete_object_btn.set_clicked_callback(self.delete_object)
        self.delete_object_btn.set_enabled(False)
        controls_layout.add_widget(self.delete_object_btn)
        
        objects_layout.add_widget(controls_layout)
        left_layout.add_widget(objects_group)
        
        # Object details
        details_group = self.ui_factory.create_group_box("Object Details")
        details_layout = self.ui_factory.create_layout("vertical")
        details_group.set_layout(details_layout)
        
        # Object name
        self.object_name_label = self.ui_factory.create_text_input()
        self.object_name_label.set_text("No object selected")
        details_layout.add_widget(self.object_name_label)
        
        # Object template
        self.object_template_label = self.ui_factory.create_text_input()
        self.object_template_label.set_text("")
        details_layout.add_widget(self.object_template_label)
        
        # Compliance progress
        self.compliance_progress = self.ui_factory.create_progress_bar()
        details_layout.add_widget(self.compliance_progress)
        
        # Required views
        views_group = self.ui_factory.create_group_box("Required Views")
        views_layout = self.ui_factory.create_layout("vertical")
        views_group.set_layout(views_layout)
        
        self.views_list = self.ui_factory.create_list_widget()
        views_layout.add_widget(self.views_list)
        
        details_layout.add_widget(views_group)
        left_layout.add_widget(details_group)
        
        # Right panel - slice creation
        right_panel = self.ui_factory.create_widget()
        right_layout = self.ui_factory.create_layout("vertical")
        right_panel.set_layout(right_layout)
        
        # Slice creation
        slice_group = self.ui_factory.create_group_box("Slice Creation")
        slice_layout = self.ui_factory.create_layout("vertical")
        slice_group.set_layout(slice_layout)
        
        # Source selection
        source_layout = self.ui_factory.create_layout("horizontal")
        source_layout.add_widget(self.ui_factory.create_text_input("Source:"))
        self.source_combo = self.ui_factory.create_combo_box()
        self.source_combo.set_current_changed_callback(self.on_source_selected)
        source_layout.add_widget(self.source_combo)
        slice_layout.add_widget(source_layout)
        
        # Canvas
        self.canvas = self.ui_factory.create_canvas()
        self.canvas.set_selection_changed_callback(self.on_selection_changed)
        slice_layout.add_widget(self.canvas)
        
        # Layer selection
        layer_layout = self.ui_factory.create_layout("horizontal")
        layer_layout.add_widget(self.ui_factory.create_text_input("Layer:"))
        self.layer_combo = self.ui_factory.create_combo_box()
        from curioshelf.ui.abstraction import UIListItem
        concept_item = UIListItem("concept")
        concept_item.set_data("concept")
        self.layer_combo.add_item(concept_item)
        
        working_item = UIListItem("working")
        working_item.set_data("working")
        self.layer_combo.add_item(working_item)
        
        production_item = UIListItem("production")
        production_item.set_data("production")
        self.layer_combo.add_item(production_item)
        self.layer_combo.set_current_index(0)
        layer_layout.add_widget(self.layer_combo)
        slice_layout.add_widget(layer_layout)
        
        # Slice controls
        slice_controls_layout = self.ui_factory.create_layout("horizontal")
        self.create_slice_btn = self.ui_factory.create_button("Create Slice")
        self.create_slice_btn.set_clicked_callback(self.create_slice)
        self.create_slice_btn.set_enabled(False)
        slice_controls_layout.add_widget(self.create_slice_btn)
        
        self.clear_selection_btn = self.ui_factory.create_button("Clear Selection")
        self.clear_selection_btn.set_clicked_callback(self.clear_selection)
        slice_controls_layout.add_widget(self.clear_selection_btn)
        
        slice_layout.add_widget(slice_controls_layout)
        right_layout.add_widget(slice_group)
        
        # Add panels to main layout
        main_layout.add_widget(left_panel)
        main_layout.add_widget(right_panel)
    
    def get_widget(self) -> UIWidget:
        """Get the main widget"""
        return self.widget
    
    def refresh(self):
        """Refresh the UI with current data"""
        self.refresh_objects_list()
        self.refresh_sources_combo()
        if self.current_object:
            self.refresh_object_details()
    
    def refresh_objects_list(self):
        """Refresh the objects list"""
        if not self.objects_list:
            return
        
        self.objects_list.clear()
        for obj in self.asset_manager.objects.values():
            obj_item = UIListItem(obj.name)
            obj_item.set_data(obj.id)
            self.objects_list.add_item(obj_item)
    
    def refresh_sources_combo(self):
        """Refresh the sources combo box"""
        if not self.source_combo:
            return
        
        self.source_combo.clear()
        for source in self.asset_manager.sources.values():
            display_text = f"{source.file_path.name} ({source.width}x{source.height})"
            source_item = UIListItem(display_text)
            source_item.set_data(source.id)
            self.source_combo.add_item(source_item)
    
    def on_object_selected(self, object_id: str):
        """Handle object selection"""
        if not object_id:
            return
        
        self.current_object = self.asset_manager.objects.get(object_id)
        
        if self.current_object:
            self.edit_object_btn.set_enabled(True)
            self.delete_object_btn.set_enabled(True)
            self.refresh_object_details()
        else:
            self.edit_object_btn.set_enabled(False)
            self.delete_object_btn.set_enabled(False)
    
    def refresh_object_details(self):
        """Refresh the object details display"""
        if not self.current_object:
            if self.object_name_label:
                self.object_name_label.set_text("No object selected")
            if self.object_template_label:
                self.object_template_label.set_text("")
            if self.compliance_progress:
                self.compliance_progress.set_visible(False)
            return
        
        if self.object_name_label:
            self.object_name_label.set_text(self.current_object.name)
        
        if self.object_template_label:
            if self.current_object.template_name:
                template = self.asset_manager.templates.get(self.current_object.template_name)
                if template:
                    self.object_template_label.set_text(f"Template: {template.name}")
                else:
                    self.object_template_label.set_text("Template: Unknown")
            else:
                self.object_template_label.set_text("No template assigned")
        
        # Refresh compliance and views
        self.refresh_compliance()
        self.refresh_views()
    
    def refresh_compliance(self):
        """Refresh the template compliance display"""
        if not self.current_object or not self.current_object.template_name:
            if self.compliance_progress:
                self.compliance_progress.set_visible(False)
            return
        
        template = self.asset_manager.templates.get(self.current_object.template_name)
        if not template:
            if self.compliance_progress:
                self.compliance_progress.set_visible(False)
            return
        
        # Get completeness status
        completeness = self.asset_manager.get_object_completeness(self.current_object.id)
        
        # Calculate progress
        total_views = len(template.required_views)
        completed_views = sum(1 for is_complete in completeness.values() if is_complete)
        progress = int((completed_views / total_views) * 100) if total_views > 0 else 0
        
        if self.compliance_progress:
            self.compliance_progress.set_value(progress)
            self.compliance_progress.set_visible(True)
    
    def refresh_views(self):
        """Refresh the views list for the current object"""
        if not self.views_list or not self.current_object:
            return
        
        self.views_list.clear()
        
        # Get template for this object
        template = None
        if self.current_object.template_name:
            template = self.asset_manager.templates.get(self.current_object.template_name)
        
        if not template:
            no_template_item = UIListItem("No template assigned")
            no_template_item.set_data("no_template")
            self.views_list.add_item(no_template_item)
            return
        
        # Group slices by view name
        slices_by_view = {}
        for slice_obj in self.current_object.slices:
            view_name = slice_obj.name
            if view_name not in slices_by_view:
                slices_by_view[view_name] = []
            slices_by_view[view_name].append(slice_obj)
        
        # Add views from template
        for view_name in template.required_views:
            if view_name in slices_by_view:
                # View has slices
                slice_count = len(slices_by_view[view_name])
                status = f"✓ {slice_count} slice(s)"
                view_item = UIListItem(f"{view_name}: {status}")
                view_item.set_data(view_name)
                self.views_list.add_item(view_item)
            else:
                # View is missing
                missing_item = UIListItem(f"{view_name}: ✗ Missing")
                missing_item.set_data(view_name)
                self.views_list.add_item(missing_item)
    
    def on_source_selected(self, source_id: str):
        """Handle source selection for slice creation"""
        if not source_id:
            return
        
        source = self.asset_manager.sources.get(source_id)
        if source:
            self.current_source = source
            self.load_source(source)
    
    def load_source(self, source):
        """Load a source image into the canvas"""
        if self.canvas:
            pixmap = self.ui_factory.create_pixmap(source.width, source.height)
            self.canvas.set_pixmap(pixmap)
            self.canvas.set_zoom(1.0)
    
    def on_selection_changed(self, selection_rect: Optional[Any]):
        """Handle selection changes from the canvas"""
        if not self.create_slice_btn:
            return
        
        if selection_rect and hasattr(selection_rect, 'isValid') and selection_rect.isValid():
            self.create_slice_btn.set_enabled(True)
        else:
            self.create_slice_btn.set_enabled(False)
    
    def create_slice(self):
        """Create a slice for the current object view"""
        if not self.current_object or not self.current_source or not self.canvas:
            return
        
        # Get the selected view from the views list
        selected_view = self.views_list.current_data() if self.views_list else None
        if not selected_view:
            msg_box = self.ui_factory.create_message_box()
            msg_box.show_warning("Error", "Please select a view to create a slice for")
            return
        
        # For testing, create a mock slice
        slice_obj = ObjectSlice(
            name=selected_view,
            source_id=self.current_source.id,
            x=10, y=10, width=100, height=100,  # Mock coordinates
            layer=self.layer_combo.current_text() if self.layer_combo else "concept"
        )
        
        # Add to source
        self.current_source.add_slice(slice_obj)
        
        # Add to object
        self.current_object.slices.append(slice_obj)
        
        # Emit callback
        if self.slice_created:
            self.slice_created(slice_obj)
        
        # Clear selection and refresh
        self.clear_selection()
        self.refresh_views()
        
        msg_box = self.ui_factory.create_message_box()
        msg_box.show_info("Success", f"Slice for view '{selected_view}' created successfully!")
    
    def clear_selection(self):
        """Clear the canvas selection"""
        if self.canvas:
            self.canvas.clear_selection()
        if self.create_slice_btn:
            self.create_slice_btn.set_enabled(False)
    
    def create_object(self):
        """Create a new object"""
        object_name = f"test_object_{len(self.asset_manager.objects)}"
        template_name = None
        
        # Use first available template if any
        if self.asset_manager.templates:
            template_name = list(self.asset_manager.templates.keys())[0]
        
        obj = self.asset_manager.add_object(object_name, template_name)
        
        # Refresh and select the new object
        self.refresh()
        if self.objects_list:
            for i in range(len(self.objects_list._items)):
                if self.objects_list._items[i][1] == obj.id:
                    self.objects_list.set_current_index(i)
                    break
        
        # Emit callback
        if self.object_created:
            self.object_created(obj)
    
    def edit_object(self):
        """Edit the selected object"""
        if not self.current_object:
            return
        
        # For testing, just update the name
        self.current_object.name = f"Updated: {self.current_object.name}"
        
        self.refresh()
        self.refresh_object_details()
        
        # Emit callback
        if self.object_updated:
            self.object_updated(self.current_object)
    
    def delete_object(self):
        """Delete the selected object"""
        if not self.current_object:
            return
        
        # Confirm deletion
        msg_box = self.ui_factory.create_message_box()
        if not msg_box.show_question(
            "Delete Object",
            f"Are you sure you want to delete '{self.current_object.name}'?"
        ):
            return
        
        object_id = self.current_object.id
        
        # Remove from asset manager
        if object_id in self.asset_manager.objects:
            del self.asset_manager.objects[object_id]
        
        # Clear current object and refresh
        self.current_object = None
        self.refresh()
        self.refresh_object_details()
        
        # Emit callback
        if self.object_deleted:
            self.object_deleted(object_id)
    
    def connect_signal(self, signal_name: str, callback: Callable):
        """Connect a signal callback"""
        if signal_name == "object_created":
            self.object_created = callback
        elif signal_name == "object_updated":
            self.object_updated = callback
        elif signal_name == "object_deleted":
            self.object_deleted = callback
        elif signal_name == "slice_created":
            self.slice_created = callback
