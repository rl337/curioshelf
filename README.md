# CurioShelf

A visual asset manager for 2D games built with Python and PySide6.

## Features

- Import and tag large SVG or raster source files
- Select rectangular regions and save them as named slices
- Group slices under named objects with multiple layers (concept, working, production)
- Template system for defining required views/states
- Visual feedback on object completeness
- Clean JSON metadata storage
- Export functionality for sprite frames and spritesheets

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

### Basic Workflow

1. **Sources Tab**: Import source images and create slices by selecting rectangular regions
2. **Templates Tab**: Create and manage templates with visual representation of required views
3. **Objects Tab**: Create objects, assign templates, and track compliance with visual progress indicators

#### Detailed Steps:
1. **Import Source**: In Sources tab, click "Import Source" to load an image file
2. **Create Slice**: Click and drag on the canvas to select a region, then create a named slice
3. **Create Template**: In Templates tab, create templates with required views (e.g., "front", "back", "walk1")
4. **Create Object**: In Objects tab, create objects and assign templates
5. **Track Progress**: View template compliance with visual progress bars and status indicators

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
