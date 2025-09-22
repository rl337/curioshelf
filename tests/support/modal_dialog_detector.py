"""
Modal Dialog Detector for automated testing
This module detects unexpected modal dialogs and prevents native dialogs from hanging tests
"""

import time
from typing import List, Optional, Callable, Dict, Any
from PySide6.QtWidgets import QApplication, QDialog, QFileDialog, QMessageBox, QWidget
from PySide6.QtCore import QTimer, QObject, Signal, Qt


class ModalDialogDetector(QObject):
    """Detects and handles unexpected modal dialogs during testing"""
    
    # Signal emitted when an unexpected modal dialog is detected
    unexpected_modal_detected = Signal(str, str)
    
    # Signal emitted when focus changes to an unexpected window
    focus_changed = Signal(str, Dict[str, Any])
    
    def __init__(self, enabled: bool = True, timeout_ms: int = 1000):
        super().__init__()
        self.enabled = enabled
        self.timeout_ms = timeout_ms
        self.expected_dialogs = set()
        self.expected_windows = set()
        self.last_focused_widget = None
        self.dialog_timer = None
        self.focus_timer = None
        self._setup_dialog_monitoring()
        self._setup_focus_monitoring()
    
    def _setup_dialog_monitoring(self):
        """Setup monitoring for modal dialogs"""
        if not self.enabled:
            return
        
        # Start monitoring for modal dialogs
        self.dialog_timer = QTimer()
        self.dialog_timer.timeout.connect(self._check_for_modal_dialogs)
        self.dialog_timer.start(100)  # Check every 100ms
    
    def _setup_focus_monitoring(self):
        """Setup monitoring for focus changes"""
        if not self.enabled:
            return
        
        # Start monitoring for focus changes
        self.focus_timer = QTimer()
        self.focus_timer.timeout.connect(self._check_focus_changes)
        self.focus_timer.start(50)  # Check every 50ms for more responsive detection
    
    def expect_dialog(self, dialog_type: str, mode: str = ""):
        """Mark a dialog as expected to prevent false alarms"""
        key = f"{dialog_type}_{mode}" if mode else dialog_type
        self.expected_dialogs.add(key)
        print(f"[MODAL DETECTOR] Expecting dialog: {key}")
    
    def dialog_completed(self, dialog_type: str, mode: str = ""):
        """Mark a dialog as completed"""
        key = f"{dialog_type}_{mode}" if mode else dialog_type
        self.expected_dialogs.discard(key)
        print(f"[MODAL DETECTOR] Dialog completed: {key}")
    
    def expect_window(self, window_title: str):
        """Mark a window as expected to prevent false alarms"""
        self.expected_windows.add(window_title.lower())
        print(f"[MODAL DETECTOR] Expecting window: {window_title}")
    
    def _check_focus_changes(self):
        """Check for focus changes and unexpected windows"""
        if not self.enabled:
            return
        
        app = QApplication.instance()
        if not app:
            return
        
        # Get currently focused widget
        focused_widget = app.focusWidget()
        
        # Check if focus changed
        if focused_widget != self.last_focused_widget:
            self.last_focused_widget = focused_widget
            
            if focused_widget:
                # Get window information
                window_info = self._get_window_info(focused_widget)
                
                # Check if this is an unexpected window
                if self._is_unexpected_window(window_info):
                    print(f"[MODAL DETECTOR] Focus changed to unexpected window: {window_info['title']}")
                    self.focus_changed.emit("unexpected_focus", window_info)
    
    def _get_window_info(self, widget: QWidget) -> Dict[str, Any]:
        """Get detailed information about a window/widget"""
        if not widget:
            return {"title": "None", "type": "None", "visible": False}
        
        # Get the top-level window
        window = widget.window()
        
        info = {
            "title": window.windowTitle() if window else "Unknown",
            "type": type(widget).__name__,
            "visible": widget.isVisible(),
            "modal": window.isModal() if window else False,
            "geometry": widget.geometry() if hasattr(widget, 'geometry') else None,
            "object_name": widget.objectName(),
            "class_name": widget.__class__.__name__,
            "parent": widget.parent().__class__.__name__ if widget.parent() else "None",
            "is_window": widget.isWindow(),
            "is_dialog": isinstance(widget, QDialog),
            "is_file_dialog": isinstance(widget, QFileDialog),
            "is_message_box": isinstance(widget, QMessageBox),
        }
        
        # Add more specific information for dialogs
        if isinstance(widget, QDialog):
            info.update({
                "dialog_result": widget.result(),
                "dialog_accepted": widget.isAccepted(),
            })
        
        return info
    
    def _is_unexpected_window(self, window_info: Dict[str, Any]) -> bool:
        """Check if a window is unexpected"""
        title = window_info.get("title", "").lower()
        
        # Skip if it's an expected window
        if any(expected in title for expected in self.expected_windows):
            return False
        
        # Skip if it's the main application window
        if "curioshelf" in title or "main" in title:
            return False
        
        # Check for unexpected dialog types
        if window_info.get("is_dialog", False):
            return True
        
        # Check for native dialogs (usually have empty or generic titles)
        if (window_info.get("is_file_dialog", False) or 
            window_info.get("is_message_box", False)):
            return True
        
        # Check for windows with suspicious titles
        suspicious_titles = ["open", "save", "browse", "select", "choose", "file"]
        if any(suspicious in title for suspicious in suspicious_titles):
            return True
        
        return False
    
    def _check_for_modal_dialogs(self):
        """Check for unexpected modal dialogs"""
        if not self.enabled:
            return
        
        app = QApplication.instance()
        if not app:
            return
        
        # Check for modal dialogs
        modal_dialogs = self._find_modal_dialogs()
        
        for dialog in modal_dialogs:
            dialog_type = self._identify_dialog_type(dialog)
            if dialog_type and dialog_type not in self.expected_dialogs:
                print(f"[MODAL DETECTOR] Unexpected modal dialog detected: {dialog_type}")
                self.unexpected_modal_detected.emit(dialog_type, str(dialog))
                
                # Close the unexpected dialog
                self._close_unexpected_dialog(dialog)
    
    def _find_modal_dialogs(self) -> List[QDialog]:
        """Find all currently open modal dialogs"""
        app = QApplication.instance()
        if not app:
            return []
        
        modal_dialogs = []
        
        # Check all top-level widgets
        for widget in app.allWidgets():
            if isinstance(widget, QDialog) and widget.isModal():
                modal_dialogs.append(widget)
        
        return modal_dialogs
    
    def _identify_dialog_type(self, dialog: QDialog) -> Optional[str]:
        """Identify the type of dialog"""
        if isinstance(dialog, QFileDialog):
            return "file_dialog"
        elif isinstance(dialog, QMessageBox):
            return "message_box"
        elif "project" in dialog.windowTitle().lower():
            return "project_dialog"
        else:
            return "unknown_dialog"
    
    def _close_unexpected_dialog(self, dialog: QDialog):
        """Close an unexpected dialog"""
        try:
            print(f"[MODAL DETECTOR] Closing unexpected dialog: {dialog.windowTitle()}")
            
            # If it's a message box, extract the error message before closing
            if isinstance(dialog, QMessageBox):
                error_text = dialog.text()
                detailed_text = dialog.detailedText() if hasattr(dialog, 'detailedText') else ""
                print(f"[MODAL DETECTOR] Error message: {error_text}")
                if detailed_text:
                    print(f"[MODAL DETECTOR] Detailed error: {detailed_text}")
            
            dialog.reject()
        except Exception as e:
            print(f"[MODAL DETECTOR] Error closing dialog: {e}")


