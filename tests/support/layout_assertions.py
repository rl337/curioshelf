"""
Layout assertion utilities for existing tests
"""

from typing import List, Optional, Set, Tuple
from curioshelf.ui.abstraction import UIWidget
from .layout_testing import LayoutTester, WidgetGeometry, LayoutViolation


def assert_no_unauthorized_overlaps(widgets: List[UIWidget], 
                                  parent_child_relationships: Optional[List[Tuple[UIWidget, UIWidget]]] = None) -> None:
    """
    Assert that no visible widgets overlap unless they have a proper parent-child relationship.
    
    Args:
        widgets: List of widgets to test
        parent_child_relationships: Optional list of (parent, child) tuples that are allowed to overlap
    """
    if parent_child_relationships is None:
        parent_child_relationships = []
    
    # Create a set of allowed overlapping pairs
    allowed_overlaps = set()
    for parent, child in parent_child_relationships:
        allowed_overlaps.add((id(parent), id(child)))
        allowed_overlaps.add((id(child), id(parent)))  # Bidirectional
    
    # Get all visible widgets
    visible_widgets = [w for w in widgets if w.is_visible()]
    
    if len(visible_widgets) < 2:
        return  # Need at least 2 widgets to test overlaps
    
    # Get geometries for all visible widgets
    geometries = []
    for widget in visible_widgets:
        x, y, width, height = widget.get_geometry()
        geometries.append(WidgetGeometry(x, y, width, height, widget))
    
    # Check for unauthorized overlaps
    violations = []
    for i, geom1 in enumerate(geometries):
        for j, geom2 in enumerate(geometries[i+1:], i+1):
            if geom1.overlaps_with(geom2):
                widget1_id = id(geom1.widget)
                widget2_id = id(geom2.widget)
                
                # Check if this overlap is allowed
                if (widget1_id, widget2_id) not in allowed_overlaps:
                    violations.append(LayoutViolation(
                        violation_type="unauthorized_overlap",
                        message=f"Unauthorized overlap: {geom1.widget.__class__.__name__} and {geom2.widget.__class__.__name__}",
                        widget1=geom1.widget,
                        widget2=geom2.widget,
                        geometry1=geom1,
                        geometry2=geom2,
                        severity="error"
                    ))
    
    if violations:
        error_messages = [f"- {v.message}" for v in violations]
        raise AssertionError(
            f"Unauthorized widget overlaps detected:\n" + "\n".join(error_messages)
        )


def assert_proper_widget_placement(widgets: List[UIWidget]) -> None:
    """
    Assert that all widgets have proper placement (no zero sizes, reasonable positions).
    
    Args:
        widgets: List of widgets to test
    """
    tester = LayoutTester()
    violations = tester.test_widget_geometries(widgets)
    
    # Filter out only critical violations
    critical_violations = [v for v in violations if v.severity == "error"]
    
    if critical_violations:
        error_messages = [f"- {v.message}" for v in critical_violations]
        raise AssertionError(
            f"Widget placement violations detected:\n" + "\n".join(error_messages)
        )


def assert_layout_hierarchy_integrity(container: UIWidget) -> None:
    """
    Assert that a container widget's layout hierarchy is properly structured.
    
    Args:
        container: The container widget to test
    """
    tester = LayoutTester()
    violations = tester.test_layout_hierarchy(container)
    
    # Filter out only critical violations
    critical_violations = [v for v in violations if v.severity == "error"]
    
    if critical_violations:
        error_messages = [f"- {v.message}" for v in critical_violations]
        raise AssertionError(
            f"Layout hierarchy violations detected:\n" + "\n".join(error_messages)
        )


