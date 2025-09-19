"""
Test configuration and utilities for CurioShelf tests

This module provides test configuration, timeouts, and utilities for handling
modal dialogs and other UI elements that might block tests.
"""

import pytest
import time
import threading
from typing import Any, Callable, Optional
from unittest.mock import Mock, patch


class TimeoutHelper:
    """Context manager for test timeouts"""
    
    def __init__(self, timeout_seconds: float = 5.0):
        self.timeout_seconds = timeout_seconds
        self.timer = None
        self.timed_out = False
    
    def __enter__(self):
        self.timer = threading.Timer(self.timeout_seconds, self._timeout_handler)
        self.timer.start()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.timer:
            self.timer.cancel()
        
        if self.timed_out:
            raise TimeoutError(f"Test timed out after {self.timeout_seconds} seconds")
    
    def _timeout_handler(self):
        self.timed_out = True
        print(f"\n[TEST TIMEOUT] Test exceeded {self.timeout_seconds} seconds - likely due to modal dialog")


class ModalDialogHandler:
    """Handles modal dialogs in tests by mocking them"""
    
    def __init__(self):
        self.patches = []
    
    def __enter__(self):
        # Mock file dialogs to return None (cancelled) immediately
        self.patches.append(patch('curioshelf.ui.qtimpl.ui_widgets.QtUIFileDialog.get_open_file_name', return_value=None))
        self.patches.append(patch('curioshelf.ui.qtimpl.ui_widgets.QtUIFileDialog.get_save_file_name', return_value=None))
        
        # Mock message boxes to not show modally
        self.patches.append(patch('curioshelf.ui.qtimpl.ui_widgets.QtUIMessageBox.show_info'))
        self.patches.append(patch('curioshelf.ui.qtimpl.ui_widgets.QtUIMessageBox.show_warning'))
        self.patches.append(patch('curioshelf.ui.qtimpl.ui_widgets.QtUIMessageBox.show_error'))
        self.patches.append(patch('curioshelf.ui.qtimpl.ui_widgets.QtUIMessageBox.show_question', return_value=False))
        
        # Start all patches
        for patch_obj in self.patches:
            patch_obj.start()
        
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        # Stop all patches
        for patch_obj in self.patches:
            patch_obj.stop()


def run_test_with_timeout(test_func: Callable, timeout_seconds: float = 5.0) -> Any:
    """Run a test function with timeout protection"""
    result = None
    exception = None
    
    def run_test():
        nonlocal result, exception
        try:
            result = test_func()
        except Exception as e:
            exception = e
    
    thread = threading.Thread(target=run_test)
    thread.daemon = True
    thread.start()
    thread.join(timeout_seconds)
    
    if thread.is_alive():
        print(f"\n[TEST TIMEOUT] Test exceeded {timeout_seconds} seconds")
        raise TimeoutError(f"Test exceeded {timeout_seconds} seconds")
    
    if exception:
        raise exception
    
    return result


@pytest.fixture
def modal_dialog_handler():
    """Fixture to handle modal dialogs in tests"""
    with ModalDialogHandler() as handler:
        yield handler


@pytest.fixture
def test_timeout():
    """Fixture for test timeouts"""
    return TestTimeout


def log_ui_events():
    """Enable detailed UI event logging for debugging"""
    import logging
    
    # Set up detailed logging for UI components
    ui_logger = logging.getLogger('curioshelf.ui')
    ui_logger.setLevel(logging.DEBUG)
    
    # Create a handler that prints to console
    handler = logging.StreamHandler()
    handler.setLevel(logging.DEBUG)
    
    # Create formatter
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    handler.setFormatter(formatter)
    
    # Add handler to logger
    ui_logger.addHandler(handler)
    
    return ui_logger


def detect_modal_dialogs():
    """Detect if any modal dialogs are currently open"""
    try:
        from PySide6.QtWidgets import QApplication
        app = QApplication.instance()
        if app:
            # Check for modal widgets
            for widget in app.allWidgets():
                if hasattr(widget, 'isModal') and widget.isModal():
                    print(f"[MODAL DETECTED] {type(widget).__name__} is modal")
                    return True
        return False
    except ImportError:
        # PySide6 not available
        return False
    except Exception as e:
        print(f"[MODAL DETECT ERROR] {e}")
        return False


class UIInstrumentationHelper:
    """Instrumentation for UI testing"""
    
    def __init__(self):
        self.ui_events = []
        self.modal_detections = []
    
    def start_monitoring(self):
        """Start monitoring UI events and modal dialogs"""
        self.ui_events.clear()
        self.modal_detections.clear()
        
        # Set up periodic modal detection
        self._start_modal_monitoring()
    
    def stop_monitoring(self):
        """Stop monitoring"""
        self._stop_modal_monitoring()
    
    def _start_modal_monitoring(self):
        """Start monitoring for modal dialogs"""
        def check_modals():
            if detect_modal_dialogs():
                self.modal_detections.append(time.time())
                print(f"[MODAL DETECTED] at {time.time()}")
        
        # Check every 0.5 seconds
        self._modal_timer = threading.Timer(0.5, check_modals)
        self._modal_timer.start()
    
    def _stop_modal_monitoring(self):
        """Stop modal monitoring"""
        if hasattr(self, '_modal_timer'):
            self._modal_timer.cancel()
    
    def get_modal_count(self):
        """Get number of modal dialogs detected"""
        return len(self.modal_detections)
    
    def get_ui_events(self):
        """Get captured UI events"""
        return self.ui_events.copy()


@pytest.fixture
def ui_instrumentation():
    """Fixture for UI instrumentation"""
    instrumentation = TestUIInstrumentation()
    instrumentation.start_monitoring()
    yield instrumentation
    instrumentation.stop_monitoring()
