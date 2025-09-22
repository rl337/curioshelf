"""
Test Plugin Loader for CurioShelf

This module loads testing plugins when running in scripted mode.
It should only be imported in test environments.
"""

import sys
from pathlib import Path

# Add test_support to path so we can import plugins
test_support_path = Path(__file__).parent
if str(test_support_path) not in sys.path:
    sys.path.insert(0, str(test_support_path))

from curioshelf.plugin_system import plugin_manager
from tests.support.plugins.qt_heartbeat_plugin import QtHeartbeatPlugin
from tests.support.plugins.qt_dialog_responder_plugin import QtDialogResponderPlugin


def load_test_plugins():
    """Load all testing plugins"""
    print("[TEST PLUGIN LOADER] Loading test plugins...")
    
    # Register Qt-specific plugins
    heartbeat_plugin = QtHeartbeatPlugin()
    dialog_responder_plugin = QtDialogResponderPlugin()
    
    plugin_manager.register_plugin(heartbeat_plugin)
    plugin_manager.register_plugin(dialog_responder_plugin)
    
    print(f"[TEST PLUGIN LOADER] Registered {len(plugin_manager.list_plugins())} plugins")
    return plugin_manager


def initialize_test_plugins(application):
    """Initialize all test plugins with the application"""
    print("[TEST PLUGIN LOADER] Initializing test plugins...")
    
    success = plugin_manager.initialize_plugins(application)
    if success:
        print("[TEST PLUGIN LOADER] All test plugins initialized successfully")
    else:
        print("[TEST PLUGIN LOADER] Some test plugins failed to initialize")
    
    return success


def cleanup_test_plugins():
    """Cleanup all test plugins"""
    print("[TEST PLUGIN LOADER] Cleaning up test plugins...")
    
    success = plugin_manager.cleanup_plugins()
    if success:
        print("[TEST PLUGIN LOADER] All test plugins cleaned up successfully")
    else:
        print("[TEST PLUGIN LOADER] Some test plugins failed to cleanup")
    
    return success


def get_heartbeat_monitor():
    """Get the heartbeat monitor from the plugin manager"""
    heartbeat_plugin = plugin_manager.get_plugin("qt_heartbeat")
    if heartbeat_plugin:
        return heartbeat_plugin.get_monitor()
    return None


def get_dialog_responder():
    """Get the dialog responder from the plugin manager"""
    dialog_plugin = plugin_manager.get_plugin("qt_dialog_responder")
    if dialog_plugin:
        return dialog_plugin.get_responder()
    return None
