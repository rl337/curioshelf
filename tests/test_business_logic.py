"""
Tests for business logic controllers
"""

import unittest
from pathlib import Path

from curioshelf.models import AssetManager, AssetSource, ObjectSlice, CurioObject, Template
from curioshelf.business_logic import SourcesController, TemplatesController, ObjectsController
from curioshelf.ui_mocks import MockUIFactory


class TestSourcesController(unittest.TestCase):
    """Test the sources controller business logic"""
    
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
        self.assertIsNotNone(self.controller.slice_name_input)
        self.assertIsNotNone(self.controller.layer_combo)
        self.assertIsNotNone(self.controller.object_combo)
        self.assertIsNotNone(self.controller.create_slice_btn)
        self.assertIsNotNone(self.controller.slices_list)
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
    
    def test_refresh_object_combo(self):
        """Test refreshing the object combo box"""
        # Add some objects
        obj1 = self.asset_manager.add_object("Object 1")
        obj2 = self.asset_manager.add_object("Object 2")
        
        self.controller.refresh_object_combo()
        
        # Check that objects are added to combo
        self.assertEqual(len(self.controller.object_combo._items), 3)  # +1 for "No Object"
        self.assertEqual(self.controller.object_combo._items[0][0], "No Object")
        self.assertEqual(self.controller.object_combo._items[1][0], "Object 1")
        self.assertEqual(self.controller.object_combo._items[2][0], "Object 2")
    
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
    
    def test_create_slice(self):
        """Test creating a slice"""
        # Setup source
        source = self.asset_manager.add_source(Path("test.png"), 200, 150)
        self.controller.current_source = source
        
        # Setup canvas with selection
        rect = self.ui_factory.create_rect(10, 20, 50, 60)
        self.controller.canvas.set_selection_rect(rect)
        
        # Setup slice name
        self.controller.slice_name_input.set_text("test_slice")
        
        # Create slice
        self.controller.create_slice()
        
        # Check that slice was created
        self.assertEqual(len(source.slices), 1)
        slice_obj = source.slices[0]
        self.assertEqual(slice_obj.name, "test_slice")
        self.assertEqual(slice_obj.x, 10)
        self.assertEqual(slice_obj.y, 20)
        self.assertEqual(slice_obj.width, 50)
        self.assertEqual(slice_obj.height, 60)
    
    def test_create_slice_with_object_assignment(self):
        """Test creating a slice and assigning it to an object"""
        # Setup source and object
        source = self.asset_manager.add_source(Path("test.png"), 200, 150)
        obj = self.asset_manager.add_object("Test Object")
        
        self.controller.current_source = source
        self.controller.object_combo.set_current_index(1)  # Select the object
        
        # Setup canvas with selection
        rect = self.ui_factory.create_rect(10, 20, 50, 60)
        self.controller.canvas.set_selection_rect(rect)
        
        # Setup slice name
        self.controller.slice_name_input.set_text("test_slice")
        
        # Create slice
        self.controller.create_slice()
        
        # Check that slice was added to both source and object
        self.assertEqual(len(source.slices), 1)
        self.assertEqual(len(obj.slices), 1)
        self.assertEqual(source.slices[0], obj.slices[0])


class TestTemplatesController(unittest.TestCase):
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
    
    def test_edit_template(self):
        """Test editing a template"""
        # Create a template
        template = self.asset_manager.add_template("test_template", "Original description", ["view1"])
        self.controller.current_template = template
        
        # Edit the template
        self.controller.edit_template()
        
        # Check that description was updated
        self.assertTrue(template.description.startswith("Updated:"))
    
    def test_delete_template(self):
        """Test deleting a template"""
        # Create a template
        template = self.asset_manager.add_template("test_template", "Description", ["view1"])
        self.controller.current_template = template
        
        # Setup message box to return True (Yes)
        self.controller.message_box.set_question_responses([True])
        
        # Delete the template
        self.controller.delete_template()
        
        # Check that template was deleted
        self.assertNotIn("test_template", self.asset_manager.templates)
        self.assertIsNone(self.controller.current_template)
    
    def test_delete_template_with_usage(self):
        """Test deleting a template that's in use"""
        # Create a template and an object using it
        template = self.asset_manager.add_template("test_template", "Description", ["view1"])
        obj = self.asset_manager.add_object("Test Object", "test_template")
        self.controller.current_template = template
        
        # Setup message box to return True (Yes)
        self.controller.message_box.set_question_responses([True])
        
        # Try to delete the template
        self.controller.delete_template()
        
        # Check that template was NOT deleted
        self.assertIn("test_template", self.asset_manager.templates)
        self.assertEqual(self.controller.current_template, template)
        
        # Check that warning message was shown
        messages = self.controller.message_box.get_messages()
        self.assertTrue(any("Cannot Delete Template" in msg[1] for msg in messages))
    
    def test_refresh_usage_stats(self):
        """Test refreshing usage statistics"""
        # Create a template and objects using it
        template = self.asset_manager.add_template("test_template", "Description", ["view1"])
        obj1 = self.asset_manager.add_object("Object 1", "test_template")
        obj2 = self.asset_manager.add_object("Object 2", "test_template")
        
        self.controller.current_template = template
        self.controller.refresh_usage_stats()
        
        # Check usage text
        usage_text = self.controller.usage_label.text
        self.assertIn("Used by 2 object(s)", usage_text)
        self.assertIn("Object 1", usage_text)
        self.assertIn("Object 2", usage_text)


