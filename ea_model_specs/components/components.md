# Component Specification
## EA Documentation Generator

---

## System Architecture

The EA Documentation Generator follows a modular architecture with clear separation of concerns:

```
┌─────────────────────────────────────────────────────────────┐
│                    Presentation Layer                        │
│  ┌──────────────────┐         ┌──────────────────┐         │
│  │  CLI Interface   │         │  GUI Interface   │         │
│  │ (sparx_doc_      │         │ (sparx_doc_      │         │
│  │  generator.py)   │         │  gui.py)         │         │
│  └────────┬─────────┘         └────────┬─────────┘         │
└───────────┼──────────────────────────────┼──────────────────┘
            │                              │
            ▼                              ▼
┌─────────────────────────────────────────────────────────────┐
│                  Application Layer                           │
│  ┌──────────────────────────────────────────────────────┐  │
│  │              Orchestration Service                    │  │
│  │  - Configuration Management                           │  │
│  │  - Workflow Coordination                              │  │
│  │  - Error Handling                                     │  │
│  └──────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
            │
            ▼
┌─────────────────────────────────────────────────────────────┐
│                    Business Logic Layer                      │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐     │
│  │  Extractor   │  │  Generators  │  │  Renderers   │     │
│  │              │  │              │  │              │     │
│  │ - Extract    │  │ - UseCase    │  │ - Diagram    │     │
│  │   model data │  │ - Class      │  │   Renderer   │     │
│  │              │  │ - Component  │  │ - Template   │     │
│  │              │  │ - StateMach  │  │   Renderer   │     │
│  │              │  │ - Requiremnt │  │              │     │
│  └──────────────┘  └──────────────┘  └──────────────┘     │
│                                                              │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐     │
│  │  Analyzers   │  │  Converters  │  │  Utilities   │     │
│  │              │  │              │  │              │     │
│  │ - Quality    │  │ - HTML       │  │ - Text       │     │
│  │   Reporter   │  │   Generator  │  │   Cleaning   │     │
│  │ - Diff       │  │ - Markdown   │  │ - Filename   │     │
│  │   Generator  │  │   Processor  │  │   Sanitize   │     │
│  └──────────────┘  └──────────────┘  └──────────────┘     │
└─────────────────────────────────────────────────────────────┘
            │
            ▼
┌─────────────────────────────────────────────────────────────┐
│                    Data Access Layer                         │
│  ┌──────────────────────────────────────────────────────┐  │
│  │           Database Access Component                   │  │
│  │  - SQLite Connection Management                       │  │
│  │  - Query Execution                                    │  │
│  │  - Schema Analysis                                    │  │
│  └──────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
            │
            ▼
┌─────────────────────────────────────────────────────────────┐
│                    External Systems                          │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐     │
│  │  .qea Files  │  │  EA COM API  │  │  File System │     │
│  │  (SQLite DB) │  │  (Windows)   │  │              │     │
│  └──────────────┘  └──────────────┘  └──────────────┘     │
└─────────────────────────────────────────────────────────────┘
```

---

## Component Catalog

### COMP-001: SparxExtractor
**Type:** Core Business Logic
**Package:** sparx_ea_doc
**File:** sparx_ea_doc/extractor.py
**Related Requirements:** FR-001, FR-001.1 through FR-001.6, NFR-001, NFR-002
**Related Use Cases:** UC-002

**Description:**
Central component responsible for extracting all model data from .qea SQLite database files. Performs database connection, schema analysis, element extraction, relationship resolution, and text cleaning.

**Provided Interfaces:**
- `IModelExtractor` - Main extraction interface

**Required Interfaces:**
- `ISQLiteConnection` - Database connectivity
- `ITextCleaner` - Text processing utilities

**Responsibilities:**
- Connect to .qea database files
- Extract packages and namespace structure
- Extract use cases, actors, and relationships
- Extract state machines, states, and transitions
- Extract components, interfaces, and ports
- Extract classes, attributes, operations, and relationships
- Extract requirements and their relationships
- Extract diagram metadata
- Resolve foreign key relationships
- Clean and normalize text content
- Sanitize filenames

