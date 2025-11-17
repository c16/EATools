# Requirements Specification
## EA Documentation Generator

---

## Functional Requirements

### FR-001: Data Extraction from EA Models
**Priority:** High
**Status:** Implemented
**Description:** The system shall extract model data from Sparx Enterprise Architect .qea database files.

**Related Use Cases:** UC-002, UC-007

**Sub-Requirements:**

#### FR-001.1: SQLite Database Connection
**Description:** Connect to and query .qea SQLite database files.
**Acceptance Criteria:**
- Successfully open .qea files
- Handle database connection errors gracefully
- Support read-only access

#### FR-001.2: Use Case Extraction
**Description:** Extract use case elements, actors, and relationships.
**Acceptance Criteria:**
- Extract use case elements with notes and stereotypes
- Extract actor elements
- Extract include/extend/association relationships
- Parse pre/post conditions from structured notes

#### FR-001.3: State Machine Extraction
**Description:** Extract state machine elements including states and transitions.
**Acceptance Criteria:**
- Extract all state types (initial, final, composite)
- Extract transitions with triggers, guards, and actions
- Preserve state hierarchy
- Extract entry/do/exit activities

#### FR-001.4: Component Extraction
**Description:** Extract component elements and their interfaces.
**Acceptance Criteria:**
- Extract component elements with stereotypes
- Extract provided and required interfaces
- Extract ports and connectors
- Extract component dependencies

#### FR-001.5: Class Extraction
**Description:** Extract class elements with attributes, operations, and relationships.
**Acceptance Criteria:**
- Extract classes, interfaces, and enumerations
- Extract attributes with types, visibility, and defaults
- Extract operations with parameters and return types
- Extract inheritance, association, aggregation, composition relationships

#### FR-001.6: Diagram Metadata Extraction
**Description:** Extract diagram information and element-diagram associations.
**Acceptance Criteria:**
- Extract diagram names and types
- Link elements to their containing diagrams
- Extract diagram dimensions and layout information

---

### FR-002: Documentation Generation
**Priority:** High
**Status:** Implemented
**Description:** Generate comprehensive documentation in multiple formats.

**Related Use Cases:** UC-001, UC-004

**Sub-Requirements:**

#### FR-002.1: Markdown Documentation
**Description:** Generate structured markdown documentation with hierarchical organization.
**Acceptance Criteria:**
- Generate markdown files for all element types
- Organize by package/namespace structure
- Include breadcrumb navigation
- Generate index files for each section

#### FR-002.2: HTML Documentation
**Description:** Convert markdown to HTML with professional styling.
**Acceptance Criteria:**
- Generate HTML from markdown
- Embed CSS for consistent styling
- Support responsive design for all screen sizes
- Preserve breadcrumb navigation as HTML links

#### FR-002.3: Breadcrumb Navigation
**Description:** Generate breadcrumb navigation showing document hierarchy.
**Acceptance Criteria:**
- Show path from root to current page
- Generate correct relative links
- Format directory names appropriately

#### FR-002.4: Quality Reports
**Description:** Generate quality analysis reports.
**Acceptance Criteria:**
- Identify undocumented elements
- Calculate documentation coverage
- Generate element statistics
- Create dependency reports

---

### FR-003: Diagram Rendering
**Priority:** High
**Status:** Implemented
**Description:** Render UML diagrams from extracted model data.

**Related Use Cases:** UC-003

**Sub-Requirements:**

#### FR-003.1: Use Case Diagram Rendering
**Description:** Render use case diagrams with actors and use cases.
**Acceptance Criteria:**
- Draw actors as stick figures
- Draw use cases as ellipses
- Show include/extend relationships with stereotypes
- Show associations between actors and use cases

#### FR-003.2: Class Diagram Rendering
**Description:** Render class diagrams with relationships.
**Acceptance Criteria:**
- Draw classes with compartments (attributes, operations)
- Show inheritance with hollow triangles
- Show associations with cardinality
- Show aggregation/composition with diamonds
- Show interfaces and realizations

#### FR-003.3: Component Diagram Rendering
**Description:** Render component diagrams with interfaces.
**Acceptance Criteria:**
- Draw components as rectangles with component icon
- Show provided interfaces (lollipop notation)
- Show required interfaces (socket notation)
- Show dependencies between components

#### FR-003.4: State Machine Diagram Rendering
**Description:** Render state machine diagrams with transitions.
**Acceptance Criteria:**
- Draw states as rounded rectangles
- Show initial and final states
- Draw transitions with arrows
- Label transitions with events and guards
- Show activities inside states (entry/do/exit)

---

### FR-004: EA Diagram Integration
**Priority:** Medium
**Status:** Implemented
**Description:** Support integration with EA-exported diagrams for pixel-perfect accuracy.

**Related Use Cases:** UC-007

**Sub-Requirements:**

#### FR-004.1: COM Automation for Diagram Extraction
**Description:** Use Windows COM automation to extract diagrams directly from EA.
**Acceptance Criteria:**
- Connect to EA application via COM
- Open .qea model files
- Export all diagrams in GUID-timestamp format
- Handle COM errors gracefully
- Windows-only functionality

#### FR-004.2: EA-Exported Diagram Usage
**Description:** Use EA-exported diagrams when available, fall back to rendering.
**Acceptance Criteria:**
- Check for EA-exported diagrams by GUID
- Use EA diagram if available
- Fall back to rendering if not available
- Support configurable diagram directory

