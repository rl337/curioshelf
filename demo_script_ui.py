#!/usr/bin/env python3
"""
Script UI Widget Demonstration

This script demonstrates the script UI widget capabilities, showing how
widgets can be created, manipulated, and queried programmatically for
headless systems without Qt dependencies.
"""

import sys
from pathlib import Path

# Add the curioshelf package to the path
sys.path.insert(0, str(Path(__file__).parent))

from curioshelf.ui.ui_factory import UIFactory
from curioshelf.ui.script.widgets import SizePolicy


def demonstrate_widget_creation():
    """Demonstrate creating various widgets"""
    print("=== Script UI Widget Creation Demo ===")
    
    # Create UI factory for script UI
    factory = UIFactory("script", verbose=True)
    ui_impl = factory.get_ui_implementation()
    ui_impl.initialize()
    
    print("\n1. Creating basic widgets...")
    
    # Create a button
    button = ui_impl.create_button("Click Me!")
    print(f"   Button created: {button.get_text()}")
    
    # Create a text input
    text_input = ui_impl.create_text_input("Enter text here...")
    print(f"   Text input created with placeholder: {text_input.placeholder}")
    
    # Create a combo box and add items
    combo_box = ui_impl.create_combo_box()
    combo_box.add_item("Option 1")
    combo_box.add_item("Option 2")
    combo_box.add_item("Option 3")
    print(f"   Combo box created with {combo_box.get_item_count()} items")
    
    # Create a list widget
    list_widget = ui_impl.create_list_widget()
    print(f"   List widget created")
    
    # Create a canvas
    canvas = ui_impl.create_canvas()
    print(f"   Canvas created")
    
    # Create a progress bar
    progress_bar = ui_impl.create_progress_bar()
    progress_bar.set_value(50)
    print(f"   Progress bar created with value: {progress_bar.get_value()}")
    
    # Create a group box
    group_box = ui_impl.create_group_box("Settings")
    print(f"   Group box created: {group_box.get_title()}")
    
    # Create a tab widget
    tab_widget = ui_impl.create_tab_widget()
    print(f"   Tab widget created")
    
    return ui_impl, button, text_input, combo_box, list_widget, canvas, progress_bar, group_box, tab_widget


def demonstrate_layout_and_sizing():
    """Demonstrate layout and sizing capabilities"""
    print("\n=== Layout and Sizing Demo ===")
    
    factory = UIFactory("script", verbose=False)
    ui_impl = factory.get_ui_implementation()
    ui_impl.initialize()
    
    # Create a vertical layout
    layout = ui_impl.create_layout("vertical")
    print(f"   Vertical layout created")
    
    # Create some widgets
    button1 = ui_impl.create_button("Button 1")
    button2 = ui_impl.create_button("Button 2")
    text_input = ui_impl.create_text_input("Input field")
    
    # Set different size policies
    button1.set_size_policy(SizePolicy.PREFERRED, SizePolicy.FIXED)
    button2.set_size_policy(SizePolicy.EXPANDING, SizePolicy.FIXED)
    text_input.set_size_policy(SizePolicy.EXPANDING, SizePolicy.FIXED)
    
    print(f"   Button 1 size policy: {button1.get_size_policy()}")
    print(f"   Button 2 size policy: {button2.get_size_policy()}")
    print(f"   Text input size policy: {text_input.get_size_policy()}")
    
    # Add widgets to layout
    layout.add_widget(button1)
    layout.add_widget(button2)
    layout.add_widget(text_input)
    
    print(f"   Layout now contains {len(layout.get_widgets())} widgets")
    
    # Set layout geometry and update
    layout.set_geometry(0, 0, 300, 200)
    layout.update_layout()
    
    print(f"   Layout size hint: {layout.size_hint().width}x{layout.size_hint().height}")
    
    # Show widget positions after layout
    for i, widget in enumerate(layout.get_widgets()):
        if hasattr(widget, 'get_geometry'):
            geom = widget.get_geometry()
            print(f"   Widget {i+1} position: ({geom.x}, {geom.y}) size: {geom.width}x{geom.height}")
    
    return layout


