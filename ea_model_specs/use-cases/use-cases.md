# Use Case Specification
## EA Documentation Generator

---

## Actors

### Primary Actors

**Software Developer**
- Role: Creates and maintains UML models in Enterprise Architect
- Goals: Generate up-to-date documentation from EA models
- Interactions: Runs command-line tool, reviews generated documentation

**Technical Writer**
- Role: Produces technical documentation for stakeholders
- Goals: Export EA models to documentation formats (HTML, Markdown)
- Interactions: Uses GUI application, configures output options

**Project Manager**
- Role: Oversees project documentation and quality
- Goals: Review documentation coverage and quality metrics
- Interactions: Reviews quality reports, tracks documentation changes

### Secondary Actors

**Enterprise Architect Application**
- Role: Source of UML model data
- Interactions: Provides .qea database files, exports diagrams via COM automation (Windows)

**CI/CD System**
- Role: Automated documentation generation in build pipeline
- Interactions: Executes command-line tool, validates output

---

## Use Cases

### UC-001: Generate Documentation
**ID:** UC-001
**Priority:** High
**Status:** Implemented
**Related Requirements:** FR-002, FR-002.1, FR-002.2, FR-002.3, FR-008, NFR-001, NFR-005

**Primary Actor:** Software Developer, Technical Writer

**Preconditions:**
- .qea model file exists and is accessible
- Python environment with required dependencies installed

**Postconditions:**
- Documentation generated in specified output directory
- Index files created for navigation
- Quality reports generated

**Main Flow:**
1. User invokes documentation generator with .qea file path
2. System validates .qea file exists
3. System connects to .qea database
4. System extracts model data (→ UC-002)
5. System renders diagrams (→ UC-003)
6. System generates markdown documentation
   - Use cases documentation
   - State machines documentation
   - Components documentation
   - Classes documentation
   - Requirements documentation
7. System generates breadcrumb navigation for all pages
8. System generates index files
9. System generates quality reports (→ UC-010)
10. If HTML output requested, system generates HTML (→ UC-004)
11. System displays summary of generated documentation
12. Documentation generation complete

**Alternative Flows:**

**3a. Database Connection Fails:**
- 3a.1. System displays error message with file path
- 3a.2. System exits with error code
- Use case ends

**5a. Diagram Rendering Fails:**
- 5a.1. System logs warning for failed diagram
- 5a.2. System continues with remaining diagrams
- Return to step 6

**11a. Template Rendering Fails:**
- 11a.1. System logs warning
- 11a.2. System falls back to hard-coded generation
- Return to step 12

**Extension Points:**
- Step 5: Use EA-exported diagrams if available (→ UC-007)
- Step 10: Track documentation changes (→ UC-005)

---

### UC-002: Extract Model Data
**ID:** UC-002
**Priority:** High
**Status:** Implemented
**Related Requirements:** FR-001, FR-001.1, FR-001.2, FR-001.3, FR-001.4, FR-001.5, FR-001.6, NFR-001, NFR-002

**Primary Actor:** System (Internal)

**Preconditions:**
- Database connection established
- .qea file is valid SQLite database

**Postconditions:**
- All model elements extracted and stored in memory
- Relationships between elements resolved
- Diagram associations established

**Main Flow:**
1. System queries database schema
2. System extracts packages and namespace structure
3. System extracts use case elements
   - Use cases with notes and stereotypes
   - Actors
   - Include/extend/association relationships
   - Pre/post conditions from structured notes
4. System extracts state machine elements
   - States (all types)
   - Transitions with triggers, guards, actions
   - State hierarchy
   - Activities (entry/do/exit)
5. System extracts component elements
   - Components with stereotypes
   - Provided and required interfaces
   - Ports and connectors
   - Dependencies
6. System extracts class elements
   - Classes, interfaces, enumerations
   - Attributes with types, visibility, defaults
   - Operations with parameters and return types
   - Inheritance and association relationships
7. System extracts requirement elements
   - Requirements with alias and priority
   - Related use cases
8. System extracts diagram metadata
   - Diagram names and types
   - Element-diagram associations
   - Diagram dimensions
9. System resolves all relationships
   - Foreign key lookups
   - Connector endpoints
   - Parent-child hierarchies
10. System cleans text content
    - Remove HTML tags
    - Decode HTML entities
    - Handle multiple encodings
    - Remove control characters
