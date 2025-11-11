# Sparx EA Documentation Generator - Quickstart

## Project Overview

This is a Python-based documentation generator for Sparx Enterprise Architect models (.qea files). It extracts information from the SQLite database within .qea files and generates comprehensive Markdown documentation with hierarchical breadcrumb navigation.

## What It Does

- **Extracts and documents** Use Cases, State Machines, Components, and Classes
- **Generates Markdown documentation** organized by package structure
- **Breadcrumb navigation** on every page for easy navigation back through hierarchy
- **Quality reports** highlighting missing documentation and relationships
- **Regression testing** to ensure consistent output across code changes
- **Change tracking** with visual diff markup to compare documentation versions

## Project Structure

```
EATools/
├── sparx_doc_generator.py          # Main orchestrator (291 lines)
├── doc_diff_manager.py             # Version history and diff management utility
├── sparx_ea_doc/                   # Modular package structure
│   ├── models.py                   # Data models (Element, UseCase, etc.)
│   ├── extractor.py                # Database extraction logic (580 lines)
│   ├── utils.py                    # Utilities (breadcrumb generation)
│   ├── diff_generator.py           # Diff tracking and visual markup generator
│   ├── generators/                 # Documentation generators
│   │   ├── use_case_generator.py   # Use case documentation
│   │   ├── state_machine_generator.py
│   │   ├── component_generator.py
│   │   └── class_generator.py
│   └── quality_reporter.py         # Quality checks and reports
├── test_model.qea                  # Test Enterprise Architect model
├── test_doc_consistency.py         # Regression testing script
├── docs_golden/                    # Golden baseline (29 reference files)
├── docs_history/                   # Version snapshots (gitignored)
└── docs_diff/                      # Diff-annotated documentation (gitignored)
```

## How to Use

### Basic Documentation Generation

```bash
python sparx_doc_generator.py test_model.qea
```

This generates documentation in `docs/` directory:
- `docs/use-cases/` - Use case documentation
- `docs/state-machines/` - State machine documentation
- `docs/components/` - Component documentation
- `docs/classes/` - Class documentation (organized by package)
- `docs/reports/` - Quality and dependency reports
- `docs/index.md` - Main index with breadcrumb navigation

### Documentation Change Tracking

Track changes between documentation versions with visual diff markup:

```bash
# Generate docs with change tracking enabled
python sparx_doc_generator.py test_model.qea --track-changes
```

This will:
1. Compare current documentation with previous version
2. Generate diff-annotated files in `docs_diff/`
3. Create a changes summary in `docs_diff/CHANGES.md`
4. Save current version to `docs_history/` for future comparisons

**Managing Version History:**

```bash
# List all tracked versions
python doc_diff_manager.py list

# Generate diff manually
python doc_diff_manager.py generate

# Show version details
python doc_diff_manager.py info v_20251110_120000

# Clean up old versions (keep last 5)
python doc_diff_manager.py cleanup --keep 5
```

**Visual Diff Markup:**
- <span style="background-color: #ccffcc;">Green highlight</span> = Added content
- <span style="background-color: #ffcccc; text-decoration: line-through;">Red strikethrough</span> = Removed content
- 🆕 marker = New files
- Change statistics header on modified files

### Regression Testing

```bash
# Test against golden baseline
python test_doc_consistency.py

# Update golden baseline (after intentional changes)
python test_doc_consistency.py --update
```

## Recent Work Completed

### Pixel-Perfect Diagram Rendering (Latest)
- Completely rewrote diagram rendering to use PIL/Pillow for pixel-perfect layout
- Diagrams now match Enterprise Architect layout exactly (same dimensions and positions)
- All diagram types supported:
  - **Use Case diagrams**: Actors as stick figures, use cases as ellipses
  - **Class diagrams**: Classes with compartments, interfaces, enumerations
  - **Component diagrams**: Components with provided/required interfaces
  - **State Machine diagrams**: States with rounded rectangles, transitions
- Proper UML notation:
  - Hollow triangles for generalization/realization
  - Hollow/filled diamonds for aggregation/composition
  - Dashed lines for dependencies
  - Solid/dashed lines based on relationship type
- Diagrams rendered at exact EA dimensions (e.g., 815 x 1067 pixels)
- Classes now show which diagrams they appear in

### Documentation Change Tracking
- Added visual diff tracking for documentation versions
- Automatic version snapshots in `docs_history/`
- Diff-annotated documentation in `docs_diff/` with visual markup
- Change summary reports showing additions, deletions, modifications
- Standalone `doc_diff_manager.py` utility for version management
- Visual indicators: green highlights for additions, red strikethrough for deletions
- `--track-changes` flag for main generator
- Features:
  - Line-by-line diff comparison
  - New file detection
  - Removed file tracking
  - Statistics and change summaries
  - Version cleanup and management

### Breadcrumb Navigation (Merged)
- Added hierarchical breadcrumb navigation to ALL documentation pages
- Created package-level indexes (e.g., `classes/domain/index.md`)
- Created reports index (`reports/index.md`)
- Examples:
  - `[Home](../index.md) > [Use Cases](index.md) > Login Use Case`
  - `[Home](../../index.md) > [Classes](../index.md) > [Domain](index.md) > Order`
- Updated golden baseline with breadcrumbs (29 files)

### Regression Testing System
- Implemented golden baseline comparison system
- Removed timestamps for deterministic output
- Golden baseline in `docs_golden/` (checked into git)
- Verifies documentation remains consistent unless intentionally changed

