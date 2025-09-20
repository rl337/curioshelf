"""
Script runtime for CurioScript

This module provides the main runtime for executing CurioScript programs.
It integrates the state machine, reflection system, operators, and functions.
"""

import sys
import traceback
from typing import Any, Dict, List, Optional, Callable
from pathlib import Path

from .state_machine import StateMachine
from .reflection import CommandReflector, create_command_reflector
from .operators import get_operators, get_binary_operators, get_unary_operators
from .functions import get_functions, get_function_help
from .simple_parser import SimpleCurioParser


class ScriptRuntime:
    """Runtime for executing CurioScript programs"""
    
    def __init__(self, application_interface: Any = None, verbose: bool = True):
        """Initialize the script runtime"""
        self.verbose = verbose
        self.state_machine = StateMachine()
        self.command_reflector = create_command_reflector(application_interface)
        self.operators = get_operators()
        self.functions = get_functions()
        self.parser = SimpleCurioParser()
        
        # Set up error handling
        self.state_machine.set_error_handler(self._handle_error)
        self.state_machine.set_execution_context(application_interface)
        
        # Register built-in functions as runnables
        for name, func_info in self.functions.items():
            self.state_machine.register_runnable(name, func_info['function'])
    
    def _handle_error(self, error_msg: str) -> None:
        """Handle errors during script execution"""
        if self.verbose:
            print(f"[SCRIPT ERROR] {error_msg}")
    
    def execute_expression(self, expression: Any) -> Any:
        """Execute an expression and return its value"""
        # This would be implemented with the ANTLR visitor
        # For now, we'll implement a simple evaluator
        return self._evaluate_expression(expression)
    
    def _evaluate_expression(self, expression: Any) -> Any:
        """Evaluate an expression (placeholder for ANTLR visitor)"""
        # This is a simplified evaluator - in practice, this would be
        # implemented using ANTLR's visitor pattern
        if isinstance(expression, str):
            # String literal
            return expression.strip('"\'')
        elif isinstance(expression, (int, float)):
            # Number literal
            return expression
        elif isinstance(expression, bool):
            # Boolean literal
            return expression
        elif isinstance(expression, dict):
            # Expression node from ANTLR
            return self._evaluate_node(expression)
        else:
            return expression
    
    def _evaluate_node(self, node: Dict[str, Any]) -> Any:
        """Evaluate a parsed node (placeholder for ANTLR visitor)"""
        node_type = node.get('type')
        
        # Handle None node type (direct values)
        if node_type is None:
            # This might be a direct value (string, number, dict, list)
            if 'value' in node:
                return node['value']
            else:
                # Return the node itself if it's a direct value
                return node
        
        if node_type == 'IDENTIFIER':
            return self.state_machine.get_variable(node['value'])
        elif node_type == 'BINARY_OPERATION':
            left = self._evaluate_expression(node['left'])
            right = self._evaluate_expression(node['right'])
            operator = node['operator']
            
            if operator in self.operators:
                op_func = self.operators[operator]['function']
                return op_func(left, right)
            else:
                raise ValueError(f"Unknown operator: {operator}")
        elif node_type == 'UNARY_OPERATION':
            operand = self._evaluate_expression(node['operand'])
            operator = node['operator']
            
            if operator in self.operators:
                op_func = self.operators[operator]['function']
                return op_func(operand)
            else:
                raise ValueError(f"Unknown unary operator: {operator}")
        elif node_type == 'FUNCTION_CALL':
            func_name = node['name']
            args = [self._evaluate_expression(arg) for arg in node.get('args', [])]
            
            if func_name in self.functions:
                func = self.functions[func_name]['function']
                return func(*args)
            else:
                raise NameError(f"Unknown function: {func_name}")
        elif node_type == 'function_call':
            # Handle function calls from the simple parser
            func_name = node['name']
            args = [self._evaluate_expression(arg) for arg in node.get('args', [])]
            
            # Check if it's a built-in function
            if func_name in self.functions:
                func = self.functions[func_name]['function']
                return func(*args)
            # Check if it's a command
            elif self.command_reflector.get_command(func_name):
                return self.command_reflector.execute_command(func_name, *args)
            else:
                raise NameError(f"Unknown function or command: {func_name}")
        elif node_type == 'COMMAND_CALL':
            cmd_name = node['name']
            args = [self._evaluate_expression(arg) for arg in node.get('args', [])]
            
            return self.command_reflector.execute_command(cmd_name, *args)
        elif node_type == 'variable':
            # Handle variable references from the simple parser
            var_name = node['name']
            return self.state_machine.get_variable(var_name)
        else:
            raise ValueError(f"Unknown node type: {node_type}")
    
    def execute_statement(self, statement: Any) -> Any:
        """Execute a statement"""
        statement_type = statement.get('type') if isinstance(statement, dict) else 'expression'
        
        if statement_type == 'assignment':
            var_name = statement['variable']
            value = self._evaluate_expression(statement['value'])
            self.state_machine.set_variable(var_name, value)
            return value
        elif statement_type == 'command':
            cmd_name = statement['name']
            args = [self._evaluate_expression(arg) for arg in statement.get('args', [])]
            return self.command_reflector.execute_command(cmd_name, *args)
        elif statement_type == 'if':
            condition = self._evaluate_expression(statement['condition'])
            if condition:
                return self.execute_statement(statement['then'])
            elif 'else' in statement:
                return self.execute_statement(statement['else'])
        elif statement_type == 'foreach':
            var_name = statement['variable']
            iterable = self._evaluate_expression(statement['iterable'])
            
            if not isinstance(iterable, (list, tuple)):
                raise TypeError(f"Expected iterable, got {type(iterable)}")
            
            results = []
            for item in iterable:
                self.state_machine.set_variable(var_name, item)
                result = self.execute_statement(statement['body'])
                results.append(result)
            
            return results
        elif statement_type == 'push':
            value = self._evaluate_expression(statement['value'])
            self.state_machine.push_value(value)
            return value
        elif statement_type == 'pop':
            var_name = statement.get('variable')
            return self.state_machine.pop_value(var_name)
        elif statement_type == 'block':
            results = []
            for stmt in statement.get('statements', []):
                result = self.execute_statement(stmt)
                results.append(result)
            return results
        else:
            # Treat as expression
            return self._evaluate_expression(statement)
    
    def execute_script_content(self, script_content: str) -> Any:
        """Execute a script from its content string"""
        try:
            statements = self.parser.parse_script(script_content)
            return self.execute_program(statements)
        except Exception as e:
            if self.verbose:
                print(f"[SCRIPT ERROR] Failed to parse script: {e}")
                traceback.print_exc()
            raise
    
    def execute_program(self, program: Any) -> Any:
        """Execute a complete program"""
        if isinstance(program, dict) and program.get('type') == 'program':
            statements = program.get('statements', [])
        elif isinstance(program, list):
            statements = program
        else:
            statements = [program]
        
        results = []
        for statement in statements:
            try:
                result = self.execute_statement(statement)
                results.append(result)
            except Exception as e:
                if self.verbose:
                    print(f"[SCRIPT ERROR] {e}")
                    traceback.print_exc()
                raise
        
        return results[-1] if results else None
    
    def get_help(self) -> str:
        """Get comprehensive help for the scripting language"""
        help_text = "CurioScript Help\n"
        help_text += "=" * 50 + "\n\n"
        
        # Commands
        help_text += self.command_reflector.get_command_help()
        help_text += "\n"
        
        # Functions
        help_text += get_function_help()
        help_text += "\n"
        
        # Language syntax
        help_text += "Language Syntax:\n"
        help_text += "-" * 20 + "\n"
        help_text += "Variables: name = value\n"
        help_text += "Commands: command_name(arg1, arg2)\n"
        help_text += "Functions: function_name(arg1, arg2)\n"
        help_text += "If: if (condition) statement [else statement]\n"
        help_text += "Foreach: foreach (var in list) statement\n"
        help_text += "Push: push value\n"
        help_text += "Pop: pop [variable]\n"
        help_text += "Blocks: { statement1; statement2; }\n"
        
        return help_text
    
    def get_debug_info(self) -> Dict[str, Any]:
        """Get debug information about the runtime"""
        return {
            'state_machine': self.state_machine.debug_info(),
            'commands': list(self.command_reflector.get_all_commands().keys()),
            'functions': list(self.functions.keys()),
            'operators': list(self.operators.keys())
        }
    
    def clear_state(self) -> None:
        """Clear the runtime state"""
        self.state_machine.clear_variables()
    
    def set_application_interface(self, interface: Any) -> None:
        """Set the application interface"""
        self.state_machine.set_execution_context(interface)
        self.command_reflector = create_command_reflector(interface)
