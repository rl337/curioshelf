"""
Tests for business logic controllers - Version 2

This version tests the new architecture where slice creation is moved
from sources to objects, establishing 1:1 correspondence between views and slices.
"""

import unittest
from pathlib import Path

from curioshelf.models import AssetManager, AssetSource, ObjectSlice, CurioObject, Template
from curioshelf.business_logic_v2 import SourcesController, TemplatesController, ObjectsController
from curioshelf.ui_mocks import MockUIFactory


class TestSourcesControllerV2(unittest.TestCase):
    """Test the sources controller business logic (simplified)"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.asset_manager = AssetManager()
        self.ui_factory = MockUIFactory
        self.controller = SourcesController(self.asset_manager, self.ui_factory)
        self.controller.setup_ui(self.ui_factory)
    
    def test_initial_state(self):
        """Test initial controller state"""
        self.assertIsNotNone(self.controller.import_btn)
        self.assertIsNotNone(self.controller.source_combo)
        self.assertIsNotNone(self.controller.canvas)
        self.assertIsNone(self.controller.current_source)
    
    def test_refresh_source_combo(self):
        """Test refreshing the source combo box"""
        # Add some sources
        source1 = self.asset_manager.add_source(Path("test1.png"), 100, 100)
        source2 = self.asset_manager.add_source(Path("test2.png"), 200, 150)
        
        self.controller.refresh_source_combo()
        
        # Check that sources are added to combo
        self.assertEqual(len(self.controller.source_combo._items), 2)
        self.assertEqual(self.controller.source_combo._items[0][0], "test1.png (100x100)")
        self.assertEqual(self.controller.source_combo._items[1][0], "test2.png (200x150)")
    
    def test_import_source(self):
        """Test importing a source"""
        # Setup file dialog to return a file path
        self.controller.file_dialog.set_open_responses(["test_image.png"])
        
        # Import source
        self.controller.import_source()
        
        # Check that source was added to asset manager
        self.assertEqual(len(self.asset_manager.sources), 1)
        source = list(self.asset_manager.sources.values())[0]
        self.assertEqual(source.file_path.name, "test_image.png")
        self.assertEqual(source.width, 800)  # Mock pixmap size
        self.assertEqual(source.height, 600)
    
    def test_load_source(self):
        """Test loading a source into the canvas"""
        source = self.asset_manager.add_source(Path("test.png"), 200, 150)
        
        self.controller.load_source(source, "test.png")
        
        self.assertEqual(self.controller.current_source, source)
        self.assertIsNotNone(self.controller.canvas._pixmap)
        self.assertEqual(self.controller.canvas.zoom_factor, 1.0)


class TestTemplatesControllerV2(unittest.TestCase):
    """Test the templates controller business logic"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.asset_manager = AssetManager()
        self.ui_factory = MockUIFactory
        self.controller = TemplatesController(self.asset_manager, self.ui_factory)
        self.controller.setup_ui(self.ui_factory)
    
    def test_initial_state(self):
        """Test initial controller state"""
        self.assertIsNotNone(self.controller.templates_list)
        self.assertIsNotNone(self.controller.template_name_label)
        self.assertIsNotNone(self.controller.template_description_label)
        self.assertIsNotNone(self.controller.views_widget)
        self.assertIsNotNone(self.controller.usage_label)
        self.assertIsNotNone(self.controller.create_template_btn)
        self.assertIsNotNone(self.controller.edit_template_btn)
        self.assertIsNotNone(self.controller.delete_template_btn)
        self.assertIsNone(self.controller.current_template)
    
    def test_refresh(self):
        """Test refreshing the template list"""
        # Add some templates
        template1 = self.asset_manager.add_template("template1", "Description 1", ["view1", "view2"])
        template2 = self.asset_manager.add_template("template2", "Description 2", ["view3", "view4"])
        
        self.controller.refresh()
        
        # Check that templates are added to list
        self.assertEqual(len(self.controller.templates_list._items), 2)
        self.assertEqual(self.controller.templates_list._items[0][0], "template1")
        self.assertEqual(self.controller.templates_list._items[1][0], "template2")
    
    def test_create_template(self):
        """Test creating a new template"""
        initial_count = len(self.asset_manager.templates)
        
        self.controller.create_template()
        
        # Check that template was created
        self.assertEqual(len(self.asset_manager.templates), initial_count + 1)
        
        # Find the new template
        new_template = None
        for template in self.asset_manager.templates.values():
            if template.name.startswith("test_template_"):
                new_template = template
                break
        
        self.assertIsNotNone(new_template)
        self.assertEqual(new_template.description, "Test template")
        self.assertEqual(new_template.required_views, ["front", "back", "left", "right"])


