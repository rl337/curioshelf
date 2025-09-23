"""
Mock UI implementations for testing

These mock implementations allow testing of business logic without requiring
the actual GUI framework to be running.
"""

from typing import List, Optional, Dict, Any, Callable
from pathlib import Path
from dataclasses import dataclass

from curioshelf.ui.abstraction import (
    UIWidget, UIButton, UITextInput, UIComboBox, UIListWidget, UIListItem, UICanvas,
    UIDialog, UIMessageBox, UIFileDialog, UIProgressBar, UILayout,
    UIGroupBox, UITabWidget, UISplitter
)


@dataclass
class MockRect:
    """Mock rectangle for canvas selection"""
    x: int = 0
    y: int = 0
    width: int = 0
    height: int = 0
    
    def isValid(self) -> bool:
        return self.width > 0 and self.height > 0
    
    def __getattr__(self, name):
        """Handle attribute access for compatibility"""
        if name in ['x', 'y', 'width', 'height']:
            return getattr(self, f'_{name}', 0)
        raise AttributeError(f"'{self.__class__.__name__}' object has no attribute '{name}'")


class MockPixmap:
    """Mock pixmap for testing"""
    
    def __init__(self, width: int = 100, height: int = 100):
        self.width = width
        self.height = height
    
    def isNull(self) -> bool:
        return False


class MockButton(UIButton):
    """Mock button implementation"""
    
    def __init__(self, text: str = ""):
        super().__init__(text)
        self._click_count = 0
    
    def click(self):
        """Simulate a button click"""
        self._click_count += 1
        super().click()
    
    @property
    def click_count(self) -> int:
        return self._click_count


class MockTextInput(UITextInput):
    """Mock text input implementation"""
    pass


class MockComboBox(UIComboBox):
    """Mock combo box implementation"""
    pass


class MockUIListItem(UIListItem):
    """Mock list item implementation"""
    pass


class MockListWidget(UIListWidget):
    """Mock list widget implementation"""
    pass


class MockCanvas(UICanvas):
    """Mock canvas implementation"""
    
    def __init__(self):
        super().__init__()
        self._selection_rect = None
    
    def set_pixmap(self, pixmap: Any):
        """Set the image to display"""
        self._pixmap = pixmap
        self.emit_signal("pixmap_changed")
    
    def canvas_to_source_rect(self, canvas_rect: MockRect) -> MockRect:
        """Convert canvas coordinates to source image coordinates"""
        if not self._pixmap:
            return MockRect()
        
        # Simple 1:1 mapping for testing
        return MockRect(
            canvas_rect.x,
            canvas_rect.y,
            canvas_rect.width,
            canvas_rect.height
        )


class MockDialog(UIDialog):
    """Mock dialog implementation"""
    
    def __init__(self, result: int = 0, data: Any = None):
        self._result = result
        self._data = data
    
    def exec(self) -> int:
        return self._result
    
    def get_data(self) -> Any:
        return self._data


class MockMessageBox(UIMessageBox):
    """Mock message box implementation"""
    
    def __init__(self):
        self._messages: List[tuple] = []  # (type, title, message) tuples
        self._question_responses: List[bool] = []
        self._question_index = 0
    
    def show_info(self, title: str, message: str) -> None:
        self._messages.append(("info", title, message))
    
    def show_warning(self, title: str, message: str) -> None:
        self._messages.append(("warning", title, message))
    
    def show_error(self, title: str, message: str) -> None:
        self._messages.append(("error", title, message))
    
    def show_question(self, title: str, message: str) -> bool:
        self._messages.append(("question", title, message))
        if self._question_index < len(self._question_responses):
            result = self._question_responses[self._question_index]
            self._question_index += 1
            return result
        return False  # Default to No
    
    def set_question_responses(self, responses: List[bool]):
        """Set the responses for question dialogs"""
        self._question_responses = responses
        self._question_index = 0
    
    def get_messages(self) -> List[tuple]:
        """Get all messages that were shown"""
        return self._messages.copy()
    
    def clear_messages(self):
        """Clear the message history"""
        self._messages.clear()


