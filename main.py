#!/usr/bin/env python3
"""
CurioShelf - Visual Asset Manager for 2D Games
Main application entry point
"""

import sys
import argparse
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from gui.ui_factory import create_ui_factory, get_available_ui_backends
from curioshelf.ui_debug import get_global_debugger, create_debugger
from curioshelf.ui_instrumentation_server import UIInstrumentationServer


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
        "--headless",
        action="store_true",
        help="Run in headless mode (equivalent to --ui headless)"
    )
    parser.add_argument(
        "--debug",
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
    
    # Override UI backend if headless flag is set
    ui_backend = "headless" if args.headless else args.ui
    
    print(f"Starting CurioShelf with {ui_backend} UI backend")
    
    # Set up debugging if requested
    debugger = None
    instrumentation_server = None
    if args.debug:
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
        
        # Create main window
        main_window = factory.create_main_window()
        
        # Register main window with instrumentation server if debugging is enabled
        if instrumentation_server:
            instrumentation_server.register_controller("main_window", main_window)
            print("Main window registered with instrumentation server")
        
        if args.verbose:
            print(f"UI Implementation: {factory.get_ui_implementation().__class__.__name__}")
            print("Main window created successfully!")
        
        # Run the application
        if ui_backend == "headless":
            print("Running in headless mode - no GUI will be shown")
            print("Use Ctrl+C to exit")
        else:
            print("Starting GUI application...")
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
