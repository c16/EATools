# Code Import Guide for Enterprise Architect
## Importing Python Code into EA UML Model

This guide explains how to import the EATools Python codebase into Enterprise Architect to create a comprehensive UML model that can then be documented using the tool itself (self-documenting).

---

## Overview

Enterprise Architect supports importing Python code through its code engineering features. This creates a UML model from existing source code, including:
- Classes and their attributes
- Methods and parameters
- Inheritance relationships
- Dependencies
- Package structure

---

## Prerequisites

1. **Enterprise Architect** installed (version 12 or higher recommended)
2. **Python Code Engineering** enabled in EA
3. **EATools source code** available locally

---

## Method 1: Using EA's Code Import Wizard (Recommended)

### Step 1: Create New Project

1. Open Enterprise Architect
2. Create new project: `File` → `New Project`
3. Choose location: `EATools.qea`
4. Select template: `Blank Model`

### Step 2: Create Package Structure

1. In Project Browser, create root package: `EATools`
2. Create sub-packages matching code structure:
   ```
   EATools
   ├── Main Scripts
   ├── sparx_ea_doc
   │   ├── generators
   │   └── core
   └── Tests
   ```

### Step 3: Import Python Code

1. Right-click on `sparx_ea_doc` package
2. Select `Code Engineering` → `Import Source Directory...`
3. Configure import settings:

   **Source Directory:** `/home/user/EATools/sparx_ea_doc`

   **Language:** Python

   **Options:**
   - ☑ Parse method bodies
   - ☑ Generate sequence diagrams
   - ☑ Import namespace/package structure
   - ☑ Include private members
   - ☑ Parse docstrings as notes

4. Click `Import`

### Step 4: Import Main Scripts

Repeat for main scripts:
1. Right-click `Main Scripts` package
2. Import individual files:
   - `sparx_doc_generator.py`
   - `sparx_doc_gui.py`
   - `ea_diagram_extractor.py`
   - `doc_diff_manager.py`

### Step 5: Import Test Files

1. Right-click `Tests` package
2. Import test files:
   - `test_doc_consistency.py`
   - `test_text_cleaning.py`

---

## Method 2: Manual Code Template Configuration

If automatic import doesn't work perfectly, you can configure code templates manually.

### Step 1: Configure Python Code Template

1. Go to `Settings` → `Code Engineering` → `Options`
2. Select `Python` language
3. Configure templates for:
   - Class
   - Attribute
   - Operation
   - Parameter

### Python Class Template

```python
{{notes}}
class {{className}}{{#if hasBaseClass}}({{baseClass}}){{/if}}:
    """{{description}}"""

    {{#for attribute in attributes}}
    {{attribute.name}}: {{attribute.type}}{{#if attribute.hasDefault}} = {{attribute.default}}{{/if}}
    {{/for}}

    {{#for operation in operations}}
    def {{operation.name}}({{operation.parameters}}) -> {{operation.returnType}}:
        """{{operation.description}}"""
        {{operation.code}}
    {{/for}}
```

### Step 2: Create Code Generation Profiles

1. `Settings` → `Code Engineering` → `Code Generation`
2. Create profile: `Python 3`
3. Configure options:
   - File extension: `.py`
   - Indentation: 4 spaces
   - Line endings: LF (Unix)
   - Encoding: UTF-8

---

## Method 3: Reverse Engineering via MDG Technology

For most accurate results, use EA's MDG Technology for Python.

### Step 1: Install Python MDG

1. `Configure` → `MDG Technologies`
2. Enable `Python` MDG
3. Restart Enterprise Architect

### Step 2: Create Reverse Engineering Profile

1. `Code Engineering` → `Options` → `Reverse Engineering`
2. Create new profile: `EATools Python`
3. Configure:
   - Language: Python
   - Parse docstrings: Yes
   - Generate diagrams: Yes
   - Include decorators: Yes
   - Include type hints: Yes

### Step 3: Execute Reverse Engineering

1. Right-click package where code should be imported
2. `Code Engineering` → `Reverse Engineer...`
3. Select profile: `EATools Python`
4. Choose directory: `/home/user/EATools`
5. Configure filters:
   - Include: `*.py`
   - Exclude: `__pycache__`, `*.pyc`, `.git`
