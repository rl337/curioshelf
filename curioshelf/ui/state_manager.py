"""
UI State Management for CurioShelf

Manages UI element states based on project and data availability.
Provides centralized state management for enabling/disabling UI elements.
Uses the UI abstraction layer for framework independence.
"""

from typing import Dict, List, Optional, Callable, Any
from .abstraction import UIWidget


class UIStateManager:
    """Manages UI state and provides signals for state changes"""
    
    def __init__(self):
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
        
        # Signal callbacks
        self._signal_callbacks: Dict[str, List[Callable]] = {
            "project_state_changed": [],
            "source_state_changed": [],
            "object_state_changed": [],
            "template_state_changed": []
        }
    
    def connect_signal(self, signal_name: str, callback: Callable):
        """Connect a callback to a signal"""
        if signal_name in self._signal_callbacks:
            self._signal_callbacks[signal_name].append(callback)
    
    def emit_signal(self, signal_name: str, data: Any = None):
        """Emit a signal to all connected callbacks"""
        if signal_name in self._signal_callbacks:
            for callback in self._signal_callbacks[signal_name]:
                callback(data)
    
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
            self.emit_signal("project_state_changed", has_project)
            self._update_all_elements()
    
    def update_source_state(self, has_sources: bool):
        """Update sources availability state"""
        if self.has_sources != has_sources:
            self.has_sources = has_sources
            self.emit_signal("source_state_changed", has_sources)
            self._update_all_elements()
    
    def update_object_state(self, has_objects: bool):
        """Update objects availability state"""
        if self.has_objects != has_objects:
            self.has_objects = has_objects
            self.emit_signal("object_state_changed", has_objects)
            self._update_all_elements()
    
    def update_template_state(self, has_templates: bool):
        """Update templates availability state"""
        if self.has_templates != has_templates:
            self.has_templates = has_templates
            self.emit_signal("template_state_changed", has_templates)
            self._update_all_elements()
    
    def update_all_states(self, has_project: bool, has_sources: bool, 
                         has_objects: bool, has_templates: bool):
        """Update all states at once"""
        self.has_project = has_project
        self.has_sources = has_sources
        self.has_objects = has_objects
        self.has_templates = has_templates
        
        # Emit all signals
        self.emit_signal("project_state_changed", has_project)
        self.emit_signal("source_state_changed", has_sources)
        self.emit_signal("object_state_changed", has_objects)
        self.emit_signal("template_state_changed", has_templates)
        
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
        if isinstance(element, UIWidget):
            element.set_enabled(enabled)
        elif hasattr(element, 'setEnabled'):
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
    
    def create_ghost_overlay(self, parent_widget: Any) -> 'GhostOverlay':
        """Create a ghost overlay for when no project is loaded"""
        return GhostOverlay(parent_widget, self)


class GhostOverlay:
    """Overlay widget that shows when no project is loaded"""
    
    def __init__(self, parent: Any, state_manager: UIStateManager):
        self.parent = parent
        self.state_manager = state_manager
        self.visible = False
        
        # Connect to state changes
        self.state_manager.connect_signal("project_state_changed", self.on_project_state_changed)
    
    def on_project_state_changed(self, has_project: bool):
        """Handle project state changes"""
        self.visible = not has_project
    
    def show(self):
        """Show the ghost overlay"""
        self.visible = True
    
    def hide(self):
        """Hide the ghost overlay"""
        self.visible = False
