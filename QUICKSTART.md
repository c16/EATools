# Sparx EA Documentation Generator - Quickstart

## Project Overview

This is a Python-based documentation generator for Sparx Enterprise Architect models (.qea files). It extracts information from the SQLite database within .qea files and generates comprehensive Markdown documentation with hierarchical breadcrumb navigation.

## What It Does

- **Extracts and documents** Use Cases, State Machines, Components, and Classes
- **Generates Markdown and HTML documentation** organized by package structure
- **Renders pixel-perfect diagrams** matching EA's visual style or uses EA-exported diagrams
- **Automated diagram extraction** (Windows only) directly from EA using COM automation
- **Breadcrumb navigation** on every page for easy navigation back through hierarchy
- **Quality reports** highlighting missing documentation and relationships
- **Regression testing** to ensure consistent output across code changes
- **Change tracking** with visual diff markup to compare documentation versions
- **EA Addin Integration** (NEW!) - Generate documentation directly from Enterprise Architect

## Two Ways to Use This Tool

### Option 1: EA Addin (Recommended for EA Users)

Generate documentation directly from Enterprise Architect without leaving EA!

**Quick Setup:**
1. Navigate to `EAAddin` folder
2. Run `build.bat` to compile the addin
3. Run `register.bat` (as administrator)
4. Restart EA
5. Use "EA Doc Generator" menu in Extensions

**Usage:**
- Open your model in EA
- Go to Extensions → EA Doc Generator
- Select documentation type to generate
- Documentation is created automatically!

See [EAAddin/README.md](EAAddin/README.md) for detailed instructions.

### Option 2: Command Line (Flexible for Automation)

Use Python scripts directly for automation, custom workflows, or non-Windows platforms.

See below for command-line usage examples.

## Project Structure

```
EATools/
├── EAAddin/                        # EA Addin for in-app documentation generation (NEW!)
│   ├── EADocGenerator.cs           # C# addin implementation
│   ├── EADocGenerator.csproj       # Visual Studio project file
│   ├── build.bat                   # Build script
│   ├── register.bat                # Registration script (run as admin)
│   ├── unregister.bat              # Unregistration script
│   └── README.md                   # Addin installation and usage guide
├── sparx_doc_generator.py          # Main orchestrator (291 lines)
├── sparx_doc_gui.py                # GUI application with preview capability
├── ea_diagram_extractor.py         # Windows COM automation for EA diagram extraction
├── doc_diff_manager.py             # Version history and diff management utility
├── sparx_ea_doc/                   # Modular package structure
│   ├── models.py                   # Data models (Element, UseCase, etc.)
│   ├── extractor.py                # Database extraction logic (580 lines)
│   ├── utils.py                    # Utilities (breadcrumb generation)
│   ├── diff_generator.py           # Diff tracking and visual markup generator
│   ├── html_generator.py           # HTML documentation generation
│   ├── diagram_renderer.py         # Pixel-perfect diagram rendering with PIL
│   ├── generators/                 # Documentation generators
│   │   ├── use_case_generator.py   # Use case documentation
│   │   ├── state_machine_generator.py
│   │   ├── component_generator.py
│   │   └── class_generator.py
│   └── quality_reporter.py         # Quality checks and reports
├── test_model.qea                  # Test Enterprise Architect model
├── test_doc_consistency.py         # Regression testing script
├── config.yaml                     # Configuration file (optional)
├── docs_golden/                    # Golden baseline (29 reference files)
├── sample_diagrams/                # EA-exported diagrams (GUID-timestamp.png format)
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
- `docs/diagrams/` - Rendered PNG diagrams
- `docs/index.md` - Main index with breadcrumb navigation

### HTML Documentation Generation

Generate HTML documentation alongside markdown:

```bash
python sparx_doc_generator.py test_model.qea --html
```

With custom output directory:

```bash
python sparx_doc_generator.py test_model.qea --html --html-output my_docs_html
```

### Automated Diagram Extraction (Windows Only)

Extract all diagrams directly from Enterprise Architect using COM automation:

```bash
python ea_diagram_extractor.py test_model.qea
```

With custom output directory:

```bash
python ea_diagram_extractor.py test_model.qea -o exported_diagrams
```

**Requirements:**
- Windows OS
- Enterprise Architect installed
- pywin32 package: `pip install pywin32`

This utility connects to EA directly and exports all diagrams in the correct `{GUID}-{timestamp}.png` format.

**Using EA-exported diagrams in documentation:**

```bash
python sparx_doc_generator.py test_model.qea --ea-diagrams-dir exported_diagrams
```

Or configure in `config.yaml`:

```yaml
diagrams:
  ea_exports_dir: "exported_diagrams"
