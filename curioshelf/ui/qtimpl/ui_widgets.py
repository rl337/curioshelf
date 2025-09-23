"""
Qt implementations of UI abstraction widgets

This module provides concrete Qt/PySide6 implementations of all UI abstraction interfaces.
"""

from typing import Any, Optional, Callable, List
from pathlib import Path

from PySide6.QtWidgets import (
    QWidget, QMainWindow, QPushButton, QLineEdit, QTextEdit, QComboBox, QListWidget,
    QGraphicsView, QGraphicsScene, QMessageBox, QFileDialog, QProgressBar,
    QGroupBox, QTabWidget, QSplitter, QVBoxLayout, QHBoxLayout, QFormLayout,
    QLabel, QListWidgetItem, QMenuBar, QMenu, QStatusBar
)
from PySide6.QtCore import Qt, QRect, QTimer, Signal, QObject
from PySide6.QtGui import QPixmap, QFont, QPainter, QPen, QBrush, QWheelEvent, QAction

from ..abstraction import (
    UIWidget, UIButton, UILabel, UITextInput, UIComboBox, UIListWidget, UIListItem, UICanvas,
    UIMessageBox, UIFileDialog, UIProgressBar, UIGroupBox, UITabWidget,
    UISplitter, UILayout, UIMenuBar, UIMenu, UIMenuItem, UIStatusBar
)
from tests.ui_debug import UIDebugMixin, get_global_debugger


class QtUIMainWidget(UIWidget, UIDebugMixin):
    """Qt implementation of UIWidget for main window (QMainWindow)"""
    
    def __init__(self) -> None:
        UIWidget.__init__(self)
        UIDebugMixin.__init__(self)
        self._qt_widget = QMainWindow()
        # Set a reasonable default size
        self._qt_widget.resize(800, 600)
        self._qt_widget.setWindowTitle("CurioShelf")
        
        # Set up debugging
        self.set_debugger(get_global_debugger())
        self.debug_log("widget_created", "QtUIMainWidget created", {
            "size": (800, 600),
            "widget_id": id(self)
        })
    
    def set_enabled(self, enabled: bool) -> None:
        """Enable or disable the widget"""
        super().set_enabled(enabled)
        self._qt_widget.setEnabled(enabled)
        self.debug_state_change(f"enabled_{enabled}", {"enabled": enabled})
    
    def set_visible(self, visible: bool) -> None:
        """Show or hide the widget"""
        super().set_visible(visible)
        self._qt_widget.setVisible(visible)
        self.debug_state_change(f"visible_{visible}", {"visible": visible})
    
    def show(self) -> None:
        """Show the widget"""
        super().show()
        self._qt_widget.show()
        self.debug_log("shown", "QtUIMainWidget shown")
    
    def set_layout(self, layout: 'UILayout') -> None:
        """Set the layout for this widget"""
        super().set_layout(layout)
        if hasattr(layout, '_qt_layout'):
            # For QMainWindow, we need to set the central widget
            central_widget = QWidget(self._qt_widget)  # Set parent
            central_widget.setLayout(layout._qt_layout)
            self._qt_widget.setCentralWidget(central_widget)
            # Set the parent widget on the layout so it can parent child widgets
            layout._parent_widget = central_widget
        self.debug_log("layout_set", "Layout set on QtUIMainWidget")
    
    @property
    def qt_widget(self) -> QMainWindow:
        """Get the underlying Qt main window"""
        return self._qt_widget
    
    def set_menu_bar(self, menu_bar: 'QtUIMenuBar') -> None:
        """Set the menu bar for the main window"""
        self._qt_widget.setMenuBar(menu_bar.qt_widget)
        self.debug_log("menu_bar_set", "Menu bar set on main window")
    
    def set_status_bar(self, status_bar: 'QtUIStatusBar') -> None:
        """Set the status bar for the main window"""
        self._qt_widget.setStatusBar(status_bar.qt_widget)
        self.debug_log("status_bar_set", "Status bar set on main window")


