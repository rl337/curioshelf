"""
Operators for CurioScript language

This module defines binary and unary operators that can be used in expressions.
Operators are decorated to specify their syntax symbols.
"""

from typing import Any, Callable
from functools import wraps


def binary_operator(symbol: str):
    """Decorator for binary operators"""
    def decorator(func: Callable[[Any, Any], Any]) -> Callable[[Any, Any], Any]:
        func._operator_symbol = symbol
        func._operator_type = 'binary'
        return func
    return decorator


def unary_operator(symbol: str):
    """Decorator for unary operators"""
    def decorator(func: Callable[[Any], Any]) -> Callable[[Any], Any]:
        func._operator_symbol = symbol
        func._operator_type = 'unary'
        return func
    return decorator


class Operators:
    """Collection of operators for the scripting language"""
    
    @staticmethod
    @binary_operator('+')
    def addition(left: Any, right: Any) -> Any:
        """Add two values"""
        try:
            # Try numeric addition first
            left_val = float(left)
            right_val = float(right)
            result = left_val + right_val
            
            # Return integer if both operands were integers and result is whole
            if (isinstance(left, int) and isinstance(right, int) and 
                result.is_integer()):
                return int(result)
            return result
        except (ValueError, TypeError):
            # Fall back to string concatenation
            return str(left) + str(right)
    
    @staticmethod
    @binary_operator('-')
    def subtraction(left: Any, right: Any) -> Any:
        """Subtract two values"""
        left_val = float(left)
        right_val = float(right)
        result = left_val - right_val
        
        # Return integer if both operands were integers and result is whole
        if (isinstance(left, int) and isinstance(right, int) and 
            result.is_integer()):
            return int(result)
        return result
    
    @staticmethod
    @binary_operator('*')
    def multiplication(left: Any, right: Any) -> Any:
        """Multiply two values"""
        # Handle string multiplication
        if isinstance(left, str) and isinstance(right, (int, float)):
            return left * int(right)
        elif isinstance(left, (int, float)) and isinstance(right, str):
            return int(left) * right
        
        # Handle numeric multiplication
        try:
            left_val = float(left)
            right_val = float(right)
            result = left_val * right_val
            
            # Return integer if both operands were integers and result is whole
            if (isinstance(left, int) and isinstance(right, int) and 
                result.is_integer()):
                return int(result)
            return result
        except (ValueError, TypeError):
            raise ValueError(f"Cannot multiply {type(left).__name__} and {type(right).__name__}")
    
    @staticmethod
    @binary_operator('/')
    def division(left: Any, right: Any) -> Any:
        """Divide two values"""
        right_val = float(right)
        if right_val == 0:
            raise ZeroDivisionError("Division by zero")
        return float(left) / right_val
    
    @staticmethod
    @binary_operator('%')
    def modulo(left: Any, right: Any) -> Any:
        """Modulo operation"""
        left_val = float(left)
        right_val = float(right)
        result = left_val % right_val
        
        # Return integer if both operands were integers and result is whole
        if (isinstance(left, int) and isinstance(right, int) and 
            result.is_integer()):
            return int(result)
        return result
    
    @staticmethod
    @binary_operator('==')
    def equality(left: Any, right: Any) -> bool:
        """Check if two values are equal"""
        return str(left) == str(right)
    
    @staticmethod
    @binary_operator('!=')
    def inequality(left: Any, right: Any) -> bool:
        """Check if two values are not equal"""
        return str(left) != str(right)
    
    @staticmethod
    @binary_operator('<')
    def less_than(left: Any, right: Any) -> bool:
        """Check if left value is less than right value"""
        try:
            return float(left) < float(right)
        except (ValueError, TypeError):
            return str(left) < str(right)
    
    @staticmethod
    @binary_operator('>')
    def greater_than(left: Any, right: Any) -> bool:
        """Check if left value is greater than right value"""
        try:
            return float(left) > float(right)
        except (ValueError, TypeError):
            return str(left) > str(right)
    
    @staticmethod
    @binary_operator('<=')
    def less_equal(left: Any, right: Any) -> bool:
        """Check if left value is less than or equal to right value"""
        try:
            return float(left) <= float(right)
        except (ValueError, TypeError):
            return str(left) <= str(right)
    
    @staticmethod
    @binary_operator('>=')
    def greater_equal(left: Any, right: Any) -> bool:
        """Check if left value is greater than or equal to right value"""
        try:
            return float(left) >= float(right)
        except (ValueError, TypeError):
            return str(left) >= str(right)
    
    @staticmethod
    @binary_operator('&&')
    def logical_and(left: Any, right: Any) -> bool:
        """Logical AND operation"""
        return bool(left) and bool(right)
    
    @staticmethod
    @binary_operator('||')
    def logical_or(left: Any, right: Any) -> bool:
        """Logical OR operation"""
        return bool(left) or bool(right)
    
    @staticmethod
    @unary_operator('!')
    def logical_not(value: Any) -> bool:
        """Logical NOT operation"""
        return not bool(value)
    
    @staticmethod
    @unary_operator('-')
    def negation(value: Any) -> Any:
        """Negate a value"""
        try:
            return -float(value)
        except (ValueError, TypeError):
            raise TypeError(f"Cannot negate non-numeric value: {value}")


def get_operators() -> dict:
    """Get all operators as a dictionary"""
    operators = {}
    
    for name in dir(Operators):
        if not name.startswith('_'):
            func = getattr(Operators, name)
            if hasattr(func, '_operator_symbol'):
                symbol = func._operator_symbol
                operator_type = func._operator_type
                operators[symbol] = {
                    'function': func,
                    'type': operator_type,
                    'name': name
                }
    
    return operators


def get_binary_operators() -> dict:
    """Get only binary operators"""
    return {symbol: info for symbol, info in get_operators().items() 
            if info['type'] == 'binary'}


def get_unary_operators() -> dict:
    """Get only unary operators"""
    return {symbol: info for symbol, info in get_operators().items() 
            if info['type'] == 'unary'}