class MockFileDialog(UIFileDialog):
    """Mock file dialog implementation"""
    
    def __init__(self):
        self._open_responses: List[Optional[str]] = []
        self._save_responses: List[Optional[str]] = []
        self._open_index = 0
        self._save_index = 0
    
    def get_open_file_name(self, title: str, filter: str = "") -> Optional[str]:
        if self._open_index < len(self._open_responses):
            result = self._open_responses[self._open_index]
            self._open_index += 1
            return result
        return None
    
    def get_save_file_name(self, title: str, filter: str = "") -> Optional[str]:
        if self._save_index < len(self._save_responses):
            result = self._save_responses[self._save_index]
            self._save_index += 1
            return result
        return None
    
    def get_existing_directory(self, title: str, directory: str = "") -> Optional[str]:
        """Get an existing directory path"""
        if self._open_index < len(self._open_responses):
            result = self._open_responses[self._open_index]
            self._open_index += 1
            return result
        return None
    
    def set_open_responses(self, responses: List[Optional[str]]):
        """Set the responses for open file dialogs"""
        self._open_responses = responses
        self._open_index = 0
    
    def set_save_responses(self, responses: List[Optional[str]]):
        """Set the responses for save file dialogs"""
        self._save_responses = responses
        self._save_index = 0


class MockProgressBar(UIProgressBar):
    """Mock progress bar implementation"""
    
    def set_value(self, value: int):
        """Set the progress value"""
        self.value = value


class MockLayout(UILayout):
    """Mock layout implementation"""
    
    def __init__(self):
        self._widgets: List[UIWidget] = []
    
    def add_widget(self, widget: UIWidget, *args, **kwargs):
        self._widgets.append(widget)
    
    def remove_widget(self, widget: UIWidget):
        if widget in self._widgets:
            self._widgets.remove(widget)
    
    def insert_widget(self, index: int, widget: UIWidget, *args, **kwargs):
        """Insert a widget at a specific index in the layout"""
        self._widgets.insert(index, widget)
    
    def get_widgets(self) -> List[UIWidget]:
        return self._widgets.copy()


class MockGroupBox(UIGroupBox):
    """Mock group box implementation"""
    
    def __init__(self, title: str = ""):
        super().__init__(title)
        self._layout = MockLayout()


class MockTabWidget(UITabWidget):
    """Mock tab widget implementation"""
    
    def __init__(self):
        super().__init__()
        self._tabs: List[tuple] = []
        self._current_index = 0
    
    def add_tab(self, widget: UIWidget, title: str):
        self._tabs.append((widget, title))
    
    def set_current_index(self, index: int):
        if 0 <= index < len(self._tabs):
            self._current_index = index
            self.emit_signal("current_changed", index)
    
    def get_tab_count(self) -> int:
        return len(self._tabs)
    
    def get_tab_title(self, index: int) -> str:
        if 0 <= index < len(self._tabs):
            return self._tabs[index][1]
        return ""


class MockSplitter(UISplitter):
    """Mock splitter implementation"""
    
    def __init__(self, orientation: str = "horizontal"):
        super().__init__(orientation)
        self._widgets: List[UIWidget] = []
        self._sizes: List[int] = []
    
    def add_widget(self, widget: UIWidget):
        self._widgets.append(widget)
        self._sizes.append(100)
    
    def get_widget_count(self) -> int:
        return len(self._widgets)


class MockUIFactory:
    """Factory for creating mock UI components"""
    
    @staticmethod
    def create_button(text: str = "") -> MockButton:
        return MockButton(text)
    
    @staticmethod
    def create_text_input(placeholder: str = "") -> MockTextInput:
        return MockTextInput(placeholder)
    
    @staticmethod
    def create_combo_box() -> MockComboBox:
        return MockComboBox()
    
    @staticmethod
    def create_list_widget() -> MockListWidget:
        return MockListWidget()
    
    @staticmethod
    def create_canvas() -> MockCanvas:
        return MockCanvas()
    
    @staticmethod
    def create_dialog(result: int = 0, data: Any = None) -> MockDialog:
        return MockDialog(result, data)
    
    @staticmethod
    def create_message_box() -> MockMessageBox:
        return MockMessageBox()
    
    @staticmethod
    def create_file_dialog() -> MockFileDialog:
        return MockFileDialog()
    
    @staticmethod
    def create_progress_bar() -> MockProgressBar:
        return MockProgressBar()
    
    @staticmethod
    def create_layout() -> MockLayout:
        return MockLayout()
    
    @staticmethod
    def create_group_box(title: str = "") -> MockGroupBox:
        return MockGroupBox(title)
    
    @staticmethod
    def create_tab_widget() -> MockTabWidget:
        return MockTabWidget()
    
    @staticmethod
    def create_splitter(orientation: str = "horizontal") -> MockSplitter:
        return MockSplitter(orientation)
    
    @staticmethod
    def create_rect(x: int = 0, y: int = 0, width: int = 0, height: int = 0) -> MockRect:
        return MockRect(x, y, width, height)
    
    @staticmethod
    def create_pixmap(width: int = 100, height: int = 100) -> MockPixmap:
        return MockPixmap(width, height)