**Key Operations:**
- `connect(qea_path: str) -> bool`
- `extract_packages() -> List[Package]`
- `extract_use_cases() -> List[UseCase]`
- `extract_state_machines() -> List[StateMachine]`
- `extract_components() -> List[Component]`
- `extract_classes() -> List[Class]`
- `extract_requirements() -> List[Requirement]`
- `extract_diagrams() -> List[Diagram]`
- `resolve_relationships() -> None`

**Dependencies:**
- Python sqlite3 module
- utils module (text cleaning, filename sanitization)
- models module (data classes)

**Configuration:**
- Minimum description length for quality checks
- Include/exclude private elements
- Extract tagged values option

---

### COMP-002: DocumentationGenerators
**Type:** Core Business Logic
**Package:** sparx_ea_doc.generators
**Files:**
- sparx_ea_doc/generators/use_case_generator.py
- sparx_ea_doc/generators/class_generator.py
- sparx_ea_doc/generators/component_generator.py
- sparx_ea_doc/generators/state_machine_generator.py
- sparx_ea_doc/generators/requirement_generator.py

**Related Requirements:** FR-002, FR-002.1, FR-002.3, FR-008
**Related Use Cases:** UC-001

**Description:**
Collection of generator components that produce markdown documentation for different element types. Each generator is responsible for one element type and follows a common pattern.

**Provided Interfaces:**
- `IDocumentationGenerator` - Common generator interface

**Required Interfaces:**
- `ITemplateRenderer` - Template processing
- `IModelData` - Extracted model data
- `IBreadcrumbGenerator` - Navigation generation

**Sub-Components:**

#### UseCaseGenerator
**Responsibilities:**
- Generate use case documentation
- Create actor catalog
- Document use case relationships (include, extend)
- Generate scenario documentation
- Link to related requirements

**Key Operations:**
- `generate() -> None`
- `_generate_use_case_docs(uc_dir: Path) -> None`
- `_generate_single_use_case(uc: UseCase, file: Path) -> str`
- `_generate_actors_doc(uc_dir: Path) -> None`

#### ClassGenerator
**Responsibilities:**
- Generate class documentation
- Organize by package structure
- Document attributes and operations
- Document relationships (inheritance, association, etc.)
- Show which diagrams contain each class

**Key Operations:**
- `generate() -> None`
- `_generate_class_docs(class_dir: Path) -> None`
- `_generate_single_class(cls: Class, file: Path) -> str`

#### ComponentGenerator
**Responsibilities:**
- Generate component documentation
- Document provided and required interfaces
- Document ports and connectors
- Document component dependencies

**Key Operations:**
- `generate() -> None`
- `_generate_component_docs(comp_dir: Path) -> None`
- `_generate_single_component(comp: Component, file: Path) -> str`

#### StateMachineGenerator
**Responsibilities:**
- Generate state machine documentation
- Document states and transitions
- Document state hierarchy
- Document activities and guards

**Key Operations:**
- `generate() -> None`
- `_generate_state_machine_docs(sm_dir: Path) -> None`
- `_generate_single_state_machine(sm: StateMachine, file: Path) -> str`

#### RequirementGenerator
**Responsibilities:**
- Generate requirement documentation
- Group by stereotype
- Link to related use cases
- Show priority and status

**Key Operations:**
- `generate() -> None`
- `_generate_requirement_docs(req_dir: Path) -> None`
- `_generate_single_requirement(req: Requirement, file: Path) -> str`

**Common Dependencies:**
- TemplateRenderer (optional, falls back to hard-coded)
- utils module (breadcrumbs, filename generation)
- models module (data classes)

---

### COMP-003: DiagramRenderer
**Type:** Core Business Logic
**Package:** sparx_ea_doc
**File:** sparx_ea_doc/diagram_renderer.py
**Related Requirements:** FR-003, FR-003.1 through FR-003.4
**Related Use Cases:** UC-003

**Description:**
Renders UML diagrams as PNG images using PIL/Pillow. Generates pixel-perfect diagrams matching Enterprise Architect's layout and dimensions.

**Provided Interfaces:**
- `IDiagramRenderer` - Main rendering interface

**Required Interfaces:**
- `IModelData` - Diagram metadata and elements
- `IImageLibrary` - PIL/Pillow for image generation

**Responsibilities:**
- Render use case diagrams (actors, use cases, relationships)
- Render class diagrams (classes, relationships, stereotypes)
- Render component diagrams (components, interfaces)
- Render state machine diagrams (states, transitions)
- Calculate element positions from EA coordinates
- Draw UML notation correctly (arrows, diamonds, triangles)
- Label relationships with stereotypes and cardinality
- Save diagrams as PNG files

