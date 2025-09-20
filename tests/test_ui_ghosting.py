"""
Tests for UI ghosting behavior - ensuring menu items are properly enabled/disabled
based on application state
"""

import pytest
import tempfile
from pathlib import Path
from unittest.mock import Mock, patch

from curioshelf.app_impl.application_impl import CurioShelfApplicationImpl
from curioshelf.mock_application import MockCurioShelfApplication
from curioshelf.ui.headless.ui_factory import HeadlessUIImplementation
from curioshelf.ui.main_window_abstracted import MainWindowAbstracted
from curioshelf.projects import ProjectMetadata, ProjectInfo
from curioshelf.event_system import UIEvent, EventType, event_bus


class TestUIGhostingBehavior:
    """Test that UI elements are properly ghosted based on application state"""
    
    def test_initial_menu_state_no_project(self):
        """Test initial menu state when no project is loaded"""
        ui = HeadlessUIImplementation(verbose=False, collect_messages=True)
        app = MockCurioShelfApplication()
        main_window = MainWindowAbstracted(ui, app, use_mock=True)
        
        # Check initial state - no project loaded
        assert not app.is_project_loaded(), "No project should be loaded initially"
        
        # Project menu items
        assert main_window.actions["new_project"].enabled, "New Project should be enabled"
        assert main_window.actions["open_project"].enabled, "Open Project should be enabled"
        assert not main_window.actions["save_project"].enabled, "Save Project should be disabled"
        assert not main_window.actions["close_project"].enabled, "Close Project should be disabled"
        
        # Asset menu items
        assert not main_window.actions["import_source"].enabled, "Import Source should be disabled"
        assert not main_window.actions["export_assets"].enabled, "Export Assets should be disabled"
        assert not main_window.actions["create_object"].enabled, "Create Object should be disabled"
        assert not main_window.actions["create_template"].enabled, "Create Template should be disabled"
    
    def test_menu_state_after_project_creation(self):
        """Test menu state after creating a project"""
        ui = HeadlessUIImplementation(verbose=False, collect_messages=True)
        app = MockCurioShelfApplication()
        main_window = MainWindowAbstracted(ui, app, use_mock=True)
        
        # Create a project
        project_info = ProjectInfo(name="Test Project", author="User", description="Test")
        app.create_project(Path("/tmp/test"), project_info)
        
        # Update menu state
        main_window._update_menu_state()
        
        # Check state after project creation
        assert app.is_project_loaded(), "Project should be loaded"
        
        # Project menu items
        assert not main_window.actions["new_project"].enabled, "New Project should be disabled"
        assert not main_window.actions["open_project"].enabled, "Open Project should be disabled"
        assert main_window.actions["save_project"].enabled, "Save Project should be enabled"
        assert main_window.actions["close_project"].enabled, "Close Project should be enabled"
        
        # Asset menu items (no sources yet)
        assert main_window.actions["import_source"].enabled, "Import Source should be enabled"
        assert not main_window.actions["export_assets"].enabled, "Export Assets should be disabled"
        assert not main_window.actions["create_object"].enabled, "Create Object should be disabled"
        assert not main_window.actions["create_template"].enabled, "Create Template should be disabled"
    
    def test_menu_state_with_sources(self):
        """Test menu state after adding sources"""
        ui = HeadlessUIImplementation(verbose=False, collect_messages=True)
        app = MockCurioShelfApplication()
        main_window = MainWindowAbstracted(ui, app, use_mock=True)
        
        # Create a project and add sources
        project_info = ProjectInfo(name="Test Project", author="User", description="Test")
        app.create_project(Path("/tmp/test"), project_info)
        app.add_source("test_source")  # Mock adding a source
        
        # Update menu state
        main_window._update_menu_state()
        
        # Check state with sources
        assert app.has_sources(), "Should have sources"
        
        # Asset menu items
        assert main_window.actions["import_source"].enabled, "Import Source should be enabled"
        assert main_window.actions["export_assets"].enabled, "Export Assets should be enabled"
        assert main_window.actions["create_object"].enabled, "Create Object should be enabled"
        assert not main_window.actions["create_template"].enabled, "Create Template should be disabled"
    
    def test_menu_state_with_objects(self):
        """Test menu state after adding objects"""
        ui = HeadlessUIImplementation(verbose=False, collect_messages=True)
        app = MockCurioShelfApplication()
        main_window = MainWindowAbstracted(ui, app, use_mock=True)
        
        # Create a project and add sources and objects
        project_info = ProjectInfo(name="Test Project", author="User", description="Test")
        app.create_project(Path("/tmp/test"), project_info)
        app.add_source("test_source")
        app.add_object("test_object")
        
        # Update menu state
        main_window._update_menu_state()
        
        # Check state with objects
        assert app.has_objects(), "Should have objects"
        
        # Asset menu items
        assert main_window.actions["import_source"].enabled, "Import Source should be enabled"
        assert main_window.actions["export_assets"].enabled, "Export Assets should be enabled"
        assert main_window.actions["create_object"].enabled, "Create Object should be enabled"
        assert main_window.actions["create_template"].enabled, "Create Template should be enabled"
    
    def test_menu_state_after_project_close(self):
        """Test menu state after closing a project"""
        ui = HeadlessUIImplementation(verbose=False, collect_messages=True)
        app = MockCurioShelfApplication()
        main_window = MainWindowAbstracted(ui, app, use_mock=True)
        
        # Create a project
        project_info = ProjectInfo(name="Test Project", author="User", description="Test")
        app.create_project(Path("/tmp/test"), project_info)
        main_window._update_menu_state()
        
        # Verify project is loaded
        assert app.is_project_loaded(), "Project should be loaded"
        assert main_window.actions["close_project"].enabled, "Close Project should be enabled"
        
        # Close the project
        app.close_project()
        main_window._update_menu_state()
        
        # Check state after closing
        assert not app.is_project_loaded(), "Project should be closed"
        
        # Project menu items should return to initial state
        assert main_window.actions["new_project"].enabled, "New Project should be enabled"
        assert main_window.actions["open_project"].enabled, "Open Project should be enabled"
        assert not main_window.actions["save_project"].enabled, "Save Project should be disabled"
        assert not main_window.actions["close_project"].enabled, "Close Project should be disabled"
        
        # Asset menu items should be disabled
        assert not main_window.actions["import_source"].enabled, "Import Source should be disabled"
        assert not main_window.actions["export_assets"].enabled, "Export Assets should be disabled"
        assert not main_window.actions["create_object"].enabled, "Create Object should be disabled"
        assert not main_window.actions["create_template"].enabled, "Create Template should be disabled"


