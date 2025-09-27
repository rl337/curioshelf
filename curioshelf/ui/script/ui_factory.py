"""
Script UI Factory for CurioShelf

This factory creates a scripting interface that allows programmatic control
of the asset manager through a simple command grammar.
"""

import sys
import traceback
from typing import Any, Optional, Dict, List
from pathlib import Path

from ..abstraction import (
    UIWidget, UIButton, UITextInput, UIComboBox, UIListWidget, UICanvas,
    UIMessageBox, UIFileDialog, UIProgressBar, UIGroupBox, UITabWidget,
    UISplitter, UILayout, UIMenuBar, UIMenu, UIMenuItem, UIStatusBar
)
from .widgets import (
    ScriptUIWidget, ScriptUIButton, ScriptUITextInput, ScriptUIComboBox, ScriptUIListWidget,
    ScriptUICanvas, ScriptUIMessageBox, ScriptUIFileDialog, ScriptUIProgressBar,
    ScriptUIGroupBox, ScriptUITabWidget, ScriptUISplitter, ScriptUILayout,
    ScriptUIMenuItem, ScriptUIMenu, ScriptUIMenuBar, ScriptUIStatusBar
)
from ..factory_interface import UIFactoryInterface
from ..ui_interface import UIImplementationInterface, UIImplementationError
from .command_parser import CommandParser, CommandError, ParsedCommand, CommandType
from .script_grammar import ScriptGrammar
from .script_runtime import ScriptRuntime