class QtUIWidget(UIWidget, UIDebugMixin):
    """Qt implementation of UIWidget"""
    
    def __init__(self, parent: Optional[QWidget] = None) -> None:
        UIWidget.__init__(self)
        UIDebugMixin.__init__(self)
        self._qt_widget = QWidget(parent)
        # Set a reasonable default size
        self._qt_widget.resize(800, 600)
        
        # Set up debugging
        self.set_debugger(get_global_debugger())
        self.debug_log("widget_created", "QtUIWidget created", {
            "size": (800, 600),
            "widget_id": id(self),
            "parent": id(parent) if parent else None
        })
    
    def set_enabled(self, enabled: bool) -> None:
        """Enable or disable the widget"""
        super().set_enabled(enabled)
        self._qt_widget.setEnabled(enabled)
        self.debug_state_change(f"enabled_{enabled}", {"enabled": enabled})
    
    def set_visible(self, visible: bool) -> None:
        """Show or hide the widget"""
        super().set_visible(visible)
        self._qt_widget.setVisible(visible)
        self.debug_state_change(f"visible_{visible}", {"visible": visible})
    
    def show(self) -> None:
        """Show the widget"""
        super().show()
        self._qt_widget.show()
        self.debug_ui_event("shown", {"widget_id": id(self)})
    
    def set_style(self, style: str) -> None:
        """Set CSS-like style for the widget"""
        self._qt_widget.setStyleSheet(style)
    
    def add_widget(self, widget: UIWidget) -> None:
        """Add a widget to this widget"""
        if hasattr(widget, 'qt_widget'):
            widget.qt_widget.setParent(self._qt_widget)
            # If this widget has a layout, add to the layout
            if hasattr(self, '_layout') and self._layout:
                self._layout.add_widget(widget)
            else:
                # Otherwise, just set as child
                widget.qt_widget.setParent(self._qt_widget)
    
    def cleanup(self) -> None:
        """Clean up the widget and its resources"""
        super().cleanup()
        if hasattr(self, '_qt_widget') and self._qt_widget:
            self._qt_widget.deleteLater()
    
    def set_layout(self, layout: 'UILayout') -> None:
        """Set the layout for the widget"""
        super().set_layout(layout)
        # Apply the layout to the Qt widget
        if hasattr(layout, '_qt_layout'):
            # Set the parent widget on the layout so it can parent child widgets
            layout._parent_widget = self._qt_widget
            # For regular QWidget, set the layout directly
            self._qt_widget.setLayout(layout._qt_layout)
            self.debug_ui_event("layout_applied", {
                "layout_type": layout.__class__.__name__,
                "widget_id": id(self)
            })
    
    @property
    def qt_widget(self) -> QWidget:
        """Get the underlying Qt widget"""
        return self._qt_widget


class QtUILabel(UILabel):
    """Qt implementation of UILabel"""
    
    def __init__(self, text: str = "", parent: Optional[QWidget] = None):
        super().__init__()
        self._qt_widget = QLabel(text, parent)
        self._qt_widget.setObjectName("ui_label")
    
    def set_text(self, text: str) -> None:
        """Set the text content of the label"""
        super().set_text(text)
        if self._qt_widget:
            self._qt_widget.setText(text)
    
    def get_text(self) -> str:
        """Get the text content of the label"""
        if self._qt_widget:
            return self._qt_widget.text()
        return super().get_text()
    
    def set_style(self, style: str) -> None:
        """Set CSS-like style for the label"""
        if self._qt_widget:
            self._qt_widget.setStyleSheet(style)
    
    @property
    def qt_widget(self) -> QLabel:
        """Get the underlying Qt widget"""
        return self._qt_widget


class QtUIButton(UIButton):
    """Qt implementation of UIButton"""
    
    def __init__(self, text: str = "", parent: Optional[QWidget] = None) -> None:
        super().__init__(text)
        self._qt_button = QPushButton(text, parent)
        self._qt_button.clicked.connect(self._on_qt_clicked)
    
    def _on_qt_clicked(self) -> None:
        """Handle Qt button click"""
        if self._clicked_callback:
            self._clicked_callback()
        self.emit_signal("clicked")
    
    @property
    def text(self) -> str:
        return self._qt_button.text()
    
    @text.setter
    def text(self, value: str) -> None:
        self._text = value
        self._qt_button.setText(value)
    
    def set_enabled(self, enabled: bool) -> None:
        """Enable or disable the button"""
        super().set_enabled(enabled)
        self._qt_button.setEnabled(enabled)
    
    def set_visible(self, visible: bool) -> None:
        """Show or hide the button"""
        super().set_visible(visible)
        self._qt_button.setVisible(visible)
    
    def set_style(self, style: str) -> None:
        """Set CSS-like style for the button"""
        self._qt_button.setStyleSheet(style)
    
    @property
    def clicked(self):
        """Get the clicked signal for connecting callbacks"""
        return self._qt_button.clicked
    
    def show(self) -> None:
        """Show the button"""
        super().show()
        self._qt_button.show()
    
    def update_state(self, state_name: str) -> None:
        """Update the button state based on the callback for the given state name"""
        super().update_state(state_name)
        # The parent class handles the actual state change, we just need to apply it to Qt
        if state_name == "enabled":
            self._qt_button.setEnabled(self.enabled)
        elif state_name == "visible":
            self._qt_button.setVisible(self.visible)
    
    @property
    def qt_widget(self) -> QPushButton:
        """Get the underlying Qt button"""
        return self._qt_button


