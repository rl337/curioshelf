"""
Pytest plugin for timeout handling and modal dialog detection

This plugin provides better timeout handling and detection of modal dialogs
that might cause tests to hang.
"""

import pytest
import time
import threading
import signal
from typing import Any, Optional


class TimeoutError(Exception):
    """Raised when a test times out"""
    pass


class TestTimeoutPlugin:
    """Pytest plugin for timeout handling"""
    
    def __init__(self):
        self.timeout_seconds = 10.0  # Default timeout
        self.active_timers = {}
    
    def pytest_configure(self, config):
        """Configure the plugin"""
        self.timeout_seconds = config.getoption("--timeout", default=10.0)
    
    def pytest_addoption(self, parser):
        """Add command line options"""
        parser.addoption(
            "--timeout",
            type=float,
            default=10.0,
            help="Test timeout in seconds (default: 10.0)"
        )
        parser.addoption(
            "--detect-modals",
            action="store_true",
            help="Detect and report modal dialogs"
        )
    
    def pytest_runtest_setup(self, item):
        """Set up timeout for each test"""
        if hasattr(item, 'get_closest_marker'):
            timeout_marker = item.get_closest_marker('timeout')
            if timeout_marker:
                self.timeout_seconds = timeout_marker.args[0]
        
        # Set up timeout timer
        self._setup_timeout(item)
    
    def pytest_runtest_teardown(self, item):
        """Clean up timeout for each test"""
        self._cleanup_timeout(item)
    
    def _setup_timeout(self, item):
        """Set up timeout timer for a test item"""
        test_name = f"{item.nodeid}"
        
        def timeout_handler():
            print(f"\n[TEST TIMEOUT] {test_name} exceeded {self.timeout_seconds} seconds")
            print("[MODAL DETECTION] Checking for modal dialogs...")
            self._check_for_modals()
            raise TimeoutError(f"Test {test_name} timed out after {self.timeout_seconds} seconds")
        
        timer = threading.Timer(self.timeout_seconds, timeout_handler)
        timer.start()
        self.active_timers[test_name] = timer
    
    def _cleanup_timeout(self, item):
        """Clean up timeout timer for a test item"""
        test_name = f"{item.nodeid}"
        if test_name in self.active_timers:
            self.active_timers[test_name].cancel()
            del self.active_timers[test_name]
    
    def _check_for_modals(self):
        """Check for modal dialogs"""
        try:
            from PySide6.QtWidgets import QApplication
            app = QApplication.instance()
            if app:
                modal_widgets = []
                for widget in app.allWidgets():
                    if hasattr(widget, 'isModal') and widget.isModal():
                        modal_widgets.append(type(widget).__name__)
                
                if modal_widgets:
                    print(f"[MODAL DIALOGS DETECTED] {', '.join(modal_widgets)}")
                else:
                    print("[NO MODAL DIALOGS] No modal widgets found")
            else:
                print("[NO QAPPLICATION] QApplication not available")
        except ImportError:
            print("[NO PYSIDE6] PySide6 not available for modal detection")
        except Exception as e:
            print(f"[MODAL DETECTION ERROR] {e}")


def pytest_configure(config):
    """Configure pytest with timeout plugin"""
    config.pluginmanager.register(TestTimeoutPlugin(), "timeout-plugin")


@pytest.fixture(autouse=True)
def timeout_protection(request):
    """Automatic timeout protection for all tests"""
    # Get timeout from marker or default
    timeout_marker = request.node.get_closest_marker('timeout')
    timeout_seconds = timeout_marker.args[0] if timeout_marker else 10.0
    
    # Set up signal-based timeout (works better than threading for some cases)
    old_handler = signal.signal(signal.SIGALRM, lambda s, f: _timeout_handler(request.node.name, timeout_seconds))
    signal.alarm(int(timeout_seconds))
    
    yield
    
    # Clean up
    signal.alarm(0)
    signal.signal(signal.SIGALRM, old_handler)


def _timeout_handler(test_name: str, timeout_seconds: float):
    """Handle test timeout"""
    print(f"\n[TEST TIMEOUT] {test_name} exceeded {timeout_seconds} seconds")
    print("[MODAL DETECTION] Checking for modal dialogs...")
    
    # Check for modal dialogs
    try:
        from PySide6.QtWidgets import QApplication
        app = QApplication.instance()
        if app:
            modal_widgets = []
            for widget in app.allWidgets():
                if hasattr(widget, 'isModal') and widget.isModal():
                    modal_widgets.append(type(widget).__name__)
            
            if modal_widgets:
                print(f"[MODAL DIALOGS DETECTED] {', '.join(modal_widgets)}")
            else:
                print("[NO MODAL DIALOGS] No modal widgets found")
        else:
            print("[NO QAPPLICATION] QApplication not available")
    except ImportError:
        print("[NO PYSIDE6] PySide6 not available for modal detection")
    except Exception as e:
        print(f"[MODAL DETECTION ERROR] {e}")
    
    raise TimeoutError(f"Test {test_name} timed out after {timeout_seconds} seconds")
