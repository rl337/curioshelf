"""
Tests for the Event Execution Layer

This module tests the event execution layer that sits between UI events
and the application interface.
"""

import pytest
from pathlib import Path
from unittest.mock import Mock, MagicMock

from curioshelf.event_execution_layer import EventExecutionLayer, EventExecutor
from curioshelf.event_system import UIEvent, EventType, EventBus, event_bus
from tests.mock_application import MockCurioShelfApplication


class TestEventExecutionLayer:
    """Test the event execution layer"""
    
    def test_event_execution_layer_creation(self):
        """Test creating an event execution layer"""
        app = MockCurioShelfApplication()
        layer = EventExecutionLayer(app)
        
        assert layer.app == app
        assert layer.executor is not None
        assert isinstance(layer.executor, EventExecutor)
    
    def test_event_execution_layer_start_stop(self):
        """Test starting and stopping the event execution layer"""
        app = MockCurioShelfApplication()
        layer = EventExecutionLayer(app)
        
        layer.start()
        layer.stop()
    
    def test_get_application(self):
        """Test getting the underlying application"""
        app = MockCurioShelfApplication()
        layer = EventExecutionLayer(app)
        
        assert layer.get_application() == app


class TestEventExecutor:
    """Test the event executor"""
    
    def test_event_executor_creation(self):
        """Test creating an event executor"""
        app = MockCurioShelfApplication()
        executor = EventExecutor(app)
        
        assert executor.app == app
    
    def test_menu_click_handling(self):
        """Test handling menu click events"""
        app = MockCurioShelfApplication()
        executor = EventExecutor(app)
        
        # Create a menu click event
        event = UIEvent(
            event_type=EventType.MENU_ITEM_CLICKED,
            source="test",
            data={"menu_item": "save_project"}
        )
        
        # Mock the application methods
        app.is_project_loaded = Mock(return_value=True)
        app.save_project = Mock(return_value=True)
        
        # Handle the event
        executor._handle_menu_click(event)
        
        # Verify save_project was called
        app.save_project.assert_called_once()
    
    def test_hotkey_handling(self):
        """Test handling hotkey events"""
        app = MockCurioShelfApplication()
        executor = EventExecutor(app)
        
        # Create a hotkey event
        event = UIEvent(
            event_type=EventType.HOTKEY_PRESSED,
            source="test",
            data={"hotkey": "save_project"}
        )
        
        # Mock the application methods
        app.is_project_loaded = Mock(return_value=True)
        app.save_project = Mock(return_value=True)
        
        # Handle the event
        executor._handle_hotkey(event)
        
        # Verify save_project was called
        app.save_project.assert_called_once()
    
    def test_dialog_accepted_handling(self):
        """Test handling dialog accepted events"""
        app = MockCurioShelfApplication()
        executor = EventExecutor(app)
        
        # Create a project dialog accepted event
        event = UIEvent(
            event_type=EventType.DIALOG_ACCEPTED,
            source="test",
            data={
                "dialog_type": "project_dialog",
                "is_new_project": True,
                "project_path": "/test/project",
                "project_info": {"name": "Test Project"}
            }
        )
        
        # Mock the application methods
        app.create_project = Mock(return_value=True)
        
        # Handle the event
        executor._handle_dialog_accepted(event)
        
        # Verify create_project was called
        app.create_project.assert_called_once()
    
    def test_command_execution_save_project(self):
        """Test executing save project command"""
        app = MockCurioShelfApplication()
        executor = EventExecutor(app)
        
        # Mock the application methods
        app.is_project_loaded = Mock(return_value=True)
        app.save_project = Mock(return_value=True)
        
        # Execute the command
        executor._execute_save_project({})
        
        # Verify the application was called
        app.is_project_loaded.assert_called_once()
        app.save_project.assert_called_once()
    
    def test_command_execution_create_object(self):
        """Test executing create object command"""
        app = MockCurioShelfApplication()
        executor = EventExecutor(app)
        
        # Mock the application methods
        app.is_project_loaded = Mock(return_value=True)
        app.create_object = Mock(return_value=True)
        
        # Execute the command
        executor._execute_create_object({"object_name": "Test Object"})
        
        # Verify the application was called
        app.is_project_loaded.assert_called_once()
        app.create_object.assert_called_once_with("Test Object", None)
    
    def test_command_execution_create_template(self):
        """Test executing create template command"""
        app = MockCurioShelfApplication()
        executor = EventExecutor(app)
        
        # Mock the application methods
        app.is_project_loaded = Mock(return_value=True)
        app.create_template = Mock(return_value=True)
        
        # Execute the command
        executor._execute_create_template({
            "template_name": "Test Template",
            "description": "A test template",
            "required_views": ["front", "side"]
        })
        
        # Verify the application was called
        app.is_project_loaded.assert_called_once()
        app.create_template.assert_called_once_with("Test Template")
    
    def test_file_dialog_result_execution(self):
        """Test executing file dialog results"""
        app = MockCurioShelfApplication()
        executor = EventExecutor(app)
        
        # Mock the application methods
        app.load_project = Mock(return_value=True)
        
        # Execute file dialog result
        executor.execute_file_dialog_result("open_project", Path("/test/project"))
        
        # Verify the application was called
        app.load_project.assert_called_once_with(Path("/test/project"))
    
    def test_error_handling(self):
        """Test error handling in command execution"""
        app = MockCurioShelfApplication()
        executor = EventExecutor(app)
        
        # Mock the application to raise an exception
        app.save_project = Mock(side_effect=Exception("Test error"))
        app.is_project_loaded = Mock(return_value=True)
        
        # Execute the command - should not raise exception
        try:
            executor._execute_save_project({})
        except Exception as e:
            pytest.fail(f"Exception should have been caught: {e}")
        
        # Verify the application was called
        app.is_project_loaded.assert_called_once()
        app.save_project.assert_called_once()


class TestEventIntegration:
    """Test integration between event system and execution layer"""
    
    def test_event_bus_integration(self):
        """Test that events are properly handled through the event bus"""
        app = MockCurioShelfApplication()
        layer = EventExecutionLayer(app)
        
        # Mock the application methods
        app.save_project = Mock(return_value=True)
        app.is_project_loaded = Mock(return_value=True)
        
        # Create and emit an event
        event = UIEvent(
            event_type=EventType.MENU_ITEM_CLICKED,
            source="test",
            data={"menu_item": "save_project"}
        )
        
        # Emit the event
        event_bus.emit(event)
        
        # Give the event bus a moment to process
        import time
        time.sleep(0.1)
        
        # Verify the application was called
        app.is_project_loaded.assert_called()
        app.save_project.assert_called()
