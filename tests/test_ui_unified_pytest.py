"""
Unified pytest-compatible tests for UI implementations

These tests work with both headless and Qt implementations using the
embedded test mode functionality in the UI abstraction layer.
"""

import pytest
import time
from typing import List, Dict, Any

from gui.ui_factory import create_ui_factory


class TestUIUnified:
    """Unified tests that work with both headless and Qt implementations"""
    
    @pytest.fixture(params=["headless", "qt"])
    def ui_factory(self, request):
        """Create UI factory for both headless and Qt implementations"""
        backend = request.param
        factory = create_ui_factory(backend, verbose=False)
        yield factory
    
    def test_ui_factory_creation(self, ui_factory):
        """Test that UI factory can be created"""
        assert ui_factory is not None
        assert hasattr(ui_factory, 'get_ui_implementation')
    
    def test_ui_implementation_creation(self, ui_factory):
        """Test that UI implementation can be created"""
        ui_impl = ui_factory.get_ui_implementation()
        assert ui_impl is not None
        assert hasattr(ui_impl, 'create_button')
        assert hasattr(ui_impl, 'create_text_input')
        assert hasattr(ui_impl, 'create_combo_box')
        assert hasattr(ui_impl, 'enable_test_mode')
        assert hasattr(ui_impl, 'disable_test_mode')
        assert hasattr(ui_impl, 'is_test_mode')
    
    def test_widget_creation(self, ui_factory):
        """Test that all widget types can be created"""
        ui_impl = ui_factory.get_ui_implementation()
        widget_types = [
            'button', 'text_input', 'combo_box', 'list_widget', 
            'canvas', 'progress_bar', 'group_box', 'tab_widget', 
            'splitter'
        ]
        
        for widget_type in widget_types:
            creator_method = getattr(ui_impl, f'create_{widget_type}')
            widget = creator_method()
            assert widget is not None
            assert hasattr(widget, 'set_enabled')
            assert hasattr(widget, 'set_visible')
            assert hasattr(widget, 'show')
        
        # Test layout separately (it's not a widget)
        layout = ui_impl.create_layout("vertical")
        assert layout is not None
        assert hasattr(layout, 'add_widget')
        assert hasattr(layout, 'remove_widget')
    
    def test_widget_operations(self, ui_factory):
        """Test widget operations"""
        ui_impl = ui_factory.get_ui_implementation()
        button = ui_impl.create_button("Test Button")
        
        # Test button state changes
        button.set_enabled(False)
        assert not button.enabled
        
        button.set_enabled(True)
        assert button.enabled
        
        button.set_visible(False)
        assert not button.visible
        
        button.set_visible(True)
        assert button.visible
    
    def test_text_input_operations(self, ui_factory):
        """Test text input operations"""
        ui_impl = ui_factory.get_ui_implementation()
        text_input = ui_impl.create_text_input("Placeholder")
        
        # Test text operations
        text_input.set_text("Test Text")
        assert text_input.text == "Test Text"
        
        text_input.text = "New Text"
        assert text_input.text == "New Text"
    
    def test_combo_box_operations(self, ui_factory):
        """Test combo box operations"""
        ui_impl = ui_factory.get_ui_implementation()
        combo = ui_impl.create_combo_box()
        
        # Test adding items
        combo.add_item("Item 1", "data1")
        combo.add_item("Item 2", "data2")
        combo.add_item("Item 3", "data3")
        
        # Qt automatically selects the first item, headless doesn't
        if ui_factory.ui_backend == "qt":
            assert combo.current_text() == "Item 1"
            assert combo.current_data() == "data1"
        else:
            assert combo.current_text() == ""
            assert combo.current_data() is None
        
        # Test selection
        combo.set_current_index(1)
        assert combo.current_text() == "Item 2"
        assert combo.current_data() == "data2"
        
        # Test clearing
        combo.clear()
        assert combo.current_text() == ""
        assert combo.current_data() is None
    
    def test_list_widget_operations(self, ui_factory):
        """Test list widget operations"""
        ui_impl = ui_factory.get_ui_implementation()
        list_widget = ui_impl.create_list_widget()
        
        # Test adding items
        list_widget.add_item("Item 1", "data1")
        list_widget.add_item("Item 2", "data2")
        list_widget.add_item("Item 3", "data3")
        
        assert list_widget.current_text() == ""
        assert list_widget.current_data() is None
        
        # Test selection
        list_widget.set_current_index(1)
        assert list_widget.current_text() == "Item 2"
        assert list_widget.current_data() == "data2"
        
        # Test clearing
        list_widget.clear()
        assert list_widget.current_text() == ""
        assert list_widget.current_data() is None
    
    def test_progress_bar_operations(self, ui_factory):
        """Test progress bar operations"""
        ui_impl = ui_factory.get_ui_implementation()
        progress = ui_impl.create_progress_bar()
        
        # Test initial values
        assert progress.value == 0
        assert progress.minimum == 0
        assert progress.maximum == 100
        
        # Test value changes
        progress.value = 50
        assert progress.value == 50
        
        progress.value = 150  # Should be clamped to maximum
        assert progress.value == 100
        
        progress.value = -10  # Should be clamped to minimum
        assert progress.value == 0
    
    def test_layout_operations(self, ui_factory):
        """Test layout operations"""
        ui_impl = ui_factory.get_ui_implementation()
        layout = ui_impl.create_layout("vertical")
        button = ui_impl.create_button("Test")
        text_input = ui_impl.create_text_input("Test")
        
        # Test adding widgets to layout
        layout.add_widget(button)
        layout.add_widget(text_input)
        
        # Test removing widgets from layout
        layout.remove_widget(button)
        layout.remove_widget(text_input)
    
    def test_main_window_creation(self, ui_factory):
        """Test main window creation"""
        main_window = ui_factory.create_main_window()
        
        assert main_window is not None
        assert hasattr(main_window, 'main_widget')
        assert hasattr(main_window, 'tab_widget')
        assert hasattr(main_window, 'status_label')
        assert hasattr(main_window, 'progress_label')
        assert hasattr(main_window, 'project_status_label')
    
    def test_main_window_methods(self, ui_factory):
        """Test main window method calls"""
        main_window = ui_factory.create_main_window()
        
        # These methods should not raise exceptions
        main_window.new_project()
        main_window.open_project()
        main_window.import_source()
        main_window.create_object()
        main_window.create_template()
        main_window.export_assets()
        main_window.save_project()
        main_window.close_project()
    
    def test_widget_show_operations(self, ui_factory):
        """Test that all widgets can be shown"""
        ui_impl = ui_factory.get_ui_implementation()
        widgets = [
            ui_impl.create_button("Test"),
            ui_impl.create_text_input("Test"),
            ui_impl.create_combo_box(),
            ui_impl.create_list_widget(),
            ui_impl.create_canvas(),
            ui_impl.create_progress_bar(),
            ui_impl.create_group_box("Test"),
            ui_impl.create_tab_widget(),
            ui_impl.create_splitter(),
        ]
        
        for widget in widgets:
            # Should not raise exception
            widget.show()
            assert widget.visible


