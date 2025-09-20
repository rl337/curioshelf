"""
Reflection system for CurioScript

This module provides reflection capabilities to discover commands from the application
interface and make them available to the scripting language.
"""

import inspect
import time
import threading
from typing import Any, Dict, List, Callable, Optional, get_type_hints
from functools import wraps


def script_command(name: str = None, description: str = "", category: str = "general", discoverable: bool = True):
    """Decorator for script commands
    
    Args:
        name: Custom name for the command (defaults to function name)
        description: Custom description (defaults to docstring)
        category: Category for grouping commands
        discoverable: Whether this command should be discoverable by reflection
    """
    def decorator(func: Callable) -> Callable:
        func._script_name = name or func.__name__
        func._script_description = description or func.__doc__ or f"Call {func.__name__} method"
        func._script_category = category
        func._script_type = 'command'
        func._script_discoverable = discoverable
        return func
    return decorator


def script_discoverable(category: str = "application", description: str = ""):
    """Decorator to mark a method as discoverable for scripts
    
    Args:
        category: Category for grouping commands
        description: Custom description (defaults to docstring)
    """
    def decorator(func: Callable) -> Callable:
        func._script_discoverable = True
        func._script_category = category
        func._script_description = description or func.__doc__ or f"Call {func.__name__} method"
        return func
    return decorator


def script_hidden(func: Callable) -> Callable:
    """Decorator to mark a method as NOT discoverable for scripts"""
    func._script_discoverable = False
    return func


