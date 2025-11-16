# Requirements-Use Case Traceability Matrix
## EA Documentation Generator

This matrix shows the relationships between requirements and use cases, demonstrating complete coverage.

---

## Primary Traceability

| Requirement ID | Requirement Name | Realizes Use Cases | Coverage |
|---------------|------------------|-------------------|----------|
| **FR-001** | Data Extraction from EA Models | UC-002, UC-007 | ✅ Full |
| FR-001.1 | SQLite Database Connection | UC-002 | ✅ Full |
| FR-001.2 | Use Case Extraction | UC-002 | ✅ Full |
| FR-001.3 | State Machine Extraction | UC-002 | ✅ Full |
| FR-001.4 | Component Extraction | UC-002 | ✅ Full |
| FR-001.5 | Class Extraction | UC-002 | ✅ Full |
| FR-001.6 | Diagram Metadata Extraction | UC-002 | ✅ Full |
| **FR-002** | Documentation Generation | UC-001, UC-004, UC-010 | ✅ Full |
| FR-002.1 | Markdown Documentation | UC-001 | ✅ Full |
| FR-002.2 | HTML Documentation | UC-004 | ✅ Full |
| FR-002.3 | Breadcrumb Navigation | UC-001, UC-004 | ✅ Full |
| FR-002.4 | Quality Reports | UC-010 | ✅ Full |
| **FR-003** | Diagram Rendering | UC-003 | ✅ Full |
| FR-003.1 | Use Case Diagram Rendering | UC-003 | ✅ Full |
| FR-003.2 | Class Diagram Rendering | UC-003 | ✅ Full |
| FR-003.3 | Component Diagram Rendering | UC-003 | ✅ Full |
| FR-003.4 | State Machine Diagram Rendering | UC-003 | ✅ Full |
| **FR-004** | EA Diagram Integration | UC-007 | ✅ Full |
| FR-004.1 | COM Automation for Diagram Extraction | UC-007 | ✅ Full |
| FR-004.2 | EA-Exported Diagram Usage | UC-007 | ✅ Full |
| **FR-005** | Change Tracking | UC-005 | ✅ Full |
| **FR-006** | Quality Analysis | UC-006, UC-010 | ✅ Full |
| **FR-007** | Configuration Management | UC-008 | ✅ Full |
| **FR-008** | Template System | UC-001 | ✅ Full |
| **NFR-001** | Performance | UC-001, UC-002 | ✅ Full |
| **NFR-002** | Robustness | UC-001, UC-002 | ✅ Full |
| **NFR-003** | Compatibility | All Use Cases | ✅ Full |
| **NFR-004** | Maintainability | All Use Cases | ✅ Full |
| **NFR-005** | Usability | UC-001, UC-008 | ✅ Full |
| **NFR-006** | Testability | UC-009 | ✅ Full |

---

## Reverse Traceability (Use Cases to Requirements)

| Use Case ID | Use Case Name | Satisfies Requirements | Components Involved |
|------------|---------------|----------------------|---------------------|
| **UC-001** | Generate Documentation | FR-002, FR-002.1, FR-002.3, FR-008, NFR-001, NFR-005 | SparxExtractor, DocumentationGenerators, TemplateRenderer, QualityReporter |
| **UC-002** | Extract Model Data | FR-001, FR-001.1-FR-001.6, NFR-001, NFR-002 | SparxExtractor, Utils, Models |
| **UC-003** | Render Diagrams | FR-003, FR-003.1-FR-003.4 | DiagramRenderer, Models |
| **UC-004** | Generate HTML Output | FR-002.2, FR-002.3 | HTMLGenerator, Utils |
| **UC-005** | Track Documentation Changes | FR-005 | DiffGenerator |
| **UC-006** | Analyze Documentation Quality | FR-006, NFR-004 | QualityReporter, Models |
| **UC-007** | Extract EA Diagrams | FR-004, FR-004.1, FR-004.2 | EADiagramExtractor |
| **UC-008** | Configure Documentation Options | FR-007, NFR-005 | ConfigManager, Utils |
| **UC-009** | Run Regression Tests | NFR-006 | TestFramework |
| **UC-010** | Generate Quality Reports | FR-002.4, FR-006 | QualityReporter, Utils |

