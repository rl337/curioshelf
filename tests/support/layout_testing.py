"""
Layout testing utilities for verifying widget positioning and detecting overlaps
"""

from typing import List, Tuple, Dict, Any, Optional
from dataclasses import dataclass
from curioshelf.ui.abstraction import UIWidget


@dataclass
class WidgetGeometry:
    """Represents the geometry of a widget"""
    x: int
    y: int
    width: int
    height: int
    widget: UIWidget
    
    @property
    def right(self) -> int:
        """Get the right edge of the widget"""
        return self.x + self.width
    
    @property
    def bottom(self) -> int:
        """Get the bottom edge of the widget"""
        return self.y + self.height
    
    @property
    def center_x(self) -> int:
        """Get the center X coordinate"""
        return self.x + self.width // 2
    
    @property
    def center_y(self) -> int:
        """Get the center Y coordinate"""
        return self.y + self.height // 2
    
    def overlaps_with(self, other: 'WidgetGeometry') -> bool:
        """Check if this widget overlaps with another widget"""
        return not (self.right <= other.x or 
                   other.right <= self.x or 
                   self.bottom <= other.y or 
                   other.bottom <= other.y)
    
    def contains_point(self, x: int, y: int) -> bool:
        """Check if a point is inside this widget"""
        return (self.x <= x < self.right and 
                self.y <= y < self.bottom)
    
    def contains_widget(self, other: 'WidgetGeometry') -> bool:
        """Check if this widget completely contains another widget"""
        return (self.x <= other.x and 
                self.y <= other.y and 
                self.right >= other.right and 
                self.bottom >= other.bottom)


@dataclass
class LayoutViolation:
    """Represents a layout violation"""
    violation_type: str
    message: str
    widget1: Optional[UIWidget] = None
    widget2: Optional[UIWidget] = None
    geometry1: Optional[WidgetGeometry] = None
    geometry2: Optional[WidgetGeometry] = None
    severity: str = "error"  # error, warning, info


