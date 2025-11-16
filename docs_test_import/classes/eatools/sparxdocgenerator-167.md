# Class: SparxDocGenerator

[Home](../../index.md) > [Classes](../index.md) > [Eatools](index.md) > SparxDocGenerator

**Package:** EATools

**Version: 1.0 | Modified: 2025-11-16 19:19:34 | GUID: {4B751440-6C53-422d-A5E5-ED3FD49BA0A1}**

**Description:** Main documentation generator orchestrator

## Diagrams

### EATools

![EATools](../../diagrams/eatools.png)


## Methods

| Name | Parameters | Return Type | Description |
|------|------------|-------------|-------------|
| __init__ | self: unknown, qea_path: str, output_dir: str, config: Optional[Dict], template_dir: str, track_changes: bool, render_diagrams: bool, generate_html: bool, html_output_dir: Optional[str], ea_diagrams_dir: Optional[str] | void |  Initialize the documentation generator  Args:     qea_path: Path to the .qea SQLite database file     output_dir: Directory for output documentation     config: Optional configuration dictionary     template_dir: Optional directory containing templates     track_changes: Enable change tracking and diff generation     render_diagrams: Enable diagram rendering to PNG     generate_html: Enable HTML generation from markdown     html_output_dir: Optional directory for HTML output (default: docs_html)     ea_diagrams_dir: Directory containing EA-exported diagrams (optional) |
| analyze_schema | self: unknown | Dict |  Analyze and document the database schema  Returns:     Dictionary containing schema information |
| extract_model_data | self: unknown | void | Extract all model data from the database |
| generate_documentation | self: unknown | void | Generate all markdown documentation |
| generate_index | self: unknown | void | Generate main index/navigation document |
| render_all_diagrams | self: unknown | void | Render all diagrams to PNG and build GUID-to-PNG mapping |
| run | self: unknown, analyze_schema_only: bool | void |  Main execution flow  Args:     analyze_schema_only: If True, only analyze schema and exit |

