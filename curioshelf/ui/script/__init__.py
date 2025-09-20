"""
Script UI implementation for CurioShelf

This module provides a scripting interface to the asset manager that allows
programmatic control through a simple command grammar. Commands are parsed
and executed to perform asset management operations.
"""

from .ui_factory import ScriptUIFactory, ScriptUIImplementation
from .command_parser import CommandParser, CommandError
from .script_grammar import ScriptGrammar

# Import to register the implementation
from . import ui_factory

__all__ = [
    'ScriptUIFactory', 'ScriptUIImplementation',
    'CommandParser', 'CommandError', 'ScriptGrammar'
]