### Documentation Features
- **Use Cases**: Left-aligned scenarios, UML notation (<<include>>), metadata (version, modified, GUID)
- **Classes**: Public members only, methods before attributes, metadata display
- **Components**: Provided/required interfaces, dependencies
- **State Machines**: States with entry/do/exit operations
- **Quality Reports**: Documentation coverage, undocumented elements

### Modular Architecture
- Refactored from 1,719-line monolithic file
- Organized into logical modules and generators
- Separation of concerns (extraction, generation, reporting)

## Technical Details

### Database Schema
Key tables in .qea SQLite database:
- **t_object** - Elements (classes, use cases, components, etc.)
- **t_diagram** - Diagrams with PDATA properties
- **t_diagramobjects** - Object positions in diagrams
- **t_attribute** - Class attributes
- **t_operation** - Class operations/methods
- **t_package** - Package hierarchy
- **t_objectscenarios** - Use case scenarios
- **t_connector** - Relationships between elements

### Breadcrumb Navigation
- Utility function in `sparx_ea_doc/utils.py`
- Generates hierarchical path: Home > Section > Subsection > Page
- Handles index.md files specially (avoids duplicate directory names)
- Supports nested packages (e.g., classes/domain/)

### Regression Testing
- **Golden baseline**: Expected output stored in `docs_golden/`
- **Checksum verification**: SHA256 comparison of all files
- **Diff display**: Shows exactly what changed when tests fail
- **Model checksum**: `ea6b4c5f76c106d671afc937deade9e018c8cdaad6028ccec32503b9caf61203`

## Dependencies

```bash
pip install graphviz Pillow
```

## Testing

### Generate Documentation
```bash
python sparx_doc_generator.py test_model.qea --output test_docs
```

### Verify Regression Test
```bash
python test_doc_consistency.py
# Should output: ✅ REGRESSION TEST PASSED
```

### Check Breadcrumb Navigation
```bash
# View a use case
cat test_docs/use-cases/login-use-case.md | head -5
# Should show: [Home](../index.md) > [Use Cases](index.md) > Login Use Case

# View a class
cat test_docs/classes/domain/order.md | head -5
# Should show: [Home](../../index.md) > [Classes](../index.md) > [Domain](index.md) > Order
```

## Current Branch Structure

- **main** - Stable production branch
- **develop** - Current development branch (**NEVER commit directly to this branch**)
- **Feature branches** - Follow pattern `claude/<name>-<session-id>` or `feature/<name>` or `bugfix/<name>`

## Workflow for Changes

**⚠️ IMPORTANT: ALL changes must be made on a feature branch. NEVER commit directly to develop or main.**

1. **Start from develop**: Ensure you're on develop and it's up to date
   ```bash
   git checkout develop
   git pull origin develop
   ```

2. **Create feature branch**: Use descriptive name for your feature or bug fix
   ```bash
   git checkout -b claude/<feature-name>-<session-id>
   # OR
   git checkout -b feature/<feature-name>
   # OR
   git checkout -b bugfix/<bug-name>
   ```

3. **Make changes**: Implement your feature or fix

4. **Run regression test**: Ensure no unintended breakage
   ```bash
   python test_doc_consistency.py
   ```

5. **Update baseline if needed**: If test fails due to **intentional changes**
   ```bash
   python test_doc_consistency.py --update
   ```
   If test fails due to **unintentional changes**: Fix the code

6. **Commit changes**: Include updated golden baseline if applicable
   ```bash
   git add .
   git commit -m "Description of changes"
   ```

7. **Push and create PR**: Push your branch and create PR to develop
   ```bash
   git push -u origin <your-branch-name>
   # Then create PR via GitHub to merge into develop
   ```

8. **Merge to develop**: After review and approval, merge the PR

9. **Delete feature branch**: Clean up after merge
   ```bash
   git checkout develop
   git pull origin develop
   git branch -d <your-branch-name>
   ```

## Known Limitations

1. Class compartments in diagrams limited to 10 attributes/operations for readability
2. Output directory is gitignored (use --output to customize)
3. Some diagram types may not render perfectly (complex nesting, custom shapes)

## Potential Next Steps

1. **Add search functionality** - Full-text search across documentation
2. **Generate navigation sidebar** - For easier browsing
3. **Support more diagram types** - Sequence, activity, deployment diagrams
4. **Add configuration file** - Customize output format, filters, etc.
5. **Cross-references** - Link between related elements in documentation
6. **Changelog generation** - Track model changes over time
7. **Improved attribute/operation formatting** - Visibility symbols (+, -, #, ~)
8. **Package diagrams** - Show package hierarchy and dependencies
9. **Diagram annotations** - Add labels, stereotypes from EA
10. **Better connector routing** - Smarter line routing in diagrams

## For New Sessions

When starting a new session, simply prompt:

```
Read QUICKSTART.md and get familiar with the project.
Remember: ALL changes must be on a feature branch - never commit directly to develop.
```

**Important reminders for new sessions:**
- Always start by creating a new feature branch from develop
- Follow the workflow in this document
- Run regression tests before committing
- Create a PR to merge back to develop

---

**Last Updated**: 2025-11-11
**Current Branch**: develop
**Latest Feature**: Pixel-perfect diagram rendering using PIL/Pillow
**Status**: All tests passing ✅
**Key Features**:
- Pixel-perfect diagrams matching EA layout exactly
- All diagram types supported (use cases, classes, components, state machines)
- Breadcrumb navigation on all pages
- Documentation change tracking with visual diff markup
- Class documentation shows associated diagrams
- Regression testing with golden baseline
