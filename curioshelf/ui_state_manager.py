"""
UI State Management for CurioShelf

Manages UI element states based on project and data availability.
Provides centralized state management for enabling/disabling UI elements.
"""

from typing import Dict, List, Optional, Callable, Any
from PySide6.QtWidgets import QWidget, QAction
from PySide6.QtCore import QObject, Signal


class UIStateManager(QObject):
    """Manages UI state and provides signals for state changes"""
    
    # Signals for state changes
    project_state_changed = Signal(bool)  # True if project is loaded
    source_state_changed = Signal(bool)   # True if sources are available
    object_state_changed = Signal(bool)   # True if objects are available
    template_state_changed = Signal(bool) # True if templates are available
    
    def __init__(self):
        super().__init__()
        
        # State flags
        self.has_project = False
        self.has_sources = False
        self.has_objects = False
        self.has_templates = False
        
        # Registered UI elements
        self.registered_elements: Dict[str, Dict[str, Any]] = {}
        
        # State groups - elements that should be enabled/disabled together
        self.state_groups: Dict[str, List[str]] = {
            "project_required": [],      # Requires project to be loaded
            "source_required": [],       # Requires sources to be available
            "object_required": [],       # Requires objects to be available
            "template_required": [],     # Requires templates to be available
            "project_or_source": [],     # Requires either project or sources
            "always_enabled": []         # Always enabled (like project creation)
        }
    
    def register_element(self, element_id: str, element: Any, 
                        state_groups: List[str] = None, 
                        custom_enable_func: Optional[Callable] = None):
        """Register a UI element for state management"""
        if state_groups is None:
            state_groups = ["project_required"]
        
        self.registered_elements[element_id] = {
            "element": element,
            "state_groups": state_groups,
            "custom_enable_func": custom_enable_func
        }
        
        # Add to state groups
        for group in state_groups:
            if group not in self.state_groups:
                self.state_groups[group] = []
            self.state_groups[group].append(element_id)
        
        # Apply initial state
        self._update_element_state(element_id)
    
    def unregister_element(self, element_id: str):
        """Unregister a UI element"""
        if element_id in self.registered_elements:
            # Remove from state groups
            element_groups = self.registered_elements[element_id]["state_groups"]
            for group in element_groups:
                if group in self.state_groups and element_id in self.state_groups[group]:
                    self.state_groups[group].remove(element_id)
            
            # Remove from registered elements
            del self.registered_elements[element_id]
    
    def update_project_state(self, has_project: bool):
        """Update project availability state"""
        if self.has_project != has_project:
            self.has_project = has_project
            self.project_state_changed.emit(has_project)
            self._update_all_elements()
    
    def update_source_state(self, has_sources: bool):
        """Update sources availability state"""
        if self.has_sources != has_sources:
            self.has_sources = has_sources
            self.source_state_changed.emit(has_sources)
            self._update_all_elements()
    
    def update_object_state(self, has_objects: bool):
        """Update objects availability state"""
        if self.has_objects != has_objects:
            self.has_objects = has_objects
            self.object_state_changed.emit(has_objects)
            self._update_all_elements()
    
    def update_template_state(self, has_templates: bool):
        """Update templates availability state"""
        if self.has_templates != has_templates:
            self.has_templates = has_templates
            self.template_state_changed.emit(has_templates)
            self._update_all_elements()
    
    def update_all_states(self, has_project: bool, has_sources: bool, 
                         has_objects: bool, has_templates: bool):
        """Update all states at once"""
        self.has_project = has_project
        self.has_sources = has_sources
        self.has_objects = has_objects
        self.has_templates = has_templates
        
        # Emit all signals
        self.project_state_changed.emit(has_project)
        self.source_state_changed.emit(has_sources)
        self.object_state_changed.emit(has_objects)
        self.template_state_changed.emit(has_templates)
        
        self._update_all_elements()
    
    def _update_all_elements(self):
        """Update all registered elements"""
        for element_id in self.registered_elements:
            self._update_element_state(element_id)
    
    def _update_element_state(self, element_id: str):
        """Update the state of a specific element"""
        if element_id not in self.registered_elements:
            return
        
        element_data = self.registered_elements[element_id]
        element = element_data["element"]
        state_groups = element_data["state_groups"]
        custom_func = element_data["custom_enable_func"]
        
        # Use custom function if provided
        if custom_func:
            enabled = custom_func(self.has_project, self.has_sources, 
                                self.has_objects, self.has_templates)
        else:
            # Use default logic based on state groups
            enabled = self._should_be_enabled(state_groups)
        
        # Apply state to element
        self._set_element_enabled(element, enabled)
    
    def _should_be_enabled(self, state_groups: List[str]) -> bool:
        """Determine if element should be enabled based on state groups"""
        for group in state_groups:
            if group == "always_enabled":
                return True
            elif group == "project_required":
                if not self.has_project:
                    return False
            elif group == "source_required":
                if not self.has_sources:
                    return False
            elif group == "object_required":
                if not self.has_objects:
                    return False
            elif group == "template_required":
                if not self.has_templates:
                    return False
            elif group == "project_or_source":
                if not (self.has_project or self.has_sources):
                    return False
        
        return True
    
    def _set_element_enabled(self, element: Any, enabled: bool):
        """Set the enabled state of a UI element"""
        if hasattr(element, 'setEnabled'):
            element.setEnabled(enabled)
        elif hasattr(element, 'set_enabled'):
            element.set_enabled(enabled)
        elif hasattr(element, 'setVisible'):
            # For some elements, we might want to hide instead of disable
            element.setVisible(enabled)
        elif hasattr(element, 'set_visible'):
            element.set_visible(enabled)
    
    def get_state_summary(self) -> Dict[str, bool]:
        """Get a summary of current states"""
        return {
            "has_project": self.has_project,
            "has_sources": self.has_sources,
            "has_objects": self.has_objects,
            "has_templates": self.has_templates
        }
    
    def create_ghost_overlay(self, parent_widget: QWidget) -> 'GhostOverlay':
        """Create a ghost overlay for when no project is loaded"""
        return GhostOverlay(parent_widget, self)