**Key Operations:**
- `render_diagram(diagram: Diagram, elements: List[Element]) -> str`
- `_render_use_case_diagram() -> Image`
- `_render_class_diagram() -> Image`
- `_render_component_diagram() -> Image`
- `_render_state_machine_diagram() -> Image`
- `_draw_element(element: Element, image: Image) -> None`
- `_draw_connector(connector: Connector, image: Image) -> None`
- `_calculate_arrow_endpoint(start, end, shape) -> Point`

**Dependencies:**
- PIL/Pillow library
- models module (diagram data)

**Configuration:**
- Diagram output directory
- Image format (PNG)
- Default colors and styles

**Visual Elements:**
- Actors: Stick figures
- Use Cases: Ellipses
- Classes: Rectangles with compartments
- Components: Rectangles with component icon
- States: Rounded rectangles
- Arrows: Lines with various endpoint shapes
- Stereotypes: Guillemet notation (« »)

---

### COMP-004: HTMLGenerator
**Type:** Output Converter
**Package:** sparx_ea_doc
**File:** sparx_ea_doc/html_generator.py
**Related Requirements:** FR-002.2
**Related Use Cases:** UC-004

**Description:**
Converts markdown documentation to HTML with embedded CSS styling. Provides responsive design for all screen sizes.

**Provided Interfaces:**
- `IHTMLConverter` - Markdown to HTML conversion

**Required Interfaces:**
- `IMarkdownProcessor` - Python markdown library

**Responsibilities:**
- Convert markdown files to HTML
- Embed CSS for professional styling
- Convert breadcrumb navigation to HTML links
- Apply responsive image CSS
- Copy diagram images to HTML output directory
- Generate HTML index pages

**Key Operations:**
- `generate_html(markdown_dir: Path, html_dir: Path) -> None`
- `_convert_markdown_file(md_file: Path) -> str`
- `_embed_css(html_content: str) -> str`
- `_copy_diagrams(src_dir: Path, dst_dir: Path) -> None`

**Dependencies:**
- Python markdown library
- File system operations

**Configuration:**
- HTML output directory
- CSS theme
- Image scaling options

**CSS Features:**
- Embedded CSS (no external files)
- Responsive design with media queries
- Proper image scaling without horizontal overflow
- Print-friendly styles
- Professional typography

---

### COMP-005: QualityReporter
**Type:** Analysis Component
**Package:** sparx_ea_doc
**File:** sparx_ea_doc/quality_reporter.py
**Related Requirements:** FR-006, NFR-004
**Related Use Cases:** UC-006, UC-010

**Description:**
Analyzes documentation quality and generates quality reports. Identifies undocumented elements and calculates coverage metrics.

**Provided Interfaces:**
- `IQualityAnalyzer` - Quality analysis interface

**Required Interfaces:**
- `IModelData` - Extracted elements for analysis

**Responsibilities:**
- Identify elements without documentation
- Calculate documentation coverage percentage
- Generate element statistics
- Identify orphaned elements
- Create dependency reports
- Generate quality report markdown

**Key Operations:**
- `analyze_quality() -> QualityMetrics`
- `generate_quality_report() -> str`
- `generate_dependency_report() -> str`
- `_check_element_documentation(element: Element) -> bool`
- `_calculate_coverage() -> float`

**Dependencies:**
- models module (element data)
- utils module (file writing)

**Output:**
- quality-report.md (statistics and issues)
- dependencies.md (dependency graph)

---

### COMP-006: DiffGenerator
**Type:** Analysis Component
**Package:** sparx_ea_doc
**File:** sparx_ea_doc/diff_generator.py
**Related Requirements:** FR-005
**Related Use Cases:** UC-005

**Description:**
Tracks changes between documentation versions and generates visual diff reports.

**Provided Interfaces:**
- `IDiffTracker` - Change tracking interface

**Required Interfaces:**
- `IFileSystem` - File operations

**Responsibilities:**
- Create version snapshots
- Compare documentation versions
- Generate diff reports with visual markup
- Calculate change statistics
- Manage version history