class NativeDialogPreventer:
    """Prevents native dialogs from being triggered during testing"""
    
    def __init__(self, enabled: bool = True):
        self.enabled = enabled
        self._original_file_dialog = None
        self._original_message_box = None
        self._setup_prevention()
    
    def _setup_prevention(self):
        """Setup prevention of native dialogs"""
        if not self.enabled:
            return
        
        # Override QFileDialog to prevent native dialogs
        self._original_file_dialog = QFileDialog.getOpenFileName
        self._original_message_box = QMessageBox.critical
        
        # Replace with test-friendly versions
        QFileDialog.getOpenFileName = self._mock_file_dialog
        QFileDialog.getExistingDirectory = self._mock_directory_dialog
        QMessageBox.critical = self._mock_message_box
    
    def _mock_file_dialog(self, parent=None, caption="", directory="", filter="", options=None):
        """Mock file dialog that returns a test path"""
        print(f"[NATIVE DIALOG PREVENTER] Mock file dialog called: {caption}")
        # Return a test file path
        return ("/tmp/test_file.txt", "Text Files (*.txt)")
    
    def _mock_directory_dialog(self, parent=None, caption="", directory=""):
        """Mock directory dialog that returns a test directory"""
        print(f"[NATIVE DIALOG PREVENTER] Mock directory dialog called: {caption}")
        # Return a test directory
        return "/tmp/test_directory"
    
    def _mock_message_box(self, parent, title, text, buttons=None, defaultButton=None):
        """Mock message box that doesn't block"""
        print(f"[NATIVE DIALOG PREVENTER] Mock message box: {title} - {text}")
        # Return a default button
        return buttons[0] if buttons else None
    
    def restore(self):
        """Restore original dialog functions"""
        if self._original_file_dialog:
            QFileDialog.getOpenFileName = self._original_file_dialog
        if self._original_message_box:
            QMessageBox.critical = self._original_message_box


# Global instances
_modal_detector = ModalDialogDetector()
_native_preventer = NativeDialogPreventer()


def get_modal_detector() -> ModalDialogDetector:
    """Get the global modal dialog detector"""
    return _modal_detector


def get_native_preventer() -> NativeDialogPreventer:
    """Get the global native dialog preventer"""
    return _native_preventer


def enable_modal_detection(enabled: bool = True):
    """Enable or disable modal dialog detection"""
    _modal_detector.enabled = enabled


def enable_native_prevention(enabled: bool = True):
    """Enable or disable native dialog prevention"""
    _native_preventer.enabled = enabled
    if enabled:
        _native_preventer._setup_prevention()
    else:
        _native_preventer.restore()
