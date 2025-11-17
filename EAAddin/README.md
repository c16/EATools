# EA Documentation Generator Addin

Generate comprehensive documentation from your Enterprise Architect models without leaving EA!

This addin integrates the Python-based Sparx EA Documentation Generator directly into Enterprise Architect, providing convenient menu-driven access to all documentation generation features.

## Features

- **Generate All Documentation** - Create complete documentation set (use cases, classes, components, state machines, requirements)
- **Selective Generation** - Generate specific documentation types:
  - Use Cases and Actors
  - Classes, Interfaces, and Enumerations
  - Components and Interfaces
  - State Machines
  - Requirements
- **Extract Diagrams** - Extract EA-rendered diagrams (Windows only, requires pywin32)
- **Quick Access** - Open output folder directly from EA
- **Settings** - Edit configuration without leaving EA
- **EA Integration** - Works seamlessly with your current repository

## Architecture

```
Enterprise Architect
        ↓
   EA Addin (C#) ← You interact here
        ↓
   Python Scripts (sparx_doc_generator.py, ea_diagram_extractor.py)
        ↓
   Generated Documentation (Markdown/HTML)
```

The addin acts as a bridge between EA and the Python documentation generator, making it easy to generate documentation with a single click.

## Prerequisites

### Required
1. **Enterprise Architect 17** (64-bit recommended)
2. **Python 3.8+** installed and in your PATH
3. **Visual Studio** or **.NET Framework SDK 4.8** (for building)
4. **Python dependencies** (install with `pip install -r requirements.txt` from the EATools root):
   - PyYAML
   - graphviz
   - Pillow
   - markdown

### Optional
- **pywin32** (for diagram extraction on Windows): `pip install pywin32`

### Important Notes
- **For EA 17 64-bit**: The project is configured to build for x64 platform explicitly (required by Sparx Systems)
- **For EA 32-bit**: You may need to change the platform target to x86 in EADocGenerator.csproj

## Installation

### Step 1: Build the Addin

1. Open a Command Prompt
2. Navigate to the EAAddin folder:
   ```cmd
   cd C:\path\to\EATools\EAAddin
   ```
3. Run the build script:
   ```cmd
   build.bat
   ```

This will compile the C# addin into a DLL.

### Step 2: Register the Addin

1. **Right-click** on `register.bat` and select **"Run as administrator"**
2. Wait for the registration to complete
3. Close Enterprise Architect if it's running

### Step 3: Enable the Addin in EA

1. Start Enterprise Architect
2. Go to **Extensions** > **Add-Ins...**
3. Find **"EA Doc Generator"** in the list
4. Check the box to enable it
5. Click **Close**

The "EA Doc Generator" menu should now appear in the Extensions menu.

## Usage

### Generate Documentation

1. Open your EA model
2. Go to **Extensions** > **EA Doc Generator**
3. Select the type of documentation you want to generate:
   - **Generate All Documentation** - Creates everything
   - **Generate Use Cases** - Only use cases and actors
   - **Generate Classes** - Only class diagrams and documentation
   - **Generate Components** - Only component documentation
   - **Generate State Machines** - Only state machine documentation
   - **Generate Requirements** - Only requirements documentation

The addin will:
- Save your model
- Run the Python documentation generator
- Show progress in EA's Output window
- Display a success message when complete
- Optionally open the output folder

### Extract Diagrams (Windows Only)

1. Go to **Extensions** > **EA Doc Generator** > **Extract Diagrams**
2. The addin will launch the diagram extractor
3. Diagrams will be saved to the `diagrams` folder

Note: This feature requires Windows and the `pywin32` package.

### Open Output Folder

1. Go to **Extensions** > **EA Doc Generator** > **Open Output Folder**
2. The documentation output folder opens in File Explorer

### Edit Settings

1. Go to **Extensions** > **EA Doc Generator** > **Settings**
2. The `config.yaml` file opens in Notepad
3. Edit settings as needed and save
4. Re-generate documentation to apply changes

## Output Location

By default, documentation is generated to:
```
C:\path\to\EATools\docs\
```

