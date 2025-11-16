# Sparx Enterprise Architect Documentation Generator

> **Note:** This is the original project specification. For current documentation, features, and usage instructions, see [README.md](README.md) and [QUICKSTART.md](QUICKSTART.md).
>
> **Project Status:** ✅ Complete and actively maintained. All core requirements implemented plus significant enhancements:
> - HTML generation with responsive images
> - Pixel-perfect diagram rendering
> - EA diagram integration and automated extraction (Windows)
> - Object ID-based filenames preventing name clashes
> - Multi-codepage text handling (UTF-8, Windows-1252, ISO-8859-1, CP1252)
> - Comprehensive test suite (29 text cleaning tests + regression tests)
> - Quality reporting and change tracking
> - Template system for customization

## Project Overview
Develop a Python utility that extracts and documents UML models from Sparx Enterprise Architect .qea files (SQLite database format) and generates comprehensive markdown documentation.

## Core Requirements

### 1. Database Analysis
- Connect to the .qea SQLite database file
- Analyze the database schema to understand table structures
- Identify key tables containing model elements:
  - `t_object` - Contains model elements (classes, components, use cases, etc.)
  - `t_attribute` - Contains attributes for classes and components
  - `t_operation` - Contains methods/operations for classes
  - `t_connector` - Contains relationships between elements
  - `t_package` - Contains package/namespace information
  - `t_diagram` - Contains diagram information
  - `t_diagramobjects` - Links objects to diagrams

### 2. Documentation Targets

#### Use Cases Documentation
Extract and document:
- Use case elements (Object_Type = 'UseCase')
- Actors (Object_Type = 'Actor')
- Use case relationships (associations, includes, extends)
- Boundaries and systems
- Pre/post conditions from Notes field
- Business rules and constraints
- Scenarios and flows (if available in tagged values)

Output format:
```markdown
# Use Cases

## UC-001: [Use Case Name]
**Description:** [Extracted from Note field]
**Primary Actor:** [Actor name]
**Preconditions:** [If available]
**Postconditions:** [If available]
**Main Flow:**
1. [Step details]
2. [Step details]

**Alternative Flows:**
- [Alternative scenarios]

**Related Use Cases:**
- <<include>> [Use case name]
- <<extend>> [Use case name]
```

#### State Machine Documentation
Extract and document:
- States (Object_Type in ['State', 'StateNode', 'InitialState', 'FinalState'])
- Transitions (Connector_Type = 'StateFlow')
- Guards and triggers
- Entry/exit actions
- Composite and orthogonal states

Output format:
```markdown
# State Machines

## [State Machine Name]

### States
| State | Type | Description | Entry Actions | Exit Actions |
|-------|------|-------------|---------------|--------------|
| [Name] | [Type] | [Description] | [Actions] | [Actions] |

### Transitions
| From | To | Trigger | Guard | Action |
|------|----|---------|-------|--------|
| [State] | [State] | [Event] | [Condition] | [Action] |

### State Hierarchy
- Parent State
  - Child State 1
  - Child State 2
```

#### Component Documentation
Extract and document:
- Components (Object_Type = 'Component')
- Provided and required interfaces
- Ports and connectors
- Component dependencies
- Deployment information

Output format:
```markdown
# Components

## [Component Name]
**Type:** [Component type/stereotype]
**Description:** [From Note field]

### Interfaces
#### Provided Interfaces
- [Interface name]: [Description]

#### Required Interfaces
- [Interface name]: [Description]

### Ports
| Port | Type | Protocol | Description |
|------|------|----------|-------------|
| [Name] | [Type] | [Protocol] | [Description] |

### Dependencies
- Depends on: [Component list]
- Used by: [Component list]
```

#### Class/Module Documentation
Extract and document:
- Classes (Object_Type = 'Class')
- Interfaces (Object_Type = 'Interface')
- Enumerations (Object_Type = 'Enumeration')
- Attributes with types, visibility, and constraints
- Operations with parameters and return types
- Inheritance relationships
- Associations, aggregations, compositions
- Design patterns used (from stereotypes)

