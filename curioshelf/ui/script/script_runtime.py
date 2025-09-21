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
from .recursive_descent_parser import RecursiveDescentParser


class BudgetExceededError(Exception):
    """Raised when the execution budget is exceeded"""
    def __init__(self, budget_used: int, budget_limit: int, operation: str = None):
        self.budget_used = budget_used
        self.budget_limit = budget_limit
        self.operation = operation
        super().__init__(f"Execution budget exceeded: used {budget_used}/{budget_limit}" + 
                        (f" during {operation}" if operation else ""))


class ScriptRuntime:
    """Runtime for executing CurioScript programs"""
    
    def __init__(self, application_interface: Any = None, verbose: bool = True, execution_budget: int = 1000):
        """Initialize the script runtime
        
        Args:
            application_interface: The application interface for command execution
            verbose: Whether to print verbose output
            execution_budget: Maximum execution cost before raising BudgetExceededError
        """
        self.verbose = verbose
        self.execution_budget = execution_budget
        self.state_machine = StateMachine()
        self.command_reflector = create_command_reflector(application_interface)
        self.operators = get_operators()
        self.functions = get_functions()
        
        # Initialize budget system first
        self.current_budget = self.execution_budget
        self.command_costs = {
            # Basic operations
            'assignment': 1,
            'variable_access': 1,
            'arithmetic': 2,
            'comparison': 2,
            'logical': 2,
            'function_call': 5,
            'command_call': 10,
            
            # Control structures
            'if_statement': 3,
            'foreach_loop': 5,
            'block': 1,
            
            # Parsing operations (reduced costs for complex scripts)
            'parse_expression': 0,  # Free for basic expressions
            'parse_dictionary': 2,  # Reduced cost
            'parse_function_call': 1,  # Reduced cost
            'parse_statement': 0,  # Free for basic statements
        }
        
        # Initialize parser with budget checker
        self.parser = RecursiveDescentParser(budget_checker=self._check_budget)
        
        # Enable auto-responder for scripted testing
        self._setup_auto_responder(application_interface)
        
        # Debug: Print available functions
        if self.verbose:
            print(f"[SCRIPT RUNTIME DEBUG] Available functions: {list(self.functions.keys())}")
    
    def _setup_auto_responder(self, application_interface: Any):
        """Setup auto-responder for dialogs during scripted testing"""
        try:
            from test_support.test_plugin_loader import get_dialog_responder, get_heartbeat_monitor
            import tempfile
            
            # Get auto-responder from plugin system
            self.auto_responder = get_dialog_responder()
            if self.auto_responder:
                self.auto_responder.enabled = True
                
                # Configure project creation response
                self.auto_responder.set_response_config("project_dialog", "create", {
                    "project_name": "Script Test Project",
                    "project_path": str(Path(tempfile.gettempdir()) / "curioshelf_script_test"),
                    "action": "create"
                })
                
                # Configure project opening response (cancel by default)
                self.auto_responder.set_response_config("project_dialog", "open", {
                    "action": "cancel"
                })
                
                if self.verbose:
                    print("[SCRIPT RUNTIME] Auto-responder enabled from plugin system")
            else:
                if self.verbose:
                    print("[SCRIPT RUNTIME] Auto-responder not available from plugin system")
            
            # Modal detection is now handled by the heartbeat plugin
            self.modal_detector = None  # No longer needed as separate component
                
        except ImportError as e:
            if self.verbose:
                print(f"[SCRIPT RUNTIME] Auto-responder not available: {e}")
        except Exception as e:
            if self.verbose:
                print(f"[SCRIPT RUNTIME] Error setting up auto-responder: {e}")
    
    def _handle_unexpected_modal(self, dialog_type: str, dialog_info: str):
        """Handle unexpected modal dialogs by raising an assertion error"""
        error_msg = f"Unexpected modal dialog detected: {dialog_type} - {dialog_info}"
        print(f"[SCRIPT RUNTIME ERROR] {error_msg}")
        raise AssertionError(error_msg)
    
    def _handle_focus_change(self, change_type: str, window_info: Dict[str, Any]):
        """Handle focus changes to unexpected windows"""
        if change_type == "unexpected_focus":
            # Format window information for debugging
            info_lines = [
                f"Focus changed to unexpected window:",
                f"  Title: {window_info.get('title', 'Unknown')}",
                f"  Type: {window_info.get('type', 'Unknown')}",
                f"  Class: {window_info.get('class_name', 'Unknown')}",
                f"  Visible: {window_info.get('visible', False)}",
                f"  Modal: {window_info.get('modal', False)}",
                f"  Is Dialog: {window_info.get('is_dialog', False)}",
                f"  Is File Dialog: {window_info.get('is_file_dialog', False)}",
                f"  Is Message Box: {window_info.get('is_message_box', False)}",
                f"  Object Name: {window_info.get('object_name', 'None')}",
                f"  Parent: {window_info.get('parent', 'None')}",
            ]
            
            if window_info.get('geometry'):
                info_lines.append(f"  Geometry: {window_info['geometry']}")
            
            debug_info = "\n".join(info_lines)
            print(f"[SCRIPT RUNTIME DEBUG] {debug_info}")
            
            # Raise assertion error with detailed information
            error_msg = f"Unexpected focus change detected:\n{debug_info}"
            raise AssertionError(error_msg)
        
        
        # Set up error handling
        self.state_machine.set_error_handler(self._handle_error)
        self.state_machine.set_execution_context(application_interface)
        
        # Connect budget system to command reflector
        self.command_reflector.set_budget_system(self)
    
    def _consume_budget(self, cost: int, operation: str = None) -> None:
        """Consume execution budget and raise error if exceeded
        
        Args:
            cost: The cost to consume
            operation: Optional operation name for error reporting
        """
        if self.current_budget < cost:
            raise BudgetExceededError(
                self.execution_budget - self.current_budget + cost,
                self.execution_budget,
                operation
            )
        self.current_budget -= cost
    
    def _check_budget(self, operation: str) -> None:
        """Check budget for a parsing operation"""
        cost = self.command_costs.get(operation, 1)
        self._consume_budget(cost, operation)
    
    def reset_budget(self) -> None:
        """Reset the execution budget to its initial value"""
        self.current_budget = self.execution_budget
    
    def get_remaining_budget(self) -> int:
        """Get the remaining execution budget"""
        return self.current_budget
    
    def get_budget_usage(self) -> Dict[str, int]:
        """Get budget usage information"""
        return {
            'total_budget': self.execution_budget,
            'remaining_budget': self.current_budget,
            'used_budget': self.execution_budget - self.current_budget,
            'usage_percentage': ((self.execution_budget - self.current_budget) / self.execution_budget) * 100
        }
        
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
            # Check if it's a parsed node (has 'type' field) or a direct dictionary value
            if 'type' in expression:
                # Expression node from ANTLR
                return self._evaluate_node(expression)
            else:
                # Direct dictionary value (e.g., {"name": "value"})
                return expression
        elif isinstance(expression, list):
            # Direct list value
            return expression
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
            self._consume_budget(self.command_costs['variable_access'], 'variable_access')
            return self.state_machine.get_variable(node['value'])
        elif node_type == 'BINARY_OPERATION':
            self._consume_budget(self.command_costs['arithmetic'], 'binary_operation')
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
                print(f"[SCRIPT DEBUG] Calling function: {func_name} with args: {args}")
                self._consume_budget(self.command_costs['function_call'], f'function_{func_name}')
                func = self.functions[func_name]['function']
                
                # Handle special functions that need runtime context
                if func_name == 'trigger_menu':
                    print(f"[SCRIPT DEBUG] Using special handler for trigger_menu")
                    return self._handle_trigger_menu(*args)
                elif func_name == 'exit':
                    print(f"[SCRIPT DEBUG] Using special handler for exit")
                    return self._handle_exit(*args)
                elif func_name == 'get_project_structure':
                    print(f"[SCRIPT DEBUG] Using special handler for get_project_structure")
                    return self._handle_get_project_structure(*args)
                else:
                    print(f"[SCRIPT DEBUG] Using regular function handler for {func_name}")
                    return func(*args)
            # Check if it's a command
            elif self.command_reflector.get_command(func_name):
                self._consume_budget(self.command_costs['command_call'], f'command_{func_name}')
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
        elif node_type == 'dictionary_access':
            # Handle dictionary access like obj["key"]
            obj = self._evaluate_expression(node['object'])
            key = self._evaluate_expression(node['key'])
            if isinstance(obj, dict):
                return obj.get(key)
            else:
                raise TypeError(f"Cannot access key '{key}' on non-dictionary object: {type(obj)}")
        elif node_type == 'comparison':
            # Handle comparison expressions
            left = self._evaluate_expression(node['left'])
            right = self._evaluate_expression(node['right'])
            operator = node['operator']
            
            if operator == '=' or operator == '==':
                return left == right
            elif operator == '!=':
                return left != right
            elif operator == '<':
                return left < right
            elif operator == '>':
                return left > right
            elif operator == '<=':
                return left <= right
            elif operator == '>=':
                return left >= right
            else:
                raise ValueError(f"Unknown comparison operator: {operator}")
        elif node_type == 'logical_and':
            # Handle logical AND
            left = self._evaluate_expression(node['left'])
            right = self._evaluate_expression(node['right'])
            return bool(left) and bool(right)
        elif node_type == 'logical_or':
            # Handle logical OR
            left = self._evaluate_expression(node['left'])
            right = self._evaluate_expression(node['right'])
            return bool(left) or bool(right)
        elif node_type == 'logical_not':
            # Handle logical NOT
            operand = self._evaluate_expression(node['operand'])
            return not bool(operand)
        elif node_type == 'dict_access':
            # Handle dictionary access (variable["key"])
            variable = self._evaluate_expression(node['variable'])
            key = self._evaluate_expression(node['key'])
            
            if isinstance(variable, dict):
                return variable.get(key)
            else:
                raise TypeError(f"Expected dictionary for access, got {type(variable)}")
        elif node_type == 'arithmetic':
            # Handle arithmetic operations
            left = self._evaluate_expression(node['left'])
            right = self._evaluate_expression(node['right'])
            operator = node['operator']
            
            if operator == '+':
                return left + right
            elif operator == '-':
                return left - right
            elif operator == '*':
                return left * right
            elif operator == '/':
                if right == 0:
                    raise ZeroDivisionError("Division by zero")
                return left / right
            else:
                raise ValueError(f"Unknown arithmetic operator: {operator}")
        else:
            raise ValueError(f"Unknown node type: {node_type}")
    
    def execute_statement(self, statement: Any) -> Any:
        """Execute a statement"""
        statement_type = statement.get('type') if isinstance(statement, dict) else 'expression'
        
        if statement_type == 'assignment':
            self._consume_budget(self.command_costs['assignment'], 'assignment')
            var_name = statement['variable']
            value = self._evaluate_expression(statement['value'])
            self.state_machine.set_variable(var_name, value)
            return value
        elif statement_type == 'command':
            self._consume_budget(self.command_costs['command_call'], f'command_{statement["name"]}')
            cmd_name = statement['name']
            args = [self._evaluate_expression(arg) for arg in statement.get('args', [])]
            
            print(f"[SCRIPT DEBUG] Executing command: {cmd_name} with args: {args}")
            
            # First try to execute as a command
            try:
                print(f"[SCRIPT DEBUG] Trying to execute as command: {cmd_name}")
                return self.command_reflector.execute_command(cmd_name, *args)
            except NameError:
                print(f"[SCRIPT DEBUG] Command not found, trying as function: {cmd_name}")
                # If not found as command, try as function
                if cmd_name in self.functions:
                    print(f"[SCRIPT DEBUG] Found as function: {cmd_name}")
                    func_info = self.functions[cmd_name]
                    func = func_info['function']
                    
                    # Handle special functions that need runtime context
                    if cmd_name == 'trigger_menu':
                        print(f"[SCRIPT DEBUG] Using special handler for trigger_menu")
                        return self._handle_trigger_menu(*args)
                    elif cmd_name == 'exit':
                        print(f"[SCRIPT DEBUG] Using special handler for exit")
                        return self._handle_exit(*args)
                    elif cmd_name == 'get_project_structure':
                        print(f"[SCRIPT DEBUG] Using special handler for get_project_structure")
                        return self._handle_get_project_structure(*args)
                    else:
                        print(f"[SCRIPT DEBUG] Using regular function handler for {cmd_name}")
                        return func(*args)
                else:
                    print(f"[SCRIPT DEBUG] Neither command nor function found: {cmd_name}")
                    raise NameError(f"Command or function '{cmd_name}' not found")
        elif statement_type == 'if':
            self._consume_budget(self.command_costs['if_statement'], 'if_statement')
            condition = self._evaluate_expression(statement['condition'])
            if condition:
                if 'then' in statement:
                    # Execute each statement in the then block
                    results = []
                    for then_stmt in statement['then']:
                        result = self.execute_statement(then_stmt)
                        results.append(result)
                    return results[-1] if results else None
                # If no 'then' block, just return the condition result
                return condition
            elif 'else' in statement:
                # Execute each statement in the else block
                results = []
                for else_stmt in statement['else']:
                    result = self.execute_statement(else_stmt)
                    results.append(result)
                return results[-1] if results else None
            else:
                return False
        elif statement_type == 'foreach':
            self._consume_budget(self.command_costs['foreach_loop'], 'foreach_loop')
            var_name = statement['variable']
            iterable = self._evaluate_expression(statement['iterable'])
            
            if not isinstance(iterable, (list, tuple)):
                raise TypeError(f"Expected iterable, got {type(iterable)}")
            
            results = []
            for item in iterable:
                # Consume budget for each iteration
                self._consume_budget(self.command_costs['foreach_loop'], 'foreach_loop_iteration')
                self.state_machine.set_variable(var_name, item)
                if 'body' in statement:
                    # Execute each statement in the body
                    for body_stmt in statement['body']:
                        result = self.execute_statement(body_stmt)
                        results.append(result)
                else:
                    # If no body, just set the variable and continue
                    results.append(item)
            
            return results
        # While loops are not supported - use foreach with range instead
        elif statement_type == 'push':
            value = self._evaluate_expression(statement['value'])
            self.state_machine.push_value(value)
            return value
        elif statement_type == 'pop':
            var_name = statement.get('variable')
            return self.state_machine.pop_value(var_name)
        elif statement_type == 'else':
            # Handle standalone else statements (should not happen in well-formed code)
            if self.verbose:
                print("[SCRIPT WARNING] Standalone else statement - this should be part of an if statement")
            return None
        elif statement_type == 'block':
            results = []
            for stmt in statement.get('statements', []):
                result = self.execute_statement(stmt)
                results.append(result)
            return results
        elif statement_type == 'expression':
            # Handle expression statements
            return self._evaluate_expression(statement['value'])
        else:
            # Treat as expression
            return self._evaluate_expression(statement)
    
    def execute_script_content(self, script_content: str, heartbeat=None) -> Any:
        """Execute a script from its content string with optional heartbeat monitoring"""
        if self.verbose:
            print(f"[SCRIPT RUNTIME] Executing script content...")
        
        try:
            # Reset budget at the start of script execution
            self.reset_budget()
            statements = self.parser.parse_script(script_content)
            
            # Store heartbeat for use during execution
            self.heartbeat = heartbeat
            
            result = self.execute_program(statements)
            
            if self.verbose:
                print(f"[SCRIPT RUNTIME] Script execution completed successfully")
            
            return result
            
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
        
        print(f"[SCRIPT DEBUG] Executing program with {len(statements)} statements")
        results = []
        for i, statement in enumerate(statements):
            print(f"[SCRIPT DEBUG] Executing statement {i}: {statement}")
            # Update heartbeat activity for each statement
            if self.heartbeat:
                self.heartbeat.update_activity()
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
        
        # Commands by category
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
    
    def _handle_trigger_menu(self, menu_name: str, item_name: str) -> None:
        """Handle trigger_menu function calls"""
        print(f"[SCRIPT DEBUG] Triggering menu: {menu_name} -> {item_name}")
        
        # Emit a menu click event through the event system
        from curioshelf.event_system import event_bus, UIEvent, EventType
        
        # Map menu items to command names
        menu_item_mapping = {
            "Project": {
                "New Project": "new_project",
                "Open Project": "open_project",
                "Save Project": "save_project",
                "Close Project": "close_project"
            },
            "Sources": {
                "Import Source": "import_source"
            },
            "Objects": {
                "Create Object": "create_object"
            },
            "Templates": {
                "Create Template": "create_template"
            }
        }
        
        # Get the command name from the mapping
        command_name = menu_item_mapping.get(menu_name, {}).get(item_name, f"{menu_name.lower()}_{item_name.lower().replace(' ', '_')}")
        
        event = UIEvent(
            event_type=EventType.MENU_ITEM_CLICKED,
            source="script",
            data={
                "menu_item": command_name,
                "menu_name": f"{menu_name} -> {item_name}",
                "menu": menu_name,
                "item": item_name
            }
        )
        print(f"[SCRIPT DEBUG] Emitting MENU_ITEM_CLICKED event: {event.data}")
        event_bus.emit(event)
        print(f"[SCRIPT DEBUG] Menu event emitted successfully")
    
    def _handle_exit(self, exit_code: int = 0) -> None:
        """Handle exit function calls"""
        if self.verbose:
            print(f"[SCRIPT] Exiting application with code: {exit_code}")
        
        # Set a flag to indicate the script wants to exit
        self.state_machine.set_variable("_script_exit_requested", True)
        self.state_machine.set_variable("_script_exit_code", exit_code)
        
        if self.verbose:
            print(f"[SCRIPT] Exit requested with code: {exit_code}")
    
    def _handle_get_project_structure(self) -> dict:
        """Handle get_project_structure function calls"""
        if self.verbose:
            print(f"[SCRIPT] Getting project structure...")
        try:
            # Get the application interface from the state machine context
            app_interface = self.state_machine.get_execution_context()
            if app_interface and hasattr(app_interface, 'get_project_structure'):
                structure = app_interface.get_project_structure()
                if self.verbose:
                    print(f"[SCRIPT] Project structure retrieved: {structure}")
                return structure
            else:
                if self.verbose:
                    print(f"[SCRIPT] No application interface available for project structure")
                return {}
        except Exception as e:
            if self.verbose:
                print(f"[SCRIPT] Error getting project structure: {e}")
            return {}
