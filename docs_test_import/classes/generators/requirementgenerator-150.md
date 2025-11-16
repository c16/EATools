# Class: RequirementGenerator

[Home](../../index.md) > [Classes](../index.md) > [Generators](index.md) > RequirementGenerator

**Package:** generators

**Version: 1.0 | Modified: 2025-11-16 19:19:33 | GUID: {DE826F90-DDC6-46dc-88C4-78EACA6975EA}**

**Description:** Generates requirement documentation

## Diagrams

### generators

![generators](../../diagrams/generators.png)


## Methods

| Name | Parameters | Return Type | Description |
|------|------------|-------------|-------------|
| __init__ | self: unknown, extractor: unknown, output_dir: Path, template_dir: Path | void |  Initialize the requirement generator  Args:     extractor: SparxExtractor instance with extracted data     output_dir: Output directory for documentation     template_dir: Directory containing templates (optional) |
| _generate_hardcoded | self: unknown, req: unknown, breadcrumbs: str | str |  Generate requirement documentation using hard-coded format (fallback)  Args:     req: Requirement object     breadcrumbs: Pre-generated breadcrumb navigation  Returns:     Generated content |
| _generate_requirement_docs | self: unknown, req_dir: Path | void | Generate individual requirement documents |
| _generate_single_requirement | self: unknown, req: unknown, req_file: Path | str |  Generate documentation for a single requirement  Args:     req: Requirement object     req_file: Output file path  Returns:     Generated content |
| _generate_with_template | self: unknown, req: unknown, breadcrumbs: str | str |  Generate requirement documentation using template  Args:     req: Requirement object     breadcrumbs: Pre-generated breadcrumb navigation  Returns:     Rendered documentation |
| generate | self: unknown | void | Generate requirement documentation |

