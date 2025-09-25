"""
Base layout widgets that handle their own internal layout management
"""

from typing import List, Optional, Any, Callable, Tuple
from abc import ABC, abstractmethod
from curioshelf.ui.abstraction import UIWidget, UILayout, UIButton, UILabel, UITextInput
from curioshelf.ui.factory_interface import UIFactoryInterface


class LayoutWidget(UIWidget, ABC):
    """Base class for widgets that manage their own internal layout"""
    
    def __init__(self, ui_factory: UIFactoryInterface, parent: Optional[UIWidget] = None):
        super().__init__()
        self.ui = ui_factory
        self.parent = parent
        self.widgets: List[UIWidget] = []
        
        # Create the container widget
        self.widget = self.ui.create_widget(f"{self.__class__.__name__.lower()}_container")
        self._setup_layout()
    
    @abstractmethod
    def _setup_layout(self) -> None:
        """Set up the internal layout for this widget"""
        pass
    
    def add_widget(self, widget: UIWidget, **kwargs) -> None:
        """Add a widget to this layout widget"""
        self.widgets.append(widget)
        self._add_widget_to_layout(widget, **kwargs)
    
    @abstractmethod
    def _add_widget_to_layout(self, widget: UIWidget, **kwargs) -> None:
        """Add a widget to the internal layout"""
        pass
    
    def remove_widget(self, widget: UIWidget) -> None:
        """Remove a widget from this layout widget"""
        if widget in self.widgets:
            self.widgets.remove(widget)
            self._remove_widget_from_layout(widget)
    
    @abstractmethod
    def _remove_widget_from_layout(self, widget: UIWidget) -> None:
        """Remove a widget from the internal layout"""
        pass
    
    def clear(self) -> None:
        """Clear all widgets from this layout widget"""
        for widget in self.widgets.copy():
            self.remove_widget(widget)
    
    def get_widgets(self) -> List[UIWidget]:
        """Get all widgets in this layout widget"""
        return self.widgets.copy()


class StackWidget(LayoutWidget):
    """A widget that arranges its children vertically in a stack"""
    
    def __init__(self, ui_factory: UIFactoryInterface, spacing: int = 5, parent: Optional[UIWidget] = None):
        self.spacing = spacing
        super().__init__(ui_factory, parent)
    
    def _setup_layout(self) -> None:
        """Set up vertical layout"""
        layout = self.ui.create_layout("vertical", self.widget)
        self.widget.set_layout(layout)
        self._layout = layout
    
    def _add_widget_to_layout(self, widget: UIWidget, **kwargs) -> None:
        """Add widget to vertical layout"""
        self._layout.add_widget(widget)
    
    def _remove_widget_from_layout(self, widget: UIWidget) -> None:
        """Remove widget from vertical layout"""
        self._layout.remove_widget(widget)
    
    # Convenience methods for common widgets
    def add_label(self, text: str, style: str = "") -> UILabel:
        """Add a label to the stack"""
        label = self.ui.create_label(text)
        if style:
            label.set_style(style)
        self.add_widget(label)
        return label
    
    def add_text_input(self, placeholder: str = "", style: str = "") -> UITextInput:
        """Add a text input to the stack"""
        text_input = self.ui.create_line_edit()
        if placeholder:
            text_input.set_placeholder(placeholder)
        if style:
            text_input.set_style(style)
        self.add_widget(text_input)
        return text_input
    
    def add_button(self, text: str, callback: Optional[Callable] = None, style: str = "") -> UIButton:
        """Add a button to the stack"""
        button = self.ui.create_button(text)
        if callback:
            button.clicked.connect(callback)
        if style:
            button.set_style(style)
        self.add_widget(button)
        return button


class RowWidget(LayoutWidget):
    """A widget that arranges its children horizontally in a row"""
    
    def __init__(self, ui_factory: UIFactoryInterface, spacing: int = 5, parent: Optional[UIWidget] = None):
        self.spacing = spacing
        super().__init__(ui_factory, parent)
    
    def _setup_layout(self) -> None:
        """Set up horizontal layout"""
        layout = self.ui.create_layout("horizontal", self.widget)
        self.widget.set_layout(layout)
        self._layout = layout
    
    def _add_widget_to_layout(self, widget: UIWidget, expand: bool = False, **kwargs) -> None:
        """Add widget to horizontal layout"""
        if expand:
            self._layout.add_widget(widget, expand=True)
        else:
            self._layout.add_widget(widget)
    
    def _remove_widget_from_layout(self, widget: UIWidget) -> None:
        """Remove widget from horizontal layout"""
        self._layout.remove_widget(widget)
    
    # Convenience methods for common widgets
    def add_label(self, text: str, style: str = "") -> UILabel:
        """Add a label to the row"""
        label = self.ui.create_label(text)
        if style:
            label.set_style(style)
        self.add_widget(label)
        return label
    
    def add_text_input(self, placeholder: str = "", expand: bool = True, style: str = "") -> UITextInput:
        """Add a text input to the row"""
        text_input = self.ui.create_line_edit()
        if placeholder:
            text_input.set_placeholder(placeholder)
        if style:
            text_input.set_style(style)
        self.add_widget(text_input, expand=expand)
        return text_input
    
    def add_button(self, text: str, callback: Optional[Callable] = None, style: str = "") -> UIButton:
        """Add a button to the row"""
        button = self.ui.create_button(text)
        if callback:
            button.clicked.connect(callback)
        if style:
            button.set_style(style)
        self.add_widget(button)
        return button