**Key Operations:**
- `create_snapshot(docs_dir: Path, version: str) -> None`
- `compare_versions(old_ver: str, new_ver: str) -> DiffReport`
- `generate_diff_markup(old: str, new: str) -> str`
- `get_change_statistics() -> Dict[str, int]`

**Dependencies:**
- Python difflib module
- File system operations

**Output:**
- Version snapshots in docs_history/
- Diff-annotated docs in docs_diff/
- Change summary reports

**Visual Markup:**
- Additions: `[+Added content+]`
- Deletions: `[-Deleted content-]`
- Modifications: `[~Modified content~]`

---

### COMP-007: TemplateRenderer
**Type:** Rendering Component
**Package:** sparx_ea_doc
**File:** sparx_ea_doc/template_renderer.py
**Related Requirements:** FR-008
**Related Use Cases:** UC-001

**Description:**
Renders documentation using customizable Jinja2-style templates. Supports conditional sections and variable substitution.

**Provided Interfaces:**
- `ITemplateEngine` - Template rendering

**Required Interfaces:**
- None (self-contained)

**Responsibilities:**
- Load templates from template directory
- Substitute variables in templates
- Handle conditional sections
- Support loops and iterations
- Fall back gracefully if template missing

**Key Operations:**
- `load_template(name: str) -> str`
- `render(template: str, data: Dict) -> str`
- `_substitute_variables(template: str, data: Dict) -> str`
- `_process_conditionals(template: str, data: Dict) -> str`

**Dependencies:**
- Template files in templates/ directory

**Template Syntax:**
- Variables: `{{variable_name}}`
- Conditionals: `{{#if condition}}...{{/if}}`
- Loops: `{{#for item in items}}...{{/for}}`

---

### COMP-008: EADiagramExtractor
**Type:** Integration Component
**File:** ea_diagram_extractor.py
**Related Requirements:** FR-004.1
**Related Use Cases:** UC-007
**Platform:** Windows only

**Description:**
Windows COM automation utility that connects to Enterprise Architect and extracts all diagrams in GUID-timestamp format.

**Provided Interfaces:**
- `IEAAutomation` - EA COM interface

**Required Interfaces:**
- `IEARepository` - EA COM API (win32com)

**Responsibilities:**
- Initialize COM connection to EA
- Open .qea model files
- Iterate through all diagrams
- Export diagrams as PNG in GUID-timestamp format
- Handle COM errors gracefully
- Clean up COM resources

**Key Operations:**
- `connect_ea() -> bool`
- `open_model(qea_path: str) -> bool`
- `extract_all_diagrams(output_dir: Path) -> int`
- `export_diagram(diagram, output_dir: Path) -> str`
- `cleanup() -> None`

**Dependencies:**
- pywin32 (win32com.client)
- Enterprise Architect installed

**Platform Limitations:**
- Windows only (COM automation)
- Requires EA installation

---

### COMP-009: Utils
**Type:** Utility Component
**Package:** sparx_ea_doc
**File:** sparx_ea_doc/utils.py
**Related Requirements:** FR-002.3, NFR-002
**Related Use Cases:** All

**Description:**
Collection of utility functions for text processing, filename generation, and navigation.

**Provided Interfaces:**
- `ITextCleaner` - Text cleaning operations
- `IFilenameSanitizer` - Filename generation
- `IBreadcrumbGenerator` - Navigation generation

**Responsibilities:**
- Clean text content (handle multiple encodings)
- Remove HTML tags and entities
- Sanitize filenames (remove invalid characters)
- Generate object ID-based filenames
- Generate breadcrumb navigation
- Format section names

**Key Operations:**
- `clean_text_content(text: str, remove_html: bool) -> str`
- `sanitize_filename(name: str) -> str`
- `generate_filename_with_id(name: str, object_id: int, prefix: str, ext: str) -> str`
- `generate_breadcrumbs(file_path: Path, output_dir: Path, title: str) -> str`

**Features:**
- Multi-encoding support (UTF-8, Windows-1252, ISO-8859-1, CP1252)
- Unicode normalization (NFKD, NFKC)
- Control character removal
- Null byte removal
- BOM removal
- Platform-safe filenames

---

### COMP-010: Models
**Type:** Data Component
**Package:** sparx_ea_doc
**File:** sparx_ea_doc/models.py
**Related Requirements:** All (data structures)
**Related Use Cases:** All

