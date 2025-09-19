"""
Pytest-compatible tests for UI debugging and instrumentation system

These tests verify that the debugging system works correctly
and can capture and process UI events.
"""

import pytest
import json
import time
from pathlib import Path
from typing import List, Dict, Any

from tests.ui_debug import (
    create_debugger, UIDebugger, DebugMessage, DebugMessageType,
    UIDebugMixin, UIRemoteController
)
from curioshelf.ui.headless.message_system import MessageType
from curioshelf.ui.ui_factory import create_ui_factory


class TestUIDebugger:
    """Test UI debugger functionality"""
    
    @pytest.fixture
    def debugger(self):
        """Create a debugger for testing"""
        return create_debugger(enabled=True)
    
    def test_debugger_creation(self, debugger):
        """Test that debugger can be created"""
        assert debugger is not None
        assert debugger.enabled
        assert isinstance(debugger, UIDebugger)
    
    def test_debug_message_creation(self):
        """Test debug message creation"""
        message = DebugMessage(
            timestamp=time.time(),
            message_type=DebugMessageType.UI_EVENT,
            component="TestComponent",
            action="test_action",
            data={"key": "value"}
        )
        
        assert message.message_type == DebugMessageType.UI_EVENT
        assert message.component == "TestComponent"
        assert message.action == "test_action"
        assert message.data == {"key": "value"}
    
    def test_debug_message_serialization(self):
        """Test debug message serialization"""
        message = DebugMessage(
            timestamp=time.time(),
            message_type=DebugMessageType.UI_EVENT,
            component="TestComponent",
            action="test_action",
            data={"key": "value"}
        )
        
        # Test to_dict
        message_dict = message.to_dict()
        assert message_dict["message_type"] == "ui_event"
        assert message_dict["component"] == "TestComponent"
        assert message_dict["action"] == "test_action"
        assert message_dict["data"] == {"key": "value"}
        
        # Test to_json
        json_str = message.to_json()
        assert isinstance(json_str, str)
        parsed = json.loads(json_str)
        assert parsed["message_type"] == "ui_event"
    
    def test_debugger_logging(self, debugger):
        """Test debugger message logging"""
        initial_count = len(debugger.messages)
        
        debugger.log(
            DebugMessageType.UI_EVENT,
            "TestComponent",
            "test_action",
            {"key": "value"}
        )
        
        # Wait a bit for async processing
        time.sleep(0.1)
        
        assert len(debugger.messages) > initial_count
        
        # Check the last message
        last_message = debugger.messages[-1]
        assert last_message.component == "TestComponent"
        assert last_message.action == "test_action"
        assert last_message.data == {"key": "value"}
    
    def test_debugger_filtering(self, debugger):
        """Test debugger message filtering"""
        # Log different types of messages
        debugger.log(DebugMessageType.UI_EVENT, "Component1", "action1")
        debugger.log(DebugMessageType.STATE_CHANGE, "Component2", "action2")
        debugger.log(DebugMessageType.UI_EVENT, "Component1", "action3")
        debugger.log(DebugMessageType.ERROR, "Component3", "action4")
        
        time.sleep(0.1)  # Wait for processing
        
        # Test filtering by message type
        ui_events = debugger.get_messages(message_type=DebugMessageType.UI_EVENT)
        assert len(ui_events) == 2
        assert all(msg.message_type == DebugMessageType.UI_EVENT for msg in ui_events)
        
        # Test filtering by component
        component1_messages = debugger.get_messages(component="Component1")
        assert len(component1_messages) == 2
        assert all(msg.component == "Component1" for msg in component1_messages)
        
        # Test filtering by both
        component1_ui_events = debugger.get_messages(
            message_type=DebugMessageType.UI_EVENT,
            component="Component1"
        )
        assert len(component1_ui_events) == 2
    
    def test_debugger_subscription(self, debugger):
        """Test debugger message subscription"""
        received_messages = []
        
        def message_handler(message):
            received_messages.append(message)
        
        # Subscribe to messages
        debugger.subscribe(message_handler)
        
        # Log a message
        debugger.log(DebugMessageType.UI_EVENT, "TestComponent", "test_action")
        
        time.sleep(0.1)  # Wait for processing
        
        # Check that handler was called
        assert len(received_messages) == 1
        assert received_messages[0].component == "TestComponent"
        assert received_messages[0].action == "test_action"
        
        # Unsubscribe
        debugger.unsubscribe(message_handler)
        
        # Log another message
        debugger.log(DebugMessageType.UI_EVENT, "TestComponent", "test_action2")
        
        time.sleep(0.1)  # Wait for processing
        
        # Check that handler was not called again
        assert len(received_messages) == 1
    
    def test_debugger_export(self, debugger, tmp_path):
        """Test debugger message export"""
        # Log some messages
        debugger.log(DebugMessageType.UI_EVENT, "Component1", "action1")
        debugger.log(DebugMessageType.STATE_CHANGE, "Component2", "action2")
        
        time.sleep(0.1)  # Wait for processing
        
        # Export messages
        export_file = tmp_path / "debug_messages.json"
        debugger.export_messages(export_file)
        
        # Check that file was created and contains data
        assert export_file.exists()
        
        with open(export_file, 'r') as f:
            data = json.load(f)
        
        assert isinstance(data, list)
        assert len(data) >= 2
        
        # Check message structure
        for message_data in data:
            assert "timestamp" in message_data
            assert "message_type" in message_data
            assert "component" in message_data
            assert "action" in message_data