---

## Component Coverage

Shows which components implement which requirements:

| Component | Implements Requirements | Used by Use Cases |
|-----------|------------------------|-------------------|
| **SparxExtractor** | FR-001.1-FR-001.6, NFR-001, NFR-002 | UC-001, UC-002 |
| **DocumentationGenerators** | FR-002.1, FR-002.3 | UC-001 |
| **DiagramRenderer** | FR-003.1-FR-003.4 | UC-001, UC-003 |
| **HTMLGenerator** | FR-002.2 | UC-001, UC-004 |
| **QualityReporter** | FR-002.4, FR-006 | UC-001, UC-006, UC-010 |
| **DiffGenerator** | FR-005 | UC-005 |
| **TemplateRenderer** | FR-008 | UC-001 |
| **EADiagramExtractor** | FR-004.1, FR-004.2 | UC-007 |
| **Utils** | NFR-002 (text cleaning, sanitization) | All |
| **Models** | All (data structures) | All |

---

## Actor-Use Case Matrix

Shows which actors interact with which use cases:

| Actor | Primary Use Cases | Secondary Use Cases |
|-------|------------------|---------------------|
| **Software Developer** | UC-001, UC-005, UC-007, UC-008, UC-009 | UC-006 |
| **Technical Writer** | UC-001, UC-007, UC-008 | - |
| **Project Manager** | UC-006 | UC-010 |
| **CI/CD System** | UC-001, UC-009 | - |
| **EA Application** | - | UC-002, UC-007 (provides data) |

---

## Coverage Analysis

### Requirements Coverage
- **Total Requirements:** 28 (8 functional + 20 sub-requirements, 6 non-functional)
- **Requirements with Use Cases:** 28 (100%)
- **Requirements without Use Cases:** 0
- **Orphaned Requirements:** 0

### Use Case Coverage
- **Total Use Cases:** 10
- **Use Cases with Requirements:** 10 (100%)
- **Use Cases without Requirements:** 0
- **Orphaned Use Cases:** 0

### Component Coverage
- **Total Components:** 10
- **Components with Requirements:** 10 (100%)
- **Components without Requirements:** 0
- **Orphaned Components:** 0

---

## Test Coverage

Shows how use cases are validated:

| Use Case | Test Method | Test Location |
|----------|-------------|---------------|
| UC-001 | Regression tests | test_doc_consistency.py |
| UC-002 | Regression tests | test_doc_consistency.py |
| UC-003 | Regression tests (diagrams) | test_doc_consistency.py |
| UC-004 | Regression tests (HTML) | test_doc_consistency.py |
| UC-005 | Manual testing | N/A |
| UC-006 | Regression tests (reports) | test_doc_consistency.py |
| UC-007 | Manual testing (Windows) | N/A |
| UC-008 | Integration tests | Manual |
| UC-009 | Self-testing | test_doc_consistency.py |
| UC-010 | Regression tests (reports) | test_doc_consistency.py |

**Test Coverage:** 70% automated, 30% manual

---

## Dependency Graph

Visual representation of relationships:

```
Requirements Layer
─────────────────────────────────────────────────
FR-001 ──┬─→ FR-001.1
         ├─→ FR-001.2
         ├─→ FR-001.3
         ├─→ FR-001.4
         ├─→ FR-001.5
         └─→ FR-001.6

FR-002 ──┬─→ FR-002.1
         ├─→ FR-002.2
         ├─→ FR-002.3
         └─→ FR-002.4

FR-003 ──┬─→ FR-003.1
         ├─→ FR-003.2
         ├─→ FR-003.3
         └─→ FR-003.4

FR-004 ──┬─→ FR-004.1
         └─→ FR-004.2

FR-005, FR-006, FR-007, FR-008
NFR-001 through NFR-006


Use Case Layer
─────────────────────────────────────────────────
UC-001 ──includes──→ UC-002
UC-001 ──includes──→ UC-003
UC-001 ──includes──→ UC-010

UC-004 ──extends──→ UC-001
UC-005 ──extends──→ UC-001

UC-007 ──extends──→ UC-003
UC-006 ──includes──→ UC-010


Component Layer
─────────────────────────────────────────────────
SparxExtractor ──uses──→ Utils
SparxExtractor ──creates──→ Models

DocumentationGenerators ──uses──→ SparxExtractor
DocumentationGenerators ──uses──→ Utils
DocumentationGenerators ──uses──→ TemplateRenderer

DiagramRenderer ──uses──→ Models

HTMLGenerator ──uses──→ Utils

QualityReporter ──uses──→ Models

EADiagramExtractor ──external──→ EA COM API
```

