"""
Tests for business logic with message system integration

This module demonstrates how to use the new message system for testing
business logic controllers with the headless UI implementation.
"""

import pytest
from pathlib import Path
import sys

# Add the project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from curioshelf.models import AssetManager, AssetSource, ObjectSlice, CurioObject, Template
from curioshelf.app_impl.controllers import SourcesController, TemplatesController, ObjectsController
from gui.ui_factory import create_ui_factory
from gui.headless.message_system import MessageCollector, MessageType


class TestBusinessLogicWithMessages:
    """Test business logic with message system integration"""
    
    def test_sources_controller_with_messages(self):
        """Test sources controller using headless UI and message collection"""
        # Create UI factory with message collection
        factory = create_ui_factory("headless", verbose=False)
        ui = factory.get_ui_implementation()
        logger = ui.get_message_logger()
        
        # Create asset manager and controller
        asset_manager = AssetManager()
        controller = SourcesController(asset_manager, ui)
        controller.setup_ui(ui)
        
        # Test initial state
        assert controller.import_btn is not None
        assert controller.source_combo is not None
        assert controller.canvas is not None
        assert controller.current_source is None
        
        # Test adding sources
        source1 = asset_manager.add_source(Path("test1.png"), 100, 100)
        source2 = asset_manager.add_source(Path("test2.png"), 200, 150)
        
        # Refresh the combo box
        controller.refresh_source_combo()
        
        # Test user interactions that should generate messages
        controller.import_btn.click()
        
        # Check that button click was logged
        user_actions = logger.get_messages_by_type(MessageType.USER_ACTION)
        assert len(user_actions) > 0, "Should have user action messages"
        
        # Test combo box interactions
        controller.source_combo.set_current_index(0)
        
        # Check that combo box interactions were logged
        combo_events = logger.get_messages_by_component("HeadlessUIComboBox")
        assert len(combo_events) > 0, "Should have combo box interaction messages"
        
        factory.cleanup()
    
    def test_templates_controller_with_messages(self):
        """Test templates controller using headless UI and message collection"""
        factory = create_ui_factory("headless", verbose=False)
        ui = factory.get_ui_implementation()
        logger = ui.get_message_logger()
        
        asset_manager = AssetManager()
        controller = TemplatesController(asset_manager, ui)
        controller.setup_ui(ui)
        
        # Test initial state
        assert controller.templates_list is not None
        assert controller.template_name_label is not None
        assert controller.template_description_label is not None
        assert controller.views_widget is not None
        
        # Test adding templates
        template1 = asset_manager.add_template("character", "Character template", ["front", "back"])
        template2 = asset_manager.add_template("tile", "Tile template", ["base", "variant"])
        
        # Refresh the list
        controller.refresh()
        
        # Test user interactions
        controller.templates_list.set_current_index(0)
        
        # Check that interactions were logged
        list_events = logger.get_messages_by_component("HeadlessUIListWidget")
        assert len(list_events) > 0, "Should have list widget interaction messages"
        
        factory.cleanup()
    
    def test_objects_controller_with_messages(self):
        """Test objects controller using headless UI and message collection"""
        factory = create_ui_factory("headless", verbose=False)
        ui = factory.get_ui_implementation()
        logger = ui.get_message_logger()
        
        asset_manager = AssetManager()
        controller = ObjectsController(asset_manager, ui)
        controller.setup_ui(ui)
        
        # Test initial state
        assert controller.objects_list is not None
        assert controller.object_name_label is not None
        assert controller.object_template_label is not None
        assert controller.compliance_progress is not None
        
        # Test adding objects
        template = asset_manager.add_template("character", "Character template", ["front", "back"])
        obj1 = asset_manager.add_object("hero", "character")
        obj2 = asset_manager.add_object("villain", "character")
        
        # Refresh the list
        controller.refresh()
        
        # Test user interactions
        controller.objects_list.set_current_index(0)
        
        # Check that interactions were logged
        list_events = logger.get_messages_by_component("HeadlessUIListWidget")
        assert len(list_events) > 0, "Should have list widget interaction messages"
        
        factory.cleanup()
    
    def test_user_interactions_with_messages(self):
        """Test user interactions and message collection"""
        factory = create_ui_factory("headless", verbose=False)
        ui = factory.get_ui_implementation()
        logger = ui.get_message_logger()
        
        # Create a simple UI
        button = ui.create_button("Test Button")
        text_input = ui.create_text_input("Enter text...")
        
        # Perform user actions
        button.click()
        text_input.set_text("Hello World")
        
        # Check that user actions were logged
        user_actions = logger.get_messages_by_type(MessageType.USER_ACTION)
        assert len(user_actions) == 1, "Should have 1 user action"
        assert user_actions[0].action == "clicked"
        assert user_actions[0].component == "HeadlessUIButton"
        
        # Check that UI events were logged
        ui_events = logger.get_messages_by_type(MessageType.UI_EVENT)
        assert len(ui_events) == 1, "Should have 1 UI event"
        assert ui_events[0].action == "text_changed"
        assert ui_events[0].component == "HeadlessUITextInput"
        
        factory.cleanup()
    
    def test_message_assertions_in_business_logic(self):
        """Test using message assertions in business logic testing"""
        factory = create_ui_factory("headless", verbose=False)
        ui = factory.get_ui_implementation()
        logger = ui.get_message_logger()
        
        # Create message collector
        collector = MessageCollector()
        collector.logger = logger
        
        # Create asset manager and controller
        asset_manager = AssetManager()
        controller = SourcesController(asset_manager, ui)
        controller.setup_ui(ui)
        
        # Test user interactions that generate messages
        controller.import_btn.click()
        collector.assert_user_action("HeadlessUIButton", "clicked")
        
        # Test state changes
        controller.source_combo.set_enabled(False)
        collector.assert_state_change("HeadlessUIComboBox", "disabled")
        
        factory.cleanup()
    
    def test_message_sequence_in_business_logic(self):
        """Test message sequence assertions in business logic"""
        factory = create_ui_factory("headless", verbose=False)
        ui = factory.get_ui_implementation()
        logger = ui.get_message_logger()
        
        # Create message collector
        collector = MessageCollector()
        collector.logger = logger
        
        # Create a workflow
        button = ui.create_button("Create")
        text_input = ui.create_text_input("Name")
        
        # Simulate a workflow
        text_input.set_text("Test Object")
        button.click()
        
        # Test sequence
        expected_sequence = [
            {"component": "HeadlessUITextInput", "action": "text_changed", "message_type": "ui_event"},
            {"component": "HeadlessUIButton", "action": "clicked", "message_type": "user_action"}
        ]
        
        collector.assert_message_sequence(expected_sequence)
        
        factory.cleanup()


if __name__ == "__main__":
    pytest.main([__file__])