class QtUITextInput(UITextInput):
    """Qt implementation of UITextInput"""
    
    def __init__(self, placeholder: str = "", parent: Optional[QWidget] = None) -> None:
        super().__init__(placeholder)
        self._qt_input = QLineEdit(parent)
        self._qt_input.setPlaceholderText(placeholder)
        self._qt_input.textChanged.connect(self._on_qt_text_changed)
    
    def _on_qt_text_changed(self, text: str) -> None:
        """Handle Qt text change"""
        self._text = text
        self.emit_signal("text_changed", text)
    
    @property
    def text(self) -> str:
        return self._qt_input.text()
    
    @text.setter
    def text(self, value: str) -> None:
        self._text = value
        self._qt_input.setText(value)
    
    def set_text(self, text: str) -> None:
        """Set text and emit signal"""
        self._qt_input.setText(text)
    
    def get_text(self) -> str:
        """Get the current text"""
        return self._qt_input.text()
    
    def set_style(self, style: str) -> None:
        """Set CSS-like style for the text input"""
        self._qt_input.setStyleSheet(style)
    
    @property
    def text_changed(self):
        """Get the text_changed signal for connecting callbacks"""
        return self._qt_input.textChanged
    
    def set_placeholder(self, placeholder: str) -> None:
        """Set the placeholder text"""
        self._qt_input.setPlaceholderText(placeholder)
    
    def set_enabled(self, enabled: bool) -> None:
        """Enable or disable the input"""
        super().set_enabled(enabled)
        self._qt_input.setEnabled(enabled)
    
    def set_visible(self, visible: bool) -> None:
        """Show or hide the input"""
        super().set_visible(visible)
        self._qt_input.setVisible(visible)
    
    def show(self) -> None:
        """Show the input"""
        super().show()
        self._qt_input.show()
    
    @property
    def qt_widget(self) -> QLineEdit:
        """Get the underlying Qt input"""
        return self._qt_input


class QtUIComboBox(UIComboBox):
    """Qt implementation of UIComboBox"""
    
    def __init__(self, parent: Optional[QWidget] = None) -> None:
        super().__init__()
        self._qt_combo = QComboBox(parent)
        self._qt_combo.currentIndexChanged.connect(self._on_qt_current_changed)
    
    def _on_qt_current_changed(self, index: int) -> None:
        """Handle Qt selection change"""
        self._current_index = index
        self.emit_signal("current_changed", self.current_data())
    
    def add_item(self, text_or_item, data: Any = None) -> None:
        """Add an item to the combo box. Can accept either text+data or a UIListItem."""
        super().add_item(text_or_item, data)
        if isinstance(text_or_item, str):
            # Old calling pattern: add_item(text, data)
            self._qt_combo.addItem(text_or_item)
        else:
            # New calling pattern: add_item(UIListItem)
            item = text_or_item
            self._qt_combo.addItem(item.get_text())
    
    def clear(self) -> None:
        """Clear all items"""
        super().clear()
        self._qt_combo.clear()
    
    def set_current_index(self, index: int) -> None:
        """Set the current selection"""
        super().set_current_index(index)
        self._qt_combo.setCurrentIndex(index)
    
    def set_enabled(self, enabled: bool) -> None:
        """Enable or disable the combo box"""
        super().set_enabled(enabled)
        self._qt_combo.setEnabled(enabled)
    
    def set_visible(self, visible: bool) -> None:
        """Show or hide the combo box"""
        super().set_visible(visible)
        self._qt_combo.setVisible(visible)
    
    def show(self) -> None:
        """Show the combo box"""
        super().show()
        self._qt_combo.show()
    
    @property
    def qt_widget(self) -> QComboBox:
        """Get the underlying Qt combo box"""
        return self._qt_combo


