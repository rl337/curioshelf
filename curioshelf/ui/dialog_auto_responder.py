"""
Dialog Auto-Responder for automated testing
This module provides automatic responses to dialogs during scripted testing
"""

from typing import Dict, Any, Optional, Callable, List
from pathlib import Path
import tempfile
import time

from PySide6.QtWidgets import QDialog, QLineEdit, QPushButton, QListWidget, QListWidgetItem
from PySide6.QtCore import QTimer, QObject, Signal

from curioshelf.projects import ProjectInfo


class DialogAutoResponder(QObject):
    """Automatically responds to dialogs during scripted testing"""
    
    # Signal emitted when a dialog is auto-responded to
    dialog_auto_responded = Signal(str, Dict[str, Any])
    
    def __init__(self, enabled: bool = True, delay_ms: int = 100):
        super().__init__()
        self.enabled = enabled
        self.delay_ms = delay_ms
        self.response_configs = {}
        self._setup_default_responses()
    
    def _setup_default_responses(self):
        """Setup default auto-responses for common dialogs"""
        # Default project creation response
        self.response_configs['project_dialog_create'] = {
            'project_name': 'Test Project',
            'project_path': str(Path(tempfile.gettempdir()) / 'curioshelf_test_project'),
            'action': 'create'
        }
        
        # Default project opening response
        self.response_configs['project_dialog_open'] = {
            'action': 'cancel'  # Cancel by default since we don't have real projects
        }
    
    def set_response_config(self, dialog_type: str, mode: str, config: Dict[str, Any]):
        """Set auto-response configuration for a specific dialog type and mode"""
        key = f"{dialog_type}_{mode}"
        self.response_configs[key] = config
    
    def auto_respond_to_dialog(self, dialog: QDialog, dialog_type: str, mode: str) -> bool:
        """Automatically respond to a dialog if auto-responder is enabled"""
        if not self.enabled:
            return False
        
        key = f"{dialog_type}_{mode}"
        config = self.response_configs.get(key)
        
        if not config:
            print(f"[AUTO-RESPONDER] No config found for {key}, skipping auto-response")
            return False
        
        print(f"[AUTO-RESPONDER] Auto-responding to {dialog_type} dialog in {mode} mode")
        
        # Execute auto-response synchronously to ensure errors are caught
        try:
            self._execute_auto_response_sync(dialog, config, dialog_type, mode)
            return True
        except Exception as e:
            print(f"[AUTO-RESPONDER ERROR] {e}")
            raise  # Re-raise the exception to be caught by the calling code
    
    def _execute_auto_response_with_timeout(self, dialog: QDialog, config: Dict[str, Any], dialog_type: str, mode: str):
        """Execute auto-response with timeout to prevent hanging"""
        try:
            # Set up a timeout timer
            timeout_timer = QTimer()
            timeout_timer.timeout.connect(lambda: self._handle_auto_response_timeout(dialog, dialog_type, mode))
            timeout_timer.setSingleShot(True)
            timeout_timer.start(5000)  # 5 second timeout
            
            # Execute the auto-response
            self._execute_auto_response(dialog, config, dialog_type, mode)
            
            # Cancel timeout if successful
            timeout_timer.stop()
            
        except Exception as e:
            error_msg = f"Auto-response failed for {dialog_type}_{mode}: {e}"
            print(f"[AUTO-RESPONDER ERROR] {error_msg}")
            raise AssertionError(error_msg)
    
    def _handle_auto_response_timeout(self, dialog: QDialog, dialog_type: str, mode: str):
        """Handle auto-response timeout by raising assertion error"""
        error_msg = f"Auto-response timeout for {dialog_type}_{mode} - dialog did not complete within 5 seconds"
        print(f"[AUTO-RESPONDER TIMEOUT] {error_msg}")
        
        # Try to close the dialog
        try:
            dialog.reject()
        except:
            pass
        
        raise AssertionError(error_msg)
    
    def _execute_auto_response_sync(self, dialog: QDialog, config: Dict[str, Any], dialog_type: str, mode: str):
        """Execute auto-response synchronously with immediate error handling and timeout"""
        print(f"[AUTO-RESPONDER] Executing synchronous auto-response for {dialog_type}_{mode}")
        
        # Validate dialog
        if not dialog or not dialog.isVisible():
            raise AssertionError("Dialog is not visible or has been closed")
        
        # Set up a timeout that will force close the dialog
        from PySide6.QtCore import QTimer
        
        def force_close_dialog():
            print(f"[AUTO-RESPONDER] TIMEOUT: Forcing dialog close after 5 seconds")
            dialog.reject()
            raise AssertionError("Auto-responder operation timed out after 5 seconds")
        
        # Set up timeout timer
        timeout_timer = QTimer()
        timeout_timer.setSingleShot(True)
        timeout_timer.timeout.connect(force_close_dialog)
        timeout_timer.start(5000)  # 5 second timeout
        
        try:
            # Execute the appropriate auto-response
            if mode == 'create' and dialog_type == 'project_dialog':
                self._auto_respond_project_create(dialog, config)
            elif mode == 'open' and dialog_type == 'project_dialog':
                self._auto_respond_project_open(dialog, config)
            else:
                raise AssertionError(f"Unknown dialog type/mode: {dialog_type}/{mode}")
            
            # Cancel timeout since we completed successfully
            timeout_timer.stop()
            print(f"[AUTO-RESPONDER] Auto-response completed for {dialog_type}_{mode}")
            
        except Exception as e:
            # Cancel timeout and re-raise the error
            timeout_timer.stop()
            raise
    
    def _execute_auto_response(self, dialog: QDialog, config: Dict[str, Any], dialog_type: str, mode: str):
        """Execute the auto-response for a dialog"""
        try:
            if mode == 'create' and dialog_type == 'project_dialog':
                self._auto_respond_project_create(dialog, config)
            elif mode == 'open' and dialog_type == 'project_dialog':
                self._auto_respond_project_open(dialog, config)
            else:
                print(f"[AUTO-RESPONDER] Unknown dialog type/mode: {dialog_type}/{mode}")
                return
            
            # Emit signal
            self.dialog_auto_responded.emit(f"{dialog_type}_{mode}", config)
            print(f"[AUTO-RESPONDER] Auto-response completed for {dialog_type}_{mode}")
            
        except Exception as e:
            print(f"[AUTO-RESPONDER] Error during auto-response: {e}")
    
    def _auto_respond_project_create(self, dialog: QDialog, config: Dict[str, Any]):
        """Auto-respond to project creation dialog"""
        print(f"[AUTO-RESPONDER] Starting project creation auto-response")
        
        try:
            # Validate dialog is still valid
            if not dialog or not dialog.isVisible():
                raise AssertionError("Dialog is not visible or has been closed")
            
            # Debug: List all QLineEdit widgets in the dialog
            print(f"[AUTO-RESPONDER] Debug: Listing all QLineEdit widgets in dialog:")
            self._debug_all_line_edits(dialog)
            
            # Find and fill project name field
            project_name_input = self._find_widget_by_type(dialog, QLineEdit, "project_name")
            if project_name_input:
                print(f"[AUTO-RESPONDER] Found project name input: {project_name_input.objectName()}")
                project_name_input.setText(config.get('project_name', 'Test Project'))
                print(f"[AUTO-RESPONDER] Set project name: {config.get('project_name')}")
            else:
                print(f"[AUTO-RESPONDER] Project name input not found")
            
            # Find and fill project path field (avoid triggering browse button)
            project_path_input = self._find_widget_by_type(dialog, QLineEdit, "project_path")
            if project_path_input:
                print(f"[AUTO-RESPONDER] Found project path input: {project_path_input.objectName()}")
                project_path = config.get('project_path', '')
                project_path_input.setText(project_path)
                print(f"[AUTO-RESPONDER] Set project path: {project_path}")
                print(f"[AUTO-RESPONDER] Project path input text after setting: {project_path_input.text()}")
            else:
                print(f"[AUTO-RESPONDER] Project path input not found")
            
            # Try multiple methods to find the create button
            create_button = None
            
            # Method 1: Find by object name
            create_button = self._find_widget_by_type(dialog, QPushButton, "create")
            if create_button:
                print(f"[AUTO-RESPONDER] Found create button by object name")
            
            # Method 2: Find by text content
            if not create_button:
                create_button = self._find_button_by_text(dialog, "create")
                if create_button:
                    print(f"[AUTO-RESPONDER] Found create button by text")
            
            # Method 3: Find any button that's not browse
            if not create_button:
                create_button = self._find_any_button_except(dialog, ["browse", "cancel", "close"])
                if create_button:
                    print(f"[AUTO-RESPONDER] Found button (excluding browse/cancel): {create_button.text()}")
            
            # Method 4: List all buttons for debugging
            if not create_button:
                self._debug_all_buttons(dialog)
                raise AssertionError("No suitable button found for project creation")
            
            # Instead of clicking the button, directly call the dialog's create method
            print(f"[AUTO-RESPONDER] Bypassing button click, calling create_project directly")
            
            # Get the project name and path from the inputs
            project_name = project_name_input.text() if project_name_input else config.get('project_name', 'Test Project')
            project_path = project_path_input.text() if project_path_input else config.get('project_path', '')
            
            # Add a small delay to ensure text fields are updated
            from PySide6.QtCore import QTimer
            QTimer.singleShot(100, lambda: self._delayed_create_project(dialog))
            
            print(f"[AUTO-RESPONDER] Direct method call completed")
            
        except Exception as e:
            error_msg = f"Project creation auto-response failed: {e}"
            print(f"[AUTO-RESPONDER ERROR] {error_msg}")
            raise AssertionError(error_msg)
    
    def _delayed_create_project(self, dialog):
        """Delayed project creation to ensure text fields are updated"""
        try:
            print(f"[AUTO-RESPONDER] Delayed create_project call")
            
            # Debug: Check what the dialog sees
            if hasattr(dialog, 'project_name_input'):
                name_text = dialog.project_name_input.text() if dialog.project_name_input else "None"
                print(f"[AUTO-RESPONDER] Dialog project_name_input.text(): '{name_text}'")
            
            if hasattr(dialog, 'project_path_input'):
                path_text = dialog.project_path_input.text() if dialog.project_path_input else "None"
                print(f"[AUTO-RESPONDER] Dialog project_path_input.text(): '{path_text}'")
            
            if hasattr(dialog, 'create_project'):
                dialog.create_project()
            else:
                print(f"[AUTO-RESPONDER] Dialog has no create_project method")
        except Exception as e:
            print(f"[AUTO-RESPONDER] Delayed create_project failed: {e}")
    
    def _debug_all_line_edits(self, parent: QObject, indent: str = ""):
        """Debug helper to list all QLineEdit widgets in the dialog"""
        from PySide6.QtWidgets import QLineEdit
        
        if isinstance(parent, QLineEdit):
            obj_name = parent.objectName() if hasattr(parent, 'objectName') else "NoName"
            text = parent.text() if hasattr(parent, 'text') else "NoText"
            print(f"[AUTO-RESPONDER] {indent}QLineEdit: '{obj_name}' = '{text}'")
        
        for child in parent.children():
            self._debug_all_line_edits(child, indent + "  ")
    
    def _debug_all_buttons(self, parent: QObject, indent: str = ""):
        """Debug helper to list all buttons in the dialog"""
        from PySide6.QtWidgets import QPushButton
        
        for child in parent.children():
            if isinstance(child, QPushButton):
                button_text = child.text() if hasattr(child, 'text') else "No text"
                object_name = child.objectName() if hasattr(child, 'objectName') else "No name"
                print(f"{indent}Button: '{button_text}' (name: '{object_name}')")
            
            # Recursively search children
            self._debug_all_buttons(child, indent + "  ")
    
    def _find_any_button_except(self, parent: QObject, exclude_texts: List[str]) -> Optional[QObject]:
        """Find any button except those with specified text"""
        from PySide6.QtWidgets import QPushButton
        
        for child in parent.children():
            if isinstance(child, QPushButton):
                button_text = child.text().lower() if hasattr(child, 'text') else ""
                if not any(exclude in button_text for exclude in exclude_texts):
                    print(f"[AUTO-RESPONDER] Found button: '{child.text()}'")
                    return child
            
            # Recursively search children
            result = self._find_any_button_except(child, exclude_texts)
            if result:
                return result
        
        return None
    
    def _auto_respond_project_open(self, dialog: QDialog, config: Dict[str, Any]):
        """Auto-respond to project opening dialog"""
        action = config.get('action', 'cancel')
        
        if action == 'cancel':
            print(f"[AUTO-RESPONDER] Canceling project open dialog")
            dialog.reject()
        elif action == 'open':
            # Find and select a project from the list
            project_list = self._find_widget_by_type(dialog, QListWidget, "project_list")
            if project_list and project_list.count() > 0:
                # Select first item
                project_list.setCurrentRow(0)
                print(f"[AUTO-RESPONDER] Selected project from list")
                
                # Find and click open button
                open_button = self._find_widget_by_type(dialog, QPushButton, "open")
                if open_button:
                    print(f"[AUTO-RESPONDER] Clicking open button")
                    open_button.click()
                else:
                    dialog.accept()
            else:
                print(f"[AUTO-RESPONDER] No projects in list, canceling")
                dialog.reject()
    
    def _find_widget_by_type(self, parent: QObject, widget_type: type, hint: str = "") -> Optional[QObject]:
        """Find a widget of the specified type within the parent widget"""
        if isinstance(parent, widget_type):
            if not hint:
                return parent
            # Check if this widget matches the hint
            child_name = parent.objectName().lower() if hasattr(parent, 'objectName') else ""
            child_text = parent.text().lower() if hasattr(parent, 'text') else ""
            child_class = str(type(parent)).lower()
            
            if (child_name == hint.lower() or 
                hint in child_text or 
                hint in child_class):
                print(f"[AUTO-RESPONDER] Found widget: {child_class} - '{child_text}' - '{child_name}'")
                return parent
        
        for child in parent.children():
            if isinstance(child, widget_type):
                # Additional filtering by hint if provided
                if hint:
                    # Check object name, text, and class name
                    child_name = child.objectName().lower() if hasattr(child, 'objectName') else ""
                    child_text = child.text().lower() if hasattr(child, 'text') else ""
                    child_class = str(type(child)).lower()
                    
                    print(f"[AUTO-RESPONDER] Checking widget: {child_class} - '{child_text}' - '{child_name}' (looking for '{hint}')")
                    
                    if (child_name == hint.lower() or 
                        hint in child_text or 
                        hint in child_class):
                        print(f"[AUTO-RESPONDER] Found widget: {child_class} - '{child_text}' - '{child_name}'")
                        return child
                else:
                    return child
            
            # Recursively search children
            result = self._find_widget_by_type(child, widget_type, hint)
            if result:
                return result
        
        return None
    
    def _find_button_by_text(self, parent: QObject, text_hint: str) -> Optional[QObject]:
        """Find a button by its text content"""
        from PySide6.QtWidgets import QPushButton
        
        for child in parent.children():
            if isinstance(child, QPushButton):
                button_text = child.text().lower() if hasattr(child, 'text') else ""
                if text_hint.lower() in button_text:
                    print(f"[AUTO-RESPONDER] Found button by text: '{child.text()}'")
                    return child
            
            # Recursively search children
            result = self._find_button_by_text(child, text_hint)
            if result:
                return result
        
        return None


# Global auto-responder instance
_auto_responder = DialogAutoResponder()


def get_auto_responder() -> DialogAutoResponder:
    """Get the global auto-responder instance"""
    return _auto_responder


def set_auto_responder_enabled(enabled: bool):
    """Enable or disable auto-responder"""
    _auto_responder.enabled = enabled


def set_auto_response_config(dialog_type: str, mode: str, config: Dict[str, Any]):
    """Set auto-response configuration"""
    _auto_responder.set_response_config(dialog_type, mode, config)
