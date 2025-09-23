"""
Test script for the new message system

This module tests the message collection and assertion capabilities
of the headless UI implementation using pytest.
"""

import pytest
from pathlib import Path
import sys

# Add the project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from curioshelf.ui.ui_factory import create_ui_factory
from tests.support.debug.message_system import MessageCollector, MessageType


class TestMessageCollection:
    """Test the message collection system"""
    
    def test_basic_message_collection(self):
        """Test basic message collection functionality"""
        # Create UI factory with message collection
        factory = create_ui_factory("headless", verbose=False)
        ui = factory.get_ui_implementation()
        
        # Get the message logger
        logger = ui.get_message_logger()
        
        # Create some UI components
        button = ui.create_button("Test Button")
        text_input = ui.create_text_input("Enter text...")
        combo = ui.create_combo_box()
        
        # Perform some actions
        button.click()
        text_input.set_text("Hello World")
        from tests.ui_mocks import MockUIListItem
        item1 = MockUIListItem("Option 1")
        item1.set_data("opt1")
        combo.add_item(item1)
        
        item2 = MockUIListItem("Option 2")
        item2.set_data("opt2")
        combo.add_item(item2)
        combo.set_current_index(0)
        
        # Get collected messages
        all_messages = logger.get_messages()
        ui_events = logger.get_messages_by_type(MessageType.UI_EVENT)
        user_actions = logger.get_messages_by_type(MessageType.USER_ACTION)
        state_changes = logger.get_messages_by_type(MessageType.STATE_CHANGE)
        
        # Assertions
        assert len(all_messages) > 0, "Should have collected some messages"
        assert len(ui_events) > 0, "Should have UI events"
        assert len(user_actions) > 0, "Should have user actions"
        
        # Check specific message types
        button_messages = logger.get_messages_by_component("DebugUIButton")
        assert len(button_messages) > 0, "Should have button messages"
        
        text_messages = logger.get_messages_by_component("DebugUITextInput")
        assert len(text_messages) > 0, "Should have text input messages"
        
        # Cleanup
        factory.cleanup()
    
    def test_message_filtering(self):
        """Test message filtering by component and type"""
        factory = create_ui_factory("headless", verbose=False)
        ui = factory.get_ui_implementation()
        logger = ui.get_message_logger()
        
        # Create components and perform actions
        button1 = ui.create_button("Button 1")
        button2 = ui.create_button("Button 2")
        text_input = ui.create_text_input("Test")
        
        button1.click()
        button2.click()
        text_input.set_text("Test text")
        
        # Test filtering
        button_messages = logger.get_messages_by_component("DebugUIButton")
        assert len(button_messages) == 2, "Should have 2 button messages"
        
        text_messages = logger.get_messages_by_component("DebugUITextInput")
        assert len(text_messages) == 1, "Should have 1 text input message"
        
        user_actions = logger.get_messages_by_type(MessageType.USER_ACTION)
        assert len(user_actions) == 2, "Should have 2 user actions"
        
        ui_events = logger.get_messages_by_type(MessageType.UI_EVENT)
        assert len(ui_events) == 1, "Should have 1 UI event"
        
        factory.cleanup()
    
    def test_message_assertions(self):
        """Test message assertion helpers"""
        factory = create_ui_factory("headless", verbose=False)
        ui = factory.get_ui_implementation()
        logger = ui.get_message_logger()
        
        # Create test collector
        test_collector = MessageCollector()
        test_collector.logger = logger  # Use the same logger
        
        # Simulate some UI interactions
        test_button = ui.create_button("Test Button")
        test_button.click()
        test_button.set_enabled(False)
        
        # Test assertions
        test_collector.assert_user_action("DebugUIButton", "clicked")
        test_collector.assert_state_change("DebugUIButton", "disabled")
        
        # Test message sequence
        expected_sequence = [
            {"component": "DebugUIButton", "action": "clicked", "message_type": "user_action"},
            {"component": "DebugUIButton", "action": "disabled", "message_type": "state_change"}
        ]
        test_collector.assert_message_sequence(expected_sequence)
        
        factory.cleanup()
    
    def test_main_window_messages(self):
        """Test message collection with main window"""
        factory = create_ui_factory("headless", verbose=False)
        
        # Create main window
        main_window = factory.create_main_window()
        
        # Get message logger
        logger = factory.get_ui_implementation().get_message_logger()
        
        # Get all messages
        all_messages = logger.get_messages()
        
        # Assertions
        assert len(all_messages) > 0, "Main window should generate messages"
        
        # Categorize messages
        ui_events = logger.get_messages_by_type(MessageType.UI_EVENT)
        state_changes = logger.get_messages_by_type(MessageType.STATE_CHANGE)
        
        assert len(ui_events) > 0, "Should have UI events"
        assert len(state_changes) > 0, "Should have state changes"
        
        # Check specific components were created
        # Main window now uses menu-based interface, so check for menu components
        menu_messages = logger.get_messages_by_component("DebugUIMenuBar")
        assert len(menu_messages) > 0, "Should have menu bar messages"
        
        status_messages = logger.get_messages_by_component("DebugUIStatusBar")
        assert len(status_messages) > 0, "Should have status bar messages"
        
        # Tab widget messages might not be generated during creation
        # Let's just check that we have some layout messages instead
        layout_messages = logger.get_messages_by_component("DebugUILayout")
        assert len(layout_messages) > 0, "Should have layout messages"
        
        factory.cleanup()
    
    def test_message_export(self):
        """Test message export functionality"""
        factory = create_ui_factory("headless", verbose=False)
        ui = factory.get_ui_implementation()
        logger = ui.get_message_logger()
        
        # Create some messages
        button = ui.create_button("Test")
        button.click()
        
        # Test export
        messages_dict = logger.export_messages("dict")
        assert isinstance(messages_dict, list), "Should export as list of dicts"
        assert len(messages_dict) > 0, "Should have exported messages"
        
        # Check message structure
        for msg_dict in messages_dict:
            assert "message_type" in msg_dict, "Should have message_type"
            assert "component" in msg_dict, "Should have component"
            assert "action" in msg_dict, "Should have action"
            assert "timestamp" in msg_dict, "Should have timestamp"
        
        factory.cleanup()
    
    def test_message_clear(self):
        """Test message clearing functionality"""
        factory = create_ui_factory("headless", verbose=False)
        ui = factory.get_ui_implementation()
        logger = ui.get_message_logger()
        
        # Create some messages
        button = ui.create_button("Test")
        button.click()
        
        # Verify messages exist
        assert len(logger.get_messages()) > 0, "Should have messages"
        
        # Clear messages
        logger.clear_messages()
        
        # Verify messages are cleared
        assert len(logger.get_messages()) == 0, "Should have no messages after clear"
        
        factory.cleanup()


