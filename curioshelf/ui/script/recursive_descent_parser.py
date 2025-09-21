"""
Recursive Descent Parser for CurioScript

This module implements a recursive descent parser for CurioScript programs.
It uses the lexer from lexer.py and implements a straightforward
recursive descent parsing algorithm.
"""

from typing import List, Dict, Any, Optional
from curioshelf.ui.script.lexer import CurioScriptLexer, Token, TokenType


class RecursiveDescentParser:
    """Recursive Descent Parser for CurioScript"""
    
    def __init__(self, budget_checker=None):
        self.tokens = []
        self.position = 0
        self.budget_checker = budget_checker
    
    def parse_script(self, script_content: str) -> List[Dict[str, Any]]:
        """Parse a script into a list of statements"""
        lexer = CurioScriptLexer(script_content)
        self.tokens = [t for t in lexer.tokens if t.type != TokenType.NEWLINE]
        self.position = 0
        
        statements = []
        while self.position < len(self.tokens) and self.tokens[self.position].type != TokenType.EOF:
            stmt = self.parse_statement()
            if stmt:
                statements.append(stmt)
            else:
                # If parsing failed, advance position to avoid infinite loop
                self.position += 1
        
        return statements
    
    def parse_statement(self) -> Optional[Dict[str, Any]]:
        """Parse a statement"""
        if self.position >= len(self.tokens):
            return None
        
        current = self.tokens[self.position]
        
        # Assignment statements
        if (current.type == TokenType.IDENTIFIER and 
            self.position + 1 < len(self.tokens) and 
            self.tokens[self.position + 1].type in [TokenType.ASSIGN, TokenType.COLON_ASSIGN]):
            return self.parse_assignment()
        
        # If statements
        elif current.type == TokenType.IF:
            return self.parse_if_statement()
        
        # Foreach statements
        elif current.type == TokenType.FOREACH:
            return self.parse_foreach_statement()
        
        # Push statements
        elif current.type == TokenType.PUSH:
            return self.parse_push_statement()
        
        # Pop statements
        elif current.type == TokenType.POP:
            return self.parse_pop_statement()
        
        # Block statements
        elif current.type == TokenType.LBRACE:
            return self.parse_block_statement()
        
        # Function call statements
        elif current.type == TokenType.IDENTIFIER:
            return self.parse_function_call_statement()
        
        # Expression statements
        else:
            expr = self.parse_expression()
            if expr:
                return {
                    'type': 'expression',
                    'value': expr
                }
        
        return None
    
    def parse_assignment(self) -> Optional[Dict[str, Any]]:
        """Parse an assignment statement"""
        if self.position >= len(self.tokens) or self.tokens[self.position].type != TokenType.IDENTIFIER:
            return None
        
        var_name = self.tokens[self.position].value
        self.position += 1
        
        if (self.position >= len(self.tokens) or 
            self.tokens[self.position].type not in [TokenType.ASSIGN, TokenType.COLON_ASSIGN]):
            return None
        
        self.position += 1  # Skip assignment operator
        
        value = self.parse_expression()
        if value is None:
            return None
        
        return {
            'type': 'assignment',
            'variable': var_name,
            'value': value
        }
    
    def parse_if_statement(self) -> Optional[Dict[str, Any]]:
        """Parse an if statement"""
        if self.position >= len(self.tokens) or self.tokens[self.position].type != TokenType.IF:
            return None
        
        self.position += 1  # Skip 'if'
        
        # Optional parentheses
        if (self.position < len(self.tokens) and 
            self.tokens[self.position].type == TokenType.LPAREN):
            self.position += 1  # Skip '('
            condition = self.parse_expression()
            if (self.position >= len(self.tokens) or 
                self.tokens[self.position].type != TokenType.RPAREN):
                return None
            self.position += 1  # Skip ')'
        else:
            condition = self.parse_expression()
        
        if condition is None:
            return None
        
        # Skip colon if present
        if (self.position < len(self.tokens) and 
            self.tokens[self.position].type == TokenType.COLON):
            self.position += 1
        
        then_stmt = self.parse_statement()
        if then_stmt is None:
            return None
        
        result = {
            'type': 'if',
            'condition': condition,
            'then': [then_stmt]  # Wrap in list for runtime compatibility
        }
        
        # Optional else clause
        if (self.position < len(self.tokens) and 
            self.tokens[self.position].type == TokenType.ELSE):
            self.position += 1  # Skip 'else'
            else_stmt = self.parse_statement()
            if else_stmt:
                result['else'] = [else_stmt]  # Wrap in list for runtime compatibility
        
        return result
    
    def parse_foreach_statement(self) -> Optional[Dict[str, Any]]:
        """Parse a foreach statement"""
        if self.position >= len(self.tokens) or self.tokens[self.position].type != TokenType.FOREACH:
            return None
        
        self.position += 1  # Skip 'foreach'
        
        # Optional parentheses
        if (self.position < len(self.tokens) and 
            self.tokens[self.position].type == TokenType.LPAREN):
            self.position += 1  # Skip '('
            if (self.position >= len(self.tokens) or 
                self.tokens[self.position].type != TokenType.IDENTIFIER):
                return None
            var_name = self.tokens[self.position].value
            self.position += 1
            
            if (self.position >= len(self.tokens) or 
                self.tokens[self.position].type != TokenType.IN):
                return None
            self.position += 1  # Skip 'in'
            
            iterable = self.parse_expression()
            if iterable is None:
                return None
            
            if (self.position >= len(self.tokens) or 
                self.tokens[self.position].type != TokenType.RPAREN):
                return None
            self.position += 1  # Skip ')'
        else:
            if (self.position >= len(self.tokens) or 
                self.tokens[self.position].type != TokenType.IDENTIFIER):
                return None
            var_name = self.tokens[self.position].value
            self.position += 1
            
            if (self.position >= len(self.tokens) or 
                self.tokens[self.position].type != TokenType.IN):
                return None
            self.position += 1  # Skip 'in'
            
            iterable = self.parse_expression()
            if iterable is None:
                return None
        
        # Skip colon if present
        if (self.position < len(self.tokens) and 
            self.tokens[self.position].type == TokenType.COLON):
            self.position += 1
        
        body = self.parse_statement()
        if body is None:
            return None
        
        return {
            'type': 'foreach',
            'variable': var_name,
            'iterable': iterable,
            'body': [body]  # Wrap in list for runtime compatibility
        }
    
    def parse_push_statement(self) -> Optional[Dict[str, Any]]:
        """Parse a push statement"""
        if self.position >= len(self.tokens) or self.tokens[self.position].type != TokenType.PUSH:
            return None
        
        self.position += 1  # Skip 'push'
        
        value = self.parse_expression()
        if value is None:
            return None
        
        return {
            'type': 'push',
            'value': value
        }
    
    def parse_pop_statement(self) -> Optional[Dict[str, Any]]:
        """Parse a pop statement"""
        if self.position >= len(self.tokens) or self.tokens[self.position].type != TokenType.POP:
            return None
        
        self.position += 1  # Skip 'pop'
        
        var_name = None
        if (self.position < len(self.tokens) and 
            self.tokens[self.position].type == TokenType.IDENTIFIER):
            var_name = self.tokens[self.position].value
            self.position += 1
        
        return {
            'type': 'pop',
            'variable': var_name
        }
    
    def parse_block_statement(self) -> Optional[Dict[str, Any]]:
        """Parse a block statement"""
        if self.position >= len(self.tokens) or self.tokens[self.position].type != TokenType.LBRACE:
            return None
        
        self.position += 1  # Skip '{'
        
        statements = []
        while (self.position < len(self.tokens) and 
               self.tokens[self.position].type != TokenType.RBRACE):
            stmt = self.parse_statement()
            if stmt:
                statements.append(stmt)
        
        if (self.position >= len(self.tokens) or 
            self.tokens[self.position].type != TokenType.RBRACE):
            return None
        
        self.position += 1  # Skip '}'
        
        return {
            'type': 'block',
            'statements': statements
        }
    
    def parse_function_call_statement(self) -> Optional[Dict[str, Any]]:
        """Parse a function call statement"""
        if self.position >= len(self.tokens) or self.tokens[self.position].type != TokenType.IDENTIFIER:
            return None
        
        func_name = self.tokens[self.position].value
        self.position += 1
        
        if (self.position >= len(self.tokens) or 
            self.tokens[self.position].type != TokenType.LPAREN):
            return None
        
        self.position += 1  # Skip '('
        
        args = []
        if (self.position < len(self.tokens) and 
            self.tokens[self.position].type != TokenType.RPAREN):
            args = self.parse_argument_list()
        
        if (self.position >= len(self.tokens) or 
            self.tokens[self.position].type != TokenType.RPAREN):
            return None
        
        self.position += 1  # Skip ')'
        
        return {
            'type': 'command',
            'name': func_name,
            'args': args
        }
    
    def parse_argument_list(self) -> List[Any]:
        """Parse an argument list"""
        args = []
        
        while self.position < len(self.tokens):
            if self.tokens[self.position].type == TokenType.RPAREN:
                break
            
            if self.budget_checker:
                self.budget_checker('parse_function_call')
            
            expr = self.parse_expression()
            if expr is None:
                break
            
            args.append(expr)
            
            if (self.position < len(self.tokens) and 
                self.tokens[self.position].type == TokenType.COMMA):
                self.position += 1  # Skip ','
            else:
                break
        
        return args
    
    def parse_expression(self) -> Any:
        """Parse an expression with proper precedence"""
        # Temporarily disable budget checking to debug infinite loop
        # if self.budget_checker:
        #     self.budget_checker('parse_expression')
        return self.parse_logical_or()
    
    def parse_logical_or(self) -> Any:
        """Parse logical OR expressions"""
        left = self.parse_logical_and()
        
        while (self.position < len(self.tokens) and 
               self.tokens[self.position].type == TokenType.OR):
            # Temporarily disable budget checking to debug infinite loop
            # if self.budget_checker:
            #     self.budget_checker('parse_expression')
            self.position += 1
            right = self.parse_logical_and()
            left = {
                'type': 'BINARY_OPERATION',
                'operator': '||',
                'left': left,
                'right': right
            }
        
        return left
    
    def parse_logical_and(self) -> Any:
        """Parse logical AND expressions"""
        left = self.parse_equality()
        
        while (self.position < len(self.tokens) and 
               self.tokens[self.position].type == TokenType.AND):
            if self.budget_checker:
                self.budget_checker('parse_expression')
            self.position += 1
            right = self.parse_equality()
            left = {
                'type': 'BINARY_OPERATION',
                'operator': '&&',
                'left': left,
                'right': right
            }
        
        return left
    
    def parse_equality(self) -> Any:
        """Parse equality expressions"""
        left = self.parse_comparison()
        
        while (self.position < len(self.tokens) and 
               self.tokens[self.position].type in [TokenType.EQUAL, TokenType.NOT_EQUAL]):
            if self.budget_checker:
                self.budget_checker('parse_expression')
            op = self.tokens[self.position].type
            self.position += 1
            right = self.parse_comparison()
            left = {
                'type': 'BINARY_OPERATION',
                'operator': '==' if op == TokenType.EQUAL else '!=',
                'left': left,
                'right': right
            }
        
        return left
    
    def parse_comparison(self) -> Any:
        """Parse comparison expressions"""
        left = self.parse_addition()
        
        while (self.position < len(self.tokens) and 
               self.tokens[self.position].type in [TokenType.LESS_THAN, TokenType.GREATER_THAN,
                                                   TokenType.LESS_EQUAL, TokenType.GREATER_EQUAL]):
            if self.budget_checker:
                self.budget_checker('parse_expression')
            op = self.tokens[self.position].type
            self.position += 1
            right = self.parse_addition()
            
            op_map = {
                TokenType.LESS_THAN: '<',
                TokenType.GREATER_THAN: '>',
                TokenType.LESS_EQUAL: '<=',
                TokenType.GREATER_EQUAL: '>='
            }
            
            left = {
                'type': 'BINARY_OPERATION',
                'operator': op_map[op],
                'left': left,
                'right': right
            }
        
        return left
    
    def parse_addition(self) -> Any:
        """Parse addition expressions"""
        left = self.parse_multiplication()
        
        while (self.position < len(self.tokens) and 
               self.tokens[self.position].type in [TokenType.PLUS, TokenType.MINUS]):
            if self.budget_checker:
                self.budget_checker('parse_expression')
            op = self.tokens[self.position].type
            self.position += 1
            right = self.parse_multiplication()
            left = {
                'type': 'BINARY_OPERATION',
                'operator': '+' if op == TokenType.PLUS else '-',
                'left': left,
                'right': right
            }
        
        return left
    
    def parse_multiplication(self) -> Any:
        """Parse multiplication expressions"""
        left = self.parse_unary()
        
        while (self.position < len(self.tokens) and 
               self.tokens[self.position].type in [TokenType.MULTIPLY, TokenType.DIVIDE, TokenType.MODULO]):
            if self.budget_checker:
                self.budget_checker('parse_expression')
            op = self.tokens[self.position].type
            self.position += 1
            right = self.parse_unary()
            
            op_map = {
                TokenType.MULTIPLY: '*',
                TokenType.DIVIDE: '/',
                TokenType.MODULO: '%'
            }
            
            left = {
                'type': 'BINARY_OPERATION',
                'operator': op_map[op],
                'left': left,
                'right': right
            }
        
        return left
    
    def parse_unary(self) -> Any:
        """Parse unary expressions"""
        if (self.position < len(self.tokens) and 
            self.tokens[self.position].type in [TokenType.NOT, TokenType.MINUS]):
            op = self.tokens[self.position].type
            self.position += 1
            operand = self.parse_unary()
            return {
                'type': 'UNARY_OPERATION',
                'operator': '!' if op == TokenType.NOT else '-',
                'operand': operand
            }
        
        return self.parse_primary()
    
    def parse_primary(self) -> Any:
        """Parse primary expressions"""
        if self.position >= len(self.tokens):
            return None
        
        current = self.tokens[self.position]
        
        # Parenthesized expressions
        if current.type == TokenType.LPAREN:
            self.position += 1
            expr = self.parse_expression()
            if (self.position >= len(self.tokens) or 
                self.tokens[self.position].type != TokenType.RPAREN):
                return None
            self.position += 1
            return expr
        
        # Function calls
        elif (current.type == TokenType.IDENTIFIER and 
              self.position + 1 < len(self.tokens) and 
              self.tokens[self.position + 1].type == TokenType.LPAREN):
            return self.parse_function_call()
        
        # List literals
        elif current.type == TokenType.LBRACKET:
            return self.parse_list_literal()
        
        # Dictionary literals
        elif current.type == TokenType.LBRACE:
            return self.parse_dictionary_literal()
        
        # Dictionary access
        elif (current.type == TokenType.IDENTIFIER and 
              self.position + 1 < len(self.tokens) and 
              self.tokens[self.position + 1].type == TokenType.LBRACKET):
            return self.parse_dictionary_access()
        
        # Literals
        elif current.type == TokenType.IDENTIFIER:
            self.position += 1
            return {
                'type': 'variable',
                'name': current.value
            }
        
        elif current.type == TokenType.STRING:
            self.position += 1
            return current.value
        
        elif current.type == TokenType.NUMBER:
            self.position += 1
            try:
                if '.' in current.value:
                    return float(current.value)
                else:
                    return int(current.value)
            except ValueError:
                return current.value
        
        elif current.type == TokenType.BOOLEAN:
            self.position += 1
            return current.value.lower() == 'true'
        
        return None
    
    def parse_function_call(self) -> Any:
        """Parse a function call"""
        if (self.position >= len(self.tokens) or 
            self.tokens[self.position].type != TokenType.IDENTIFIER):
            return None
        
        func_name = self.tokens[self.position].value
        self.position += 1
        
        if (self.position >= len(self.tokens) or 
            self.tokens[self.position].type != TokenType.LPAREN):
            return None
        
        self.position += 1  # Skip '('
        
        args = []
        if (self.position < len(self.tokens) and 
            self.tokens[self.position].type != TokenType.RPAREN):
            args = self.parse_argument_list()
        
        if (self.position >= len(self.tokens) or 
            self.tokens[self.position].type != TokenType.RPAREN):
            return None
        
        self.position += 1  # Skip ')'
        
        return {
            'type': 'function_call',
            'name': func_name,
            'args': args
        }
    
    def parse_dictionary_literal(self) -> Any:
        """Parse dictionary literal"""
        if (self.position >= len(self.tokens) or 
            self.tokens[self.position].type != TokenType.LBRACE):
            return None
        
        if self.budget_checker:
            self.budget_checker('parse_dictionary')
        
        self.position += 1  # Skip '{'
        
        dictionary = {}
        
        # Check for empty dictionary
        if (self.position < len(self.tokens) and 
            self.tokens[self.position].type == TokenType.RBRACE):
            self.position += 1  # Skip '}'
            return dictionary
        
        # Parse key-value pairs
        while self.position < len(self.tokens):
            if self.tokens[self.position].type == TokenType.RBRACE:
                break
            
            # Budget check for each key-value pair
            if self.budget_checker:
                self.budget_checker('parse_dictionary')
            
            # Parse key (must be a string literal)
            if self.tokens[self.position].type != TokenType.STRING:
                return None
            
            key = self.tokens[self.position].value
            self.position += 1
            
            # Skip colon
            if (self.position >= len(self.tokens) or 
                self.tokens[self.position].type != TokenType.COLON):
                return None
            self.position += 1
            
            # Parse value
            value = self.parse_expression()
            if value is None:
                return None
            
            dictionary[key] = value
            
            # Skip comma if present
            if (self.position < len(self.tokens) and 
                self.tokens[self.position].type == TokenType.COMMA):
                self.position += 1
            else:
                break
        
        if (self.position >= len(self.tokens) or 
            self.tokens[self.position].type != TokenType.RBRACE):
            return None
        
        self.position += 1  # Skip '}'
        
        return dictionary
    
    def parse_list_literal(self) -> Any:
        """Parse list literal"""
        if (self.position >= len(self.tokens) or 
            self.tokens[self.position].type != TokenType.LBRACKET):
            return None
        
        if self.budget_checker:
            self.budget_checker('parse_dictionary')  # Reuse dictionary cost
        
        self.position += 1  # Skip '['
        
        elements = []
        
        # Check for empty list
        if (self.position < len(self.tokens) and 
            self.tokens[self.position].type == TokenType.RBRACKET):
            self.position += 1  # Skip ']'
            return elements
        
        # Parse elements
        while self.position < len(self.tokens):
            if self.tokens[self.position].type == TokenType.RBRACKET:
                break
            
            if self.budget_checker:
                self.budget_checker('parse_dictionary')  # Reuse dictionary cost
            
            expr = self.parse_expression()
            if expr is None:
                break
            
            elements.append(expr)
            
            if (self.position < len(self.tokens) and 
                self.tokens[self.position].type == TokenType.COMMA):
                self.position += 1  # Skip ','
            else:
                break
        
        if (self.position >= len(self.tokens) or 
            self.tokens[self.position].type != TokenType.RBRACKET):
            return None
        
        self.position += 1  # Skip ']'
        
        return elements
    
    def parse_dictionary_access(self) -> Any:
        """Parse dictionary access"""
        if (self.position >= len(self.tokens) or 
            self.tokens[self.position].type != TokenType.IDENTIFIER):
            return None
        
        obj_name = self.tokens[self.position].value
        self.position += 1
        
        if (self.position >= len(self.tokens) or 
            self.tokens[self.position].type != TokenType.LBRACKET):
            return None
        
        self.position += 1  # Skip '['
        
        key = self.parse_expression()
        if key is None:
            return None
        
        if (self.position >= len(self.tokens) or 
            self.tokens[self.position].type != TokenType.RBRACKET):
            return None
        
        self.position += 1  # Skip ']'
        
        return {
            'type': 'dictionary_access',
            'object': {
                'type': 'variable',
                'name': obj_name
            },
            'key': key
        }