class TestObjectsController(unittest.TestCase):
    """Test the objects controller business logic"""
    
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
        self.assertIsNotNone(self.controller.slices_list)
        self.assertIsNotNone(self.controller.create_object_btn)
        self.assertIsNotNone(self.controller.edit_object_btn)
        self.assertIsNotNone(self.controller.delete_object_btn)
        self.assertIsNone(self.controller.current_object)
    
    def test_refresh(self):
        """Test refreshing the object list"""
        # Add some objects
        obj1 = self.asset_manager.add_object("Object 1")
        obj2 = self.asset_manager.add_object("Object 2")
        
        self.controller.refresh()
        
        # Check that objects are added to list
        self.assertEqual(len(self.controller.objects_list._items), 2)
        self.assertEqual(self.controller.objects_list._items[0][0], "Object 1")
        self.assertEqual(self.controller.objects_list._items[1][0], "Object 2")
    
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
    
    def test_edit_object(self):
        """Test editing an object"""
        # Create an object
        obj = self.asset_manager.add_object("Test Object")
        self.controller.current_object = obj
        
        # Edit the object
        self.controller.edit_object()
        
        # Check that name was updated
        self.assertTrue(obj.name.startswith("Updated:"))
    
    def test_delete_object(self):
        """Test deleting an object"""
        # Create an object
        obj = self.asset_manager.add_object("Test Object")
        self.controller.current_object = obj
        
        # Setup message box to return True (Yes)
        self.controller.message_box.set_question_responses([True])
        
        # Delete the object
        self.controller.delete_object()
        
        # Check that object was deleted
        self.assertNotIn(obj.id, self.asset_manager.objects)
        self.assertIsNone(self.controller.current_object)
    
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
    
    def test_refresh_slices(self):
        """Test refreshing the slices list"""
        # Create an object with slices
        obj = self.asset_manager.add_object("Test Object")
        slice1 = ObjectSlice("slice1", "source1", 0, 0, 10, 10, "concept")
        slice2 = ObjectSlice("slice2", "source1", 0, 0, 10, 10, "working")
        obj.slices = [slice1, slice2]
        
        self.controller.current_object = obj
        self.controller.refresh_slices()
        
        # Check that slices are added to list
        self.assertEqual(len(self.controller.slices_list._items), 4)  # 2 headers + 2 slices
        self.assertEqual(self.controller.slices_list._items[0][0], "--- CONCEPT ---")
        self.assertEqual(self.controller.slices_list._items[1][0], "  slice1")
        self.assertEqual(self.controller.slices_list._items[2][0], "--- WORKING ---")
        self.assertEqual(self.controller.slices_list._items[3][0], "  slice2")


class TestIntegration(unittest.TestCase):
    """Test integration between controllers"""
    
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
    
    def test_full_workflow(self):
        """Test a complete workflow from template creation to slice creation"""
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
        
        # 4. Create a slice and assign it to the object
        self.sources_controller.current_source = source
        self.sources_controller.object_combo.set_current_index(1)  # Select the object
        
        rect = self.ui_factory.create_rect(10, 20, 50, 60)
        self.sources_controller.canvas.set_selection_rect(rect)
        self.sources_controller.slice_name_input.set_text("front")
        
        self.sources_controller.create_slice()
        
        # 5. Verify the complete workflow
        self.assertEqual(len(source.slices), 1)
        self.assertEqual(len(obj.slices), 1)
        self.assertEqual(source.slices[0].name, "front")
        self.assertEqual(obj.slices[0].name, "front")
        
        # 6. Check template compliance
        self.objects_controller.current_object = obj
        self.objects_controller.refresh_compliance()
        
        # Should show some progress (1 out of 4 views complete)
        self.assertGreater(self.objects_controller.compliance_progress.value, 0)


if __name__ == "__main__":
    unittest.main()