---

### FR-005: Change Tracking
**Priority:** Medium
**Status:** Implemented
**Description:** Track changes between documentation versions.

**Related Use Cases:** UC-005

**Acceptance Criteria:**
- Create version snapshots of documentation
- Compare documentation versions
- Generate diff reports with visual markup
- Show additions, deletions, and modifications
- Generate change summary statistics

---

### FR-006: Quality Analysis
**Priority:** Medium
**Status:** Implemented
**Description:** Analyze model quality and documentation completeness.

**Related Use Cases:** UC-006, UC-010

**Acceptance Criteria:**
- Identify elements without documentation
- Calculate documentation coverage percentage
- Generate element count statistics
- Identify orphaned elements
- Create dependency analysis reports

---

### FR-007: Configuration Management
**Priority:** Medium
**Status:** Implemented
**Description:** Support flexible configuration options.

**Related Use Cases:** UC-008

**Acceptance Criteria:**
- Support YAML configuration files
- Support command-line arguments
- Configuration hierarchy: CLI > YAML > defaults
- Validate configuration options

---

### FR-008: Template System
**Priority:** Low
**Status:** Implemented
**Description:** Support customizable documentation templates.

**Related Use Cases:** UC-001

**Acceptance Criteria:**
- Load templates from template directory
- Support conditional sections in templates
- Fall back to hard-coded generation if template fails
- Support template variables and loops

---

## Non-Functional Requirements

### NFR-001: Performance
**Priority:** High
**Status:** Implemented
**Description:** The system shall handle large models efficiently.

**Related Use Cases:** UC-001, UC-002

**Acceptance Criteria:**
- Process models with 1000+ elements in reasonable time (< 5 minutes)
- Use efficient SQL queries
- Minimize memory usage
- Support incremental generation (future)

---

### NFR-002: Robustness
**Priority:** High
**Status:** Implemented
**Description:** The system shall handle problematic input data gracefully.

**Acceptance Criteria:**
- Handle multiple text encodings (UTF-8, Windows-1252, ISO-8859-1, CP1252)
- Remove null bytes and control characters
- Sanitize filenames (remove tabs, newlines, unprintable characters)
- Handle missing or null database values
- Never crash due to encoding errors

---

### NFR-003: Compatibility
**Priority:** High
**Status:** Implemented
**Description:** The system shall support standard EA database formats.

**Acceptance Criteria:**
- Support .qea (SQLite) format
- Work on Windows, Linux, and macOS
- Support Python 3.7+
- Handle EA database schema variations

---

### NFR-004: Maintainability
**Priority:** Medium
**Status:** Implemented
**Description:** The system shall be modular and maintainable.

**Acceptance Criteria:**
- Modular package structure
- Separate generators for each element type
- Clear separation of concerns
- Comprehensive regression testing
- Self-documenting code with docstrings

---

### NFR-005: Usability
**Priority:** Medium
**Status:** Implemented
**Description:** The system shall be easy to use.

**Acceptance Criteria:**
- Command-line interface with clear options
- GUI for non-technical users
- Helpful error messages
- Verbose mode for debugging
- Sensible defaults

---

### NFR-006: Testability
**Priority:** Medium
**Status:** Implemented
**Description:** The system shall be thoroughly testable.

**Acceptance Criteria:**
- Regression test suite with golden baseline
- Text cleaning test suite (29 test cases)
- Checksum-based verification
- Automated test execution
- Update mechanism for baseline

---

## Requirements Traceability Matrix

| Requirement | Use Cases | Status |
|------------|-----------|---------|
| FR-001 | UC-002, UC-007 | ✅ Implemented |
| FR-001.1 | UC-002 | ✅ Implemented |
| FR-001.2 | UC-002 | ✅ Implemented |
| FR-001.3 | UC-002 | ✅ Implemented |
| FR-001.4 | UC-002 | ✅ Implemented |
| FR-001.5 | UC-002 | ✅ Implemented |
| FR-001.6 | UC-002 | ✅ Implemented |
| FR-002 | UC-001, UC-004 | ✅ Implemented |
| FR-002.1 | UC-001 | ✅ Implemented |
| FR-002.2 | UC-004 | ✅ Implemented |
| FR-002.3 | UC-001, UC-004 | ✅ Implemented |
| FR-002.4 | UC-010 | ✅ Implemented |
| FR-003 | UC-003 | ✅ Implemented |
| FR-003.1 | UC-003 | ✅ Implemented |
| FR-003.2 | UC-003 | ✅ Implemented |
| FR-003.3 | UC-003 | ✅ Implemented |
| FR-003.4 | UC-003 | ✅ Implemented |
| FR-004 | UC-007 | ✅ Implemented |
| FR-004.1 | UC-007 | ✅ Implemented |
| FR-004.2 | UC-007 | ✅ Implemented |
| FR-005 | UC-005 | ✅ Implemented |
| FR-006 | UC-006, UC-010 | ✅ Implemented |
| FR-007 | UC-008 | ✅ Implemented |
| FR-008 | UC-001 | ✅ Implemented |
| NFR-001 | UC-001, UC-002 | ✅ Implemented |
| NFR-002 | All | ✅ Implemented |
| NFR-003 | All | ✅ Implemented |
| NFR-004 | All | ✅ Implemented |
| NFR-005 | UC-001, UC-008 | ✅ Implemented |
| NFR-006 | UC-009 | ✅ Implemented |
