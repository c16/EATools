# Class: QualityReporter

[Home](../../index.md) > [Classes](../index.md) > [Sparx Ea Doc](index.md) > QualityReporter

**Package:** sparx_ea_doc

**Version: 1.0 | Modified: 2025-11-16 19:19:34 | GUID: {4AA60C2B-6C5E-4f02-AD4F-A6A78DFE9019}**

**Description:** Performs quality checks and generates reports

## Diagrams

### sparx_ea_doc

![sparx_ea_doc](../../diagrams/sparx_ea_doc.png)


## Methods

| Name | Parameters | Return Type | Description |
|------|------------|-------------|-------------|
| __init__ | self: unknown, extractor: unknown, output_dir: Path, config: Dict | void |  Initialize the quality reporter  Args:     extractor: SparxExtractor instance with extracted data     output_dir: Output directory for documentation     config: Optional configuration dictionary |
| _generate_reports_index | self: unknown | void | Generate or update the reports index page |
| generate_dependencies_report | self: unknown | void | Generate dependencies analysis report |
| generate_quality_report | self: unknown | void | Generate quality report |
| perform_quality_checks | self: unknown | void | Perform quality checks on the model |

