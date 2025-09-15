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
    
    args = parser.parse_args()
    
    # Override UI backend if headless flag is set
    ui_backend = "headless" if args.headless else args.ui
    
    print(f"Starting CurioShelf with {ui_backend} UI backend")
    
    try:
        # Create UI factory
        factory = create_ui_factory(ui_backend, args.verbose)
        
        # Create main window
        main_window = factory.create_main_window()
        
        if args.verbose:
            print(f"UI Implementation: {factory.get_ui_implementation().__class__.__name__}")
            print("Main window created successfully!")
        
        # Run the application
        if ui_backend == "headless":
            print("Running in headless mode - no GUI will be shown")
            print("Use Ctrl+C to exit")
        else:
            print("Starting GUI application...")
            factory.get_ui_implementation().run_event_loop()
    
    except KeyboardInterrupt:
        print("\nApplication interrupted by user")
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)
    finally:
        factory.cleanup()


if __name__ == "__main__":
    main()