class TestMenuClickBehavior:
    """Test that disabled menu items don't execute their callbacks"""
    
    def test_disabled_menu_item_click_ignored(self):
        """Test that clicking a disabled menu item doesn't execute the callback"""
        ui = HeadlessUIImplementation(verbose=False, collect_messages=True)
        app = MockCurioShelfApplication()
        main_window = MainWindowAbstracted(ui, app, use_mock=True)
        
        # Capture events to verify no execution
        events = []
        def capture_event(event):
            events.append(event)
        
        event_bus.subscribe(EventType.SUCCESS, capture_event)
        event_bus.subscribe(EventType.ERROR, capture_event)
        
        # Initially no project loaded - close project should be disabled
        close_project_item = main_window.actions["close_project"]
        assert not close_project_item.enabled, "Close Project should be disabled"
        
        # Try to click the disabled menu item
        # This should not execute the callback
        close_project_item._on_clicked()
        
        # Verify no events were emitted (no project operations occurred)
        success_events = [e for e in events if e.event_type == EventType.SUCCESS]
        assert len(success_events) == 0, "No success events should be emitted for disabled menu item"
        
        # Verify project is still not loaded
        assert not app.is_project_loaded(), "Project should still not be loaded"
    
    def test_enabled_menu_item_click_executes(self):
        """Test that clicking an enabled menu item executes the callback"""
        ui = HeadlessUIImplementation(verbose=False, collect_messages=True)
        app = MockCurioShelfApplication()
        main_window = MainWindowAbstracted(ui, app, use_mock=True)
        
        # Capture events to verify execution
        events = []
        def capture_event(event):
            events.append(event)
        
        event_bus.subscribe(EventType.SUCCESS, capture_event)
        event_bus.subscribe(EventType.ERROR, capture_event)
        
        # New project should be enabled initially
        new_project_item = main_window.actions["new_project"]
        assert new_project_item.enabled, "New Project should be enabled"
        
        # Click the enabled menu item
        new_project_item._on_clicked()
        
        # Verify events were emitted
        success_events = [e for e in events if e.event_type == EventType.SUCCESS]
        assert len(success_events) > 0, "Success events should be emitted for enabled menu item"
        
        # Verify project was created
        assert app.is_project_loaded(), "Project should be loaded after clicking New Project"
    
    def test_menu_state_updates_after_operations(self):
        """Test that menu state updates automatically after operations"""
        ui = HeadlessUIImplementation(verbose=False, collect_messages=True)
        app = MockCurioShelfApplication()
        main_window = MainWindowAbstracted(ui, app, use_mock=True)
        
        # Initially no project
        assert not main_window.actions["close_project"].enabled, "Close Project should be disabled initially"
        
        # Create project
        project_info = ProjectInfo(name="Test Project", author="User", description="Test")
        app.create_project(Path("/tmp/test"), project_info)
        
        # Update menu state
        main_window._update_menu_state()
        
        # Now close project should be enabled
        assert main_window.actions["close_project"].enabled, "Close Project should be enabled after project creation"
        
        # Close project
        app.close_project()
        main_window._update_menu_state()
        
        # Close project should be disabled again
        assert not main_window.actions["close_project"].enabled, "Close Project should be disabled after project close"


