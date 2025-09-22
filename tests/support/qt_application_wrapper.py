"""
Qt Application Wrapper for Tests

This module provides a wrapper around Qt applications that automatically
instruments them with heartbeat monitoring and timeouts to prevent test hanging.
"""

import sys
import threading
import time
from typing import Optional, Any
from contextlib import contextmanager

# Try to import Qt components
try:
    from PySide6.QtWidgets import QApplication
    from PySide6.QtCore import QTimer, QObject, Signal
    QT_AVAILABLE = True
except ImportError:
    QT_AVAILABLE = False


class QtApplicationWrapper:
    """Wrapper for Qt applications that provides automatic heartbeat monitoring"""
    
    def __init__(self):
        self._original_qapplication = None
        self._wrapped_app = None
        self._heartbeat_timer = None
        self._timeout_timer = None
        self._last_activity = time.time()
        self._activity_timeout = 30.0  # 30 seconds timeout
        self._heartbeat_interval = 1.0  # 1 second heartbeat
        self._monitoring = False
        self._monitor_thread = None
        
    def wrap_application(self, app: Any) -> Any:
        """Wrap a Qt application with heartbeat monitoring"""
        if not QT_AVAILABLE:
            return app
            
        self._wrapped_app = app
        self._start_monitoring()
        return app
    
    def _start_monitoring(self):
        """Start heartbeat monitoring"""
        if not QT_AVAILABLE or self._monitoring:
            return
            
        self._monitoring = True
        self._last_activity = time.time()
        
        # Create heartbeat timer
        self._heartbeat_timer = QTimer()
        self._heartbeat_timer.timeout.connect(self._heartbeat_check)
        self._heartbeat_timer.start(int(self._heartbeat_interval * 1000))
        
        # Create timeout timer
        self._timeout_timer = QTimer()
        self._timeout_timer.timeout.connect(self._timeout_handler)
        self._timeout_timer.setSingleShot(True)
        self._timeout_timer.start(int(self._activity_timeout * 1000))
        
        print(f"[QT WRAPPER] Started heartbeat monitoring (timeout: {self._activity_timeout}s)")
    
    def _stop_monitoring(self):
        """Stop heartbeat monitoring"""
        if not self._monitoring:
            return
            
        self._monitoring = False
        
        if self._heartbeat_timer:
            self._heartbeat_timer.stop()
            self._heartbeat_timer = None
            
        if self._timeout_timer:
            self._timeout_timer.stop()
            self._timeout_timer = None
            
        print("[QT WRAPPER] Stopped heartbeat monitoring")
    
    def _heartbeat_check(self):
        """Check if application is still responsive"""
        if not self._monitoring:
            return
            
        current_time = time.time()
        time_since_activity = current_time - self._last_activity
        
        # Check for modal dialogs
        if self._wrapped_app:
            self._check_for_modal_dialogs()
        
        # Reset timeout timer
        if self._timeout_timer:
            self._timeout_timer.stop()
            self._timeout_timer.start(int(self._activity_timeout * 1000))
    
    def _check_for_modal_dialogs(self):
        """Check for unexpected modal dialogs and close them"""
        if not QT_AVAILABLE or not self._wrapped_app:
            return
            
        try:
            # Get all top-level widgets
            widgets = self._wrapped_app.allWidgets()
            for widget in widgets:
                if hasattr(widget, 'isModal') and widget.isModal():
                    print(f"[QT WRAPPER] Detected modal dialog: {widget.__class__.__name__}")
                    # Close the modal dialog
                    if hasattr(widget, 'reject'):
                        widget.reject()
                    elif hasattr(widget, 'close'):
                        widget.close()
                    print(f"[QT WRAPPER] Closed modal dialog: {widget.__class__.__name__}")
        except Exception as e:
            print(f"[QT WRAPPER] Error checking for modal dialogs: {e}")
    
    def _timeout_handler(self):
        """Handle timeout - force quit the application"""
        print(f"[QT WRAPPER] TIMEOUT: Application hung for {self._activity_timeout} seconds")
        print("[QT WRAPPER] Force quitting application...")
        
        if self._wrapped_app:
            try:
                # Try to close all windows
                for widget in self._wrapped_app.allWidgets():
                    if hasattr(widget, 'close'):
                        widget.close()
                
                # Force quit
                self._wrapped_app.quit()
            except Exception as e:
                print(f"[QT WRAPPER] Error during force quit: {e}")
        
        # Force exit the process
        import os
        os._exit(1)
    
    def update_activity(self):
        """Update the last activity time"""
        self._last_activity = time.time()
    
    def cleanup(self):
        """Cleanup the wrapper"""
        self._stop_monitoring()


# Global wrapper instance
_qt_wrapper = QtApplicationWrapper()


def wrap_qt_application(app: Any) -> Any:
    """Wrap a Qt application with heartbeat monitoring"""
    return _qt_wrapper.wrap_application(app)


def cleanup_qt_wrapper():
    """Cleanup the global Qt wrapper"""
    _qt_wrapper.cleanup()


@contextmanager
def qt_application_context():
    """Context manager for Qt applications with automatic monitoring"""
    try:
        yield _qt_wrapper
    finally:
        _qt_wrapper.cleanup()


# Monkey patch QApplication to automatically wrap it
if QT_AVAILABLE:
    # Global variables for Qt wrapper
    _original_qapplication_init = QApplication.__init__
    _heartbeat_timer = None
    _app_instance_ref = None
    
    def _handle_timeout():
        """Handle timeout by closing modal dialogs and exiting"""
        print("[QT WRAPPER] Timeout detected, closing modal dialogs...")
        if _app_instance_ref:
            for widget in QApplication.allWidgets():
                if hasattr(widget, 'close') and widget.isModal():
                    print(f"[QT WRAPPER] Closing modal dialog: {widget}")
                    widget.close()
        print("[QT WRAPPER] Forcing application quit...")
        QApplication.quit()
    
    def _wrapped_qapplication_init(self, *args, **kwargs):
        """Wrapped QApplication constructor"""
        _original_qapplication_init(self, *args, **kwargs)
        # Start monitoring after initialization
        global _heartbeat_timer, _app_instance_ref
        _app_instance_ref = self
        if _heartbeat_timer is None:
            _heartbeat_timer = QTimer()
            _heartbeat_timer.timeout.connect(_handle_timeout)
            _heartbeat_timer.start(1000)  # Check every second
        print("[QT WRAPPER] QApplication initialized with monitoring")
    
    # Replace the constructor
    QApplication.__init__ = _wrapped_qapplication_init
    print("[QT WRAPPER] QApplication monkey patched for automatic monitoring")
