#!/usr/bin/env python3
"""
Test script for the new message system

This script demonstrates the message collection and assertion capabilities
of the headless UI implementation.
"""

import sys
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from gui.ui_factory import create_ui_factory
from gui.headless.message_system import TestMessageCollector, MessageType


def test_message_collection():
    """Test the message collection system"""
    print("=" * 80)
    print("TESTING MESSAGE COLLECTION SYSTEM")
    print("=" * 80)
    
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
    combo.add_item("Option 1", "opt1")
    combo.add_item("Option 2", "opt2")
    combo.set_current_index(0)
    
    # Get collected messages
    all_messages = logger.get_messages()
    ui_events = logger.get_messages_by_type(MessageType.UI_EVENT)
    user_actions = logger.get_messages_by_type(MessageType.USER_ACTION)
    state_changes = logger.get_messages_by_type(MessageType.STATE_CHANGE)
    
    print(f"\nTotal messages collected: {len(all_messages)}")
    print(f"UI Events: {len(ui_events)}")
    print(f"User Actions: {len(user_actions)}")
    print(f"State Changes: {len(state_changes)}")
    
    print("\nAll messages:")
    for i, msg in enumerate(all_messages):
        print(f"  {i+1}. {msg}")
    
    print("\nUI Events:")
    for msg in ui_events:
        print(f"  - {msg}")
    
    print("\nUser Actions:")
    for msg in user_actions:
        print(f"  - {msg}")
    
    print("\nState Changes:")
    for msg in state_changes:
        print(f"  - {msg}")
    
    # Test message filtering
    button_messages = logger.get_messages_by_component("HeadlessUIButton")
    print(f"\nButton-specific messages: {len(button_messages)}")
    for msg in button_messages:
        print(f"  - {msg}")
    
    # Test assertions
    print("\n" + "=" * 50)
    print("TESTING ASSERTIONS")
    print("=" * 50)
    
    # Create test collector
    test_collector = TestMessageCollector()
    
    # Simulate some UI interactions
    test_button = ui.create_button("Test Button 2")
    test_button.click()
    test_button.set_enabled(False)
    
    # Test assertions
    try:
        test_collector.assert_user_action("HeadlessUIButton", "clicked")
        print("✅ User action assertion passed")
    except AssertionError as e:
        print(f"❌ User action assertion failed: {e}")
    
    try:
        test_collector.assert_state_change("HeadlessUIButton", "disabled")
        print("✅ State change assertion passed")
    except AssertionError as e:
        print(f"❌ State change assertion failed: {e}")
    
    # Test message sequence
    try:
        expected_sequence = [
            {"component": "HeadlessUIButton", "action": "clicked", "message_type": "user_action"},
            {"component": "HeadlessUIButton", "action": "disabled", "message_type": "state_change"}
        ]
        test_collector.assert_message_sequence(expected_sequence)
        print("✅ Message sequence assertion passed")
    except AssertionError as e:
        print(f"❌ Message sequence assertion failed: {e}")
    
    # Cleanup
    factory.cleanup()
    print("\n✅ Message system test completed!")


def test_main_window_messages():
    """Test message collection with main window"""
    print("\n" + "=" * 80)
    print("TESTING MAIN WINDOW MESSAGE COLLECTION")
    print("=" * 80)
    
    # Create UI factory
    factory = create_ui_factory("headless", verbose=False)
    
    # Create main window
    main_window = factory.create_main_window()
    
    # Get message logger
    logger = factory.get_ui_implementation().get_message_logger()
    
    # Get all messages
    all_messages = logger.get_messages()
    
    print(f"Main window generated {len(all_messages)} messages")
    
    # Categorize messages
    ui_events = logger.get_messages_by_type(MessageType.UI_EVENT)
    state_changes = logger.get_messages_by_type(MessageType.STATE_CHANGE)
    
    print(f"UI Events: {len(ui_events)}")
    print(f"State Changes: {len(state_changes)}")
    
    # Show some example messages
    print("\nFirst 10 messages:")
    for i, msg in enumerate(all_messages[:10]):
        print(f"  {i+1}. {msg}")
    
    if len(all_messages) > 10:
        print(f"  ... and {len(all_messages) - 10} more messages")
    
    # Test specific assertions
    test_collector = TestMessageCollector()
    test_collector.logger = logger  # Use the same logger
    
    try:
        # Check that buttons were created and configured
        button_messages = logger.get_messages_by_component("HeadlessUIButton")
        assert len(button_messages) > 0, "No button messages found"
        print("✅ Button creation messages found")
        
        # Check that text inputs were created
        text_messages = logger.get_messages_by_component("HeadlessUITextInput")
        assert len(text_messages) > 0, "No text input messages found"
        print("✅ Text input creation messages found")
        
        # Check that tabs were created
        tab_messages = logger.get_messages_by_component("HeadlessUITabWidget")
        assert len(tab_messages) > 0, "No tab widget messages found"
        print("✅ Tab widget creation messages found")
        
    except AssertionError as e:
        print(f"❌ Assertion failed: {e}")
    
    # Cleanup
    factory.cleanup()
    print("✅ Main window message test completed!")


if __name__ == "__main__":
    test_message_collection()
    test_main_window_messages()
    
    print("\n" + "=" * 80)
    print("ALL TESTS COMPLETED!")
    print("=" * 80)