class GhostOverlay(QWidget):
    """Overlay widget that shows when no project is loaded"""
    
    def __init__(self, parent: QWidget, state_manager: UIStateManager):
        super().__init__(parent)
        self.state_manager = state_manager
        self.setup_ui()
        
        # Connect to state changes
        self.state_manager.project_state_changed.connect(self.on_project_state_changed)
    
    def setup_ui(self):
        """Setup the ghost overlay UI"""
        from PySide6.QtWidgets import QVBoxLayout, QLabel, QPushButton
        from PySide6.QtCore import Qt
        from PySide6.QtGui import QFont
        
        # Make overlay cover the entire parent
        self.setGeometry(0, 0, self.parent().width(), self.parent().height())
        
        # Create layout
        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignCenter)
        
        # Create ghost message
        ghost_label = QLabel("No Project Loaded")
        ghost_label.setAlignment(Qt.AlignCenter)
        font = QFont()
        font.setPointSize(24)
        font.setBold(True)
        ghost_label.setFont(font)
        ghost_label.setStyleSheet("color: #666666;")
        layout.addWidget(ghost_label)
        
        # Create instruction text
        instruction_label = QLabel("Create a new project or load an existing one to get started")
        instruction_label.setAlignment(Qt.AlignCenter)
        instruction_label.setStyleSheet("color: #888888; margin: 20px;")
        layout.addWidget(instruction_label)
        
        # Create buttons
        button_layout = QVBoxLayout()
        button_layout.setSpacing(10)
        
        new_project_btn = QPushButton("Create New Project")
        new_project_btn.setMinimumSize(200, 40)
        new_project_btn.clicked.connect(self.create_new_project)
        button_layout.addWidget(new_project_btn)
        
        load_project_btn = QPushButton("Load Existing Project")
        load_project_btn.setMinimumSize(200, 40)
        load_project_btn.clicked.connect(self.load_existing_project)
        button_layout.addWidget(load_project_btn)
        
        layout.addLayout(button_layout)
        
        # Initially hidden
        self.hide()
    
    def on_project_state_changed(self, has_project: bool):
        """Handle project state changes"""
        if has_project:
            self.hide()
        else:
            self.show()
            # Update size to match parent
            self.setGeometry(0, 0, self.parent().width(), self.parent().height())
    
    def create_new_project(self):
        """Emit signal to create new project"""
        # This would be connected to the main window's new project action
        pass
    
    def load_existing_project(self):
        """Emit signal to load existing project"""
        # This would be connected to the main window's load project action
        pass
    
    def resizeEvent(self, event):
        """Handle resize events"""
        super().resizeEvent(event)
        # Keep overlay covering the entire parent
        self.setGeometry(0, 0, self.parent().width(), self.parent().height())