def demonstrate_widget_manipulation():
    """Demonstrate widget manipulation and querying"""
    print("\n=== Widget Manipulation Demo ===")
    
    factory = UIFactory("script", verbose=False)
    ui_impl = factory.get_ui_implementation()
    ui_impl.initialize()
    
    # Create a button and manipulate it
    button = ui_impl.create_button("Original Text")
    print(f"   Button text: {button.get_text()}")
    
    # Change button text
    button.set_text("Updated Text")
    print(f"   Button text after update: {button.get_text()}")
    
    # Test button click
    print("   Simulating button click...")
    button.click()
    
    # Create text input and manipulate it
    text_input = ui_impl.create_text_input("Initial placeholder")
    print(f"   Text input placeholder: {text_input.placeholder}")
    
    # Change text
    text_input.set_text("User entered text")
    print(f"   Text input value: {text_input.get_text()}")
    
    # Create combo box and manipulate it
    combo_box = ui_impl.create_combo_box()
    combo_box.add_item("First Item")
    combo_box.add_item("Second Item")
    combo_box.add_item("Third Item")
    
    print(f"   Combo box has {combo_box.get_item_count()} items")
    
    # Select an item
    combo_box.set_current_index(1)
    print(f"   Combo box selection: {combo_box.get_current_text()}")
    
    # Create progress bar and manipulate it
    progress_bar = ui_impl.create_progress_bar()
    progress_bar.set_range(0, 100)
    
    for value in [25, 50, 75, 100]:
        progress_bar.set_value(value)
        print(f"   Progress bar value: {progress_bar.get_value()}% ({progress_bar.get_percentage():.1f}%)")
    
    return button, text_input, combo_box, progress_bar


def demonstrate_widget_tree():
    """Demonstrate widget hierarchy and tree structure"""
    print("\n=== Widget Tree Demo ===")
    
    factory = UIFactory("script", verbose=False)
    ui_impl = factory.get_ui_implementation()
    ui_impl.initialize()
    
    # Create a complex widget hierarchy
    main_layout = ui_impl.create_layout("vertical")
    
    # Create a group box with its own layout
    group_box = ui_impl.create_group_box("Main Controls")
    group_layout = ui_impl.create_layout("horizontal")
    
    button1 = ui_impl.create_button("Button 1")
    button2 = ui_impl.create_button("Button 2")
    text_input = ui_impl.create_text_input("Input")
    
    group_layout.add_widget(button1)
    group_layout.add_widget(button2)
    group_layout.add_widget(text_input)
    
    # Add group layout to group box (simulated)
    group_box.add_child(group_layout)
    
    # Add group box to main layout
    main_layout.add_widget(group_box)
    
    # Add more widgets to main layout
    progress_bar = ui_impl.create_progress_bar()
    canvas = ui_impl.create_canvas()
    
    main_layout.add_widget(progress_bar)
    main_layout.add_widget(canvas)
    
    # Set geometry and update layout
    main_layout.set_geometry(0, 0, 400, 300)
    main_layout.update_layout()
    
    print(f"   Main layout contains {len(main_layout.get_widgets())} widgets")
    print(f"   Group layout contains {len(group_layout.get_widgets())} widgets")
    
    # Show widget tree structure
    print("   Widget tree structure:")
    def print_widget_tree(widget, indent=0):
        if hasattr(widget, 'get_widget_tree'):
            tree = widget.get_widget_tree()
            print("   " + "  " * indent + f"- {tree['type']} (id: {tree['id']})")
            for child in tree.get('children', []):
                print_widget_tree(child, indent + 1)
    
    print_widget_tree(main_layout)
    
    return main_layout


def main():
    """Main demonstration function"""
    print("Script UI Widget Demonstration")
    print("=" * 50)
    
    try:
        # Run all demonstrations
        ui_impl, *widgets = demonstrate_widget_creation()
        layout = demonstrate_layout_and_sizing()
        *manipulated_widgets, = demonstrate_widget_manipulation()
        main_layout = demonstrate_widget_tree()
        
        print("\n=== Demo Complete ===")
        print("✅ All script UI widget demonstrations completed successfully!")
        print("\nKey Features Demonstrated:")
        print("  • Widget creation (buttons, text inputs, combo boxes, etc.)")
        print("  • Qt-like layout and sizing system")
        print("  • Widget manipulation and querying")
        print("  • Widget hierarchy and tree structure")
        print("  • Programmatic control without Qt dependencies")
        
        # Cleanup
        ui_impl.cleanup()
        
    except Exception as e:
        print(f"❌ Demo failed with error: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
