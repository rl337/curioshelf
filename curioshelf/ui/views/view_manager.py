"""
View manager for handling view switching in the main window
"""

from typing import Optional, Dict, Any
from pathlib import Path

from curioshelf.ui.abstraction import UIWidget, UILayout
from curioshelf.ui.views.base_view import BaseView
from curioshelf.ui.views.project_create_view import ProjectCreateView
from curioshelf.ui.views.project_open_view import ProjectOpenView


class ViewManager:
    """Manages view switching in the main window"""
    
    def __init__(self, ui_implementation, main_widget: UIWidget):
        self.ui = ui_implementation
        self.main_widget = main_widget
        self.current_view: Optional[BaseView] = None
        self.views: Dict[str, BaseView] = {}
        self.default_view: Optional[BaseView] = None
        
        # Create main layout
        self.main_layout = self.ui.create_layout("vertical")
        self.main_widget.set_layout(self.main_layout)
        
        # Create view container
        self.view_container = self.ui.create_widget("view_container")
        self.view_container.set_style("flex: 1;")
        self.view_container.set_visible(True)  # Make sure the container is visible
        self.main_layout.add_widget(self.view_container)
    
    def register_view(self, name: str, view: BaseView) -> None:
        """Register a view with the manager"""
        self.views[name] = view
        view.hide()  # Hide by default
    
    def set_default_view(self, view: BaseView) -> None:
        """Set the default view to show when no other view is active"""
        self.default_view = view
        if not self.current_view:
            self.show_view(view)
    
    def show_view(self, view: BaseView) -> None:
        """Show a specific view"""
        # Hide current view
        if self.current_view:
            self.current_view.hide()
        
        # Show new view
        self.current_view = view
        view.show()
        
        # Update view container
        if hasattr(self.view_container, 'clear'):
            self.view_container.clear()
        if view.widget:
            self.view_container.add_widget(view.widget)
            # Ensure the widget is visible
            view.widget.set_visible(True)
    
    def show_view_by_name(self, name: str) -> bool:
        """Show a view by name"""
        if name in self.views:
            self.show_view(self.views[name])
            return True
        return False
    
    def hide_current_view(self) -> None:
        """Hide the current view and return to default"""
        if self.current_view:
            self.current_view.hide()
            self.current_view = None
        
        if self.default_view:
            self.show_view(self.default_view)
    
    def get_current_view(self) -> Optional[BaseView]:
        """Get the current view"""
        return self.current_view
    
    def is_view_visible(self, name: str) -> bool:
        """Check if a specific view is visible"""
        if name in self.views:
            return self.views[name].is_visible()
        return False
    
    def cleanup(self) -> None:
        """Clean up all views"""
        for view in self.views.values():
            view.cleanup()
        self.views.clear()
        self.current_view = None
        self.default_view = None
