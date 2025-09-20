"""
Built-in functions for CurioScript language

This module defines built-in functions that can be called from the scripting language.
Functions are decorated to specify their metadata.
"""

from typing import Any, List, Callable
from functools import wraps


def script_function(name: str = None, description: str = ""):
    """Decorator for script functions"""
    def decorator(func: Callable) -> Callable:
        func._script_name = name or func.__name__
        func._script_description = description
        func._script_type = 'function'
        return func
    return decorator


class Functions:
    """Collection of built-in functions for the scripting language"""
    
    @staticmethod
    @script_function("len", "Get the length of a string or list")
    def length(value: Any) -> int:
        """Get the length of a string, list, or other sequence.
        
        Args:
            value: A string, list, tuple, or other sequence to measure
            
        Returns:
            int: The length of the value, or length of string representation if not a sequence
            
        Example:
            len("hello")  # Returns 5
            len([1, 2, 3])  # Returns 3
        """
        if isinstance(value, (str, list, tuple)):
            return len(value)
        else:
            return len(str(value))
    
    @staticmethod
    @script_function("upper", "Convert string to uppercase")
    def upper(value: Any) -> str:
        """Convert a value to uppercase string"""
        return str(value).upper()
    
    @staticmethod
    @script_function("lower", "Convert string to lowercase")
    def lower(value: Any) -> str:
        """Convert a value to lowercase string"""
        return str(value).lower()
    
    @staticmethod
    @script_function("trim", "Remove whitespace from string")
    def trim(value: Any) -> str:
        """Remove leading and trailing whitespace"""
        return str(value).strip()
    
    @staticmethod
    @script_function("substring", "Extract substring from string")
    def substring(value: Any, start: int, length: int = None) -> str:
        """Extract a substring"""
        s = str(value)
        if length is None:
            return s[start:]
        else:
            return s[start:start + length]
    
    @staticmethod
    @script_function("contains", "Check if string contains substring")
    def contains(value: Any, substring: Any) -> bool:
        """Check if a string contains a substring"""
        return str(substring) in str(value)
    
    @staticmethod
    @script_function("startsWith", "Check if string starts with prefix")
    def starts_with(value: Any, prefix: Any) -> bool:
        """Check if a string starts with a prefix"""
        return str(value).startswith(str(prefix))
    
    @staticmethod
    @script_function("endsWith", "Check if string ends with suffix")
    def ends_with(value: Any, suffix: Any) -> bool:
        """Check if a string ends with a suffix"""
        return str(value).endswith(str(suffix))
    
    @staticmethod
    @script_function("split", "Split string into list")
    def split(value: Any, delimiter: str = " ") -> List[str]:
        """Split a string into a list"""
        return str(value).split(str(delimiter))
    
    @staticmethod
    @script_function("join", "Join list into string")
    def join(values: List[Any], delimiter: str = " ") -> str:
        """Join a list of values into a string"""
        return str(delimiter).join(str(v) for v in values)
    
    @staticmethod
    @script_function("toNumber", "Convert value to number")
    def to_number(value: Any) -> float:
        """Convert a value to a number"""
        try:
            return float(value)
        except (ValueError, TypeError):
            raise ValueError(f"Cannot convert '{value}' to number")
    
    @staticmethod
    @script_function("toString", "Convert value to string")
    def to_string(value: Any) -> str:
        """Convert a value to a string"""
        return str(value)
    
    @staticmethod
    @script_function("isNumber", "Check if value is a number")
    def is_number(value: Any) -> bool:
        """Check if a value is a number"""
        try:
            float(value)
            return True
        except (ValueError, TypeError):
            return False
    
    @staticmethod
    @script_function("isString", "Check if value is a string")
    def is_string(value: Any) -> bool:
        """Check if a value is a string"""
        return isinstance(value, str)
    
    @staticmethod
    @script_function("isList", "Check if value is a list")
    def is_list(value: Any) -> bool:
        """Check if a value is a list"""
        return isinstance(value, (list, tuple))
    
    @staticmethod
    @script_function("isEmpty", "Check if value is empty")
    def is_empty(value: Any) -> bool:
        """Check if a value is empty"""
        if isinstance(value, (str, list, tuple)):
            return len(value) == 0
        else:
            return not bool(value)
    
    @staticmethod
    @script_function("print", "Print values to output")
    def print_value(*values: Any) -> None:
        """Print one or more values to the console output.
        
        Args:
            *values: One or more values to print. Can be strings, numbers, booleans, etc.
        
        Returns:
            None
            
        Example:
            print("Hello, world!")
            print("Value:", 42, "is", True)
        """
        if len(values) == 1:
            print(str(values[0]))
        else:
            # Join multiple values with spaces
            print(' '.join(str(v) for v in values))
    
    @staticmethod
    @script_function("assert", "Assert a condition and exit with error if false")
    def assert_condition(condition: Any, message: str = "Assertion failed") -> None:
        """Assert a condition and exit with error if false.
        
        Args:
            condition: The condition to test (will be converted to boolean)
            message: Optional error message to display if assertion fails
        
        Returns:
            None
            
        Raises:
            AssertionError: If the condition is false
            
        Example:
            assert(5 > 3, "Math is broken!")
            assert(is_project_loaded(), "Project should be loaded")
        """
        if not bool(condition):
            raise AssertionError(f"ASSERTION FAILED: {message}")
        # If we get here, the assertion passed
    
    @staticmethod
    @script_function("debug", "Print debug information")
    def debug(value: Any) -> None:
        """Print debug information (returns None)"""
        print(f"[DEBUG] {value}")
    
    @staticmethod
    @script_function("pop", "Pop a value from the stack")
    def pop_value() -> Any:
        """Pop a value from the stack and return it.
        
        Args:
            None
            
        Returns:
            Any: The value that was popped from the stack
            
        Example:
            value := pop()  # Pop and assign to variable
        """
        # This is a placeholder - in a real implementation, this would
        # interact with the state machine's stack
        return "stack_value"  # Placeholder return value


def get_functions() -> dict:
    """Get all functions as a dictionary"""
    functions = {}
    
    for name in dir(Functions):
        if not name.startswith('_'):
            func = getattr(Functions, name)
            if hasattr(func, '_script_name'):
                script_name = func._script_name
                functions[script_name] = {
                    'function': func,
                    'description': func._script_description,
                    'name': name
                }
    
    return functions


def get_function_help() -> str:
    """Get help text for all functions"""
    help_text = "Built-in Functions:\n"
    help_text += "=" * 50 + "\n"
    
    functions = get_functions()
    for name, info in sorted(functions.items()):
        help_text += f"{name:<15} - {info['description']}\n"
    
    return help_text
