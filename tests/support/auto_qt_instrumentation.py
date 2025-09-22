"""
Automatic Qt Instrumentation for Tests

This module provides automatic instrumentation of Qt applications
to prevent test hanging by monkey-patching Qt components.
"""

import sys
import os
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).parent.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

# Import the Qt wrapper
try:
    from tests.support.qt_application_wrapper import wrap_qt_application, cleanup_qt_wrapper
    QT_WRAPPER_AVAILABLE = True
except ImportError:
    QT_WRAPPER_AVAILABLE = False

# Import the test plugin loader
try:
    from tests.support.test_plugin_loader import load_test_plugins, initialize_test_plugins, get_heartbeat_monitor
    TEST_PLUGINS_AVAILABLE = True
except ImportError:
    TEST_PLUGINS_AVAILABLE = False


def instrument_qt_components():
    """Instrument Qt components to prevent hanging"""
    if not QT_WRAPPER_AVAILABLE:
        return
    
    # The Qt wrapper already monkey-patches QApplication
    print("[AUTO QT] Qt components instrumented for test safety")


def instrument_curioshelf_application():
    """Instrument CurioShelf application components"""
    if not TEST_PLUGINS_AVAILABLE:
        return
    
    # Load test plugins
    load_test_plugins()
    print("[AUTO QT] CurioShelf application instrumented for test safety")


def setup_test_safety():
    """Setup comprehensive test safety measures"""
    print("[AUTO QT] Setting up test safety measures...")
    
    # Instrument Qt components
    instrument_qt_components()
    
    # Instrument CurioShelf application
    instrument_curioshelf_application()
    
    print("[AUTO QT] Test safety measures configured")


def cleanup_test_safety():
    """Cleanup test safety measures"""
    if QT_WRAPPER_AVAILABLE:
        cleanup_qt_wrapper()
    print("[AUTO QT] Test safety measures cleaned up")


# Auto-setup when module is imported
if __name__ != "__main__":
    setup_test_safety()
