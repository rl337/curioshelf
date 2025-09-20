"""
Simple parser for CurioScript

This module provides a basic parser for CurioScript that can handle
the essential syntax without requiring ANTLR. This is a temporary
solution until the full ANTLR integration is complete.
"""

import re
import json
from typing import Any, Dict, List, Optional, Tuple, Union
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
            if ':=' in line:
                # Check if this line starts a multi-line dictionary assignment
                if line.strip().endswith('{') or (i + 1 < len(lines) and lines[i + 1].strip().startswith('{')):
                    # Multi-line dictionary assignment
                    statement = self._parse_multiline_assignment(lines, i)
                    if statement:
                        statements.append(statement)
                    # Skip the lines we processed
                    if line.strip().endswith('{'):
                        # The { is on the same line, start looking from the next line
                        i = self._find_matching_brace(lines, i + 1) + 1
                    else:
                        # The { is on the next line
                        i = self._find_matching_brace(lines, i + 1) + 1
                    continue
            
            # Check for control structures that might have bodies
            if (line.startswith('while ') or line.startswith('if ') or 
                line.startswith('foreach ') or line.startswith('for ')):
                # Parse control structure with potential body
                statement, next_i = self._parse_control_structure_with_body(lines, i)
                if statement:
                    statements.append(statement)
                i = next_i
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
        # Remove inline comments (but not inside strings)
        line = self._remove_inline_comments(line)
        
        # Assignment: variable := value (Pascal-like syntax)
        if ':=' in line and not self._is_inside_string(line, line.find(':=')):
            return self._parse_assignment(line)
        
        # If statement: if (condition) statement
        elif line.startswith('if '):
            return self._parse_if_statement(line)
        
        # Foreach statement: foreach (var in list) statement
        elif line.startswith('foreach '):
            return self._parse_foreach_statement(line)
        
        # While statement: while (condition) statement
        elif line.startswith('while '):
            return self._parse_while_statement(line)
        
        # Push statement: push value or push(value)
        elif line.startswith('push '):
            return self._parse_push_statement(line)
        elif line.startswith('push('):
            return self._parse_push_statement(line)
        
        # Pop statement: pop [variable] or pop()
        elif line.startswith('pop'):
            return self._parse_pop_statement(line)
        
        # Print statement: print(...)
        elif line.startswith('print('):
            return self._parse_print_statement(line)
        
        # Function/command call: name(args)
        elif '(' in line and ')' in line:
            return self._parse_function_call(line)
        
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
        assign_pos = line.find(':=')
        var_name = line[:assign_pos].strip()
        value_expr = line[assign_pos + 2:].strip()
        
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
        # Remove 'if ' from the beginning
        condition_line = line[3:].strip()
        
        # Check if condition is in parentheses
        if condition_line.startswith('(') and condition_line.endswith(')'):
            # Extract condition from if (condition)
            condition = condition_line[1:-1].strip()
        else:
            # Extract condition from if condition: (remove trailing colon if present)
            condition = condition_line.rstrip(':').strip()
        
        return {
            'type': 'if',
            'condition': self._parse_expression(condition)
        }
    
    def _parse_foreach_statement(self, line: str) -> Dict[str, Any]:
        """Parse a foreach statement"""
        # Extract var and list from foreach (var in list)
        start = line.find('(') + 1
        
        # Find the matching closing parenthesis, handling nested parentheses
        paren_count = 0
        end = start
        for i, char in enumerate(line[start:], start):
            if char == '(':
                paren_count += 1
            elif char == ')':
                if paren_count == 0:
                    end = i
                    break
                paren_count -= 1
        
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
    
    def _parse_control_structure_with_body(self, lines: List[str], start_i: int) -> Tuple[Optional[Dict[str, Any]], int]:
        """Parse a control structure (while, if, foreach) with its body"""
        line = lines[start_i].strip()
        
        if line.startswith('while '):
            return self._parse_while_with_body(lines, start_i)
        elif line.startswith('if '):
            return self._parse_if_with_body(lines, start_i)
        elif line.startswith('foreach '):
            return self._parse_foreach_with_body(lines, start_i)
        else:
            # Fallback to single line parsing
            statement = self._parse_line(line)
            return statement, start_i + 1
    
    def _parse_while_with_body(self, lines: List[str], start_i: int) -> Tuple[Optional[Dict[str, Any]], int]:
        """Parse a while statement with its body"""
        line = lines[start_i].strip()
        condition_line = line[6:].strip()  # Remove 'while '
        
        # Check if condition is in parentheses
        if condition_line.startswith('(') and condition_line.endswith(')'):
            condition = condition_line[1:-1].strip()
        else:
            condition = condition_line.rstrip(':').strip()
        
        # Parse the body (indented lines following the while statement)
        body_statements = []
        i = start_i + 1
        
        # Determine base indentation from the while line
        base_indent = len(lines[start_i]) - len(lines[start_i].lstrip())
        
        while i < len(lines):
            current_line = lines[i]
            
            # Skip empty lines and comments
            if not current_line.strip() or current_line.strip().startswith('#'):
                i += 1
                continue
            
            # Check if this line is part of the while body (indented more than the while line)
            current_indent = len(current_line) - len(current_line.lstrip())
            
            if current_indent <= base_indent:
                # This line is not indented enough to be part of the while body
                break
            
            # Parse this line as a statement
            try:
                statement = self._parse_line(current_line.strip())
                if statement:
                    body_statements.append(statement)
            except Exception as e:
                print(f"Parse error in while body at line {i + 1}: {e}")
                print(f"  Line: {current_line}")
            
            i += 1
        
        return {
            'type': 'while',
            'condition': self._parse_expression(condition),
            'body': body_statements
        }, i
    
    def _parse_if_with_body(self, lines: List[str], start_i: int) -> Tuple[Optional[Dict[str, Any]], int]:
        """Parse an if statement with its body"""
        line = lines[start_i].strip()
        condition_line = line[3:].strip()  # Remove 'if '
        
        # Check if condition is in parentheses
        if condition_line.startswith('(') and condition_line.endswith(')'):
            condition = condition_line[1:-1].strip()
        else:
            condition = condition_line.rstrip(':').strip()
        
        # Parse the body (indented lines following the if statement)
        body_statements = []
        i = start_i + 1
        
        # Determine base indentation from the if line
        base_indent = len(lines[start_i]) - len(lines[start_i].lstrip())
        
        while i < len(lines):
            current_line = lines[i]
            
            # Skip empty lines and comments
            if not current_line.strip() or current_line.strip().startswith('#'):
                i += 1
                continue
            
            # Check if this line is part of the if body (indented more than the if line)
            current_indent = len(current_line) - len(current_line.lstrip())
            
            if current_indent <= base_indent:
                # This line is not indented enough to be part of the if body
                break
            
            # Parse this line as a statement
            try:
                statement = self._parse_line(current_line.strip())
                if statement:
                    body_statements.append(statement)
            except Exception as e:
                print(f"Parse error in if body at line {i + 1}: {e}")
                print(f"  Line: {current_line}")
            
            i += 1
        
        return {
            'type': 'if',
            'condition': self._parse_expression(condition),
            'then': body_statements
        }, i
    
    def _parse_foreach_with_body(self, lines: List[str], start_i: int) -> Tuple[Optional[Dict[str, Any]], int]:
        """Parse a foreach statement with its body"""
        line = lines[start_i].strip()
        foreach_line = line[8:].strip()  # Remove 'foreach '
        
        
        # Parse foreach (var in list) or foreach var in list:
        if foreach_line.startswith('(') and (foreach_line.endswith(')') or foreach_line.endswith('):')):
            # Remove the opening parenthesis and closing parenthesis/colon
            if foreach_line.endswith('):'):
                content = foreach_line[1:-2].strip()
            else:
                content = foreach_line[1:-1].strip()
        else:
            content = foreach_line.rstrip(':').strip()
        
        # Parse "var in list" pattern
        if ' in ' in content:
            var_name, iterable_expr = content.split(' in ', 1)
            var_name = var_name.strip()
            iterable_expr = iterable_expr.strip()
            
            # Clean up variable name (remove any leading/trailing parentheses)
            if var_name.startswith('('):
                var_name = var_name[1:].strip()
            if var_name.endswith(')'):
                var_name = var_name[:-1].strip()
            
            # For the iterable expression, only remove parentheses if they're from the foreach syntax
            # Don't remove parentheses that are part of function calls like range(inner_max)
            if iterable_expr.startswith('(') and iterable_expr.endswith(')') and not '(' in iterable_expr[1:-1]:
                # This is a simple parenthesized expression, remove the outer parentheses
                iterable_expr = iterable_expr[1:-1].strip()
            
            iterable = self._parse_expression(iterable_expr)
        else:
            raise ValueError(f"Invalid foreach syntax: {content}")
        
        # Parse the body (indented lines following the foreach statement)
        body_statements = []
        i = start_i + 1
        
        # Determine base indentation from the foreach line
        base_indent = len(lines[start_i]) - len(lines[start_i].lstrip())
        
        while i < len(lines):
            current_line = lines[i]
            
            # Skip empty lines and comments
            if not current_line.strip() or current_line.strip().startswith('#'):
                i += 1
                continue
            
            # Check if this line is part of the foreach body (indented more than the foreach line)
            current_indent = len(current_line) - len(current_line.lstrip())
            
            if current_indent <= base_indent:
                # This line is not indented enough to be part of the foreach body
                break
            
            # Parse this line as a statement
            try:
                statement = self._parse_line(current_line.strip())
                if statement:
                    body_statements.append(statement)
            except Exception as e:
                print(f"Parse error in foreach body at line {i + 1}: {e}")
                print(f"  Line: {current_line}")
            
            i += 1
        
        return {
            'type': 'foreach',
            'variable': var_name,
            'iterable': iterable,
            'body': body_statements
        }, i

    def _parse_while_statement(self, line: str) -> Dict[str, Any]:
        """Parse a while statement (single line, no body)"""
        # Remove 'while ' from the beginning
        condition_line = line[6:].strip()
        
        # Check if condition is in parentheses
        if condition_line.startswith('(') and condition_line.endswith(')'):
            # Extract condition from while (condition)
            condition = condition_line[1:-1].strip()
        else:
            # Extract condition from while condition: (remove trailing colon if present)
            condition = condition_line.rstrip(':').strip()
        
        return {
            'type': 'while',
            'condition': self._parse_expression(condition)
        }
    
    def _parse_push_statement(self, line: str) -> Dict[str, Any]:
        """Parse a push statement"""
        if line.startswith('push('):
            # Handle push(value) format
            start = line.find('(') + 1
            end = line.rfind(')')
            value = line[start:end].strip()
        else:
            # Handle push value format
            value = line[5:].strip()  # Remove 'push '
        
        return {
            'type': 'push',
            'value': self._parse_expression(value)
        }
    
    def _parse_pop_statement(self, line: str) -> Dict[str, Any]:
        """Parse a pop statement"""
        if line == 'pop':
            return {'type': 'pop'}
        elif line.startswith('pop('):
            # Handle pop() format
            start = line.find('(') + 1
            end = line.rfind(')')
            content = line[start:end].strip()
            if content:
                return {
                    'type': 'pop',
                    'variable': content
                }
            else:
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
        
        # Check for parenthesized expressions first
        if expr.startswith('(') and expr.endswith(')'):
            # Check if this is a parenthesized expression or a function call
            # by looking for a function name before the opening parenthesis
            paren_pos = expr.find('(')
            if paren_pos > 0:
                # This might be a function call
                return self._parse_function_call(expr)
            else:
                # This is a parenthesized expression
                inner_expr = expr[1:-1].strip()
                return self._parse_expression(inner_expr)
        
        # Check for logical operators first (before function calls)
        if ' and ' in expr:
            return self._parse_logical_and(expr)
        if ' && ' in expr:
            return self._parse_logical_and(expr)
        if ' or ' in expr:
            return self._parse_logical_or(expr)
        if ' || ' in expr:
            return self._parse_logical_or(expr)
        if expr.startswith('not '):
            return self._parse_logical_not(expr)
        
        # Check for arithmetic operators (before function calls)
        arithmetic_ops = ['+', '-', '*', '/']
        for op in arithmetic_ops:
            if op in expr and not self._is_inside_nested_structure(expr, expr.find(op)):
                return self._parse_arithmetic(expr, op)
        
        # Check for comparison operators (but not inside strings or function calls)
        # Check for == first, then single = if it's not part of := assignment
        comparison_ops = ['==', '!=', '<=', '>=', '<', '>']
        for op in comparison_ops:
            if op in expr and not self._is_inside_nested_structure(expr, expr.find(op)):
                return self._parse_comparison(expr, op)
        
        # Check for single = if it's not part of := assignment
        if '=' in expr and ':=' not in expr and not self._is_inside_nested_structure(expr, expr.find('=')):
            return self._parse_comparison(expr, '=')

        # Variable reference or function call
        if '(' in expr and ')' in expr:
            return self._parse_function_call(expr)
        
        # Check for dictionary access (variable["key"])
        if '[' in expr and ']' in expr and not self._is_inside_nested_structure(expr, expr.find('[')):
            return self._parse_dict_access(expr)
        
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
    
    def _remove_inline_comments(self, line: str) -> str:
        """Remove inline comments from a line, but not from inside strings"""
        # Find the first # that's not inside a string
        comment_pos = -1
        i = 0
        while i < len(line):
            if line[i] == '#':
                if not self._is_inside_string(line, i):
                    comment_pos = i
                    break
            i += 1
        
        if comment_pos >= 0:
            return line[:comment_pos].strip()
        return line
    
    def _is_inside_nested_structure(self, line: str, pos: int) -> bool:
        """Check if a position is inside a nested structure (string, function call, etc.)"""
        in_string = False
        string_char = None
        paren_depth = 0
        bracket_depth = 0
        
        for i, char in enumerate(line[:pos]):
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
            else:
                if char == string_char and (i == 0 or line[i-1] != '\\'):
                    in_string = False
                    string_char = None
        
        return in_string or paren_depth > 0 or bracket_depth > 0
    
    def _parse_multiline_assignment(self, lines: List[str], start_idx: int) -> Optional[Dict[str, Any]]:
        """Parse a multi-line assignment (like dictionary)"""
        # Get the variable name from the first line
        first_line = lines[start_idx].strip()
        if ':=' not in first_line:
            return None
        
        # Extract variable name (everything before :=)
        var_name = first_line[:first_line.find(':=')].strip()
        
        # Find the matching closing brace
        end_idx = self._find_matching_brace(lines, start_idx + 1)
        if end_idx == -1:
            return None
        
        # Collect all lines between the braces
        dict_lines = []
        for i in range(start_idx + 1, end_idx + 1):
            dict_lines.append(lines[i].strip())
        
        # Join them and create a proper dictionary string
        dict_content = ' '.join(dict_lines)
        dict_string = '{' + dict_content + '}'
        
        return {
            'type': 'assignment',
            'variable': var_name,
            'value': self._parse_expression(dict_string)
        }
    
    def _find_matching_brace(self, lines: List[str], start_idx: int) -> int:
        """Find the matching closing brace for a dictionary or list"""
        brace_count = 1  # Start at 1 because we're looking for the closing brace of an already opened brace
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
    
    def _parse_comparison(self, expr: str, op: str) -> Dict[str, Any]:
        """Parse a comparison expression"""
        parts = expr.split(op, 1)
        if len(parts) != 2:
            # If we can't split properly, treat as a variable
            return {
                'type': 'variable',
                'name': expr
            }
        
        left = parts[0].strip()
        right = parts[1].strip()
        
        return {
            'type': 'comparison',
            'operator': op,
            'left': self._parse_expression(left),
            'right': self._parse_expression(right)
        }
    
    def _parse_logical_and(self, expr: str) -> Dict[str, Any]:
        """Parse a logical AND expression"""
        # Check for && first, then and
        if ' && ' in expr:
            parts = expr.split(' && ', 1)
        elif ' and ' in expr:
            parts = expr.split(' and ', 1)
        else:
            return self._parse_expression(expr)
        
        if len(parts) != 2:
            return self._parse_expression(expr)
        
        left = parts[0].strip()
        right = parts[1].strip()
        
        return {
            'type': 'logical_and',
            'left': self._parse_expression(left),
            'right': self._parse_expression(right)
        }
    
    def _parse_logical_or(self, expr: str) -> Dict[str, Any]:
        """Parse a logical OR expression"""
        parts = expr.split(' or ', 1)
        if len(parts) != 2:
            return self._parse_expression(expr)
        
        left = parts[0].strip()
        right = parts[1].strip()
        
        return {
            'type': 'logical_or',
            'left': self._parse_expression(left),
            'right': self._parse_expression(right)
        }
    
    def _parse_logical_not(self, expr: str) -> Dict[str, Any]:
        """Parse a logical NOT expression"""
        if not expr.startswith('not '):
            return self._parse_expression(expr)
        
        operand = expr[4:].strip()  # Remove 'not '
        
        return {
            'type': 'logical_not',
            'operand': self._parse_expression(operand)
        }
    
    def _parse_dict_access(self, expr: str) -> Dict[str, Any]:
        """Parse dictionary access expression (variable["key"])"""
        # Find the opening bracket
        bracket_pos = expr.find('[')
        if bracket_pos == -1:
            return self._parse_expression(expr)
        
        # Extract variable name
        var_name = expr[:bracket_pos].strip()
        
        # Find the closing bracket
        close_bracket_pos = expr.rfind(']')
        if close_bracket_pos == -1 or close_bracket_pos <= bracket_pos:
            return self._parse_expression(expr)
        
        # Extract key expression
        key_expr = expr[bracket_pos + 1:close_bracket_pos].strip()
        
        return {
            'type': 'dict_access',
            'variable': self._parse_expression(var_name),
            'key': self._parse_expression(key_expr)
        }
    
    def _parse_arithmetic(self, expr: str, op: str) -> Dict[str, Any]:
        """Parse arithmetic expression"""
        parts = expr.split(op, 1)
        if len(parts) != 2:
            # If we can't split properly, treat as a variable
            return {
                'type': 'variable',
                'name': expr
            }
        
        left = parts[0].strip()
        right = parts[1].strip()
        
        return {
            'type': 'arithmetic',
            'operator': op,
            'left': self._parse_expression(left),
            'right': self._parse_expression(right)
        }
