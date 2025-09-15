# CurioShelf Architecture V2

## Overview

This document describes the updated architecture for CurioShelf that establishes a 1:1 correspondence between object views and source slices, moving slice creation from the sources tab to the objects tab.

## Key Changes

### 1. **Slice Creation Moved to Objects Tab**

**Before (V1):**
- Slice creation was in the sources tab
- Slices were created independently of objects
- No clear relationship between views and slices

**After (V2):**
- Slice creation is now in the objects tab
- Slices are created specifically for object views
- 1:1 correspondence between views and slices

### 2. **Simplified Sources Tab**

**Before (V1):**
- Complex UI with slice creation controls
- Slices subpane taking up significant space
- Mixed responsibilities (source management + slice creation)

**After (V2):**
- Clean, focused UI for source management only
- Image preview and basic source information
- Single responsibility: import and manage source images

### 3. **Enhanced Objects Tab**

**Before (V1):**
- Object management only
- No slice creation capabilities
- Limited view of object completeness

**After (V2):**
- Complete object lifecycle management
- Integrated slice creation for views
- Visual feedback on template compliance
- Source selection for slice creation

## New Architecture

### Business Logic Controllers

#### SourcesController (Simplified)
```python
class SourcesController:
    """Simplified controller for source management only"""
    
    # UI Components
    - import_btn: UIButton
    - source_combo: UIComboBox  
    - canvas: UICanvas
    
    # Methods
    - import_source()
    - load_source()
    - refresh_source_combo()
```

#### ObjectsController (Enhanced)
```python
class ObjectsController:
    """Enhanced controller with slice creation capabilities"""
    
    # Object Management
    - objects_list: UIListWidget
    - object_name_label: UIWidget
    - compliance_progress: UIProgressBar
    
    # Slice Creation
    - source_combo: UIComboBox
    - canvas: UICanvas
    - views_list: UIListWidget
    - create_slice_btn: UIButton
    
    # Methods
    - create_object()
    - refresh_views()
    - create_slice()  # NEW: Creates slice for selected view
    - load_source()   # NEW: Loads source for slice creation
```

### Data Model

#### 1:1 Correspondence
- **View Name** = **Slice Name**
- Each object view has exactly one corresponding slice
- Slice creation is always tied to a specific view
- No orphaned slices or duplicate views

#### Template Compliance
- Objects follow templates that define required views
- Each view can have multiple slices (different layers)
- Compliance is calculated based on view completion
- Visual progress indicators show completion status

### User Workflow

#### 1. **Template Creation**
1. Go to Templates tab
2. Create template with required views (e.g., "front", "back", "left", "right")
3. Define template description and requirements

#### 2. **Object Creation**
1. Go to Objects tab
2. Create object and assign template
3. Object shows all required views from template
4. Views are marked as "Missing" until slices are created

#### 3. **Source Import**
1. Go to Sources tab
2. Import source images
3. Preview images and manage sources
4. No slice creation here (simplified)

#### 4. **Slice Creation**
1. In Objects tab, select an object
2. Select a source from the dropdown
3. Select a view from the required views list
4. Draw selection rectangle on the canvas
5. Click "Create Slice for Selected View"
6. Slice is created with view name = slice name

### UI Layout

#### Sources Tab (Simplified)
```
┌─────────────────────────────────────┐
│ [Import Source] [Source: ▼] [0 sources] │
├─────────────────┬───────────────────┤
│ Sources         │ Preview           │
│ ┌─────────────┐ │ ┌───────────────┐ │
│ │ source1.png │ │ │               │ │
│ │ source2.png │ │ │   [Canvas]    │ │
│ └─────────────┘ │ │               │ │
│ [Delete Source] │ └───────────────┘ │
│                 │ File: source1.png │
│                 │ Size: 800x600     │
│                 │ Slices: 3         │
└─────────────────┴───────────────────┘
```

#### Objects Tab (Enhanced)
```
┌─────────────────────────────────────────────────────────┐
│ [Create Object] [Search: ___] [0 objects]              │
├─────────────┬───────────────────────────────────────────┤
│ Objects     │ Object Details                            │
│ ┌─────────┐ │ ┌─────────────────────────────────────┐   │
│ │ Object1 │ │ │ Object Name                         │   │
│ │ Object2 │ │ │ Template: character                 │   │
│ └─────────┘ │ └─────────────────────────────────────┘   │
│ [Edit][Del] │ ┌─────────────────────────────────────┐   │
│             │ │ Template Compliance: [████░░░░] 50% │   │
│             │ │ ✓ front: 1 slice(s)                 │   │
│             │ │ ✗ back: Missing                     │   │
│             │ │ ✗ left: Missing                     │   │
│             │ │ ✗ right: Missing                    │   │
│             │ └─────────────────────────────────────┘   │
│             │ ┌─────────────────────────────────────┐   │
│             │ │ Create Slices for Views             │   │
│             │ │ Source: [source1.png ▼] Layer: [concept ▼] │
│             │ │ ┌─────────────────────────────────┐ │   │
│             │ │ │                                 │ │   │
│             │ │ │        [Canvas]                 │ │   │
│             │ │ │                                 │ │   │
│             │ │ └─────────────────────────────────┘ │   │
│             │ │ Required Views:                    │   │
│             │ │ ┌─────────────────────────────────┐ │   │
│             │ │ │ ✗ front: Missing               │ │   │
│             │ │ │ ✗ back: Missing                │ │   │
│             │ │ │ ✗ left: Missing                │ │   │
│             │ │ │ ✗ right: Missing               │ │   │
│             │ │ └─────────────────────────────────┘ │   │
│             │ │ [Create Slice for Selected View]   │   │
│             │ └─────────────────────────────────────┘   │
└─────────────┴───────────────────────────────────────────┘
```

## Benefits

### 1. **Clearer Mental Model**
- Views and slices are directly connected
- No confusion about slice ownership
- Template compliance is immediately visible

### 2. **Better User Experience**
- Single workflow for object completion
- Visual feedback on progress
- No need to switch between tabs for slice creation

### 3. **Simplified Code**
- Clear separation of concerns
- Easier to test and maintain
- Reduced complexity in sources tab

### 4. **Data Integrity**
- 1:1 correspondence prevents orphaned data
- Template compliance is always accurate
- No duplicate or conflicting slices

## Migration Path

### Phase 1: New Architecture (Current)
- ✅ Business logic controllers updated
- ✅ UI abstraction layer created
- ✅ Comprehensive test suite
- ✅ New UI components designed

### Phase 2: UI Implementation (Next)
- 🔄 Replace existing GUI with new architecture
- 🔄 Update main window to use new tabs
- 🔄 Integrate business logic controllers

### Phase 3: Testing & Refinement
- 🔄 End-to-end testing
- 🔄 User experience validation
- 🔄 Performance optimization

## Testing

The new architecture is fully tested with:
- **17 comprehensive tests** covering all functionality
- **Mock UI implementations** for fast, reliable testing
- **Integration tests** for complete workflows
- **Business logic validation** independent of GUI

Run tests with:
```bash
python run_tests.py
# or
poetry run curioshelf-test
```

## Conclusion

The V2 architecture provides a cleaner, more intuitive user experience while maintaining the powerful functionality of CurioShelf. The 1:1 correspondence between views and slices eliminates confusion and makes the asset management workflow more efficient and reliable.
