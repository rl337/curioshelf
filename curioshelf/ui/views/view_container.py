"""
View container widget for managing multiple views in the main window
"""

from typing import Optional, Dict, Any
from curioshelf.ui.abstraction import UIWidget, UILayout
from curioshelf.ui.views.base_view import BaseView


class ViewContainer(UIWidget):
    """Container widget that manages multiple views and switches between them"""
    
    def __init__(self, ui_implementation):
        super().__init__()
        self.ui = ui_implementation
        self.current_view: Optional[BaseView] = None
        self.views: Dict[str, BaseView] = {}
        self.default_view: Optional[BaseView] = None
        
        # Create the container widget
        self.container_widget = self.ui.create_widget("view_container")
        self.container_widget.set_style("flex: 1; width: 100%; height: 100%;")
        
        # Create a layout for the container
        self.container_layout = self.ui.create_layout("vertical")
        self.container_widget.set_layout(self.container_layout)
        
        # Set up the container to fill the available space
        self.container_widget.set_visible(True)
    
    def register_view(self, name: str, view: BaseView) -> None:
        """Register a view with the container"""
        self.views[name] = view
        # Initially hide all views
        view.hide()
        # Add the view's widget to the container layout
        if view.widget:
            self.container_layout.add_widget(view.widget)
    
    def set_default_view(self, view: BaseView) -> None:
        """Set the default view to show when no other view is active"""
        self.default_view = view
        if not self.current_view:
            self.show_view(view)
    
    def show_view(self, view: BaseView) -> None:
        """Show a specific view and hide all others"""
        # Hide current view
        if self.current_view and self.current_view != view:
            self.current_view.hide()
        
        # Show new view
        self.current_view = view
        view.show()
        
        # Ensure the view's widget is visible and takes up the full space
        if view.widget:
            view.widget.set_visible(True)
            # Make sure the view fills the container
            view.widget.set_style("flex: 1; width: 100%; height: 100%;")
    
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
    
    def get_view(self, name: str) -> Optional[BaseView]:
        """Get a view by name"""
        return self.views.get(name)
    
    def get_widget(self) -> UIWidget:
        """Get the container widget for adding to layouts"""
        return self.container_widget
    
    def set_visible(self, visible: bool) -> None:
        """Show or hide the container"""
        super().set_visible(visible)
        self.container_widget.set_visible(visible)
    
    def is_visible(self) -> bool:
        """Check if the container is visible"""
        return self.container_widget.is_visible() if hasattr(self.container_widget, 'is_visible') else True
