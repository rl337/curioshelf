"""
Qt Dialog Auto-Responder Plugin for CurioShelf Testing

This plugin provides automatic dialog interaction for Qt applications during scripted testing.
It should only be used in test environments, never in production.
"""

import tempfile
from pathlib import Path
from typing import Any, Dict, Optional, List
from PySide6.QtCore import QObject, QTimer, Signal
from PySide6.QtWidgets import QApplication, QDialog, QLineEdit, QPushButton, QMessageBox

from curioshelf.plugin_system import Plugin


class QtDialogAutoResponder(QObject):
    """Qt-based dialog auto-responder for scripted testing"""
    
    dialog_auto_responded = Signal(str, dict)  # dialog_type, config
    
    def __init__(self):
        super().__init__()
        self.enabled = False
        self.response_configs = {}
        self.delay_ms = 100
        self._setup_default_responses()
    
    def _setup_default_responses(self):
        """Setup default auto-responses for common dialogs"""
        # Default project creation response
        self.response_configs['project_dialog_create'] = {
            'project_name': 'Script Test Project',
            'project_path': str(Path(tempfile.gettempdir()) / 'curioshelf_script_test'),
            'action': 'create'
        }
        
        # Default project open response
        self.response_configs['project_dialog_open'] = {
            'action': 'open'
        }
    
    def set_response_config(self, dialog_type: str, mode: str, config: Dict[str, Any]):
        """Set response configuration for a specific dialog type and mode"""
        key = f"{dialog_type}_{mode}"
        self.response_configs[key] = config
    
    def auto_respond_to_dialog(self, dialog: QDialog, dialog_type: str, mode: str):
        """Auto-respond to a dialog"""
        if not self.enabled:
            return
        
        key = f"{dialog_type}_{mode}"
        config = self.response_configs.get(key, {})
        
        if not config:
            print(f"[AUTO-RESPONDER] No configuration found for {key}")
            return
        
        print(f"[AUTO-RESPONDER] Auto-responding to {dialog_type} dialog in {mode} mode")
        
        # Use a timer to allow the dialog to be shown first
        QTimer.singleShot(self.delay_ms, lambda: self._execute_auto_response(dialog, config, dialog_type, mode))
    
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
            
            # Find and fill project name field
            project_name_input = self._find_widget_by_type(dialog, QLineEdit, "project_name")
            if project_name_input:
                print(f"[AUTO-RESPONDER] Found project name input: {project_name_input.objectName()}")
                project_name_input.setText(config.get('project_name', 'Test Project'))
                print(f"[AUTO-RESPONDER] Set project name: {config.get('project_name')}")
            else:
                print(f"[AUTO-RESPONDER] Project name input not found")
            
            # Find and fill project path field
            project_path_input = self._find_widget_by_type(dialog, QLineEdit, "project_path")
            if project_path_input:
                print(f"[AUTO-RESPONDER] Found project path input: {project_path_input.objectName()}")
                project_path = config.get('project_path', '')
                project_path_input.setText(project_path)
                print(f"[AUTO-RESPONDER] Set project path: {project_path}")
                print(f"[AUTO-RESPONDER] Project path input text after setting: {project_path_input.text()}")
            else:
                print(f"[AUTO-RESPONDER] Project path input not found")
            
            # Find and click create button
            create_button = self._find_widget_by_type(dialog, QPushButton, "create")
            if create_button:
                print(f"[AUTO-RESPONDER] Found create button: {create_button.objectName()}")
                # Add a small delay to ensure text fields are updated
                QTimer.singleShot(100, lambda: self._delayed_create_project(dialog))
            else:
                print(f"[AUTO-RESPONDER] Create button not found")
                raise AssertionError("No suitable button found for project creation")
            
        except Exception as e:
            error_msg = f"Project creation auto-response failed: {e}"
            print(f"[AUTO-RESPONDER ERROR] {error_msg}")
            raise AssertionError(error_msg)
    
    def _auto_respond_project_open(self, dialog: QDialog, config: Dict[str, Any]):
        """Auto-respond to project open dialog"""
        print(f"[AUTO-RESPONDER] Starting project open auto-response")
        
        try:
            # Find project list and select first item
            project_list = self._find_widget_by_type(dialog, type(None), "project_list")  # QListWidget
            if project_list and hasattr(project_list, 'count') and project_list.count() > 0:
                project_list.setCurrentRow(0)
                print(f"[AUTO-RESPONDER] Selected first project in list")
                
                # Find and click open button
                open_button = self._find_widget_by_type(dialog, QPushButton, "open")
                if open_button:
                    open_button.click()
                    print(f"[AUTO-RESPONDER] Clicked open button")
                else:
                    # Try double-clicking the list item
                    project_list.itemDoubleClicked.emit(project_list.item(0))
                    print(f"[AUTO-RESPONDER] Double-clicked project item")
            else:
                print(f"[AUTO-RESPONDER] No projects in list, canceling")
                dialog.reject()
                
        except Exception as e:
            error_msg = f"Project open auto-response failed: {e}"
            print(f"[AUTO-RESPONDER ERROR] {error_msg}")
            raise AssertionError(error_msg)
    
    def _delayed_create_project(self, dialog):
        """Delayed project creation to ensure text fields are updated"""
        try:
            print(f"[AUTO-RESPONDER] Delayed create_project call")
            if hasattr(dialog, 'create_project'):
                dialog.create_project()
            else:
                print(f"[AUTO-RESPONDER] Dialog has no create_project method")
        except Exception as e:
            print(f"[AUTO-RESPONDER] Delayed create_project failed: {e}")
    
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


class QtDialogResponderPlugin(Plugin):
    """Plugin that provides Qt dialog auto-responding for testing"""
    
    def __init__(self):
        super().__init__("qt_dialog_responder", "1.0.0")
        self.responder: Optional[QtDialogAutoResponder] = None
    
    def initialize(self, application: Any) -> bool:
        """Initialize the dialog responder"""
        try:
            # Only initialize if we have a Qt application
            app = QApplication.instance()
            if not app:
                print("[QT DIALOG RESPONDER] No QApplication available, skipping initialization")
                return True  # Return True to not fail the test, but don't initialize
            
            self.responder = QtDialogAutoResponder()
            return True
        except Exception as e:
            print(f"Failed to initialize Qt dialog responder plugin: {e}")
            return False
    
    def cleanup(self) -> bool:
        """Cleanup the dialog responder"""
        if self.responder:
            self.responder.enabled = False
            self.responder = None
        return True
    
    def get_responder(self) -> Optional[QtDialogAutoResponder]:
        """Get the dialog responder instance"""
        return self.responder
