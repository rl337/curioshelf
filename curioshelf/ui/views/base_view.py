"""
Base view class for main window views
"""

from abc import ABC, abstractmethod
from typing import Optional, Dict, Any
from pathlib import Path

from curioshelf.ui.abstraction import UIWidget, UILayout, UIButton, UILabel, UITextInput, UIGroupBox


class BaseView(ABC):
    """Base class for main window views"""
    
    def __init__(self, ui_implementation, parent: Optional[UIWidget] = None):
        self.ui = ui_implementation
        self.parent = parent
        self.widget = None
        self._setup_ui()
    
    @abstractmethod
    def _setup_ui(self) -> None:
        """Set up the UI for this view"""
        pass
    
    @abstractmethod
    def get_title(self) -> str:
        """Get the title for this view"""
        pass
    
    def show(self) -> None:
        """Show this view"""
        if self.widget:
            self.widget.set_visible(True)
    
    def hide(self) -> None:
        """Hide this view"""
        if self.widget:
            self.widget.set_visible(False)
    
    def is_visible(self) -> bool:
        """Check if this view is visible"""
        return self.widget.is_visible() if self.widget else False
    
    def cleanup(self) -> None:
        """Clean up resources"""
        if self.widget:
            self.widget.cleanup()
