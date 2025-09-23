"""
Tests for UI abstraction layer
"""

import unittest
from unittest.mock import Mock

from curioshelf.ui.abstraction import (
    UIButton, UITextInput, UIComboBox, UIListWidget, UICanvas,
    UIMessageBox, UIFileDialog, UIProgressBar, UIGroupBox, UITabWidget
)
from tests.ui_mocks import MockUIFactory


class TestUIAbstraction(unittest.TestCase):
    """Test the UI abstraction layer"""
    
    def test_button_creation(self):
        """Test button creation and basic functionality"""
        button = MockUIFactory.create_button("Test Button")
        
        self.assertEqual(button.text, "Test Button")
        self.assertTrue(button.enabled)
        self.assertTrue(button.visible)
        
        # Test text setting
        button.text = "New Text"
        self.assertEqual(button.text, "New Text")
        
        # Test click callback
        callback_called = False
        def test_callback():
            nonlocal callback_called
            callback_called = True
        
        button.set_clicked_callback(test_callback)
        button.click()
        self.assertTrue(callback_called)
    
    def test_text_input(self):
        """Test text input functionality"""
        text_input = MockUIFactory.create_text_input("Enter text...")
        
        self.assertEqual(text_input.placeholder, "Enter text...")
        self.assertEqual(text_input.text, "")
        
        # Test text setting
        text_input.set_text("Hello World")
        self.assertEqual(text_input.text, "Hello World")
        
        # Test text change callback
        callback_data = None
        def text_callback(text):
            nonlocal callback_data
            callback_data = text
        
        text_input.set_text_changed_callback(text_callback)
        text_input.set_text("New Text")
        self.assertEqual(callback_data, "New Text")
    
    def test_combo_box(self):
        """Test combo box functionality"""
        combo = MockUIFactory.create_combo_box()
        
        # Add items
        from tests.ui_mocks import MockUIListItem
        item1 = MockUIListItem("Item 1")
        item1.set_data("data1")
        combo.add_item(item1)
        
        item2 = MockUIListItem("Item 2")
        item2.set_data("data2")
        combo.add_item(item2)
        
        self.assertEqual(len(combo._items), 2)
        
        # Test selection
        combo.set_current_index(0)
        self.assertEqual(combo.current_text(), "Item 1")
        self.assertEqual(combo.current_data(), "data1")
        
        combo.set_current_index(1)
        self.assertEqual(combo.current_text(), "Item 2")
        self.assertEqual(combo.current_data(), "data2")
        
        # Test callback
        callback_data = None
        def selection_callback(data):
            nonlocal callback_data
            callback_data = data
        
        combo.set_current_changed_callback(selection_callback)
        combo.set_current_index(0)
        self.assertEqual(callback_data, "data1")
    
    def test_list_widget(self):
        """Test list widget functionality"""
        list_widget = MockUIFactory.create_list_widget()
        
        # Add items
        from tests.ui_mocks import MockUIListItem
        item1 = MockUIListItem("Item 1")
        item1.set_data("data1")
        list_widget.add_item(item1)
        
        item2 = MockUIListItem("Item 2")
        item2.set_data("data2")
        list_widget.add_item(item2)
        
        self.assertEqual(len(list_widget._items), 2)
        
        # Test selection
        list_widget.set_current_index(0)
        self.assertEqual(list_widget.current_text(), "Item 1")
        self.assertEqual(list_widget.current_data(), "data1")
        
        # Test clear
        list_widget.clear()
        self.assertEqual(len(list_widget._items), 0)
        self.assertEqual(list_widget.current_text(), "")
    
    def test_canvas(self):
        """Test canvas functionality"""
        canvas = MockUIFactory.create_canvas()
        
        # Test pixmap setting
        pixmap = MockUIFactory.create_pixmap(200, 150)
        canvas.set_pixmap(pixmap)
        self.assertEqual(canvas._pixmap, pixmap)
        
        # Test zoom
        canvas.set_zoom(1.5)
        self.assertEqual(canvas.zoom_factor, 1.5)
        
        # Test selection
        rect = MockUIFactory.create_rect(10, 20, 100, 80)
        canvas.set_selection_rect(rect)
        self.assertEqual(canvas.selection_rect, rect)
        
        # Test selection callback
        callback_data = None
        def selection_callback(rect):
            nonlocal callback_data
            callback_data = rect
        
        canvas.set_selection_changed_callback(selection_callback)
        canvas.set_selection_rect(rect)
        self.assertEqual(callback_data, rect)
    
    def test_message_box(self):
        """Test message box functionality"""
        msg_box = MockUIFactory.create_message_box()
        
        # Test different message types
        msg_box.show_info("Info", "This is info")
        msg_box.show_warning("Warning", "This is a warning")
        msg_box.show_error("Error", "This is an error")
        
        messages = msg_box.get_messages()
        self.assertEqual(len(messages), 3)
        self.assertEqual(messages[0], ("info", "Info", "This is info"))
        self.assertEqual(messages[1], ("warning", "Warning", "This is a warning"))
        self.assertEqual(messages[2], ("error", "Error", "This is an error"))
        
        # Test question responses
        msg_box.set_question_responses([True, False])
        self.assertTrue(msg_box.show_question("Question", "Yes or No?"))
        self.assertFalse(msg_box.show_question("Question", "Yes or No?"))
    
    def test_file_dialog(self):
        """Test file dialog functionality"""
        file_dialog = MockUIFactory.create_file_dialog()
        
        # Test open file responses
        file_dialog.set_open_responses(["file1.png", "file2.jpg", None])
        
        self.assertEqual(file_dialog.get_open_file_name("Open"), "file1.png")
        self.assertEqual(file_dialog.get_open_file_name("Open"), "file2.jpg")
        self.assertIsNone(file_dialog.get_open_file_name("Open"))
        
        # Test save file responses
        file_dialog.set_save_responses(["output.json"])
        self.assertEqual(file_dialog.get_save_file_name("Save"), "output.json")
    
    def test_progress_bar(self):
        """Test progress bar functionality"""
        progress = MockUIFactory.create_progress_bar()
        
        self.assertEqual(progress.value, 0)
        self.assertEqual(progress.minimum, 0)
        self.assertEqual(progress.maximum, 100)
        
        # Test value setting
        progress.value = 50
        self.assertEqual(progress.value, 50)
        
        # Test bounds
        progress.value = 150
        self.assertEqual(progress.value, 100)  # Should be clamped to maximum
        
        progress.value = -10
        self.assertEqual(progress.value, 0)  # Should be clamped to minimum
    
    def test_group_box(self):
        """Test group box functionality"""
        group_box = MockUIFactory.create_group_box("Test Group")
        
        self.assertEqual(group_box.title, "Test Group")
        
        # Test title setting
        group_box.title = "New Title"
        self.assertEqual(group_box.title, "New Title")
    
    def test_tab_widget(self):
        """Test tab widget functionality"""
        tab_widget = MockUIFactory.create_tab_widget()
        
        # Add tabs
        widget1 = MockUIFactory.create_button("Button 1")
        widget2 = MockUIFactory.create_button("Button 2")
        
        tab_widget.add_tab(widget1, "Tab 1")
        tab_widget.add_tab(widget2, "Tab 2")
        
        self.assertEqual(tab_widget.get_tab_count(), 2)
        self.assertEqual(tab_widget.get_tab_title(0), "Tab 1")
        self.assertEqual(tab_widget.get_tab_title(1), "Tab 2")
        
        # Test tab switching
        tab_widget.set_current_index(1)
        self.assertEqual(tab_widget.current_index(), 1)
        
        # Test callback
        callback_data = None
        def tab_callback(index):
            nonlocal callback_data
            callback_data = index
        
        tab_widget.set_current_changed_callback(tab_callback)
        tab_widget.set_current_index(0)
        self.assertEqual(callback_data, 0)


if __name__ == "__main__":
    unittest.main()
