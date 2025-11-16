# EA Model Specifications
## EATools Self-Documentation Project

This directory contains specifications for creating an Enterprise Architect UML model of the EA Documentation Generator itself - enabling the tool to document itself!

---

## Purpose

These specifications guide the creation of a comprehensive EA model that captures:
- **Requirements** - What the system should do
- **Use Cases** - How users interact with the system
- **Components** - The architectural building blocks
- **Classes** - The implementation (reverse engineered from code)

Once the EA model is created, you can use EATools to generate its own documentation - achieving self-documenting software.

---

## Directory Structure

```
ea_model_specs/
├── README.md                    # This file - overview and quick start
├── CODE_IMPORT_GUIDE.md        # Detailed guide for importing Python code into EA
├── requirements/
│   └── requirements.md          # Complete requirements specification
├── use-cases/
│   └── use-cases.md            # Complete use case specification
└── components/
    └── components.md           # Component architecture specification
```

---

## Quick Start

### Option 1: Manual Creation in EA (Recommended for Learning)

1. **Create New EA Project**
   ```
   File → New Project → EATools.qea
   ```

2. **Create Package Structure**
   ```
   EATools
   ├── Requirements
   ├── Use Cases
   ├── Components
   ├── Classes
   └── State Machines
   ```

3. **Import Requirements**
   - Open `requirements/requirements.md`
   - Create requirement elements in EA
   - Follow the hierarchy (FR-001 → FR-001.1, etc.)
   - Set properties: Priority, Status, Description

4. **Import Use Cases**
   - Open `use-cases/use-cases.md`
   - Create actors: Software Developer, Technical Writer, Project Manager
   - Create use case elements (UC-001 through UC-010)
   - Add scenarios from specifications
   - Link use cases to requirements

5. **Import Components**
   - Open `components/components.md`
   - Create component elements
   - Add provided/required interfaces
   - Document dependencies

6. **Reverse Engineer Code**
   - Follow `CODE_IMPORT_GUIDE.md`
   - Import Python code into Classes package
   - Create class diagrams

7. **Generate Self-Documentation**
   ```bash
   python sparx_doc_generator.py EATools.qea --output docs_self --html
   ```

### Option 2: Quick Import (Automated)

1. **Use EA's Import Feature**
   ```
   Right-click package → Import → CSV or XML
   ```

2. **Convert Markdown to EA Import Format**
   - Use a conversion script (see below)
   - Import requirements as CSV
   - Import use cases as CSV

3. **Reverse Engineer Code**
   ```
   Code Engineering → Import Source Directory
   ```

---

## Specifications Summary

### Requirements (28 total)

**Functional Requirements:**
- FR-001: Data Extraction (6 sub-requirements)
- FR-002: Documentation Generation (4 sub-requirements)
- FR-003: Diagram Rendering (4 sub-requirements)
- FR-004: EA Diagram Integration (2 sub-requirements)
- FR-005: Change Tracking
- FR-006: Quality Analysis
- FR-007: Configuration Management
- FR-008: Template System

**Non-Functional Requirements:**
- NFR-001: Performance
- NFR-002: Robustness
- NFR-003: Compatibility
- NFR-004: Maintainability
- NFR-005: Usability
- NFR-006: Testability

### Use Cases (10 total)

| ID | Name | Priority | Actors |
|----|------|----------|--------|
| UC-001 | Generate Documentation | High | Developer, Writer |
| UC-002 | Extract Model Data | High | System |
| UC-003 | Render Diagrams | High | System |
| UC-004 | Generate HTML Output | Medium | System |
| UC-005 | Track Documentation Changes | Medium | Developer |
| UC-006 | Analyze Documentation Quality | Medium | Manager, Developer |
| UC-007 | Extract EA Diagrams | Medium | Developer, Writer |
| UC-008 | Configure Documentation Options | Medium | Developer, Writer |
| UC-009 | Run Regression Tests | Medium | Developer |
| UC-010 | Generate Quality Reports | Low | Manager |

### Components (10 total)

| Component | Type | Package | Purpose |
|-----------|------|---------|---------|
| SparxExtractor | Core | sparx_ea_doc | Extract data from .qea files |
| DocumentationGenerators | Core | sparx_ea_doc.generators | Generate markdown docs |
| DiagramRenderer | Core | sparx_ea_doc | Render UML diagrams |
| HTMLGenerator | Converter | sparx_ea_doc | Convert markdown to HTML |
| QualityReporter | Analyzer | sparx_ea_doc | Analyze quality |
| DiffGenerator | Analyzer | sparx_ea_doc | Track changes |
| TemplateRenderer | Renderer | sparx_ea_doc | Process templates |
| EADiagramExtractor | Integration | root | Extract diagrams via COM |
| Utils | Utility | sparx_ea_doc | Text cleaning, filenames |
| Models | Data | sparx_ea_doc | Data classes |

