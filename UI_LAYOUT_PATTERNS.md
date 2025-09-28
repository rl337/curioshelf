# UI Layout Patterns Guide

This document establishes clear patterns for UI layout management in CurioShelf to ensure consistency and avoid layout issues.

## ✅ **RECOMMENDED PATTERNS**

### 1. **Use Specialized Layout Widgets (Preferred)**

For most UI components, use the specialized layout widgets that handle their own internal layout management:

```python
# ✅ GOOD: Use specialized layout widgets
def _setup_ui(self) -> None:
    # Create main container
    self.widget = self.ui.create_widget("my_view")
    
    # Use DirectionalLayout for main structure
    from curioshelf.ui.layouts.directional_layout import DirectionalLayout, Direction
    main_layout = DirectionalLayout(self.widget)
    self.widget.set_layout(main_layout)
    
    # Title at top
    title_label = self.ui.create_label("My View")
    title_label.set_style("font-size: 18px; font-weight: bold; margin: 20px;")
    main_layout.add_widget(title_label, Direction.NORTH)
    
    # Main content using StackWidget
    content_stack = self.ui.create_stack_widget(spacing=15)
    main_layout.add_widget(content_stack.widget, Direction.CENTER, expand=True)
    
    # Add content to stack
    content_stack.add_label("Section 1:", style="font-weight: bold;")
    content_stack.add_text_input("Enter text...", style="padding: 8px;")
    
    # Button row using RowWidget
    button_row = self.ui.create_row_widget(spacing=10)
    content_stack.add_widget(button_row.widget)
    
    button_row.add_button("Action 1", self._on_action1, "padding: 8px 16px;")
    button_row.add_button("Action 2", self._on_action2, "padding: 8px 16px;")
    
    # Bottom buttons using ButtonRowWidget
    bottom_buttons = self.ui.create_button_row_widget(spacing=10)
    main_layout.add_widget(bottom_buttons.widget, Direction.SOUTH)
    
    bottom_buttons.add_secondary_button("Cancel", self._on_cancel)
    bottom_buttons.add_primary_button("OK", self._on_ok)
```

### 2. **Available Specialized Layout Widgets**

- **`DirectionalLayout`**: Main layout with NORTH, CENTER, SOUTH sections
- **`StackWidget`**: Vertical stacking of widgets with spacing
- **`RowWidget`**: Horizontal arrangement of widgets
- **`ButtonRowWidget`**: Specialized row for buttons with consistent styling
- **`FormWidget`**: Form with labeled input fields

### 3. **Layout Widget Convenience Methods**

Each layout widget provides convenience methods:

```python
# StackWidget methods
stack.add_label("Text", style="font-weight: bold;")
stack.add_text_input("Placeholder", style="padding: 8px;")
stack.add_button("Click me", callback, "padding: 8px;")
stack.add_widget(some_widget)

# RowWidget methods  
row.add_label("Label", style="padding: 5px;")
row.add_text_input("Input", expand=True, style="padding: 8px;")
row.add_button("Button", callback, "padding: 8px;")
row.add_widget(some_widget, expand=True)

# ButtonRowWidget methods
button_row.add_button("Regular", callback)
button_row.add_primary_button("Primary", callback)  # Highlighted
button_row.add_secondary_button("Secondary", callback)  # Muted
```

## ❌ **AVOID THESE PATTERNS**

### 1. **Don't Use Basic Layouts Directly**

```python
# ❌ BAD: Using basic layouts directly
def _setup_ui(self) -> None:
    self.widget = self.ui.create_widget("my_view")
    
    # This causes layout issues
    main_layout = self.ui.create_layout("vertical")
    self.widget.set_layout(main_layout)
    
    # This doesn't work well with Qt
    main_layout.add_widget(some_widget, expand=True)
```

### 2. **Don't Use CSS-Style Properties in Qt**