class TestObjectsControllerV2(unittest.TestCase):
    """Test the objects controller business logic with slice creation"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.asset_manager = AssetManager()
        self.ui_factory = MockUIFactory
        self.controller = ObjectsController(self.asset_manager, self.ui_factory)
        self.controller.setup_ui(self.ui_factory)
    
    def test_initial_state(self):
        """Test initial controller state"""
        self.assertIsNotNone(self.controller.objects_list)
        self.assertIsNotNone(self.controller.object_name_label)
        self.assertIsNotNone(self.controller.object_template_label)
        self.assertIsNotNone(self.controller.compliance_progress)
        self.assertIsNotNone(self.controller.compliance_widget)
        self.assertIsNotNone(self.controller.views_list)
        self.assertIsNotNone(self.controller.create_object_btn)
        self.assertIsNotNone(self.controller.edit_object_btn)
        self.assertIsNotNone(self.controller.delete_object_btn)
        
        # Slice creation components
        self.assertIsNotNone(self.controller.source_combo)
        self.assertIsNotNone(self.controller.canvas)
        self.assertIsNotNone(self.controller.layer_combo)
        self.assertIsNotNone(self.controller.create_slice_btn)
        self.assertIsNotNone(self.controller.clear_selection_btn)
        
        self.assertIsNone(self.controller.current_object)
        self.assertIsNone(self.controller.current_source)
    
    def test_refresh_objects_list(self):
        """Test refreshing the objects list"""
        # Add some objects
        obj1 = self.asset_manager.add_object("Object 1")
        obj2 = self.asset_manager.add_object("Object 2")
        
        self.controller.refresh_objects_list()
        
        # Check that objects are added to list
        self.assertEqual(len(self.controller.objects_list._items), 2)
        self.assertEqual(self.controller.objects_list._items[0][0], "Object 1")
        self.assertEqual(self.controller.objects_list._items[1][0], "Object 2")
    
    def test_refresh_sources_combo(self):
        """Test refreshing the sources combo box"""
        # Add some sources
        source1 = self.asset_manager.add_source(Path("test1.png"), 100, 100)
        source2 = self.asset_manager.add_source(Path("test2.png"), 200, 150)
        
        self.controller.refresh_sources_combo()
        
        # Check that sources are added to combo
        self.assertEqual(len(self.controller.source_combo._items), 2)
        self.assertEqual(self.controller.source_combo._items[0][0], "test1.png (100x100)")
        self.assertEqual(self.controller.source_combo._items[1][0], "test2.png (200x150)")
    
    def test_create_object(self):
        """Test creating a new object"""
        initial_count = len(self.asset_manager.objects)
        
        self.controller.create_object()
        
        # Check that object was created
        self.assertEqual(len(self.asset_manager.objects), initial_count + 1)
        
        # Find the new object
        new_object = None
        for obj in self.asset_manager.objects.values():
            if obj.name.startswith("test_object_"):
                new_object = obj
                break
        
        self.assertIsNotNone(new_object)
    
    def test_refresh_views(self):
        """Test refreshing the views list for an object with template"""
        # Create template and object
        template = self.asset_manager.add_template("test_template", "Description", ["front", "back", "left", "right"])
        obj = self.asset_manager.add_object("Test Object", "test_template")
        
        # Add some slices to the object
        slice1 = ObjectSlice("front", "source1", 0, 0, 10, 10, "concept")
        slice2 = ObjectSlice("back", "source1", 0, 0, 10, 10, "concept")
        obj.slices = [slice1, slice2]
        
        self.controller.current_object = obj
        self.controller.refresh_views()
        
        # Check that views are displayed correctly
        self.assertEqual(len(self.controller.views_list._items), 4)  # 4 template views
        self.assertEqual(self.controller.views_list._items[0][0], "front: ✓ 1 slice(s)")
        self.assertEqual(self.controller.views_list._items[1][0], "back: ✓ 1 slice(s)")
        self.assertEqual(self.controller.views_list._items[2][0], "left: ✗ Missing")
        self.assertEqual(self.controller.views_list._items[3][0], "right: ✗ Missing")
    
    def test_create_slice_for_view(self):
        """Test creating a slice for a specific view"""
        # Setup template, object, and source
        template = self.asset_manager.add_template("test_template", "Description", ["front", "back"])
        obj = self.asset_manager.add_object("Test Object", "test_template")
        source = self.asset_manager.add_source(Path("test.png"), 200, 150)
        
        self.controller.current_object = obj
        self.controller.current_source = source
        self.controller.load_source(source)
        
        # Refresh views to populate the views list
        self.controller.refresh_views()
        
        # Select the "front" view
        self.controller.views_list.set_current_index(0)  # "front" view
        
        # Setup canvas with selection
        rect = self.ui_factory.create_rect(10, 20, 50, 60)
        self.controller.canvas.set_selection_rect(rect)
        
        # Create slice
        self.controller.create_slice()
        
        # Check that slice was created with correct name
        self.assertEqual(len(source.slices), 1)
        self.assertEqual(len(obj.slices), 1)
        slice_obj = source.slices[0]
        self.assertEqual(slice_obj.name, "front")  # Slice name = view name
        self.assertEqual(slice_obj.x, 10)
        self.assertEqual(slice_obj.y, 20)
        self.assertEqual(slice_obj.width, 50)
        self.assertEqual(slice_obj.height, 60)
    
    def test_create_slice_without_view_selection(self):
        """Test that slice creation fails without view selection"""
        # Setup object and source
        obj = self.asset_manager.add_object("Test Object")
        source = self.asset_manager.add_source(Path("test.png"), 200, 150)
        
        self.controller.current_object = obj
        self.controller.current_source = source
        self.controller.load_source(source)
        
        # Setup canvas with selection but no view selected
        rect = self.ui_factory.create_rect(10, 20, 50, 60)
        self.controller.canvas.set_selection_rect(rect)
        
        # Try to create slice
        self.controller.create_slice()
        
        # Check that no slice was created
        self.assertEqual(len(source.slices), 0)
        self.assertEqual(len(obj.slices), 0)
        
        # Check that warning message was shown
        messages = self.controller.message_box.get_messages()
        self.assertTrue(any("Please select a view" in msg[2] for msg in messages))
    
    def test_refresh_compliance(self):
        """Test refreshing template compliance"""
        # Create a template and object
        template = self.asset_manager.add_template("test_template", "Description", ["front", "back", "left", "right"])
        obj = self.asset_manager.add_object("Test Object", "test_template")
        
        # Add some slices to the object
        slice1 = ObjectSlice("front", "source1", 0, 0, 10, 10, "concept")
        slice2 = ObjectSlice("back", "source1", 0, 0, 10, 10, "concept")
        obj.slices = [slice1, slice2]
        
        self.controller.current_object = obj
        self.controller.refresh_compliance()
        
        # Check that progress bar shows 50% (2 out of 4 views complete)
        self.assertEqual(self.controller.compliance_progress.value, 50)
        self.assertTrue(self.controller.compliance_progress.visible)
    
    def test_clear_selection(self):
        """Test clearing canvas selection"""
        # Setup canvas with selection
        rect = self.ui_factory.create_rect(10, 20, 50, 60)
        self.controller.canvas.set_selection_rect(rect)
        self.controller.create_slice_btn.set_enabled(True)
        
        # Clear selection
        self.controller.clear_selection()
        
        # Check that selection is cleared and button is disabled
        self.assertIsNone(self.controller.canvas.selection_rect)
        self.assertFalse(self.controller.create_slice_btn.enabled)


class TestIntegrationV2(unittest.TestCase):
    """Test integration between controllers - Version 2"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.asset_manager = AssetManager()
        self.ui_factory = MockUIFactory
        
        self.sources_controller = SourcesController(self.asset_manager, self.ui_factory)
        self.templates_controller = TemplatesController(self.asset_manager, self.ui_factory)
        self.objects_controller = ObjectsController(self.asset_manager, self.ui_factory)
        
        self.sources_controller.setup_ui(self.ui_factory)
        self.templates_controller.setup_ui(self.ui_factory)
        self.objects_controller.setup_ui(self.ui_factory)
    
    def test_full_workflow_v2(self):
        """Test a complete workflow with slice creation in objects tab"""
        # 1. Create a template
        self.templates_controller.create_template()
        template = list(self.asset_manager.templates.values())[0]
        
        # 2. Create an object with the template
        self.objects_controller.create_object()
        obj = list(self.asset_manager.objects.values())[0]
        obj.template_name = template.name
        
        # 3. Import a source
        self.sources_controller.file_dialog.set_open_responses(["test.png"])
        self.sources_controller.import_source()
        source = list(self.asset_manager.sources.values())[0]
        
        # 4. Select the object and source in objects controller
        self.objects_controller.current_object = obj
        self.objects_controller.current_source = source
        self.objects_controller.load_source(source)
        
        # 5. Refresh views and select a view to create a slice
        self.objects_controller.refresh_views()
        self.objects_controller.views_list.set_current_index(0)  # Select first view
        
        rect = self.ui_factory.create_rect(10, 20, 50, 60)
        self.objects_controller.canvas.set_selection_rect(rect)
        
        self.objects_controller.create_slice()
        
        # 6. Verify the complete workflow
        self.assertEqual(len(source.slices), 1)
        self.assertEqual(len(obj.slices), 1)
        self.assertEqual(source.slices[0].name, "front")  # First view from template
        self.assertEqual(obj.slices[0].name, "front")
        
        # 7. Check template compliance
        self.objects_controller.refresh_compliance()
        self.assertGreater(self.objects_controller.compliance_progress.value, 0)


if __name__ == "__main__":
    unittest.main()
