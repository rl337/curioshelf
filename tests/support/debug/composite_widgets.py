"""
Headless implementations of composite widgets that match Qt behavior exactly
"""

from typing import List, Optional, Any, Callable
from curioshelf.ui.abstraction import UIWidget, UILabel, UITextInput, UIButton, UILayout
from .directional_layout import DebugDirectionalLayout, Direction
from .ui_widgets import DebugUIWidget, DebugUILabel, DebugUITextInput, DebugUIButton
from .message_system import MessageLogger


class DebugStack(UIWidget):
    """Headless vertical stack of widgets that matches Qt behavior"""
    
    def __init__(self, ui_implementation, spacing: int = 5, parent: Optional[UIWidget] = None,
                 message_logger: Optional[MessageLogger] = None):
        super().__init__()
        self.ui = ui_implementation
        self.spacing = spacing
        self.widgets: List[UIWidget] = []
        self.message_logger = message_logger or MessageLogger(collect_messages=True, print_messages=True)
        
        # Create the container widget
        self.widget = DebugUIWidget(message_logger=self.message_logger)
        self._setup_layout()
        
        # Log stack creation
        self.message_logger.log_ui_event("DebugStack", "stack_created", {
            "spacing": spacing,
            "stack_id": id(self)
        })
    
    def _setup_layout(self):
        """Set up the vertical layout"""
        layout = DebugDirectionalLayout(self.widget, message_logger=self.message_logger)
        layout.set_parent_widget(self.widget)
        self.widget.set_layout(layout)
        self._layout = layout
        
        self.message_logger.log_ui_event("DebugStack", "layout_setup", {
            "stack_id": id(self)
        })
    
    def add_widget(self, widget: UIWidget, expand: bool = False) -> None:
        """Add a widget to the stack"""
        self.widgets.append(widget)
        self._layout.add_widget(widget, Direction.NORTH, expand=expand)
        
        self.message_logger.log_ui_event("DebugStack", "widget_added", {
            "widget_type": widget.__class__.__name__,
            "expand": expand,
            "stack_id": id(self),
            "widget_id": id(widget)
        })
    
    def add_label(self, text: str, style: str = "") -> UILabel:
        """Add a label to the stack"""
        label = DebugUILabel(text, message_logger=self.message_logger)
        if style:
            label.set_style(style)
        self.add_widget(label)
        return label
    
    def add_text_input(self, placeholder: str = "", style: str = "") -> UITextInput:
        """Add a text input to the stack"""
        text_input = DebugUITextInput(message_logger=self.message_logger)
        if placeholder:
            text_input.set_placeholder(placeholder)
        if style:
            text_input.set_style(style)
        self.add_widget(text_input)
        return text_input
    
    def add_button(self, text: str, callback: Optional[Callable] = None, style: str = "") -> UIButton:
        """Add a button to the stack"""
        button = DebugUIButton(text, message_logger=self.message_logger)
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
        
        self.message_logger.log_ui_event("DebugStack", "stack_cleared", {
            "stack_id": id(self)
        })
    
    def get_widgets(self) -> List[UIWidget]:
        """Get all widgets in the stack"""
        return self.widgets.copy()


