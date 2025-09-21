"""
Lexer for CurioScript

This module provides the lexer components (TokenType, Token, CurioScriptLexer) 
for tokenizing CurioScript programs.
"""

from typing import List
from dataclasses import dataclass
from enum import Enum


class TokenType(Enum):
    """Token types for CurioScript lexer"""
    # Literals
    IDENTIFIER = "IDENTIFIER"
    STRING = "STRING"
    NUMBER = "NUMBER"
    BOOLEAN = "BOOLEAN"
    
    # Operators
    ASSIGN = "ASSIGN"           # =
    COLON_ASSIGN = "COLON_ASSIGN"  # :=
    PLUS = "PLUS"               # +
    MINUS = "MINUS"             # -
    MULTIPLY = "MULTIPLY"       # *
    DIVIDE = "DIVIDE"           # /
    MODULO = "MODULO"           # %
    EQUAL = "EQUAL"             # ==
    NOT_EQUAL = "NOT_EQUAL"     # !=
    LESS_THAN = "LESS_THAN"     # <
    GREATER_THAN = "GREATER_THAN"  # >
    LESS_EQUAL = "LESS_EQUAL"   # <=
    GREATER_EQUAL = "GREATER_EQUAL"  # >=
    AND = "AND"                 # &&
    OR = "OR"                   # ||
    NOT = "NOT"                 # !
    
    # Punctuation
    LPAREN = "LPAREN"           # (
    RPAREN = "RPAREN"           # )
    LBRACE = "LBRACE"           # {
    RBRACE = "RBRACE"           # }
    LBRACKET = "LBRACKET"       # [
    RBRACKET = "RBRACKET"       # ]
    COMMA = "COMMA"             # ,
    SEMICOLON = "SEMICOLON"     # ;
    COLON = "COLON"             # :
    
    # Keywords
    IF = "IF"
    ELSE = "ELSE"
    FOREACH = "FOREACH"
    IN = "IN"
    PUSH = "PUSH"
    POP = "POP"
    
    # Special
    EOF = "EOF"
    NEWLINE = "NEWLINE"


@dataclass
class Token:
    """A token in the CurioScript language"""
    type: TokenType
    value: str
    line: int
    column: int
    
    def __str__(self):
        return f"{self.type.value}({self.value})"