---

## Traceability Matrix

This shows key linkages between requirements and use cases:

| Requirement | Use Cases | Status |
|-------------|-----------|--------|
| FR-001 | UC-002, UC-007 | ✅ Implemented |
| FR-002 | UC-001, UC-004 | ✅ Implemented |
| FR-003 | UC-003 | ✅ Implemented |
| FR-004 | UC-007 | ✅ Implemented |
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

---

## Creating the EA Model - Step by Step

### Phase 1: Requirements (30 minutes)

1. Create `Requirements` view in EA
2. Add requirement elements from `requirements.md`:
   - Create parent requirements (FR-001, FR-002, etc.)
   - Create child requirements (FR-001.1, FR-001.2, etc.)
   - Set attributes: Priority, Status, Description
3. Organize in hierarchy

**EA Element Properties:**
- Type: Requirement
- Stereotype: functional, non-functional
- Status: Implemented
- Priority: High, Medium, Low
- Notes: Description from specification

### Phase 2: Actors (10 minutes)

1. Create `Use Cases` view
2. Create use case diagram: "System Context"
3. Add actors:
   - Software Developer (primary)
   - Technical Writer (primary)
   - Project Manager (primary)
   - CI/CD System (secondary)
   - Enterprise Architect Application (secondary)

**EA Element Properties:**
- Type: Actor
- Notes: Role description from specification

### Phase 3: Use Cases (45 minutes)

1. Create use case elements (UC-001 through UC-010)
2. For each use case, add:
   - Description
   - Preconditions
   - Postconditions
   - Main flow (as structured note or scenario)
   - Alternative flows
3. Create relationships:
   - Actor associations
   - Include relationships (UC-001 includes UC-002)
   - Extend relationships (UC-004 extends UC-001)

**EA Element Properties:**
- Type: UseCase
- Scenarios: Main flow, alternative flows
- Preconditions: Structured constraints
- Postconditions: Structured constraints

### Phase 4: Link Requirements to Use Cases (20 minutes)

1. Open use case diagram
2. For each use case, add `Realize` relationships to requirements
3. Use relationship matrix for bulk linking
4. Document traceability

**Example Links:**
```
UC-001 (Generate Documentation) → realizes → FR-002 (Documentation Generation)
UC-002 (Extract Model Data) → realizes → FR-001 (Data Extraction)
UC-003 (Render Diagrams) → realizes → FR-003 (Diagram Rendering)
```

### Phase 5: Components (40 minutes)

1. Create `Components` view
2. Create component diagram: "System Architecture"
3. Add component elements from `components.md`
4. For each component, add:
   - Provided interfaces (lollipop notation)
   - Required interfaces (socket notation)
   - Dependencies
5. Create dependency relationships

**EA Element Properties:**
- Type: Component
- Interfaces: IModelExtractor, IDocumentationGenerator, etc.
- Dependencies: Component A uses Component B

### Phase 6: Reverse Engineer Code (60 minutes)

1. Follow `CODE_IMPORT_GUIDE.md`
2. Import Python code using:
   ```
   Code Engineering → Import Source Directory
   ```
3. Review imported classes
4. Clean up and organize
5. Create class diagrams:
   - Core classes (models.py)
   - Generators (generators/)
   - Utilities (utils.py)

### Phase 7: State Machines (Optional, 30 minutes)

1. Create state machine for "Documentation Generation Process"
2. Add states:
   - Initial
   - Connected
   - Extracting
   - Rendering
   - Generating
   - Complete
   - Error
3. Add transitions with triggers and guards

---

## Validating the Model

After creating the EA model, validate completeness:

### Requirements Checklist
- ✅ All 28 requirements created
- ✅ Hierarchy correct (parent-child)
- ✅ All attributes set (Priority, Status)
- ✅ Descriptions complete

### Use Cases Checklist
- ✅ All 10 use cases created
- ✅ All 5 actors created
- ✅ Scenarios documented
- ✅ Preconditions/postconditions set
- ✅ Relationships correct (includes, extends)

### Traceability Checklist
- ✅ Requirements linked to use cases
- ✅ Use cases linked to components
- ✅ Components linked to classes