Output format:
```markdown
# Classes and Modules

## [Package/Namespace]

### Class: [Class Name]
**Stereotype:** <<[stereotype]>>
**Description:** [From Note field]
**Visibility:** [public/private/protected]
**Abstract:** [yes/no]

#### Attributes
| Name | Type | Visibility | Default | Static | Description |
|------|------|------------|---------|--------|-------------|
| [attr] | [type] | [vis] | [default] | [Y/N] | [desc] |

#### Methods
| Name | Parameters | Return Type | Visibility | Abstract | Description |
|------|------------|-------------|------------|----------|-------------|
| [method] | [params] | [type] | [vis] | [Y/N] | [desc] |

#### Relationships
- **Inherits from:** [Parent class]
- **Implements:** [Interface list]
- **Associations:**
  - [Related class] ([cardinality]) - [role/description]
- **Dependencies:**
  - [Class] - [description]
```

### 3. Implementation Guidelines

#### Core Script Structure
```python
# sparx_doc_generator.py

import sqlite3
import json
from pathlib import Path
from datetime import datetime
import argparse
import re
import html

class SparxDocGenerator:
    def __init__(self, qea_path: str, output_dir: str = "docs"):
        # Initialize with database path and output directory
        
    def analyze_schema(self) -> dict:
        # Explore and document database schema
        # Save schema analysis to schema.json
        
    def extract_model_data(self):
        # Main extraction orchestrator
        # Calls specific extraction methods
        
    def generate_documentation(self):
        # Generate markdown files
        # Create index.md with navigation
        
    def run(self):
        # Main execution flow
        # Handle errors gracefully
```

#### SQL Queries Reference

```sql
-- Get all use cases with their packages
SELECT o.Object_ID, o.Name, o.Note, o.Stereotype, p.Name as Package
FROM t_object o
LEFT JOIN t_package p ON o.Package_ID = p.Package_ID
WHERE o.Object_Type = 'UseCase'

-- Get state machine elements
SELECT * FROM t_object 
WHERE Object_Type IN ('State', 'StateNode', 'StateMachine')
ORDER BY ParentID, Name

-- Get class attributes
SELECT Name, Type, Scope, Default, Notes, IsStatic, IsConst
FROM t_attribute 
WHERE Object_ID = ?
ORDER BY Pos

-- Get relationships
SELECT c.*, 
       o1.Name as SourceName, o1.Object_Type as SourceType,
       o2.Name as TargetName, o2.Object_Type as TargetType
FROM t_connector c
JOIN t_object o1 ON c.Start_Object_ID = o1.Object_ID
JOIN t_object o2 ON c.End_Object_ID = o2.Object_ID
WHERE c.Start_Object_ID = ? OR c.End_Object_ID = ?
```

### 4. Advanced Features

#### Tagged Values Extraction
- Extract custom properties from t_objectproperties
- Include requirements, constraints, business rules
- Extract test cases if linked

#### Diagram Information
- List which diagrams contain each element
- Include diagram types and purposes
- Generate diagram inventory

#### Cross-References
- Generate element index with links
- Create traceability matrix
- Build dependency graphs in mermaid format

#### Quality Checks
- Identify undocumented elements (empty Note fields)
- Find orphaned elements (no package or diagram)
- Check for missing relationships
- Report incomplete state machines

### 5. Output Structure

```
docs/
├── index.md                 # Main navigation and summary
├── schema.json              # Database schema documentation
├── use-cases/
│   ├── index.md            # Use case overview
│   ├── actors.md           # Actor catalog
│   └── uc-[id]-[name].md   # Individual use case files
├── state-machines/
│   ├── index.md            # State machine overview
│   └── sm-[name].md        # Individual state machine files
├── components/
│   ├── index.md            # Component overview
│   ├── interfaces.md       # Interface catalog
│   └── comp-[name].md      # Individual component files
├── classes/
│   ├── index.md            # Class overview
│   ├── packages.md         # Package structure
│   └── [package]/          # Package-based organization
│       └── [class].md      # Individual class files
└── reports/
    ├── quality-report.md   # Documentation quality metrics
    ├── dependencies.md     # Dependency analysis
    └── traceability.md     # Traceability matrix
```

### 6. Error Handling

- Gracefully handle missing or null values
- Clean HTML tags from Note fields
- Handle special characters in names
- Report but don't fail on missing relationships
- Validate foreign key references

### 7. Configuration File