def get_parent_child_relationships(container: UIWidget) -> List[Tuple[UIWidget, UIWidget]]:
    """
    Get all parent-child relationships in a widget hierarchy.
    
    Args:
        container: The root container widget
        
    Returns:
        List of (parent, child) tuples
    """
    relationships = []
    
    def _collect_relationships(widget: UIWidget, parent: Optional[UIWidget] = None):
        if parent is not None:
            relationships.append((parent, widget))
        
        # If this widget has child widgets, collect their relationships
        if hasattr(widget, 'get_widgets'):
            for child in widget.get_widgets():
                _collect_relationships(child, widget)
        
        # Also check for layout widgets that might contain children
        if hasattr(widget, 'widgets'):  # For layout widgets
            for child in widget.widgets:
                _collect_relationships(child, widget)
        
        # Check for manually set children
        if hasattr(widget, '_children'):  # For manually set children
            for child in widget._children:
                _collect_relationships(child, widget)
    
    _collect_relationships(container)
    return relationships


def assert_comprehensive_layout(container: UIWidget) -> None:
    """
    Perform comprehensive layout assertions on a container widget.
    
    Args:
        container: The container widget to test
    """
    # Get all widgets in the hierarchy
    tester = LayoutTester()
    all_widgets = tester._get_all_widgets(container)
    
    # Get parent-child relationships
    relationships = get_parent_child_relationships(container)
    
    # Test for unauthorized overlaps
    assert_no_unauthorized_overlaps(all_widgets, relationships)
    
    # Test for proper placement
    assert_proper_widget_placement(all_widgets)
    
    # Test layout hierarchy integrity
    assert_layout_hierarchy_integrity(container)


def assert_widget_visibility_consistency(widgets: List[UIWidget]) -> None:
    """
    Assert that widget visibility is consistent across implementations.
    
    Args:
        widgets: List of widgets to test
    """
    for widget in widgets:
        # All widgets should have visibility methods
        assert hasattr(widget, 'is_visible'), f"Widget {widget.__class__.__name__} missing is_visible method"
        assert hasattr(widget, 'is_enabled'), f"Widget {widget.__class__.__name__} missing is_enabled method"
        
        # Visibility should return a boolean
        assert isinstance(widget.is_visible(), bool), f"is_visible() should return bool for {widget.__class__.__name__}"
        assert isinstance(widget.is_enabled(), bool), f"is_enabled() should return bool for {widget.__class__.__name__}"


def assert_widget_geometry_consistency(widgets: List[UIWidget]) -> None:
    """
    Assert that widget geometry methods are consistent across implementations.
    
    Args:
        widgets: List of widgets to test
    """
    for widget in widgets:
        # All widgets should have geometry methods
        assert hasattr(widget, 'get_size'), f"Widget {widget.__class__.__name__} missing get_size method"
        assert hasattr(widget, 'get_position'), f"Widget {widget.__class__.__name__} missing get_position method"
        assert hasattr(widget, 'get_geometry'), f"Widget {widget.__class__.__name__} missing get_geometry method"
        
        # Geometry methods should return tuples
        size = widget.get_size()
        position = widget.get_position()
        geometry = widget.get_geometry()
        
        assert isinstance(size, tuple), f"get_size() should return tuple for {widget.__class__.__name__}"
        assert len(size) == 2, f"get_size() should return (width, height) for {widget.__class__.__name__}"
        
        assert isinstance(position, tuple), f"get_position() should return tuple for {widget.__class__.__name__}"
        assert len(position) == 2, f"get_position() should return (x, y) for {widget.__class__.__name__}"
        
        assert isinstance(geometry, tuple), f"get_geometry() should return tuple for {widget.__class__.__name__}"
        assert len(geometry) == 4, f"get_geometry() should return (x, y, width, height) for {widget.__class__.__name__}"
        
        # Geometry should be consistent
        assert geometry[0] == position[0], f"Geometry x should match position x for {widget.__class__.__name__}"
        assert geometry[1] == position[1], f"Geometry y should match position y for {widget.__class__.__name__}"
        assert geometry[2] == size[0], f"Geometry width should match size width for {widget.__class__.__name__}"
        assert geometry[3] == size[1], f"Geometry height should match size height for {widget.__class__.__name__}"
