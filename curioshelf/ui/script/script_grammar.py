"""
Script grammar for CurioShelf

This module defines the grammar and syntax for the scripting interface.
It provides a simple, intuitive command language for asset management.
"""

from typing import Dict, List, Any, Optional
from enum import Enum


class GrammarToken(Enum):
    """Tokens in the script grammar"""
    # Keywords
    PROJECT = "project"
    SOURCE = "source"
    OBJECT = "object"
    TEMPLATE = "template"
    EXPORT = "export"
    HELP = "help"
    QUIT = "quit"
    EXIT = "exit"
    
    # Actions
    CREATE = "create"
    OPEN = "open"
    SAVE = "save"
    CLOSE = "close"
    LIST = "list"
    DELETE = "delete"
    IMPORT = "import"
    ASSETS = "assets"
    
    # Modifiers
    AUTHOR = "--author"
    DESCRIPTION = "--description"
    NAME = "--name"
    SOURCE_REF = "--source"
    OBJECT_REF = "--object"
    FORMAT = "--format"
    OUTPUT = "--output"
    
    # Literals
    STRING = "string"
    IDENTIFIER = "identifier"
    EOF = "eof"


class ScriptGrammar:
    """Grammar definition for the script interface"""
    
    def __init__(self):
        """Initialize the script grammar"""
        self.keywords = {
            'project': GrammarToken.PROJECT,
            'source': GrammarToken.SOURCE,
            'object': GrammarToken.OBJECT,
            'template': GrammarToken.TEMPLATE,
            'export': GrammarToken.EXPORT,
            'help': GrammarToken.HELP,
            'quit': GrammarToken.QUIT,
            'exit': GrammarToken.EXIT,
            'create': GrammarToken.CREATE,
            'open': GrammarToken.OPEN,
            'save': GrammarToken.SAVE,
            'close': GrammarToken.CLOSE,
            'list': GrammarToken.LIST,
            'delete': GrammarToken.DELETE,
            'import': GrammarToken.IMPORT,
            'assets': GrammarToken.ASSETS,
        }
        
        self.modifiers = {
            '--author': GrammarToken.AUTHOR,
            '--description': GrammarToken.DESCRIPTION,
            '--name': GrammarToken.NAME,
            '--source': GrammarToken.SOURCE_REF,
            '--object': GrammarToken.OBJECT_REF,
            '--format': GrammarToken.FORMAT,
            '--output': GrammarToken.OUTPUT,
        }
    
    def get_syntax_examples(self) -> Dict[str, List[str]]:
        """Get syntax examples for each command category"""
        return {
            "Project Management": [
                'project create "My Project"',
                'project create "My Project" --author "John Doe" --description "A test project"',
                'project open "/path/to/project"',
                'project save',
                'project close',
                'project list'
            ],
            "Source Management": [
                'source import "/path/to/image.png"',
                'source import "/path/to/image.png" --name "my_source"',
                'source list',
                'source delete "my_source"'
            ],
            "Object Management": [
                'object create "my_object"',
                'object create "my_object" --source "my_source"',
                'object list',
                'object delete "my_object"'
            ],
            "Template Management": [
                'template create "my_template"',
                'template create "my_template" --object "my_object"',
                'template list',
                'template delete "my_template"'
            ],
            "Export": [
                'export assets',
                'export assets --format "png"',
                'export assets --format "png" --output "/path/to/output"'
            ],
            "Utilities": [
                'help',
                'quit',
                'exit'
            ]
        }
    
    def get_grammar_rules(self) -> Dict[str, str]:
        """Get formal grammar rules"""
        return {
            "command": "entity action [arguments]",
            "entity": "project | source | object | template | export",
            "action": "create | open | save | close | list | delete | import | assets",
            "arguments": "string_literal [modifier string_literal]*",
            "string_literal": '"text"',
            "modifier": "--author | --description | --name | --source | --object | --format | --output",
            "identifier": "word without spaces",
            "comment": "# text until end of line"
        }
    
    def validate_syntax(self, command: str) -> bool:
        """Validate basic syntax of a command"""
        # Basic validation rules
        if not command.strip():
            return False
        
        # Check for balanced quotes
        quote_count = command.count('"')
        if quote_count % 2 != 0:
            return False
        
        # Check for valid entity-action pairs
        parts = command.split()
        if len(parts) < 2:
            return False
        
        entity = parts[0].lower()
        action = parts[1].lower()
        
        valid_entities = ['project', 'source', 'object', 'template', 'export', 'help', 'quit', 'exit']
        if entity not in valid_entities:
            return False
        
        # Check for valid action for each entity
        valid_actions = {
            'project': ['create', 'open', 'save', 'close', 'list'],
            'source': ['import', 'list', 'delete'],
            'object': ['create', 'list', 'delete'],
            'template': ['create', 'list', 'delete'],
            'export': ['assets'],
            'help': [],
            'quit': [],
            'exit': []
        }
        
        if action not in valid_actions.get(entity, []):
            return False
        
        return True
    
    def get_completion_suggestions(self, partial_command: str) -> List[str]:
        """Get completion suggestions for a partial command"""
        suggestions = []
        parts = partial_command.strip().split()
        
        if len(parts) == 0:
            # Suggest entities
            suggestions = ['project', 'source', 'object', 'template', 'export', 'help', 'quit', 'exit']
        elif len(parts) == 1:
            # Suggest actions for the entity
            entity = parts[0].lower()
            valid_actions = {
                'project': ['create', 'open', 'save', 'close', 'list'],
                'source': ['import', 'list', 'delete'],
                'object': ['create', 'list', 'delete'],
                'template': ['create', 'list', 'delete'],
                'export': ['assets'],
                'help': [],
                'quit': [],
                'exit': []
            }
            suggestions = valid_actions.get(entity, [])
        elif len(parts) >= 2:
            # Suggest modifiers
            entity = parts[0].lower()
            action = parts[1].lower()
            
            if entity == 'project' and action == 'create':
                suggestions = ['--author', '--description']
            elif entity == 'source' and action == 'import':
                suggestions = ['--name']
            elif entity == 'object' and action == 'create':
                suggestions = ['--source']
            elif entity == 'template' and action == 'create':
                suggestions = ['--object']
            elif entity == 'export' and action == 'assets':
                suggestions = ['--format', '--output']
        
        return suggestions
