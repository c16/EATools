# Sparx EA Documentation Generator - GUI

A graphical user interface for selective documentation generation from Sparx Enterprise Architect models.

## Installation

### Prerequisites

The GUI requires Python 3.8+ and tkinter (usually included with Python).

### Install Dependencies

```bash
# Install Python package dependencies
pip install -r requirements.txt

# Install tkinter if not already available
# Ubuntu/Debian:
sudo apt-get install python3-tk

# Fedora:
sudo dnf install python3-tkinter

# macOS (from python.org):
# tkinter is included

# Windows:
# tkinter is included with standard Python
```

### Quick Install (Development Mode)

```bash
# Install package in development mode
pip install -e .

# This makes sparx-doc-gui command available globally
sparx-doc-gui
```

## Overview

The GUI allows you to:
- **Select specific documents** to generate using checkboxes
- **Preview document structure** in a hierarchical tree view
- **Generate only selected documents** while maintaining the correct folder hierarchy
- **View markdown previews** of selected documents (right panel)

## Features

- **Left Panel**: Tree view showing all available documents with checkboxes
  - Organized by type (Use Cases, State Machines, Components, Classes, Reports)
  - Hierarchical structure matches output directory layout
  - Click checkboxes to select/deselect individual files
  - Click folders to select/deselect all children

- **Right Panel**: Document preview area
  - Shows preview of selected document
  - Displays file path and selection status

- **Controls**:
  - **Browse**: Select a .qea file to load
  - **Select All**: Check all documents for generation
  - **Deselect All**: Uncheck all documents
  - **Generate Selected Documents**: Generate only the checked documents

## Usage

### Starting the GUI

```bash
python sparx_doc_gui.py
```

### Workflow

1. **Open a .qea File**
   - Click "File > Open .qea File..." or click the "Browse..." button
   - Select your Enterprise Architect .qea file
   - The tool will load the model and populate the document tree

2. **Select Documents**
   - All documents are selected by default
   - Click checkboxes to deselect documents you don't want
   - Use "Select All" / "Deselect All" for quick selection
   - Click on a document to preview it in the right panel

3. **Generate Documentation**
   - Click "Generate Selected Documents"
   - Choose an output directory
   - Wait for generation to complete
   - A success dialog will show when done

## Document Structure

The tree view shows all possible documents organized by type:

```
☑ index.md
☑ use-cases/
  ☑ index.md
  ☑ actors.md
  ☑ login-use-case.md
  ☑ process-order.md
  ...
☑ state-machines/
  ☑ index.md
  ☑ sm-order-state-machine.md
  ...
☑ components/
  ☑ index.md
  ☑ interfaces.md
  ☑ comp-userinterface.md
  ...
☑ classes/
  ☑ index.md
  ☑ domain/
    ☑ order.md
    ☑ user.md
    ...
☑ reports/
  ☑ quality-report.md
  ☑ dependencies.md
```

## Selective Generation

The GUI implements **selective generation**, meaning:
- Only checked documents are written to disk
- The folder hierarchy is always maintained (directories are created as needed)
- Index files always list all items, but only checked items are actually generated
- This allows you to generate partial documentation while keeping navigation intact

## Technical Details

### Dependencies

The GUI requires:
- **tkinter**: Python's standard GUI library (usually included with Python)
- All standard Sparx EA Doc Generator dependencies

### Architecture

The GUI uses:
- `sparx_ea_doc.selective_generator.SelectiveGenerator`: Handles selective document generation
- `DocumentTreeBuilder`: Builds the document tree structure from extracted model data
- `SparxDocGUI`: Main GUI application class

### File Structure

- `sparx_doc_gui.py`: Main GUI application
- `sparx_ea_doc/selective_generator.py`: Selective generation logic
- `sparx_ea_doc/generators/*.py`: Modified generators with selection support
- `test_selective_generation.py`: Tests for selective generation

## Examples

### Example 1: Generate Only Use Cases

1. Open your .qea file
2. Click "Deselect All"
3. Expand "use-cases/"
4. Check the use cases you want
5. Check "use-cases/index.md"
6. Check "index.md" (for main navigation)
7. Generate

Result: Only selected use case files and necessary indexes are created.

### Example 2: Generate Documentation for Specific Package

1. Open your .qea file
2. Expand "classes/"
3. Expand the package you want (e.g., "domain/")
4. Ensure all classes in that package are checked
5. Uncheck other packages
6. Keep "classes/index.md" and "index.md" checked
7. Generate

Result: Only classes from the selected package are generated.

### Example 3: Generate Reports Only

1. Open your .qea file
2. Click "Deselect All"
3. Check "reports/quality-report.md"
4. Check "reports/dependencies.md"
5. Check "index.md"
6. Generate

Result: Only quality and dependency reports are created.

## Troubleshooting

### GUI doesn't start

**Problem**: `ModuleNotFoundError: No module named 'tkinter'`

**Solution**: Install tkinter for your Python version:
- **Ubuntu/Debian**: `sudo apt-get install python3-tk`
- **Fedora**: `sudo dnf install python3-tkinter`
- **macOS**: tkinter should be included with Python from python.org
- **Windows**: tkinter should be included with standard Python installation

### Model doesn't load

**Problem**: Error when opening .qea file

**Solution**:
- Ensure the .qea file is not corrupted
- Check that you have read permissions
- Verify the file is a valid Sparx EA database file

### Generation fails

**Problem**: Error during document generation

**Solution**:
- Check you have write permissions to the output directory
- Ensure sufficient disk space
- Check the console/log for specific error messages

## Known Limitations

1. **Preview Panel**: Currently shows placeholder text; full markdown rendering coming soon
2. **Progress Bar**: Shows indeterminate progress; specific progress tracking coming soon
3. **Large Models**: Very large models (1000+ elements) may take time to load the tree

## Future Enhancements

Planned features:
- Full markdown preview rendering with syntax highlighting
- Search/filter functionality in the tree view
- Save/load selection profiles
- Export selection to configuration file
- Batch processing multiple .qea files
- Real-time progress updates during generation
- Undo/redo for selection changes

## See Also

- [QUICKSTART.md](QUICKSTART.md): Main documentation generator guide
- [README.md](README.md): Project overview
- [test_selective_generation.py](test_selective_generation.py): Automated tests

---

**Last Updated**: 2025-11-11
