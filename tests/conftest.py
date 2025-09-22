"""
Pytest configuration and fixtures for CurioShelf tests

This module provides shared fixtures and configuration for all tests,
including automatic loading of test plugins for Qt-related tests.
"""

import pytest
import sys
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

# Import test plugin loader
try:
    from tests.support.test_plugin_loader import load_test_plugins, initialize_test_plugins, get_heartbeat_monitor
    TEST_PLUGINS_AVAILABLE = True
except ImportError:
    TEST_PLUGINS_AVAILABLE = False

# Import automatic Qt instrumentation
try:
    from tests.support.auto_qt_instrumentation import setup_test_safety, cleanup_test_safety
    AUTO_QT_INSTRUMENTATION_AVAILABLE = True
except ImportError:
    AUTO_QT_INSTRUMENTATION_AVAILABLE = False


@pytest.fixture(scope="session", autouse=True)
def setup_test_environment():
    """Setup test environment with plugins if available"""
    if AUTO_QT_INSTRUMENTATION_AVAILABLE:
        # Setup comprehensive test safety measures
        setup_test_safety()
    
    yield
    
    # Cleanup
    if AUTO_QT_INSTRUMENTATION_AVAILABLE:
        cleanup_test_safety()
    
    # Cleanup UI debugger threads
    try:
        from tests.ui_debug import cleanup_global_debugger
        cleanup_global_debugger()
    except ImportError:
        pass
    except Exception as e:
        print(f"[CONFTEST] Error cleaning up UI debugger: {e}")


@pytest.fixture(scope="function")
def qt_test_environment():
    """Fixture for tests that need Qt components with heartbeat monitoring"""
    if not TEST_PLUGINS_AVAILABLE:
        pytest.skip("Test plugins not available")
    
    # Initialize test plugins with a mock application
    from tests.mock_application import MockCurioShelfApplication
    mock_app = MockCurioShelfApplication()
    
    if not initialize_test_plugins(mock_app):
        pytest.skip("Failed to initialize test plugins")
    
    # Get heartbeat monitor (it starts automatically)
    heartbeat_monitor = get_heartbeat_monitor()
    
    yield mock_app
    
    # Cleanup
    if heartbeat_monitor:
        heartbeat_monitor.heartbeat_timer.stop()


@pytest.fixture(scope="function")
def real_qt_test_environment():
    """Fixture for tests that need real Qt application with heartbeat monitoring"""
    if not TEST_PLUGINS_AVAILABLE:
        pytest.skip("Test plugins not available")
    
    # Create a real application implementation
    from curioshelf.app_impl.application_impl import CurioShelfApplicationImpl
    real_app = CurioShelfApplicationImpl()
    
    if not initialize_test_plugins(real_app):
        pytest.skip("Failed to initialize test plugins")
    
    # Get heartbeat monitor
    heartbeat_monitor = get_heartbeat_monitor()
    if heartbeat_monitor:
        heartbeat_monitor.start_monitoring()
    
    yield real_app
    
    # Cleanup
    if heartbeat_monitor:
        heartbeat_monitor.stop_monitoring()


# Auto-use fixtures for tests that might need Qt
def pytest_collection_modifyitems(config, items):
    """Automatically mark tests that might need Qt components"""
    qt_test_patterns = [
        'test_ui_',
        'test_project_functionality',
        'test_event_execution',
        'test_ui_functionality',
        'test_ui_ghosting',
        'test_ui_debugging',
        'test_business_logic_with_messages',
        'test_message_system',
        'test_curio_scripts',
        'test_app',
    ]
    
    for item in items:
        # Check if test name matches any Qt-related patterns
        if any(pattern in item.name for pattern in qt_test_patterns):
            # Mark test as needing Qt environment
            item.add_marker(pytest.mark.qt_test)
            
            # Auto-use the qt_test_environment fixture
            if 'qt_test_environment' not in item.fixturenames:
                item.fixturenames.append('qt_test_environment')


# Pytest markers
def pytest_configure(config):
    """Configure pytest markers"""
    config.addinivalue_line(
        "markers", "qt_test: mark test as requiring Qt components with heartbeat monitoring"
    )
    config.addinivalue_line(
        "markers", "real_qt_test: mark test as requiring real Qt application with heartbeat monitoring"
    )