class TestUITestMode:
    """Test the embedded test mode functionality"""
    
    @pytest.fixture(params=["headless", "qt"])
    def ui_factory(self, request):
        """Create UI factory for both headless and Qt implementations"""
        backend = request.param
        factory = create_ui_factory(backend, verbose=False)
        yield factory
    
    def test_test_mode_enable_disable(self, ui_factory):
        """Test enabling and disabling test mode"""
        ui_impl = ui_factory.get_ui_implementation()
        
        # Initially not in test mode
        assert not ui_impl.is_test_mode()
        
        # Enable test mode
        test_commands = [
            {"command": "create_widget", "widget_type": "button", "text": "Test Button"},
            {"command": "wait", "duration": 0.1},
            {"command": "assert", "condition": True, "message": "Test completed"}
        ]
        
        ui_impl.enable_test_mode(test_commands)
        
        # In headless mode, commands execute immediately, so test mode is disabled right away
        # We just verify that the commands executed without error
        assert not ui_impl.is_test_mode()  # Should be disabled after immediate execution
    
    def test_test_mode_widget_creation(self, ui_factory):
        """Test widget creation through test mode"""
        ui_impl = ui_factory.get_ui_implementation()
        
        test_commands = [
            {"command": "create_widget", "widget_type": "button", "text": "Test Button 1"},
            {"command": "create_widget", "widget_type": "text_input", "placeholder": "Test Input 1"},
            {"command": "create_widget", "widget_type": "combo_box"},
            {"command": "create_widget", "widget_type": "list_widget"},
            {"command": "create_widget", "widget_type": "canvas"},
            {"command": "create_widget", "widget_type": "progress_bar"},
            {"command": "create_widget", "widget_type": "group_box", "title": "Test Group"},
            {"command": "create_widget", "widget_type": "tab_widget"},
            {"command": "create_widget", "widget_type": "splitter"},
            {"command": "create_widget", "widget_type": "layout", "layout_type": "vertical"},
            {"command": "wait", "duration": 0.1},
            {"command": "assert", "condition": True, "message": "Widget creation test completed"}
        ]
        
        ui_impl.enable_test_mode(test_commands)
        
        # Wait for test execution to complete
        time.sleep(0.5)
        
        # Should be out of test mode after execution
        assert not ui_impl.is_test_mode()
    
    def test_test_mode_assertions(self, ui_factory):
        """Test assertions in test mode"""
        ui_impl = ui_factory.get_ui_implementation()
        
        # Test successful assertion
        test_commands = [
            {"command": "assert", "condition": True, "message": "This should pass"},
            {"command": "wait", "duration": 0.1},
            {"command": "assert", "condition": 1 + 1 == 2, "message": "Math should work"}
        ]
        
        ui_impl.enable_test_mode(test_commands)
        
        # Wait for test execution to complete
        time.sleep(0.5)
        
        # Should be out of test mode after execution
        assert not ui_impl.is_test_mode()
    
    def test_test_mode_wait_commands(self, ui_factory):
        """Test wait commands in test mode"""
        ui_impl = ui_factory.get_ui_implementation()
        
        test_commands = [
            {"command": "wait", "duration": 0.1},
            {"command": "create_widget", "widget_type": "button", "text": "After Wait"},
            {"command": "wait", "duration": 0.05},
            {"command": "assert", "condition": True, "message": "Wait test completed"}
        ]
        
        ui_impl.enable_test_mode(test_commands)
        
        # Wait for test execution to complete
        time.sleep(0.5)
        
        # Should be out of test mode after execution
        assert not ui_impl.is_test_mode()
    
    def test_test_mode_error_handling(self, ui_factory):
        """Test error handling in test mode"""
        ui_impl = ui_factory.get_ui_implementation()
        
        # Test with a failing assertion
        test_commands = [
            {"command": "create_widget", "widget_type": "button", "text": "Before Error"},
            {"command": "assert", "condition": False, "message": "This should fail"},
            {"command": "create_widget", "widget_type": "button", "text": "After Error"}
        ]
        
        ui_impl.enable_test_mode(test_commands)
        
        # Wait for test execution to complete
        time.sleep(0.5)
        
        # Should be out of test mode after execution (even with error)
        assert not ui_impl.is_test_mode()
    
    def test_test_mode_complex_workflow(self, ui_factory):
        """Test a complex workflow in test mode"""
        ui_impl = ui_factory.get_ui_implementation()
        
        test_commands = [
            # Create various widgets
            {"command": "create_widget", "widget_type": "button", "text": "Start Button"},
            {"command": "create_widget", "widget_type": "text_input", "placeholder": "Input Field"},
            {"command": "create_widget", "widget_type": "combo_box"},
            {"command": "wait", "duration": 0.1},
            
            # Create more widgets
            {"command": "create_widget", "widget_type": "list_widget"},
            {"command": "create_widget", "widget_type": "progress_bar"},
            {"command": "create_widget", "widget_type": "group_box", "title": "Test Group"},
            {"command": "wait", "duration": 0.1},
            
            # Create layout and remaining widgets
            {"command": "create_widget", "widget_type": "layout", "layout_type": "vertical"},
            {"command": "create_widget", "widget_type": "tab_widget"},
            {"command": "create_widget", "widget_type": "splitter"},
            {"command": "create_widget", "widget_type": "canvas"},
            {"command": "wait", "duration": 0.1},
            
            # Final assertions
            {"command": "assert", "condition": True, "message": "Complex workflow completed successfully"}
        ]
        
        ui_impl.enable_test_mode(test_commands)
        
        # Wait for test execution to complete
        time.sleep(1.0)  # Longer wait for complex workflow
        
        # Should be out of test mode after execution
        assert not ui_impl.is_test_mode()
