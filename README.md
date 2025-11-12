# Sparx Enterprise Architect Documentation Generator

A Python utility that extracts and documents UML models from Sparx Enterprise Architect .qea files (SQLite database format) and generates comprehensive markdown and HTML documentation.

## Features

- **Multi-format Documentation**: Extracts Use Cases, Requirements, State Machines, Components, and Classes/Modules
- **HTML Generation**: Convert markdown documentation to HTML with embedded CSS styling
- **Diagram Rendering**: Generates pixel-perfect PNG diagrams matching EA's visual style
- **EA Diagram Integration**: Use EA-exported diagrams when available for perfect accuracy
- **Rich Relationship Mapping**: Documents inheritance, associations, dependencies, and more
- **Quality Analysis**: Identifies undocumented elements and quality issues
- **Markdown Output**: Professional, navigable documentation in markdown format
- **Change Tracking**: Track documentation versions and generate diffs
- **Configurable**: Customizable extraction and documentation options via YAML config

## Requirements

- Python 3.7 or higher
- Required packages (see requirements.txt):
  - PyYAML (for configuration file support)
  - graphviz (for diagram rendering)
  - Pillow (for image processing)
  - markdown (for HTML generation)

## Installation

1. Clone or download this repository
2. Install dependencies:

```bash
pip install -r requirements.txt
```

3. Make the script executable (optional, Linux/Mac):

```bash
chmod +x sparx_doc_generator.py
```

## Usage

### Basic Usage

Extract and document a complete model:

```bash
python sparx_doc_generator.py model.qea
```

This will create a `docs/` directory with all documentation.

### Specify Output Directory

```bash
python sparx_doc_generator.py model.qea --output my-docs
```

### Use Configuration File

```bash
python sparx_doc_generator.py model.qea --config config.yaml
```

### Schema Analysis Only

To analyze the database schema without generating documentation:

```bash
python sparx_doc_generator.py model.qea --analyze-schema
```

This will create `docs/schema.json` with detailed schema information.

### Verbose Mode

Enable detailed logging:

```bash
python sparx_doc_generator.py model.qea --verbose
```

### HTML Generation

Generate HTML documentation alongside markdown:

```bash
python sparx_doc_generator.py model.qea --html
```

With custom HTML output directory:

```bash
python sparx_doc_generator.py model.qea --html --html-output docs_html
```

### EA Exported Diagrams

Use EA-exported diagrams instead of generating them:

```bash
python sparx_doc_generator.py model.qea --ea-diagrams-dir /path/to/ea/exports
```

Export diagrams from EA with format: `{GUID}-{timestamp}.png`

### Change Tracking

Enable documentation version tracking:

```bash
python sparx_doc_generator.py model.qea --track-changes
```

## Command-Line Options

```
usage: sparx_doc_generator.py [-h] [--output OUTPUT] [--config CONFIG]
                              [--analyze-schema] [--verbose] [--track-changes]
                              [--html] [--html-output HTML_OUTPUT]
                              [--ea-diagrams-dir EA_DIAGRAMS_DIR]
                              qea_file

Generate documentation from Sparx Enterprise Architect .qea files

positional arguments:
  qea_file              Path to the .qea SQLite database file

optional arguments:
  -h, --help            show this help message and exit
  --output OUTPUT, -o OUTPUT
                        Output directory for documentation (default: docs)
  --config CONFIG, -c CONFIG
                        Path to configuration YAML file
  --analyze-schema      Only analyze and output database schema
  --verbose, -v         Enable verbose logging
  --track-changes       Enable change tracking and generate diff documentation
  --html                Generate HTML documentation in addition to markdown
  --html-output HTML_OUTPUT
                        Output directory for HTML documentation (default: docs_html)
  --ea-diagrams-dir EA_DIAGRAMS_DIR
                        Directory containing EA-exported diagrams (GUID-timestamp.png format)
```

## Output Structure

The generator creates the following documentation structure:

```
docs/
├── index.md                      # Main navigation and summary
├── schema.json                   # Database schema documentation
├── diagrams/                     # Rendered PNG diagrams
│   ├── usecases.png
│   ├── components.png
│   ├── domain.png
│   └── [diagram-name].png
├── use-cases/
│   ├── index.md                 # Use case overview
│   ├── actors.md                # Actor catalog
│   └── uc-[id]-[name].md        # Individual use case files
├── requirements/
│   ├── index.md                 # Requirements overview
│   └── req-[name].md            # Individual requirement files
├── state-machines/
│   ├── index.md                 # State machine overview
│   └── sm-[name].md             # Individual state machine files
├── components/
│   ├── index.md                 # Component overview
│   ├── interfaces.md            # Interface catalog
│   └── comp-[name].md           # Individual component files
├── classes/
│   ├── index.md                 # Class overview
│   └── [package]/               # Package-based organization
│       └── [class].md           # Individual class files
└── reports/
    ├── quality-report.md        # Documentation quality metrics
    └── dependencies.md          # Dependency analysis

docs_html/                        # HTML version (if --html used)
├── index.html
├── diagrams/
└── [same structure as markdown]
```

## Documentation Types

### Use Cases

Extracts and documents:
- Use case elements
- Actors
- Relationships (includes, extends, associations)
- Pre/post conditions
- Descriptions and notes

### State Machines

Extracts and documents:
- States (all types)
- Transitions with triggers and guards
- State hierarchy
- Entry/exit actions