11. System sanitizes names for filenames
    - Remove tabs, newlines, unprintable characters
    - Unicode normalization
    - Generate object ID-based filenames
12. Extraction complete

**Alternative Flows:**

**3a. Encoding Errors in Notes:**
- 3a.1. System attempts multiple encodings (UTF-8, Windows-1252, ISO-8859-1, CP1252)
- 3a.2. System uses replacement for undecodable characters
- 3a.3. System removes problematic characters
- Return to step 4

**9a. Broken Relationship References:**
- 9a.1. System logs warning for missing target
- 9a.2. System skips broken relationship
- Return to step 10

**11a. Invalid Characters in Names:**
- 11a.1. System sanitizes filename
- 11a.2. System appends object ID to prevent clashes
- Return to step 12

---

### UC-003: Render Diagrams
**ID:** UC-003
**Priority:** High
**Status:** Implemented
**Related Requirements:** FR-003, FR-003.1, FR-003.2, FR-003.3, FR-003.4

**Primary Actor:** System (Internal)

**Preconditions:**
- Model data extracted
- Diagram metadata available
- PIL/Pillow library installed

**Postconditions:**
- PNG diagrams generated for all diagram types
- Diagrams saved to output directory
- Diagrams match EA layout dimensions

**Main Flow:**
1. System iterates through all diagrams
2. For each diagram, system determines diagram type
3. System creates blank image with EA dimensions
4. System renders diagram based on type:

   **For Use Case Diagrams:**
   - Draw actors as stick figures
   - Draw use cases as ellipses
   - Draw boundaries as rectangles
   - Draw relationships with stereotypes

   **For Class Diagrams:**
   - Draw classes as rectangles with compartments
   - Draw attributes and operations (limited to 10 each)
   - Draw inheritance with hollow triangles
   - Draw associations with cardinality
   - Draw aggregation/composition with diamonds

   **For Component Diagrams:**
   - Draw components as rectangles with icon
   - Draw interfaces (lollipop and socket notation)
   - Draw dependencies as dashed arrows

   **For State Machine Diagrams:**
   - Draw states as rounded rectangles
   - Draw initial/final states
   - Draw transitions with arrows
   - Label transitions with events and guards
   - Show activities inside states

5. System saves diagram as PNG
6. System updates diagram index
7. Repeat for all diagrams
8. Diagram rendering complete

**Alternative Flows:**

**2a. Unknown Diagram Type:**
- 2a.1. System logs warning
- 2a.2. System skips diagram
- Return to step 7

**5a. Save Fails:**
- 5a.1. System logs error with file path
- 5a.2. System continues with next diagram
- Return to step 7

---

### UC-004: Generate HTML Output
**ID:** UC-004
**Priority:** Medium
**Status:** Implemented
**Related Requirements:** FR-002.2, FR-002.3

**Primary Actor:** System (Internal)

**Preconditions:**
- Markdown documentation generated
- HTML output requested via CLI or config

**Postconditions:**
- HTML files generated in HTML output directory
- CSS embedded in HTML files
- Breadcrumb navigation converted to HTML links
- Images render correctly without overflow

**Main Flow:**
1. System creates HTML output directory
2. System copies diagram images to HTML directory
3. For each markdown file:
   - Parse markdown content
   - Convert to HTML using markdown library
   - Embed CSS styling
   - Convert breadcrumb links to HTML
   - Apply responsive image CSS
   - Save as .html file
4. System generates HTML index page
5. HTML generation complete

**Alternative Flows:**

**3a. Markdown Parsing Fails:**
- 3a.1. System logs error
- 3a.2. System outputs raw markdown as text
- Return to step 4

**Features:**
- Embedded CSS for professional styling
- Responsive design (desktop, tablet, mobile)
- Images scale to fit screen without horizontal overflow
- Breadcrumb navigation as clickable links
- Consistent styling across all pages

---

### UC-005: Track Documentation Changes
**ID:** UC-005
**Priority:** Medium
**Status:** Implemented
**Related Requirements:** FR-005

**Primary Actor:** Software Developer

**Preconditions:**
- Documentation generation enabled with --track-changes flag
- At least one previous documentation version exists

**Postconditions:**
- Current documentation snapshot saved
- Diff report generated showing changes
- Change summary statistics calculated

