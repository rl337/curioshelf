#!/usr/bin/env python3
"""
CurioShelf - Visual Asset Manager for 2D Games
Main application entry point
"""

import sys
import argparse
import logging
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from .ui.ui_factory import create_ui_factory, get_available_ui_backends
from tests.ui_debug import get_global_debugger, create_debugger
from tests.ui_instrumentation_server import UIInstrumentationServer


def configure_logging(debug: bool = False, verbose: bool = False):
    """Configure logging levels based on flags"""
    if debug:
        level = logging.DEBUG
    elif verbose:
        level = logging.INFO
    else:
        level = logging.WARNING
    
    # Configure root logger
    logging.basicConfig(
        level=level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%H:%M:%S'
    )
    
    # Set specific loggers to appropriate levels
    if debug:
        # Enable debug logging for all CurioShelf modules
        logging.getLogger('curioshelf').setLevel(logging.DEBUG)
    else:
        # Only show warnings and errors for CurioShelf modules
        logging.getLogger('curioshelf').setLevel(logging.WARNING)


def main():
    """Main application entry point"""
    parser = argparse.ArgumentParser(description="CurioShelf - Visual Asset Manager")
    parser.add_argument(
        "--ui",
        default="qt",
        help="UI backend to use (default: qt). Available: " + ", ".join(get_available_ui_backends())
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Enable verbose logging"
    )
    parser.add_argument(
        "--debug-ui",
        action="store_true",
        help="Run in debug UI mode (equivalent to --ui debug)"
    )
    parser.add_argument(
        "--run-for-real",
        action="store_true",
        help="Run the actual GUI application (default: runs in scripted mode for testing)"
    )
    parser.add_argument(
        "--script",
        type=str,
        help="Run the actual GUI with scripted instrumentation from the specified .curio file"
    )
    parser.add_argument(
        "--debug",
        action="store_true",
        help="Enable debug logging (DEBUG level)"
    )
    parser.add_argument(
        "--ui-debug",
        action="store_true",
        help="Enable UI debugging and instrumentation server"
    )
    parser.add_argument(
        "--debug-port",
        type=int,
        default=8888,
        help="Port for UI instrumentation server (default: 8888)"
    )
    parser.add_argument(
        "--debug-log",
        type=str,
        help="File to log debug messages to"
    )
    
    args = parser.parse_args()
    
    # Configure logging first
    configure_logging(debug=args.debug, verbose=args.verbose)
    
    # Override UI backend if debug-ui flag is set
    ui_backend = "debug" if args.debug_ui else args.ui
    
    # Check for mutually exclusive flags
    if args.run_for_real and args.script:
        print("Error: --run-for-real and --script are mutually exclusive")
        sys.exit(1)
    
    print(f"Starting CurioShelf with {ui_backend} UI backend")
    
    # Set up UI debugging if requested
    debugger = None
    instrumentation_server = None
    if args.ui_debug:
        print("Setting up UI debugging and instrumentation...")
        debug_log_file = Path(args.debug_log) if args.debug_log else None
        debugger = create_debugger(enabled=True, log_file=debug_log_file)
        
        # Start instrumentation server
        instrumentation_server = UIInstrumentationServer(debugger, port=args.debug_port)
        instrumentation_server.start()
        print(f"UI instrumentation server started on port {args.debug_port}")
        print("Use 'python debug_ui.py' to connect and control the UI")
    
    try:
        # Create UI factory
        factory = create_ui_factory(ui_backend, args.verbose)
        
        # Handle script execution mode
        if args.script:
            script_path = Path(args.script)
            if not script_path.exists():
                print(f"Error: Script file not found: {script_path}")
                sys.exit(1)
            
            print(f"Running GUI with scripted instrumentation from: {script_path}")
            
            # Read the script content
            with open(script_path, 'r') as f:
                script_content = f.read()
            
            # Create main window
            main_window = factory.create_main_window()
            
            # Get the application instance from the main window
            app_instance = main_window.app
            
            # Load test plugins for scripted execution
            from test_support.test_plugin_loader import load_test_plugins, initialize_test_plugins, get_heartbeat_monitor
            
            # Load and initialize test plugins
            load_test_plugins()
            if not initialize_test_plugins(app_instance):
                print("Warning: Some test plugins failed to initialize")
            
            # Get the UI implementation and run the script with test plugins
            ui_impl = factory.get_ui_implementation()
            if hasattr(ui_impl, 'execute_script_content'):
                print("Executing script with test plugins...")
                
                # Get heartbeat monitor from plugin system
                heartbeat = get_heartbeat_monitor()
                
                # Execute script with heartbeat monitoring
                try:
                    result = ui_impl.execute_script_content(script_content, app_instance, heartbeat)
                    print(f"Script execution completed with result: {result}")
                except Exception as e:
                    print(f"Script execution failed: {e}")
                    sys.exit(1)
            else:
                print("Error: UI implementation does not support script execution")
                sys.exit(1)
            
            return
        
        # Create main window (not needed for script UI)
        if ui_backend != "script":
            main_window = factory.create_main_window()
            
            # Register main window with instrumentation server if debugging is enabled
            if instrumentation_server:
                instrumentation_server.register_controller("main_window", main_window)
                print("Main window registered with instrumentation server")
            
            if args.verbose:
                print(f"UI Implementation: {factory.get_ui_implementation().__class__.__name__}")
                print("Main window created successfully!")
        else:
            if args.verbose:
                print(f"UI Implementation: {factory.get_ui_implementation().__class__.__name__}")
        
        # Run the application
        if ui_backend == "debug":
            print("Running in debug mode - no GUI will be shown")
            print("Use Ctrl+C to exit")
        elif ui_backend == "script":
            print("Running in script mode - command interface")
            print("Use Ctrl+C to exit")
            factory.get_ui_implementation().run_event_loop()
        elif args.run_for_real:
            print("Starting GUI application (--run-for-real flag set)...")
            # Show the main window for GUI applications
            if hasattr(main_window, 'main_widget'):
                print(f"Main window has main_widget: {main_window.main_widget}")
                # For Qt implementations, show the underlying Qt widget
                if hasattr(main_window.main_widget, 'qt_widget'):
                    print("Showing Qt widget...")
                    main_window.main_widget.qt_widget.show()
                    print(f"Qt widget visible: {main_window.main_widget.qt_widget.isVisible()}")
                elif hasattr(main_window.main_widget, 'show'):
                    print("Showing main widget...")
                    main_window.main_widget.show()
            elif hasattr(main_window, 'show'):
                print("Showing main window...")
                main_window.show()
            
            print("Starting event loop...")
            factory.get_ui_implementation().run_event_loop()
        else:
            print("=" * 60)
            print("🚨 SCRIPTED MODE - GUI NOT RUNNING 🚨")
            print("=" * 60)
            print("The application is running in scripted mode for testing.")
            print("To run the actual GUI application, use the --run-for-real flag:")
            print()
            print("  poetry run python main.py --run-for-real")
            print()
            print("This prevents the GUI from hanging during testing and debugging.")
            print("Use the scripted testing system to interact with the UI:")
            print("  poetry run python debug_ui_layout.py")
            print("=" * 60)
            
            # Run a simple scripted test instead
            ui_impl = factory.get_ui_implementation()
            test_commands = [
                {"command": "wait", "duration": 0.5, "description": "Initial wait"},
                {"command": "debug_info", "info_type": "windows", "description": "List windows"},
                {"command": "debug_info", "info_type": "parenting", "description": "Check parenting"},
                {"command": "wait", "duration": 1.0, "description": "Final wait"}
            ]
            
            print("Running scripted test...")
            ui_impl.enable_test_mode(test_commands)
            print("Scripted test completed!")
    
    except KeyboardInterrupt:
        print("\nApplication interrupted by user")
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)
    finally:
        if instrumentation_server:
            instrumentation_server.stop()
        factory.cleanup()


if __name__ == "__main__":
    main()
