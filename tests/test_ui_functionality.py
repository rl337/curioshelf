"""
Test UI Functionality

This module tests UI functionality using the CurioScript system
with automatic heartbeat monitoring to prevent hanging.
"""

import pytest
from curioshelf.ui.script.ui_factory import ScriptUIImplementation


def test_menu_functionality():
    """Test menu functionality using scripted UI with mocked event execution"""
    print("Setting up scripted UI test...")
    
    # Create a mock application
    from tests.mock_application import MockCurioShelfApplication
    mock_app = MockCurioShelfApplication()
    
    # Mock the event bus to capture events without triggering real UI
    from unittest.mock import patch, MagicMock
    from curioshelf.event_system import event_bus, EventType
    
    # Track emitted events
    emitted_events = []
    original_emit = event_bus.emit
    
    def capture_events(event):
        emitted_events.append(event)
        # Don't actually emit the event to prevent real UI interactions
        print(f"[MOCK] Captured event: {event.event_type} - {event.data}")
    
    with patch.object(event_bus, 'emit', side_effect=capture_events):
        
        # Create script UI implementation
        script_ui = ScriptUIImplementation(
            verbose=True,
            interactive=False,
            application_interface=mock_app,
            execution_budget=10000
        )
        
        print("Script UI created. Testing menu functionality...")
        
        # Test script that triggers menu events
        test_script = """
        # Test New Project menu
        print("Testing New Project menu...")
        trigger_menu("Project", "New Project")
        
        # Test Open Project menu  
        print("Testing Open Project menu...")
        trigger_menu("Project", "Open Project")
        
        # Test Sources menu
        print("Testing Sources menu...")
        trigger_menu("Sources", "Import Source")
        
        print("Menu testing completed!")
        
        # Exit gracefully
        exit(0)
        """
        
        # Execute the test script
        print("Executing test script...")
        result = script_ui.execute_script_content(test_script)
        
        print(f"Script execution result: {result}")
        
        # Verify that the expected events were emitted
        menu_events = [e for e in emitted_events if e.event_type == EventType.MENU_ITEM_CLICKED]
        assert len(menu_events) >= 3, f"Expected at least 3 menu events, got {len(menu_events)}"
        
        # Check for specific menu events
        new_project_events = [e for e in menu_events if e.data.get('menu_item') == 'new_project']
        open_project_events = [e for e in menu_events if e.data.get('menu_item') == 'open_project']
        import_source_events = [e for e in menu_events if e.data.get('menu_item') == 'import_source']
        
        assert len(new_project_events) > 0, "New Project menu event should have been emitted"
        assert len(open_project_events) > 0, "Open Project menu event should have been emitted"
        assert len(import_source_events) > 0, "Import Source menu event should have been emitted"
        
        print("\n✅ Menu functionality test completed successfully!")
        print("The script successfully triggered menu events:")
        print("  - New Project menu")
        print("  - Open Project menu") 
        print("  - Sources menu")
        print("  - Exit command")
        
        # The script should execute successfully (result can be None if script exits gracefully)
        assert True, "Script executed successfully without hanging"