class CommandReflector:
    """Reflects commands from application interfaces"""
    
    def __init__(self):
        """Initialize the command reflector"""
        self._commands: Dict[str, Dict[str, Any]] = {}
        self._categories: Dict[str, List[str]] = {}
    
    def reflect_interface(self, interface: Any, prefix: str = "") -> None:
        """
        Reflect commands from an application interface
        
        Args:
            interface: The application interface to reflect
            prefix: Optional prefix for command names
        """
        if interface is None:
            return
        
        # Get all methods from the interface
        for name, method in inspect.getmembers(interface, predicate=inspect.ismethod):
            if name.startswith('_'):
                continue  # Skip private methods
            
            # Check if method should be discoverable
            # Default to True for backward compatibility, but check for explicit flags
            discoverable = True
            if hasattr(method, '_script_discoverable'):
                discoverable = method._script_discoverable
            elif hasattr(method, '_script_type') and method._script_type == 'command':
                # Commands are discoverable by default
                discoverable = True
            else:
                # For methods without explicit decorators, only discover if they're from the interface
                # This prevents internal implementation methods from being discovered
                discoverable = True  # Keep current behavior for now
            
            if not discoverable:
                continue  # Skip hidden methods
            
            # Check if it's a script command with decorator
            if hasattr(method, '_script_type') and method._script_type == 'command':
                command_name = method._script_name
                description = method._script_description
                category = method._script_category
            elif hasattr(method, '_script_discoverable') and method._script_discoverable:
                # Method marked as discoverable with decorator
                command_name = name
                description = method._script_description
                category = method._script_category
            else:
                # Auto-discover public methods as commands (default behavior)
                command_name = name
                description = method.__doc__ or f"Call {name} method"
                category = "application"
            
            if prefix:
                command_name = f"{prefix}_{command_name}"
            
            # Get method signature
            sig = inspect.signature(method)
            parameters = []
            for param_name, param in sig.parameters.items():
                if param_name == 'self':
                    continue
                
                param_info = {
                    'name': param_name,
                    'type': param.annotation if param.annotation != inspect.Parameter.empty else Any,
                    'default': param.default if param.default != inspect.Parameter.empty else None,
                    'required': param.default == inspect.Parameter.empty
                }
                parameters.append(param_info)
            
            # Store command information
            self._commands[command_name] = {
                'function': method,
                'description': description,
                'category': category,
                'parameters': parameters,
                'interface': interface
            }
            
            # Add to category
            if category not in self._categories:
                self._categories[category] = []
            if command_name not in self._categories[category]:
                self._categories[category].append(command_name)
    
    def get_command(self, name: str) -> Optional[Dict[str, Any]]:
        """Get command information by name"""
        return self._commands.get(name)
    
    def get_all_commands(self) -> Dict[str, Dict[str, Any]]:
        """Get all discovered commands"""
        return self._commands.copy()
    
    def get_commands_by_category(self, category: str) -> List[str]:
        """Get command names by category"""
        return self._categories.get(category, []).copy()
    
    def get_categories(self) -> List[str]:
        """Get all categories"""
        return list(self._categories.keys())
    
    def execute_command(self, name: str, *args, **kwargs) -> Any:
        """Execute a command by name with timeout-based budget consumption"""
        command_info = self.get_command(name)
        if not command_info:
            raise NameError(f"Command '{name}' not found")
        
        # Check if we have a budget system available
        budget_system = getattr(self, '_budget_system', None)
        
        if budget_system:
            return self._execute_with_timeout_budget(command_info['function'], name, args, kwargs, budget_system)
        else:
            # Fallback to direct execution if no budget system
            try:
                return command_info['function'](*args, **kwargs)
            except Exception as e:
                raise RuntimeError(f"Error executing command '{name}': {e}")
    
    def _execute_with_timeout_budget(self, func: Callable, name: str, args: tuple, kwargs: dict, budget_system) -> Any:
        """Execute a command with timeout-based budget consumption"""
        result = [None]
        exception = [None]
        start_time = time.time()
        
        def target():
            try:
                result[0] = func(*args, **kwargs)
            except Exception as e:
                exception[0] = e
        
        # Start the command in a separate thread
        thread = threading.Thread(target=target)
        thread.daemon = True
        thread.start()
        
        # Monitor execution time and consume budget
        while thread.is_alive():
            elapsed_time = time.time() - start_time
            if elapsed_time >= 1.0:  # Every second
                # Consume budget based on elapsed time
                cost = int(elapsed_time) * budget_system.command_costs.get('command_call', 10)
                try:
                    budget_system._consume_budget(cost, f'command_{name}_timeout')
                except Exception as budget_error:
                    # If budget exceeded, we can't stop the thread, but we can raise the error
                    raise budget_error
                start_time = time.time()  # Reset for next second
            
            time.sleep(0.1)  # Check every 100ms
        
        # Wait for thread to complete
        thread.join()
        
        if exception[0]:
            raise RuntimeError(f"Error executing command '{name}': {exception[0]}")
        
        return result[0]
    
    def set_budget_system(self, budget_system):
        """Set the budget system for timeout-based cost calculation"""
        self._budget_system = budget_system
    
    def get_command_help(self, name: str = None) -> str:
        """Get help text for commands"""
        if name:
            # Help for specific command
            command_info = self.get_command(name)
            if not command_info:
                return f"Command '{name}' not found"
            
            help_text = f"Command: {name}\n"
            help_text += f"Description: {command_info['description']}\n"
            help_text += f"Category: {command_info['category']}\n"
            help_text += "Parameters:\n"
            
            for param in command_info['parameters']:
                required = "required" if param['required'] else "optional"
                default = f" (default: {param['default']})" if param['default'] is not None else ""
                help_text += f"  {param['name']}: {param['type']} ({required}){default}\n"
            
            return help_text
        else:
            # Help for all commands
            help_text = "Available Commands:\n"
            help_text += "=" * 50 + "\n"
            
            for category in sorted(self.get_categories()):
                help_text += f"\n{category.title()}:\n"
                commands = self.get_commands_by_category(category)
                for cmd_name in sorted(commands):
                    cmd_info = self._commands[cmd_name]
                    help_text += f"  {cmd_name:<20} - {cmd_info['description']}\n"
            
            return help_text
    
    def get_command_signature(self, name: str) -> str:
        """Get the signature of a command"""
        command_info = self.get_command(name)
        if not command_info:
            return f"Command '{name}' not found"
        
        params = []
        for param in command_info['parameters']:
            if param['required']:
                params.append(param['name'])
            else:
                params.append(f"{param['name']}={param['default']}")
        
        return f"{name}({', '.join(params)})"
    
    def validate_command_call(self, name: str, args: List[Any], kwargs: Dict[str, Any]) -> bool:
        """Validate a command call before execution"""
        command_info = self.get_command(name)
        if not command_info:
            return False
        
        # Check required parameters
        required_params = [p['name'] for p in command_info['parameters'] if p['required']]
        provided_params = set(kwargs.keys())
        
        # Check if all required parameters are provided
        for param in required_params:
            if param not in provided_params and len(args) <= command_info['parameters'].index(
                next(p for p in command_info['parameters'] if p['name'] == param)
            ):
                return False
        
        return True


def create_command_reflector(application_interface: Any) -> CommandReflector:
    """Create a command reflector for an application interface"""
    reflector = CommandReflector()
    reflector.reflect_interface(application_interface)
    return reflector
