"""
Composite widgets for simplified UI layout management
"""

from typing import List, Optional, Any, Callable
from curioshelf.ui.abstraction import UIWidget, UILabel, UITextInput, UIButton, UILayout
from curioshelf.ui.layouts.directional_layout import DirectionalLayout, Direction


class Stack(UIWidget):
    """Vertical stack of widgets"""
    
    def __init__(self, ui_implementation, spacing: int = 5, parent: Optional[UIWidget] = None):
        super().__init__()
        self.ui = ui_implementation
        self.spacing = spacing
        self.widgets: List[UIWidget] = []
        
        # Create the container widget
        self.widget = self.ui.create_widget("stack_container")
        self._setup_layout()
    
    def _setup_layout(self):
        """Set up the vertical layout"""
        layout = DirectionalLayout(self.widget)
        layout.set_parent_widget(self.widget)
        self.widget.set_layout(layout)
        self._layout = layout
    
    def add_widget(self, widget: UIWidget, expand: bool = False) -> None:
        """Add a widget to the stack"""
        self.widgets.append(widget)
        self._layout.add_widget(widget, Direction.NORTH, expand=expand)
    
    def add_label(self, text: str, style: str = "") -> UILabel:
        """Add a label to the stack"""
        label = self.ui.create_label(text)
        label.set_text(text)
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
    
    def clear(self) -> None:
        """Clear all widgets from the stack"""
        self.widgets.clear()
        self._layout.clear()
    
    def get_widgets(self) -> List[UIWidget]:
        """Get all widgets in the stack"""
        return self.widgets.copy()


class Row(UIWidget):
    """Horizontal row of widgets"""
    
    def __init__(self, ui_implementation, spacing: int = 5, parent: Optional[UIWidget] = None):
        super().__init__()
        self.ui = ui_implementation
        self.spacing = spacing
        self.widgets: List[UIWidget] = []
        
        # Create the container widget
        self.widget = self.ui.create_widget("row_container")
        self._setup_layout()
    
    def _setup_layout(self):
        """Set up the horizontal layout"""
        layout = DirectionalLayout(self.widget)
        layout.set_parent_widget(self.widget)
        self.widget.set_layout(layout)
        self._layout = layout
    
    def add_widget(self, widget: UIWidget, expand: bool = False) -> None:
        """Add a widget to the row"""
        self.widgets.append(widget)
        if expand:
            self._layout.add_widget(widget, Direction.CENTER, expand=True)
        else:
            self._layout.add_widget(widget, Direction.WEST)
    
    def add_label(self, text: str, style: str = "") -> UILabel:
        """Add a label to the row"""
        label = self.ui.create_label(text)
        label.set_text(text)
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
    
    def clear(self) -> None:
        """Clear all widgets from the row"""
        self.widgets.clear()
        self._layout.clear()
    
    def get_widgets(self) -> List[UIWidget]:
        """Get all widgets in the row"""
        return self.widgets.copy()


class Form(Stack):
    """Form widget - a stack of labeled input rows"""
    
    def __init__(self, ui_implementation, spacing: int = 10, parent: Optional[UIWidget] = None):
        super().__init__(ui_implementation, spacing, parent)
        self.rows: List[Row] = []
    
    def add_field(self, label_text: str, placeholder: str = "", 
                  input_style: str = "", label_style: str = "") -> tuple[UILabel, UITextInput]:
        """Add a labeled input field to the form"""
        row = Row(self.ui, spacing=5)
        self.rows.append(row)
        
        # Add label
        label = row.add_label(label_text, style=label_style or "font-weight: bold; margin-right: 10px;")
        
        # Add text input
        text_input = row.add_text_input(placeholder, expand=True, 
                                      style=input_style or "padding: 8px; font-size: 14px;")
        
        # Add the row to the form
        self.add_widget(row)
        
        return label, text_input
    
    def add_button_row(self, buttons: List[tuple[str, Optional[Callable], str]]) -> List[UIButton]:
        """Add a row of buttons to the form"""
        button_row = ButtonRow(self.ui)
        button_list = []
        
        for text, callback, style in buttons:
            button = button_row.add_button(text, callback, style)
            button_list.append(button)
        
        self.add_widget(button_row)
        return button_list
    
    def get_rows(self) -> List[Row]:
        """Get all rows in the form"""
        return self.rows.copy()


class ButtonRow(Row):
    """Specialized row for buttons with consistent styling"""
    
    def __init__(self, ui_implementation, spacing: int = 10, parent: Optional[UIWidget] = None):
        super().__init__(ui_implementation, spacing, parent)
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
        
        # Add to row based on alignment
        if align == "right":
            self._layout.add_widget(button, Direction.EAST)
        elif align == "left":
            self._layout.add_widget(button, Direction.WEST)
        else:
            self._layout.add_widget(button, Direction.CENTER)
        
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
