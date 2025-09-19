"""
Abstract UI Factory Interface

This module defines the abstract interface for UI factories, providing
proper type safety for business logic components.
"""

from abc import ABC, abstractmethod
from typing import Any, Optional, List
from pathlib import Path

from .abstraction import (
    UIWidget, UIButton, UITextInput, UIComboBox, UIListWidget, UICanvas,
    UIMessageBox, UIFileDialog, UIProgressBar, UIGroupBox, UITabWidget,
    UISplitter, UILayout
)


class UIFactoryInterface(ABC):
    """Abstract interface for UI factory implementations"""
    
    @abstractmethod
    def create_button(self, text: str = "") -> UIButton:
        """Create a button widget"""
        pass
    
    @abstractmethod
    def create_text_input(self, placeholder: str = "") -> UITextInput:
        """Create a text input widget"""
        pass
    
    @abstractmethod
    def create_combo_box(self) -> UIComboBox:
        """Create a combo box widget"""
        pass
    
    @abstractmethod
    def create_list_widget(self) -> UIListWidget:
        """Create a list widget"""
        pass
    
    @abstractmethod
    def create_canvas(self) -> UICanvas:
        """Create a canvas widget"""
        pass
    
    @abstractmethod
    def create_message_box(self) -> UIMessageBox:
        """Create a message box widget"""
        pass
    
    @abstractmethod
    def create_file_dialog(self) -> UIFileDialog:
        """Create a file dialog widget"""
        pass
    
    @abstractmethod
    def create_progress_bar(self) -> UIProgressBar:
        """Create a progress bar widget"""
        pass
    
    @abstractmethod
    def create_group_box(self, title: str = "") -> UIGroupBox:
        """Create a group box widget"""
        pass
    
    @abstractmethod
    def create_tab_widget(self) -> UITabWidget:
        """Create a tab widget"""
        pass
    
    @abstractmethod
    def create_splitter(self, orientation: str = "horizontal") -> UISplitter:
        """Create a splitter widget"""
        pass
    
    @abstractmethod
    def create_layout(self, orientation: str = "vertical") -> UILayout:
        """Create a layout widget"""
        pass
    
    @abstractmethod
    def create_pixmap(self, width: int, height: int) -> Any:
        """Create a pixmap/image object (implementation-specific)"""
        pass


class UIComponentManager:
    """Helper class to manage UI components with proper null checking"""
    
    def __init__(self, factory: UIFactoryInterface) -> None:
        self.factory = factory
        self._components: dict[str, Any] = {}
    
    def create_component(self, name: str, component_type: str, **kwargs: Any) -> Any:
        """Create a UI component and store it by name"""
        component: Any
        if component_type == "button":
            component = self.factory.create_button(**kwargs)
        elif component_type == "text_input":
            component = self.factory.create_text_input(**kwargs)
        elif component_type == "combo_box":
            component = self.factory.create_combo_box()
        elif component_type == "list_widget":
            component = self.factory.create_list_widget()
        elif component_type == "canvas":
            component = self.factory.create_canvas()
        elif component_type == "message_box":
            component = self.factory.create_message_box()
        elif component_type == "file_dialog":
            component = self.factory.create_file_dialog()
        elif component_type == "progress_bar":
            component = self.factory.create_progress_bar()
        elif component_type == "group_box":
            component = self.factory.create_group_box(**kwargs)
        elif component_type == "tab_widget":
            component = self.factory.create_tab_widget()
        elif component_type == "splitter":
            component = self.factory.create_splitter(**kwargs)
        elif component_type == "layout":
            component = self.factory.create_layout(**kwargs)
        else:
            raise ValueError(f"Unknown component type: {component_type}")
        
        self._components[name] = component
        return component
    
    def get_component(self, name: str) -> Optional[UIWidget]:
        """Get a component by name"""
        return self._components.get(name)
    
    def get_button(self, name: str) -> Optional[UIButton]:
        """Get a button component with proper typing"""
        component = self.get_component(name)
        return component if isinstance(component, UIButton) else None
    
    def get_text_input(self, name: str) -> Optional[UITextInput]:
        """Get a text input component with proper typing"""
        component = self.get_component(name)
        return component if isinstance(component, UITextInput) else None
    
    def get_combo_box(self, name: str) -> Optional[UIComboBox]:
        """Get a combo box component with proper typing"""
        component = self.get_component(name)
        return component if isinstance(component, UIComboBox) else None
    
    def get_list_widget(self, name: str) -> Optional[UIListWidget]:
        """Get a list widget component with proper typing"""
        component = self.get_component(name)
        return component if isinstance(component, UIListWidget) else None
    
    def get_canvas(self, name: str) -> Optional[UICanvas]:
        """Get a canvas component with proper typing"""
        component = self.get_component(name)
        return component if isinstance(component, UICanvas) else None
    
    def get_message_box(self, name: str) -> Optional[UIMessageBox]:
        """Get a message box component with proper typing"""
        component = self.get_component(name)
        return component if isinstance(component, UIMessageBox) else None
    
    def get_file_dialog(self, name: str) -> Optional[UIFileDialog]:
        """Get a file dialog component with proper typing"""
        component = self.get_component(name)
        return component if isinstance(component, UIFileDialog) else None
    
    def get_progress_bar(self, name: str) -> Optional[UIProgressBar]:
        """Get a progress bar component with proper typing"""
        component = self.get_component(name)
        return component if isinstance(component, UIProgressBar) else None
    
    def get_group_box(self, name: str) -> Optional[UIGroupBox]:
        """Get a group box component with proper typing"""
        component = self.get_component(name)
        return component if isinstance(component, UIGroupBox) else None
    
    def get_tab_widget(self, name: str) -> Optional[UITabWidget]:
        """Get a tab widget component with proper typing"""
        component = self.get_component(name)
        return component if isinstance(component, UITabWidget) else None
    
    def get_splitter(self, name: str) -> Optional[UISplitter]:
        """Get a splitter component with proper typing"""
        component = self.get_component(name)
        return component if isinstance(component, UISplitter) else None
    
    def get_layout(self, name: str) -> Optional[UILayout]:
        """Get a layout component with proper typing"""
        component = self.get_component(name)
        return component if isinstance(component, UILayout) else None