```

The generator will use EA-exported diagrams when available (pixel-perfect accuracy) and fall back to rendering for any missing diagrams.

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

### Robustness & Reliability Improvements (Latest - Nov 2025)
- **Object ID in filenames** - Prevents name clashes when importing from other repositories
  - Format: `name-objectid.md` (e.g., `login-use-case-10.md`)
  - All generators updated: use cases, state machines, components, classes, requirements
  - Cross-reference links updated to use object IDs
- **Enhanced filename sanitization** - Handles tabs, newlines, unprintable characters
  - Unicode normalization (NFKD)
  - Removes control characters and problematic symbols
  - Length limit of 200 characters
  - Platform-safe across Windows, Linux, macOS
- **Robust text cleaning** - Handles notes from different codepages without crashes
  - Supports UTF-8, Windows-1252, ISO-8859-1, CP1252
  - Removes null bytes, control characters, format characters
  - Preserves intentional formatting (newlines, paragraph breaks)
  - Comprehensive test suite with 29 test cases - all passing ✅
- **HTML image overflow fix** - Large diagrams no longer cut off horizontally
  - Responsive image scaling with breakpoints
  - Centered images with proper spacing
  - Works on all screen sizes (desktop, tablet, mobile)
- **Future enhancements roadmap** - 86+ enhancement ideas documented
  - Organized into 11 categories
  - "Quick Wins" section with 10 high-impact, 2-4 hour tasks

### EA Diagram Extraction & Integration
- Added Windows COM automation utility (`ea_diagram_extractor.py`) for extracting diagrams directly from EA
- Automatic diagram export in `{GUID}-{timestamp}.png` format
- Configurable EA diagrams directory via YAML, CLI (`--ea-diagrams-dir`), and GUI
- Generator uses EA-exported diagrams when available (pixel-perfect accuracy)
- Falls back to PIL rendering for missing diagrams
- Supports configuration hierarchy: CLI arg > YAML config > default

### HTML Documentation Generation
- Native Python HTML generation using markdown library (no pandoc dependency)
- Professional styling with embedded CSS
- Breadcrumb navigation converted to HTML links
- CLI options: `--html` and `--html-output`
- GUI checkbox for HTML generation
- Parallel markdown and HTML output

### Pixel-Perfect Diagram Rendering
- Completely rewrote diagram rendering to use PIL/Pillow for pixel-perfect layout
- Diagrams now match Enterprise Architect layout exactly (same dimensions and positions)
- All diagram types supported:
  - **Use Case diagrams**: Actors as stick figures, use cases as ellipses
  - **Class diagrams**: Classes with compartments, interfaces, enumerations
  - **Component diagrams**: Components with provided/required interfaces
  - **State Machine diagrams**: States with rounded rectangles, transitions with arrows
- Proper UML notation:
  - Hollow triangles for generalization/realization
  - Hollow/filled diamonds for aggregation/composition
  - Dashed lines for dependencies
  - Solid/dashed lines based on relationship type
  - Stereotypes displayed on relationships (e.g., «extend», «include»)
  - State activities (entry/do/exit) shown inside states
  - Transition labels with events and guard conditions
- Improved arrow rendering with edge intersection calculations
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
pip install -r requirements.txt
```

Core dependencies:
- `PyYAML` - Configuration file support
- `graphviz` - Diagram generation
- `Pillow` - Image processing for diagrams
- `markdown` - HTML documentation generation