class LayoutTester:
    """Utility class for testing widget layouts and detecting violations"""
    
    def __init__(self):
        self.violations: List[LayoutViolation] = []
    
    def test_widget_geometries(self, widgets: List[UIWidget]) -> List[LayoutViolation]:
        """Test a list of widgets for layout violations"""
        self.violations.clear()
        
        # Get geometries for all widgets
        geometries = []
        for widget in widgets:
            if widget.is_visible():
                x, y, width, height = widget.get_geometry()
                geometries.append(WidgetGeometry(x, y, width, height, widget))
        
        # Test for various violations
        self._test_overlaps(geometries)
        self._test_zero_sizes(geometries)
        self._test_negative_positions(geometries)
        self._test_container_bounds(geometries)
        
        return self.violations.copy()
    
    def _test_overlaps(self, geometries: List[WidgetGeometry]) -> None:
        """Test for overlapping widgets"""
        for i, geom1 in enumerate(geometries):
            for j, geom2 in enumerate(geometries[i+1:], i+1):
                if geom1.overlaps_with(geom2):
                    self.violations.append(LayoutViolation(
                        violation_type="overlap",
                        message=f"Widgets overlap: {geom1.widget.__class__.__name__} and {geom2.widget.__class__.__name__}",
                        widget1=geom1.widget,
                        widget2=geom2.widget,
                        geometry1=geom1,
                        geometry2=geom2,
                        severity="error"
                    ))
    
    def _test_zero_sizes(self, geometries: List[WidgetGeometry]) -> None:
        """Test for widgets with zero or negative sizes"""
        for geom in geometries:
            if geom.width <= 0:
                self.violations.append(LayoutViolation(
                    violation_type="zero_width",
                    message=f"Widget has zero or negative width: {geom.widget.__class__.__name__}",
                    widget1=geom.widget,
                    geometry1=geom,
                    severity="error"
                ))
            
            if geom.height <= 0:
                self.violations.append(LayoutViolation(
                    violation_type="zero_height",
                    message=f"Widget has zero or negative height: {geom.widget.__class__.__name__}",
                    widget1=geom.widget,
                    geometry1=geom,
                    severity="error"
                ))
    
    def _test_negative_positions(self, geometries: List[WidgetGeometry]) -> None:
        """Test for widgets with negative positions"""
        for geom in geometries:
            if geom.x < 0:
                self.violations.append(LayoutViolation(
                    violation_type="negative_x",
                    message=f"Widget has negative X position: {geom.widget.__class__.__name__}",
                    widget1=geom.widget,
                    geometry1=geom,
                    severity="warning"
                ))
            
            if geom.y < 0:
                self.violations.append(LayoutViolation(
                    violation_type="negative_y",
                    message=f"Widget has negative Y position: {geom.widget.__class__.__name__}",
                    widget1=geom.widget,
                    geometry1=geom,
                    severity="warning"
                ))
    
    def _test_container_bounds(self, geometries: List[WidgetGeometry]) -> None:
        """Test for widgets that extend beyond reasonable bounds"""
        if not geometries:
            return
        
        # Find the bounds of all widgets
        min_x = min(geom.x for geom in geometries)
        min_y = min(geom.y for geom in geometries)
        max_x = max(geom.right for geom in geometries)
        max_y = max(geom.bottom for geom in geometries)
        
        # Check for widgets that are way outside the main area
        for geom in geometries:
            if geom.x > max_x + 1000:  # Way to the right
                self.violations.append(LayoutViolation(
                    violation_type="out_of_bounds",
                    message=f"Widget is positioned far outside main area: {geom.widget.__class__.__name__}",
                    widget1=geom.widget,
                    geometry1=geom,
                    severity="warning"
                ))
            
            if geom.y > max_y + 1000:  # Way below
                self.violations.append(LayoutViolation(
                    violation_type="out_of_bounds",
                    message=f"Widget is positioned far outside main area: {geom.widget.__class__.__name__}",
                    widget1=geom.widget,
                    geometry1=geom,
                    severity="warning"
                ))
    
    def test_layout_hierarchy(self, container: UIWidget) -> List[LayoutViolation]:
        """Test the layout hierarchy of a container widget"""
        self.violations.clear()
        
        # Get all child widgets recursively
        all_widgets = self._get_all_widgets(container)
        
        # Test geometries
        self.test_widget_geometries(all_widgets)
        
        # Test parent-child relationships
        self._test_parent_child_relationships(container)
        
        return self.violations.copy()
    
    def _get_all_widgets(self, widget: UIWidget) -> List[UIWidget]:
        """Recursively get all widgets in a hierarchy"""
        widgets = [widget]
        
        # If this is a layout widget, get its child widgets
        if hasattr(widget, 'get_widgets'):
            for child in widget.get_widgets():
                widgets.extend(self._get_all_widgets(child))
        
        return widgets
    
    def _test_parent_child_relationships(self, container: UIWidget) -> None:
        """Test that child widgets are properly contained within their parents"""
        container_geom = WidgetGeometry(*container.get_geometry(), container)
        
        if hasattr(container, 'get_widgets'):
            for child in container.get_widgets():
                child_geom = WidgetGeometry(*child.get_geometry(), child)
                
                # Check if child is completely outside parent
                if not container_geom.overlaps_with(child_geom):
                    self.violations.append(LayoutViolation(
                        violation_type="child_outside_parent",
                        message=f"Child widget is completely outside parent: {child.__class__.__name__}",
                        widget1=container,
                        widget2=child,
                        geometry1=container_geom,
                        geometry2=child_geom,
                        severity="error"
                    ))
    
    def assert_no_violations(self, widgets: List[UIWidget], 
                           allowed_violations: List[str] = None) -> None:
        """Assert that there are no layout violations (except allowed ones)"""
        violations = self.test_widget_geometries(widgets)
        
        if allowed_violations is None:
            allowed_violations = []
        
        # Filter out allowed violations
        critical_violations = [
            v for v in violations 
            if v.violation_type not in allowed_violations and v.severity == "error"
        ]
        
        if critical_violations:
            error_messages = [f"- {v.message}" for v in critical_violations]
            raise AssertionError(
                f"Layout violations detected:\n" + "\n".join(error_messages)
            )
    
    def assert_no_overlaps(self, widgets: List[UIWidget]) -> None:
        """Assert that no widgets overlap"""
        violations = self.test_widget_geometries(widgets)
        overlap_violations = [v for v in violations if v.violation_type == "overlap"]
        
        if overlap_violations:
            error_messages = [f"- {v.message}" for v in overlap_violations]
            raise AssertionError(
                f"Widget overlaps detected:\n" + "\n".join(error_messages)
            )
    
    def assert_widget_contains(self, container: UIWidget, child: UIWidget) -> None:
        """Assert that a container widget contains a child widget"""
        container_geom = WidgetGeometry(*container.get_geometry(), container)
        child_geom = WidgetGeometry(*child.get_geometry(), child)
        
        if not container_geom.contains_widget(child_geom):
            raise AssertionError(
                f"Container {container.__class__.__name__} does not contain "
                f"child {child.__class__.__name__}"
            )
    
    def assert_widget_position(self, widget: UIWidget, expected_x: int, expected_y: int, 
                             tolerance: int = 5) -> None:
        """Assert that a widget is positioned at the expected location"""
        actual_x, actual_y = widget.get_position()
        
        if abs(actual_x - expected_x) > tolerance:
            raise AssertionError(
                f"Widget {widget.__class__.__name__} X position {actual_x} "
                f"does not match expected {expected_x} (tolerance: {tolerance})"
            )
        
        if abs(actual_y - expected_y) > tolerance:
            raise AssertionError(
                f"Widget {widget.__class__.__name__} Y position {actual_y} "
                f"does not match expected {expected_y} (tolerance: {tolerance})"
            )
    
    def assert_widget_size(self, widget: UIWidget, expected_width: int, expected_height: int,
                          tolerance: int = 5) -> None:
        """Assert that a widget has the expected size"""
        actual_width, actual_height = widget.get_size()
        
        if abs(actual_width - expected_width) > tolerance:
            raise AssertionError(
                f"Widget {widget.__class__.__name__} width {actual_width} "
                f"does not match expected {expected_width} (tolerance: {tolerance})"
            )
        
        if abs(actual_height - expected_height) > tolerance:
            raise AssertionError(
                f"Widget {widget.__class__.__name__} height {actual_height} "
                f"does not match expected {expected_height} (tolerance: {tolerance})"
            )
    
    def get_layout_summary(self, widgets: List[UIWidget]) -> Dict[str, Any]:
        """Get a summary of the layout for debugging"""
        geometries = []
        for widget in widgets:
            if widget.is_visible():
                x, y, width, height = widget.get_geometry()
                geometries.append(WidgetGeometry(x, y, width, height, widget))
        
        if not geometries:
            return {"message": "No visible widgets found"}
        
        min_x = min(geom.x for geom in geometries)
        min_y = min(geom.y for geom in geometries)
        max_x = max(geom.right for geom in geometries)
        max_y = max(geom.bottom for geom in geometries)
        
        return {
            "total_widgets": len(geometries),
            "bounds": {
                "min_x": min_x,
                "min_y": min_y,
                "max_x": max_x,
                "max_y": max_y,
                "width": max_x - min_x,
                "height": max_y - min_y
            },
            "widgets": [
                {
                    "type": geom.widget.__class__.__name__,
                    "geometry": (geom.x, geom.y, geom.width, geom.height)
                }
                for geom in geometries
            ]
        }
