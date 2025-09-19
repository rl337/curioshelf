"""
Pytest configuration for CurioShelf tests

This file contains shared fixtures and configuration for all tests.
"""

import pytest
import sys
import time
import threading
from pathlib import Path
from unittest.mock import patch

# Add the project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Import timeout plugin
from .pytest_timeout_plugin import TestTimeoutPlugin


def pytest_configure(config):
    """Configure pytest with custom markers and plugins"""
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
    config.addinivalue_line(
        "markers", "timeout: mark test with specific timeout"
    )
    
    # Register timeout plugin
    config.pluginmanager.register(TestTimeoutPlugin(), "timeout-plugin")


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


# Removed test_data_dir fixture - using temporary directories instead


@pytest.fixture
def temp_project_dir(tmp_path):
    """Provide a temporary directory for project testing"""
    project_dir = tmp_path / "test_project"
    project_dir.mkdir(exist_ok=True)
    return project_dir


@pytest.fixture
def temp_project_with_files(temp_project_dir):
    """Provide a temporary project directory with some test files"""
    # Create some test files in the project directory
    (temp_project_dir / "sources").mkdir(exist_ok=True)
    (temp_project_dir / "templates").mkdir(exist_ok=True)
    (temp_project_dir / "objects").mkdir(exist_ok=True)
    
    # Create a curioshelf.json file with the new project structure
    from curioshelf.projects import ProjectMetadata, ProjectStructure
    
    metadata = ProjectMetadata(
        name="Test Project",
        description="A test project for unit testing",
        author="Test User"
    )
    
    structure = ProjectStructure(metadata=metadata)
    
    import json
    with open(temp_project_dir / "curioshelf.json", "w") as f:
        json.dump(structure.to_dict(), f, indent=2)
    
    return temp_project_dir


@pytest.fixture
def sample_image_path(tmp_path):
    """Provide a path to a sample image for testing"""
    # Create a simple test image in a temporary directory
    image_path = tmp_path / "sample.png"
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
    from tests.ui_debug import create_debugger
    return create_debugger(enabled=True)


@pytest.fixture
def message_collector():
    """Provide a message collector for testing"""
    from curioshelf.ui.headless.message_system import MessageCollector
    return MessageCollector()


@pytest.fixture(autouse=True)
def modal_dialog_protection():
    """Automatically mock modal dialogs to prevent test hangs"""
    with patch('curioshelf.ui.qtimpl.ui_widgets.QtUIFileDialog.get_open_file_name', return_value=None), \
         patch('curioshelf.ui.qtimpl.ui_widgets.QtUIFileDialog.get_save_file_name', return_value=None), \
         patch('curioshelf.ui.qtimpl.ui_widgets.QtUIMessageBox.show_info'), \
         patch('curioshelf.ui.qtimpl.ui_widgets.QtUIMessageBox.show_warning'), \
         patch('curioshelf.ui.qtimpl.ui_widgets.QtUIMessageBox.show_error'), \
         patch('curioshelf.ui.qtimpl.ui_widgets.QtUIMessageBox.show_question', return_value=False):
        yield


@pytest.fixture
def timeout_protection():
    """Provide timeout protection for tests"""
    def _timeout_protection(timeout_seconds=10.0):
        def decorator(func):
            def wrapper(*args, **kwargs):
                result = [None]
                exception = [None]
                
                def run_test():
                    try:
                        result[0] = func(*args, **kwargs)
                    except Exception as e:
                        exception[0] = e
                
                thread = threading.Thread(target=run_test)
                thread.daemon = True
                thread.start()
                thread.join(timeout_seconds)
                
                if thread.is_alive():
                    print(f"\n[TEST TIMEOUT] {func.__name__} exceeded {timeout_seconds} seconds")
                    raise TimeoutError(f"Test {func.__name__} timed out after {timeout_seconds} seconds")
                
                if exception[0]:
                    raise exception[0]
                
                return result[0]
            return wrapper
        return decorator
    return _timeout_protection


@pytest.fixture
def ui_logging():
    """Enable detailed UI logging for debugging"""
    import logging
    
    # Set up detailed logging for UI components
    ui_logger = logging.getLogger('curioshelf.ui')
    ui_logger.setLevel(logging.DEBUG)
    
    # Create a handler that prints to console
    handler = logging.StreamHandler()
    handler.setLevel(logging.DEBUG)
    
    # Create formatter
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    handler.setFormatter(formatter)
    
    # Add handler to logger
    ui_logger.addHandler(handler)
    
    yield ui_logger
    
    # Clean up
    ui_logger.removeHandler(handler)