**Windows-only (for EA diagram extraction):**
```bash
pip install pywin32
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

## Future Enhancements

### 🔍 Search & Navigation (High Priority)
1. **Full-text search** - Searchable HTML documentation with client-side JavaScript search
2. **Navigation sidebar** - Collapsible tree view of all documentation sections
3. **Breadcrumb improvements** - Show element types and stereotypes in breadcrumbs
4. **Table of contents** - Auto-generate TOC for long documents
5. **Cross-reference links** - Auto-link element names mentioned in notes to their documentation
6. **"Back to top" links** - Quick navigation on long pages
7. **Recently viewed** - Track and show recently accessed documentation pages

### 📊 Additional Diagram Types
1. **Sequence diagrams** - Interaction diagrams showing message flows
2. **Activity diagrams** - Process flows and workflows
3. **Deployment diagrams** - System architecture and node relationships
4. **Package diagrams** - Package hierarchy and dependencies
5. **Timing diagrams** - Time-based behavior visualization
6. **Communication diagrams** - Collaboration between objects
7. **Interactive SVG diagrams** - Clickable diagram elements that link to documentation
8. **Diagram zoom/pan** - Viewer controls for large diagrams
9. **Mermaid diagram generation** - Generate Mermaid.js code for diagrams

### 📈 Traceability & Analysis (High Value)
1. **Traceability matrix** - Requirements → Use Cases → Classes → Tests
2. **Impact analysis** - Show what's affected by changes to an element
3. **Coverage reports** - Which requirements have use cases, which use cases have tests
4. **Dependency graph** - Visual graph of element dependencies
5. **Gap analysis** - Find missing relationships, undocumented elements
6. **Model metrics dashboard** - Complexity, coverage, documentation completeness
7. **Element usage tracking** - Where is this class/interface used?
8. **Orphan detection** - Find unreferenced elements

### 📝 Export & Integration
1. **PDF export** - Generate professional PDF documentation with table of contents
2. **MS Word/DocX export** - Corporate documentation format
3. **Confluence integration** - Push documentation directly to Confluence wiki
4. **SharePoint integration** - Sync with SharePoint document libraries
5. **LaTeX export** - For academic/scientific documentation
6. **API documentation** - Generate OpenAPI/Swagger specs from interfaces
7. **Multiple language support** - Generate docs in multiple languages
8. **Custom CSS themes** - Allow users to customize HTML styling

### ✅ Quality & Validation
1. **Model validation rules** - Check EA modeling best practices
   - Naming conventions (PascalCase for classes, camelCase for attributes)
   - Required stereotypes for specific element types
   - Mandatory documentation for public elements
   - Relationship consistency checks
2. **Spelling checker** - Check element names and notes for typos
3. **Consistency checks** - Verify naming patterns across packages
4. **Documentation coverage** - Report on elements without notes
5. **Broken link detection** - Find references to non-existent elements
6. **Duplicate detection** - Find elements with duplicate names or similar purposes

### 🎨 Customization & Templates
1. **Custom documentation templates** - User-defined Jinja2 templates for all element types
2. **Template library** - Pre-built templates for different documentation styles
3. **Conditional sections** - Show/hide sections based on stereotypes or tags
4. **Custom styling** - CSS customization for HTML output
5. **Logo and branding** - Add company logo to documentation
6. **Header/footer customization** - Custom headers and footers
7. **Custom metadata fields** - Support for EA tagged values in documentation

### 🔄 Version Control & Comparison
1. **Side-by-side diff viewer** - Visual comparison of two documentation versions in HTML
2. **Model timeline** - Show evolution of model over time
3. **Change notifications** - Email notifications when elements change
4. **Version annotations** - Tag documentation with version numbers
5. **Baseline comparison** - Compare current model against baseline
6. **Change approval workflow** - Review and approve documentation changes

### 🎯 Filtering & Scoping
1. **Package filtering** - Generate docs for specific packages only
2. **Stereotype filtering** - Document only elements with specific stereotypes
3. **Status filtering** - Filter by element status (Proposed, Approved, Implemented)
4. **Tag-based filtering** - Use EA tags to control what gets documented
5. **Custom queries** - SQL queries to select elements for documentation
6. **Baseline filtering** - Document only changes since last baseline

### 🔧 Advanced Features
1. **Incremental generation** - Only regenerate changed documentation
2. **Parallel processing** - Multi-threaded documentation generation
3. **Watch mode** - Auto-regenerate when .qea file changes
4. **Glossary generation** - Extract and document domain terms
5. **Index generation** - Alphabetical index of all elements
6. **Acronym list** - Auto-detect and list acronyms
7. **UML visibility symbols** - Show +, -, #, ~ for public/private/protected/package
8. **Method signatures** - Full signatures with return types and parameters
9. **Inheritance tree** - Show class hierarchy visually
10. **Interface implementation matrix** - Which classes implement which interfaces

### 🌐 Web Portal Features
1. **Static site generator** - Generate complete documentation website
2. **Dark mode** - Toggle between light and dark themes
3. **Responsive design** - Mobile-friendly documentation
4. **Print optimization** - CSS for clean printing
5. **Bookmark functionality** - Allow users to bookmark pages
6. **Comment system** - Allow team members to comment on documentation
7. **Version selector** - Switch between different documentation versions

### 🧪 Testing & Quality Assurance
1. **Link validation** - Verify all internal links work
2. **Image validation** - Check all diagram images exist and render
3. **HTML validation** - W3C compliance checking
4. **Accessibility audit** - WCAG compliance for HTML docs
5. **Performance metrics** - Track generation time and optimization opportunities
6. **Spell check integration** - Automated spell checking in CI/CD

### 🔌 Tool Integration
1. **JIRA integration** - Link requirements to JIRA issues
2. **Git integration** - Track which code files implement which classes
3. **PlantUML export** - Generate PlantUML text from diagrams
4. **Archimate export** - Convert to enterprise architecture format
5. **XMI import/export** - Standard UML model exchange
6. **CSV export** - Export element lists to CSV for analysis in Excel

---

## Quick Wins (2-4 Hours Each)

These enhancements offer high value with relatively low implementation effort:

### 1. ⚡ UML Visibility Symbols (2 hours)
**Impact:** Better UML compliance, easier to scan class documentation
**Effort:** Modify class_generator.py to add +/−/#/~ symbols
**Files:** `sparx_ea_doc/generators/class_generator.py`

### 2. ⚡ Table of Contents for Long Documents (2 hours)
**Impact:** Much easier navigation on long use case/class pages
**Effort:** Add TOC generation to HTML generator using markdown extension
**Files:** `sparx_ea_doc/html_generator.py`

### 3. ⚡ Index Page Generation (3 hours)
**Impact:** Alphabetical index makes finding elements easy
**Effort:** Create new generator that builds A-Z index of all elements
**Files:** New `sparx_ea_doc/generators/index_generator.py`

### 4. ⚡ CSV Export for Requirements (2 hours)
**Impact:** Stakeholders can analyze requirements in Excel
**Effort:** Add CSV output option to requirement_generator
**Files:** `sparx_ea_doc/generators/requirement_generator.py`

### 5. ⚡ Dark Mode Toggle (3 hours)
**Impact:** Better reading experience, modern UI
**Effort:** Add CSS dark theme + JavaScript toggle to HTML template
**Files:** `sparx_ea_doc/html_generator.py`

### 6. ⚡ Enhanced Traceability Report (4 hours)
**Impact:** High-value matrix showing Requirements → Use Cases → Classes
**Effort:** Create new report generator with matrix visualization
**Files:** New `sparx_ea_doc/generators/traceability_generator.py`

### 7. ⚡ Package Filtering via CLI (2 hours)
**Impact:** Generate docs for specific packages only (faster, focused)
**Effort:** Add `--packages` CLI argument with filtering logic
**Files:** `sparx_doc_generator.py`, `sparx_ea_doc/extractor.py`

### 8. ⚡ Print-Friendly CSS (2 hours)
**Impact:** Professional printed documentation
**Effort:** Add `@media print` CSS rules to HTML generator
**Files:** `sparx_ea_doc/html_generator.py`

### 9. ⚡ Glossary Generator (3 hours)
**Impact:** Auto-generate glossary from tagged terms
**Effort:** Extract terms from element notes, build glossary page
**Files:** New `sparx_ea_doc/generators/glossary_generator.py`

### 10. ⚡ Link Validation (3 hours)
**Impact:** Catch broken internal links before publishing
**Effort:** Add post-generation validation script
**Files:** New `validate_links.py`

---

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

**Last Updated**: 2025-11-12
**Current Branch**: develop
**Latest Feature**: EA diagram extraction utility with COM automation
**Status**: All tests passing ✅
**Key Features**:
- Windows COM automation for extracting diagrams directly from EA
- Configurable EA diagrams directory (YAML, CLI, GUI)
- HTML documentation generation with native Python
- Pixel-perfect diagrams matching EA layout exactly
- All diagram types supported (use cases, classes, components, state machines)
- Breadcrumb navigation on all pages
- Documentation change tracking with visual diff markup
- Class documentation shows associated diagrams
- Regression testing with golden baseline
