"""
Command parser for script UI implementation

This module provides a simple command parser that can parse commands
in a natural language format and convert them to executable operations.
"""

import re
from typing import Dict, List, Any, Optional, Union
from dataclasses import dataclass
from enum import Enum


class CommandType(Enum):
    """Types of commands that can be parsed"""
    PROJECT_CREATE = "project_create"
    PROJECT_OPEN = "project_open"
    PROJECT_SAVE = "project_save"
    PROJECT_CLOSE = "project_close"
    PROJECT_LIST = "project_list"
    
    SOURCE_IMPORT = "source_import"
    SOURCE_LIST = "source_list"
    SOURCE_DELETE = "source_delete"
    
    OBJECT_CREATE = "object_create"
    OBJECT_LIST = "object_list"
    OBJECT_DELETE = "object_delete"
    
    TEMPLATE_CREATE = "template_create"
    TEMPLATE_LIST = "template_list"
    TEMPLATE_DELETE = "template_delete"
    
    EXPORT_ASSETS = "export_assets"
    
    HELP = "help"
    QUIT = "quit"
    EXIT = "exit"


@dataclass
class ParsedCommand:
    """Represents a parsed command with its arguments"""
    command_type: CommandType
    args: Dict[str, Any]
    raw_command: str


class CommandError(Exception):
    """Exception raised when command parsing fails"""
    pass


class CommandParser:
    """Parser for script commands"""
    
    def __init__(self):
        """Initialize the command parser"""
        self.commands = {
            # Project commands
            r'^project\s+create\s+"([^"]+)"(?:\s+--author\s+"([^"]+)")?(?:\s+--description\s+"([^"]+)")?$': CommandType.PROJECT_CREATE,
            r'^project\s+open\s+"([^"]+)"$': CommandType.PROJECT_OPEN,
            r'^project\s+save$': CommandType.PROJECT_SAVE,
            r'^project\s+close$': CommandType.PROJECT_CLOSE,
            r'^project\s+list$': CommandType.PROJECT_LIST,
            
            # Source commands
            r'^source\s+import\s+"([^"]+)"(?:\s+--name\s+"([^"]+)")?$': CommandType.SOURCE_IMPORT,
            r'^source\s+list$': CommandType.SOURCE_LIST,
            r'^source\s+delete\s+"([^"]+)"$': CommandType.SOURCE_DELETE,
            
            # Object commands
            r'^object\s+create\s+"([^"]+)"(?:\s+--source\s+"([^"]+)")?$': CommandType.OBJECT_CREATE,
            r'^object\s+list$': CommandType.OBJECT_LIST,
            r'^object\s+delete\s+"([^"]+)"$': CommandType.OBJECT_DELETE,
            
            # Template commands
            r'^template\s+create\s+"([^"]+)"(?:\s+--object\s+"([^"]+)")?$': CommandType.TEMPLATE_CREATE,
            r'^template\s+list$': CommandType.TEMPLATE_LIST,
            r'^template\s+delete\s+"([^"]+)"$': CommandType.TEMPLATE_DELETE,
            
            # Export commands
            r'^export\s+assets(?:\s+--format\s+"([^"]+)")?(?:\s+--output\s+"([^"]+)")?$': CommandType.EXPORT_ASSETS,
            
            # Utility commands
            r'^help$': CommandType.HELP,
            r'^quit$': CommandType.QUIT,
            r'^exit$': CommandType.EXIT,
        }
    
    def parse(self, command: str) -> ParsedCommand:
        """
        Parse a command string into a ParsedCommand object
        
        Args:
            command: The command string to parse
            
        Returns:
            ParsedCommand object with parsed information
            
        Raises:
            CommandError: If the command cannot be parsed
        """
        command = command.strip()
        
        if not command:
            raise CommandError("Empty command")
        
        # Try to match against each command pattern
        for pattern, command_type in self.commands.items():
            match = re.match(pattern, command, re.IGNORECASE)
            if match:
                args = self._extract_args(command_type, match.groups())
                return ParsedCommand(
                    command_type=command_type,
                    args=args,
                    raw_command=command
                )
        
        raise CommandError(f"Unknown command: {command}")
    
    def _extract_args(self, command_type: CommandType, groups: tuple) -> Dict[str, Any]:
        """Extract arguments from regex match groups based on command type"""
        args = {}
        
        if command_type == CommandType.PROJECT_CREATE:
            args['name'] = groups[0] if groups[0] else "New Project"
            args['author'] = groups[1] if len(groups) > 1 and groups[1] else "User"
            args['description'] = groups[2] if len(groups) > 2 and groups[2] else "A new project"
            
        elif command_type == CommandType.PROJECT_OPEN:
            args['path'] = groups[0]
            
        elif command_type == CommandType.SOURCE_IMPORT:
            args['file_path'] = groups[0]
            args['name'] = groups[1] if len(groups) > 1 and groups[1] else None
            
        elif command_type == CommandType.SOURCE_DELETE:
            args['name'] = groups[0]
            
        elif command_type == CommandType.OBJECT_CREATE:
            args['name'] = groups[0]
            args['source'] = groups[1] if len(groups) > 1 and groups[1] else None
            
        elif command_type == CommandType.OBJECT_DELETE:
            args['name'] = groups[0]
            
        elif command_type == CommandType.TEMPLATE_CREATE:
            args['name'] = groups[0]
            args['object'] = groups[1] if len(groups) > 1 and groups[1] else None
            
        elif command_type == CommandType.TEMPLATE_DELETE:
            args['name'] = groups[0]
            
        elif command_type == CommandType.EXPORT_ASSETS:
            args['format'] = groups[0] if len(groups) > 0 and groups[0] else "png"
            args['output'] = groups[1] if len(groups) > 1 and groups[1] else None
            
        return args
    
    def get_help(self) -> str:
        """Get help text for all available commands"""
        help_text = """
CurioShelf Script Interface Commands:

Project Management:
  project create "name" [--author "author"] [--description "description"]
  project open "path"
  project save
  project close
  project list

Source Management:
  source import "file_path" [--name "name"]
  source list
  source delete "name"

Object Management:
  object create "name" [--source "source_name"]
  object list
  object delete "name"

Template Management:
  template create "name" [--object "object_name"]
  template list
  template delete "name"

Export:
  export assets [--format "format"] [--output "path"]

Utilities:
  help
  quit / exit
"""
        return help_text.strip()
    
    def is_valid_command(self, command: str) -> bool:
        """Check if a command string is valid without parsing it"""
        try:
            self.parse(command)
            return True
        except CommandError:
            return False