class TestUIStateConsistency:
    """Test that UI state remains consistent across operations"""
    
    def test_state_callback_updates(self):
        """Test that state callbacks properly update UI elements"""
        ui = HeadlessUIImplementation(verbose=False, collect_messages=True)
        app = MockCurioShelfApplication()
        main_window = MainWindowAbstracted(ui, app, use_mock=True)
        
        # Get a menu item with state callback
        close_project_item = main_window.actions["close_project"]
        
        # Initially disabled
        assert not close_project_item.enabled, "Should be disabled initially"
        
        # Create project
        project_info = ProjectInfo(name="Test Project", author="User", description="Test")
        app.create_project(Path("/tmp/test"), project_info)
        
        # Update the specific state
        close_project_item.update_state("enabled")
        
        # Should now be enabled
        assert close_project_item.enabled, "Should be enabled after state update"
        
        # Close project
        app.close_project()
        
        # Update the specific state
        close_project_item.update_state("enabled")
        
        # Should be disabled again
        assert not close_project_item.enabled, "Should be disabled after project close"
    
    def test_all_states_update_together(self):
        """Test that update_all_states updates all menu items"""
        ui = HeadlessUIImplementation(verbose=False, collect_messages=True)
        app = MockCurioShelfApplication()
        main_window = MainWindowAbstracted(ui, app, use_mock=True)
        
        # Create project
        project_info = ProjectInfo(name="Test Project", author="User", description="Test")
        app.create_project(Path("/tmp/test"), project_info)
        
        # Update all states
        main_window._update_menu_state()
        
        # All project-related items should be in correct state
        assert not main_window.actions["new_project"].enabled, "New Project should be disabled"
        assert not main_window.actions["open_project"].enabled, "Open Project should be disabled"
        assert main_window.actions["save_project"].enabled, "Save Project should be enabled"
        assert main_window.actions["close_project"].enabled, "Close Project should be enabled"
        assert main_window.actions["import_source"].enabled, "Import Source should be enabled"


class TestUIStateEdgeCases:
    """Test edge cases in UI state management"""
    
    def test_menu_item_without_state_callback(self):
        """Test menu items that don't have state callbacks"""
        ui = HeadlessUIImplementation(verbose=False, collect_messages=True)
        app = MockCurioShelfApplication()
        main_window = MainWindowAbstracted(ui, app, use_mock=True)
        
        # Create a menu item without state callback
        from curioshelf.ui.headless.ui_widgets import HeadlessUIMenuItem
        test_item = HeadlessUIMenuItem("Test Item")
        
        # Should not crash when updating state
        test_item.update_state("enabled")
        test_item.update_all_states()
        
        # Should remain in its current state
        assert test_item.enabled, "Should remain enabled"
    
    def test_invalid_state_name(self):
        """Test updating with invalid state name"""
        ui = HeadlessUIImplementation(verbose=False, collect_messages=True)
        app = MockCurioShelfApplication()
        main_window = MainWindowAbstracted(ui, app, use_mock=True)
        
        close_project_item = main_window.actions["close_project"]
        
        # Update with invalid state name
        close_project_item.update_state("invalid_state")
        
        # Should not crash and should remain in current state
        assert not close_project_item.enabled, "Should remain disabled"
    
    def test_state_callback_returns_false(self):
        """Test state callback that returns False"""
        ui = HeadlessUIImplementation(verbose=False, collect_messages=True)
        app = MockCurioShelfApplication()
        main_window = MainWindowAbstracted(ui, app, use_mock=True)
        
        # Set up a state callback that returns False
        test_item = main_window.actions["close_project"]
        test_item.set_enabled_callback(lambda: False)
        
        # Update state
        test_item.update_state("enabled")
        
        # Should be disabled
        assert not test_item.enabled, "Should be disabled when callback returns False"