class DebugRow(UIWidget):
    """Headless horizontal row of widgets that matches Qt behavior"""
    
    def __init__(self, ui_implementation, spacing: int = 5, parent: Optional[UIWidget] = None,
                 message_logger: Optional[MessageLogger] = None):
        super().__init__()
        self.ui = ui_implementation
        self.spacing = spacing
        self.widgets: List[UIWidget] = []
        self.message_logger = message_logger or MessageLogger(collect_messages=True, print_messages=True)
        
        # Create the container widget
        self.widget = DebugUIWidget(message_logger=self.message_logger)
        self._setup_layout()
        
        # Log row creation
        self.message_logger.log_ui_event("DebugRow", "row_created", {
            "spacing": spacing,
            "row_id": id(self)
        })
    
    def _setup_layout(self):
        """Set up the horizontal layout"""
        layout = DebugDirectionalLayout(self.widget, message_logger=self.message_logger)
        layout.set_parent_widget(self.widget)
        self.widget.set_layout(layout)
        self._layout = layout
        
        self.message_logger.log_ui_event("DebugRow", "layout_setup", {
            "row_id": id(self)
        })
    
    def add_widget(self, widget: UIWidget, expand: bool = False) -> None:
        """Add a widget to the row"""
        self.widgets.append(widget)
        if expand:
            self._layout.add_widget(widget, Direction.CENTER, expand=True)
        else:
            self._layout.add_widget(widget, Direction.WEST)
        
        self.message_logger.log_ui_event("DebugRow", "widget_added", {
            "widget_type": widget.__class__.__name__,
            "expand": expand,
            "row_id": id(self),
            "widget_id": id(widget)
        })
    
    def add_label(self, text: str, style: str = "") -> UILabel:
        """Add a label to the row"""
        label = DebugUILabel(text, message_logger=self.message_logger)
        if style:
            label.set_style(style)
        self.add_widget(label)
        return label
    
    def add_text_input(self, placeholder: str = "", expand: bool = True, style: str = "") -> UITextInput:
        """Add a text input to the row"""
        text_input = DebugUITextInput(message_logger=self.message_logger)
        if placeholder:
            text_input.set_placeholder(placeholder)
        if style:
            text_input.set_style(style)
        self.add_widget(text_input, expand=expand)
        return text_input
    
    def add_button(self, text: str, callback: Optional[Callable] = None, style: str = "") -> UIButton:
        """Add a button to the row"""
        button = DebugUIButton(text, message_logger=self.message_logger)
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
        
        self.message_logger.log_ui_event("DebugRow", "row_cleared", {
            "row_id": id(self)
        })
    
    def get_widgets(self) -> List[UIWidget]:
        """Get all widgets in the row"""
        return self.widgets.copy()


class DebugForm(DebugStack):
    """Headless form widget - a stack of labeled input rows that matches Qt behavior"""
    
    def __init__(self, ui_implementation, spacing: int = 10, parent: Optional[UIWidget] = None,
                 message_logger: Optional[MessageLogger] = None):
        super().__init__(ui_implementation, spacing, parent, message_logger)
        self.rows: List[DebugRow] = []
        
        # Log form creation
        self.message_logger.log_ui_event("DebugForm", "form_created", {
            "spacing": spacing,
            "form_id": id(self)
        })
    
    def add_field(self, label_text: str, placeholder: str = "", 
                  input_style: str = "", label_style: str = "") -> tuple[UILabel, UITextInput]:
        """Add a labeled input field to the form"""
        row = DebugRow(self.ui, spacing=5, message_logger=self.message_logger)
        self.rows.append(row)
        
        # Add label
        label = row.add_label(label_text, style=label_style or "font-weight: bold; margin-right: 10px;")
        
        # Add text input
        text_input = row.add_text_input(placeholder, expand=True, 
                                      style=input_style or "padding: 8px; font-size: 14px;")
        
        # Add the row to the form
        self.add_widget(row.widget)
        
        self.message_logger.log_ui_event("DebugForm", "field_added", {
            "label_text": label_text,
            "placeholder": placeholder,
            "form_id": id(self),
            "row_id": id(row)
        })
        
        return label, text_input
    
    def add_button_row(self, buttons: List[tuple[str, Optional[Callable], str]]) -> List[UIButton]:
        """Add a row of buttons to the form"""
        button_row = DebugButtonRow(self.ui, message_logger=self.message_logger)
        button_list = []
        
        for text, callback, style in buttons:
            button = button_row.add_button(text, callback, style)
            button_list.append(button)
        
        self.add_widget(button_row.widget)
        
        self.message_logger.log_ui_event("DebugForm", "button_row_added", {
            "button_count": len(buttons),
            "form_id": id(self)
        })
        
        return button_list
    
    def get_rows(self) -> List[DebugRow]:
        """Get all rows in the form"""
        return self.rows.copy()


class DebugButtonRow(DebugRow):
    """Headless specialized row for buttons with consistent styling that matches Qt behavior"""
    
    def __init__(self, ui_implementation, spacing: int = 10, parent: Optional[UIWidget] = None,
                 message_logger: Optional[MessageLogger] = None):
        super().__init__(ui_implementation, spacing, parent, message_logger)
        self.buttons: List[UIButton] = []
        
        # Log button row creation
        self.message_logger.log_ui_event("DebugButtonRow", "button_row_created", {
            "spacing": spacing,
            "button_row_id": id(self)
        })
    
    def add_button(self, text: str, callback: Optional[Callable] = None, 
                   style: str = "", align: str = "right") -> UIButton:
        """Add a button to the button row"""
        button = DebugUIButton(text, message_logger=self.message_logger)
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
        
        self.message_logger.log_ui_event("DebugButtonRow", "button_added", {
            "button_text": text,
            "align": align,
            "button_row_id": id(self),
            "button_id": id(button)
        })
        
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