Create `config.yaml` for customization:
```yaml
output:
  directory: "docs"
  include_timestamp: true
  include_author: true
  
extraction:
  include_private: false
  include_deprecated: true
  extract_tagged_values: true
  extract_diagrams: true
  
documentation:
  use_cases:
    detailed_scenarios: true
    include_test_cases: true
  classes:
    include_private_members: false
    show_dependencies: true
  components:
    show_deployment: true
    
quality_checks:
  check_undocumented: true
  check_orphaned: true
  min_description_length: 20
```

### 8. Command Line Interface

```bash
# Basic usage
python sparx_doc_generator.py model.qea

# With options
python sparx_doc_generator.py model.qea \
  --output docs \
  --config config.yaml \
  --format markdown \
  --verbose \
  --check-quality

# Schema analysis only
python sparx_doc_generator.py model.qea --analyze-schema

# Specific documentation types
python sparx_doc_generator.py model.qea --only use-cases,classes
```

## Test Model Requirements

The test model (test_model.qea) should contain the following elements to fully test the documentation generator:

### Package Structure
- Root package: "TestSystem"
- Sub-packages: "UseCases", "Components", "Domain", "StateMachines"

### Use Cases (minimum 3)
1. **Login Use Case**
   - Actors: User (primary), System Administrator (secondary)
   - Include: Validate Credentials
   - Extend: Reset Password
   - Description with pre/postconditions

2. **Process Order**
   - Actors: Customer, Payment System
   - Multiple scenarios/flows
   - Business rules in notes

3. **Generate Report**
   - Actor: Manager
   - Include relationship to "Fetch Data"

### State Machine (minimum 1 complete)
1. **Order State Machine**
   - States: Initial, Pending, Processing, Shipped, Delivered, Cancelled, Final
   - Transitions with guards and triggers
   - At least one composite state with substates
   - Entry/exit actions on some states

### Components (minimum 3)
1. **UserInterface**
   - Provided interfaces: IUserDisplay
   - Required interfaces: IDataService
   - Ports defined

2. **BusinessLogic**
   - Multiple provided/required interfaces
   - Dependencies to other components

3. **DataAccess**
   - Provided interfaces: IDataService
   - Component relationships

### Classes (minimum 5)
1. **Abstract class: Entity**
   - id: String
   - created: DateTime
   - Abstract methods

2. **Class: User (inherits Entity)**
   - Attributes: username, email, password
   - Methods: login(), logout(), resetPassword()
   - Association to Role class

3. **Class: Order**
   - Multiple attributes with different visibilities
   - Static methods
   - Aggregation to OrderItem

4. **Interface: IDataService**
   - Method signatures
   - Used by multiple classes

5. **Enumeration: OrderStatus**
   - Values: PENDING, PROCESSING, SHIPPED, DELIVERED, CANCELLED

### Additional Elements
- At least 2 diagrams containing the elements
- Tagged values on some elements (requirements, constraints)
- Notes/descriptions on all major elements (minimum 20 words)
- Various relationship types: association, aggregation, composition, dependency, realization

## Development Process

1. **Phase 1: Schema Analysis**
   - Connect to provided .qea file
   - Analyze and document all tables
   - Identify data relationships
   - Output schema.json and analysis

2. **Phase 2: Basic Extraction**
   - Implement extraction for each element type
   - Handle NULL values and data cleaning
   - Create data models/classes for elements

3. **Phase 3: Documentation Generation**
   - Generate markdown for each element type
   - Create navigation and indices
   - Implement cross-referencing

4. **Phase 4: Advanced Features**
   - Add quality checks
   - Implement configuration options
   - Add diagram extraction
   - Generate visual representations (mermaid)

5. **Phase 5: Polish**
   - Error handling and logging
   - Performance optimization
   - Command-line interface
   - Comprehensive testing

## Success Criteria

- Successfully connects to and reads .qea SQLite database
- Extracts all four documentation types accurately
- Generates well-formatted, navigable markdown documentation
- Handles edge cases gracefully
- Provides useful quality reports
- Maintains relationships and cross-references
- Produces professional documentation suitable for technical stakeholders

## Notes

- The .qea file is a SQLite database with a specific schema used by Sparx EA
- HTML tags in Note fields should be cleaned
- Some tables may use BLOBs for certain data - handle appropriately
- Foreign key relationships may not be enforced - validate references
- Consider performance for large models (1000+ elements)