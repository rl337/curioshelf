"""
Headless implementations of layout widgets that match Qt behavior exactly
"""

from typing import List, Optional, Any, Callable, Tuple
from curioshelf.ui.abstraction import UIWidget, UILayout, UIButton, UILabel, UITextInput
from .ui_widgets import DebugUIWidget, DebugUILabel, DebugUITextInput, DebugUIButton, DebugUILayout
from .message_system import MessageLogger


class DebugLayoutWidget(DebugUIWidget):
    """Base class for headless layout widgets that manage their own internal layout"""
    
    def __init__(self, ui_factory, parent: Optional[UIWidget] = None, 
                 message_logger: Optional[MessageLogger] = None):
        super().__init__(message_logger=message_logger)
        self.ui = ui_factory
        self.parent = parent
        self.widgets: List[UIWidget] = []
        
        # Create the container widget
        self.widget = DebugUIWidget(message_logger=message_logger)
        self._setup_layout()
        
        # Log layout widget creation
        self.message_logger.log_ui_event(self.__class__.__name__, "layout_widget_created", {
            "widget_type": self.__class__.__name__,
            "widget_id": id(self)
        })
    
    def _setup_layout(self) -> None:
        """Set up the internal layout for this widget"""
        layout = DebugUILayout("vertical", message_logger=self.message_logger)
        self.widget.set_layout(layout)
        self._layout = layout
        
        self.message_logger.log_ui_event(self.__class__.__name__, "layout_setup", {
            "widget_id": id(self)
        })
    
    def add_widget(self, widget: UIWidget, **kwargs) -> None:
        """Add a widget to this layout widget"""
        self.widgets.append(widget)
        self._add_widget_to_layout(widget, **kwargs)
        
        self.message_logger.log_ui_event(self.__class__.__name__, "widget_added", {
            "widget_type": widget.__class__.__name__,
            "widget_id": id(widget),
            "layout_widget_id": id(self)
        })
    
    def _add_widget_to_layout(self, widget: UIWidget, **kwargs) -> None:
        """Add a widget to the internal layout"""
        self._layout.add_widget(widget)
    
    def remove_widget(self, widget: UIWidget) -> None:
        """Remove a widget from this layout widget"""
        if widget in self.widgets:
            self.widgets.remove(widget)
            self._remove_widget_from_layout(widget)
            
            self.message_logger.log_ui_event(self.__class__.__name__, "widget_removed", {
                "widget_type": widget.__class__.__name__,
                "widget_id": id(widget),
                "layout_widget_id": id(self)
            })
    
    def _remove_widget_from_layout(self, widget: UIWidget) -> None:
        """Remove a widget from the internal layout"""
        self._layout.remove_widget(widget)
    
    def clear(self) -> None:
        """Clear all widgets from this layout widget"""
        for widget in self.widgets.copy():
            self.remove_widget(widget)
        
        self.message_logger.log_ui_event(self.__class__.__name__, "layout_cleared", {
            "widget_id": id(self)
        })
    
    def get_widgets(self) -> List[UIWidget]:
        """Get all widgets in this layout widget"""
        return self.widgets.copy()


class DebugStackWidget(DebugLayoutWidget):
    """Headless stack widget that arranges its children vertically"""
    
    def __init__(self, ui_factory, spacing: int = 5, parent: Optional[UIWidget] = None,
                 message_logger: Optional[MessageLogger] = None):
        self.spacing = spacing
        super().__init__(ui_factory, parent, message_logger)
        
        self.message_logger.log_ui_event("DebugStackWidget", "stack_widget_created", {
            "spacing": spacing,
            "widget_id": id(self)
        })
    
    def _setup_layout(self) -> None:
        """Set up vertical layout"""
        layout = DebugUILayout("vertical", message_logger=self.message_logger)
        self.widget.set_layout(layout)
        self._layout = layout
        
        self.message_logger.log_ui_event("DebugStackWidget", "vertical_layout_setup", {
            "spacing": self.spacing,
            "widget_id": id(self)
        })
    
    # Convenience methods for common widgets
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


class DebugRowWidget(DebugLayoutWidget):
    """Headless row widget that arranges its children horizontally"""
    
    def __init__(self, ui_factory, spacing: int = 5, parent: Optional[UIWidget] = None,
                 message_logger: Optional[MessageLogger] = None):
        self.spacing = spacing
        super().__init__(ui_factory, parent, message_logger)
        
        self.message_logger.log_ui_event("DebugRowWidget", "row_widget_created", {
            "spacing": spacing,
            "widget_id": id(self)
        })
    
    def _setup_layout(self) -> None:
        """Set up horizontal layout"""
        layout = DebugUILayout("horizontal", message_logger=self.message_logger)
        self.widget.set_layout(layout)
        self._layout = layout
        
        self.message_logger.log_ui_event("DebugRowWidget", "horizontal_layout_setup", {
            "spacing": self.spacing,
            "widget_id": id(self)
        })
    
    def _add_widget_to_layout(self, widget: UIWidget, expand: bool = False, **kwargs) -> None:
        """Add widget to horizontal layout"""
        if expand:
            self._layout.add_widget(widget, expand=True)
        else:
            self._layout.add_widget(widget)
    
    # Convenience methods for common widgets
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