### Components Checklist
- ✅ All 10 components created
- ✅ Interfaces defined
- ✅ Dependencies documented

### Classes Checklist
- ✅ All Python files imported
- ✅ Classes organized by package
- ✅ Relationships preserved
- ✅ Docstrings imported as notes

---

## Generating Self-Documentation

Once your EA model is complete:

```bash
# Basic markdown documentation
python sparx_doc_generator.py EATools.qea --output docs_self

# With HTML output
python sparx_doc_generator.py EATools.qea --output docs_self --html

# With EA-exported diagrams (Windows)
python ea_diagram_extractor.py EATools.qea -o ea_diagrams_self
python sparx_doc_generator.py EATools.qea \
  --output docs_self \
  --html \
  --ea-diagrams-dir ea_diagrams_self
```

**Result:** Complete documentation of EATools, generated by EATools itself!

The generated documentation will include:
- Requirements documentation with hierarchy
- Use case documentation with scenarios
- Component architecture
- Class documentation with attributes and operations
- Traceability links between all elements
- Quality reports
- UML diagrams

---

## Tips for Success

### 1. Start Small
Create a minimal viable model first:
- 3-4 key requirements
- 2-3 primary use cases
- Main components
- Test documentation generation
- Iterate and expand

### 2. Use Templates
EA supports templates for common patterns:
- Requirement templates
- Use case templates
- Component templates

### 3. Leverage Tagged Values
Add metadata to elements:
- Requirements: Effort, Complexity
- Use Cases: Frequency, Priority
- Classes: Test Coverage, File Path

### 4. Document as You Go
Don't wait until the end:
- Add notes to each element immediately
- Document relationships
- Keep specifications up to date

### 5. Review and Iterate
- Generate documentation frequently
- Review output
- Refine model based on output
- Update code documentation

---

## Converting Specifications to EA Import Format

If you want to bulk-import requirements and use cases, you can convert the markdown specifications to CSV format that EA can import.

### Requirements CSV Format

```csv
"Type","Name","Notes","Priority","Status","Parent"
"requirement","FR-001","Data Extraction from EA Models","High","Implemented",""
"requirement","FR-001.1","SQLite Database Connection","High","Implemented","FR-001"
"requirement","FR-001.2","Use Case Extraction","High","Implemented","FR-001"
```

### Use Cases CSV Format

```csv
"Type","Name","Notes","Stereotype"
"usecase","Generate Documentation","Generate comprehensive documentation...","primary"
"actor","Software Developer","Creates and maintains UML models",""
```

---

## Integration with CI/CD

Once the EA model exists, integrate documentation generation into your CI/CD pipeline:

```yaml
# .github/workflows/documentation.yml
name: Generate Documentation

on:
  push:
    branches: [ main, develop ]

jobs:
  generate-docs:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Setup Python
        uses: actions/setup-python@v2
        with:
          python-version: '3.9'
      - name: Install dependencies
        run: pip install -r requirements.txt
      - name: Generate Documentation
        run: |
          python sparx_doc_generator.py EATools.qea \
            --output docs \
            --html \
            --html-output docs_html
      - name: Deploy to GitHub Pages
        uses: peaceiris/actions-gh-pages@v3
        with:
          github_token: ${{ secrets.GITHUB_TOKEN }}
          publish_dir: ./docs_html
```

---

## Next Steps

1. **Review Specifications**
   - Read `requirements/requirements.md`
   - Read `use-cases/use-cases.md`
   - Read `components/components.md`

2. **Follow Import Guide**
   - Read `CODE_IMPORT_GUIDE.md`
   - Execute step-by-step

3. **Create EA Model**
   - Follow phase-by-phase plan above
   - Validate at each step

4. **Generate Documentation**
   - Run documentation generator
   - Review output
   - Iterate on model

5. **Maintain Model**
   - Keep model in sync with code
   - Update after significant changes
   - Re-generate documentation regularly

---

## Resources

- **EA User Guide**: https://sparxsystems.com/resources/user-guides/
- **Python Code Engineering**: EA Help → Code Engineering → Python
- **MDG Technologies**: https://sparxsystems.com/products/mdg/
- **UML Best Practices**: EA Help → Getting Started → Best Practices

---

**Goal:** Self-documenting software - EATools documenting itself with pixel-perfect accuracy!

**Status:** Specifications complete ✅ Ready for EA model creation ✅

**Last Updated:** 2025-11-16
