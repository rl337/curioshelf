"""
Headless implementation of the UI abstraction layer

This module provides command-line implementations of all UI abstraction interfaces
that emit messages instead of rendering GUI components. Useful for testing and
headless operation.
"""

from .ui_factory import HeadlessUIFactory, HeadlessUIImplementation
from .ui_widgets import (
    HeadlessUIWidget, HeadlessUIButton, HeadlessUITextInput, HeadlessUIComboBox, 
    HeadlessUIListWidget, HeadlessUICanvas, HeadlessUIMessageBox, HeadlessUIFileDialog, 
    HeadlessUIProgressBar, HeadlessUIGroupBox, HeadlessUITabWidget, HeadlessUISplitter
)

# Import to register the implementation
from . import ui_factory

__all__ = [
    'HeadlessUIFactory', 'HeadlessUIImplementation',
    'HeadlessUIWidget', 'HeadlessUIButton', 'HeadlessUITextInput', 'HeadlessUIComboBox', 
    'HeadlessUIListWidget', 'HeadlessUICanvas', 'HeadlessUIMessageBox', 'HeadlessUIFileDialog', 
    'HeadlessUIProgressBar', 'HeadlessUIGroupBox', 'HeadlessUITabWidget', 'HeadlessUISplitter'
]
