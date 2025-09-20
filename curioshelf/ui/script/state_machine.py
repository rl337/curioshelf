"""
State machine for CurioScript runtime

This module provides a state machine that manages local variables, stack operations,
and execution context for the scripting language.
"""

from typing import Any, Dict, List, Optional, Callable
from dataclasses import dataclass
import traceback


@dataclass
class StackFrame:
    """Represents a stack frame with local variables"""
    variables: Dict[str, Any]
    return_value: Any = None
    parent_frame: Optional['StackFrame'] = None


class StateMachine:
    """State machine for script execution"""
    
    def __init__(self):
        """Initialize the state machine"""
        self._stack: List[StackFrame] = []
        self._current_frame: Optional[StackFrame] = None
        self._global_variables: Dict[str, Any] = {}
        self._runnables: Dict[str, Callable] = {}
        self._execution_context: Optional[Any] = None
        self._error_handler: Optional[Callable] = None
        
        # Initialize with empty frame
        self._push_frame()
    
    def _push_frame(self) -> None:
        """Push a new stack frame"""
        parent = self._current_frame
        frame = StackFrame(variables={}, parent_frame=parent)
        self._stack.append(frame)
        self._current_frame = frame
    
    def _pop_frame(self) -> Optional[StackFrame]:
        """Pop the current stack frame"""
        if len(self._stack) <= 1:  # Keep at least one frame
            return None
        
        frame = self._stack.pop()
        self._current_frame = self._stack[-1] if self._stack else None
        return frame
    
    def set_variable(self, name: str, value: Any) -> None:
        """Set a variable in the current frame"""
        if self._current_frame:
            self._current_frame.variables[name] = value
        else:
            self._global_variables[name] = value
    
    def get_variable(self, name: str) -> Any:
        """Get a variable from the current frame or parent frames"""
        # Check current frame
        if self._current_frame and name in self._current_frame.variables:
            return self._current_frame.variables[name]
        
        # Check parent frames
        frame = self._current_frame
        while frame and frame.parent_frame:
            frame = frame.parent_frame
            if name in frame.variables:
                return frame.variables[name]
        
        # Check global variables
        if name in self._global_variables:
            return self._global_variables[name]
        
        # Check runnables
        if name in self._runnables:
            runnable = self._runnables[name]
            try:
                return runnable()
            except Exception as e:
                if self._error_handler:
                    self._error_handler(f"Error executing runnable '{name}': {e}")
                else:
                    raise
        
        raise NameError(f"Variable '{name}' not found")
    
    def has_variable(self, name: str) -> bool:
        """Check if a variable exists"""
        try:
            self.get_variable(name)
            return True
        except NameError:
            return False
    
    def push_value(self, value: Any) -> None:
        """Push a value onto the stack"""
        if self._current_frame:
            # Use a special variable name for stack values
            stack_var = f"__stack_{len(self._current_frame.variables)}"
            self._current_frame.variables[stack_var] = value
    
    def pop_value(self, variable_name: str = None) -> Any:
        """Pop a value from the stack"""
        if not self._current_frame:
            raise RuntimeError("No active stack frame")
        
        if variable_name:
            # Pop specific variable
            if variable_name in self._current_frame.variables:
                value = self._current_frame.variables.pop(variable_name)
                return value
            else:
                raise NameError(f"Variable '{variable_name}' not found in current frame")
        else:
            # Pop last stack value
            stack_vars = [k for k in self._current_frame.variables.keys() if k.startswith("__stack_")]
            if stack_vars:
                last_var = max(stack_vars, key=lambda k: int(k.split("_")[-1]))
                value = self._current_frame.variables.pop(last_var)
                return value
            else:
                raise RuntimeError("Stack is empty")
    
    def register_runnable(self, name: str, runnable: Callable) -> None:
        """Register a runnable that can be called from the script"""
        self._runnables[name] = runnable
    
    def unregister_runnable(self, name: str) -> None:
        """Unregister a runnable"""
        if name in self._runnables:
            del self._runnables[name]
    
    def set_execution_context(self, context: Any) -> None:
        """Set the execution context (e.g., application interface)"""
        self._execution_context = context
    
    def get_execution_context(self) -> Any:
        """Get the execution context"""
        return self._execution_context
    
    def set_error_handler(self, handler: Callable[[str], None]) -> None:
        """Set the error handler for runnable execution"""
        self._error_handler = handler
    
    def get_all_variables(self) -> Dict[str, Any]:
        """Get all variables from current frame and parents"""
        variables = {}
        
        # Add global variables
        variables.update(self._global_variables)
        
        # Add variables from all frames (current frame takes precedence)
        frame = self._current_frame
        while frame:
            variables.update(frame.variables)
            frame = frame.parent_frame
        
        return variables
    
    def clear_variables(self) -> None:
        """Clear all variables except runnables"""
        self._global_variables.clear()
        if self._current_frame:
            self._current_frame.variables.clear()
    
    def get_stack_depth(self) -> int:
        """Get the current stack depth"""
        return len(self._stack)
    
    def get_frame_info(self) -> List[Dict[str, Any]]:
        """Get information about all stack frames"""
        frames = []
        for i, frame in enumerate(self._stack):
            frames.append({
                'index': i,
                'variables': frame.variables.copy(),
                'return_value': frame.return_value,
                'is_current': frame == self._current_frame
            })
        return frames
    
    def execute_in_new_frame(self, func: Callable, *args, **kwargs) -> Any:
        """Execute a function in a new stack frame"""
        self._push_frame()
        try:
            result = func(*args, **kwargs)
            return result
        finally:
            self._pop_frame()
    
    def debug_info(self) -> Dict[str, Any]:
        """Get debug information about the state machine"""
        return {
            'stack_depth': self.get_stack_depth(),
            'current_frame_variables': self._current_frame.variables.copy() if self._current_frame else {},
            'global_variables': self._global_variables.copy(),
            'runnables': list(self._runnables.keys()),
            'execution_context': type(self._execution_context).__name__ if self._execution_context else None
        }