class DebugFormWidget(DebugStackWidget):
    """Headless form widget that creates a form with labeled input fields"""
    
    def __init__(self, ui_factory, spacing: int = 10, parent: Optional[UIWidget] = None,
                 message_logger: Optional[MessageLogger] = None):
        super().__init__(ui_factory, spacing, parent, message_logger)
        self.rows: List[DebugRowWidget] = []
        
        self.message_logger.log_ui_event("DebugFormWidget", "form_widget_created", {
            "spacing": spacing,
            "widget_id": id(self)
        })
    
    def add_field(self, label_text: str, placeholder: str = "", 
                  input_style: str = "", label_style: str = "") -> Tuple[UILabel, UITextInput]:
        """Add a labeled input field to the form"""
        row = DebugRowWidget(self.ui, spacing=5, message_logger=self.message_logger)
        self.rows.append(row)
        
        # Add label
        label = row.add_label(label_text, style=label_style or "font-weight: bold; margin-right: 10px;")
        
        # Add text input
        text_input = row.add_text_input(placeholder, expand=True, 
                                      style=input_style or "padding: 8px; font-size: 14px;")
        
        # Add the row to the form
        self.add_widget(row.widget)
        
        self.message_logger.log_ui_event("DebugFormWidget", "field_added", {
            "label_text": label_text,
            "placeholder": placeholder,
            "form_id": id(self),
            "row_id": id(row)
        })
        
        return label, text_input
    
    def add_button_row(self, buttons: List[Tuple[str, Optional[Callable], str]]) -> List[UIButton]:
        """Add a row of buttons to the form"""
        button_row = DebugButtonRowWidget(self.ui, message_logger=self.message_logger)
        button_list = []
        
        for text, callback, style in buttons:
            button = button_row.add_button(text, callback, style)
            button_list.append(button)
        
        self.add_widget(button_row.widget)
        
        self.message_logger.log_ui_event("DebugFormWidget", "button_row_added", {
            "button_count": len(buttons),
            "form_id": id(self)
        })
        
        return button_list
    
    def get_rows(self) -> List[DebugRowWidget]:
        """Get all rows in the form"""
        return self.rows.copy()


class DebugButtonRowWidget(DebugRowWidget):
    """Headless specialized row widget for buttons with consistent styling"""
    
    def __init__(self, ui_factory, spacing: int = 10, parent: Optional[UIWidget] = None,
                 message_logger: Optional[MessageLogger] = None):
        super().__init__(ui_factory, spacing, parent, message_logger)
        self.buttons: List[UIButton] = []
        
        self.message_logger.log_ui_event("DebugButtonRowWidget", "button_row_widget_created", {
            "spacing": spacing,
            "widget_id": id(self)
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
        
        # Add to row
        self.add_widget(button)
        self.buttons.append(button)
        
        self.message_logger.log_ui_event("DebugButtonRowWidget", "button_added", {
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


class DebugTableWidget(DebugLayoutWidget):
    """Headless table widget that arranges its children in a grid layout"""
    
    def __init__(self, ui_factory, rows: int = 1, cols: int = 1, spacing: int = 5,
                 parent: Optional[UIWidget] = None, message_logger: Optional[MessageLogger] = None):
        self.rows = rows
        self.cols = cols
        self.spacing = spacing
        super().__init__(ui_factory, parent, message_logger)
        
        self.message_logger.log_ui_event("DebugTableWidget", "table_widget_created", {
            "rows": rows,
            "cols": cols,
            "spacing": spacing,
            "widget_id": id(self)
        })
    
    def _setup_layout(self) -> None:
        """Set up grid layout"""
        layout = DebugUILayout("grid", message_logger=self.message_logger)
        self.widget.set_layout(layout)
        self._layout = layout
        
        self.message_logger.log_ui_event("DebugTableWidget", "grid_layout_setup", {
            "rows": self.rows,
            "cols": self.cols,
            "spacing": self.spacing,
            "widget_id": id(self)
        })
    
    def _add_widget_to_layout(self, widget: UIWidget, row: int = 0, col: int = 0, 
                             rowspan: int = 1, colspan: int = 1, **kwargs) -> None:
        """Add widget to grid layout"""
        self._layout.add_widget(widget, row=row, col=col, rowspan=rowspan, colspan=colspan)
        
        self.message_logger.log_ui_event("DebugTableWidget", "widget_added_to_grid", {
            "widget_type": widget.__class__.__name__,
            "row": row,
            "col": col,
            "rowspan": rowspan,
            "colspan": colspan,
            "widget_id": id(widget),
            "table_id": id(self)
        })
    
    def add_widget_at(self, widget: UIWidget, row: int, col: int, 
                      rowspan: int = 1, colspan: int = 1) -> None:
        """Add a widget at a specific grid position"""
        self.add_widget(widget, row=row, col=col, rowspan=rowspan, colspan=colspan)