class FormWidget(StackWidget):
    """A widget that creates a form with labeled input fields"""
    
    def __init__(self, ui_factory: UIFactoryInterface, spacing: int = 10, parent: Optional[UIWidget] = None):
        super().__init__(ui_factory, spacing, parent)
        self.rows: List[RowWidget] = []
    
    def add_field(self, label_text: str, placeholder: str = "", 
                  input_style: str = "", label_style: str = "") -> Tuple[UILabel, UITextInput]:
        """Add a labeled input field to the form"""
        row = RowWidget(self.ui, spacing=5)
        self.rows.append(row)
        
        # Add label
        label = row.add_label(label_text, style=label_style or "font-weight: bold; margin-right: 10px;")
        
        # Add text input
        text_input = row.add_text_input(placeholder, expand=True, 
                                      style=input_style or "padding: 8px; font-size: 14px;")
        
        # Add the row to the form
        self.add_widget(row.widget)
        
        return label, text_input
    
    def add_button_row(self, buttons: List[Tuple[str, Optional[Callable], str]]) -> List[UIButton]:
        """Add a row of buttons to the form"""
        button_row = ButtonRowWidget(self.ui)
        button_list = []
        
        for text, callback, style in buttons:
            button = button_row.add_button(text, callback, style)
            button_list.append(button)
        
        self.add_widget(button_row.widget)
        return button_list
    
    def get_rows(self) -> List[RowWidget]:
        """Get all rows in the form"""
        return self.rows.copy()


class ButtonRowWidget(RowWidget):
    """A specialized row widget for buttons with consistent styling"""
    
    def __init__(self, ui_factory: UIFactoryInterface, spacing: int = 10, parent: Optional[UIWidget] = None):
        super().__init__(ui_factory, spacing, parent)
        self.buttons: List[UIButton] = []
    
    def add_button(self, text: str, callback: Optional[Callable] = None, 
                   style: str = "", align: str = "right") -> UIButton:
        """Add a button to the button row"""
        button = self.ui.create_button(text)
        if callback:
            button.clicked.connect(callback)
        
        # Default button styling
        default_style = "padding: 10px 20px; font-size: 14px; margin-left: 10px;"
        if style:
            button_style = default_style + " " + style
        else:
            button_style = default_style
        
        button.set_style(button_style)
        
        # Add to row
        self.add_widget(button)
        self.buttons.append(button)
        
        return button
    
    def add_primary_button(self, text: str, callback: Optional[Callable] = None) -> UIButton:
        """Add a primary (highlighted) button"""
        return self.add_button(text, callback, "background-color: #007acc; color: white;")
    
    def add_secondary_button(self, text: str, callback: Optional[Callable] = None) -> UIButton:
        """Add a secondary button"""
        return self.add_button(text, callback, "background-color: #f0f0f0; color: #333;")
    
    def get_buttons(self) -> List[UIButton]:
        """Get all buttons in the row"""
        return self.buttons.copy()


class TableWidget(LayoutWidget):
    """A widget that arranges its children in a table/grid layout"""
    
    def __init__(self, ui_factory: UIFactoryInterface, rows: int = 1, cols: int = 1, 
                 spacing: int = 5, parent: Optional[UIWidget] = None):
        self.rows = rows
        self.cols = cols
        self.spacing = spacing
        super().__init__(ui_factory, parent)
    
    def _setup_layout(self) -> None:
        """Set up grid layout"""
        layout = self.ui.create_layout("grid", self.widget)
        self.widget.set_layout(layout)
        self._layout = layout
    
    def _add_widget_to_layout(self, widget: UIWidget, row: int = 0, col: int = 0, 
                             rowspan: int = 1, colspan: int = 1, **kwargs) -> None:
        """Add widget to grid layout"""
        self._layout.add_widget(widget, row=row, col=col, rowspan=rowspan, colspan=colspan)
    
    def _remove_widget_from_layout(self, widget: UIWidget) -> None:
        """Remove widget from grid layout"""
        self._layout.remove_widget(widget)
    
    def add_widget_at(self, widget: UIWidget, row: int, col: int, 
                      rowspan: int = 1, colspan: int = 1) -> None:
        """Add a widget at a specific grid position"""
        self.add_widget(widget, row=row, col=col, rowspan=rowspan, colspan=colspan)