class QtUIListWidget(UIListWidget):
    """Qt implementation of UIListWidget"""
    
    def __init__(self, parent: Optional[QWidget] = None) -> None:
        super().__init__()
        self._qt_list = QListWidget(parent)
        self._qt_list.currentRowChanged.connect(self._on_qt_current_changed)
    
    def _on_qt_current_changed(self, row: int) -> None:
        """Handle Qt selection change"""
        self._current_index = row
        self.emit_signal("current_changed", self.current_data())
    
    def add_item(self, text: str, data: Any = None) -> None:
        """Add an item to the list"""
        super().add_item(text, data)
        item = QListWidgetItem(text)
        item.setData(Qt.UserRole, data)
        self._qt_list.addItem(item)
    
    def clear(self) -> None:
        """Clear all items"""
        super().clear()
        self._qt_list.clear()
    
    def set_current_index(self, index: int) -> None:
        """Set the current selection"""
        super().set_current_index(index)
        self._qt_list.setCurrentRow(index)
    
    def set_enabled(self, enabled: bool) -> None:
        """Enable or disable the list"""
        super().set_enabled(enabled)
        self._qt_list.setEnabled(enabled)
    
    def set_visible(self, visible: bool) -> None:
        """Show or hide the list"""
        super().set_visible(visible)
        self._qt_list.setVisible(visible)
    
    def show(self) -> None:
        """Show the list"""
        super().show()
        self._qt_list.show()
    
    def create_item(self, text: str) -> 'QtUIListItem':
        """Create a new list item"""
        return QtUIListItem(text)
    
    def add_item(self, item: 'UIListItem') -> None:
        """Add an item to the list"""
        data = item.get_data()
        # If data is a tuple, use the first element for backward compatibility
        if isinstance(data, tuple) and len(data) > 0:
            data_for_storage = data[0]
        else:
            data_for_storage = data
        
        super().add_item(item)
        qt_item = QListWidgetItem(item.get_text())
        qt_item.setData(Qt.UserRole, data_for_storage)
        self._qt_list.addItem(qt_item)
    
    def remove_item(self, item: 'UIListItem') -> None:
        """Remove an item from the list"""
        # Find and remove the Qt item
        for i in range(self._qt_list.count()):
            qt_item = self._qt_list.item(i)
            if qt_item and qt_item.text() == item.get_text() and qt_item.data(Qt.UserRole) == item.get_data():
                self._qt_list.takeItem(i)
                break
        super().remove_item(item)
    
    def get_item_count(self) -> int:
        """Get the number of items in the list"""
        return self._qt_list.count()
    
    def get_item(self, index: int) -> Optional['QtUIListItem']:
        """Get an item by index"""
        if 0 <= index < self._qt_list.count():
            qt_item = self._qt_list.item(index)
            if qt_item:
                item = QtUIListItem(qt_item.text())
                data = qt_item.data(Qt.UserRole)
                print(f"DEBUG: qt_item.data(Qt.UserRole) returned: {data} (type: {type(data)})")
                item.set_data(data)
                return item
        return None
    
    def get_selected_item(self) -> Optional['QtUIListItem']:
        """Get the currently selected item"""
        current_row = self._qt_list.currentRow()
        if current_row >= 0:
            qt_item = self._qt_list.item(current_row)
            if qt_item:
                item = QtUIListItem(qt_item.text())
                data = qt_item.data(Qt.UserRole)
                print(f"DEBUG: qt_item.data(Qt.UserRole) returned: {data} (type: {type(data)})")
                item.set_data(data)
                return item
        return None
    
    def set_style(self, style: str) -> None:
        """Set CSS-like style for the list widget"""
        self._qt_list.setStyleSheet(style)
    
    @property
    def item_selected(self):
        """Get the item_selected signal for connecting callbacks"""
        return self._qt_list.currentRowChanged
    
    @property
    def qt_widget(self) -> QListWidget:
        """Get the underlying Qt list widget"""
        return self._qt_list


class QtUIListItem(UIListItem):
    """Qt implementation of UIListItem"""
    
    def __init__(self, text: str) -> None:
        super().__init__(text)