The folder structure looks like:
```
docs/
├── index.md
├── use-cases/
├── classes/
├── components/
├── state-machines/
├── requirements/
├── reports/
└── diagrams/
```

## Configuration

Edit `config.yaml` in the EATools root directory to customize:

- Output directory
- EA diagrams directory
- Documentation types to include
- Private member visibility
- Deprecated element handling
- Quality check thresholds

See the main [README.md](../README.md) for full configuration options.

## Troubleshooting

### Menu Doesn't Appear

1. Go to **Extensions** > **Add-Ins...**
2. Check if "EA Doc Generator" is listed
3. If not listed, re-run `register.bat` as administrator
4. If listed but unchecked, check the box to enable it
5. Restart EA

### "Python not found" Error

1. Make sure Python is installed
2. Open Command Prompt and type: `python --version`
3. If not found, add Python to your PATH:
   - Windows Settings → System → About → Advanced System Settings
   - Environment Variables → System Variables → Path → Edit
   - Add your Python installation directory

### "Script not found" Error

The addin expects this folder structure:
```
EATools/
├── EAAddin/
│   └── bin/
│       └── Release/
│           └── EADocGenerator.dll  ← Addin location
├── sparx_doc_generator.py          ← Python script
├── ea_diagram_extractor.py         ← Diagram extractor
└── config.yaml                     ← Configuration
```

Make sure you haven't moved files around.

### Documentation Generation Fails

1. Check EA's Output window for error messages
2. Try running the Python script manually:
   ```cmd
   cd C:\path\to\EATools
   python sparx_doc_generator.py "path\to\your\model.qea"
   ```
3. Make sure all Python dependencies are installed:
   ```cmd
   pip install -r requirements.txt
   ```

### Diagram Extraction Fails

Diagram extraction requires:
- Windows OS
- `pywin32` package: `pip install pywin32`
- Enterprise Architect must be running

## Uninstallation

1. **Right-click** on `unregister.bat` and select **"Run as administrator"**
2. Restart Enterprise Architect
3. Optionally delete the `EAAddin` folder

## Development

### Modifying the Addin

1. Edit `EADocGenerator.cs`
2. Run `build.bat` to rebuild
3. Run `unregister.bat` (as admin)
4. Run `register.bat` (as admin)
5. Restart EA to test changes

### Debugging

To debug the addin:
1. Open `EADocGenerator.csproj` in Visual Studio
2. Set the Debug executable to EA: `C:\Program Files\Sparx Systems\EA\EA.exe`
3. Press F5 to start debugging
4. EA will launch with the debugger attached

## Architecture Notes

### How It Works

1. The C# addin implements EA's `EA.Addin` interface
2. EA loads the addin via COM registration
3. The addin adds menu items to EA's Extensions menu
4. When you click a menu item:
   - The addin gets the current repository path
   - It launches the Python script with appropriate arguments
   - Output is shown in EA's Output window
   - Results are displayed in a message box

### File Locations

The addin determines the Python script location relative to its own location:
- Addin DLL: `EATools/EAAddin/bin/x64/Release/EADocGenerator.dll` (64-bit EA)
- Python scripts: `EATools/*.py`
- Output: `EATools/docs/`

### Platform Targeting

This addin is built for **x64** by default to support EA 17 64-bit. According to Sparx Systems documentation:
> "When generating a .NET assembly, you must explicitly set the 'Target Platform' to x86/x64. Leaving it on 'Any CPU' could cause issues."

If you have EA 32-bit, modify `EADocGenerator.csproj` to change the platform from x64 to x86.

## Support

For issues or questions:
1. Check the main [README.md](../README.md)
2. Check the [QUICKSTART.md](../QUICKSTART.md)
3. Review error messages in EA's Output window
4. Try running Python scripts manually to isolate issues

## Version History

### 1.0.0 (2025)
- Initial release
- Menu-driven documentation generation
- Integration with Python generator
- Diagram extraction support
- Settings editor
- Output folder quick access

## License

Same as the parent EATools project.
