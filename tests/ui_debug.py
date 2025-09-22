"""
UI Debugging and Instrumentation System

This module provides debugging and instrumentation capabilities for the UI system,
allowing external tools to monitor, control, and debug UI components.
"""

import json
import time
from typing import Any, Dict, List, Optional, Callable, Union
from dataclasses import dataclass, asdict
from enum import Enum
from pathlib import Path
import threading
import queue


class DebugMessageType(Enum):
    """Types of debug messages"""
    UI_EVENT = "ui_event"
    STATE_CHANGE = "state_change"
    LAYOUT_UPDATE = "layout_update"
    WIDGET_CREATED = "widget_created"
    WIDGET_DESTROYED = "widget_destroyed"
    SIGNAL_EMITTED = "signal_emitted"
    CALLBACK_INVOKED = "callback_invoked"
    ERROR = "error"
    WARNING = "warning"
    INFO = "info"


@dataclass
class DebugMessage:
    """A debug message with metadata"""
    timestamp: float
    message_type: DebugMessageType
    component: str
    action: str
    data: Optional[Dict[str, Any]] = None
    thread_id: Optional[int] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization"""
        result = asdict(self)
        result['message_type'] = self.message_type.value
        return result
    
    def to_json(self) -> str:
        """Convert to JSON string"""
        return json.dumps(self.to_dict(), indent=2)


class UIDebugger:
    """Main UI debugging and instrumentation system"""
    
    def __init__(self, enabled: bool = True, log_file: Optional[Path] = None):
        self.enabled = enabled
        self.log_file = log_file
        self.messages: List[DebugMessage] = []
        self.message_queue = queue.Queue()
        self.subscribers: List[Callable[[DebugMessage], None]] = []
        self.thread_id = threading.get_ident()
        self._stop_event = threading.Event()
        self._processor_thread = None
        
        # Start message processing thread
        if self.enabled:
            self._start_message_processor()
    
    def __del__(self):
        """Destructor to ensure cleanup"""
        try:
            self.cleanup()
        except:
            pass  # Ignore errors during destruction
    
    def _start_message_processor(self):
        """Start the message processing thread"""
        def process_messages():
            try:
                while not self._stop_event.is_set():
                    try:
                        message = self.message_queue.get(timeout=1.0)
                        self._process_message(message)
                    except queue.Empty:
                        continue
                    except Exception as e:
                        print(f"Error processing debug message: {e}")
            except Exception as e:
                print(f"Fatal error in message processor: {e}")
            finally:
                print("[UI DEBUG] Message processor thread exiting")
        
        self._processor_thread = threading.Thread(target=process_messages, daemon=True, name="UIDebugProcessor")
        self._processor_thread.start()
        print(f"[UI DEBUG] Started message processor thread: {self._processor_thread.name}")
    
    def cleanup(self):
        """Cleanup the debug system and stop threads"""
        print("[UI DEBUG] Starting cleanup...")
        if self._processor_thread and self._processor_thread.is_alive():
            print("[UI DEBUG] Stopping message processor thread...")
            self._stop_event.set()
            self._processor_thread.join(timeout=2.0)
            if self._processor_thread.is_alive():
                print("[UI DEBUG] Warning: Thread did not stop gracefully")
            else:
                print("[UI DEBUG] Thread stopped successfully")
        else:
            print("[UI DEBUG] No active thread to cleanup")
        self._processor_thread = None
        print("[UI DEBUG] Cleanup completed")
    
    def _process_message(self, message: DebugMessage):
        """Process a debug message"""
        if not self.enabled:
            return
        
        # Add to message list
        self.messages.append(message)
        
        # Notify subscribers
        for subscriber in self.subscribers:
            try:
                subscriber(message)
            except Exception as e:
                print(f"Error in debug subscriber: {e}")
        
        # Write to log file if specified
        if self.log_file:
            try:
                with open(self.log_file, 'a') as f:
                    f.write(message.to_json() + '\n')
            except Exception as e:
                print(f"Error writing to log file: {e}")
    
    def log(self, message_type: DebugMessageType, component: str, action: str, 
            data: Optional[Dict[str, Any]] = None):
        """Log a debug message"""
        if not self.enabled:
            return
        
        message = DebugMessage(
            timestamp=time.time(),
            message_type=message_type,
            component=component,
            action=action,
            data=data or {},
            thread_id=threading.get_ident()
        )
        
        self.message_queue.put(message)
    
    def subscribe(self, callback: Callable[[DebugMessage], None]):
        """Subscribe to debug messages"""
        self.subscribers.append(callback)
    
    def unsubscribe(self, callback: Callable[[DebugMessage], None]):
        """Unsubscribe from debug messages"""
        if callback in self.subscribers:
            self.subscribers.remove(callback)
    
    def get_messages(self, message_type: Optional[DebugMessageType] = None, 
                    component: Optional[str] = None) -> List[DebugMessage]:
        """Get filtered debug messages"""
        messages = self.messages
        
        if message_type:
            messages = [m for m in messages if m.message_type == message_type]
        
        if component:
            messages = [m for m in messages if m.component == component]
        
        return messages
    
    def clear_messages(self):
        """Clear all debug messages"""
        self.messages.clear()
    
    def export_messages(self, file_path: Path):
        """Export messages to a file"""
        with open(file_path, 'w') as f:
            json.dump([msg.to_dict() for msg in self.messages], f, indent=2)


class UIDebugMixin:
    """Mixin class to add debugging capabilities to UI components"""
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._debugger: Optional[UIDebugger] = None
        self._debug_enabled = False
    
    def set_debugger(self, debugger: UIDebugger):
        """Set the debugger instance"""
        self._debugger = debugger
        self._debug_enabled = True
    
    def debug_log(self, message_type: DebugMessageType, action: str, 
                  data: Optional[Dict[str, Any]] = None):
        """Log a debug message"""
        if self._debug_enabled and self._debugger:
            component = self.__class__.__name__
            self._debugger.log(message_type, component, action, data)
    
    def debug_ui_event(self, action: str, data: Optional[Dict[str, Any]] = None):
        """Log a UI event"""
        self.debug_log(DebugMessageType.UI_EVENT, action, data)
    
    def debug_state_change(self, action: str, data: Optional[Dict[str, Any]] = None):
        """Log a state change"""
        self.debug_log(DebugMessageType.STATE_CHANGE, action, data)
    
    def debug_signal_emitted(self, signal_name: str, data: Optional[Any] = None):
        """Log a signal emission"""
        self.debug_log(DebugMessageType.SIGNAL_EMITTED, f"signal_{signal_name}", 
                      {"signal": signal_name, "data": str(data)})
    
    def debug_callback_invoked(self, callback_name: str, data: Optional[Dict[str, Any]] = None):
        """Log a callback invocation"""
        self.debug_log(DebugMessageType.CALLBACK_INVOKED, f"callback_{callback_name}", data)


class UIRemoteController:
    """Remote controller for UI components"""
    
    def __init__(self, debugger: UIDebugger):
        self.debugger = debugger
        self.controllers: Dict[str, Any] = {}
    
    def register_controller(self, name: str, controller: Any):
        """Register a UI controller for remote control"""
        self.controllers[name] = controller
        self.debugger.log(DebugMessageType.INFO, "UIRemoteController", 
                         f"registered_controller", {"name": name})
    
    def send_command(self, controller_name: str, command: str, 
                    args: Optional[Dict[str, Any]] = None) -> bool:
        """Send a command to a registered controller"""
        if controller_name not in self.controllers:
            self.debugger.log(DebugMessageType.ERROR, "UIRemoteController", 
                             "controller_not_found", {"name": controller_name})
            return False
        
        try:
            controller = self.controllers[controller_name]
            if hasattr(controller, command):
                method = getattr(controller, command)
                if callable(method):
                    if args:
                        result = method(**args)
                    else:
                        result = method()
                    
                    self.debugger.log(DebugMessageType.INFO, "UIRemoteController", 
                                     "command_executed", {
                                         "controller": controller_name,
                                         "command": command,
                                         "result": str(result)
                                     })
                    return True
                else:
                    self.debugger.log(DebugMessageType.ERROR, "UIRemoteController", 
                                     "command_not_callable", {"command": command})
                    return False
            else:
                self.debugger.log(DebugMessageType.ERROR, "UIRemoteController", 
                                 "command_not_found", {"command": command})
                return False
        except Exception as e:
            self.debugger.log(DebugMessageType.ERROR, "UIRemoteController", 
                             "command_failed", {"error": str(e)})
            return False
    
    def list_controllers(self) -> List[str]:
        """List all registered controllers"""
        return list(self.controllers.keys())
    
    def list_commands(self, controller_name: str) -> List[str]:
        """List available commands for a controller"""
        if controller_name not in self.controllers:
            return []
        
        controller = self.controllers[controller_name]
        commands = []
        for attr_name in dir(controller):
            if not attr_name.startswith('_') and callable(getattr(controller, attr_name)):
                commands.append(attr_name)
        return commands


# Global debugger instance
_global_debugger: Optional[UIDebugger] = None


def get_global_debugger() -> UIDebugger:
    """Get the global debugger instance"""
    global _global_debugger
    if _global_debugger is None:
        _global_debugger = UIDebugger(enabled=True)
    return _global_debugger


def set_global_debugger(debugger: UIDebugger):
    """Set the global debugger instance"""
    global _global_debugger
    _global_debugger = debugger


def create_debugger(enabled: bool = True, log_file: Optional[Path] = None) -> UIDebugger:
    """Create a new debugger instance"""
    return UIDebugger(enabled=enabled, log_file=log_file)


def cleanup_global_debugger():
    """Cleanup the global debugger instance"""
    global _global_debugger
    if _global_debugger:
        print("[UI DEBUG] Cleaning up global debugger...")
        _global_debugger.cleanup()
        _global_debugger = None
        print("[UI DEBUG] Global debugger cleaned up")