class QtUICanvas(UICanvas):
    """Qt implementation of UICanvas"""
    
    def __init__(self) -> None:
        super().__init__()
        self._qt_view = QGraphicsView()
        self._qt_scene = QGraphicsScene()
        self._qt_view.setScene(self._qt_scene)
        self._qt_view.setDragMode(QGraphicsView.RubberBandDrag)
        self._qt_view.setRenderHint(QPainter.Antialiasing)
        
        # Connect selection changes
        self._qt_scene.selectionChanged.connect(self._on_qt_selection_changed)
    
    def _on_qt_selection_changed(self) -> None:
        """Handle Qt selection changes"""
        items = self._qt_scene.selectedItems()
        if items:
            # Get the bounding rect of selected items
            rect = items[0].boundingRect()
            self._selection_rect = rect
        else:
            self._selection_rect = None
        
        self.emit_signal("selection_changed", self._selection_rect)
    
    def set_pixmap(self, pixmap: Any) -> None:
        """Set the image to display"""
        super().set_pixmap(pixmap)
        if isinstance(pixmap, QPixmap):
            self._qt_scene.clear()
            self._qt_scene.addPixmap(pixmap)
            self._qt_view.fitInView(self._qt_scene.itemsBoundingRect(), Qt.KeepAspectRatio)
        self.emit_signal("pixmap_changed")
    
    def set_zoom(self, zoom_factor: float) -> None:
        """Set the zoom factor"""
        super().set_zoom(zoom_factor)
        self._qt_view.resetTransform()
        self._qt_view.scale(zoom_factor, zoom_factor)
        self.emit_signal("zoom_changed")
    
    def set_selection_rect(self, rect: Any) -> None:
        """Set the selection rectangle"""
        super().set_selection_rect(rect)
        if isinstance(rect, QRect):
            # Select items in the rect
            self._qt_scene.clearSelection()
            for item in self._qt_scene.items(rect):
                item.setSelected(True)
    
    def clear_selection(self) -> None:
        """Clear the current selection"""
        super().clear_selection()
        self._qt_scene.clearSelection()
    
    def set_enabled(self, enabled: bool) -> None:
        """Enable or disable the canvas"""
        super().set_enabled(enabled)
        self._qt_view.setEnabled(enabled)
    
    def set_visible(self, visible: bool) -> None:
        """Show or hide the canvas"""
        super().set_visible(visible)
        self._qt_view.setVisible(visible)
    
    def show(self) -> None:
        """Show the canvas"""
        super().show()
        self._qt_view.show()
    
    @property
    def qt_widget(self) -> QGraphicsView:
        """Get the underlying Qt graphics view"""
        return self._qt_view


class QtUIMessageBox(UIMessageBox):
    """Qt implementation of UIMessageBox"""
    
    def show_info(self, title: str, message: str) -> None:
        """Show an info message - log to console instead of modal dialog"""
        print(f"[QT INFO] {title}: {message}")
    
    def show_warning(self, title: str, message: str) -> None:
        """Show a warning message - log to console instead of modal dialog"""
        print(f"[QT WARNING] {title}: {message}")
    
    def show_error(self, title: str, message: str) -> None:
        """Show an error message - log to console instead of modal dialog"""
        print(f"[QT ERROR] {title}: {message}")
    
    def show_question(self, title: str, message: str) -> bool:
        """Show a question dialog and return True if Yes was clicked - log instead of modal"""
        print(f"[QT QUESTION] {title}: {message}")
        # For now, always return True to avoid blocking
        # In a real implementation, this would show a non-modal dialog or use a different UI pattern
        return True


class QtUIFileDialog(UIFileDialog):
    """Qt implementation of UIFileDialog"""
    
    def get_open_file_name(self, title: str, filter: str = "", directory: str = "") -> Optional[str]:
        """Get a file name for opening"""
        file_path, _ = QFileDialog.getOpenFileName(None, title, directory, filter)
        return file_path if file_path else None
    
    def get_save_file_name(self, title: str, filter: str = "") -> Optional[str]:
        """Get a file name for saving"""
        file_path, _ = QFileDialog.getSaveFileName(None, title, "", filter)
        return file_path if file_path else None
    
    def get_existing_directory(self, title: str, directory: str = "") -> Optional[str]:
        """Get an existing directory path"""
        directory_path = QFileDialog.getExistingDirectory(None, title, directory)
        return directory_path if directory_path else None


