# Sparx EA Documentation Generator - Quickstart

## Project Overview

This is a Python-based documentation generator for Sparx Enterprise Architect models (.qea files). It extracts information from the SQLite database within .qea files and generates comprehensive Markdown documentation with hierarchical breadcrumb navigation.

## What It Does

- **Extracts and documents** Use Cases, State Machines, Components, and Classes
- **Generates Markdown documentation** organized by package structure
- **Breadcrumb navigation** on every page for easy navigation back through hierarchy
- **Quality reports** highlighting missing documentation and relationships
- **Regression testing** to ensure consistent output across code changes

## Project Structure

```
EATools/
├── sparx_doc_generator.py          # Main orchestrator (291 lines)
├── sparx_ea_doc/                   # Modular package structure
│   ├── models.py                   # Data models (Element, UseCase, etc.)
│   ├── extractor.py                # Database extraction logic (580 lines)
│   ├── utils.py                    # Utilities (breadcrumb generation)
│   ├── generators/                 # Documentation generators
│   │   ├── use_case_generator.py   # Use case documentation
│   │   ├── state_machine_generator.py
│   │   ├── component_generator.py
│   │   └── class_generator.py
│   └── quality_reporter.py         # Quality checks and reports
├── test_model.qea                  # Test Enterprise Architect model
├── test_doc_consistency.py         # Regression testing script
└── docs_golden/                    # Golden baseline (29 reference files)
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

### Regression Testing

```bash
# Test against golden baseline
python test_doc_consistency.py

# Update golden baseline (after intentional changes)
python test_doc_consistency.py --update
```

## Recent Work Completed

### Breadcrumb Navigation (Latest - Merged)
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

- **develop** - Current development branch (all features merged here)
- **main** - Stable production branch
- **Feature branches** - Follow pattern `claude/<name>-<session-id>`

## Workflow for Changes

1. Create feature branch from develop: `git checkout -b claude/<feature>-<session-id>`
2. Make changes
3. Run regression test: `python test_doc_consistency.py`
4. If test fails due to **intentional changes**: `python test_doc_consistency.py --update`
5. If test fails due to **unintentional changes**: Fix the code
6. Commit changes (include updated golden baseline if applicable)
7. Push and create PR to develop
8. Merge to develop

## Known Limitations

1. Diagram rendering code exists but not yet merged (on separate branch)
2. Class compartments in diagrams limited to first 5 attributes/operations
3. Output directory is gitignored (use --output to customize)

## Potential Next Steps

1. **Merge diagram rendering** - From `claude/diagram-renderer-011CUsF8Ao5L71EDHDcdVJhU`
2. **Add search functionality** - Full-text search across documentation
3. **Generate navigation sidebar** - For easier browsing
4. **Support more diagram types** - Sequence, activity, etc.
5. **Add configuration file** - Customize output format, filters, etc.
6. **Export to HTML** - Static site generation
7. **Cross-references** - Link between related elements
8. **Changelog generation** - Track model changes over time
9. **Improved attribute/operation formatting** - Visibility symbols (+, -, #, ~)
10. **Package diagrams** - Show package hierarchy and dependencies

## For New Sessions

When starting a new session, simply prompt:

```
Read QUICKSTART.md and get familiar with the project.
We're on the develop branch. The latest work added breadcrumb
navigation to all documentation pages.
```

---

**Last Updated**: 2025-11-08
**Current Branch**: develop
**Latest Feature**: Breadcrumb navigation on all pages
**Status**: All tests passing ✅
**Files**: 29 golden baseline files with breadcrumbs