class CurioScriptLexer:
    """Lexer for CurioScript that tokenizes input text"""
    
    def __init__(self, text: str):
        self.text = text
        self.position = 0
        self.line = 1
        self.column = 1
        self.tokens = []
        self._tokenize()
    
    def _tokenize(self):
        """Tokenize the input text"""
        while self.position < len(self.text):
            char = self.text[self.position]
            
            if char.isspace():
                if char == '\n':
                    self.tokens.append(Token(TokenType.NEWLINE, '\n', self.line, self.column))
                    self.line += 1
                    self.column = 1
                else:
                    self.column += 1
                self.position += 1
            elif char == '#':
                self._tokenize_comment()
            elif char.isalpha() or char == '_':
                self._tokenize_identifier()
            elif char.isdigit():
                self._tokenize_number()
            elif char in '"\'':
                self._tokenize_string()
            elif char in '+-*/%=!<>&|':
                self._tokenize_operator()
            elif char in '(){}[],;':
                self._tokenize_punctuation()
            elif char == ':':
                # Check for := operator first
                if self.position + 1 < len(self.text) and self.text[self.position + 1] == '=':
                    self._tokenize_operator()
                else:
                    self._tokenize_punctuation()
            else:
                self.position += 1
                self.column += 1
        
        self.tokens.append(Token(TokenType.EOF, '', self.line, self.column))
    
    def _tokenize_comment(self):
        """Tokenize a comment (skip it)"""
        while self.position < len(self.text) and self.text[self.position] != '\n':
            self.position += 1
            self.column += 1
    
    def _tokenize_identifier(self):
        """Tokenize an identifier or keyword"""
        start = self.position
        while (self.position < len(self.text) and 
               (self.text[self.position].isalnum() or self.text[self.position] == '_')):
            self.position += 1
            self.column += 1
        
        text = self.text[start:self.position]
        
        # Check if it's a keyword
        keyword_map = {
            'if': TokenType.IF,
            'else': TokenType.ELSE,
            'foreach': TokenType.FOREACH,
            'in': TokenType.IN,
            'push': TokenType.PUSH,
            'pop': TokenType.POP,
            'true': TokenType.BOOLEAN,
            'false': TokenType.BOOLEAN,
            'not': TokenType.NOT,
            'and': TokenType.AND,
            'or': TokenType.OR
        }
        
        if text.lower() in keyword_map:
            token_type = keyword_map[text.lower()]
        else:
            token_type = TokenType.IDENTIFIER
        
        self.tokens.append(Token(token_type, text, self.line, self.column - len(text)))
    
    def _tokenize_number(self):
        """Tokenize a number literal"""
        start = self.position
        while (self.position < len(self.text) and 
               (self.text[self.position].isdigit() or self.text[self.position] == '.')):
            self.position += 1
            self.column += 1
        
        text = self.text[start:self.position]
        self.tokens.append(Token(TokenType.NUMBER, text, self.line, self.column - len(text)))
    
    def _tokenize_string(self):
        """Tokenize a string literal"""
        quote_char = self.text[self.position]
        self.position += 1
        self.column += 1
        start = self.position
        
        while self.position < len(self.text) and self.text[self.position] != quote_char:
            if self.text[self.position] == '\\' and self.position + 1 < len(self.text):
                # Escape sequence
                self.position += 2
                self.column += 2
            else:
                self.position += 1
                self.column += 1
        
        if self.position < len(self.text):
            text = self.text[start:self.position]
            self.position += 1
            self.column += 1
            self.tokens.append(Token(TokenType.STRING, text, self.line, self.column - len(text) - 2))
    
    def _tokenize_punctuation(self):
        """Tokenize punctuation"""
        char = self.text[self.position]
        punctuation_map = {
            '(': TokenType.LPAREN,
            ')': TokenType.RPAREN,
            '{': TokenType.LBRACE,
            '}': TokenType.RBRACE,
            '[': TokenType.LBRACKET,
            ']': TokenType.RBRACKET,
            ',': TokenType.COMMA,
            ';': TokenType.SEMICOLON,
            ':': TokenType.COLON
        }
        
        token_type = punctuation_map[char]
        self.tokens.append(Token(token_type, char, self.line, self.column))
        self.position += 1
        self.column += 1
    
    def _tokenize_operator(self):
        """Tokenize operators"""
        char = self.text[self.position]
        
        # Check for two-character operators first
        if self.position + 1 < len(self.text):
            two_char = self.text[self.position:self.position + 2]
            two_char_ops = {
                '==': TokenType.EQUAL,
                '!=': TokenType.NOT_EQUAL,
                '<=': TokenType.LESS_EQUAL,
                '>=': TokenType.GREATER_EQUAL,
                '&&': TokenType.AND,
                '||': TokenType.OR,
                ':=': TokenType.COLON_ASSIGN
            }
            
            if two_char in two_char_ops:
                self.tokens.append(Token(two_char_ops[two_char], two_char, self.line, self.column))
                self.position += 2
                self.column += 2
                return
        
        # Single character operators
        single_char_ops = {
            '=': TokenType.ASSIGN,
            '+': TokenType.PLUS,
            '-': TokenType.MINUS,
            '*': TokenType.MULTIPLY,
            '/': TokenType.DIVIDE,
            '%': TokenType.MODULO,
            '<': TokenType.LESS_THAN,
            '>': TokenType.GREATER_THAN,
            '!': TokenType.NOT
        }
        
        if char in single_char_ops:
            self.tokens.append(Token(single_char_ops[char], char, self.line, self.column))
            self.position += 1
            self.column += 1
        else:
            # Skip unknown characters
            self.position += 1
            self.column += 1
