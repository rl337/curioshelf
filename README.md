# CurioShelf V2

A visual asset manager for 2D games built with Python and PySide6.

## Features

- Import and tag large SVG or raster source files
- **View-based slice creation** with 1:1 correspondence between views and slices
- Group slices under named objects with multiple layers (concept, working, production)
- Template system for defining required views/states
- Visual feedback on object completeness
- Clean JSON metadata storage
- Export functionality for sprite frames and spritesheets

## What's New in V2

- **Simplified Sources Tab**: Focused purely on source image management
- **Enhanced Objects Tab**: Integrated slice creation for object views
- **1:1 Correspondence**: Each object view has exactly one corresponding slice
- **Better UX**: Single workflow for object completion
- **Improved Architecture**: Clean separation between UI and business logic

## Installation

1. Install Python 3.8 or higher
2. Install Poetry: https://python-poetry.org/docs/#installation
3. Install dependencies:
   ```bash
   poetry install
   ```

## Usage

Run the application:
```bash
# Using Poetry
poetry run python main.py

# Or install and run directly
poetry install
poetry run curioshelf

# Or activate the virtual environment
poetry shell
python main.py
```

### Basic Workflow (V2)

1. **Sources Tab**: Import and manage source images (simplified)
2. **Templates Tab**: Create and manage templates with visual representation of required views
3. **Objects Tab**: Create objects, assign templates, and create slices for views (enhanced)

#### Detailed Steps:
1. **Import Source**: In Sources tab, click "Import Source" to load an image file
2. **Create Template**: In Templates tab, create templates with required views (e.g., "front", "back", "walk1")
3. **Create Object**: In Objects tab, create objects and assign templates
4. **Create Slices**: In Objects tab, select a source, select a view, draw selection, and create slice
5. **Track Progress**: View template compliance with visual progress bars and status indicators

#### V2 Improvements:
- **Unified Workflow**: Slice creation is now part of the object management process
- **1:1 Correspondence**: Each view has exactly one corresponding slice
- **Better Organization**: No orphaned slices or duplicate views
- **Clearer Mental Model**: Views and slices are directly connected

### Templates

Templates define the required views for different types of objects:
- **Character**: front, back, left, right, walk1, walk2, idle
- **Tile**: base, variant1, variant2
- **UI Element**: normal, hover, pressed, disabled

## Project Structure

```
curioshelf/
├── curioshelf/          # Core Python module
│   ├── __init__.py
│   └── models.py        # Data models
├── gui/                 # Qt GUI code
│   ├── __init__.py
│   ├── tabbed_main_window.py # Main tabbed application window
│   ├── sources_tab.py   # Sources management tab
│   ├── templates_tab.py # Templates management tab
│   ├── objects_tab.py   # Objects management tab
│   ├── main_window.py   # Legacy main window (deprecated)
│   ├── canvas_widget.py # Image canvas and selection
│   ├── object_panel.py  # Legacy object panel (deprecated)
│   └── template_panel.py # Legacy template panel (deprecated)
├── assets/              # Test images and example SVGs
├── metadata/            # Object and template definitions
├── build/               # Output files (excluded from git)
├── main.py              # Application entry point
├── test_app.py          # Test suite
├── run.sh               # Launcher script
└── pyproject.toml       # Poetry configuration
```

## Development

This is a work in progress. Current features:
- ✅ Modern tabbed interface with dedicated views
- ✅ Sources tab for image import and slice creation
- ✅ Templates tab with visual template cards
- ✅ Objects tab with compliance tracking
- ✅ Core data models with JSON persistence
- ✅ PySide6 GUI framework
- ✅ Image loading and rectangular region selection
- ✅ Template compliance with progress indicators
- ✅ Cross-tab communication and real-time updates

Planned features:
- 🔄 Image slicing and export
- 🔄 SVG support
- 🔄 Filters (pixelation, palettization)
- 🔄 Spritesheet generation
- 🔄 Batch operations