### Components

Extracts and documents:
- Components
- Provided and required interfaces
- Ports and connectors
- Dependencies
- Attributes and operations

### Classes and Modules

Extracts and documents:
- Classes, interfaces, and enumerations
- Attributes with full details (type, visibility, defaults)
- Methods/operations with parameters
- Inheritance relationships
- Associations, aggregations, compositions
- Dependencies

## Configuration

Create a `config.yaml` file to customize the documentation generation:

```yaml
output:
  directory: "docs"
  include_timestamp: true
  include_author: true

diagrams:
  ea_exports_dir: "sample_diagrams"  # Directory containing EA-exported diagrams

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

## Quality Checks

The generator performs automatic quality checks:

- **Undocumented Elements**: Identifies elements with missing or insufficient descriptions
- **Documentation Rate**: Calculates overall documentation coverage
- **Statistics**: Provides counts for all element types

View the quality report at `docs/reports/quality-report.md` after generation.

## Dependency Analysis

The generator creates a dependency analysis report that includes:

- Complete list of all dependencies
- Dependency graph visualization (Mermaid format)
- Component and class relationships

View the dependency report at `docs/reports/dependencies.md`.

## Database Schema

The .qea file is a SQLite database with the following key tables:

- `t_object` - Contains model elements (classes, components, use cases, etc.)
- `t_attribute` - Contains attributes for classes and components
- `t_operation` - Contains methods/operations for classes
- `t_connector` - Contains relationships between elements
- `t_package` - Contains package/namespace information
- `t_diagram` - Contains diagram information

Run with `--analyze-schema` to get a complete schema analysis.

## Examples

### Example 1: Full Documentation with HTML and EA Diagrams

```bash
python sparx_doc_generator.py mymodel.qea \
  --output project-docs \
  --html \
  --ea-diagrams-dir /path/to/ea/exports \
  --config my-config.yaml \
  --verbose
```

### Example 2: Documentation with Change Tracking

```bash
python sparx_doc_generator.py mymodel.qea \
  --track-changes \
  --html
```

### Example 3: Quick Schema Check

```bash
python sparx_doc_generator.py mymodel.qea --analyze-schema
```

### Example 4: Standard Documentation

```bash
python sparx_doc_generator.py mymodel.qea
cd docs
# Open index.md in your markdown viewer
```

## Troubleshooting

### Error: "QEA file not found"
- Verify the path to your .qea file is correct
- Use absolute paths if relative paths don't work

### Error: "Database connection error"
- Ensure the .qea file is not corrupted
- Check that the file is a valid SQLite database
- Make sure the file is not open in Sparx EA (may be locked)

### Missing Elements in Documentation
- Some elements may not be extracted if they don't follow standard Sparx EA conventions
- Check the quality report for undocumented elements
- Use `--verbose` to see extraction details

### Empty or Incomplete Documentation
- Verify your model contains the expected elements
- Run with `--analyze-schema` to inspect the database structure
- Check that element types match expected values (UseCase, Actor, Component, etc.)

## Limitations

- Only supports .qea (SQLite) format, not .eap (Access) format
- HTML in notes is stripped (converted to plain text)
- Tagged values extraction is basic (can be extended)
- Performance may vary with very large models (1000+ elements)
- Generated diagrams may not exactly match EA's layout (use --ea-diagrams-dir for pixel-perfect diagrams)

## Development

### Project Structure

```
EATools/
├── sparx_doc_generator.py          # Main CLI entry point
├── sparx_doc_gui.py                # GUI application
├── config.yaml                      # Sample configuration file
├── requirements.txt                 # Python dependencies
├── templates/                       # Markdown templates
├── sparx_ea_doc/                   # Core package
│   ├── extractor.py                # Database extraction
│   ├── generators/                 # Documentation generators
│   ├── diagram_renderer.py         # Diagram rendering
│   ├── html_generator.py          # HTML conversion
│   ├── quality_reporter.py        # Quality analysis
│   ├── diff_generator.py          # Change tracking
│   └── template_renderer.py       # Template processing
├── docs_golden/                    # Regression test baseline
├── sample_diagrams/               # EA-exported diagrams
└── test_doc_consistency.py        # Regression tests
```

### Extending the Generator

The generator is designed to be extensible. Key areas for enhancement:

1. **Add new element types**: Extend extraction methods in `SparxExtractor`
2. **Custom documentation formats**: Create new generators in `sparx_ea_doc/generators/`
3. **Additional quality checks**: Add to `QualityReporter`
4. **Enhanced diagram rendering**: Improve `DiagramRenderer` algorithms
5. **Tagged values**: Enhance tagged value extraction from `t_objectproperties`
6. **Export formats**: Add new export formats beyond HTML and Markdown

## License

This project is provided as-is for educational and professional use.

## Contributing

Contributions are welcome! Areas for improvement:

- Support for additional UML element types (Activities, Sequences, Deployments)
- Enhanced diagram rendering algorithms for better layout matching
- More comprehensive tagged value handling
- Export to additional formats (PDF, DocX, Confluence)
- Performance optimizations for large models (10,000+ elements)
- Expanded unit tests and integration tests
- GUI enhancements and usability improvements
- Additional template customization options

## Support

For issues, questions, or contributions, please refer to the project documentation or contact the maintainers.

## Acknowledgments

Developed for extracting and documenting UML models from Sparx Enterprise Architect, a powerful modeling tool for software architects and developers.