**Main Flow:**
1. User invokes generator with --track-changes flag
2. System generates current documentation
3. System creates version snapshot in docs_history/
4. System checks for previous version
5. If previous version exists:
   - Compare current version with previous
   - Identify additions, deletions, modifications
   - Generate diff-annotated documentation in docs_diff/
   - Generate change summary report
6. System displays change statistics
7. Change tracking complete

**Alternative Flows:**

**4a. No Previous Version:**
- 4a.1. System creates initial snapshot
- 4a.2. System displays message: "Initial version created"
- Use case ends

**5a. Diff Generation Fails:**
- 5a.1. System logs error
- 5a.2. System saves snapshot but skips diff
- Return to step 7

---

### UC-006: Analyze Documentation Quality
**ID:** UC-006
**Priority:** Medium
**Status:** Implemented
**Related Requirements:** FR-006

**Primary Actor:** Project Manager, Software Developer

**Preconditions:**
- Model data extracted
- Documentation generated

**Postconditions:**
- Quality report generated
- Undocumented elements identified
- Coverage statistics calculated

**Main Flow:**
1. System analyzes all extracted elements
2. For each element, system checks:
   - Is Note field populated?
   - Is Note field > minimum length?
   - Does element have relationships?
   - Is element included in diagrams?
3. System calculates statistics:
   - Total elements by type
   - Documented vs undocumented count
   - Documentation coverage percentage
4. System identifies quality issues:
   - Elements without documentation
   - Orphaned elements (no package)
   - Elements not in any diagram
5. System generates quality report
6. System saves report to docs/reports/quality-report.md
7. Quality analysis complete

**Alternative Flows:**

**2a. Minimum Documentation Length Not Met:**
- 2a.1. System marks element as "insufficiently documented"
- 2a.2. System includes in quality report
- Return to step 3

---

### UC-007: Extract EA Diagrams
**ID:** UC-007
**Priority:** Medium
**Status:** Implemented (Windows only)
**Related Requirements:** FR-004, FR-004.1, FR-004.2

**Primary Actor:** Software Developer, Technical Writer

**Preconditions:**
- Windows operating system
- Enterprise Architect installed
- pywin32 package installed
- .qea model file accessible

**Postconditions:**
- All diagrams exported as PNG files
- Filenames in GUID-timestamp format
- Diagrams saved to specified output directory

**Main Flow:**
1. User invokes ea_diagram_extractor.py with .qea file
2. System initializes COM connection to EA
3. System opens .qea model in EA (read-only)
4. System retrieves all diagrams from model
5. For each diagram:
   - Get diagram GUID
   - Generate timestamp
   - Export diagram as PNG with name: {GUID}-{timestamp}.png
   - Save to output directory
6. System closes EA model
7. System releases COM connection
8. System displays export summary (count, location)
9. Diagram extraction complete

**Alternative Flows:**

**2a. COM Connection Fails:**
- 2a.1. System displays error: "EA not installed or COM not available"
- 2a.2. Use case ends

**3a. File Open Fails:**
- 3a.1. System displays error with file path
- 3a.2. System releases COM connection
- Use case ends

**5a. Diagram Export Fails:**
- 5a.1. System logs warning for failed diagram
- 5a.2. System continues with next diagram
- Return to step 6

**Usage with Documentation Generator:**
- Extracted diagrams can be used with --ea-diagrams-dir flag
- Generator uses EA diagrams when available (pixel-perfect)
- Falls back to rendering for missing diagrams

---

### UC-008: Configure Documentation Options
**ID:** UC-008
**Priority:** Medium
**Status:** Implemented
**Related Requirements:** FR-007, NFR-005

**Primary Actor:** Software Developer, Technical Writer

**Preconditions:**
- Documentation generator installed

**Postconditions:**
- Configuration applied to documentation generation
- Custom output directories created
- Options validated

**Main Flow:**
1. User creates config.yaml file or uses CLI arguments
2. User specifies configuration options:
   - Output directory
   - HTML output directory
   - EA diagrams directory
   - Include/exclude options
   - Template directory
   - Quality check settings
3. User invokes documentation generator
4. System loads configuration:
   - Read CLI arguments
   - Read YAML config file
   - Apply defaults for unspecified options
5. System validates configuration:
   - Check paths exist
   - Check values are valid
6. System applies configuration hierarchy:
   - CLI arguments override YAML
   - YAML overrides defaults