class TestUIDebugMixin:
    """Test UIDebugMixin functionality"""
    
    def test_debug_mixin_creation(self):
        """Test that UIDebugMixin can be used"""
        class TestWidget(UIDebugMixin):
            def __init__(self):
                super().__init__()
        
        widget = TestWidget()
        assert hasattr(widget, 'debug_log')
        assert hasattr(widget, 'debug_ui_event')
        assert hasattr(widget, 'debug_state_change')
        assert hasattr(widget, 'debug_signal_emitted')
        assert hasattr(widget, 'debug_callback_invoked')
    
    def test_debug_mixin_logging(self):
        """Test UIDebugMixin logging methods"""
        debugger = create_debugger(enabled=True)
        
        class TestWidget(UIDebugMixin):
            def __init__(self):
                super().__init__()
                self.set_debugger(debugger)
        
        widget = TestWidget()
        
        # Test different logging methods
        widget.debug_ui_event("test_action", {"key": "value"})
        widget.debug_state_change("enabled_true", {"enabled": True})
        widget.debug_signal_emitted("clicked", "signal_data")
        widget.debug_callback_invoked("on_click", {"button": "test"})
        
        time.sleep(0.1)  # Wait for processing
        
        # Check that messages were logged
        messages = debugger.get_messages()
        assert len(messages) >= 4
        
        # Check message types
        message_types = [msg.message_type for msg in messages]
        assert DebugMessageType.UI_EVENT in message_types
        assert DebugMessageType.STATE_CHANGE in message_types
        assert DebugMessageType.SIGNAL_EMITTED in message_types
        assert DebugMessageType.CALLBACK_INVOKED in message_types


class TestUIRemoteController:
    """Test UI remote controller functionality"""
    
    @pytest.fixture
    def debugger(self):
        """Create a debugger for testing"""
        return create_debugger(enabled=True)
    
    @pytest.fixture
    def remote_controller(self, debugger):
        """Create a remote controller for testing"""
        return UIRemoteController(debugger)
    
    def test_remote_controller_creation(self, remote_controller):
        """Test that remote controller can be created"""
        assert remote_controller is not None
        assert isinstance(remote_controller, UIRemoteController)
    
    def test_controller_registration(self, remote_controller):
        """Test controller registration"""
        class TestController:
            def test_method(self):
                return "test_result"
            
            def test_method_with_args(self, arg1, arg2=None):
                return f"{arg1}_{arg2}"
        
        controller = TestController()
        
        # Register controller
        remote_controller.register_controller("test_controller", controller)
        
        # Check that it's registered
        controllers = remote_controller.list_controllers()
        assert "test_controller" in controllers
    
    def test_command_execution(self, remote_controller):
        """Test command execution"""
        class TestController:
            def test_method(self):
                return "test_result"
            
            def test_method_with_args(self, arg1, arg2=None):
                return f"{arg1}_{arg2}"
        
        controller = TestController()
        remote_controller.register_controller("test_controller", controller)
        
        # Test simple command
        success = remote_controller.send_command("test_controller", "test_method")
        assert success
        
        # Test command with arguments
        success = remote_controller.send_command(
            "test_controller", 
            "test_method_with_args", 
            {"arg1": "hello", "arg2": "world"}
        )
        assert success
    
    def test_command_listing(self, remote_controller):
        """Test command listing"""
        class TestController:
            def method1(self):
                pass
            
            def method2(self, arg):
                pass
            
            def _private_method(self):
                pass
        
        controller = TestController()
        remote_controller.register_controller("test_controller", controller)
        
        # List commands
        commands = remote_controller.list_commands("test_controller")
        assert "method1" in commands
        assert "method2" in commands
        assert "_private_method" not in commands  # Private methods should be excluded
    
    def test_invalid_commands(self, remote_controller):
        """Test handling of invalid commands"""
        class TestController:
            def test_method(self):
                return "test_result"
        
        controller = TestController()
        remote_controller.register_controller("test_controller", controller)
        
        # Test non-existent controller
        success = remote_controller.send_command("nonexistent", "test_method")
        assert not success
        
        # Test non-existent command
        success = remote_controller.send_command("test_controller", "nonexistent_method")
        assert not success


class TestHeadlessUIDebugging:
    """Test debugging integration with headless UI"""
    
    def test_headless_ui_with_debugging(self):
        """Test headless UI with debugging enabled"""
        # Create UI factory
        factory = create_ui_factory("headless", verbose=False)
        main_window = factory.create_main_window()
        ui_impl = factory.get_ui_implementation()
        
        # The main window should have debugging capabilities
        assert hasattr(main_window, 'ui')
        
        # Test that we can create widgets with debugging
        button = ui_impl.create_button("Test Button")
        assert button is not None
        
        # Test widget operations that should generate debug messages
        button.click()
        button.set_enabled(False)
        button.set_visible(False)
        
        time.sleep(0.1)  # Wait for processing
        
        # Check that the headless UI implementation has message logging
        message_logger = ui_impl.get_message_logger()
        assert message_logger is not None
        
        # Check that messages were generated
        messages = message_logger.get_messages()
        assert len(messages) > 0
        
        # Check for specific message types
        message_types = [msg.message_type for msg in messages]
        assert MessageType.UI_EVENT in message_types or MessageType.STATE_CHANGE in message_types