**Description:**
Data classes representing EA model elements.

**Provided Interfaces:**
- Data classes for all element types

**Classes:**
- `Element` - Base class for all elements
- `UseCase` - Use case element
- `Actor` - Actor element
- `StateMachine` - State machine element
- `State` - State element
- `Transition` - State transition
- `Component` - Component element
- `Class` - Class element
- `Attribute` - Class attribute
- `Operation` - Class operation
- `Requirement` - Requirement element
- `Diagram` - Diagram metadata
- `Connector` - Relationship connector
- `Package` - Package/namespace

**Responsibilities:**
- Store extracted data
- Provide clean accessors (e.g., `clean_note()`)
- Parse structured notes
- Maintain relationships

---

## Component Dependencies

```
CLI/GUI
   ↓
Orchestrator
   ↓
   ├──→ SparxExtractor ──→ Utils ──→ Models
   ├──→ DocumentationGenerators ──→ TemplateRenderer
   │        ↓
   │     Utils, Models
   ├──→ DiagramRenderer ──→ Models
   ├──→ HTMLGenerator
   ├──→ QualityReporter ──→ Models
   ├──→ DiffGenerator
   └──→ EADiagramExtractor (Windows)
```

---

## Deployment View

```
┌─────────────────────────────────────┐
│       Development Environment        │
│  ┌──────────────────────────────┐   │
│  │  Python 3.7+ Runtime         │   │
│  └──────────────────────────────┘   │
│  ┌──────────────────────────────┐   │
│  │  EATools Package             │   │
│  │  - sparx_doc_generator.py    │   │
│  │  - sparx_doc_gui.py          │   │
│  │  - ea_diagram_extractor.py   │   │
│  │  - sparx_ea_doc/             │   │
│  └──────────────────────────────┘   │
│  ┌──────────────────────────────┐   │
│  │  Dependencies                │   │
│  │  - PyYAML                    │   │
│  │  - Pillow                    │   │
│  │  - markdown                  │   │
│  │  - pywin32 (Windows)         │   │
│  └──────────────────────────────┘   │
└─────────────────────────────────────┘
            ↓
┌─────────────────────────────────────┐
│      CI/CD Pipeline (Optional)       │
│  ┌──────────────────────────────┐   │
│  │  Automated Documentation     │   │
│  │  Generation                  │   │
│  └──────────────────────────────┘   │
└─────────────────────────────────────┘
            ↓
┌─────────────────────────────────────┐
│       Output Artifacts               │
│  ┌──────────────────────────────┐   │
│  │  docs/ (Markdown)            │   │
│  │  docs_html/ (HTML)           │   │
│  │  docs_history/ (Snapshots)   │   │
│  │  docs_diff/ (Diffs)          │   │
│  └──────────────────────────────┘   │
└─────────────────────────────────────┘
```

---

## Interface Catalog

### IModelExtractor
**Operations:**
- `connect(qea_path: str) -> bool`
- `extract_all() -> None`
- `get_use_cases() -> List[UseCase]`
- `get_state_machines() -> List[StateMachine]`
- `get_components() -> List[Component]`
- `get_classes() -> List[Class]`
- `get_requirements() -> List[Requirement]`

### IDocumentationGenerator
**Operations:**
- `generate() -> None`
- `set_output_dir(path: Path) -> None`
- `set_template_dir(path: Path) -> None`

### IDiagramRenderer
**Operations:**
- `render_diagram(diagram: Diagram) -> Path`
- `set_output_dir(path: Path) -> None`

### IHTMLConverter
**Operations:**
- `generate_html(markdown_dir: Path, html_dir: Path) -> None`

### IQualityAnalyzer
**Operations:**
- `analyze_quality() -> QualityMetrics`
- `generate_report() -> str`

### ITemplateEngine
**Operations:**
- `load_template(name: str) -> str`
- `render(template: str, data: Dict) -> str`

### ITextCleaner
**Operations:**
- `clean_text_content(text: str, remove_html: bool) -> str`

### IFilenameSanitizer
**Operations:**
- `sanitize_filename(name: str) -> str`
- `generate_filename_with_id(name: str, id: int, prefix: str, ext: str) -> str`

### IBreadcrumbGenerator
**Operations:**
- `generate_breadcrumbs(file_path: Path, output_dir: Path, title: str) -> str`
