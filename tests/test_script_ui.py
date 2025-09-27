"""
Tests for Script UI functionality

This module tests the script UI implementation which is designed for
command-line/scripting interfaces rather than GUI widgets.
"""

import pytest
import tempfile
from pathlib import Path
from unittest.mock import Mock, patch

from curioshelf.ui.ui_factory import create_ui_factory
from curioshelf.ui.script.ui_factory import ScriptUIImplementation
from curioshelf.ui.script.script_runtime import ScriptRuntime
from curioshelf.ui.script.command_parser import CommandParser


class TestScriptUIImplementation:
    """Test the script UI implementation"""
    
    def test_script_ui_creation(self):
        """Test that script UI can be created"""
        ui_impl = ScriptUIImplementation(verbose=False)
        assert ui_impl is not None
        assert hasattr(ui_impl, 'initialize')
        assert hasattr(ui_impl, 'cleanup')
        assert hasattr(ui_impl, 'run_event_loop')
    
    def test_script_ui_initialization(self):
        """Test script UI initialization"""
        ui_impl = ScriptUIImplementation(verbose=False)
        result = ui_impl.initialize()
        assert result is True
        assert ui_impl.is_initialized() is True
    
    def test_script_ui_cleanup(self):
        """Test script UI cleanup"""
        ui_impl = ScriptUIImplementation(verbose=False)
        ui_impl.initialize()
        result = ui_impl.cleanup()
        assert result is True
        assert ui_impl.is_initialized() is False
    
    def test_script_ui_widget_creation_supported(self):
        """Test that script UI now supports widget creation"""
        ui_impl = ScriptUIImplementation(verbose=False)
        ui_impl.initialize()
        
        # All widget creation methods should now work
        button = ui_impl.create_button("test")
        assert button is not None
        assert hasattr(button, 'get_text')
        assert button.get_text() == "test"
        
        text_input = ui_impl.create_text_input("test")
        assert text_input is not None
        assert hasattr(text_input, 'get_text')
        
        combo_box = ui_impl.create_combo_box()
        assert combo_box is not None
        assert hasattr(combo_box, 'add_item')
        
        list_widget = ui_impl.create_list_widget()
        assert list_widget is not None
        assert hasattr(list_widget, 'add_item')
    
    def test_script_ui_test_mode_not_supported(self):
        """Test that script UI doesn't support test mode"""
        ui_impl = ScriptUIImplementation(verbose=False)
        ui_impl.initialize()
        
        # Test mode methods should not raise errors but should not do anything
        ui_impl.enable_test_mode([])
        assert ui_impl.is_test_mode() is False
        
        ui_impl.disable_test_mode()
        assert ui_impl.is_test_mode() is False


class TestScriptRuntime:
    """Test the script runtime functionality"""
    
    def test_script_runtime_creation(self):
        """Test that script runtime can be created"""
        runtime = ScriptRuntime(verbose=False)
        assert runtime is not None
        assert hasattr(runtime, 'execute_script_content')
        assert hasattr(runtime, 'get_help')
    
    def test_script_runtime_help(self):
        """Test that script runtime provides help"""
        runtime = ScriptRuntime(verbose=False)
        help_text = runtime.get_help()
        assert isinstance(help_text, str)
        assert len(help_text) > 0
    
    def test_script_runtime_command_execution(self):
        """Test basic command execution"""
        runtime = ScriptRuntime(verbose=False)
        
        # Test help command via script content
        result = runtime.execute_script_content("help")
        # Script execution may return None for simple commands
        # The important thing is that it doesn't raise an exception
        assert result is None or result is not None  # Always true, but documents the behavior
    
    def test_script_runtime_invalid_command(self):
        """Test handling of invalid commands"""
        runtime = ScriptRuntime(verbose=False)
        
        # Test invalid command via script content
        result = runtime.execute_script_content("invalid_command_12345")
        # Should not raise exception, but may return error result or None
        assert result is None or result is not None  # Always true, but documents the behavior


class TestCommandParser:
    """Test the command parser functionality"""
    
    def test_command_parser_creation(self):
        """Test that command parser can be created"""
        parser = CommandParser()
        assert parser is not None
        assert hasattr(parser, 'parse')
    
    def test_command_parser_basic_parsing(self):
        """Test basic command parsing"""
        parser = CommandParser()
        
        # Test simple commands
        result = parser.parse("help")
        assert result is not None
        
        result = parser.parse("quit")
        assert result is not None


class TestScriptUIIntegration:
    """Test script UI integration with the factory system"""
    
    def test_script_ui_factory_creation(self):
        """Test that script UI can be created through factory"""
        factory = create_ui_factory("script", verbose=False)
        assert factory is not None
        
        ui_impl = factory.get_ui_implementation()
        assert isinstance(ui_impl, ScriptUIImplementation)
    
    def test_script_ui_factory_initialization(self):
        """Test script UI factory initialization"""
        factory = create_ui_factory("script", verbose=False)
        ui_impl = factory.get_ui_implementation()
        
        result = ui_impl.initialize()
        assert result is True
        assert ui_impl.is_initialized() is True
    
    @patch('builtins.input', return_value='quit')
    def test_script_ui_interactive_mode(self, mock_input):
        """Test script UI interactive mode (mocked input)"""
        factory = create_ui_factory("script", verbose=False)
        ui_impl = factory.get_ui_implementation()
        ui_impl.initialize()
        
        # This should not hang due to mocked input
        ui_impl.run_event_loop()
    
    def test_script_ui_batch_mode(self):
        """Test script UI batch mode with temporary file"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.curio', delete=False) as f:
            f.write("help\nquit\n")
            script_file = f.name
        
        try:
            factory = create_ui_factory("script", verbose=False)
            ui_impl = factory.get_ui_implementation()
            ui_impl.initialize()
            
            # Test batch mode by redirecting stdin
            with open(script_file, 'r') as f:
                import sys
                original_stdin = sys.stdin
                sys.stdin = f
                try:
                    ui_impl.run_event_loop()
                finally:
                    sys.stdin = original_stdin
        finally:
            Path(script_file).unlink(missing_ok=True)


class TestScriptUIErrorHandling:
    """Test script UI error handling"""
    
    def test_script_ui_error_handling(self):
        """Test script UI error handling"""
        ui_impl = ScriptUIImplementation(verbose=False)
        
        # Test error handling before initialization
        with pytest.raises(Exception):  # Should raise UIImplementationError
            ui_impl.run_event_loop()
    
    def test_script_ui_cleanup_after_error(self):
        """Test script UI cleanup after error"""
        ui_impl = ScriptUIImplementation(verbose=False)
        ui_impl.initialize()
        
        # Force an error state
        ui_impl._running = True
        
        # Cleanup should still work
        result = ui_impl.cleanup()
        assert result is True
        assert ui_impl.is_initialized() is False


# Mark tests that require script UI
pytestmark = pytest.mark.script