class QtUIProgressBar(UIProgressBar):
    """Qt implementation of UIProgressBar"""
    
    def __init__(self, parent: Optional[QWidget] = None) -> None:
        super().__init__()
        self._qt_progress = QProgressBar(parent)
        self._qt_progress.setMinimum(self._minimum)
        self._qt_progress.setMaximum(self._maximum)
        self._qt_progress.setValue(self._value)
    
    @property
    def value(self) -> int:
        return self._qt_progress.value()
    
    @value.setter
    def value(self, value: int) -> None:
        # Clamp value to valid range
        value = max(self.minimum, min(value, self.maximum))
        self._qt_progress.setValue(value)
    
    @property
    def minimum(self) -> int:
        return self._qt_progress.minimum()
    
    @minimum.setter
    def minimum(self, value: int) -> None:
        super().minimum = value
        self._qt_progress.setMinimum(value)
    
    @property
    def maximum(self) -> int:
        return self._qt_progress.maximum()
    
    @maximum.setter
    def maximum(self, value: int) -> None:
        super().maximum = value
        self._qt_progress.setMaximum(value)
    
    def set_enabled(self, enabled: bool) -> None:
        """Enable or disable the progress bar"""
        super().set_enabled(enabled)
        self._qt_progress.setEnabled(enabled)
    
    def set_visible(self, visible: bool) -> None:
        """Show or hide the progress bar"""
        super().set_visible(visible)
        self._qt_progress.setVisible(visible)
    
    def show(self) -> None:
        """Show the progress bar"""
        super().show()
        self._qt_progress.show()
    
    @property
    def qt_widget(self) -> QProgressBar:
        """Get the underlying Qt progress bar"""
        return self._qt_progress


class QtUIGroupBox(UIGroupBox):
    """Qt implementation of UIGroupBox"""
    
    def __init__(self, title: str = "") -> None:
        super().__init__(title)
        self._title = title
        self._qt_group = QGroupBox(title)
    
    @property
    def title(self) -> str:
        return self._qt_group.title()
    
    @title.setter
    def title(self, value: str) -> None:
        self._title = value
        self._qt_group.setTitle(value)
    
    def set_enabled(self, enabled: bool) -> None:
        """Enable or disable the group box"""
        super().set_enabled(enabled)
        self._qt_group.setEnabled(enabled)
    
    def set_visible(self, visible: bool) -> None:
        """Show or hide the group box"""
        super().set_visible(visible)
        self._qt_group.setVisible(visible)
    
    def show(self) -> None:
        """Show the group box"""
        super().show()
        self._qt_group.show()
    
    def set_title(self, title: str) -> None:
        """Set the title of the group box"""
        self.title = title
    
    @property
    def qt_widget(self) -> QGroupBox:
        """Get the underlying Qt group box"""
        return self._qt_group


class QtUITabWidget(UITabWidget):
    """Qt implementation of UITabWidget"""
    
    def __init__(self, parent: Optional[QWidget] = None) -> None:
        super().__init__()
        self._qt_tabs = QTabWidget(parent)
        self._qt_tabs.currentChanged.connect(self._on_qt_current_changed)
    
    def _on_qt_current_changed(self, index: int) -> None:
        """Handle Qt tab change"""
        self._current_index = index
        self.emit_signal("current_changed", index)
    
    def add_tab(self, widget: UIWidget, title: str) -> None:
        """Add a tab"""
        super().add_tab(widget, title)
        if isinstance(widget, QtUIWidget):
            self._qt_tabs.addTab(widget.qt_widget, title)
    
    def set_current_index(self, index: int) -> None:
        """Set the current tab"""
        super().set_current_index(index)
        self._qt_tabs.setCurrentIndex(index)
    
    def set_enabled(self, enabled: bool) -> None:
        """Enable or disable the tab widget"""
        super().set_enabled(enabled)
        self._qt_tabs.setEnabled(enabled)
    
    def set_visible(self, visible: bool) -> None:
        """Show or hide the tab widget"""
        super().set_visible(visible)
        self._qt_tabs.setVisible(visible)
    
    def show(self) -> None:
        """Show the tab widget"""
        super().show()
        self._qt_tabs.show()
    
    @property
    def qt_widget(self) -> QTabWidget:
        """Get the underlying Qt tab widget"""
        return self._qt_tabs


class QtUISplitter(UISplitter):
    """Qt implementation of UISplitter"""
    
    def __init__(self, orientation: str = "horizontal") -> None:
        super().__init__(orientation)
        qt_orientation = Qt.Horizontal if orientation == "horizontal" else Qt.Vertical
        self._qt_splitter = QSplitter(qt_orientation)
    
    def add_widget(self, widget: UIWidget) -> None:
        """Add a widget to the splitter"""
        super().add_widget(widget)
        if isinstance(widget, QtUIWidget):
            self._qt_splitter.addWidget(widget.qt_widget)
    
    def set_sizes(self, sizes: List[int]) -> None:
        """Set the sizes of the widgets"""
        super().set_sizes(sizes)
        self._qt_splitter.setSizes(sizes)
    
    def set_enabled(self, enabled: bool) -> None:
        """Enable or disable the splitter"""
        super().set_enabled(enabled)
        self._qt_splitter.setEnabled(enabled)
    
    def set_visible(self, visible: bool) -> None:
        """Show or hide the splitter"""
        super().set_visible(visible)
        self._qt_splitter.setVisible(visible)
    
    @property
    def qt_widget(self) -> QSplitter:
        """Get the underlying Qt splitter"""
        return self._qt_splitter