6. Click `Reverse Engineer`

---

## Post-Import Tasks

After importing code, enhance the model with additional UML elements:

### 1. Create Component Diagram

1. Create new diagram: `Component Diagram`
2. Add components from imported classes:
   - SparxExtractor
   - DocumentationGenerators
   - DiagramRenderer
   - HTMLGenerator
   - QualityReporter
   - DiffGenerator
   - TemplateRenderer
3. Add interfaces:
   - IModelExtractor
   - IDocumentationGenerator
   - IDiagramRenderer
   - IHTMLConverter
   - IQualityAnalyzer
4. Connect components with dependencies

### 2. Create Use Case Diagram

1. Create new diagram: `Use Case Diagram`
2. Add actors:
   - Software Developer
   - Technical Writer
   - Project Manager
   - CI/CD System
3. Add use cases from specifications:
   - Generate Documentation
   - Extract Model Data
   - Render Diagrams
   - etc. (see use-cases.md)
4. Add relationships:
   - Associations (actor to use case)
   - Include relationships
   - Extend relationships

### 3. Create Requirements

1. Create `Requirements` view
2. Add requirements from specifications (see requirements.md)
3. Create requirement hierarchy:
   - FR-001 (parent)
     - FR-001.1 (child)
     - FR-001.2 (child)
     - etc.
4. Link requirements to use cases:
   - Drag requirement onto use case diagram
   - Create `Realize` relationship

### 4. Create Class Diagrams

1. Create class diagram for each package:
   - `Core Classes` (models.py)
   - `Generators` (generators/)
   - `Utilities` (utils.py)
2. Show relationships:
   - Inheritance (Element → UseCase, Actor, etc.)
   - Dependencies (Generators → Utils)
   - Associations (Generator → Extractor)

### 5. Add Documentation

For each element:
1. Double-click element
2. Go to `Notes` tab
3. Add description from docstrings
4. Add stereotypes where appropriate:
   - `<<utility>>` for Utils
   - `<<service>>` for Extractor
   - `<<generator>>` for documentation generators

### 6. Create State Machine Diagrams

Create state machine for documentation generation process:

**States:**
- Initial
- Connected
- Extracting
- Rendering
- Generating
- Complete
- Error

**Transitions:**
- Connected → Extracting [file valid] / extract data
- Extracting → Rendering [data extracted] / render diagrams
- Rendering → Generating [diagrams ready] / generate docs
- Generating → Complete [success] / save files
- Any → Error [error occurs] / log error

---

## Linking Requirements to Use Cases

After creating both requirements and use cases in EA:

### Method 1: Drag and Drop

1. Open use case diagram
2. From Project Browser, drag requirement onto diagram
3. Select `Realize` relationship type
4. Draw from use case to requirement

### Method 2: Relationship Matrix

1. `View` → `Relationship Matrix`
2. Rows: Use Cases
3. Columns: Requirements
4. Click cell to create relationship
5. Select relationship type: `Realize` or `Trace`

### Method 3: Properties Panel

1. Select use case element
2. Go to `Relationships` tab
3. Click `New`
4. Select relationship type: `Realize`
5. Select target requirement
6. Add notes explaining how UC realizes requirement

### Create Traceability

Example linkages:
```
FR-001 (Data Extraction) ←→ UC-002 (Extract Model Data)
FR-002 (Documentation Generation) ←→ UC-001 (Generate Documentation)
FR-002.2 (HTML Documentation) ←→ UC-004 (Generate HTML Output)
FR-003 (Diagram Rendering) ←→ UC-003 (Render Diagrams)
FR-004 (EA Diagram Integration) ←→ UC-007 (Extract EA Diagrams)
FR-005 (Change Tracking) ←→ UC-005 (Track Documentation Changes)
FR-006 (Quality Analysis) ←→ UC-006 (Analyze Documentation Quality)
```

---

## Tagged Values

Add custom properties to elements using tagged values:

### For Requirements:
- `Priority`: High, Medium, Low
- `Status`: Proposed, Approved, Implemented, Verified
- `Version`: 1.0, 1.1, etc.
- `Effort`: Story points or hours

