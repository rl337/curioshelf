"""
Qt Heartbeat Plugin for CurioShelf Testing

This plugin provides heartbeat monitoring for Qt applications during scripted testing.
It should only be used in test environments, never in production.
"""

import time
from typing import Any, Optional
from PySide6.QtCore import QObject, QTimer, Signal
from PySide6.QtWidgets import QApplication

from curioshelf.plugin_system import Plugin


class QtHeartbeatMonitor(QObject):
    """Qt-based heartbeat monitor for scripted testing"""
    
    timeout_reached = Signal()
    
    def __init__(self, timeout_seconds: int = 8):
        super().__init__()
        self.timeout_seconds = timeout_seconds
        self.start_time = time.time()
        self.last_activity_time = time.time()
        self.expected_focus_widgets = set()
        self.heartbeat_timer = QTimer()
        self.heartbeat_timer.timeout.connect(self.check_timeout)
        self.heartbeat_timer.start(100)  # Check every 100ms
        
    def add_expected_focus_widget(self, widget):
        """Add a widget that we expect to have focus during script execution"""
        self.expected_focus_widgets.add(widget)
        
    def update_activity(self):
        """Call this when script makes progress"""
        self.last_activity_time = time.time()
        
    def check_timeout(self):
        """Called by Qt timer - check if we've timed out"""
        current_time = time.time()
        
        # Check for overall timeout
        if current_time - self.start_time > self.timeout_seconds:
            print(f"SCRIPT TIMEOUT: Script execution exceeded {self.timeout_seconds} seconds")
            self.timeout_reached.emit()
            return
        
        # Check for activity timeout (no progress for 3 seconds)
        if current_time - self.last_activity_time > 3.0:
            print(f"SCRIPT TIMEOUT: No activity for 3 seconds")
            self.timeout_reached.emit()
            return
        
        # Check for unexpected focus
        app = QApplication.instance()
        if app:
            focused_widget = app.focusWidget()
            if focused_widget and focused_widget not in self.expected_focus_widgets:
                # Check if it's a modal dialog or unexpected window
                if hasattr(focused_widget, 'isModal') and focused_widget.isModal():
                    print(f"SCRIPT TIMEOUT: Unexpected modal dialog has focus: {focused_widget}")
                    self.timeout_reached.emit()
                    return


class QtHeartbeatPlugin(Plugin):
    """Plugin that provides Qt heartbeat monitoring for testing"""
    
    def __init__(self):
        super().__init__("qt_heartbeat", "1.0.0")
        self.monitor: Optional[QtHeartbeatMonitor] = None
        self.timeout_handler = None
    
    def initialize(self, application: Any) -> bool:
        """Initialize the heartbeat monitor"""
        try:
            # Only initialize if we have a Qt application
            app = QApplication.instance()
            if not app:
                return False
            
            self.monitor = QtHeartbeatMonitor(timeout_seconds=8)
            
            # Set up timeout handler
            def handle_timeout():
                print("Closing all modal dialogs and exiting...")
                app = QApplication.instance()
                if app:
                    for widget in app.allWidgets():
                        if hasattr(widget, 'close') and widget.isModal():
                            print(f"Closing modal dialog: {widget}")
                            widget.close()
                print("Forcing application exit...")
                import sys
                sys.exit(1)
            
            self.monitor.timeout_reached.connect(handle_timeout)
            self.timeout_handler = handle_timeout
            
            return True
        except Exception as e:
            print(f"Failed to initialize Qt heartbeat plugin: {e}")
            return False
    
    def cleanup(self) -> bool:
        """Cleanup the heartbeat monitor"""
        if self.monitor:
            self.monitor.heartbeat_timer.stop()
            self.monitor = None
        return True
    
    def get_monitor(self) -> Optional[QtHeartbeatMonitor]:
        """Get the heartbeat monitor instance"""
        return self.monitor