class ScriptUIImplementation(UIImplementationInterface, UIFactoryInterface):
    """Script implementation of the UI interface for programmatic control"""
    
    def __init__(self, verbose: bool = True, interactive: bool = True, application_interface: Any = None, execution_budget: int = 1000):
        super().__init__(verbose)
        self._initialized = False
        self._running = False
        self._interactive = interactive
        self._command_parser = CommandParser()
        self._grammar = ScriptGrammar()
        self._command_history: List[str] = []
        self._output_buffer: List[str] = []
        self._script_runtime = ScriptRuntime(application_interface, verbose, execution_budget)
        
    def initialize(self) -> bool:
        """Initialize the script UI implementation"""
        self._initialized = True
        if self.verbose:
            print("[SCRIPT] UI implementation initialized")
            print("[SCRIPT] Available commands:")
            print(self._script_runtime.get_help())
        return True
    
    def cleanup(self) -> bool:
        """Cleanup the script UI implementation"""
        self._initialized = False
        self._running = False
        if self.verbose:
            print("[SCRIPT] UI implementation cleaned up")
        return True
    
    def get_ui_implementation(self) -> 'UIImplementationInterface':
        """Get the UI implementation instance"""
        return self
    
    def is_initialized(self) -> bool:
        """Check if script UI is initialized"""
        return self._initialized
    
    def run_event_loop(self) -> int:
        """Run the script event loop"""
        if not self._initialized:
            raise UIImplementationError("Script UI not initialized")
        
        self._running = True
        if self.verbose:
            print("[SCRIPT] Starting script interface...")
        
        if self._interactive:
            self._run_interactive_mode()
        else:
            self._run_batch_mode()
        
        return 0
    
    def quit_event_loop(self) -> None:
        """Quit the script event loop"""
        self._running = False
        if self.verbose:
            print("[SCRIPT] Quitting script interface...")
    
    def set_global_style(self, style: Dict[str, Any]) -> None:
        """Set global styling (not applicable for script UI)"""
        pass
    
    def handle_error(self, error: Exception, context: str = "") -> None:
        """Handle script UI errors"""
        error_msg = f"Script UI Error: {str(error)}"
        if self.verbose:
            print(f"[SCRIPT ERROR] {error_msg} (Context: {context})")
        raise UIImplementationError(error_msg, "script", context)
    
    def _run_interactive_mode(self) -> None:
        """Run in interactive mode with command prompt"""
        print("\nCurioShelf Script Interface")
        print("Type 'help' for available commands, 'quit' to exit")
        print("-" * 50)
        
        while self._running:
            try:
                command = input("curioshelf> ").strip()
                
                if not command:
                    continue
                
                self._command_history.append(command)
                
                if command.lower() in ['quit', 'exit']:
                    break
                
                self._execute_command(command)
                
            except KeyboardInterrupt:
                print("\n[SCRIPT] Interrupted by user")
                break
            except EOFError:
                print("\n[SCRIPT] End of input")
                break
            except Exception as e:
                print(f"[SCRIPT ERROR] {e}")
    
    def _run_batch_mode(self) -> None:
        """Run in batch mode, reading commands from stdin"""
        if self.verbose:
            print("[SCRIPT] Running in batch mode...")
        
        try:
            for line in sys.stdin:
                if not self._running:
                    break
                    
                command = line.strip()
                if command:
                    self._execute_command(command)
                    
                    # Check if script requested exit
                    if not self._running:
                        break
        except KeyboardInterrupt:
            if self.verbose:
                print("\n[SCRIPT] Interrupted by user")
        except Exception as e:
            print(f"[SCRIPT ERROR] {e}")
    
    def _execute_command(self, command: str) -> None:
        """Execute a parsed command"""
        try:
            # For now, use the simple command parser
            # In the future, this would use ANTLR to parse the full grammar
            parsed = self._command_parser.parse(command)
            self._output_buffer.append(f"Executing: {parsed.raw_command}")
            
            # Execute using the script runtime
            # Convert parsed command to a statement that the runtime can execute
            statement = self._convert_to_statement(parsed)
            result = self._script_runtime.execute_statement(statement)
            
            # Check if the script requested an exit
            try:
                if self._script_runtime.state_machine.get_variable("_script_exit_requested"):
                    try:
                        exit_code = self._script_runtime.state_machine.get_variable("_script_exit_code")
                    except NameError:
                        exit_code = 0
                    if self.verbose:
                        print(f"[SCRIPT] Exit requested with code: {exit_code}")
                    self._running = False
                    return
            except NameError:
                # _script_exit_requested not set, continue normally
                pass
            
            if result is not None:
                self._output_buffer.append(f"Result: {result}")
            
            if self.verbose:
                print(f"[SCRIPT] {parsed.command_type.value}: {parsed.args}")
                if result is not None:
                    print(f"[SCRIPT] Result: {result}")
                
        except CommandError as e:
            error_msg = f"Command error: {e}"
            self._output_buffer.append(error_msg)
            if self.verbose:
                print(f"[SCRIPT ERROR] {error_msg}")
        except Exception as e:
            error_msg = f"Execution error: {e}"
            self._output_buffer.append(error_msg)
            if self.verbose:
                print(f"[SCRIPT ERROR] {error_msg}")
                traceback.print_exc()
    
    def _convert_to_statement(self, parsed: ParsedCommand) -> Dict[str, Any]:
        """Convert a parsed command to a statement for the runtime"""
        # This is a simplified conversion - in practice, this would be
        # handled by the ANTLR visitor
        if parsed.command_type == CommandType.HELP:
            return {
                'type': 'command',
                'name': 'help',
                'args': []
            }
        elif parsed.command_type == CommandType.QUIT or parsed.command_type == CommandType.EXIT:
            return {
                'type': 'command',
                'name': 'quit',
                'args': []
            }
        else:
            # Convert to a command call
            return {
                'type': 'command',
                'name': parsed.command_type.value,
                'args': list(parsed.args.values())
            }
    
    def get_output(self) -> List[str]:
        """Get the output buffer"""
        return self._output_buffer.copy()
    
    def clear_output(self) -> None:
        """Clear the output buffer"""
        self._output_buffer.clear()
    
    def get_command_history(self) -> List[str]:
        """Get command history"""
        return self._command_history.copy()
    
    def get_completion_suggestions(self, partial_command: str) -> List[str]:
        """Get completion suggestions for a partial command"""
        return self._grammar.get_completion_suggestions(partial_command)
    
    # UI Factory methods (stubs for compatibility)
    def create_widget(self, parent: Optional['UIWidget'] = None) -> 'UIWidget':
        """Create a basic widget for script UI"""
        from .widgets import ScriptUIWidget
        widget = ScriptUIWidget()
        if self.verbose:
            print(f"[SCRIPT UI] Created generic widget: {widget}")
        return widget
    
    def create_button(self, text: str = "", parent: Optional['UIWidget'] = None) -> 'UIButton':
        """Create a button for script UI"""
        button = ScriptUIButton(text)
        if self.verbose:
            print(f"[SCRIPT UI] Created button: '{text}'")
        return button
    
    def create_text_input(self, placeholder: str = "", parent: Optional['UIWidget'] = None) -> 'UITextInput':
        """Create a text input for script UI"""
        text_input = ScriptUITextInput(placeholder)
        if self.verbose:
            print(f"[SCRIPT UI] Created text input with placeholder: '{placeholder}'")
        return text_input
    
    def create_line_edit(self, parent: Optional['UIWidget'] = None) -> 'UITextInput':
        """Create a line edit widget for script UI"""
        line_edit = ScriptUITextInput()
        if self.verbose:
            print(f"[SCRIPT UI] Created line edit")
        return line_edit
    
    def create_label(self, text: str = "", parent: Optional['UIWidget'] = None) -> 'UILabel':
        """Create a label widget for script UI"""
        # For now, use a text input as a label (read-only)
        label = ScriptUITextInput(text)
        label.set_enabled(False)  # Make it read-only
        if self.verbose:
            print(f"[SCRIPT UI] Created label: '{text}'")
        return label
    
    def create_combo_box(self, parent: Optional['UIWidget'] = None) -> 'UIComboBox':
        """Create a combo box for script UI"""
        combo_box = ScriptUIComboBox()
        if self.verbose:
            print(f"[SCRIPT UI] Created combo box")
        return combo_box
    
    def create_list_widget(self, parent: Optional['UIWidget'] = None) -> 'UIListWidget':
        """Create a list widget for script UI"""
        list_widget = ScriptUIListWidget()
        if self.verbose:
            print(f"[SCRIPT UI] Created list widget")
        return list_widget
    
    def create_canvas(self, parent: Optional['UIWidget'] = None) -> 'UICanvas':
        """Create a canvas widget for script UI"""
        canvas = ScriptUICanvas()
        if self.verbose:
            print(f"[SCRIPT UI] Created canvas")
        return canvas
    
    def create_message_box(self, parent: Optional['UIWidget'] = None) -> 'UIMessageBox':
        """Create a message box for script UI"""
        message_box = ScriptUIMessageBox()
        if self.verbose:
            print(f"[SCRIPT UI] Created message box")
        return message_box
    
    def create_file_dialog(self, parent: Optional['UIWidget'] = None) -> 'UIFileDialog':
        """Create a file dialog for script UI"""
        file_dialog = ScriptUIFileDialog()
        if self.verbose:
            print(f"[SCRIPT UI] Created file dialog")
        return file_dialog
    
    def create_progress_bar(self, parent: Optional['UIWidget'] = None) -> 'UIProgressBar':
        """Create a progress bar for script UI"""
        progress_bar = ScriptUIProgressBar()
        if self.verbose:
            print(f"[SCRIPT UI] Created progress bar")
        return progress_bar
    
    def create_group_box(self, title: str = "") -> 'UIGroupBox':
        """Create a group box for script UI"""
        group_box = ScriptUIGroupBox(title)
        if self.verbose:
            print(f"[SCRIPT UI] Created group box: '{title}'")
        return group_box
    
    def create_tab_widget(self, parent: Optional['UIWidget'] = None) -> 'UITabWidget':
        """Create a tab widget for script UI"""
        tab_widget = ScriptUITabWidget()
        if self.verbose:
            print(f"[SCRIPT UI] Created tab widget")
        return tab_widget
    
    def create_splitter(self, orientation: str = "horizontal", parent: Optional['UIWidget'] = None) -> 'UISplitter':
        """Create a splitter widget for script UI"""
        splitter = ScriptUISplitter(orientation)
        if self.verbose:
            print(f"[SCRIPT UI] Created splitter with orientation: {orientation}")
        return splitter
    
    def create_layout(self, orientation: str = "vertical", parent: Optional['UIWidget'] = None) -> 'UILayout':
        """Create a layout for script UI"""
        layout = ScriptUILayout(orientation)
        if self.verbose:
            print(f"[SCRIPT UI] Created layout with orientation: {orientation}")
        return layout
    
    def create_menu_bar(self, parent: Optional['UIWidget'] = None) -> 'UIMenuBar':
        """Create a menu bar for script UI"""
        menu_bar = ScriptUIMenuBar()
        if self.verbose:
            print(f"[SCRIPT UI] Created menu bar")
        return menu_bar
    
    def create_menu(self, title: str, parent: Optional['UIWidget'] = None) -> 'UIMenu':
        """Create a menu for script UI"""
        menu = ScriptUIMenu(title)
        if self.verbose:
            print(f"[SCRIPT UI] Created menu: '{title}'")
        return menu
    
    def create_menu_item(self, text: str, parent: Optional['UIWidget'] = None) -> 'UIMenuItem':
        """Create a menu item for script UI"""
        menu_item = ScriptUIMenuItem(text)
        if self.verbose:
            print(f"[SCRIPT UI] Created menu item: '{text}'")
        return menu_item
    
    def create_status_bar(self, parent: Optional['UIWidget'] = None) -> 'UIStatusBar':
        """Create a status bar for script UI"""
        status_bar = ScriptUIStatusBar()
        if self.verbose:
            print(f"[SCRIPT UI] Created status bar")
        return status_bar
    
    def create_label(self, text: str = "", parent: Optional['UIWidget'] = None) -> 'UIWidget':
        """Create a label for script UI"""
        # For now, return a basic widget with text property
        label = ScriptUIWidget()
        label.set_property("text", text)
        # Add set_text method for compatibility
        def set_text(new_text: str) -> None:
            label.set_property("text", new_text)
        label.set_text = set_text
        if self.verbose:
            print(f"[SCRIPT UI] Created label: '{text}'")
        return label
    
    def create_main_widget(self, parent: Optional['UIWidget'] = None) -> 'UIWidget':
        """Create a main widget for the main window"""
        # For script UI, we'll create a simple widget that can be used as main widget
        from curioshelf.ui.abstraction import UIWidget
        return UIWidget()
    
    # Required abstract methods from UIImplementationInterface
    def create_pixmap(self, width: int, height: int) -> Any:
        """Create a pixmap (not applicable for script UI)"""
        raise NotImplementedError("Script UI does not support pixmap creation")
    
    def get_dpi_scale(self) -> float:
        """Get DPI scale (not applicable for script UI)"""
        return 1.0
    
    def get_screen_size(self) -> tuple:
        """Get screen size (not applicable for script UI)"""
        return (1920, 1080)  # Default screen size
    
    def enable_test_mode(self, commands: List[Dict[str, Any]]) -> None:
        """Enable test mode (not applicable for script UI)"""
        pass
    
    def disable_test_mode(self) -> None:
        """Disable test mode (not applicable for script UI)"""
        pass
    
    def is_test_mode(self) -> bool:
        """Check if in test mode (not applicable for script UI)"""
        return False
    
    def execute_script_content(self, script_content: str) -> Any:
        """Execute script content directly"""
        if not self._initialized:
            self.initialize()
        
        self._running = True
        try:
            # Execute the script content directly
            result = self._script_runtime.execute_script_content(script_content)
            
            # Check if script requested exit
            try:
                if self._script_runtime.state_machine.get_variable("_script_exit_requested"):
                    try:
                        exit_code = self._script_runtime.state_machine.get_variable("_script_exit_code")
                    except NameError:
                        exit_code = 0
                    if self.verbose:
                        print(f"[SCRIPT] Exit requested with code: {exit_code}")
                    self._running = False
            except NameError:
                # Variable not set, continue normally
                pass
            
            return result
        except Exception as e:
            if self.verbose:
                print(f"[SCRIPT ERROR] {e}")
            raise


# Alias for backward compatibility
ScriptUIFactory = ScriptUIImplementation


# Register the implementation
from ..ui_interface import UIImplementationRegistry
UIImplementationRegistry.register("script", ScriptUIImplementation)