```python
# ❌ BAD: CSS properties not supported in Qt
widget.set_style("display: flex; gap: 10px; justify-content: space-between;")

# ✅ GOOD: Use Qt-compatible properties
widget.set_style("padding: 10px; margin: 5px;")
```

## 🔧 **MIGRATION GUIDE**

### Converting from Basic Layouts to Specialized Widgets

**Before (Basic Layout):**
```python
def _setup_ui(self) -> None:
    self.widget = self.ui.create_widget("my_view")
    main_layout = self.ui.create_layout("vertical")
    self.widget.set_layout(main_layout)
    
    # Title
    title = self.ui.create_label("Title")
    main_layout.add_widget(title)
    
    # Content
    content_layout = self.ui.create_layout("horizontal")
    main_layout.add_widget(content_layout)
    
    # Buttons
    btn_layout = self.ui.create_layout("horizontal")
    main_layout.add_widget(btn_layout)
```

**After (Specialized Widgets):**
```python
def _setup_ui(self) -> None:
    self.widget = self.ui.create_widget("my_view")
    
    # Use DirectionalLayout for main structure
    from curioshelf.ui.layouts.directional_layout import DirectionalLayout, Direction
    main_layout = DirectionalLayout(self.widget)
    self.widget.set_layout(main_layout)
    
    # Title at top
    title = self.ui.create_label("Title")
    title.set_style("font-size: 18px; font-weight: bold; margin: 20px;")
    main_layout.add_widget(title, Direction.NORTH)
    
    # Content using StackWidget
    content_stack = self.ui.create_stack_widget(spacing=15)
    main_layout.add_widget(content_stack.widget, Direction.CENTER, expand=True)
    
    # Buttons using ButtonRowWidget
    button_row = self.ui.create_button_row_widget(spacing=10)
    main_layout.add_widget(button_row.widget, Direction.SOUTH)
```

## 📋 **CHECKLIST FOR NEW UI COMPONENTS**

- [ ] Use `DirectionalLayout` for main structure
- [ ] Use `StackWidget` for vertical content
- [ ] Use `RowWidget` for horizontal arrangements
- [ ] Use `ButtonRowWidget` for button groups
- [ ] Avoid direct `create_layout()` calls
- [ ] Use convenience methods (`add_label`, `add_button`, etc.)
- [ ] Set styles with Qt-compatible properties only
- [ ] Test with both Qt and Script UI backends

## 🧪 **TESTING PATTERNS**

### Test Layout Components

```python
def test_ui_layout():
    """Test UI component layout"""
    factory = create_ui_factory("script", verbose=True)
    ui_impl = factory.get_ui_implementation()
    ui_impl.initialize()
    
    # Create component
    view = MyView(ui_impl)
    
    # Verify all components exist
    assert view.widget is not None
    assert hasattr(view, 'title_label')
    assert hasattr(view, 'input_field')
    assert hasattr(view, 'action_button')
    
    # Test functionality
    view.input_field.set_text("test")
    assert view.input_field.get_text() == "test"
    
    print("✓ Layout test passed")
```

## 📁 **FILES TO UPDATE**

The following files need to be updated to follow the new patterns:

- [ ] `curioshelf/ui/views/sources_list_view.py` - Convert to specialized widgets
- [ ] `curioshelf/ui/objects_tab_abstracted.py` - Convert to specialized widgets  
- [ ] `curioshelf/ui/sources_tab_abstracted.py` - Convert to specialized widgets
- [ ] `curioshelf/ui/templates_tab_abstracted.py` - Convert to specialized widgets
- [ ] Any other UI components using basic layouts

## 🎯 **BENEFITS**

1. **Consistent Layout**: All components follow the same patterns
2. **Qt Compatibility**: Avoids layout issues with Qt backend
3. **Maintainable**: Clear, readable layout code
4. **Testable**: Easy to test with script UI backend
5. **Extensible**: Easy to add new components following established patterns
