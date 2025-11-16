# Class: ComponentGenerator

[Home](../../index.md) > [Classes](../index.md) > [Generators](index.md) > ComponentGenerator

**Package:** generators

**Version: 1.0 | Modified: 2025-11-16 19:19:33 | GUID: {60147DD5-8544-438f-9D1D-5F34D4596CEB}**

**Description:** Generates component documentation

## Diagrams

### generators

![generators](../../diagrams/generators.png)


## Methods

| Name | Parameters | Return Type | Description |
|------|------------|-------------|-------------|
| __init__ | self: unknown, extractor: unknown, output_dir: Path, template_dir: Path, diagram_guid_to_png: Dict[str, str] | void |  Initialize the component generator  Args:     extractor: SparxExtractor instance with extracted data     output_dir: Output directory for documentation     template_dir: Directory containing templates (optional)     diagram_guid_to_png: Mapping of diagram GUIDs to PNG file paths |
| _generate_interfaces_catalog | self: unknown, comp_dir: Path | void | Generate interfaces catalog |
| _generate_single_component | self: unknown, comp: unknown, comp_file: Path | str | Generate documentation for a single component |
| _get_package_diagrams | self: unknown, package_names: List[str] | List[tuple] |  Get diagrams for given package names  Args:     package_names: List of package names to find diagrams for  Returns:     List of (diagram_guid, diagram_name) tuples |
| generate | self: unknown | void | Generate component documentation |

