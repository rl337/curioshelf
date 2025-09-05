#!/usr/bin/env python3
"""
CurioShelf - Visual Asset Manager for 2D Games
Main application entry point
"""

import sys
import os
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from PySide6.QtWidgets import QApplication
from PySide6.QtCore import Qt

from gui.tabbed_main_window import TabbedMainWindow


def main():
    """Main application entry point"""
    # Create QApplication
    app = QApplication(sys.argv)
    app.setApplicationName("CurioShelf")
    app.setApplicationVersion("0.1.0")
    app.setOrganizationName("CurioShelf")
    
    # Set application style
    app.setStyle('Fusion')  # Modern look
    
    # Create and show main window
    window = TabbedMainWindow()
    window.show()
    
    # Run the application
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
