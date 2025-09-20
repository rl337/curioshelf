"""
Simple parser for CurioScript

This module provides a basic parser for CurioScript that can handle
the essential syntax without requiring ANTLR. This is a temporary
solution until the full ANTLR integration is complete.
"""

import re
import json
from typing import Any, Dict, List, Optional, Union
from pathlib import Path


class SimpleCurioParser:
    """Simple parser for CurioScript syntax"""
    
    def __init__(self):
        """Initialize the parser"""
        self._line_number = 0
        self._current_line = ""
    
    def parse_script(self, script_content: str) -> List[Dict[str, Any]]:
        """Parse a script into a list of statements"""
        statements = []
        lines = script_content.split('\n')
        
        i = 0
        while i < len(lines):
            line_num = i + 1
            line = lines[i].strip()
            
            # Skip empty lines and comments
            if not line or line.startswith('#'):
                i += 1
                continue
            
            # Check for multi-line structures
            if line.endswith('=') and i + 1 < len(lines):
                # This might be a multi-line assignment
                next_line = lines[i + 1].strip()
                if next_line.startswith('{'):
                    # Multi-line dictionary assignment
                    statement = self._parse_multiline_assignment(lines, i)
                    if statement:
                        statements.append(statement)
                    # Skip the lines we processed
                    i = self._find_matching_brace(lines, i + 1) + 1
                    continue
            
            try:
                statement = self._parse_line(line)
                if statement:
                    statements.append(statement)
            except Exception as e:
                print(f"Parse error at line {line_num}: {e}")
                print(f"  Line: {line}")
            
            i += 1
        
        return statements
    
    def _parse_line(self, line: str) -> Optional[Dict[str, Any]]:
        """Parse a single line into a statement"""
        # Assignment: variable = value
        if '=' in line and not self._is_inside_string(line, line.find('=')):
            return self._parse_assignment(line)
        
        # Function/command call: name(args)
        elif '(' in line and ')' in line:
            return self._parse_function_call(line)
        
        # Print statement: print(...)
        elif line.startswith('print('):
            return self._parse_print_statement(line)
        
        # If statement: if (condition) statement
        elif line.startswith('if '):
            return self._parse_if_statement(line)
        
        # Foreach statement: foreach (var in list) statement
        elif line.startswith('foreach '):
            return self._parse_foreach_statement(line)
        
        # While statement: while (condition) statement
        elif line.startswith('while '):
            return self._parse_while_statement(line)
        
        # Push statement: push value
        elif line.startswith('push '):
            return self._parse_push_statement(line)
        
        # Pop statement: pop [variable]
        elif line.startswith('pop'):
            return self._parse_pop_statement(line)
        
        # Block start/end
        elif line == '{':
            return {'type': 'block_start'}
        elif line == '}':
            return {'type': 'block_end'}
        
        # Else statement
        elif line == 'else:':
            return {'type': 'else'}
        
        else:
            # Try to parse as expression
            return self._parse_expression(line)
    
    def _parse_assignment(self, line: str) -> Dict[str, Any]:
        """Parse an assignment statement"""
        equals_pos = line.find('=')
        var_name = line[:equals_pos].strip()
        value_expr = line[equals_pos + 1:].strip()
        
        return {
            'type': 'assignment',
            'variable': var_name,
            'value': self._parse_expression(value_expr)
        }
    
    def _parse_function_call(self, line: str) -> Dict[str, Any]:
        """Parse a function or command call"""
        # Find the opening parenthesis
        paren_pos = line.find('(')
        func_name = line[:paren_pos].strip()
        
        # Extract arguments
        args_start = paren_pos + 1
        args_end = line.rfind(')')
        args_str = line[args_start:args_end].strip()
        
        args = []
        if args_str:
            args = self._parse_argument_list(args_str)
        
        return {
            'type': 'function_call',
            'name': func_name,
            'args': args
        }
    
    def _parse_print_statement(self, line: str) -> Dict[str, Any]:
        """Parse a print statement"""
        # Extract the content inside print(...)
        start = line.find('(') + 1
        end = line.rfind(')')
        content = line[start:end].strip()
        
        # Parse the content as arguments
        args = self._parse_argument_list(content)
        
        return {
            'type': 'function_call',
            'name': 'print',
            'args': args
        }
    
    def _parse_if_statement(self, line: str) -> Dict[str, Any]:
        """Parse an if statement"""
        # Extract condition from if (condition)
        start = line.find('(') + 1
        end = line.find(')')
        condition = line[start:end].strip()
        
        return {
            'type': 'if',
            'condition': self._parse_expression(condition)
        }
    
    def _parse_foreach_statement(self, line: str) -> Dict[str, Any]:
        """Parse a foreach statement"""
        # Extract var and list from foreach (var in list)
        start = line.find('(') + 1
        end = line.find(')')
        content = line[start:end].strip()
        
        # Split by ' in '
        parts = content.split(' in ')
        if len(parts) != 2:
            raise ValueError("Invalid foreach syntax")
        
        var_name = parts[0].strip()
        list_expr = parts[1].strip()
        
        return {
            'type': 'foreach',
            'variable': var_name,
            'iterable': self._parse_expression(list_expr)
        }
    
    def _parse_while_statement(self, line: str) -> Dict[str, Any]:
        """Parse a while statement"""
        # Extract condition from while (condition)
        start = line.find('(') + 1
        end = line.find(')')
        condition = line[start:end].strip()
        
        return {
            'type': 'while',
            'condition': self._parse_expression(condition)
        }
    
    def _parse_push_statement(self, line: str) -> Dict[str, Any]:
        """Parse a push statement"""
        value = line[5:].strip()  # Remove 'push '
        return {
            'type': 'push',
            'value': self._parse_expression(value)
        }
    
    def _parse_pop_statement(self, line: str) -> Dict[str, Any]:
        """Parse a pop statement"""
        if line == 'pop':
            return {'type': 'pop'}
        else:
            var_name = line[4:].strip()  # Remove 'pop '
            return {
                'type': 'pop',
                'variable': var_name
            }
    
    def _parse_argument_list(self, args_str: str) -> List[Any]:
        """Parse a comma-separated argument list"""
        if not args_str:
            return []
        
        args = []
        current_arg = ""
        paren_depth = 0
        bracket_depth = 0
        in_string = False
        string_char = None
        
        i = 0
        while i < len(args_str):
            char = args_str[i]
            
            if not in_string:
                if char in ['"', "'"]:
                    in_string = True
                    string_char = char
                elif char == '(':
                    paren_depth += 1
                elif char == ')':
                    paren_depth -= 1
                elif char == '[':
                    bracket_depth += 1
                elif char == ']':
                    bracket_depth -= 1
                elif char == ',' and paren_depth == 0 and bracket_depth == 0:
                    args.append(self._parse_expression(current_arg.strip()))
                    current_arg = ""
                    i += 1
                    continue
            else:
                if char == string_char and (i == 0 or args_str[i-1] != '\\'):
                    in_string = False
                    string_char = None
            
            current_arg += char
            i += 1
        
        if current_arg.strip():
            args.append(self._parse_expression(current_arg.strip()))
        
        return args
    
    def _parse_expression(self, expr: str) -> Any:
        """Parse an expression"""
        expr = expr.strip()
        
        # String literal
        if (expr.startswith('"') and expr.endswith('"')) or (expr.startswith("'") and expr.endswith("'")):
            return expr[1:-1]  # Remove quotes
        
        # Number literal
        try:
            if '.' in expr:
                return float(expr)
            else:
                return int(expr)
        except ValueError:
            pass
        
        # Boolean literal
        if expr.lower() in ['true', 'false']:
            return expr.lower() == 'true'
        
        # List literal
        if expr.startswith('[') and expr.endswith(']'):
            list_content = expr[1:-1].strip()
            if not list_content:
                return []
            return self._parse_argument_list(list_content)
        
        # Dictionary literal
        if expr.startswith('{') and expr.endswith('}'):
            # Simple dictionary parsing
            dict_content = expr[1:-1].strip()
            if not dict_content:
                return {}
            
            # This is a simplified dictionary parser
            # In a real implementation, this would be more robust
            try:
                return json.loads(expr)
            except:
                # Fallback to simple parsing
                return self._parse_simple_dict(dict_content)
        
        # Variable reference or function call
        if '(' in expr and ')' in expr:
            return self._parse_function_call(expr)
        else:
            # Variable reference
            return {
                'type': 'variable',
                'name': expr
            }
    
    def _parse_simple_dict(self, content: str) -> Dict[str, Any]:
        """Parse a simple dictionary literal"""
        # This is a very basic dictionary parser
        # In practice, you'd want something more robust
        result = {}
        
        # Split by commas, but be careful about nested structures
        parts = []
        current = ""
        depth = 0
        
        for char in content:
            if char in ['{', '[']:
                depth += 1
            elif char in ['}', ']']:
                depth -= 1
            elif char == ',' and depth == 0:
                parts.append(current.strip())
                current = ""
                continue
            current += char
        
        if current.strip():
            parts.append(current.strip())
        
        for part in parts:
            if ':' in part:
                key, value = part.split(':', 1)
                key = key.strip().strip('"\'')
                value = value.strip()
                result[key] = self._parse_expression(value)
        
        return result
    
    def _is_inside_string(self, line: str, pos: int) -> bool:
        """Check if a position is inside a string literal"""
        in_string = False
        string_char = None
        
        for i, char in enumerate(line[:pos]):
            if not in_string:
                if char in ['"', "'"]:
                    in_string = True
                    string_char = char
            else:
                if char == string_char and (i == 0 or line[i-1] != '\\'):
                    in_string = False
                    string_char = None
        
        return in_string
    
    def _parse_multiline_assignment(self, lines: List[str], start_idx: int) -> Optional[Dict[str, Any]]:
        """Parse a multi-line assignment (like dictionary)"""
        # Get the variable name from the first line
        first_line = lines[start_idx].strip()
        if not first_line.endswith('='):
            return None
        
        var_name = first_line[:-1].strip()
        
        # Find the matching closing brace
        end_idx = self._find_matching_brace(lines, start_idx + 1)
        if end_idx == -1:
            return None
        
        # Collect all lines between the braces
        dict_lines = []
        for i in range(start_idx + 1, end_idx + 1):
            dict_lines.append(lines[i].strip())
        
        # Join them and parse as a dictionary
        dict_content = ' '.join(dict_lines)
        
        return {
            'type': 'assignment',
            'variable': var_name,
            'value': self._parse_expression(dict_content)
        }
    
    def _find_matching_brace(self, lines: List[str], start_idx: int) -> int:
        """Find the matching closing brace for a dictionary or list"""
        brace_count = 0
        in_string = False
        string_char = None
        
        for i in range(start_idx, len(lines)):
            line = lines[i].strip()
            
            for char in line:
                if not in_string:
                    if char in ['"', "'"]:
                        in_string = True
                        string_char = char
                    elif char == '{':
                        brace_count += 1
                    elif char == '}':
                        brace_count -= 1
                        if brace_count == 0:
                            return i
                else:
                    if char == string_char and (char == line[0] or line[line.index(char)-1] != '\\'):
                        in_string = False
                        string_char = None
        
        return -1  # Not found
