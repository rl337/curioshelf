"""
Debug implementation of the UI abstraction layer

This module provides command-line implementations of all UI abstraction interfaces
that emit messages instead of rendering GUI components. Useful for development,
testing, and debugging purposes.
"""

from .ui_factory import DebugUIFactory, DebugUIImplementation
from .ui_widgets import (
    DebugUIWidget, DebugUIButton, DebugUITextInput, DebugUIComboBox, 
    DebugUIListWidget, DebugUICanvas, DebugUIMessageBox, DebugUIFileDialog, 
    DebugUIProgressBar, DebugUIGroupBox, DebugUITabWidget, DebugUISplitter
)

# Import to register the implementation
from . import ui_factory

__all__ = [
    'DebugUIFactory', 'DebugUIImplementation',
    'DebugUIWidget', 'DebugUIButton', 'DebugUITextInput', 'DebugUIComboBox', 
    'DebugUIListWidget', 'DebugUICanvas', 'DebugUIMessageBox', 'DebugUIFileDialog', 
    'DebugUIProgressBar', 'DebugUIGroupBox', 'DebugUITabWidget', 'DebugUISplitter'
]
