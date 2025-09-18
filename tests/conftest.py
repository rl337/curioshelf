"""
Pytest configuration for CurioShelf tests

This file contains shared fixtures and configuration for all tests.
"""

import pytest
import sys
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))


def pytest_configure(config):
    """Configure pytest with custom markers"""
    config.addinivalue_line(
        "markers", "qt: mark test as requiring Qt/PySide6"
    )
    config.addinivalue_line(
        "markers", "display: mark test as requiring a display"
    )
    config.addinivalue_line(
        "markers", "headless: mark test as using headless UI"
    )
    config.addinivalue_line(
        "markers", "slow: mark test as slow running"
    )


def pytest_collection_modifyitems(config, items):
    """Modify test collection based on available dependencies"""
    # Check if PySide6 is available
    try:
        import PySide6
        PYSIDE6_AVAILABLE = True
    except ImportError:
        PYSIDE6_AVAILABLE = False
    
    # Check if display is available
    DISPLAY_AVAILABLE = False
    if PYSIDE6_AVAILABLE:
        try:
            from PySide6.QtWidgets import QApplication
            app = QApplication.instance()
            if app is None:
                app = QApplication([])
            DISPLAY_AVAILABLE = True
            if app:
                app.quit()
        except Exception:
            DISPLAY_AVAILABLE = False
    
    # Skip Qt tests if PySide6 is not available
    for item in items:
        if "qt" in item.keywords and not PYSIDE6_AVAILABLE:
            item.add_marker(pytest.mark.skip(reason="PySide6 not available"))
        elif "display" in item.keywords and not DISPLAY_AVAILABLE:
            item.add_marker(pytest.mark.skip(reason="Display not available"))


@pytest.fixture(scope="session")
def project_root_path():
    """Provide the project root path"""
    return Path(__file__).parent.parent


@pytest.fixture(scope="session")
def test_data_dir(project_root_path):
    """Provide the test data directory"""
    return project_root_path / "tests" / "data"


@pytest.fixture
def temp_project_dir(tmp_path):
    """Provide a temporary directory for project testing"""
    return tmp_path / "test_project"


@pytest.fixture
def sample_image_path(test_data_dir):
    """Provide a path to a sample image for testing"""
    # Create a simple test image if it doesn't exist
    image_path = test_data_dir / "sample.png"
    if not image_path.exists():
        test_data_dir.mkdir(exist_ok=True)
        # Create a simple 100x100 PNG image
        from PIL import Image
        img = Image.new('RGB', (100, 100), color='red')
        img.save(image_path)
    return image_path


@pytest.fixture
def headless_ui_factory():
    """Provide a headless UI factory for testing"""
    from curioshelf.ui.ui_factory import create_ui_factory
    return create_ui_factory("headless", verbose=False)


@pytest.fixture
def qt_ui_factory():
    """Provide a Qt UI factory for testing (if available)"""
    try:
        from curioshelf.ui.ui_factory import create_ui_factory
        return create_ui_factory("qt", verbose=False)
    except ImportError:
        pytest.skip("Qt UI not available")


@pytest.fixture
def debugger():
    """Provide a debugger for testing"""
    from curioshelf.ui_debug import create_debugger
    return create_debugger(enabled=True)


@pytest.fixture
def message_collector():
    """Provide a message collector for testing"""
    from curioshelf.ui.headless.message_system import MessageCollector
    return MessageCollector()
