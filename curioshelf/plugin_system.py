"""
Plugin system for CurioShelf

This module provides a plugin architecture that allows different UI backends
to register their own specific functionality without polluting the core application.
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional, Type
import logging

logger = logging.getLogger(__name__)


class Plugin(ABC):
    """Base class for all CurioShelf plugins"""
    
    def __init__(self, name: str, version: str = "1.0.0"):
        self.name = name
        self.version = version
        self.enabled = False
    
    @abstractmethod
    def initialize(self, application: Any) -> bool:
        """Initialize the plugin with the application instance"""
        pass
    
    @abstractmethod
    def cleanup(self) -> bool:
        """Cleanup the plugin resources"""
        pass
    
    def enable(self) -> None:
        """Enable the plugin"""
        self.enabled = True
        logger.debug(f"Plugin {self.name} enabled")
    
    def disable(self) -> None:
        """Disable the plugin"""
        self.enabled = False
        logger.debug(f"Plugin {self.name} disabled")


class PluginManager:
    """Manages plugins for the application"""
    
    def __init__(self):
        self.plugins: Dict[str, Plugin] = {}
        self.application: Optional[Any] = None
        self.logger = logging.getLogger(__name__)
    
    def register_plugin(self, plugin: Plugin) -> bool:
        """Register a plugin with the manager"""
        if plugin.name in self.plugins:
            self.logger.warning(f"Plugin {plugin.name} is already registered")
            return False
        
        self.plugins[plugin.name] = plugin
        self.logger.debug(f"Registered plugin: {plugin.name} v{plugin.version}")
        return True
    
    def unregister_plugin(self, name: str) -> bool:
        """Unregister a plugin"""
        if name not in self.plugins:
            self.logger.warning(f"Plugin {name} is not registered")
            return False
        
        plugin = self.plugins[name]
        if plugin.enabled:
            plugin.cleanup()
        
        del self.plugins[name]
        self.logger.debug(f"Unregistered plugin: {name}")
        return True
    
    def initialize_plugins(self, application: Any) -> bool:
        """Initialize all registered plugins"""
        self.application = application
        success = True
        
        for plugin in self.plugins.values():
            try:
                if plugin.initialize(application):
                    self.logger.debug(f"Plugin {plugin.name} initialized successfully")
                else:
                    self.logger.error(f"Failed to initialize plugin {plugin.name}")
                    success = False
            except Exception as e:
                self.logger.error(f"Error initializing plugin {plugin.name}: {e}")
                success = False
        
        return success
    
    def cleanup_plugins(self) -> bool:
        """Cleanup all plugins"""
        success = True
        
        for plugin in self.plugins.values():
            try:
                if plugin.cleanup():
                    self.logger.debug(f"Plugin {plugin.name} cleaned up successfully")
                else:
                    self.logger.error(f"Failed to cleanup plugin {plugin.name}")
                    success = False
            except Exception as e:
                self.logger.error(f"Error cleaning up plugin {plugin.name}: {e}")
                success = False
        
        return success
    
    def get_plugin(self, name: str) -> Optional[Plugin]:
        """Get a plugin by name"""
        return self.plugins.get(name)
    
    def list_plugins(self) -> List[str]:
        """List all registered plugin names"""
        return list(self.plugins.keys())
    
    def enable_plugin(self, name: str) -> bool:
        """Enable a specific plugin"""
        plugin = self.get_plugin(name)
        if plugin:
            plugin.enable()
            return True
        return False
    
    def disable_plugin(self, name: str) -> bool:
        """Disable a specific plugin"""
        plugin = self.get_plugin(name)
        if plugin:
            plugin.disable()
            return True
        return False


# Global plugin manager instance
plugin_manager = PluginManager()
