"""
Sources list view for the main window
"""

from typing import Optional, Callable, List
from pathlib import Path

from curioshelf.ui.abstraction import UIWidget, UILayout, UIButton, UILabel, UIGroupBox, UIListWidget
from curioshelf.ui.views.base_view import BaseView


class SourcesListView(BaseView):
    """View for displaying and managing sources"""
    
    def __init__(self, ui_implementation, parent: Optional[UIWidget] = None,
                 on_import_source: Optional[Callable[[], None]] = None):
        self.on_import_source = on_import_source
        self.sources = []
        super().__init__(ui_implementation, parent)
    
    def _setup_ui(self) -> None:
        """Set up the sources list UI"""
        # Create main container
        self.widget = self.ui.create_widget("sources_list_view")
        
        # Create main layout
        main_layout = self.ui.create_layout("vertical")
        self.widget.set_layout(main_layout)
        
        # Create title
        title_label = self.ui.create_label("Sources")
        title_label.set_text("Sources")
        title_label.set_style("font-size: 18px; font-weight: bold; margin-bottom: 20px;")
        main_layout.add_widget(title_label)
        
        # Create sources group
        sources_group = self.ui.create_group_box("Project Sources")
        sources_group.set_title("Project Sources")
        sources_layout = self.ui.create_layout("vertical")
        sources_group.set_layout(sources_layout)
        
        # Sources list
        self.sources_list = self.ui.create_list_widget()
        self.sources_list.set_style("width: 100%; height: 300px; margin-bottom: 15px;")
        sources_layout.add_widget(self.sources_list)
        
        # Sources buttons
        sources_btn_layout = self.ui.create_layout("horizontal")
        sources_btn_layout.set_style("justify-content: flex-start; gap: 10px;")
        
        self.import_btn = self.ui.create_button("Import Source")
        self.import_btn.set_style("padding: 8px 16px; font-size: 14px;")
        self.import_btn.clicked.connect(self._on_import_source)
        sources_btn_layout.add_widget(self.import_btn)
        
        self.remove_btn = self.ui.create_button("Remove Selected")
        self.remove_btn.set_style("padding: 8px 16px; font-size: 14px;")
        self.remove_btn.clicked.connect(self._on_remove_source)
        self.remove_btn.set_enabled(False)
        sources_btn_layout.add_widget(self.remove_btn)
        
        sources_layout.add_widget(sources_btn_layout)
        main_layout.add_widget(sources_group)
        
        # Create empty state message
        self.empty_label = self.ui.create_label("No sources imported yet")
        self.empty_label.set_text("No sources imported yet. Click 'Import Source' to add your first source.")
        self.empty_label.set_style("text-align: center; color: #666; margin-top: 50px; font-style: italic;")
        self.empty_label.set_visible(True)
        main_layout.add_widget(self.empty_label)
        
        # Update UI state
        self._update_ui_state()
    
    def get_title(self) -> str:
        """Get the title for this view"""
        return "Sources"
    
    def _on_import_source(self) -> None:
        """Handle import source button click"""
        if self.on_import_source:
            self.on_import_source()
    
    def _on_remove_source(self) -> None:
        """Handle remove source button click"""
        selected_item = self.sources_list.get_selected_item()
        if selected_item:
            # Remove from list
            self.sources_list.remove_item(selected_item)
            self._update_ui_state()
    
    def add_source(self, source_path: Path) -> None:
        """Add a source to the list"""
        source_name = source_path.name
        item = self.sources_list.create_item(source_name)
        item.set_data(str(source_path), source_name)
        self.sources_list.add_item(item)
        self.sources.append(source_path)
        self._update_ui_state()
    
    def remove_source(self, source_path: Path) -> None:
        """Remove a source from the list"""
        # Find and remove the item
        for i in range(self.sources_list.get_item_count()):
            item = self.sources_list.get_item(i)
            if item and item.get_data("path") == str(source_path):
                self.sources_list.remove_item(item)
                break
        
        # Remove from sources list
        if source_path in self.sources:
            self.sources.remove(source_path)
        
        self._update_ui_state()
    
    def clear_sources(self) -> None:
        """Clear all sources"""
        self.sources_list.clear()
        self.sources.clear()
        self._update_ui_state()
    
    def get_sources(self) -> List[Path]:
        """Get list of current sources"""
        return self.sources.copy()
    
    def _update_ui_state(self) -> None:
        """Update UI state based on current sources"""
        has_sources = len(self.sources) > 0
        
        # Show/hide empty state
        self.empty_label.set_visible(not has_sources)
        
        # Enable/disable remove button
        self.remove_btn.set_enabled(has_sources)