### For Use Cases:
- `Complexity`: Low, Medium, High
- `Frequency`: Daily, Weekly, On-demand
- `Implementation Status`: Complete, In Progress, Planned

### For Classes:
- `Test Coverage`: Percentage
- `Code File`: Path to .py file
- `Line Count`: Number of lines

To add tagged values:
1. Right-click element
2. `Features and Properties` → `Tagged Values`
3. Click `New`
4. Enter tag name and value

---

## Generating Documentation from the Model

Once you've created the EA model of EATools itself, you can generate documentation using the tool:

```bash
# Generate markdown documentation of EATools model
python sparx_doc_generator.py EATools.qea --output docs_self

# Generate HTML as well
python sparx_doc_generator.py EATools.qea --output docs_self --html

# Extract diagrams from EA first (Windows)
python ea_diagram_extractor.py EATools.qea -o ea_diagrams_self
python sparx_doc_generator.py EATools.qea --output docs_self --ea-diagrams-dir ea_diagrams_self
```

This creates self-documenting documentation - the tool documenting itself!

---

## Tips for Best Results

### 1. Consistent Naming
- Use PascalCase for classes: `SparxExtractor`
- Use snake_case for methods: `extract_use_cases()`
- Use clear, descriptive names

### 2. Comprehensive Docstrings
EA can import docstrings as notes:
```python
def extract_use_cases(self) -> List[UseCase]:
    """
    Extract all use case elements from the database.

    Queries the t_object table for elements with Object_Type='UseCase'
    and creates UseCase objects with all related data.

    Returns:
        List of UseCase objects with actors and relationships
    """
```

### 3. Type Hints
EA recognizes type hints:
```python
def generate_filename_with_id(
    name: str,
    object_id: int,
    prefix: str = '',
    extension: str = 'md'
) -> str:
    """Generate filename with object ID"""
```

### 4. Package Organization
Mirror your code structure in EA:
```
sparx_ea_doc/
├── __init__.py        → Package: sparx_ea_doc
├── extractor.py       → Class: SparxExtractor
├── models.py          → Classes: Element, UseCase, etc.
├── utils.py           → Functions in utility package
└── generators/        → Package: generators
    ├── use_case_generator.py → Class: UseCaseGenerator
    └── ...
```

### 5. Relationship Documentation
After import, manually add:
- Component dependencies
- Interface realizations
- Package dependencies
- Aggregation/composition where appropriate

---

## Common Issues and Solutions

### Issue: Import Creates Flat Structure
**Solution:**
- Manually create package hierarchy first
- Import into each package separately

### Issue: Docstrings Not Imported
**Solution:**
- Check "Parse method bodies" option
- Verify docstrings use """ not '''

### Issue: Type Hints Not Recognized
**Solution:**
- Ensure using Python 3.5+ type hints
- Check EA version supports type hints
- Update MDG Technology

### Issue: Relationships Not Created
**Solution:**
- Manually add dependencies after import
- Use dependency matrix to bulk-create relationships

### Issue: Large Files Cause Import Failure
**Solution:**
- Import files one at a time
- Split large files before import
- Increase EA memory allocation

---

## Next Steps

After successful import:

1. ✅ **Validate Model**
   - Check all classes imported
   - Verify relationships
   - Review notes from docstrings

2. ✅ **Add Use Cases**
   - Create from specifications
   - Link to requirements
   - Add scenarios

3. ✅ **Add Requirements**
   - Import from requirements.md
   - Create hierarchy
   - Link to use cases

4. ✅ **Create Diagrams**
   - Component diagram (architecture)
   - Class diagrams (by package)
   - Use case diagrams
   - State machine diagrams

5. ✅ **Generate Documentation**
   - Run documentation generator
   - Review output
   - Iterate on model

6. ✅ **Maintain Sync**
   - Re-import code after changes
   - Update requirements and use cases
   - Keep model current

---

## Resources

- **EA User Guide:** Help → User Guide → Code Engineering
- **Python MDG:** Sparx website → MDG Technologies
- **Code Templates:** Settings → Code Engineering → Code Templates
- **Reverse Engineering:** Help → User Guide → Reverse Engineering

---

**Result:** Self-documenting application - EATools documented by EATools!