---

## Verification Checklist

Use this checklist when creating the EA model:

### Requirements
- [ ] All 28 requirements created in EA
- [ ] Hierarchy correct (parent-child relationships)
- [ ] All attributes set (Priority, Status, Description)
- [ ] All descriptions complete with acceptance criteria

### Use Cases
- [ ] All 10 use cases created in EA
- [ ] All 5 actors created in EA
- [ ] Scenarios documented (main flow, alternative flows)
- [ ] Preconditions and postconditions set
- [ ] All relationships correct (includes, extends, associations)

### Traceability
- [ ] All requirements linked to use cases (Realize relationships)
- [ ] All use cases linked to actors (Association relationships)
- [ ] All use cases linked to components (Dependency relationships)
- [ ] Relationship matrix validates all links

### Components
- [ ] All 10 components created in EA
- [ ] All interfaces defined (provided and required)
- [ ] All dependencies documented
- [ ] Component diagram shows architecture

### Classes
- [ ] Python code imported via reverse engineering
- [ ] Classes organized by package
- [ ] Attributes and operations complete
- [ ] Relationships preserved (inheritance, associations)

### Diagrams
- [ ] Use case diagram created
- [ ] Component diagram created
- [ ] Class diagrams created (one per package)
- [ ] State machine diagram created (optional)

### Documentation
- [ ] Notes added to all elements
- [ ] Stereotypes applied where appropriate
- [ ] Tagged values set for metadata
- [ ] Model ready for documentation generation

---

## EA Relationship Types to Use

When creating links in Enterprise Architect:

### Requirements → Use Cases
**Relationship Type:** `Realize`
- UC-001 realizes FR-002
- UC-002 realizes FR-001
- etc.

### Use Cases → Use Cases
**Relationship Type:** `Include` or `Extend`
- UC-001 includes UC-002
- UC-004 extends UC-001
- etc.

### Actors → Use Cases
**Relationship Type:** `Association`
- Software Developer → UC-001
- Technical Writer → UC-001
- etc.

### Use Cases → Components
**Relationship Type:** `Dependency`
- UC-001 depends on SparxExtractor
- UC-001 depends on DocumentationGenerators
- etc.

### Components → Components
**Relationship Type:** `Dependency` or `Usage`
- DocumentationGenerators uses SparxExtractor
- SparxExtractor uses Utils
- etc.

### Components → Interfaces
**Relationship Type:** `Realization` (provided) or `Usage` (required)
- SparxExtractor realizes IModelExtractor
- DocumentationGenerators uses IModelExtractor
- etc.

---

## Import Order

For best results, create elements in this order:

1. **Requirements** (bottom-up: children first, then parents)
2. **Actors**
3. **Use Cases**
4. **Requirement-Use Case Links** (Realize relationships)
5. **Actor-Use Case Links** (Associations)
6. **Use Case-Use Case Links** (Include/Extend)
7. **Components and Interfaces**
8. **Component Dependencies**
9. **Classes** (via code import)
10. **Class Relationships**
11. **Diagrams** (organize elements visually)

---

## Summary Statistics

**Requirements:** 28 total (100% coverage)
**Use Cases:** 10 total (100% coverage)
**Actors:** 5 total
**Components:** 10 total (100% coverage)
**Classes:** ~15 main classes (to be imported)
**Relationships:** ~80+ relationships

**Traceability:** Complete ✅
**Coverage:** 100% ✅
**Status:** All implemented ✅

**Ready for EA Model Creation** ✅

---

**Last Updated:** 2025-11-16