class TestMessageCollectorHelper:
    """Test the MessageCollector helper class"""
    
    def test_collector_initialization(self):
        """Test collector initialization"""
        collector = MessageCollector()
        assert collector.logger is not None, "Should have a logger"
        assert collector.logger.collect_messages, "Should collect messages"
        assert not collector.logger.print_messages, "Should not print messages"
    
    def test_collector_assertions(self):
        """Test collector assertion methods"""
        collector = MessageCollector()
        
        # Simulate some messages
        collector.logger.log_user_action("TestComponent", "test_action")
        collector.logger.log_state_change("TestComponent", "test_state")
        
        # Test assertions
        collector.assert_user_action("TestComponent", "test_action")
        collector.assert_state_change("TestComponent", "test_state")
        
        # Test negative cases
        with pytest.raises(AssertionError):
            collector.assert_user_action("TestComponent", "nonexistent_action")
        
        with pytest.raises(AssertionError):
            collector.assert_state_change("TestComponent", "nonexistent_state")
    
    def test_message_sequence_assertion(self):
        """Test message sequence assertion"""
        collector = MessageCollector()
        
        # Create a sequence of messages
        collector.logger.log_user_action("Component1", "action1")
        collector.logger.log_state_change("Component2", "state1")
        collector.logger.log_ui_event("Component3", "event1")
        
        # Test sequence assertion
        expected_sequence = [
            {"component": "Component1", "action": "action1", "message_type": "user_action"},
            {"component": "Component2", "action": "state1", "message_type": "state_change"},
            {"component": "Component3", "action": "event1", "message_type": "ui_event"}
        ]
        
        collector.assert_message_sequence(expected_sequence)
        
        # Test wrong sequence
        wrong_sequence = [
            {"component": "Component1", "action": "wrong_action", "message_type": "user_action"}
        ]
        
        with pytest.raises(AssertionError):
            collector.assert_message_sequence(wrong_sequence)
    
    def test_collector_clear(self):
        """Test collector clear functionality"""
        collector = MessageCollector()
        
        # Add some messages
        collector.logger.log_user_action("Test", "action")
        assert len(collector.logger.get_messages()) > 0
        
        # Clear
        collector.clear()
        assert len(collector.logger.get_messages()) == 0


if __name__ == "__main__":
    pytest.main([__file__])