7. System uses configuration during generation
8. Configuration applied successfully

**Alternative Flows:**

**5a. Invalid Configuration:**
- 5a.1. System displays error with problematic option
- 5a.2. System suggests correct format
- Use case ends

**5b. Path Does Not Exist:**
- 5b.1. System creates directory if possible
- 5b.2. If creation fails, display error
- Return to step 6 or end

**Configuration Options:**
- `output.directory`: Markdown output path
- `diagrams.ea_exports_dir`: EA diagrams path
- `extraction.include_private`: Include private elements
- `documentation.use_cases.detailed_scenarios`: Scenario details
- `quality_checks.check_undocumented`: Enable quality checks

---

### UC-009: Run Regression Tests
**ID:** UC-009
**Priority:** Medium
**Status:** Implemented
**Related Requirements:** NFR-006

**Primary Actor:** Software Developer

**Preconditions:**
- test_model.qea exists
- docs_golden/ baseline exists
- Python environment set up

**Postconditions:**
- Test results displayed
- Documentation consistency verified
- Differences reported (if any)

**Main Flow:**
1. Developer runs test_doc_consistency.py
2. System generates fresh documentation from test_model.qea
3. System calculates SHA256 checksums for all generated files
4. System compares with golden baseline checksums
5. System verifies:
   - All expected files present
   - No unexpected files present
   - All checksums match
6. System displays test results
7. If all tests pass:
   - Display "✅ All tests passed"
   - Exit with code 0
8. Regression test complete

**Alternative Flows:**

**5a. Checksum Mismatch:**
- 5a.1. System identifies mismatched files
- 5a.2. System displays diff for each file
- 5a.3. System displays "❌ Tests failed"
- 5a.4. Exit with code 1
- Use case ends

**5b. Missing Files:**
- 5b.1. System lists missing files
- 5b.2. System displays test failure
- Return to 5a.4

**5c. Extra Files:**
- 5c.1. System lists unexpected files
- 5c.2. System displays test failure
- Return to 5a.4

**Update Baseline:**
- Developer runs with --update flag
- System copies current output to docs_golden/
- New baseline established

---

### UC-010: Generate Quality Reports
**ID:** UC-010
**Priority:** Low
**Status:** Implemented
**Related Requirements:** FR-002.4, FR-006

**Primary Actor:** Project Manager

**Preconditions:**
- Documentation generated
- Quality analysis performed

**Postconditions:**
- Quality report saved
- Dependency report saved
- Reports accessible in docs/reports/

**Main Flow:**
1. System performs quality analysis (→ UC-006)
2. System generates quality-report.md:
   - Documentation statistics
   - Undocumented elements list
   - Coverage metrics
3. System generates dependencies.md:
   - Dependency graph in Mermaid format
   - Component dependencies list
   - Class dependencies list
4. System saves reports to docs/reports/
5. Quality reports generated

---

## Use Case Relationships

### Includes
- UC-001 includes UC-002 (Extract Model Data)
- UC-001 includes UC-003 (Render Diagrams)
- UC-001 includes UC-010 (Generate Quality Reports)
- UC-006 includes UC-010 (Generate Quality Reports)

### Extends
- UC-004 extends UC-001 (when --html flag used)
- UC-005 extends UC-001 (when --track-changes flag used)
- UC-007 extends UC-003 (when EA diagrams available)

### Depends On
- UC-003 depends on UC-002 (needs extracted data)
- UC-004 depends on UC-001 (needs markdown)
- UC-005 depends on UC-001 (needs documentation)
- UC-006 depends on UC-002 (needs extracted data)

---

## Use Case Priority Matrix

| Use Case | Priority | Complexity | Status |
|----------|----------|------------|---------|
| UC-001 | High | Medium | ✅ Implemented |
| UC-002 | High | High | ✅ Implemented |
| UC-003 | High | High | ✅ Implemented |
| UC-004 | Medium | Low | ✅ Implemented |
| UC-005 | Medium | Medium | ✅ Implemented |
| UC-006 | Medium | Low | ✅ Implemented |
| UC-007 | Medium | Medium | ✅ Implemented |
| UC-008 | Medium | Low | ✅ Implemented |
| UC-009 | Medium | Low | ✅ Implemented |
| UC-010 | Low | Low | ✅ Implemented |