class QtUILayout(UILayout):
    """Qt implementation of UILayout"""
    
    def __init__(self, orientation: str = "vertical", parent: Optional[QWidget] = None) -> None:
        self._orientation = orientation
        self._parent_widget = parent
        if orientation == "vertical":
            self._qt_layout = QVBoxLayout()
        elif orientation == "horizontal":
            self._qt_layout = QHBoxLayout()
        elif orientation == "form":
            self._qt_layout = QFormLayout()
        else:
            self._qt_layout = QVBoxLayout()
    
    def add_widget(self, widget: UIWidget, *args, **kwargs) -> None:
        """Add a widget to the layout"""
        # Check if widget has a qt_widget property (all Qt implementations should have this)
        if hasattr(widget, 'qt_widget'):
            # Ensure the widget is properly parented
            if hasattr(self, '_parent_widget') and self._parent_widget:
                widget.qt_widget.setParent(self._parent_widget)
            self._qt_layout.addWidget(widget.qt_widget, *args, **kwargs)
        elif hasattr(widget, '_qt_tabs'):  # Special case for QtUITabWidget
            # Ensure the widget is properly parented
            if hasattr(self, '_parent_widget') and self._parent_widget:
                widget._qt_tabs.setParent(self._parent_widget)
            self._qt_layout.addWidget(widget._qt_tabs, *args, **kwargs)
        else:
            print(f"Warning: Cannot add widget {widget} to layout - no Qt widget found")
    
    def remove_widget(self, widget: UIWidget) -> None:
        """Remove a widget from the layout"""
        if hasattr(widget, 'qt_widget'):
            self._qt_layout.removeWidget(widget.qt_widget)
        elif hasattr(widget, '_qt_tabs'):  # Special case for QtUITabWidget
            self._qt_layout.removeWidget(widget._qt_tabs)
    
    def insert_widget(self, index: int, widget: UIWidget, *args, **kwargs) -> None:
        """Insert a widget at a specific index in the layout"""
        # Check if widget has a qt_widget property (all Qt implementations should have this)
        if hasattr(widget, 'qt_widget'):
            # Ensure the widget is properly parented
            if hasattr(self, '_parent_widget') and self._parent_widget:
                widget.qt_widget.setParent(self._parent_widget)
            self._qt_layout.insertWidget(index, widget.qt_widget, *args, **kwargs)
        elif hasattr(widget, '_qt_tabs'):  # Special case for QtUITabWidget
            # Ensure the widget is properly parented
            if hasattr(self, '_parent_widget') and self._parent_widget:
                widget._qt_tabs.setParent(self._parent_widget)
            self._qt_layout.insertWidget(index, widget._qt_tabs, *args, **kwargs)
        else:
            print(f"Warning: Cannot insert widget {widget} to layout - no Qt widget found")
    
    def set_style(self, style: str) -> None:
        """Set CSS-like style for the layout"""
        # Layouts don't have styles in Qt, but we can apply to the parent widget
        if hasattr(self, '_parent_widget') and self._parent_widget:
            self._parent_widget.setStyleSheet(style)
    
    @property
    def qt_layout(self) -> None:
        """Get the underlying Qt layout"""
        return self._qt_layout


class QtUIMenuBar(UIMenuBar, UIDebugMixin):
    """Qt implementation of UIMenuBar"""
    
    def __init__(self, parent: Optional[QWidget] = None) -> None:
        super().__init__()
        UIDebugMixin.__init__(self)
        self._qt_menu_bar = QMenuBar(parent)
        
        # Set up debugging
        self.set_debugger(get_global_debugger())
        self.debug_log("widget_created", "QtUIMenuBar created", {
            "widget_id": id(self)
        })
    
    @property
    def qt_widget(self) -> QMenuBar:
        """Get the underlying Qt menu bar"""
        return self._qt_menu_bar
    
    def add_menu(self, menu: 'UIMenu') -> None:
        """Add a menu to the menu bar"""
        super().add_menu(menu)
        if isinstance(menu, QtUIMenu):
            self._qt_menu_bar.addMenu(menu.qt_widget)
    
    def show(self) -> None:
        """Show the menu bar"""
        super().show()
        self._qt_menu_bar.show()


class QtUIMenu(UIMenu, UIDebugMixin):
    """Qt implementation of UIMenu"""
    
    def __init__(self, title: str, parent: Optional[QMenuBar] = None) -> None:
        super().__init__(title)
        UIDebugMixin.__init__(self)
        self._qt_menu = QMenu(title, parent)
        
        # Set up debugging
        self.set_debugger(get_global_debugger())
        self.debug_log("widget_created", "QtUIMenu created", {
            "title": title,
            "widget_id": id(self)
        })
    
    @property
    def qt_widget(self) -> QMenu:
        """Get the underlying Qt menu"""
        return self._qt_menu
    
    def add_item(self, item: 'UIMenuItem') -> None:
        """Add a menu item to the menu"""
        super().add_item(item)
        if isinstance(item, QtUIMenuItem):
            self._qt_menu.addAction(item.qt_action)
    
    def add_separator(self) -> None:
        """Add a separator to the menu"""
        super().add_separator()
        self._qt_menu.addSeparator()
    
    def show(self) -> None:
        """Show the menu"""
        super().show()
        self._qt_menu.show()


class QtUIMenuItem(UIMenuItem, UIDebugMixin):
    """Qt implementation of UIMenuItem"""
    
    def __init__(self, text: str, parent: Optional[QMenu] = None) -> None:
        super().__init__(text)
        UIDebugMixin.__init__(self)
        self._qt_action = QAction(text, parent)
        self._qt_action.triggered.connect(self._on_qt_clicked)
        
        # Set up debugging
        self.set_debugger(get_global_debugger())
        self.debug_log("widget_created", "QtUIMenuItem created", {
            "text": text,
            "widget_id": id(self)
        })
    
    @property
    def qt_action(self) -> QAction:
        """Get the underlying Qt action"""
        return self._qt_action
    
    def _on_qt_clicked(self) -> None:
        """Handle Qt menu item click"""
        self._on_clicked()
    
    def set_text(self, text: str) -> None:
        """Set the text of the menu item"""
        self.text = text
        self._qt_action.setText(text)
    
    @property
    def clicked(self):
        """Get the clicked signal for connecting callbacks"""
        return self._qt_action.triggered
    
    def show(self) -> None:
        """Show the menu item"""
        super().show()
        self._qt_action.setVisible(True)
    
    def set_enabled(self, enabled: bool) -> None:
        """Enable or disable the menu item"""
        super().set_enabled(enabled)
        self._qt_action.setEnabled(enabled)
    
    def set_visible(self, visible: bool) -> None:
        """Show or hide the menu item"""
        super().set_visible(visible)
        self._qt_action.setVisible(visible)
    
    def update_state(self, state_name: str) -> None:
        """Update the menu item state based on the callback for the given state name"""
        super().update_state(state_name)
        # The parent class handles the actual state change, we just need to apply it to Qt
        if state_name == "enabled":
            self._qt_action.setEnabled(self.enabled)
        elif state_name == "visible":
            self._qt_action.setVisible(self.visible)


class QtUIStatusBar(UIStatusBar, UIDebugMixin):
    """Qt implementation of UIStatusBar"""
    
    def __init__(self, parent: Optional[QWidget] = None) -> None:
        super().__init__()
        UIDebugMixin.__init__(self)
        self._qt_status_bar = QStatusBar(parent)
        
        # Set up debugging
        self.set_debugger(get_global_debugger())
        self.debug_log("widget_created", "QtUIStatusBar created", {
            "widget_id": id(self)
        })
    
    @property
    def qt_widget(self) -> QStatusBar:
        """Get the underlying Qt status bar"""
        return self._qt_status_bar
    
    def set_message(self, message: str) -> None:
        """Set the status bar message"""
        super().set_message(message)
        self._qt_status_bar.showMessage(message)
    
    def add_widget(self, widget: 'UIWidget') -> None:
        """Add a widget to the status bar"""
        super().add_widget(widget)
        if hasattr(widget, 'qt_widget'):
            self._qt_status_bar.addWidget(widget.qt_widget)
    
    def show(self) -> None:
        """Show the status bar"""
        super().show()
        self._qt_status_bar.show()
